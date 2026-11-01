"""Backtest result store: incremental upsert, materialised index and publishing.

Every merged-pipeline run keeps its own ``evaluations.json``. This module adds the
cross-run layer that the research loop needs:

* **incremental upsert** -- expressions are keyed by their canonical form; a
  re-evaluated expression updates the existing record (``revision`` increments)
  instead of creating a duplicate;
* **event log** -- ``experiments/.index/results_events.jsonl`` is append-only,
  so nothing is ever silently lost;
* **materialised index** -- ``experiments/.index/results_index.json`` /
  ``results.csv`` are rebuilt from the per-run files and always reflect the
  latest state;
* **publishing** -- a merged batch is written into its date-ordered experiment
  directory (``experiments/<YYYYMMDD>-<name>/``) so it can be committed.

``python -m factorlab.xy_results --rebuild-index``
``python -m factorlab.xy_results --publish <run_id> [--top 10]``
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from .config import PROJECT_ROOT
from .experiments_store import (
    EXPERIMENTS,
    dated_experiment_dir,
    experiment_date_for_run,
    find_run_dir,
    iter_evaluation_files,
)
from .markdown import md_table

RESULTS_DIR = EXPERIMENTS
INDEX_DIR = EXPERIMENTS / ".index"
EVENTS_PATH = INDEX_DIR / "results_events.jsonl"
INDEX_PATH = INDEX_DIR / "results_index.json"
CSV_PATH = INDEX_DIR / "results.csv"
PUBLISHED_DIR = EXPERIMENTS


def _canonical(expression: str) -> str:
    from .xy_pipeline import _canonical as canonical

    return canonical(expression)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_safe(value):
    import math

    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


# --------------------------------------------------------------------------- #
# per-run evaluations: load / upsert
# --------------------------------------------------------------------------- #
def load_evaluations(path: str | Path) -> list[dict]:
    """Read one run's ``evaluations.json`` (legacy list or keyed dict)."""
    path = Path(path)
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if isinstance(payload, dict) and "records" in payload:
        payload = payload["records"]
    if isinstance(payload, dict):
        payload = list(payload.values())
    return [record for record in payload if isinstance(record, dict)]


def _write_evaluations(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "updated_at": _now(),
        "n_records": len(records),
        "records": [_json_safe(record) for record in records],
    }
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def upsert_evaluations(path: str | Path, new_records: Iterable[dict], run_id: str = "") -> dict:
    """Merge ``new_records`` into a run's evaluation file, keyed by canonical form.

    Returns ``{"inserted": n, "updated": n, "unchanged": n}``. Existing records
    keep their identity while the changed fields (metrics, decision, display,
    stability) are replaced and ``revision`` is incremented.
    """
    path = Path(path)
    existing = load_evaluations(path)
    index: dict[str, dict] = {}
    for record in existing:
        expression = record.get("expression")
        key = _canonical(expression) if expression else f"_noexpr_{id(record)}"
        index[key] = record

    stats = {"inserted": 0, "updated": 0, "unchanged": 0}
    for record in new_records:
        record = dict(record)
        expression = record.get("expression")
        if not expression:
            continue
        key = _canonical(expression)
        previous = index.get(key)
        if previous is None:
            record["revision"] = 1
            record["updated_at"] = _now()
            record["run_id"] = run_id or record.get("run_id", "")
            index[key] = record
            stats["inserted"] += 1
            continue
        merged = dict(previous)
        changed = False
        for field, value in record.items():
            if field in ("revision", "updated_at", "created_at", "run_id"):
                continue
            if merged.get(field) != value:
                merged[field] = value
                changed = True
        if not changed:
            stats["unchanged"] += 1
            continue
        merged["revision"] = int(previous.get("revision", 1)) + 1
        merged["updated_at"] = _now()
        merged.setdefault("created_at", previous.get("updated_at", _now()))
        merged["run_id"] = run_id or previous.get("run_id", "")
        index[key] = merged
        stats["updated"] += 1

    ordered = sorted(index.values(), key=lambda item: str(item.get("updated_at", "")))
    _write_evaluations(path, ordered)
    return stats


# --------------------------------------------------------------------------- #
# append-only event log
# --------------------------------------------------------------------------- #
def record_events(
    path: str | Path,
    run_id: str,
    records: Iterable[dict],
    stage: str = "evaluated",
) -> int:
    """Append one event per record; the log is append-only and never rewritten."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            expression = record.get("expression")
            if not expression:
                continue
            is_metrics = ((record.get("is") or {}).get("metrics")) or {}
            segments = ((record.get("display") or {}).get("segments")) or {}
            event = {
                "event_id": f"{run_id}:{_canonical(expression)[:40]}:{stage}:{int(time.time() * 1000)}",
                "run_id": run_id,
                "stage": stage,
                "expression": expression,
                "decision": record.get("decision"),
                "revision": record.get("revision"),
                "in_sample": {
                    key: is_metrics.get(key)
                    for key in ("sharpe", "ann_return", "turnover", "max_drawdown", "rank_ic")
                },
                "display": {
                    "is_sharpe": (segments.get("is") or {}).get("sharpe"),
                    "oos_sharpe": (segments.get("oos") or {}).get("sharpe"),
                    "holdout_sharpe": (segments.get("holdout") or {}).get("sharpe"),
                },
                "recorded_at": _now(),
            }
            handle.write(json.dumps(_json_safe(event), ensure_ascii=False) + "\n")
            written += 1
    return written


# --------------------------------------------------------------------------- #
# materialised index
# --------------------------------------------------------------------------- #
def _run_evaluation_files(results_dir: Path) -> list[Path]:
    if Path(results_dir) == EXPERIMENTS:
        return iter_evaluation_files()
    if not results_dir.exists():
        return []
    files = []
    for run_dir in sorted(p for p in results_dir.iterdir() if p.is_dir()):
        path = run_dir / "evaluations.json"
        if path.exists():
            files.append(path)
        nested = run_dir / "runs"
        if nested.is_dir():
            files.extend(sorted(p / "evaluations.json" for p in nested.iterdir() if (p / "evaluations.json").exists()))
    return files


def _resolve_run_dir(run_id: str, results_dir: Path) -> Path:
    if Path(results_dir) == EXPERIMENTS:
        found = find_run_dir(run_id)
        if found is not None:
            return found
    return Path(results_dir) / run_id


def rebuild_index(
    results_dir: str | Path = RESULTS_DIR,
    index_path: str | Path = INDEX_PATH,
    csv_path: str | Path = CSV_PATH,
) -> dict:
    """Rebuild the cross-run index/CSV from every run's evaluations.json."""
    results_dir = Path(results_dir)
    latest: dict[tuple[str, str], dict] = {}
    for path in _run_evaluation_files(results_dir):
        run_id = path.parent.name
        for record in load_evaluations(path):
            expression = record.get("expression")
            if not expression:
                continue
            key = (run_id, _canonical(expression))
            updated = str(record.get("updated_at", ""))
            previous = latest.get(key)
            if previous is None or updated >= str(previous.get("updated_at", "")):
                is_metrics = ((record.get("is") or {}).get("metrics")) or {}
                segments = ((record.get("display") or {}).get("segments")) or {}
                latest[key] = {
                    "run_id": run_id,
                    "expression": expression,
                    "decision": record.get("decision"),
                    "revision": record.get("revision", 1),
                    "sharpe_is": is_metrics.get("sharpe"),
                    "ann_return_is": is_metrics.get("ann_return"),
                    "turnover_is": is_metrics.get("turnover"),
                    "rank_ic_is": is_metrics.get("rank_ic"),
                    "sharpe_oos": (segments.get("oos") or {}).get("sharpe"),
                    "sharpe_holdout": (segments.get("holdout") or {}).get("sharpe"),
                    "updated_at": updated or record.get("updated_at"),
                }
    rows = sorted(latest.values(), key=lambda item: (item["run_id"], item["expression"]))
    index_path = Path(index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps({"updated_at": _now(), "n_records": len(rows), "records": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    frame = pd.DataFrame(rows)
    frame.to_csv(csv_path, index=False, encoding="utf-8")
    return {"n_records": len(rows), "runs": len({row["run_id"] for row in rows})}


# --------------------------------------------------------------------------- #
# publishing
# --------------------------------------------------------------------------- #
def _run_dir(run_id: str, results_dir: Path) -> Path:
    return _resolve_run_dir(run_id, results_dir)


def _overview_plot(rows: list[dict], out_path: Path, title: str) -> Optional[Path]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:  # pragma: no cover - matplotlib is a dependency
        return None
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axes[0]
    xs = [row["sharpe_is"] for row in rows if row.get("sharpe_is") is not None]
    ys = [row.get("sharpe_oos") for row in rows if row.get("sharpe_is") is not None]
    ys = [value if value is not None else float("nan") for value in ys]
    ax.scatter(xs, ys, s=18, alpha=0.75, color="#1f77b4")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("in-sample Sharpe")
    ax.set_ylabel("out-of-sample Sharpe (display only)")
    ax.set_title("IS vs OOS (OOS never fed back)", fontsize=10)
    ax.grid(alpha=0.25)
    ax = axes[1]
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row.get("decision"))] = counts.get(str(row.get("decision")), 0) + 1
    names = list(counts)
    ax.bar(names, [counts[name] for name in names], color="#8c564b")
    ax.set_title("reviewer decisions", fontsize=10)
    ax.tick_params(axis="x", rotation=20)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    tmp = out_path.with_name(out_path.name + ".tmp.png")
    fig.savefig(tmp, dpi=130, bbox_inches="tight")
    plt.close(fig)
    for _ in range(5):
        try:
            os.replace(tmp, out_path)
            return out_path
        except OSError:
            time.sleep(0.2)
    return None


def _fmt(value) -> str:
    return "-" if value is None else f"{value:.3f}"


def _resolve_figure(run_dir: Path, record: dict) -> Optional[Path]:
    """Find the display figure for a record, tolerating stale/relative paths."""
    display = record.get("display") or {}
    candidates: list[Path] = []
    figure = display.get("figure")
    if figure:
        path = Path(str(figure))
        candidates.append(path if path.is_absolute() else run_dir / path)
    expression_id = record.get("expression_id")
    if expression_id:
        candidates.append(run_dir / "display" / expression_id / "pnl.png")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _row_metrics(record: dict) -> dict:
    is_metrics = ((record.get("is") or {}).get("metrics")) or {}
    display = record.get("display") or {}
    segments = display.get("segments") or {}
    return {
        "expression": record.get("expression"),
        "expression_id": record.get("expression_id"),
        "label": display.get("label") or "",
        "hypothesis": display.get("hypothesis") or "",
        "slug": display.get("slug") or "",
        "decision": record.get("decision"),
        "sharpe_is": is_metrics.get("sharpe"),
        "ann_return_is": is_metrics.get("ann_return"),
        "turnover_is": is_metrics.get("turnover"),
        "rank_ic_is": is_metrics.get("rank_ic"),
        "sharpe_oos": (segments.get("oos") or {}).get("sharpe"),
        "sharpe_holdout": (segments.get("holdout") or {}).get("sharpe"),
    }


def _copy_figures(
    frame: pd.DataFrame,
    run_dir: Path,
    figures: Path,
    top: int,
    per_run_labels: bool = False,
) -> list[dict]:
    """Copy display figures into ``figures/`` and write ``figures/index.csv``."""
    limit = len(frame) if not top else max(0, int(top))
    index_rows: list[dict] = []
    for rank, (_, row) in enumerate(frame.iterrows(), start=1):
        if rank > limit:
            break
        figure = row.get("figure")
        if not figure or not Path(str(figure)).is_file():
            continue
        expression_id = str(row.get("expression_id") or f"expr{rank:03d}")
        suffix = Path(str(figure)).suffix or ".png"
        run_label = row.get("run_id") if per_run_labels else run_dir.name
        factor_label = str(row.get("label") or "").strip() or expression_id
        safe_label = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in factor_label)
        destination = figures / f"rank{rank:03d}_{run_label}_{safe_label}{suffix}"
        shutil.copyfile(Path(str(figure)), destination)
        index_rows.append(
            {
                "rank": rank,
                "run_id": row.get("run_id", run_dir.name),
                "expression_id": expression_id,
                "label": row.get("label") or "",
                "hypothesis": row.get("hypothesis") or "",
                "expression": row.get("expression"),
                "decision": row.get("decision"),
                "sharpe_is": row.get("sharpe_is"),
                "sharpe_oos": row.get("sharpe_oos"),
                "sharpe_holdout": row.get("sharpe_holdout"),
                "figure": destination.relative_to(figures.parent).as_posix(),
            }
        )
    if index_rows:
        pd.DataFrame(index_rows).to_csv(figures / "index.csv", index=False, encoding="utf-8")
    return index_rows


def _figure_table(index_rows: list[dict]) -> list[str]:
    lines = [
        "| rank | factor | hypothesis | run | IS | OOS | holdout | decision | figure |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for item in index_rows:
        lines.append(
            f"| {item['rank']} | `{item.get('label') or '-'}` | "
            f"{_md_escape(str(item.get('hypothesis') or ''))[:70]} | `{item['run_id']}` | "
            f"{_fmt(item.get('sharpe_is'))} | {_fmt(item.get('sharpe_oos'))} | "
            f"{_fmt(item.get('sharpe_holdout'))} | {item.get('decision') or '-'} | "
            f"`{item['figure']}` |"
        )
    return lines


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def publish_run(
    run_id: str,
    results_dir: str | Path = RESULTS_DIR,
    published_dir: str | Path = PUBLISHED_DIR,
    top: int = 0,
) -> Path:
    """Copy a single run's summary, display figures and overview chart for git."""
    results_dir = Path(results_dir)
    source = _run_dir(run_id, results_dir)
    evaluations = load_evaluations(source / "evaluations.json")
    if not evaluations:
        raise FileNotFoundError(f"no evaluations for run {run_id!r} under {source}")
    if str(published_dir) == str(EXPERIMENTS):
        target = dated_experiment_dir(run_id, experiment_date_for_run(run_id))
    else:
        target = Path(published_dir) / run_id
    figures = target / "figures"
    for directory in (target, figures):
        directory.mkdir(parents=True, exist_ok=True)

    rows = []
    for record in evaluations:
        if record.get("status") != "evaluated":
            continue
        row = _row_metrics(record)
        row["figure"] = _resolve_figure(source, record)
        rows.append(row)
    frame = pd.DataFrame(rows).sort_values("sharpe_is", ascending=False, na_position="last")
    frame.drop(columns=["figure"]).to_csv(target / "summary.csv", index=False, encoding="utf-8")

    index_rows = _copy_figures(frame, source, figures, top)

    for name in ("report.md", "run.json"):
        candidate = source / name
        if candidate.exists():
            shutil.copyfile(candidate, target / name)
    _overview_plot(rows, target / "overview.png", f"{run_id} | {len(rows)} evaluated expressions")

    lines = [
        f"# Published results: `{run_id}`",
        "",
        f"- evaluated expressions: {len(rows)}",
        f"- display figures: {len(index_rows)} (every evaluated expression unless --top is set)",
        "- data isolation: the optimisation loop and the reviewer saw in-sample only; "
        "OOS/holdout are display-only and were never fed back",
        "",
        "## Summary",
        "",
        md_table(
            frame[["expression", "sharpe_is", "turnover_is", "sharpe_oos", "sharpe_holdout", "decision"]]
            if not frame.empty
            else frame
        ),
        "",
        "## Figures",
        "",
    ] + _figure_table(index_rows)
    (target / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return target


def _collect_rows(run_ids: list[str], results_dir: Path) -> list[dict]:
    rows = []
    for run_id in run_ids:
        run_dir = _run_dir(run_id, results_dir)
        for record in load_evaluations(run_dir / "evaluations.json"):
            if record.get("status") != "evaluated":
                continue
            row = _row_metrics(record)
            row["run_id"] = run_id
            row["figure"] = _resolve_figure(run_dir, record)
            rows.append(row)
    return rows


def publish_combined(
    name: str,
    run_ids: Iterable[str],
    results_dir: str | Path = RESULTS_DIR,
    published_dir: str | Path = PUBLISHED_DIR,
    top: int = 0,
) -> Path:
    """Merge several runs into one publishable folder (summary + every figure)."""
    results_dir = Path(results_dir)
    run_ids = list(run_ids)
    rows = _collect_rows(run_ids, results_dir)
    if not rows:
        raise FileNotFoundError(f"no evaluated expressions for runs {run_ids}")
    if str(published_dir) == str(EXPERIMENTS):
        target = dated_experiment_dir(name, experiment_date_for_run(run_ids[0]))
    else:
        target = Path(published_dir) / name
    figures = target / "figures"
    for directory in (target, figures):
        directory.mkdir(parents=True, exist_ok=True)

    frame = pd.DataFrame(rows).sort_values("sharpe_is", ascending=False, na_position="last")
    frame.drop(columns=["figure"]).to_csv(target / "summary.csv", index=False, encoding="utf-8")
    index_rows = _copy_figures(frame, results_dir, figures, top, per_run_labels=True)

    _overview_plot(rows, target / "overview.png", f"{name} | {len(rows)} evaluated expressions")
    unique = len({_canonical(row["expression"]) for row in rows})
    lines = [
        f"# Published results: `{name}`",
        "",
        f"- runs: {', '.join(f'`{run_id}`' for run_id in run_ids)}",
        f"- evaluated expressions: {len(rows)} ({unique} unique canonical forms)",
        f"- display figures: {len(index_rows)} (every evaluated expression unless --top is set)",
        "- data isolation: the optimisation loop and the reviewer saw in-sample only; "
        "OOS/holdout are display-only and were never fed back",
        "",
        "## Summary",
        "",
        md_table(
            frame[[
                "run_id",
                "expression",
                "sharpe_is",
                "turnover_is",
                "rank_ic_is",
                "sharpe_oos",
                "sharpe_holdout",
                "decision",
            ]]
        ),
        "",
        "## Figures",
        "",
    ] + _figure_table(index_rows)
    (target / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return target


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild-index", action="store_true")
    parser.add_argument("--publish", default=None, help="run id to publish")
    parser.add_argument("--publish-combined", default=None, help="name of a combined publication")
    parser.add_argument("--runs", default="", help="comma separated run ids for --publish-combined")
    parser.add_argument("--top", type=int, default=0,
                        help="number of figures to publish (0 = every evaluated expression)")
    parser.add_argument("--all-figures", action="store_true", help="publish every display figure")
    parser.add_argument("--results-dir", default=str(RESULTS_DIR))
    args = parser.parse_args(argv)
    top = 0 if args.all_figures else args.top
    if args.rebuild_index:
        print(rebuild_index(results_dir=args.results_dir))
    if args.publish:
        target = publish_run(args.publish, results_dir=args.results_dir, top=top)
        print(f"published: {target}")
    if args.publish_combined:
        run_ids = [item.strip() for item in args.runs.split(",") if item.strip()]
        target = publish_combined(args.publish_combined, run_ids, results_dir=args.results_dir, top=top)
        print(f"published combined: {target}")
    if not args.rebuild_index and not args.publish and not args.publish_combined:
        parser.print_help()


if __name__ == "__main__":
    main()

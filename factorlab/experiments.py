"""Aggregate experiment ledger.

Every attempt of every run — accepted or abandoned — is flattened into one row
so that in-sample and untouched out-of-sample performance can be compared across
runs in a single table::

    experiments/ledger.csv

The ledger is rebuilt from ``runs/*/`` after each run (and on demand with
``python -m factorlab ledger --rebuild``), so the raw run directories stay the
source of truth and the CSV is a derived, human-readable summary.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

from .config import PROJECT_ROOT

LEDGER_DIR = PROJECT_ROOT / "experiments" / ".index"
LEDGER_PATH = LEDGER_DIR / "ledger.csv"

#: one row per attempt; ``*_full`` is the whole-sample backtest, ``*_is`` /
#: ``*_oos`` / ``*_holdout`` are the three segments, ``*_sub`` the sub-universe
LEDGER_COLUMNS: tuple[str, ...] = (
    "run_id",
    "timestamp",
    "llm",
    "data",
    "n_dates",
    "n_tickers",
    "hypothesis",
    "attempt",
    "decision",
    "source",
    "spec_kind",
    "expression",
    "validation_ok",
    "decay",
    "transform",
    "cap_filter",
    "windows",
    "params",
    "sharpe_full",
    "ann_return_full",
    "turnover_full",
    "max_drawdown_full",
    "rank_ic_full",
    "pearson_ic_full",
    "fitness_full",
    "n_names_full",
    "hit_rate_full",
    "sharpe_is",
    "ann_return_is",
    "turnover_is",
    "max_drawdown_is",
    "rank_ic_is",
    "sharpe_oos",
    "ann_return_oos",
    "turnover_oos",
    "max_drawdown_oos",
    "rank_ic_oos",
    "sharpe_holdout",
    "ann_return_holdout",
    "turnover_holdout",
    "max_drawdown_holdout",
    "rank_ic_holdout",
    "sharpe_sub",
    "ann_return_sub",
    "turnover_sub",
    "max_drawdown_sub",
    "rank_ic_sub",
    "sub_sharpe_is",
    "sub_sharpe_oos",
    "sub_sharpe_holdout",
    "is_range",
    "oos_range",
    "holdout_range",
    "factor_id",
    "elapsed_s",
    "error",
    "verification_status",
)


def _run_timestamp(run_id: str) -> Optional[str]:
    """``20261031-083828-e2e`` -> ``2026-10-31 08:38:28``."""
    head = str(run_id).split("-")[:2]
    if len(head) != 2:
        return None
    try:
        return datetime.strptime("-".join(head), "%Y%m%d-%H%M%S").isoformat(sep=" ")
    except ValueError:
        return None


def _dumps(value) -> str:
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return ""
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _num(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return np.nan
    return value if np.isfinite(value) else np.nan


def flatten_attempt(
    run_id: str,
    attempt: dict,
    panel_summary: Optional[dict] = None,
    llm: Optional[str] = None,
) -> dict:
    """Flatten one ``attempts.jsonl`` record into a ledger row."""
    grid = attempt.get("grid") or {}
    best = grid.get("best") or {}
    split = grid.get("split") or {}
    spec = attempt.get("spec") or {}
    review = attempt.get("review") or {}
    sub = grid.get("subuniverse") or {}
    sub_metrics = sub.get("metrics") or {}
    sub_segments = sub.get("segments") or {}
    panel_summary = panel_summary or {}

    row = {
        "run_id": run_id,
        "timestamp": _run_timestamp(run_id),
        "llm": llm or ("llm" if review.get("source") == "llm" else "offline"),
        "data": panel_summary.get("name"),
        "n_dates": panel_summary.get("n_dates"),
        "n_tickers": panel_summary.get("n_tickers"),
        "hypothesis": attempt.get("hypothesis"),
        "attempt": attempt.get("attempt"),
        "decision": review.get("decision") or ("error" if attempt.get("error") else ""),
        "source": review.get("source"),
        "spec_kind": spec.get("kind"),
        "expression": spec.get("expression") or ("<script>" if spec.get("script") else ""),
        "validation_ok": (attempt.get("validation") or {}).get("ok"),
        "decay": best.get("decay"),
        "transform": best.get("transform"),
        "cap_filter": best.get("cap_filter"),
        "windows": _dumps(best.get("windows")),
        "params": _dumps(best.get("params")),
        "factor_id": attempt.get("factor_id"),
        "elapsed_s": attempt.get("elapsed_s"),
        "error": attempt.get("error"),
        "is_range": " .. ".join(split.get("is_range") or []) or None,
        "oos_range": " .. ".join(split.get("oos_range") or []) or None,
        "holdout_range": " .. ".join(split.get("holdout_range") or []) or None,
    }

    for key in (
        "sharpe",
        "ann_return",
        "turnover",
        "max_drawdown",
        "pearson_ic",
        "fitness",
        "n_names",
        "hit_rate",
    ):
        row[f"{key}_full"] = _num(best.get(key))
    # ``ic`` was the pre-rename name of the rank IC in older runs
    row["rank_ic_full"] = _num(best.get("rank_ic", best.get("ic")))

    for segment, prefix in (("in_sample", "is"), ("out_of_sample", "oos"), ("holdout", "holdout")):
        seg = grid.get(segment) or {}
        for key in ("sharpe", "ann_return", "turnover", "max_drawdown"):
            row[f"{key}_{prefix}"] = _num(seg.get(key))
        row[f"rank_ic_{prefix}"] = _num(seg.get("rank_ic", seg.get("ic")))

    for key in ("sharpe", "ann_return", "turnover", "max_drawdown"):
        row[f"{key}_sub"] = _num(sub_metrics.get(key))
    row["rank_ic_sub"] = _num(sub_metrics.get("rank_ic", sub_metrics.get("ic")))
    for segment, prefix in (("is", "is"), ("oos", "oos"), ("holdout", "holdout")):
        seg = sub_segments.get(segment) or {}
        row[f"sub_sharpe_{prefix}"] = _num(seg.get("sharpe"))

    return row


def _read_run(run_dir: Path) -> tuple[list[dict], Optional[dict], Optional[str]]:
    run_json = run_dir / "run.json"
    attempts: list[dict] = []
    llm: Optional[str] = None
    if run_json.exists():
        try:
            payload = json.loads(run_json.read_text(encoding="utf-8"))
            attempts = payload.get("attempts") or []
            llm = payload.get("llm")
        except json.JSONDecodeError:
            attempts = []
    if not attempts:
        jsonl = run_dir / "attempts.jsonl"
        if jsonl.exists():
            for line in jsonl.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        attempts.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    panel_summary = None
    ps = run_dir / "panel_summary.json"
    if ps.exists():
        try:
            panel_summary = json.loads(ps.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            panel_summary = None
    return attempts, panel_summary, llm


def ledger_path_for(runs_dir: str | Path) -> Path:
    """The derived ledger lives in ``experiments/.index/ledger.csv``."""
    return PROJECT_ROOT / "experiments" / ".index" / "ledger.csv"


def rebuild_ledger(
    runs_dir: str | Path = PROJECT_ROOT / "runs",
    out: Optional[str | Path] = None,
) -> pd.DataFrame:
    """Rebuild the ledger from every ``runs/*/`` directory.

    ``out`` defaults to ``experiments/.index/ledger.csv`` so a test or a
    custom ``--runs`` directory writes its own ledger instead of overwriting the
    project one.
    """
    runs_dir = Path(runs_dir)
    out = Path(out) if out is not None else ledger_path_for(runs_dir)
    rows: list[dict] = []
    if runs_dir.exists():
        for run_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
            attempts, panel_summary, llm = _read_run(run_dir)
            for attempt in attempts:
                rows.append(
                    flatten_attempt(run_dir.name, attempt, panel_summary, llm=llm)
                )

    df = pd.DataFrame(rows, columns=list(LEDGER_COLUMNS)) if rows else pd.DataFrame(
        columns=list(LEDGER_COLUMNS)
    )
    if not df.empty:
        df = (
            df.drop_duplicates(subset=["run_id", "hypothesis", "attempt"], keep="last")
            .sort_values(["timestamp", "hypothesis"], na_position="last")
            .reset_index(drop=True)
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    df["verification_status"] = df["verification_status"].astype(object)
    audit = out.parent / "batch10" / "verification.json"
    if audit.exists():
        for item in json.loads(audit.read_text(encoding="utf-8")):
            matched = (df["run_id"] == item["run_id"]) & (df["hypothesis"] == item["hypothesis"])
            df.loc[matched, "verification_status"] = item["verification_status"]
    df.to_csv(out, index=False, encoding="utf-8")

    # keep the human-readable conclusions next to the ledger so they are
    # versioned too (runs/ itself stays local and gitignored)
    reports_dir = out.parent / "reports"
    if runs_dir.exists():
        reports_dir.mkdir(parents=True, exist_ok=True)
        for run_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
            report = run_dir / "report.md"
            if report.exists():
                (reports_dir / f"{run_dir.name}.md").write_text(
                    report.read_text(encoding="utf-8"), encoding="utf-8"
                )
    return df


def load_ledger(path: str | Path = LEDGER_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=list(LEDGER_COLUMNS))
    df = pd.read_csv(path)
    return df.reindex(columns=list(LEDGER_COLUMNS))


def render(df: pd.DataFrame, sort: str = "sharpe_oos", top: int = 30) -> str:
    """Compact markdown view: the whole sample next to the untouched segments."""
    if df.empty:
        return "_ledger is empty: run `python -m factorlab run ...` first_"
    cols = [
        "run_id",
        "hypothesis",
        "decision",
        "verification_status",
        "sharpe_full",
        "sharpe_is",
        "sharpe_oos",
        "sharpe_holdout",
        "ann_return_oos",
        "rank_ic_oos",
        "sharpe_sub",
        "factor_id",
    ]
    cols = [c for c in cols if c in df.columns]
    view = df.copy()
    if sort in view.columns:
        view = view.sort_values(sort, ascending=False, na_position="last")
    view = view.head(max(1, int(top)))
    try:
        from .markdown import md_table

        return md_table(view[cols])
    except Exception:  # pragma: no cover - cosmetic fallback
        return view[cols].to_string(index=False)

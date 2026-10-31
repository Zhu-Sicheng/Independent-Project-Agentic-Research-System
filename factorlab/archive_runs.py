"""Archive local run artifacts and rebuild a batch's readable report.

``python -m factorlab.archive_runs --runs <run_id> ... --batch experiments/batch10``

The raw ``runs/`` directory is gitignored because it is large and machine-local;
this command copies the structured artifacts into the date-ordered
``experiments/<YYYYMMDD>-mining-runs/records/<run_id>/``
and rebuilds ``summary``/``README`` (including the natural-language hypotheses)
from those copies, so the uploaded batch is self-contained.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from .config import PROJECT_ROOT
from .markdown import md_table

RUNS_DIR = PROJECT_ROOT / "runs"
from .experiments_store import EXPERIMENTS, date_of

RECORDS_ROOT = EXPERIMENTS

_HYPOTHESIS_LINE = re.compile(r"^\*\*hypothesis\*\*:\s*(.+)$")
_SECTION = re.compile(r"^##\s+([A-Za-z0-9_\-]+)\s*$")
_LOG_LINE = re.compile(r"^\[([A-Za-z0-9_\-]+)\]\s+(.+)$")


def _read_text(path: Path) -> str:
    raw = path.read_bytes()[:2]
    encoding = "utf-16" if raw == b"\xff\xfe" or raw == b"\xfe\xff" else "utf-8"
    return path.read_text(encoding=encoding, errors="ignore")


def parse_report_hypotheses(path: Path) -> dict[str, str]:
    """Recover ``name -> hypothesis text`` from a run's ``report.md``."""
    out: dict[str, str] = {}
    current: Optional[str] = None
    for line in _read_text(path).splitlines():
        section = _SECTION.match(line.strip())
        if section:
            current = section.group(1)
            continue
        match = _HYPOTHESIS_LINE.match(line.strip())
        if match and current:
            out[current] = match.group(1).strip()
    return out


def parse_log_hypotheses(path: Path) -> dict[str, str]:
    """Recover ``name -> hypothesis text`` from a run log (``[name] text``)."""
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in _read_text(path).splitlines():
        match = _LOG_LINE.match(line.strip())
        if match:
            out[match.group(1)] = match.group(2).strip()
    return out


def archive_runs(
    run_ids: Iterable[str],
    logs: Iterable[str] = (),
    batch_dir: Optional[str] = None,
) -> dict[str, str]:
    """Copy run artifacts into the date-ordered experiment dir; return the hypothesis texts."""
    texts: dict[str, str] = {}
    for run_id in run_ids:
        run_dir = RUNS_DIR / run_id
        if not run_dir.is_dir():
            raise FileNotFoundError(run_dir)
        dest = RECORDS_ROOT / f"{date_of(run_id)}-mining-runs" / "records" / run_id
        dest.mkdir(parents=True, exist_ok=True)
        for item in run_dir.iterdir():
            if item.is_file():
                shutil.copyfile(item, dest / item.name)
        report = dest / "report.md"
        if report.exists():
            texts.update(parse_report_hypotheses(report))

    for log in logs:
        texts.update(parse_log_hypotheses(PROJECT_ROOT / log))

    for run_id in run_ids:
        dest = RECORDS_ROOT / f"{date_of(run_id)}-mining-runs" / "records" / run_id
        journal = dest / "attempts.jsonl"
        if not journal.exists():
            continue
        attempts = [
            json.loads(line)
            for line in journal.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        mapping = {
            attempt["hypothesis"]: texts.get(attempt["hypothesis"], "")
            for attempt in attempts
        }
        (dest / "hypotheses.json").write_text(
            json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    if batch_dir:
        rebuild_batch_readme(
            Path(batch_dir) if Path(batch_dir).is_absolute() else PROJECT_ROOT / batch_dir,
            run_ids,
            texts,
        )
    return texts


def rebuild_batch_readme(batch_dir: Path, run_ids: Iterable[str], texts: dict[str, str]) -> None:
    """Rewrite ``README.md`` with the hypothesis text next to every result."""
    summary = pd.read_csv(batch_dir / "summary.csv")
    attempts_path = batch_dir / "attempts.json"
    records = json.loads(attempts_path.read_text(encoding="utf-8")) if attempts_path.exists() else []
    reviews = {(r["run_id"], r["hypothesis"]): (r.get("review") or {}) for r in records}

    cols = [
        "hypothesis",
        "n_evals",
        "decision",
        "sharpe_full",
        "sharpe_is",
        "sharpe_oos",
        "sharpe_holdout",
        "sharpe_sub",
    ]
    report = json.loads((batch_dir / "verification.json").read_text(encoding="utf-8"))
    invalid = {item["hypothesis"] for item in report if item["verification_status"] != "verified"}

    lines = [
        "# Ten-attempt real-data batch",
        "",
        "Ten completed attempts: four from an interrupted first run and six from its continuation.",
        "The overnight/intraday mechanism repeats across the two runs, so this is ten evaluations,",
        "not ten independent mechanisms. The first four used up to 120 grid evaluations, the",
        "continuation up to 80. Selection uses in-sample (2000–2020) only; OOS is 2021–2024.",
        "The 2025+ holdout has already been inspected during review and is not pristine.",
        "Costs are zero; the capital filter is itself a grid dimension, so the primary and",
        "sub-universe books can coincide.",
        "",
        "Verification status is recorded per attempt:",
    ]
    if invalid:
        lines.append(
            "`invalid_constant_signal` marks a factor whose best window made the signal constant;"
        )
        lines.append(
            "its historical Sharpe came from round-off amplified into positions and must not be used."
        )
    lines += ["", md_table(summary[cols]), ""]

    for row in summary.to_dict("records"):
        review = reviews.get((row["run_id"], row["hypothesis"]), {})
        text = texts.get(row["hypothesis"], "")
        lines += [
            f"## {row['hypothesis']} ({row['run_id']})",
            "",
            f"**Hypothesis**: {text or '_not recorded_'}",
            "",
            f"**Effective expression**: `{row['expression']}`",
            "",
            f"**Decision**: **{row['decision']}**. {review.get('reasoning', '')}",
            "",
            f"![Equity, drawdown and yearly Sharpe]({row['plot']})",
            "",
            f"[Calendar-year statistics]({row['yearly']})",
            "",
        ]
    (batch_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--logs", nargs="*", default=[])
    parser.add_argument("--batch", default=None)
    args = parser.parse_args()
    texts = archive_runs(args.runs, logs=args.logs, batch_dir=args.batch)
    print(f"archived {len(args.runs)} runs, {len(texts)} hypothesis texts")


if __name__ == "__main__":
    main()

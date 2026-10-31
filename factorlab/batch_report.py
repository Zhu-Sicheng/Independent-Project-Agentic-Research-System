"""Summarise a batch of mining sessions from the archived attempt records.

``python -m factorlab.batch_report --prefix p100 --out experiments/batch100``

Reads ``experiments/records/<run_id>/attempts.jsonl`` (archived by the mining
loop), keeps the attempts whose run tag starts with ``--prefix`` and writes a
single ``summary.csv`` + ``README.md``. No backtest is re-run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .config import PROJECT_ROOT
from .markdown import md_table

RECORDS = PROJECT_ROOT / "experiments" / "records"


def _segment(attempt: dict, name: str, key: str):
    grid = attempt.get("grid") or {}
    block = grid.get(name) or {}
    value = block.get(key)
    return value


def collect(prefix: str, records_dir: Path = RECORDS) -> pd.DataFrame:
    rows = []
    if not records_dir.exists():
        return pd.DataFrame()
    for run_dir in sorted(p for p in records_dir.iterdir() if p.is_dir()):
        if not run_dir.name.split("-", 2)[-1].startswith(prefix):
            continue
        journal = run_dir / "attempts.jsonl"
        if not journal.exists():
            continue
        for line in journal.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            attempt = json.loads(line)
            grid = attempt.get("grid") or {}
            if not grid:
                continue
            best = grid.get("best") or {}
            stability = grid.get("stability") or {}
            sub = grid.get("subuniverse") or {}
            review = attempt.get("review") or {}
            spec = attempt.get("spec") or {}
            rows.append(
                {
                    "run_id": run_dir.name,
                    "hypothesis": attempt.get("hypothesis"),
                    "expression": spec.get("expression") or ("<script>" if spec.get("script") else ""),
                    "decision": review.get("decision"),
                    "source": review.get("source"),
                    "n_evals": grid.get("n_evals"),
                    "sharpe_full": best.get("sharpe"),
                    "ann_return_full": best.get("ann_return"),
                    "turnover_full": best.get("turnover"),
                    "max_drawdown_full": best.get("max_drawdown"),
                    "rank_ic_full": best.get("rank_ic", best.get("ic")),
                    "sharpe_is": _segment(attempt, "in_sample", "sharpe"),
                    "sharpe_oos": _segment(attempt, "out_of_sample", "sharpe"),
                    "ann_return_oos": _segment(attempt, "out_of_sample", "ann_return"),
                    "sharpe_holdout": _segment(attempt, "holdout", "sharpe"),
                    "sharpe_sub": (sub.get("metrics") or {}).get("sharpe"),
                    "stability_sub_sharpe": stability.get("subuniverse_sharpe"),
                    "stability_min_corr": stability.get("min_pnl_corr"),
                    "stability_flags": ",".join(stability.get("flags") or []),
                    "factor_id": attempt.get("factor_id"),
                }
            )
    return pd.DataFrame(rows)


def write_batch(prefix: str, out: str | Path, records_dir: Path = RECORDS) -> Path:
    out = Path(out)
    if not out.is_absolute():
        out = PROJECT_ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    frame = collect(prefix, records_dir)
    if frame.empty:
        raise SystemExit(f"no attempts found for prefix {prefix!r}")
    frame = frame.sort_values(["decision", "sharpe_oos"], ascending=[True, False])
    frame.to_csv(out / "summary.csv", index=False, encoding="utf-8")

    decisions = frame["decision"].value_counts().to_dict()
    accepted = frame[frame["decision"] == "accept"]
    flagged = frame[frame["stability_flags"].fillna("") != ""]
    lines = [
        f"# Batch `{prefix}`",
        "",
        f"- attempts: **{len(frame)}** across {frame['run_id'].nunique()} sessions",
        f"- decisions: {decisions}",
        f"- accepted: {len(accepted)}",
        f"- with stability flags: {len(flagged)}",
        "",
        "Selection uses in-sample (2000–2020) only; OOS is 2021–2024 and the 2025+",
        "holdout has been inspected repeatedly. Costs are zero. The capital filter is",
        "a grid dimension, so the sub-universe book can coincide with the primary one.",
        "",
        md_table(
            frame[
                [
                    "hypothesis",
                    "decision",
                    "sharpe_full",
                    "sharpe_oos",
                    "sharpe_holdout",
                    "sharpe_sub",
                    "stability_flags",
                ]
            ]
            .head(40)
            .round(3)
        ),
        "",
        f"Full table: `summary.csv` ({len(frame)} rows).",
    ]
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default="p100")
    parser.add_argument("--out", default="experiments/batch100")
    args = parser.parse_args()
    target = write_batch(args.prefix, args.out)
    print(f"batch report written to {target}")


if __name__ == "__main__":
    main()

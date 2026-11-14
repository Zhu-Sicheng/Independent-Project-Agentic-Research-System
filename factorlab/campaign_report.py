"""Summarise a mining campaign: every evaluated expression across runs in one table.

The merged pipeline writes one ``evaluations.json`` per run; this module merges
them (deduplicating by canonical expression), joins the in-sample and display
(OOS/holdout) metrics, and writes a publishable ``summary.csv`` + ``README.md``::

    python -m factorlab.campaign_report --out-root experiments/20261114-systemv1-500 \
        --name systemv1-500

The report is explicit about the data-isolation contract: selection/review used
in-sample only; OOS/holdout come from the display layer and are presented, never
optimised.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .config import PROJECT_ROOT
from .markdown import md_table

SUMMARY_COLUMNS = [
    "run_id",
    "round",
    "hypothesis",
    "expression",
    "decision",
    "review_source",
    "is_sharpe",
    "is_ann_return",
    "is_turnover",
    "is_max_drawdown",
    "is_rank_ic",
    "is_n_evals",
    "subuniverse_sharpe",
    "oos_sharpe",
    "oos_ann_return",
    "oos_rank_ic",
    "holdout_sharpe",
    "holdout_ann_return",
    "holdout_rank_ic",
    "revision",
    "updated_at",
]


def _metric(block: Optional[dict], key: str):
    try:
        value = float((block or {}).get(key))
    except (TypeError, ValueError):
        return np.nan
    return value if np.isfinite(value) else np.nan


def load_records(out_root: str | Path) -> tuple[list[dict], list[str]]:
    """Merge every run's ``evaluations.json``; return (records, run ids)."""
    out_root = Path(out_root)
    if not out_root.is_absolute():
        out_root = PROJECT_ROOT / out_root
    rows: list[dict] = []
    run_ids: list[str] = []
    for path in sorted(out_root.glob("*/evaluations.json")):
        run_id = path.parent.name
        run_ids.append(run_id)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for record in payload.get("records") or []:
            is_block = (record.get("is") or {}).get("metrics") or {}
            display = record.get("display") or {}
            segments = display.get("segments") or {}
            stability = record.get("stability_is") or {}
            rows.append(
                {
                    "run_id": run_id,
                    "round": record.get("round"),
                    "hypothesis": record.get("hypothesis"),
                    "expression": record.get("expression") or record.get("expression_raw"),
                    "decision": record.get("decision"),
                    "review_source": record.get("review_source"),
                    "is_sharpe": _metric(is_block, "sharpe"),
                    "is_ann_return": _metric(is_block, "ann_return"),
                    "is_turnover": _metric(is_block, "turnover"),
                    "is_max_drawdown": _metric(is_block, "max_drawdown"),
                    "is_rank_ic": _metric(is_block, "rank_ic"),
                    "is_n_evals": (record.get("is") or {}).get("n_evals"),
                    "subuniverse_sharpe": _metric(stability, "subuniverse_sharpe"),
                    "oos_sharpe": _metric(segments.get("oos"), "sharpe"),
                    "oos_ann_return": _metric(segments.get("oos"), "ann_return"),
                    "oos_rank_ic": _metric(segments.get("oos"), "rank_ic"),
                    "holdout_sharpe": _metric(segments.get("holdout"), "sharpe"),
                    "holdout_ann_return": _metric(segments.get("holdout"), "ann_return"),
                    "holdout_rank_ic": _metric(segments.get("holdout"), "rank_ic"),
                    "revision": record.get("revision"),
                    "updated_at": record.get("updated_at"),
                }
            )
    return rows, run_ids


def build_summary(rows: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(rows, columns=SUMMARY_COLUMNS)
    if frame.empty:
        return frame
    # the same canonical expression can be re-evaluated (revision); keep the latest
    frame = (
        frame.sort_values(["expression", "updated_at"], na_position="first")
        .drop_duplicates(subset=["expression"], keep="last")
        .sort_values("is_sharpe", ascending=False, na_position="last")
        .reset_index(drop=True)
    )
    return frame


def _stats(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"n": 0}
    is_sharpe = frame["is_sharpe"].dropna()
    oos = frame["oos_sharpe"].dropna()
    hold = frame["holdout_sharpe"].dropna()

    def _share(series: pd.Series, threshold: float) -> float:
        return float((series > threshold).mean()) if len(series) else np.nan

    both = frame.dropna(subset=["oos_sharpe", "holdout_sharpe"])
    return {
        "n": int(len(frame)),
        "n_decision": frame["decision"].value_counts(dropna=False).to_dict(),
        "is_median": float(is_sharpe.median()) if len(is_sharpe) else np.nan,
        "is_p90": float(is_sharpe.quantile(0.9)) if len(is_sharpe) else np.nan,
        "is_share_gt1": _share(is_sharpe, 1.0),
        "oos_median": float(oos.median()) if len(oos) else np.nan,
        "oos_share_positive": _share(oos, 0.0),
        "holdout_median": float(hold.median()) if len(hold) else np.nan,
        "holdout_share_positive": _share(hold, 0.0),
        "both_positive_share": (
            float(((both["oos_sharpe"] > 0) & (both["holdout_sharpe"] > 0)).mean())
            if len(both)
            else np.nan
        ),
        "n_with_display": int(len(both)),
    }


def write_report(out_root: str | Path, name: str, top: int = 20) -> pd.DataFrame:
    out_root = Path(out_root)
    if not out_root.is_absolute():
        out_root = PROJECT_ROOT / out_root
    rows, run_ids = load_records(out_root)
    frame = build_summary(rows)
    stats = _stats(frame)
    frame.to_csv(out_root / "summary.csv", index=False)

    cols = [
        "hypothesis",
        "decision",
        "is_sharpe",
        "is_ann_return",
        "is_turnover",
        "is_rank_ic",
        "oos_sharpe",
        "oos_ann_return",
        "holdout_sharpe",
        "subuniverse_sharpe",
        "run_id",
    ]
    head = frame.head(top)[cols].copy()
    for column in ("is_ann_return", "oos_ann_return"):
        head[column] = head[column].map(lambda v: f"{v:.1%}" if np.isfinite(v) else "-")
    for column in ("is_sharpe", "oos_sharpe", "holdout_sharpe", "subuniverse_sharpe"):
        head[column] = head[column].map(lambda v: f"{v:.3f}" if np.isfinite(v) else "-")
    head["is_rank_ic"] = head["is_rank_ic"].map(lambda v: f"{v:.4f}" if np.isfinite(v) else "-")

    lines = [
        f"# Published results: `{name}`",
        "",
        f"- runs: {len(run_ids)} ({', '.join(run_ids[:6])}{', ...' if len(run_ids) > 6 else ''})",
        f"- evaluated expressions: {stats.get('n', 0)} unique canonical forms",
        f"- decisions: {stats.get('n_decision', {})}",
        "- data isolation: the optimisation loop and the reviewer saw in-sample only; "
        "OOS/holdout are display-only and were never fed back",
        "",
        "## Headline statistics",
        "",
        "| metric | value |",
        "|---|---|",
        f"| IS Sharpe median / p90 | {stats.get('is_median', float('nan')):.3f} / "
        f"{stats.get('is_p90', float('nan')):.3f} |",
        f"| share of expressions with IS Sharpe > 1 | {stats.get('is_share_gt1', float('nan')):.1%} |",
        f"| OOS Sharpe median | {stats.get('oos_median', float('nan')):.3f} |",
        f"| share of expressions with OOS Sharpe > 0 | {stats.get('oos_share_positive', float('nan')):.1%} |",
        f"| holdout Sharpe median | {stats.get('holdout_median', float('nan')):.3f} |",
        f"| share with both OOS and holdout positive | {stats.get('both_positive_share', float('nan')):.1%} "
        f"(n={stats.get('n_with_display', 0)}) |",
        "",
        f"## Top {min(top, len(frame))} by in-sample Sharpe",
        "",
        md_table(head),
        "",
        "`summary.csv` has every evaluated expression with IS, sub-universe, OOS and "
        "holdout metrics, the hypothesis and the reviewer decision.",
        "",
    ]
    (out_root / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return frame


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-root", required=True, help="campaign directory holding run subdirs")
    parser.add_argument("--name", default=None, help="publication name (default: directory name)")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args(argv)
    out_root = Path(args.out_root)
    name = args.name or out_root.name
    frame = write_report(out_root, name, top=args.top)
    print(f"wrote {len(frame)} unique expressions to {out_root}/summary.csv")


if __name__ == "__main__":
    main()

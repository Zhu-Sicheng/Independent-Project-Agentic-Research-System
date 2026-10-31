"""Redraw a batch's figures from saved daily pnl without replaying backtests.

``python -m factorlab.replot --batch experiments/batch10``
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .backtest.split import resolve_split
from .config import PROJECT_ROOT
from .data import load_processed
from .view import plot_from_daily


def replot(batch_dir: str | Path) -> int:
    batch_dir = Path(batch_dir)
    if not batch_dir.is_absolute():
        batch_dir = PROJECT_ROOT / batch_dir
    summary = pd.read_csv(batch_dir / "summary.csv")
    if summary.empty:
        raise SystemExit(f"no rows in {batch_dir / 'summary.csv'}")

    panel = load_processed(PROJECT_ROOT / "data" / "processed" / "panel")
    masks = resolve_split(panel.dates, panel.meta.get("default_split"))

    drawn = 0
    for row in summary.to_dict("records"):
        plot_name = str(row.get("plot") or "")
        if not plot_name:
            continue
        daily = batch_dir / plot_name.replace(".png", "_daily.csv")
        if not daily.exists():
            print(f"skip {row['hypothesis']}: missing {daily.name}")
            continue
        segments = {
            seg: {
                "sharpe": row.get(f"sharpe_{seg}"),
                "ann_return": row.get(f"ann_return_{seg}"),
                "turnover": row.get(f"turnover_{seg}"),
                "max_drawdown": row.get(f"max_drawdown_{seg}"),
                "rank_ic": row.get(f"rank_ic_{seg}"),
            }
            for seg in ("is", "oos", "holdout")
        }
        plot_from_daily(
            daily,
            masks,
            segments,
            batch_dir / plot_name,
            f"{row['hypothesis']} | {row.get('expression', '')}",
        )
        drawn += 1
    print(f"redrew {drawn} figures in {batch_dir}")
    return drawn


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", default="experiments/batch10")
    args = parser.parse_args()
    replot(args.batch)


if __name__ == "__main__":
    main()

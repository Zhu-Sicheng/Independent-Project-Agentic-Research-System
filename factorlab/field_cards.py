"""Field cards: one evolving card per panel field.

Each card stores two things and is refreshed from the experiment store rather
than hand-edited:

1. **EDA evidence** -- what Agent 1's data-understanding pass said about the raw
   columns that map to this panel field (`field_catalog.csv`, translated through
   ``agent_adapter.FIELD_MAP``);
2. **backtest evidence** -- every evaluated expression that uses the field, with
   its idea/hypothesis, expression, reviewer decision and in-sample / display
   metrics.

Rebuilding is idempotent: cards are derived from ``evaluations.json`` files and
Agent 1 catalogs, so each campaign run refreshes them with the newest evidence.

    python -m factorlab.field_cards --rebuild
    python -m factorlab.field_cards --field close
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from .agent_adapter import FIELD_MAP
from .config import PROJECT_ROOT
from .expr import parser as P
from .markdown import md_table

CARDS_DIR = PROJECT_ROOT / "experiments" / "field_cards"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

#: panel fields that have a stored column and therefore can have EDA evidence
STORED_FIELDS = ("open", "high", "low", "close", "volume", "cap")
#: every field the current panel can serve (stored + derived)
PANEL_VOCAB = frozenset(STORED_FIELDS) | {
    "returns", "log_returns", "amount", "adv20", "cap_rank",
    "range", "close_position", "intraday_return", "overnight_return",
}
#: rows shown in the markdown table; the JSON keeps the complete history
MAX_TABLE_ROWS = 100


def _catalog_to_panel(field: str) -> Optional[str]:
    """Translate a raw data-contract field name to the panel vocabulary."""
    if field in FIELD_MAP:
        return FIELD_MAP[field]
    normalised = str(field).strip()
    if normalised in FIELD_MAP:
        return FIELD_MAP[normalised]
    return None


def _evaluations_paths(root: Path) -> list[Path]:
    """Every pipeline run's evaluations.json under the experiments tree."""
    paths: list[Path] = []
    for pattern in (
        "*/evaluations.json",
        "*/*/evaluations.json",
        "*/runs/*/evaluations.json",
    ):
        paths.extend(sorted(root.glob(pattern)))
    return paths


def _catalog_paths(root: Path) -> list[Path]:
    return sorted(root.glob("*/runs/*/agent1/*/field_catalog.csv")) + sorted(
        root.glob("*/*/agent1/*/field_catalog.csv")
    )


def collect_eda(root: Path | str = EXPERIMENTS_DIR) -> dict[str, list[dict]]:
    """field -> list of EDA catalog rows (deduplicated by dataset + raw name)."""
    root = Path(root)
    eda: dict[str, list[dict]] = {}
    seen: set[tuple] = set()
    for catalog in _catalog_paths(root):
        try:
            frame = pd.read_csv(catalog)
        except (OSError, pd.errors.ParserError):
            continue
        frame.columns = [str(c).lstrip("\ufeff") for c in frame.columns]
        for row in frame.to_dict("records"):
            raw = str(row.get("name") or "")
            field = _catalog_to_panel(raw)
            if field is None:
                continue
            key = (field, row.get("dataset_id"), raw)
            if key in seen:
                continue
            seen.add(key)
            eda.setdefault(field, []).append(
                {
                    "dataset_id": row.get("dataset_id"),
                    "source_field": raw,
                    "semantic_role": row.get("semantic_role"),
                    "factor_usage": row.get("factor_usage"),
                    "unit": row.get("unit"),
                    "missing_fraction": row.get("missing_fraction"),
                    "blocking_reasons": row.get("blocking_reasons"),
                    "catalog": str(catalog),
                }
            )
    return eda


def _expression_fields(expression: str) -> list[str]:
    try:
        return P.collect_vars(P.parse(expression))
    except Exception:
        return []


def _float(value) -> Optional[float]:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if value == value and abs(value) != float("inf") else None


def collect_backtests(root: Path | str = EXPERIMENTS_DIR) -> list[dict]:
    """One row per (run, expression) evaluation, attributed to every field it uses."""
    root = Path(root)
    rows: list[dict] = []
    seen: set[tuple] = set()
    for path in _evaluations_paths(root):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        run_id = path.parent.name
        for record in payload.get("records") or []:
            expression = record.get("expression") or record.get("expression_raw")
            if not expression:
                continue
            key = (run_id, expression)
            if key in seen:
                continue
            seen.add(key)
            fields = _expression_fields(expression)
            if not fields:
                continue
            is_metrics = (record.get("is") or {}).get("metrics") or {}
            segments = ((record.get("display") or {}).get("segments")) or {}
            oos = segments.get("oos") or {}
            holdout = segments.get("holdout") or {}
            stability = record.get("stability_is") or {}
            base = {
                "run_id": run_id,
                "round": record.get("round"),
                "hypothesis": record.get("hypothesis") or "",
                "expression": expression,
                "decision": record.get("decision"),
                "is_sharpe": _float(is_metrics.get("sharpe")),
                "is_turnover": _float(is_metrics.get("turnover")),
                "is_rank_ic": _float(is_metrics.get("rank_ic")),
                "oos_sharpe": _float(oos.get("sharpe")),
                "holdout_sharpe": _float(holdout.get("sharpe")),
                "subuniverse_sharpe": _float(stability.get("subuniverse_sharpe")),
                "updated_at": record.get("updated_at"),
            }
            for field in fields:
                rows.append({"field": field, **base})
    return rows


def _card_markdown(field: str, eda_rows: list[dict], backtests: list[dict]) -> str:
    in_panel = field in PANEL_VOCAB
    lines = [
        f"# Field card: `{field}`",
        "",
        f"_updated {time.strftime('%Y-%m-%d %H:%M:%S')}_",
        "",
        f"- in current panel vocabulary: **{'yes' if in_panel else 'no (raw data-contract field, historical records only)'}**",
        "",
    ]
    lines += ["## EDA evidence", ""]
    if eda_rows:
        table = pd.DataFrame(eda_rows)[
            ["source_field", "dataset_id", "semantic_role", "factor_usage", "unit",
             "missing_fraction", "blocking_reasons"]
        ]
        lines.append(md_table(table))
    else:
        lines.append("_no Agent-1 EDA evidence for this field (derived or not in raw data)_")
    lines += ["", f"## Backtest evidence ({len(backtests)})", ""]
    if backtests:
        frame = pd.DataFrame(backtests).sort_values(
            "is_sharpe", ascending=False, na_position="last"
        )
        view = frame[
            ["run_id", "round", "hypothesis", "expression", "decision",
             "is_sharpe", "is_turnover", "is_rank_ic", "oos_sharpe",
             "holdout_sharpe", "subuniverse_sharpe"]
        ].copy()
        for column in ("is_sharpe", "oos_sharpe", "holdout_sharpe", "subuniverse_sharpe"):
            view[column] = view[column].map(lambda v: f"{v:.3f}" if v is not None else "-")
        view["is_turnover"] = view["is_turnover"].map(
            lambda v: f"{v:.1f}" if v is not None else "-"
        )
        view["is_rank_ic"] = view["is_rank_ic"].map(
            lambda v: f"{v:.4f}" if v is not None else "-"
        )
        view["hypothesis"] = view["hypothesis"].map(lambda s: str(s)[:160])
        view["expression"] = view["expression"].map(lambda s: str(s)[:200])
        total = len(view)
        view = view.head(MAX_TABLE_ROWS)
        lines.append(md_table(view))
        if total > MAX_TABLE_ROWS:
            lines.append(f"_showing top {MAX_TABLE_ROWS} of {total} backtests by IS Sharpe; "
                         f"the full history is in `{field}.json`_")
        sharpes = [row["is_sharpe"] for row in backtests if row["is_sharpe"] is not None]
        oos = [row["oos_sharpe"] for row in backtests if row["oos_sharpe"] is not None]
        best = max(backtests, key=lambda r: r["is_sharpe"] or -1e9, default=None)
        lines += ["", "## Summary", ""]
        if sharpes:
            series = pd.Series(sharpes)
            lines.append(f"- backtests: {len(backtests)}, median IS Sharpe {series.median():.3f}, "
                         f"p90 {series.quantile(0.9):.3f}")
        if best and best.get("is_sharpe") is not None:
            lines.append(f"- best IS Sharpe {best['is_sharpe']:.3f}: `{best['expression']}`")
        if oos:
            lines.append(f"- share of expressions with OOS Sharpe > 0: "
                         f"{sum(1 for v in oos if v > 0) / len(oos):.1%} (n={len(oos)})")
    else:
        lines.append("_no backtest evidence yet_")
    return "\n".join(lines) + "\n"


def update_field_cards(
    experiments_root: Path | str = EXPERIMENTS_DIR,
    cards_dir: Path | str = CARDS_DIR,
) -> int:
    """Rebuild every field card from the experiment store; return card count."""
    root = Path(experiments_root)
    cards_dir = Path(cards_dir)
    eda = collect_eda(root)
    backtests = collect_backtests(root)
    grouped: dict[str, list[dict]] = {}
    for row in backtests:
        grouped.setdefault(row["field"], []).append(row)
    fields = sorted(set(eda) | set(grouped) | set(STORED_FIELDS))
    cards_dir.mkdir(parents=True, exist_ok=True)
    index_rows = []
    for field in fields:
        rows = grouped.get(field, [])
        (cards_dir / f"{field}.md").write_text(
            _card_markdown(field, eda.get(field, []), rows), encoding="utf-8"
        )
        (cards_dir / f"{field}.json").write_text(
            json.dumps(
                {"field": field, "eda": eda.get(field, []), "backtests": rows},
                indent=2, ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        sharpes = [r["is_sharpe"] for r in rows if r["is_sharpe"] is not None]
        oos = [r["oos_sharpe"] for r in rows if r["oos_sharpe"] is not None]
        index_rows.append(
            {
                "field": field,
                "n_backtests": len(rows),
                "n_eda_sources": len(eda.get(field, [])),
                "median_is_sharpe": float(pd.Series(sharpes).median()) if sharpes else None,
                "best_is_sharpe": float(max(sharpes)) if sharpes else None,
                "share_oos_positive": (
                    sum(1 for v in oos if v > 0) / len(oos) if oos else None
                ),
            }
        )
    pd.DataFrame(index_rows).to_csv(cards_dir / "index.csv", index=False)
    return len(fields)


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiments", default=str(EXPERIMENTS_DIR))
    parser.add_argument("--out", default=str(CARDS_DIR))
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--field", default=None, help="print one card and exit")
    args = parser.parse_args(argv)
    cards_dir = Path(args.out)
    if args.field:
        card = cards_dir / f"{args.field}.md"
        if not card.exists():
            update_field_cards(args.experiments, args.out)
        print(card.read_text(encoding="utf-8"))
        return
    count = update_field_cards(args.experiments, args.out)
    print(f"refreshed {count} field cards in {cards_dir}")


if __name__ == "__main__":
    main()

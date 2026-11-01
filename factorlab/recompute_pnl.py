"""Recompute backtest statistics and redraw display panels under the current pnl mode.

The project now reports cumulative PnL as a plain sum of daily net pnl
(``cumsum``). This tool replays the stored IS-chosen configuration of every
evaluated factor on the in-sample and full panels and refreshes:

* ``is.metrics`` -- in-sample metrics (the grid's Sharpe ranking is unchanged by
  the pnl aggregation, so the stored decisions stay valid),
* ``stability_is`` -- the in-sample robustness battery,
* ``display`` -- OOS/holdout segment metrics plus the re-drawn figure
  (``equity = pnl.cumsum()``).

It does not call any agent and never shows OOS/holdout inside the optimisation
evidence: the display block remains presentation-only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from .config import PROJECT_ROOT, US_EQUITY_SPLIT
from .refresh_display import _load_ideas, _resolve_experiment, _run_dirs
from .stability import stability_summary
from .xy_pipeline import (
    IS_END_DEFAULT,
    _grid_settings,
    _load_factor,
    display_labels,
    split_is_panel,
)
from .xy_results import _write_evaluations, load_evaluations, upsert_evaluations


def recompute_experiment(
    experiment: Path,
    panel_dir: Optional[Path] = None,
    research_end: str = IS_END_DEFAULT,
    run_ids: Optional[list[str]] = None,
    stability: bool = True,
    verbose: bool = True,
    pnl_mode: str = "additive",
) -> dict:
    from factorlab.backtest import metrics as M
    from factorlab.backtest.engine import run_backtest_with_subuniverse
    from factorlab.backtest.split import resolve_split, segment_metrics
    from factorlab.data import load_processed
    from factorlab.view import draw_panels

    panel_dir = panel_dir or PROJECT_ROOT / "data" / "processed" / "panel"
    panel_full = load_processed(panel_dir)
    panel_is = split_is_panel(panel_full, research_end)
    masks = resolve_split(panel_full.dates, US_EQUITY_SPLIT)
    runs = _run_dirs(experiment)
    if run_ids:
        wanted = set(run_ids)
        runs = [run for run in runs if run.name in wanted]
    refreshed = 0
    for run_dir in runs:
        evaluation_file = run_dir / "evaluations.json"
        if not evaluation_file.exists():
            continue
        records = load_evaluations(evaluation_file)
        if not records:
            continue
        run_id = run_dir.name
        state_file = run_dir / "run.json"
        if state_file.exists():
            try:
                run_id = json.loads(state_file.read_text(encoding="utf-8")).get("run_id", run_id)
            except (json.JSONDecodeError, OSError):
                pass
        labels = display_labels(_load_ideas(run_dir), records)
        display_root = run_dir / "display"
        display_root.mkdir(parents=True, exist_ok=True)
        for record in records:
            if record.get("status") != "evaluated" or not record.get("expression"):
                continue
            expression = str(record["expression"])
            config = (record.get("is") or {}).get("config") or {}
            windows = config.get("windows") or []
            settings = _grid_settings({"best": config}, pnl_mode)
            mode = getattr(settings, "pnl_mode", "additive")
            info = labels.get(record.get("expression_id")) or {}
            label = info.get("label") or "factor"
            title = f"{label} · {info['slug']}" if info.get("slug") else label
            try:
                # --- in-sample statistics --------------------------------------
                factor_is = _load_factor(panel_is, expression, windows)
                result_is = run_backtest_with_subuniverse(factor_is, panel_is, settings)
                record["is"] = {
                    "n_evals": (record.get("is") or {}).get("n_evals"),
                    "metrics": result_is.metrics,
                    "config": config,
                }
                if stability:
                    attempt_like = {
                        "hypothesis": record.get("expression_id"),
                        "spec": {"kind": "expression", "expression": expression},
                        "grid": {"best": config},
                    }
                    record["stability_is"] = stability_summary(panel_is, attempt_like)
                # --- display statistics (presentation only) --------------------
                factor_full = _load_factor(panel_full, expression, windows)
                result_full = run_backtest_with_subuniverse(factor_full, panel_full, settings)
                result_full.segments = segment_metrics(
                    result_full.pnl,
                    result_full.turnover,
                    result_full.ic,
                    factor_full,
                    masks,
                    ann=settings.ann,
                    mode=mode,
                )
                result_full.segments["full"] = M.summarise_pnl(
                    result_full.pnl,
                    result_full.turnover,
                    result_full.ic,
                    ann=settings.ann,
                    mode=mode,
                )
                target = display_root / str(record["expression_id"])
                target.mkdir(parents=True, exist_ok=True)
                draw_panels(
                    result_full.pnl,
                    result_full.turnover,
                    result_full.ic,
                    result_full.segments,
                    masks,
                    target / "pnl.png",
                    title,
                    mode=mode,
                )
                previous = record.get("display") or {}
                record["display"] = {
                    "segments": result_full.segments,
                    "figure": (target / "pnl.png").relative_to(run_dir).as_posix(),
                    "stability_dir": previous.get("stability_dir"),
                    "label": info.get("label"),
                    "slug": info.get("slug"),
                    "hypothesis": info.get("hypothesis"),
                    "oos_sharpe": (result_full.segments.get("oos") or {}).get("sharpe"),
                    "holdout_sharpe": (result_full.segments.get("holdout") or {}).get("sharpe"),
                }
                refreshed += 1
                if verbose:
                    is_sharpe = (result_full.segments.get("is") or {}).get("sharpe")
                    oos = record["display"]["oos_sharpe"]
                    print(
                        f"[recompute] {run_dir.name}/{label}: IS {is_sharpe:+.2f} | OOS {oos:+.2f}",
                        flush=True,
                    )
            except Exception as exc:  # pragma: no cover - defensive
                record["display_error"] = f"{type(exc).__name__}: {exc}"
                if verbose:
                    print(f"[recompute] {run_dir.name} failed: {exc}", flush=True)
        _write_evaluations(evaluation_file, records)

    merged = experiment / "evaluations.json"
    if merged.exists():
        merged.unlink()
    merged_count = 0
    for run_dir in _run_dirs(experiment):
        evaluation_file = run_dir / "evaluations.json"
        if not evaluation_file.exists():
            continue
        records = load_evaluations(evaluation_file)
        if records:
            merged_count += upsert_evaluations(merged, records, run_dir.name)["inserted"]
    return {"refreshed_records": refreshed, "merged_records": merged_count}


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, help="dated experiment directory or its slug")
    parser.add_argument("--panel", default=None, help="processed panel directory")
    parser.add_argument("--research-end", default=IS_END_DEFAULT, help="in-sample cutoff")
    parser.add_argument("--runs", default="", help="comma separated run ids (default: all)")
    parser.add_argument("--no-stability", action="store_true", help="skip the IS stability battery")
    parser.add_argument("--pnl-mode", choices=("additive", "compound"), default="additive")
    args = parser.parse_args(argv)
    experiment = _resolve_experiment(args.experiment)
    run_ids = [item.strip() for item in args.runs.split(",") if item.strip()]
    result = recompute_experiment(
        experiment,
        panel_dir=Path(args.panel) if args.panel else None,
        research_end=args.research_end,
        run_ids=run_ids or None,
        stability=not args.no_stability,
        pnl_mode=args.pnl_mode,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

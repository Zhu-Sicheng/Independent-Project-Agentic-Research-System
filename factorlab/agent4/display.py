"""Agent 4b -- display layer: OOS/holdout statistics and figures.

Presentation material only: this module is allowed to see the full panel because
its output is never fed back to the agents or the reviewer. The label scheme is
``H<i>-F<j>`` (see ``agent4.labels``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .evaluation import _grid_settings, _load_factor

def display_evaluation(
    panel_full,
    records: list[dict],
    run_id: str,
    output_root: Path,
    split=None,
    verbose: bool = True,
    only_missing: bool = True,
    labels: Optional[dict] = None,
    compute_stability: bool = True,
    redraw: bool = False,
    pnl_mode: str = "additive",
) -> list[dict]:
    """Re-apply the IS-chosen configuration to the full panel and draw it.

    The output here is presentation material only: it is never passed back to
    the agents or the reviewer.
    """
    from factorlab.backtest.engine import run_backtest_with_subuniverse
    from factorlab.backtest.split import resolve_split, segment_metrics
    from factorlab.config import US_EQUITY_SPLIT
    from factorlab.stability import run_stability
    from factorlab.view import draw_panels

    split = split or US_EQUITY_SPLIT
    masks = resolve_split(panel_full.dates, split)
    display_root = output_root / "display"
    display_root.mkdir(parents=True, exist_ok=True)

    drawn = 0
    for record in records:
        if record.get("status") != "evaluated" or not record.get("expression"):
            continue
        if only_missing and record.get("display") and not redraw:
            continue
        drawn += 1
        info = (labels or {}).get(record.get("expression_id")) or {}
        label = info.get("label") or f"factor {drawn:02d}"
        title = f"{label} · {info['slug']}" if info.get("slug") else label
        try:
            config = (record.get("is") or {}).get("config") or {}
            settings = _grid_settings({"best": config}, pnl_mode)
            windows = config.get("windows") or []
            factor = _load_factor(panel_full, record["expression"], windows)
            result = run_backtest_with_subuniverse(factor, panel_full, settings)
            result.segments = segment_metrics(
                result.pnl, result.turnover, result.ic, factor, masks,
                mode=getattr(settings, "pnl_mode", "additive"),
            )
            # segment_metrics aliases full=is when no full mask exists; the display
            # layer must show the true full-sample metric instead
            from factorlab.backtest import metrics as _M

            result.segments["full"] = _M.summarise_pnl(
                result.pnl, result.turnover, result.ic, ann=settings.ann,
                mode=getattr(settings, "pnl_mode", "additive"),
            )
            target = display_root / str(record["expression_id"])
            target.mkdir(parents=True, exist_ok=True)
            draw_panels(
                result.pnl,
                result.turnover,
                result.ic,
                result.segments,
                masks,
                target / "pnl.png",
                title,
            )
            attempt_like = {
                "hypothesis": record["expression_id"],
                "spec": {"kind": "expression", "expression": record["expression"]},
                "grid": {"best": config},
            }
            stability_dir = None
            if compute_stability:
                stability_dir = run_stability(
                    panel_full, attempt_like, run_id, out_dir=target / "stability"
                )
            elif isinstance(record.get("display"), dict):
                stability_dir = record["display"].get("stability_dir")
            record["display"] = {
                "segments": result.segments,
                "figure": (target / "pnl.png").relative_to(output_root).as_posix(),
                "stability_dir": (
                    (Path(stability_dir).relative_to(output_root).as_posix()
                     if stability_dir and Path(stability_dir).is_absolute()
                     and output_root in Path(stability_dir).parents
                     else str(stability_dir) if stability_dir else None)
                ),
                "label": info.get("label"),
                "slug": info.get("slug"),
                "hypothesis": info.get("hypothesis"),
                "oos_sharpe": (result.segments.get("oos") or {}).get("sharpe"),
                "holdout_sharpe": (result.segments.get("holdout") or {}).get("sharpe"),
            }
            if verbose:
                oos = record["display"]["oos_sharpe"]
                is_sharpe = (result.segments.get("is") or {}).get("sharpe")
                print(
                    f"  [display] {record['expression_id']}: IS {is_sharpe:+.2f} | OOS {oos:+.2f}",
                    flush=True,
                )
        except Exception as exc:  # pragma: no cover - defensive
            record["display_error"] = f"{type(exc).__name__}: {exc}"
    return records

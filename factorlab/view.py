"""Inspect one experiment: rebuild its factor, plot it, tabulate it.

Usage::

    python -m factorlab view --list
    python -m factorlab view --run 20261031-083828-e2e
    python -m factorlab view --run 20261031-083828-e2e --hypothesis overnight_intraday_return_divergence

The raw ``runs/`` directory stores the spec and the winning configuration but not
the factor matrix, so the view rebuilds the factor from the spec, re-runs the
backtest on the full panel, and slices the resulting pnl into the IS / OOS /
holdout segments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .backtest.engine import run_backtest_with_subuniverse, subuniverse_mask
from .backtest.split import resolve_split, segment_metrics
from .config import PROJECT_ROOT, BacktestSettings
from .data.panel import PanelStore
from .experiments import LEDGER_PATH, load_ledger, render
from .expr.evaluator import evaluate
from .expr import parser as P
from .expr.script import run_script
from .markdown import md_table

PLOTS_DIR = PROJECT_ROOT / "experiments" / "plots"


def _run_dir(run: str) -> Path:
    path = Path(run)
    if path.is_dir():
        return path
    for root in (PROJECT_ROOT / "runs", PROJECT_ROOT / "experiments" / "records"):
        candidate = root / run
        if candidate.is_dir():
            return candidate
    matches = sorted((PROJECT_ROOT / "runs").glob(f"*{run}*"))
    dirs = [m for m in matches if m.is_dir()]
    if len(dirs) == 1:
        return dirs[0]
    if not dirs:
        raise FileNotFoundError(f"no run matching {run!r} under runs/")
    raise ValueError(f"{run!r} matches several runs: {[d.name for d in dirs]}")


def load_attempt(run: str, hypothesis: Optional[str] = None) -> tuple[Path, dict]:
    run_dir = _run_dir(run)
    journal = run_dir / "attempts.jsonl"
    if journal.exists():
        attempts = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        payload = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        attempts = payload.get("attempts") or []
    if not attempts:
        raise ValueError(f"{run_dir.name} has no attempts")
    if hypothesis:
        matched = [a for a in attempts if a.get("hypothesis") == hypothesis]
        if not matched:
            names = sorted({a.get("hypothesis") for a in attempts})
            raise KeyError(f"{hypothesis!r} not in {run_dir.name}; available: {names}")
        attempt = matched[-1]
    else:
        attempt = attempts[-1]
    return run_dir, attempt


def winning_expression(attempt: dict) -> str:
    spec = attempt.get("spec") or {}
    ast = P.parse(spec.get("expression", ""))
    windows = ((attempt.get("grid") or {}).get("best") or {}).get("windows")
    if windows is not None and P.collect_windows(ast):
        ast = P.substitute_windows(ast, windows)
    return P.to_string(ast)


def rebuild_result(
    panel: PanelStore, attempt: dict, subuniverse: Optional[float] = 0.3
):
    """Recompute the factor and its backtest from the stored spec + best config."""
    spec = attempt.get("spec") or {}
    grid = attempt.get("grid") or {}
    best = grid.get("best") or {}
    settings = BacktestSettings(
        decay=int(best.get("decay") or 0),
        transform=str(best.get("transform") or "none"),
        cap_filter=(float(best["cap_filter"]) if best.get("cap_filter") is not None
                    and np.isfinite(float(best["cap_filter"])) else None),
        compute_ic=True,
        subuniverse=subuniverse,
    )
    if spec.get("kind") == "script":
        factor = run_script(spec.get("script", ""), panel, best.get("params") or {})
    else:
        factor = evaluate(P.parse(winning_expression(attempt)), panel)
    result = run_backtest_with_subuniverse(factor, panel, settings)
    from .config import SampleSplit
    split_meta = grid.get("split") or {}
    ranges = [split_meta.get(k) for k in ("is_range", "oos_range", "holdout_range")]
    split = panel.meta.get("default_split")
    if split_meta.get("mode") == "none":
        split = None
    elif ranges[0] and ranges[1]:
        split = SampleSplit(train_start=ranges[0][0], train_end=ranges[0][1],
                            test_start=ranges[1][0], test_end=ranges[1][1],
                            holdout_start=ranges[2][0] if ranges[2] else None,
                            holdout_end=ranges[2][1] if ranges[2] else None)
    masks = resolve_split(panel.dates, split)
    result.segments = segment_metrics(
        result.pnl, result.turnover, result.ic, result.factor, masks, ann=settings.ann
    )
    if result.subuniverse is not None:
        result.subuniverse.segments = segment_metrics(
            result.subuniverse.pnl,
            result.subuniverse.turnover,
            result.subuniverse.ic,
            result.subuniverse.factor,
            masks,
            ann=settings.ann,
        )
    return result, masks


def yearly_stats(pnl: pd.Series, turnover: pd.Series, ic: pd.Series) -> pd.DataFrame:
    """Calendar-year sharpe / return / turnover / drawdown / rank IC."""
    from .backtest import metrics as M

    rows = []
    clean = pnl.dropna()
    for year, sub in clean.groupby(clean.index.year):
        cum = (1 + sub).cumprod()
        rows.append(
            {
                "year": int(year),
                "return": float(cum.iloc[-1] - 1),
                "sharpe": M.sharpe_ratio(sub),
                "turnover": float(turnover.reindex(sub.index).mean() * 252),
                "max_drawdown": M.max_drawdown(cum),
                "rank_ic": float(ic.reindex(sub.index).mean()),
                "n_days": int(len(sub)),
            }
        )
    return pd.DataFrame(rows).set_index("year") if rows else pd.DataFrame()


def _fmt(value, digits: int = 2, pct: bool = False) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "-"
    if not np.isfinite(value):
        return "-"
    return f"{value:.1%}" if pct else f"{value:.{digits}f}"


def plot_result(
    attempt: dict,
    result,
    masks,
    out_path: Path,
    title: str,
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.transforms import blended_transform_factory

    pnl = result.pnl.fillna(0.0)
    equity = (1 + pnl).cumprod()
    drawdown = equity / equity.cummax() - 1
    yearly = yearly_stats(result.pnl, result.turnover, result.ic)

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(11.5, 9.5),
        gridspec_kw={"height_ratios": [3.2, 1.1, 1.3], "hspace": 0.42},
    )

    # ---- equity, shaded by segment -----------------------------------
    ax = axes[0]
    ax.plot(equity.index, equity.values, color="#1f4e79", linewidth=1.4, label="cumulative pnl")
    seg_styles = {
        "is": ("#dfe9f7", "in-sample"),
        "oos": ("#fdeedd", "out-of-sample"),
        "holdout": ("#e3f2e3", "observed holdout"),
    }
    blend = blended_transform_factory(ax.transData, ax.transAxes)
    for name, (color, label) in seg_styles.items():
        mask = masks.masks.get(name)
        if mask is None or not bool(mask.any()):
            continue
        idx = mask.index[mask.to_numpy()]
        ax.axvspan(idx[0], idx[-1], color=color, alpha=0.75, zorder=0)
        ax.axvline(idx[0], color="#999999", linewidth=0.8, linestyle="--", zorder=1)
        seg = (result.segments or {}).get(name) or {}
        ax.text(
            idx[0] + (idx[-1] - idx[0]) * 0.5,
            0.97,
            f"{label}\nsharpe {_fmt(seg.get('sharpe'))}",
            transform=blend,
            ha="center",
            va="top",
            fontsize=7.5,
            color="#333333",
            bbox={"facecolor": "white", "alpha": 0.65, "edgecolor": "none", "pad": 1.5},
        )
    import textwrap
    ax.set_title("\n".join(textwrap.wrap(title, 110)), fontsize=8.5)
    ax.set_ylabel("growth of 1 (1x gross)")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, loc="lower left", frameon=False)

    # ---- drawdown -----------------------------------------------------
    ax = axes[1]
    ax.fill_between(drawdown.index, drawdown.values, 0, color="#b23b3b", alpha=0.45)
    ax.set_ylabel("drawdown")
    ax.grid(alpha=0.25)
    ax.text(
        0.01,
        0.08,
        f"max drawdown {drawdown.min():.1%}",
        transform=ax.transAxes,
        fontsize=8,
        color="#7a1f1f",
        bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "none", "pad": 1.5},
    )

    # ---- yearly sharpe ------------------------------------------------
    ax = axes[2]
    if not yearly.empty:
        colors = ["#4a7ebb" if v >= 0 else "#b23b3b" for v in yearly["sharpe"]]
        ax.bar(yearly.index.astype(str), yearly["sharpe"], color=colors, alpha=0.85)
        ax.axhline(0, color="#333333", linewidth=0.8)
        ax.set_ylabel("yearly sharpe")
        ax.tick_params(axis="x", labelrotation=60, labelsize=7)
        ax.grid(alpha=0.2, axis="y")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(top=0.90, bottom=0.07)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _segment_table(result) -> str:
    rows = []
    for name, label in (("full", "full"), ("is", "IS"), ("oos", "OOS"), ("holdout", "holdout")):
        metrics = (
            result.metrics
            if name == "full"
            else (result.segments or {}).get(name) or {}
        )
        if not metrics:
            continue
        rows.append(
            {
                "segment": label,
                "sharpe": _fmt(metrics.get("sharpe")),
                "ann_return": _fmt(metrics.get("ann_return"), pct=True),
                "turnover": _fmt(metrics.get("turnover"), 1),
                "max_drawdown": _fmt(metrics.get("max_drawdown"), pct=True),
                "rank_ic": _fmt(metrics.get("rank_ic", metrics.get("ic")), 4),
                "pearson_ic": _fmt(metrics.get("pearson_ic"), 4),
            }
        )
    return md_table(pd.DataFrame(rows))


def view(
    run: Optional[str],
    hypothesis: Optional[str],
    data: str,
    plot: bool = True,
    out_dir: Optional[Path] = None,
) -> str:
    """Return the markdown report of one attempt; write the plot when asked."""
    from .data import load_processed

    if run is None:
        ledger = load_ledger()
        return render(ledger, sort="sharpe_oos", top=50)

    run_dir, attempt = load_attempt(run, hypothesis)
    panel = load_processed(data)
    result, masks = rebuild_result(panel, attempt)
    effective = winning_expression(attempt) if (attempt.get("spec") or {}).get("kind") != "script" else "<script>"
    spec = attempt.get("spec") or {}
    grid = attempt.get("grid") or {}
    best = grid.get("best") or {}
    review = attempt.get("review") or {}

    lines = [
        f"# {attempt.get('hypothesis')}",
        "",
        f"- run: `{run_dir.name}` | attempt {attempt.get('attempt', 0) + 1} | "
        f"decision **{review.get('decision', '?')}**",
        f"- spec: `{spec.get('expression') or '<script>'}`",
        f"- config: decay={best.get('decay')}, transform={best.get('transform')}, "
        f"cap_filter={best.get('cap_filter')}, windows={best.get('windows')}, "
        f"params={best.get('params')}",
        f"- effective expression: `{effective}`",
        f"- sub-universe threshold: {result.settings.subuniverse}",
        "",
        "## Segments",
        "",
        _segment_table(result),
    ]
    if review.get("reasoning"):
        lines += ["", "## Review", "", f"- reasoning: {review.get('reasoning')}"]
        if review.get("diagnosis"):
            lines.append(f"- diagnosis: {review.get('diagnosis')}")

    yearly = yearly_stats(result.pnl, result.turnover, result.ic)
    if not yearly.empty:
        view = yearly.copy()
        view["return"] = view["return"].map(lambda x: f"{x:.1%}")
        view["max_drawdown"] = view["max_drawdown"].map(lambda x: f"{x:.1%}")
        for col in ("sharpe", "turnover", "rank_ic"):
            view[col] = view[col].map(lambda x: f"{x:.2f}" if col != "rank_ic" else f"{x:.3f}")
        lines += ["", "## Yearly statistics", "", md_table(view.reset_index())]

    if result.subuniverse is not None:
        sub = result.subuniverse
        lines += [
            "",
            "## Sub-universe (reference)",
            "",
            f"- threshold: rank(cap) > {sub.threshold}",
            f"- sharpe {_fmt(sub.metrics.get('sharpe'))}, "
            f"return {_fmt(sub.metrics.get('ann_return'), pct=True)}, "
            f"rank IC {_fmt(sub.metrics.get('rank_ic'), 4)}",
        ]
        sub_yearly = yearly_stats(sub.pnl, sub.turnover, sub.ic)
        if not sub_yearly.empty:
            view = sub_yearly[["sharpe", "turnover", "rank_ic"]].copy()
            for col in view.columns:
                view[col] = view[col].map(lambda x: f"{x:.3f}")
            lines += ["", md_table(view.reset_index())]

    if plot:
        slug = str(attempt.get("hypothesis") or "factor").replace(" ", "_")
        root = Path(out_dir or PLOTS_DIR)
        root.mkdir(parents=True, exist_ok=True)
        stem = f"{run_dir.name}_{slug}_a{attempt.get('attempt', 0)}"
        out = root / f"{stem}.png"
        daily = pd.DataFrame({"pnl": result.pnl, "turnover": result.turnover,
                              "rank_ic": result.ic, "pearson_ic": result.pearson_ic})
        if result.subuniverse is not None:
            daily["sub_pnl"] = result.subuniverse.pnl
        daily.to_csv(root / f"{stem}_daily.csv", index_label="date")
        yearly.to_csv(root / f"{stem}_yearly.csv")
        plot_result(
            attempt,
            result,
            masks,
            out,
            title=f"{attempt.get('hypothesis')} | {effective}",
        )
        lines += ["", f"![plot]({out})", "", f"plot: `{out}`"]

    text = "\n".join(lines)
    if plot:
        (root / f"{stem}.md").write_text(text, encoding="utf-8")
    return text

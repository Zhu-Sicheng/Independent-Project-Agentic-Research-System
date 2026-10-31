"""Stability checks for one factor: same signal, different implementation knobs.

The mining loop reports the *best* configuration. A factor that only works for
one decay / one cross-section transform / one window is fragile, so this module
re-runs the same signal under the checks the research plan calls for:

* ``subuniverse`` — ``if_else(rank(cap) > 0.3, factor, nan)``
* ``cap``        — the capital filter on / off
* ``transform``  — none / rank / sign
* ``decay``      — 0 / 5 / 20 / 60
* ``window``     — every literal window in the expression replaced one slot at a time

Every variant gets its own pnl, metrics and a correlation with the baseline pnl.
Results go to a dedicated directory (``experiments/stability/<run>__<factor>/``)
and never overwrite the batch / view figures.

``python -m factorlab.stability --run <run_id> --hypothesis <name>``
``python -m factorlab.stability --run <run_id> --all``
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

from .backtest.engine import run_backtest, subuniverse_mask
from .config import ALLOWED_WINDOWS, DEFAULT_DECAYS, DEFAULT_TRANSFORMS, PROJECT_ROOT, BacktestSettings
from .data.panel import PanelStore
from .expr import parser as P
from .expr.evaluator import evaluate
from .markdown import md_table
from .view import load_attempt, winning_expression

STABILITY_DIR = PROJECT_ROOT / "experiments" / "stability"
SUBUNIVERSE_THRESHOLD = 0.3


@dataclass
class Variant:
    name: str
    group: str
    pnl: pd.Series
    metrics: dict
    note: str = ""

    def row(self) -> dict:
        return {
            "variant": self.name,
            "group": self.group,
            "sharpe": self.metrics.get("sharpe"),
            "ann_return": self.metrics.get("ann_return"),
            "turnover": self.metrics.get("turnover"),
            "max_drawdown": self.metrics.get("max_drawdown"),
            "rank_ic": self.metrics.get("rank_ic"),
            "n_names": self.metrics.get("n_names"),
            "note": self.note,
        }


def baseline_settings(attempt: dict) -> BacktestSettings:
    best = (attempt.get("grid") or {}).get("best") or {}
    cap = best.get("cap_filter")
    try:
        cap = None if cap is None or not np.isfinite(float(cap)) else float(cap)
    except (TypeError, ValueError):
        cap = None
    return BacktestSettings(
        decay=int(best.get("decay") or 0),
        transform=str(best.get("transform") or "none"),
        cap_filter=cap,
        compute_ic=True,
        subuniverse=None,  # the sub-universe is a variant here, not a nested run
    )


def factor_ast(attempt: dict) -> tuple[object, list[int]]:
    spec = attempt.get("spec") or {}
    if spec.get("kind") == "script":
        raise ValueError("stability checks currently support expression factors only")
    ast = P.parse(spec.get("expression", ""))
    best = (attempt.get("grid") or {}).get("best") or {}
    windows = best.get("windows")
    if windows:
        base_windows = [int(w) for w in windows]
    else:
        base_windows = [int(w) for w in P.collect_windows(ast)]
    return ast, base_windows


def _with_windows(ast, windows: list[int]):
    return P.substitute_windows(ast, windows) if P.collect_windows(ast) else ast


def build_variants(
    panel: PanelStore,
    attempt: dict,
    decays: Iterable[int] = DEFAULT_DECAYS,
    transforms: Iterable[str] = DEFAULT_TRANSFORMS,
    windows: Iterable[int] = ALLOWED_WINDOWS,
    cap_filters: Iterable[Optional[float]] = (None, 0.3),
) -> list[Variant]:
    """Re-run the same signal under every stability check."""
    base = baseline_settings(attempt)
    ast, base_windows = factor_ast(attempt)
    base_factor = evaluate(_with_windows(ast, base_windows), panel)

    variants: list[Variant] = []

    def add(name: str, group: str, factor, settings: BacktestSettings, note: str = "", mask=None) -> None:
        # only the baseline carries the (expensive) IC panel; variants need pnl
        if group != "original":
            settings = settings.replace(compute_ic=False)
        result = run_backtest(factor, panel, settings, universe_mask=mask)
        variants.append(Variant(name, group, result.pnl, result.metrics, note))

    add("original", "original", base_factor, base, note=f"decay={base.decay}, transform={base.transform}, cap={base.cap_filter}")

    # ---- sub-universe: same signal, smallest 30% of names removed ----
    mask = subuniverse_mask(panel, SUBUNIVERSE_THRESHOLD)
    add(
        f"subuniverse(rank(cap)>{SUBUNIVERSE_THRESHOLD})",
        "subuniverse",
        base_factor,
        base,
        note="if_else(rank(cap) > 0.3, factor, nan)",
        mask=mask,
    )

    # ---- capital filter flipped ----
    for cap in cap_filters:
        cap = None if cap is None else float(cap)
        if cap == base.cap_filter:
            continue
        add(
            f"cap_filter={cap}",
            "cap",
            base_factor,
            base.replace(cap_filter=cap),
            note="drop the smallest names before demeaning" if cap else "keep the full universe",
        )

    # ---- cross-sectional transform ----
    for transform in transforms:
        if transform == base.transform:
            continue
        add(f"transform={transform}", "transform", base_factor, base.replace(transform=transform))

    # ---- time decay ----
    for decay in decays:
        if int(decay) == int(base.decay):
            continue
        add(f"decay={int(decay)}", "decay", base_factor, base.replace(decay=int(decay)))

    # ---- expression windows, one slot at a time ----
    for slot, current in enumerate(base_windows):
        for window in windows:
            window = int(window)
            if window == current:
                continue
            candidate = list(base_windows)
            candidate[slot] = window
            try:
                factor = evaluate(_with_windows(ast, candidate), panel)
            except Exception as exc:  # pragma: no cover - defensive
                variants.append(Variant(f"window[{slot}]={window}", "window", pd.Series(dtype=float), {"error": str(exc)}))
                continue
            print(f"  window[{slot}]={window}", flush=True)
            add(
                f"window[{slot}]={window}",
                "window",
                factor,
                base,
                note=f"slot {slot}: {current} -> {window}",
            )

    return variants


def _draw(variants: list[Variant], out_path: Path, title: str) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    baseline = next(v for v in variants if v.group == "original")
    base_eq = (1 + baseline.pnl.fillna(0.0)).cumprod()
    groups = [g for g in ("subuniverse", "cap", "transform", "decay", "window") if any(v.group == g for v in variants)]
    ncols = 2
    nrows = max(1, int(np.ceil(len(groups) / ncols)))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12.5, 3.6 * nrows), sharex=True, squeeze=False)

    palette = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b", "#17becf", "#7f7f7f"]

    for ax, group in zip(axes.ravel(), groups):
        ax.plot(base_eq.index, base_eq.values, color="black", linewidth=1.8, label="original")
        for i, variant in enumerate(v for v in variants if v.group == group):
            if variant.pnl.empty:
                continue
            eq = (1 + variant.pnl.fillna(0.0)).cumprod()
            sharpe = variant.metrics.get("sharpe")
            ax.plot(
                eq.index,
                eq.values,
                linewidth=0.9,
                alpha=0.85,
                color=palette[i % len(palette)],
                label=f"{variant.name} (S={sharpe:.2f})" if isinstance(sharpe, (int, float)) and np.isfinite(sharpe) else variant.name,
            )
        ax.set_title(group, fontsize=10)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=6.5, loc="best", frameon=False)
    for ax in axes.ravel()[len(groups):]:
        ax.axis("off")

    fig.suptitle(title, fontsize=9.5)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_name(out_path.name + ".tmp.png")
    fig.savefig(tmp, dpi=130, bbox_inches="tight")
    plt.close(fig)
    import os
    import time

    for _ in range(5):
        try:
            os.replace(tmp, out_path)
            return out_path
        except OSError:
            time.sleep(0.4)
    raise OSError(f"could not replace {out_path}")


def run_stability(
    panel: PanelStore,
    attempt: dict,
    run_id: str,
    out_dir: Optional[Path] = None,
) -> Path:
    """Run every check for one factor and write png / csv / markdown."""
    variants = build_variants(panel, attempt)
    base = next(v for v in variants if v.group == "original")

    out = Path(out_dir) if out_dir else STABILITY_DIR / f"{run_id}__{attempt['hypothesis']}"
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    for variant in variants:
        row = variant.row()
        if not variant.pnl.empty:
            joined = pd.concat([base.pnl.rename("base"), variant.pnl.rename("var")], axis=1).dropna()
            row["pnl_corr_with_original"] = (
                float(joined["base"].corr(joined["var"])) if len(joined) > 3 else np.nan
            )
        else:
            row["pnl_corr_with_original"] = np.nan
        rows.append(row)
    table = pd.DataFrame(rows)
    table.to_csv(out / "metrics.csv", index=False, encoding="utf-8")

    pnl_frame = pd.concat(
        {variant.name: variant.pnl for variant in variants if not variant.pnl.empty}, axis=1
    )
    pnl_frame.to_csv(out / "pnl_daily.csv", index_label="date")

    _draw(variants, out / "pnl.png", f"{attempt['hypothesis']} | {winning_expression(attempt)}")

    baseline_cfg = baseline_settings(attempt)
    lines = [
        f"# Stability checks — {attempt['hypothesis']}",
        "",
        f"- run: `{run_id}`",
        f"- expression: `{winning_expression(attempt)}`",
        f"- baseline: decay={baseline_cfg.decay}, transform={baseline_cfg.transform}, cap={baseline_cfg.cap_filter}",
        "",
        "Each variant keeps the signal and changes one implementation knob. "
        "`pnl_corr_with_original` is the daily pnl correlation with the baseline.",
        "",
        (
            "Note: when the baseline already uses `cap_filter=0.3`, the sub-universe "
            "variant is identical by construction (both drop the smallest 30%)."
            if baseline_cfg.cap_filter == SUBUNIVERSE_THRESHOLD
            else "The sub-universe variant removes the smallest 30% by cap rank."
        ),
        "",
        md_table(table[["variant", "group", "sharpe", "ann_return", "turnover", "max_drawdown", "rank_ic", "pnl_corr_with_original"]]),
        "",
        f"![stability]({'pnl.png'})",
    ]
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return out


def build_index(root: str | Path = STABILITY_DIR) -> Path:
    """One table summarising every factor's stability diagnostics."""
    root = Path(root)
    rows = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        metrics = folder / "metrics.csv"
        if not metrics.exists():
            continue
        table = pd.read_csv(metrics)
        base = table[table["group"] == "original"]
        if base.empty:
            continue
        base = base.iloc[0]

        def span(group: str, column: str = "sharpe") -> tuple[float, float]:
            values = table.loc[table["group"] == group, column].dropna()
            return (float(values.min()), float(values.max())) if len(values) else (np.nan, np.nan)

        sub = table[table["group"] == "subuniverse"]["sharpe"]
        decay_lo, decay_hi = span("decay")
        transform_lo, transform_hi = span("transform")
        window_lo, window_hi = span("window")
        corr = table["pnl_corr_with_original"].dropna()
        rows.append(
            {
                "factor": folder.name.split("__", 1)[-1],
                "run": folder.name.split("__", 1)[0],
                "sharpe": base["sharpe"],
                "subuniverse": float(sub.iloc[0]) if len(sub) else np.nan,
                "decay_range": f"{decay_lo:.2f}..{decay_hi:.2f}",
                "transform_range": f"{transform_lo:.2f}..{transform_hi:.2f}",
                "window_range": f"{window_lo:.2f}..{window_hi:.2f}",
                "min_pnl_corr": float(corr.min()) if len(corr) else np.nan,
                "max_turnover": float(table["turnover"].max()),
            }
        )
    frame = pd.DataFrame(rows)
    out = root / "README.md"
    if frame.empty:
        out.write_text("# Stability checks\n\n_no results yet_\n", encoding="utf-8")
        return out
    frame = frame.sort_values("sharpe", ascending=False)
    lines = [
        "# Stability checks",
        "",
        "Same signal, different implementation knobs. `*_range` is the min..max Sharpe",
        "across that group of variants; a wide range or a large drop in `min_pnl_corr`",
        "means the result depends on the exact configuration rather than the mechanism.",
        "",
        md_table(frame),
        "",
        "Per-factor details live in the sub-directories (`metrics.csv`, `pnl.png`, `README.md`).",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    parser.add_argument("--hypothesis", default=None)
    parser.add_argument("--all", action="store_true", help="every completed attempt of the run")
    parser.add_argument("--data", default=str(PROJECT_ROOT / "data" / "processed" / "panel"))
    parser.add_argument("--out", default=None)
    parser.add_argument("--index", action="store_true", help="rebuild the summary table only")
    args = parser.parse_args()

    if args.index:
        print(build_index())
        return

    from .data import load_processed

    panel = load_processed(args.data)
    run_dir = Path(args.run)
    if not run_dir.is_absolute():
        run_dir = PROJECT_ROOT / "runs" / args.run if (PROJECT_ROOT / "runs" / args.run).is_dir() else run_dir

    if args.all:
        journal = run_dir / "attempts.jsonl"
        attempts = [
            json.loads(line)
            for line in journal.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        attempts = [a for a in attempts if (a.get("grid") or {}).get("best")]
    else:
        _, attempt = load_attempt(str(run_dir), args.hypothesis)
        attempts = [attempt]

    for attempt in attempts:
        print(f"stability: {attempt['hypothesis']} ...", flush=True)
        target = run_stability(panel, attempt, run_dir.name, Path(args.out) if args.out else None)
        print(f"stability: {attempt['hypothesis']} -> {target}", flush=True)
    print(build_index())


if __name__ == "__main__":
    main()

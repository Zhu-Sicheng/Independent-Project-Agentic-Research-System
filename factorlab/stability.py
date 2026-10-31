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
Results go to a derived directory (``experiments/.index/stability/<run>__<factor>/``)
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

STABILITY_DIR = PROJECT_ROOT / "experiments" / ".index" / "stability"
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
            add(
                f"window[{slot}]={window}",
                "window",
                factor,
                base,
                note=f"slot {slot}: {current} -> {window}",
            )

    return variants


GROUP_STYLE = {
    "original": ("#000000", 2.4, "-"),
    "subuniverse": ("#d62728", 1.6, "--"),
    "cap": ("#8c564b", 1.3, "--"),
    "transform": ("#ff7f0e", 1.1, "-"),
    "decay": ("#1f77b4", 1.1, "-"),
    "window": ("#2ca02c", 0.9, "-"),
}


def _group_colors(group: str, count: int) -> list:
    """Shades of one colour per check group, so groups stay distinguishable."""
    import matplotlib

    cmap = {
        "transform": matplotlib.colormaps["Oranges"],
        "decay": matplotlib.colormaps["Blues"],
        "window": matplotlib.colormaps["Greens"],
    }.get(group)
    if cmap is None or count <= 1:
        return [GROUP_STYLE.get(group, ("#7f7f7f", 1.0, "-"))[0]] * count
    return [cmap(x) for x in np.linspace(0.45, 0.95, count)]


def draw_single_panel(
    series: dict,
    groups: dict,
    sharpes: dict,
    out_path: Path,
    title: str,
) -> Path:
    """All variant pnl curves on one axes, colour-coded by check group."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12.5, 7.0))
    order = ["original", "subuniverse", "cap", "transform", "decay", "window"]
    counts = {group: sum(1 for g in groups.values() if g == group) for group in order}
    used = {group: 0 for group in order}

    for name, pnl in series.items():
        group = groups.get(name, "original")
        if group == "original":
            color, width, style = GROUP_STYLE["original"]
            zorder = 5
        else:
            idx = used[group]
            used[group] += 1
            color = _group_colors(group, counts[group])[idx]
            _, width, style = GROUP_STYLE.get(group, ("#7f7f7f", 1.0, "-"))
            zorder = 3

        equity = (1 + pd.Series(pnl).fillna(0.0)).cumprod()
        sharpe = sharpes.get(name)
        label = f"{name} (S={sharpe:.2f})" if isinstance(sharpe, (int, float)) and np.isfinite(sharpe) else name
        ax.plot(equity.index, equity.values, color=color, linewidth=width, linestyle=style, alpha=0.9, label=label, zorder=zorder)

    ax.set_ylabel("growth of 1 (1x gross)")
    ax.grid(alpha=0.25)
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=6.2, loc="upper left", ncol=2, frameon=False)
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


def replot_folder(folder: str | Path) -> Path:
    """Redraw one factor's stability figure from its saved pnl_daily.csv."""
    folder = Path(folder)
    daily = folder / "pnl_daily.csv"
    metrics = folder / "metrics.csv"
    if not daily.exists() or not metrics.exists():
        raise FileNotFoundError(f"{folder} has no pnl_daily.csv / metrics.csv")
    frame = pd.read_csv(daily, index_col=0, parse_dates=True)
    table = pd.read_csv(metrics)
    groups = dict(zip(table["variant"], table["group"]))
    sharpes = dict(zip(table["variant"], table["sharpe"]))
    title = folder.name.replace("__", " | ")
    return draw_single_panel(
        {name: frame[name] for name in frame.columns}, groups, sharpes, folder / "pnl.png", title
    )


def replot_all(root: str | Path = STABILITY_DIR) -> int:
    root = Path(root)
    drawn = 0
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        if (folder / "pnl_daily.csv").exists():
            replot_folder(folder)
            drawn += 1
    return drawn


def _span(values: Iterable[float]) -> list[float]:
    clean = [float(v) for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
    return [min(clean), max(clean)] if clean else [float("nan"), float("nan")]


def stability_summary(panel: PanelStore, attempt: dict) -> dict:
    """Compact evidence handed to the review agent (no plots, no files)."""
    variants = build_variants(panel, attempt)
    baseline = next(v for v in variants if v.group == "original")
    base_pnl = baseline.pnl

    def sharpes(group: str) -> list[float]:
        return [v.metrics.get("sharpe") for v in variants if v.group == group]

    def correlations(variants_subset) -> list[float]:
        out = []
        for variant in variants_subset:
            joined = pd.concat([base_pnl.rename("a"), variant.pnl.rename("b")], axis=1).dropna()
            if len(joined) > 3:
                value = float(joined["a"].corr(joined["b"]))
                if np.isfinite(value):
                    out.append(value)
        return out

    non_baseline = [v for v in variants if v.group != "original" and not v.pnl.empty]
    sub = [v for v in variants if v.group == "subuniverse"]
    sub_sharpe = float(sub[0].metrics.get("sharpe")) if sub else float("nan")
    base_sharpe = float(baseline.metrics.get("sharpe", np.nan))

    summary = {
        "baseline_sharpe": base_sharpe,
        "subuniverse_sharpe": sub_sharpe,
        "subuniverse_delta": sub_sharpe - base_sharpe if np.isfinite(sub_sharpe) else float("nan"),
        "transform_sharpe_span": _span(sharpes("transform")),
        "decay_sharpe_span": _span(sharpes("decay")),
        "window_sharpe_span": _span(sharpes("window")),
        "min_pnl_corr": min(correlations(non_baseline), default=float("nan")),
        "max_turnover": max(
            (float(v.metrics.get("turnover", np.nan)) for v in variants
             if np.isfinite(float(v.metrics.get("turnover", np.nan)))),
            default=float("nan"),
        ),
        "n_variants": len(variants),
    }

    flags = []
    if np.isfinite(sub_sharpe) and np.isfinite(base_sharpe) and sub_sharpe <= 0 < base_sharpe:
        flags.append("subuniverse_flips_sign")
    elif np.isfinite(sub_sharpe) and np.isfinite(base_sharpe) and sub_sharpe < 0.5 * abs(base_sharpe):
        flags.append("subuniverse_halves_edge")
    window_lo, window_hi = summary["window_sharpe_span"]
    if np.isfinite(window_lo) and np.isfinite(window_hi) and window_lo < 0 < window_hi:
        flags.append("window_span_crosses_zero")
    if np.isfinite(summary["min_pnl_corr"]) and summary["min_pnl_corr"] < 0.3:
        flags.append("variant_pnl_decorrelates")
    summary["flags"] = flags
    return summary


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

    baseline_cfg = baseline_settings(attempt)
    expression = winning_expression(attempt)
    meta = {
        "run_id": run_id,
        "hypothesis": attempt.get("hypothesis"),
        "expression": expression,
        "baseline": {
            "decay": baseline_cfg.decay,
            "transform": baseline_cfg.transform,
            "cap_filter": baseline_cfg.cap_filter,
        },
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    draw_single_panel(
        {variant.name: variant.pnl for variant in variants if not variant.pnl.empty},
        {variant.name: variant.group for variant in variants},
        {variant.name: variant.metrics.get("sharpe") for variant in variants},
        out / "pnl.png",
        f"{attempt['hypothesis']} | {winning_expression(attempt)}",
    )

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
        meta_path = folder / "meta.json"
        expression = ""
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            expression = meta.get("expression", "")
        else:
            readme = folder / "README.md"
            if readme.exists():
                run_id = folder.name.split("__", 1)[0]
                hypothesis = folder.name.split("__", 1)[1]
                baseline: dict = {}
                for line in readme.read_text(encoding="utf-8").splitlines():
                    if line.startswith("- expression:"):
                        expression = line.split("`")[1] if "`" in line else line.split(":", 1)[1].strip()
                    elif line.startswith("- baseline:"):
                        parts = line.split(":", 1)[1]
                        for chunk in parts.split(","):
                            if "=" in chunk:
                                key, _, value = chunk.partition("=")
                                baseline[key.strip()] = value.strip()
                meta_path.write_text(
                    json.dumps(
                        {
                            "run_id": run_id,
                            "hypothesis": hypothesis,
                            "expression": expression,
                            "baseline": baseline,
                        },
                        indent=2,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
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
                "expression": expression,
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
    parser.add_argument("--run", default=None)
    parser.add_argument("--hypothesis", default=None)
    parser.add_argument("--all", action="store_true", help="every completed attempt of the run")
    parser.add_argument("--data", default=str(PROJECT_ROOT / "data" / "processed" / "panel"))
    parser.add_argument("--out", default=None)
    parser.add_argument("--index", action="store_true", help="rebuild the summary table only")
    parser.add_argument("--replot", action="store_true", help="redraw pngs from saved pnl_daily.csv")
    args = parser.parse_args()

    if args.index:
        print(build_index())
        return

    if args.replot:
        print(f"redrew {replot_all()} stability figures")
        return

    if not args.run:
        parser.error("--run is required unless --index/--replot is used")

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

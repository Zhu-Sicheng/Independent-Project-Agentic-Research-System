"""Grid search over the post-processing knobs and the factor's own windows.

The search space the user asked for:

* decay in {0, 5, 20, 60} days
* cross-sectional transform in {none, rank, sign}
* cap filter in {none, drop the smallest 30% by cap rank}
* for expression factors: every literal time-series window may be re-drawn
  from {5, 20, 60, 120, 240}
* for script factors: declared ``param_grid`` values

Each point is a full backtest.  When an out-of-sample split is configured the
ranking uses the **in-sample** segment only; the untouched holdout is evaluated
afterwards and reported next to it (see :mod:`factorlab.backtest.split`).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from ..config import BacktestSettings, GridConfig, SampleSplit
from ..data.panel import PanelStore
from ..expr import parser as P
from ..expr.evaluator import evaluate
from ..expr.script import run_script
from ..expr.spec import FactorSpec
from .engine import BacktestResult, run_backtest, yearly_table
from .split import SEGMENT_KEYS, SplitMasks, resolve_split, segment_metrics


class GridError(ValueError):
    pass


def _round_metrics(metrics: Optional[dict], digits: int = 4) -> Optional[dict]:
    if not metrics:
        return None
    out = {}
    for key, value in metrics.items():
        try:
            value = float(value)
            out[key] = round(value, digits) if np.isfinite(value) else None
        except (TypeError, ValueError):
            out[key] = value
    return out


@dataclass
class GridResult:
    table: pd.DataFrame
    best: BacktestResult
    best_factor: pd.DataFrame
    best_row: dict
    objective: str
    n_evals: int
    failures: list[str] = field(default_factory=list)
    spec: Optional[FactorSpec] = None
    split_meta: dict = field(default_factory=dict)
    oos_yearly: Optional[pd.DataFrame] = None
    holdout_yearly: Optional[pd.DataFrame] = None

    @property
    def has_oos(self) -> bool:
        return bool(self.split_meta.get("has_oos"))

    @property
    def has_holdout(self) -> bool:
        return bool(self.split_meta.get("has_holdout"))

    def top(self, n: int = 5) -> pd.DataFrame:
        cols = [
            c
            for c in (
                "decay",
                "transform",
                "cap_filter",
                "windows",
                "params",
                "sharpe",
                "ann_return",
                "turnover",
                "max_drawdown",
                "ic",
                "sharpe_is",
                "sharpe_oos",
                "sharpe_holdout",
            )
            if c in self.table.columns
        ]
        return self.table.head(n)[cols]

    def summary(self) -> dict:
        t = self.table
        if t.empty:
            return {"n_evals": 0}
        m = self.best.metrics
        pos = float((t["sharpe"] > 0).mean())
        good = float((t["sharpe"] > 0.5).mean())
        best = {
            "decay": self.best_row.get("decay"),
            "transform": self.best_row.get("transform"),
            "cap_filter": self.best_row.get("cap_filter"),
            "windows": list(self.best_row.get("windows") or []),
            "params": self.best_row.get("params") or {},
            "sharpe": round(float(m.get("sharpe", np.nan)), 3),
            "ann_return": round(float(m.get("ann_return", np.nan)), 4),
            "ann_vol": round(float(m.get("ann_vol", np.nan)), 4),
            "turnover": round(float(m.get("turnover", np.nan)), 3),
            "max_drawdown": round(float(m.get("max_drawdown", np.nan)), 4),
            "ic": round(float(m.get("ic", np.nan)), 4),
            "ic_ir": round(float(m.get("ic_ir", np.nan)), 3),
            "n_names": round(float(m.get("n_names", np.nan)), 1),
            "hit_rate": round(float(m.get("hit_rate", np.nan)), 3),
            "fitness": round(float(m.get("fitness", np.nan)), 3),
        }
        out = {
            "objective": self.objective,
            "selection": "in-sample" if self.has_oos else "full-sample",
            "n_evals": int(self.n_evals),
            "best": best,
            "share_positive_sharpe": round(pos, 3),
            "share_sharpe_gt_0.5": round(good, 3),
            "yearly": self.best.yearly.reset_index().to_dict(orient="records"),
        }
        if self.has_oos:
            segs = self.best.segments or {}
            out["split"] = {
                "description": self.split_meta.get("description"),
                "is_range": self.split_meta.get("is_range"),
                "oos_range": self.split_meta.get("oos_range"),
                "holdout_range": self.split_meta.get("holdout_range"),
                "n_is": self.split_meta.get("n_is"),
                "n_oos": self.split_meta.get("n_oos"),
                "n_holdout": self.split_meta.get("n_holdout"),
            }
            out["in_sample"] = _round_metrics(segs.get("is"))
            out["out_of_sample"] = _round_metrics(segs.get("oos"))
            if (
                out.get("out_of_sample") is not None
                and self.oos_yearly is not None
                and not self.oos_yearly.empty
            ):
                out["out_of_sample"]["yearly"] = self.oos_yearly.reset_index().to_dict(
                    orient="records"
                )
        if self.has_holdout:
            segs = self.best.segments or {}
            out["holdout"] = _round_metrics(segs.get("holdout"))
            if (
                out.get("holdout") is not None
                and self.holdout_yearly is not None
                and not self.holdout_yearly.empty
            ):
                out["holdout"]["yearly"] = self.holdout_yearly.reset_index().to_dict(
                    orient="records"
                )
        return out


class GridSearch:
    def __init__(
        self,
        panel: PanelStore,
        config: Optional[GridConfig] = None,
        base: Optional[BacktestSettings] = None,
        split: Optional[SampleSplit] = None,
    ):
        self.panel = panel
        self.config = config or GridConfig()
        self.base = base or BacktestSettings()
        self.split_masks: SplitMasks = resolve_split(panel.dates, split)
        self.n_settings = (
            len(self.config.decays)
            * len(self.config.transforms)
            * len(self.config.cap_filters)
        )

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #
    def run_spec(self, spec: FactorSpec) -> GridResult:
        if spec.kind == "expression":
            return self.run_expression(spec.expression, spec=spec)
        return self.run_script(spec)

    def run_expression(self, expression: str, spec: Optional[FactorSpec] = None) -> GridResult:
        ast = P.parse(expression)
        slots = tuple(int(w) for w in P.collect_windows(ast))
        combos = self._window_combos(slots)

        rows: list[dict] = []
        results: list[BacktestResult] = []
        factors: dict[int, pd.DataFrame] = {}
        failures: list[str] = []
        evals = 0

        for cid, combo in enumerate(combos):
            if evals >= self.config.max_evals:
                break
            try:
                ast2 = P.substitute_windows(ast, combo) if slots else ast
                factor = evaluate(ast2, self.panel)
            except Exception as exc:
                failures.append(f"windows={combo}: {exc}")
                continue
            factors[cid] = factor
            evals = self._sweep(factor, {"windows": combo, "params": None, "combo_id": cid},
                                rows, results, factors, failures, evals)

        return self._finish(rows, results, factors, failures, evals, spec)

    def run_script(self, spec: FactorSpec) -> GridResult:
        combos = spec.param_combos()
        rows: list[dict] = []
        results: list[BacktestResult] = []
        factors: dict[int, pd.DataFrame] = {}
        failures: list[str] = []
        evals = 0

        for cid, params in enumerate(combos):
            if evals >= self.config.max_evals:
                break
            try:
                factor = run_script(spec.script, self.panel, params)
            except Exception as exc:
                failures.append(f"params={params}: {exc}")
                continue
            factors[cid] = factor
            evals = self._sweep(
                factor,
                {"windows": tuple(spec.windows), "params": params, "combo_id": cid},
                rows,
                results,
                factors,
                failures,
                evals,
            )

        if not rows:
            raise GridError(
                "every script parameter combination failed: " + "; ".join(failures[:3])
            )
        return self._finish(rows, results, factors, failures, evals, spec)

    def run_matrix(self, matrix: pd.DataFrame, label: str = "matrix") -> GridResult:
        rows: list[dict] = []
        results: list[BacktestResult] = []
        factors = {0: matrix}
        failures: list[str] = []
        evals = self._sweep(
            matrix, {"windows": (), "params": None, "combo_id": 0}, rows, results, factors, failures, 0
        )
        return self._finish(rows, results, factors, failures, evals, None)

    # ------------------------------------------------------------------ #
    # internals
    # ------------------------------------------------------------------ #
    def _sweep(
        self,
        factor: pd.DataFrame,
        meta: dict,
        rows: list,
        results: list,
        factors: dict,
        failures: list,
        evals: int,
    ) -> int:
        for decay, transform, cap in itertools.product(
            self.config.decays, self.config.transforms, self.config.cap_filters
        ):
            if evals >= self.config.max_evals:
                break
            settings = self.base.replace(
                decay=int(decay),
                transform=str(transform),
                cap_filter=None if cap is None else float(cap),
                compute_ic=False,
            )
            try:
                res = run_backtest(factor, self.panel, settings)
            except Exception as exc:
                failures.append(f"{settings}: {exc}")
                continue
            res.segments = segment_metrics(
                res.pnl,
                res.turnover,
                res.ic,
                factor,
                self.split_masks,
                ann=settings.ann,
            )
            # the full matrix is ~60 MB on a 6700 x 1200 panel; keep only the
            # best one (grid.best_factor) instead of one per evaluation
            res.factor = None
            row = {
                "decay": int(decay),
                "transform": str(transform),
                "cap_filter": None if cap is None else float(cap),
                **meta,
                **res.metrics,
                **self._segment_columns(res.segments),
            }
            rows.append(row)
            results.append(res)
            evals += 1
        return evals

    def _segment_columns(self, segments: Optional[dict]) -> dict:
        if not segments or not self.split_masks.has_oos:
            return {}
        out: dict = {}
        for segment in ("is", "oos", "holdout"):
            metrics = segments.get(segment)
            if not metrics:
                continue
            for key in SEGMENT_KEYS:
                value = metrics.get(key)
                if value is not None:
                    out[f"{key}_{segment}"] = value
        return out

    def _assign_segment_columns(self, table: pd.DataFrame, pos: int, segments: dict) -> None:
        for key, value in self._segment_columns(segments).items():
            table.loc[pos, key] = value

    def _finish(
        self,
        rows: list[dict],
        results: list[BacktestResult],
        factors: dict,
        failures: list[str],
        evals: int,
        spec: Optional[FactorSpec],
    ) -> GridResult:
        if not rows:
            raise GridError("grid search produced no successful backtest: " + "; ".join(failures[:5]))

        table = pd.DataFrame(rows)
        objective = self.config.objective
        if objective not in table.columns:
            objective = "sharpe"

        # with a holdout, only in-sample performance may drive the selection
        score_col = objective
        if self.split_masks.has_oos and f"{objective}_is" in table.columns:
            score_col = f"{objective}_is"
        table["_score"] = table[score_col].fillna(-1e9)
        order = table.sort_values(["_score", "turnover"], ascending=[False, True])

        # IC is expensive; recompute it (and the segment metrics) only for the
        # configurations that are actually in the running
        top_positions = list(order.index[:10])
        for pos in top_positions:
            cid = int(rows[pos]["combo_id"])
            factor = factors.get(cid)
            if factor is None or "ic" not in table.columns:
                continue
            try:
                refreshed = run_backtest(
                    factor,
                    self.panel,
                    results[pos].settings.replace(compute_ic=True),
                )
            except Exception as exc:  # pragma: no cover - defensive
                failures.append(f"ic refresh failed: {exc}")
                continue
            refreshed.segments = segment_metrics(
                refreshed.pnl,
                refreshed.turnover,
                refreshed.ic,
                factor,
                self.split_masks,
                ann=refreshed.settings.ann,
            )
            refreshed.factor = None
            results[pos] = refreshed
            for key in ("ic", "ic_ir", "ic_positive_ratio"):
                table.loc[pos, key] = refreshed.metrics.get(key, np.nan)
            self._assign_segment_columns(table, pos, refreshed.segments)

        order = table.sort_values(["_score", "turnover"], ascending=[False, True])
        best_idx = int(order.index[0])
        best_row = order.iloc[0].drop(labels=["_score"]).to_dict()
        best_settings = results[best_idx].settings
        best = run_backtest(
            factors[int(best_row["combo_id"])],
            self.panel,
            best_settings.replace(compute_ic=True, keep_positions=True),
        )
        best.segments = segment_metrics(
            best.pnl,
            best.turnover,
            best.ic,
            best.factor,
            self.split_masks,
            ann=best.settings.ann,
        )
        oos_yearly = None
        holdout_yearly = None
        if self.split_masks.has_oos:
            mask = self.split_masks.masks["oos"]
            oos_yearly = yearly_table(
                best.pnl.loc[mask],
                best.turnover.loc[mask],
                best.ic.loc[mask],
                best.settings.ann,
            )
        if self.split_masks.has_holdout:
            mask = self.split_masks.masks["holdout"]
            holdout_yearly = yearly_table(
                best.pnl.loc[mask],
                best.turnover.loc[mask],
                best.ic.loc[mask],
                best.settings.ann,
            )
        table = table.drop(columns=["_score"]).loc[order.index].reset_index(drop=True)
        best_factor = factors.get(int(best_row["combo_id"]), next(iter(factors.values())))

        return GridResult(
            table=table,
            best=best,
            best_factor=best_factor,
            best_row=best_row,
            objective=objective,
            n_evals=evals,
            failures=failures,
            spec=spec,
            split_meta=dict(self.split_masks.meta),
            oos_yearly=oos_yearly,
            holdout_yearly=holdout_yearly,
        )

    def _window_combos(self, slots: Sequence[int]) -> list[tuple]:
        k = len(slots)
        if k == 0:
            return [()]
        allowed = [int(w) for w in self.config.windows]
        full = list(itertools.product(allowed, repeat=k))
        base = tuple(int(w) for w in slots)
        max_win = max(1, int(self.config.max_evals) // max(1, self.n_settings))

        if len(full) <= max_win:
            combos = ([base] if base not in full else []) + full
            return combos

        rng = np.random.default_rng(self.config.seed)
        combos = [base]
        seen = {base}
        # coordinate sweep: move one window at a time, keep the rest at the base
        for i in range(k):
            for w in allowed:
                cand = list(base)
                cand[i] = w
                cand = tuple(cand)
                if cand not in seen:
                    seen.add(cand)
                    combos.append(cand)
        budget = max_win - len(combos)
        if budget > 0:
            idx = rng.choice(len(full), size=min(budget * 3, len(full)), replace=False)
            for j in idx:
                cand = full[int(j)]
                if cand not in seen:
                    seen.add(cand)
                    combos.append(cand)
                if len(combos) >= max_win:
                    break
        return combos[:max_win]

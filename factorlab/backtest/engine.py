"""Event-free daily backtest of a factor matrix.

Conventions
-----------
* return definition ``y``: close-to-close by default, i.e. ``close_t/close_{t-1}-1``
* ``delay = 1``: the factor observed after the close of day ``t`` is traded at
  the close of ``t`` and earns the ``t -> t+1`` return.  No look-ahead.
* weights are dollar neutral (cross-sectional demean) and scaled to unit gross
  exposure, so "return" is the return of a 1x gross long/short book.
* costs are ``cost_bps`` of traded notional; turnover is one-way
  (``0.5 * sum|w_t - w_{t-1}|``).

The hot path is numpy based on purpose: the grid search runs hundreds of
backtests per factor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from ..config import BacktestSettings
from ..data.panel import PanelStore
from . import metrics as M


class BacktestError(ValueError):
    pass


@dataclass
class SubUniverseResult:
    """Backtest of the same factor restricted to the sub-universe.

    ``if_else(rank(cap) > threshold, factor, nan)``: the smallest names are
    dropped and the book is rebuilt on the remaining names.  This is a
    *reference* diagnostic; the primary metrics stay the full-universe ones.
    """

    threshold: float
    metrics: dict
    pnl: pd.Series
    turnover: pd.Series
    ic: pd.Series
    pearson_ic: Optional[pd.Series] = None
    factor: Optional[pd.DataFrame] = None
    segments: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "threshold": self.threshold,
            "metrics": self.metrics,
            "segments": self.segments,
        }


@dataclass
class BacktestResult:
    settings: BacktestSettings
    metrics: dict
    yearly: pd.DataFrame
    pnl: pd.Series
    turnover: pd.Series
    ic: pd.Series
    factor: Optional[pd.DataFrame] = None
    positions: Optional[pd.DataFrame] = None
    pearson_ic: Optional[pd.Series] = None
    #: metrics per segment: ``{"full": ..., "is": ..., "oos": ...}``
    segments: dict = field(default_factory=dict)
    #: reference backtest on ``if_else(rank(cap) > settings.subuniverse, f, nan)``
    subuniverse: Optional[SubUniverseResult] = None

    def to_dict(self) -> dict:
        return {
            "settings": {
                "y": self.settings.y,
                "delay": self.settings.delay,
                "decay": self.settings.decay,
                "transform": self.settings.transform,
                "cap_filter": self.settings.cap_filter,
                "neutralize": self.settings.neutralize,
                "cost_bps": self.settings.cost_bps,
                "subuniverse": self.settings.subuniverse,
            },
            "metrics": self.metrics,
            "segments": self.segments,
            "subuniverse": self.subuniverse.to_dict() if self.subuniverse else None,
            "yearly": self.yearly.reset_index().to_dict(orient="records"),
        }


# --------------------------------------------------------------------------- #
# returns
# --------------------------------------------------------------------------- #
def forward_returns(panel: PanelStore, y: str = "close_to_close") -> pd.DataFrame:
    """Daily forward return.

    ``close_to_close`` is the default and the only convention used by the
    mining loop: ``r_t = close_t / close_{t-1} - 1``.  It is served from the
    cached ``returns`` field of the panel; any other price field is accepted and
    converted to a simple return.
    """
    if y == "close_to_close":
        if "close" not in panel:
            raise BacktestError("panel has no 'close' field")
        # cached on the panel: recomputing pct_change on 8M cells per grid point
        # is the single most wasted second in the sweep
        ret = panel.field("returns")
    elif y == "returns":
        ret = panel.field("returns")
    elif panel.has(y):
        ret = panel.field(y).pct_change(fill_method=None)
    else:
        raise BacktestError(f"unknown return definition / field {y!r}")
    return ret.astype("float64")


# --------------------------------------------------------------------------- #
# factor -> weights
# --------------------------------------------------------------------------- #
def prepare_factor(
    raw: pd.DataFrame,
    panel: PanelStore,
    settings: BacktestSettings,
    universe_mask: Optional[pd.DataFrame] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply cap filter, cross-sectional transform and decay.

    Returns ``(factor_used, weights)`` where ``weights`` is the tradable book.
    Order: cap filter -> transform -> decay -> demean -> unit gross exposure.
    """
    f = raw.reindex(index=panel.dates, columns=panel.tickers).astype("float64")
    f = f.replace([np.inf, -np.inf], np.nan)
    if universe_mask is not None:
        mask = universe_mask.reindex(index=f.index, columns=f.columns)
        f = f.where(mask.fillna(False).astype(bool))
    arr = f.to_numpy(copy=False)

    if settings.cap_filter is not None:
        if "cap" not in panel:
            raise BacktestError("cap filter requested but panel has no 'cap' field")
        cap_rank = panel.field("cap_rank").to_numpy(copy=False)
        arr = np.where(cap_rank > float(settings.cap_filter), arr, np.nan)
        f = pd.DataFrame(arr, index=f.index, columns=f.columns)

    transform = settings.transform
    if transform == "rank":
        f = f.rank(axis=1, pct=True, method="average")
    elif transform == "sign":
        f = pd.DataFrame(np.sign(f.to_numpy(copy=False)), index=f.index, columns=f.columns)
    elif transform == "zscore":
        mu = f.mean(axis=1)
        sd = f.std(axis=1).replace(0.0, np.nan)
        f = f.sub(mu, axis=0).div(sd, axis=0)
    elif transform not in ("none", None):
        raise BacktestError(f"unknown transform {transform!r}")

    if settings.decay and int(settings.decay) > 0:
        from ..expr.ops import _ts_decay_linear

        f = _ts_decay_linear(f, int(settings.decay))

    farr = f.to_numpy(dtype="float64", copy=False)
    finite = np.isfinite(farr)
    if settings.neutralize:
        counts = finite.sum(axis=1)
        sums = np.nansum(farr, axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            mu = sums / np.where(counts > 0, counts, np.nan)
        w = farr - mu[:, None]
    else:
        w = farr.copy()
    gross = np.nansum(np.abs(w), axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        w = w / np.where(gross > 0, gross, np.nan)[:, None]

    n_valid = finite.sum(axis=1)
    thin = n_valid < settings.min_names
    if thin.any():
        w[thin, :] = 0.0
    w = np.nan_to_num(w, nan=0.0, posinf=0.0, neginf=0.0)

    weights = pd.DataFrame(w, index=f.index, columns=f.columns)
    return f, weights


# --------------------------------------------------------------------------- #
# backtest
# --------------------------------------------------------------------------- #
def run_backtest(
    raw: pd.DataFrame,
    panel: PanelStore,
    settings: BacktestSettings = BacktestSettings(),
    universe_mask: Optional[pd.DataFrame] = None,
) -> BacktestResult:
    ret_df = forward_returns(panel, settings.y)
    f, w_df = prepare_factor(raw, panel, settings, universe_mask=universe_mask)

    ret = ret_df.to_numpy(dtype="float64", copy=False)
    w = w_df.to_numpy(dtype="float64", copy=False)
    T, N = w.shape
    delay = int(settings.delay)
    if delay > 0:
        w_lag = np.vstack([np.full((delay, N), np.nan), w[:-delay]])
        ret_mask = np.isnan(ret).all(axis=1)
    else:
        w_lag = w
        ret_mask = np.isnan(ret).all(axis=1)

    with np.errstate(invalid="ignore"):
        gross = np.nansum(w_lag * ret, axis=1)
    gross = np.where(ret_mask, np.nan, gross)

    if T > 1:
        w_prev = np.vstack([np.full((1, N), np.nan), w[:-1]])
        traded = np.nansum(np.abs(w - w_prev), axis=1)
    else:
        traded = np.full(T, np.nan)
    to = 0.5 * traded
    if delay > 0:
        cost = np.concatenate([np.zeros(delay), traded[:-delay]]) * float(settings.cost_bps) / 1e4
    else:
        cost = traded * float(settings.cost_bps) / 1e4
    net = gross - cost
    net = np.where(np.isfinite(net), net, np.nan)

    idx = ret_df.index
    net_s = pd.Series(net, index=idx, name="pnl")
    to_s = pd.Series(np.where(np.isfinite(to), to, np.nan), index=idx, name="turnover")

    if settings.compute_ic:
        fwd = ret_df.shift(-delay)
        min_ic_names = max(10, settings.min_names // 2)
        ic_s = M.xs_spearman(f, fwd, min_names=min_ic_names)
        pearson_s = M.xs_pearson(f, fwd, min_names=min_ic_names)
    else:
        ic_s = pd.Series(np.nan, index=idx, name="ic")
        pearson_s = pd.Series(np.nan, index=idx, name="pearson_ic")

    metrics = M.summarise_pnl(net_s, to_s, ic_s, pearson_ic=pearson_s, ann=settings.ann)
    valid_counts = pd.Series(np.isfinite(f.to_numpy()).sum(axis=1), index=idx)
    metrics["n_names"] = float(valid_counts.reindex(net_s.dropna().index).mean())
    metrics["factor_coverage"] = float(np.isfinite(f.to_numpy()).mean())

    yearly = yearly_table(net_s, to_s, ic_s, settings.ann)

    return BacktestResult(
        settings=settings,
        metrics=metrics,
        yearly=yearly,
        pnl=net_s,
        turnover=to_s,
        ic=ic_s,
        pearson_ic=pearson_s,
        factor=f,
        positions=w_df if settings.keep_positions else None,
    )


# --------------------------------------------------------------------------- #
# sub-universe reference backtest
# --------------------------------------------------------------------------- #
def subuniverse_mask(panel: PanelStore, threshold: float = 0.3) -> pd.DataFrame:
    """``if_else(rank(cap) > threshold, True, False)`` on the panel grid."""
    if "cap" not in panel:
        raise BacktestError("subuniverse requested but panel has no 'cap' field")
    return panel.field("cap_rank") > float(threshold)


def run_backtest_with_subuniverse(
    raw: pd.DataFrame,
    panel: PanelStore,
    settings: BacktestSettings = BacktestSettings(),
    universe_mask: Optional[pd.DataFrame] = None,
) -> BacktestResult:
    """Full-universe backtest plus the reference sub-universe one.

    The primary result is untouched; ``result.subuniverse`` holds the book
    rebuilt after masking out names whose cap rank is below
    ``settings.subuniverse``.  Disabled when the threshold is ``None`` or
    ``settings.compute_subuniverse`` is ``False``.
    """
    main = run_backtest(raw, panel, settings, universe_mask=universe_mask)
    threshold = settings.subuniverse
    if threshold is None or not settings.compute_subuniverse:
        return main

    mask = subuniverse_mask(panel, float(threshold))
    if universe_mask is not None:
        base = universe_mask.reindex(index=mask.index, columns=mask.columns)
        mask = mask & base.fillna(False).astype(bool)
    sub = run_backtest(raw, panel, settings, universe_mask=mask)
    main.subuniverse = SubUniverseResult(
        threshold=float(threshold),
        metrics=sub.metrics,
        pnl=sub.pnl,
        turnover=sub.turnover,
        ic=sub.ic,
        pearson_ic=sub.pearson_ic,
        factor=sub.factor,
    )
    return main


def yearly_table(net: pd.Series, to: pd.Series, ic: pd.Series, ann: int) -> pd.DataFrame:
    rows = []
    net_clean = net.dropna()
    if net_clean.empty:
        return pd.DataFrame(
            columns=["total_return", "sharpe", "turnover", "max_drawdown", "ic", "n_days"]
        )
    years = net_clean.index.year
    for year in sorted(set(years)):
        sub = net_clean.loc[years == year]
        cum = (1.0 + sub).cumprod()
        rows.append(
            {
                "year": int(year),
                "total_return": float(cum.iloc[-1] - 1.0),
                "sharpe": M.sharpe_ratio(sub, ann),
                "turnover": float(to.reindex(sub.index).mean() * ann),
                "max_drawdown": M.max_drawdown(cum),
                "ic": float(ic.reindex(sub.index).mean()),
                "n_days": int(len(sub)),
            }
        )
    return pd.DataFrame(rows).set_index("year")

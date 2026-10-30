"""Statistics used by the backtester and the factor pool."""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def xs_spearman(
    a: pd.DataFrame, b: pd.DataFrame, min_names: int = 10
) -> pd.Series:
    """Per-date cross-sectional Spearman correlation of two factor matrices.

    NaNs are handled pairwise: only names present in both matrices on a given
    date enter that date's correlation.  Dates with fewer than ``min_names``
    overlapping names are dropped (not set to zero).
    """
    idx = a.index
    cols = a.columns
    if not (idx.equals(b.index) and cols.equals(b.columns)):
        idx = a.index.intersection(b.index)
        cols = a.columns.intersection(b.columns)
        a = a.reindex(index=idx, columns=cols)
        b = b.reindex(index=idx, columns=cols)

    valid = a.notna() & b.notna()
    n = valid.sum(axis=1)
    aa = a.where(valid).rank(axis=1, method="average")
    bb = b.where(valid).rank(axis=1, method="average")

    aa = aa.sub(aa.mean(axis=1), axis=0)
    bb = bb.sub(bb.mean(axis=1), axis=0)
    num = (aa * bb).sum(axis=1, min_count=1)
    den = np.sqrt((aa**2).sum(axis=1) * (bb**2).sum(axis=1))
    corr = num / den.replace(0.0, np.nan)
    corr = corr.where(n >= min_names)
    corr.name = "xs_spearman"
    return corr


def xs_pearson(
    a: pd.DataFrame, b: pd.DataFrame, min_names: int = 10
) -> pd.Series:
    """Per-date cross-sectional Pearson correlation of two factor matrices."""
    if not (a.index.equals(b.index) and a.columns.equals(b.columns)):
        idx = a.index.intersection(b.index)
        cols = a.columns.intersection(b.columns)
        a = a.reindex(index=idx, columns=cols)
        b = b.reindex(index=idx, columns=cols)

    valid = a.notna() & b.notna()
    n = valid.sum(axis=1)
    aa = a.where(valid)
    bb = b.where(valid)
    aa = aa.sub(aa.mean(axis=1), axis=0)
    bb = bb.sub(bb.mean(axis=1), axis=0)
    num = (aa * bb).sum(axis=1, min_count=1)
    den = np.sqrt((aa**2).sum(axis=1) * (bb**2).sum(axis=1))
    corr = num / den.replace(0.0, np.nan)
    corr = corr.where(n >= min_names)
    corr.name = "xs_pearson"
    return corr


def spearman_over_time(
    a: pd.DataFrame, b: pd.DataFrame, min_names: int = 10
) -> dict:
    """Summarise the cross-sectional rank correlation between two factors."""
    s = xs_spearman(a, b, min_names=min_names).dropna()
    if s.empty:
        return {"mean": float("nan"), "std": float("nan"), "n_days": 0}
    return {
        "mean": float(s.mean()),
        "std": float(s.std()),
        "n_days": int(s.size),
        "positive_ratio": float((s > 0).mean()),
    }


def pearson(a: pd.Series, b: pd.Series) -> dict:
    """Pearson correlation of two PnL series on their common dates."""
    idx = a.dropna().index.intersection(b.dropna().index)
    if len(idx) < 3:
        return {"pearson": float("nan"), "n_days": int(len(idx))}
    x = a.reindex(idx).to_numpy(dtype=float)
    y = b.reindex(idx).to_numpy(dtype=float)
    if x.std() == 0 or y.std() == 0:
        return {"pearson": float("nan"), "n_days": int(len(idx))}
    return {"pearson": float(np.corrcoef(x, y)[0, 1]), "n_days": int(len(idx))}


def max_drawdown(cum: pd.Series) -> float:
    if cum.empty:
        return float("nan")
    peak = cum.cummax()
    dd = cum / peak - 1.0
    return float(dd.min())


def sharpe_ratio(returns: pd.Series, ann: int = 252) -> float:
    r = returns.dropna()
    if len(r) < 5 or r.std() == 0:
        return float("nan")
    return float(r.mean() / r.std() * np.sqrt(ann))


def annualized_return(cum: pd.Series, ann: int = 252) -> float:
    cum = cum.dropna()
    if len(cum) < 2 or cum.iloc[-1] <= 0:
        return float("nan")
    n = len(cum)
    return float(cum.iloc[-1] ** (ann / n) - 1.0)


def turnover_series(weights: pd.DataFrame) -> pd.Series:
    """One-way turnover: half the sum of absolute weight changes."""
    return 0.5 * (weights - weights.shift(1)).abs().sum(axis=1)


def summarise_pnl(
    net: pd.Series,
    turnover: pd.Series,
    ic: Optional[pd.Series] = None,
    pearson_ic: Optional[pd.Series] = None,
    ann: int = 252,
) -> dict:
    net = net.dropna()
    if net.empty:
        return {
            "n_days": 0,
            "sharpe": float("nan"),
            "ann_return": float("nan"),
            "total_return": float("nan"),
            "max_drawdown": float("nan"),
            "turnover": float("nan"),
        }
    cum = (1.0 + net).cumprod()
    ann_ret = annualized_return(cum, ann)
    ann_vol = float(net.std() * np.sqrt(ann))
    shp = sharpe_ratio(net, ann)
    to = float(turnover.reindex(net.index).mean() * ann)
    out = {
        "n_days": int(net.size),
        "total_return": float(cum.iloc[-1] - 1.0),
        "ann_return": ann_ret,
        "ann_vol": ann_vol,
        "sharpe": shp,
        "max_drawdown": max_drawdown(cum),
        "turnover": to,
        "hit_rate": float((net > 0).mean()),
        "fitness": float(shp * np.sqrt(abs(ann_ret) / max(to, 0.125)))
        if np.isfinite(shp) and np.isfinite(ann_ret)
        else float("nan"),
    }
    if ic is not None:
        ic = ic.dropna()
        # ``ic`` is the cross-sectional *rank* IC (daily Spearman); the name is
        # kept for backward compatibility, ``rank_ic`` is the explicit alias
        out["rank_ic"] = float(ic.mean()) if not ic.empty else float("nan")
        out["rank_ic_ir"] = (
            float(ic.mean() / ic.std()) if len(ic) > 2 and ic.std() > 0 else float("nan")
        )
        out["rank_ic_positive_ratio"] = (
            float((ic > 0).mean()) if not ic.empty else float("nan")
        )
        out["ic"] = out["rank_ic"]
        out["ic_ir"] = out["rank_ic_ir"]
        out["ic_positive_ratio"] = out["rank_ic_positive_ratio"]
    if pearson_ic is not None:
        pic = pearson_ic.dropna()
        out["pearson_ic"] = float(pic.mean()) if not pic.empty else float("nan")
        out["pearson_ic_ir"] = (
            float(pic.mean() / pic.std()) if len(pic) > 2 and pic.std() > 0 else float("nan")
        )
        out["pearson_ic_positive_ratio"] = (
            float((pic > 0).mean()) if not pic.empty else float("nan")
        )
    return out

"""Operator registry: the vocabulary an agent may use in an expression.

Every operator is a pure function over a ``date x ticker`` DataFrame (or a
scalar, which broadcasts).  The registry doubles as documentation: the
implementer agent (2.2) receives :func:`catalog_text`, the validator checks arity and
window arguments against :data:`ALLOWED_WINDOWS`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional

import numpy as np
import pandas as pd

from ..config import ALLOWED_WINDOWS


class OpError(ValueError):
    """Raised when an operator is called with invalid arguments."""


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _minp(d: int) -> int:
    """Minimum observations inside a rolling window (half window, at least 3)."""
    return max(3, int(d) // 2)


def _is_df(x) -> bool:
    return isinstance(x, pd.DataFrame)


def _like(y, x: pd.DataFrame) -> pd.DataFrame:
    """Broadcast a scalar / Series to the shape of ``x``."""
    if isinstance(y, pd.DataFrame):
        return y
    if isinstance(y, pd.Series):
        return pd.DataFrame(
            np.repeat(y.to_numpy()[:, None], x.shape[1], axis=1),
            index=x.index,
            columns=x.columns,
        )
    return pd.DataFrame(float(y), index=x.index, columns=x.columns)


def _num(x):
    return x.astype("float64") if _is_df(x) else float(x)


# --------------------------------------------------------------------------- #
# element-wise
# --------------------------------------------------------------------------- #
def _abs(x):
    return _num(x).abs() if _is_df(x) else abs(x)


def _sign(x):
    return np.sign(_num(x))


def _log(x):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log(_num(x))


def _log1p(x):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log1p(_num(x).clip(lower=-0.999999))


def _sqrt(x):
    return np.sqrt(_num(x).clip(lower=0))


def _exp(x):
    return np.exp(_num(x).clip(upper=50))


def _signed_power(x, a):
    return np.sign(_num(x)) * np.abs(_num(x)) ** float(a)


def _clip(x, lo, hi):
    return _num(x).clip(lower=float(lo), upper=float(hi))


def _nan_to_num(x, value=0.0):
    return _num(x).fillna(float(value))


def _maximum(x, y):
    if _is_df(x) or _is_df(y):
        base = x if _is_df(x) else y
        return np.maximum(_num(x), _like(y, base))
    return max(x, y)


def _minimum(x, y):
    if _is_df(x) or _is_df(y):
        base = x if _is_df(x) else y
        return np.minimum(_num(x), _like(y, base))
    return min(x, y)


# --------------------------------------------------------------------------- #
# cross-sectional (per date)
# --------------------------------------------------------------------------- #
def _rank(x):
    if not _is_df(x):
        return x
    return x.rank(axis=1, pct=True, method="average")


def _zscore(x):
    if not _is_df(x):
        return x
    mu = x.mean(axis=1)
    sd = x.std(axis=1).replace(0.0, np.nan)
    return x.sub(mu, axis=0).div(sd, axis=0)


def _demean(x):
    if not _is_df(x):
        return x
    return x.sub(x.mean(axis=1), axis=0)


def _scale(x, a=1.0):
    if not _is_df(x):
        return x
    denom = x.abs().sum(axis=1).replace(0.0, np.nan)
    return x.div(denom, axis=0) * float(a)


def _winsorize(x, p=0.01):
    if not _is_df(x):
        return x
    lo = x.quantile(float(p), axis=1)
    hi = x.quantile(1.0 - float(p), axis=1)
    return x.clip(lower=lo, upper=hi, axis=0)


# --------------------------------------------------------------------------- #
# time-series (per ticker)
# --------------------------------------------------------------------------- #
def _ts_apply(x, d, method: str):
    if not _is_df(x):
        return x
    d = int(d)
    return getattr(x.rolling(d, min_periods=_minp(d)), method)()


def _ts_roll(x, d, method: Optional[str] = None, min_periods: Optional[int] = None):
    """Rolling view / reduction with the reference policy: a full valid window.

    The vetted implementation in ``factorlab/agents/research/operators.py`` uses
    ``rolling(d, min_periods=d)`` -- deliberately stricter than the partial
    windows in the source document. ``method=None`` returns the rolling object.
    """
    if not _is_df(x):
        return x
    d = int(d)
    mp = d if min_periods is None else int(min_periods)
    roll = x.rolling(d, min_periods=mp)
    return roll if method is None else getattr(roll, method)()


def _safe_div(left, right, epsilon: float = 1e-12):
    """Division that masks near-zero denominators (reference ``safe_div``)."""
    if isinstance(right, (int, float)):
        return left / right if abs(right) > epsilon else left * np.nan
    return left / right.where(right.abs() > epsilon)


def _delay(x, d):
    return x.shift(int(d)) if _is_df(x) else x


def _delta(x, d):
    return x - x.shift(int(d)) if _is_df(x) else x


def _ts_returns(x, d):
    if not _is_df(x):
        return x
    return x / x.shift(int(d)).replace(0.0, np.nan) - 1.0


def _ts_decay_linear(x, d):
    if not _is_df(x):
        return x
    d = int(d)
    if d <= 1:
        return x.copy()
    arr = x.to_numpy(dtype="float64")
    T, N = arr.shape
    out = np.full((T, N), np.nan)
    if d > T:
        return pd.DataFrame(out, index=x.index, columns=x.columns)
    valid = np.isfinite(arr)
    z = np.where(valid, arr, 0.0)
    t = np.arange(T, dtype="float64")[:, None]
    S = np.cumsum(z, axis=0)
    W = np.cumsum(z * t, axis=0)
    C = np.cumsum(valid, axis=0).astype("float64")
    pad = np.zeros((1, N))
    Sp = np.vstack([pad, S])
    Wp = np.vstack([pad, W])
    Cp = np.vstack([pad, C])
    wsum = Sp[d:] - Sp[:-d]
    wwin = Wp[d:] - Wp[:-d]
    cwin = Cp[d:] - Cp[:-d]
    tidx = np.arange(d - 1, T, dtype="float64")[:, None]
    num = wwin - (tidx - d) * wsum
    res = num / (d * (d + 1) / 2.0)
    res = np.where(cwin >= _minp(d), res, np.nan)
    out[d - 1 :] = res
    return pd.DataFrame(out, index=x.index, columns=x.columns)


def _ts_corr(x, y, d):
    if not _is_df(x):
        return x
    d = int(d)
    return x.rolling(d, min_periods=_minp(d)).corr(_like(y, x))


def _ts_cov(x, y, d):
    if not _is_df(x):
        return x
    d = int(d)
    return x.rolling(d, min_periods=_minp(d)).cov(_like(y, x))


def _ts_arg(x, d, which: str):
    if not _is_df(x):
        return x
    d = int(d)
    arr = x.to_numpy(dtype=float)
    T, N = arr.shape
    out = np.full((T, N), np.nan)
    if d > T:
        return pd.DataFrame(out, index=x.index, columns=x.columns)
    from numpy.lib.stride_tricks import sliding_window_view

    for j in range(N):
        W = sliding_window_view(arr[:, j], d)
        valid = np.isfinite(W)
        filled = np.where(valid, W, -np.inf if which == "max" else np.inf)
        pos = (
            np.argmax(filled, axis=1)
            if which == "max"
            else np.argmin(filled, axis=1)
        )
        res = (pos + 1.0) / d
        res = np.where(valid.sum(axis=1) >= _minp(d), res, np.nan)
        res = np.where(np.isfinite(arr[d - 1 :, j]), res, np.nan)
        out[d - 1 :, j] = res
    return pd.DataFrame(out, index=x.index, columns=x.columns)


def _ts_rank(x, d):
    if not _is_df(x):
        return x
    d = int(d)
    arr = x.to_numpy(dtype=float)
    T, N = arr.shape
    out = np.full((T, N), np.nan)
    if d > T:
        return pd.DataFrame(out, index=x.index, columns=x.columns)
    from numpy.lib.stride_tricks import sliding_window_view

    for j in range(N):
        col = arr[:, j]
        W = sliding_window_view(col, d)
        last = W[:, -1]
        valid = np.isfinite(W)
        cnt = valid.sum(axis=1)
        less = ((W <= last[:, None]) & valid).sum(axis=1)
        res = np.where(cnt > 0, less / np.maximum(cnt, 1), np.nan)
        res = np.where(cnt >= _minp(d), res, np.nan)
        res = np.where(np.isfinite(last), res, np.nan)
        out[d - 1 :, j] = res
    return pd.DataFrame(out, index=x.index, columns=x.columns)


def _ts_ir(x, d):
    if not _is_df(x):
        return x
    mean = _ts_roll(x, d, "mean")
    std = x.rolling(int(d), min_periods=int(d)).std(ddof=0)
    return _safe_div(mean, std, epsilon=1e-10)


# --------------------------------------------------------------------------- #
# conditional
# --------------------------------------------------------------------------- #
def _if_else(cond, a, b):
    if _is_df(cond):
        idx, cols = cond.index, cond.columns
        c = cond.to_numpy(dtype=bool)
        av = _like(a, cond).to_numpy(dtype=float) if not np.isscalar(a) else float(a)
        bv = _like(b, cond).to_numpy(dtype=float) if not np.isscalar(b) else float(b)
        out = np.where(c, av, bv)
        return pd.DataFrame(out, index=idx, columns=cols)
    return a if bool(cond) else b


def _mask(x, cond):
    if not _is_df(cond):
        return x if bool(cond) else (x * np.nan)
    return x.where(cond)


# --------------------------------------------------------------------------- #
# registry
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Arg:
    name: str
    kind: str = "value"  # value | window | lag | scalar
    default: Optional[float] = None


@dataclass(frozen=True)
class Operator:
    name: str
    category: str
    func: Callable
    args: tuple[Arg, ...]
    doc: str
    min_args: int = 0
    max_args: int = 0

    def window_positions(self) -> tuple[int, ...]:
        """Arguments replaced by the grid search (must be an allowed horizon)."""
        return tuple(i for i, a in enumerate(self.args) if a.kind == "window")

    def lag_positions(self) -> tuple[int, ...]:
        """Fixed lags: economically meaningful at any positive integer (e.g. 1)."""
        return tuple(i for i, a in enumerate(self.args) if a.kind == "lag")


REGISTRY: dict[str, Operator] = {}


def register(
    name: str,
    category: str,
    args: Iterable[Arg],
    doc: str,
    min_args: Optional[int] = None,
    max_args: Optional[int] = None,
):
    args = tuple(args)

    def deco(fn: Callable):
        REGISTRY[name] = Operator(
            name=name,
            category=category,
            func=fn,
            args=args,
            doc=doc,
            min_args=len([a for a in args if a.default is None]) if min_args is None else min_args,
            max_args=len(args) if max_args is None else max_args,
        )
        return fn

    return deco


W = Arg("d", "window")
X = Arg("x")
Y = Arg("y")

register("abs", "element-wise", [X], "absolute value", 1, 1)(_abs)
register("sign", "element-wise", [X], "sign in {-1,0,1} per stock per day", 1, 1)(_sign)
register("log", "element-wise", [X], "natural log (non-positive -> nan)", 1, 1)(_log)
register("log1p", "element-wise", [X], "log(1+x)", 1, 1)(_log1p)
register("sqrt", "element-wise", [X], "square root of clipped non-negative", 1, 1)(_sqrt)
register("exp", "element-wise", [X], "exponential (clipped to avoid overflow)", 1, 1)(_exp)
register("signed_power", "element-wise", [X, Arg("a")], "sign(x)*|x|^a", 2, 2)(
    _signed_power
)
register("clip", "element-wise", [X, Arg("lo"), Arg("hi")], "clip to [lo, hi]", 3, 3)(
    _clip
)
register("nan_to_num", "element-wise", [X, Arg("v", "scalar", 0.0)], "replace nan", 1, 2)(
    _nan_to_num
)
register("max", "element-wise", [X, Y], "element-wise maximum", 2, 2)(_maximum)
register("min", "element-wise", [X, Y], "element-wise minimum", 2, 2)(_minimum)

register("rank", "cross-sectional", [X], "cross-sectional percentile rank in [0,1] per day", 1, 1)(
    _rank
)
register("zscore", "cross-sectional", [X], "cross-sectional z-score per day", 1, 1)(_zscore)
register("demean", "cross-sectional", [X], "subtract the cross-sectional mean", 1, 1)(_demean)
register("scale", "cross-sectional", [X, Arg("a", "scalar", 1.0)], "x / sum|x| * a", 1, 2)(
    _scale
)
register("winsorize", "cross-sectional", [X, Arg("p", "scalar", 0.01)], "clip daily tails", 1, 2)(
    _winsorize
)

register("delay", "time-series", [X, Arg("d", "lag")], "value d days ago (lag, e.g. 1)", 2, 2)(_delay)
register("delta", "time-series", [X, Arg("d", "lag")], "x - delay(x, d) (lag)", 2, 2)(_delta)
register("ts_returns", "time-series", [X, W], "x / delay(x,d) - 1", 2, 2)(_ts_returns)
register("ts_sum", "time-series", [X, W], "rolling sum", 2, 2)(
    lambda x, d: _ts_roll(x, d, "sum")
)
register("ts_mean", "time-series", [X, W], "rolling mean", 2, 2)(
    lambda x, d: _ts_roll(x, d, "mean")
)
register("ts_std", "time-series", [X, W], "rolling standard deviation", 2, 2)(
    lambda x, d: _ts_apply(x, d, "std")
)
register("ts_min", "time-series", [X, W], "rolling minimum", 2, 2)(
    lambda x, d: _ts_roll(x, d, "min")
)
register("ts_max", "time-series", [X, W], "rolling maximum", 2, 2)(
    lambda x, d: _ts_roll(x, d, "max")
)
register("ts_median", "time-series", [X, W], "rolling median", 2, 2)(
    lambda x, d: _ts_roll(x, d, "median")
)
register("ts_skew", "time-series", [X, W], "rolling skewness", 2, 2)(
    lambda x, d: _ts_apply(x, d, "skew")
)
register("ts_kurt", "time-series", [X, W], "rolling kurtosis", 2, 2)(
    lambda x, d: _ts_apply(x, d, "kurt")
)
register("ts_rank", "time-series", [X, W], "percentile rank of today's value in the window", 2, 2)(
    _ts_rank
)
def _ts_zscore(x, d):
    if not _is_df(x):
        return x
    roll = x.rolling(int(d), min_periods=int(d))
    mean, std = roll.mean(), roll.std(ddof=0)
    res = _safe_div(x - mean, std, epsilon=1e-14)
    return res.mask((std.abs() < 1e-14) & std.notna(), 0.0)


register("ts_zscore", "time-series", [X, W], "(x - ts_mean) / ts_std", 2, 2)(_ts_zscore)
register("ts_ir", "time-series", [X, W], "ts_mean / ts_std", 2, 2)(_ts_ir)
register("ts_argmax", "time-series", [X, W], "normalized position of the window max", 2, 2)(
    lambda x, d: _ts_arg(x, d, "max")
)
register("ts_argmin", "time-series", [X, W], "normalized position of the window min", 2, 2)(
    lambda x, d: _ts_arg(x, d, "min")
)
register("ts_corr", "time-series", [X, Y, W], "rolling correlation", 3, 3)(_ts_corr)
register("ts_cov", "time-series", [X, Y, W], "rolling covariance", 3, 3)(_ts_cov)
register("ts_decay_linear", "time-series", [X, W], "linear decay, recent weighted most", 2, 2)(
    _ts_decay_linear
)

register("if_else", "conditional", [Arg("cond"), Arg("a"), Arg("b")], "cond ? a : b", 3, 3)(
    _if_else
)
register("mask", "conditional", [X, Arg("cond")], "x where cond else nan", 2, 2)(_mask)


# --------------------------------------------------------------------------- #
# approved time-series operators (spec: docs/operators.md)
# --------------------------------------------------------------------------- #
#: window reductions are evaluated in column blocks to bound peak memory on a
#: 6700 x 1200 panel; ~100 MB per temporary
_WINDOW_BUDGET = 100e6


def _window_reduce(x, d, fn, min_periods=1):
    """Apply ``fn(window_matrix) -> (T-d+1, b)`` along the time axis."""
    from numpy.lib.stride_tricks import sliding_window_view

    arr = x.to_numpy(dtype="float64")
    T, N = arr.shape
    d = int(d)
    out = np.full((T, N), np.nan)
    if d > T or N == 0:
        return pd.DataFrame(out, index=x.index, columns=x.columns)
    m = max(1, int(min_periods))
    span = max(1, T - d + 1)
    block = max(1, min(N, int(_WINDOW_BUDGET / (8.0 * d * span))))
    for j0 in range(0, N, block):
        chunk = arr[:, j0 : j0 + block]
        W = sliding_window_view(chunk, d, axis=0)
        valid = np.isfinite(W).sum(axis=2)
        with np.errstate(all="ignore"):
            res = fn(W)
        res = np.where(valid >= m, res, np.nan)
        out[d - 1 :, j0 : j0 + block] = res
    return pd.DataFrame(out, index=x.index, columns=x.columns)


def _ts_std_dev(x, d):
    if not _is_df(x):
        return x
    return x.rolling(int(d), min_periods=int(d)).std(ddof=0)


def _ts_ema(x, d):
    if not _is_df(x):
        return x
    d = int(d)
    full = x.rolling(d, min_periods=d).count() == d
    return x.ewm(span=d, adjust=False, min_periods=d).mean().where(full)


def _ts_percentage(x, d, percentage=0.5):
    if not _is_df(x):
        return x
    return x.rolling(int(d), min_periods=int(d)).quantile(float(percentage))


def _ts_scale(x, d, constant=0.0):
    if not _is_df(x):
        return x
    d = int(d)
    roll = x.rolling(d, min_periods=d)
    rmin, rmax = roll.min(), roll.max()
    return _safe_div(x - rmin, rmax - rmin, epsilon=1e-10) + float(constant)


def _ts_rank_spec(x, d, constant=0.0):
    """``constant=1`` -> percentile rank; otherwise the integer rank in 1..d."""
    if float(constant) == 1.0:
        return _ts_rank(x, d)
    d = int(d)

    def fn(W):
        last = W[:, :, -1]
        valid = np.isfinite(W)
        res = ((W <= last[:, :, None]) & valid).sum(axis=2).astype("float64")
        return np.where(np.isfinite(last), res, np.nan)

    return _window_reduce(x, d, fn, min_periods=_minp(d))


def _ts_quantile(x, d, driver="gaussian"):
    if not _is_df(x):
        return x
    rank = _ts_rank(x, d)
    if driver == "uniform":
        return rank
    if driver != "gaussian":
        raise OpError(f"ts_quantile: unknown driver {driver!r}")
    from scipy.stats import norm

    arr = norm.ppf(np.clip(rank.to_numpy(dtype="float64"), 1e-10, 1 - 1e-10))
    return pd.DataFrame(arr, index=x.index, columns=x.columns)


def _ts_arg_lag(x, d, which):
    """Days since the window max/min (0 = today)."""
    d = int(d)

    def fn(W):
        valid = np.isfinite(W)
        fill = np.where(valid, W, -np.inf if which == "max" else np.inf)
        pos = np.argmax(fill, axis=2) if which == "max" else np.argmin(fill, axis=2)
        res = (d - 1 - pos).astype("float64")
        return np.where(np.isfinite(W[:, :, -1]), res, np.nan)

    return _window_reduce(x, d, fn, min_periods=_minp(d))


def _ts_product(x, d):
    return _window_reduce(
        x, d, lambda W: np.nanprod(W, axis=2), min_periods=_minp(d)
    )


def _ts_hhi(x, d):
    def fn(W):
        mag = np.abs(W)
        total = np.nansum(mag, axis=2)
        share = mag / np.where(total > 0, total, np.nan)[:, :, None]
        return np.nansum(share**2, axis=2)

    return _window_reduce(x, d, fn, min_periods=_minp(d))


def _ts_entropy(x, d):
    def fn(W):
        mag = np.abs(W)
        total = np.nansum(mag, axis=2)
        share = mag / np.where(total > 0, total, np.nan)[:, :, None]
        with np.errstate(divide="ignore", invalid="ignore"):
            terms = np.where(share > 0, share * np.log(share), 0.0)
        return -np.nansum(terms, axis=2)

    return _window_reduce(x, d, fn, min_periods=_minp(d))


def _ts_mad(x, d):
    def fn(W):
        mu = np.nanmean(W, axis=2, keepdims=True)
        return np.nanmean(np.abs(W - mu), axis=2)

    return _window_reduce(x, d, fn, min_periods=_minp(d))


def _ts_max_drawdown(x, d):
    def fn(W):
        filled = np.where(np.isfinite(W), W, -np.inf)
        peak = np.maximum.accumulate(filled, axis=2)
        safe = np.where(np.isfinite(peak) & (peak > -np.inf), peak, np.nan)
        with np.errstate(all="ignore"):
            dd = W / safe - 1.0
        return np.nanmin(dd, axis=2)

    return _window_reduce(x, d, fn, min_periods=_minp(d))


def _ts_gain_loss_ratio(x, d):
    def fn(W):
        diff = W[:, :, 1:] - W[:, :, :-1]
        gains = np.nansum(np.where(diff > 0, diff, 0.0), axis=2)
        losses = np.nansum(np.where(diff < 0, -diff, 0.0), axis=2)
        return np.where(losses > 0, gains / np.where(losses > 0, losses, np.nan), np.nan)

    return _window_reduce(x, d, fn, min_periods=_minp(d))


def _ts_positive_ratio(x, d):
    if not _is_df(x):
        return x
    positive = (x > 0).where(x.notna())
    return positive.rolling(int(d), min_periods=1).mean()


def _ts_count_nans(x, d):
    if not _is_df(x):
        return x
    return x.isna().astype(float).rolling(int(d), min_periods=int(d)).sum()


def _ts_bollinger(x, d, k):
    roll = _ts_roll(x, d)
    ma, sd = roll.mean(), roll.std(ddof=0)
    return ma, sd


def _ts_bollinger_percent(x, d, k=2.0):
    if not _is_df(x):
        return x
    ma, sd = _ts_bollinger(x, d, k)
    k = float(k)
    return _safe_div(x - (ma - k * sd), 2.0 * k * sd)


def _ts_bollinger_position(x, d, k=2.0):
    pct = _ts_bollinger_percent(x, d, k)
    return pct.clip(0, 1) if _is_df(pct) else pct


def _ts_bollinger_width(x, d, k=2.0):
    if not _is_df(x):
        return x
    ma, sd = _ts_bollinger(x, d, k)
    return _safe_div(2.0 * float(k) * sd, ma.abs(), epsilon=1e-12)


def _ts_max_diff(x, d):
    return x - _ts_roll(x, d, "max")


def _ts_min_diff(x, d):
    return x - _ts_roll(x, d, "min")


def _ts_min_max_diff(x, d, f=0.5):
    return x - float(f) * (_ts_roll(x, d, "min") + _ts_roll(x, d, "max"))


def _ts_range(x, d):
    return _ts_roll(x, d, "max") - _ts_roll(x, d, "min")


def _ts_extreme_ratio(x, d):
    return _safe_div(_ts_roll(x, d, "max"), _ts_roll(x, d, "min"), epsilon=1e-12)


def _ts_returns_spec(x, d, mode=1.0):
    if not _is_df(x):
        return x
    shifted = x.shift(int(d))
    res = _safe_div(x - shifted, shifted, epsilon=1e-12)
    if float(mode) == 0:
        res = res * 100
    return res


def _ts_av_diff(x, d):
    return x - _ts_roll(x, d, "mean")


def _ts_delta_spec(x, d):
    return x - x.shift(int(d)) if _is_df(x) else x


register("ts_arg_max", "time-series", [X, W], "days since the window max (0 = today)", 2, 2)(
    lambda x, d: _ts_arg_lag(x, d, "max")
)
register("ts_arg_min", "time-series", [X, W], "days since the window min (0 = today)", 2, 2)(
    lambda x, d: _ts_arg_lag(x, d, "min")
)
register("ts_av_diff", "time-series", [X, W], "x - ts_mean(x, d)", 2, 2)(_ts_av_diff)
register(
    "ts_bollinger_percent",
    "time-series",
    [X, W, Arg("k", "scalar", 2.0)],
    "(x - lower) / (upper - lower), bands = mean +/- k*std",
    2,
    3,
)(_ts_bollinger_percent)
register(
    "ts_bollinger_position",
    "time-series",
    [X, W, Arg("k", "scalar", 2.0)],
    "bollinger percent clipped to [0, 1]",
    2,
    3,
)(_ts_bollinger_position)
register(
    "ts_bollinger_width",
    "time-series",
    [X, W, Arg("k", "scalar", 2.0)],
    "2*k*std / |mean| (band width relative to the mean)",
    2,
    3,
)(_ts_bollinger_width)
register("ts_count_nans", "time-series", [X, W], "number of NaNs inside the window", 2, 2)(
    _ts_count_nans
)
register("ts_delta", "time-series", [X, Arg("d", "lag")], "x - x(t-d) (lag, d >= 1)", 2, 2)(_ts_delta_spec)
register("ts_ema", "time-series", [X, W], "exponential moving average, span = d", 2, 2)(_ts_ema)
register("ts_entropy", "time-series", [X, W], "entropy of |x| shares inside the window", 2, 2)(
    _ts_entropy
)
register(
    "ts_extreme_ratio",
    "time-series",
    [X, W],
    "ts_max(x, d) / ts_min(x, d)",
    2,
    2,
)(_ts_extreme_ratio)
register(
    "ts_gain_loss_ratio",
    "time-series",
    [X, W],
    "sum of positive changes / sum of |negative changes| inside the window",
    2,
    2,
)(_ts_gain_loss_ratio)
register("ts_hhi", "time-series", [X, W], "Herfindahl index of |x| shares", 2, 2)(_ts_hhi)
register("ts_mad", "time-series", [X, W], "mean absolute deviation from the window mean", 2, 2)(
    _ts_mad
)
register("ts_max_diff", "time-series", [X, W], "x - ts_max(x, d)", 2, 2)(_ts_max_diff)
register(
    "ts_max_drawdown",
    "time-series",
    [X, W],
    "worst drawdown inside the window",
    2,
    2,
)(_ts_max_drawdown)
register("ts_min_diff", "time-series", [X, W], "x - ts_min(x, d)", 2, 2)(_ts_min_diff)
register(
    "ts_min_max_diff",
    "time-series",
    [X, W, Arg("f", "scalar", 0.5)],
    "x - f * (ts_min + ts_max)",
    2,
    3,
)(_ts_min_max_diff)
register(
    "ts_percentage",
    "time-series",
    [X, W, Arg("percentage", "scalar", 0.5)],
    "rolling quantile of x at `percentage`",
    2,
    3,
)(_ts_percentage)
register(
    "ts_positive_ratio",
    "time-series",
    [X, W],
    "fraction of positive values inside the window",
    2,
    2,
)(_ts_positive_ratio)
register("ts_product", "time-series", [X, W], "rolling product", 2, 2)(_ts_product)
register(
    "ts_quantile",
    "time-series",
    [X, W, Arg("driver", "value", "gaussian")],
    "rank mapped through the gaussian (or uniform) quantile function",
    2,
    3,
)(_ts_quantile)
register("ts_range", "time-series", [X, W], "ts_max(x, d) - ts_min(x, d)", 2, 2)(_ts_range)
register(
    "ts_rank",
    "time-series",
    [X, W, Arg("constant", "scalar", 0.0)],
    "rank of today's value in the window; constant=1 -> percentile",
    2,
    3,
)(_ts_rank_spec)
register(
    "ts_returns",
    "time-series",
    [X, W, Arg("mode", "scalar", 1.0)],
    "(x - x(t-d)) / x(t-d); mode=0 -> percent",
    2,
    3,
)(_ts_returns_spec)
register(
    "ts_scale",
    "time-series",
    [X, W, Arg("constant", "scalar", 0.0)],
    "min-max scale of x inside the window, plus `constant`",
    2,
    3,
)(_ts_scale)
register("ts_std_dev", "time-series", [X, W], "rolling standard deviation (ddof=0)", 2, 2)(
    _ts_std_dev
)


#: operators that are *not* allowed to appear inside another window arg, used
#: by the validator to reject nonsense like ts_mean(x, ts_mean(y, 5))
INFIX = ("+", "-", "*", "/", "^", ">", "<", ">=", "<=", "==", "!=", "&", "|", "!")


def get(name: str) -> Operator:
    try:
        return REGISTRY[name]
    except KeyError as exc:  # pragma: no cover - message path
        raise OpError(f"unknown operator {name!r}") from exc


def check_windows(windows: Iterable[int], allowed: Iterable[int] = ALLOWED_WINDOWS) -> list[str]:
    bad = [int(w) for w in windows if int(w) not in set(allowed)]
    if bad:
        return [
            f"window {w} is not economically meaningful; allowed: {sorted(allowed)}"
            for w in bad
        ]
    return []


def catalog_text(only: Optional[Iterable[str]] = None) -> str:
    """Compact operator cheat-sheet handed to the implementer agent (2.2)."""
    allowed = set(only) if only is not None else None
    lines = []
    for cat in ("element-wise", "cross-sectional", "time-series", "conditional"):
        ops = [
            op
            for op in REGISTRY.values()
            if op.category == cat and (allowed is None or op.name in allowed)
        ]
        if not ops:
            continue
        lines.append(f"[{cat}]")
        for op in ops:
            sig = ", ".join(a.name for a in op.args)
            lines.append(f"  {op.name}({sig})  -- {op.doc}")
    lines.append("[infix]")
    lines.append("  + - * / ^  > < >= <= == !=  & | !   (element-wise; & = and, | = or)")
    lines.append("  constants: nan, inf, true, false; use if_else for conditionals")
    return "\n".join(lines)

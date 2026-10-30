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
    mean = _ts_apply(x, d, "mean")
    std = _ts_apply(x, d, "std").replace(0.0, np.nan)
    return mean / std


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
    lambda x, d: _ts_apply(x, d, "sum")
)
register("ts_mean", "time-series", [X, W], "rolling mean", 2, 2)(
    lambda x, d: _ts_apply(x, d, "mean")
)
register("ts_std", "time-series", [X, W], "rolling standard deviation", 2, 2)(
    lambda x, d: _ts_apply(x, d, "std")
)
register("ts_min", "time-series", [X, W], "rolling minimum", 2, 2)(
    lambda x, d: _ts_apply(x, d, "min")
)
register("ts_max", "time-series", [X, W], "rolling maximum", 2, 2)(
    lambda x, d: _ts_apply(x, d, "max")
)
register("ts_median", "time-series", [X, W], "rolling median", 2, 2)(
    lambda x, d: _ts_apply(x, d, "median")
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
register("ts_zscore", "time-series", [X, W], "(x - ts_mean) / ts_std", 2, 2)(
    lambda x, d: (x - _ts_apply(x, d, "mean"))
    / _ts_apply(x, d, "std").replace(0.0, np.nan)
)
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


def catalog_text() -> str:
    """Compact operator cheat-sheet handed to the implementer agent (2.2)."""
    lines = []
    for cat in ("element-wise", "cross-sectional", "time-series", "conditional"):
        lines.append(f"[{cat}]")
        for op in REGISTRY.values():
            if op.category != cat:
                continue
            sig = ", ".join(a.name for a in op.args)
            lines.append(f"  {op.name}({sig})  -- {op.doc}")
    lines.append("[infix]")
    lines.append("  + - * / ^  > < >= <= == !=  & | !   (element-wise; & = and, | = or)")
    lines.append("  constants: nan, inf, true, false; use if_else for conditionals")
    return "\n".join(lines)

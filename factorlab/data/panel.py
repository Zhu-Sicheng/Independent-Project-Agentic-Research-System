"""The data module: a panel store of date x ticker matrices.

`PanelStore` is deliberately dumb: it only holds aligned two dimensional
matrices and a few derived fields.  Everything downstream (expressions,
backtests, grid search) consumes it through :meth:`PanelStore.field`.
Adding a data source therefore only means producing one of these objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd


class PanelError(ValueError):
    """Raised for malformed or inconsistent panel data."""


#: common aliases so that agents/LLMs can use natural names
ALIASES: Dict[str, str] = {
    "ret": "returns",
    "return": "returns",
    "px": "close",
    "price": "close",
    "adj_close": "close",
    "mktcap": "cap",
    "market_cap": "cap",
    "dollar_volume": "amount",
    "turnover_value": "amount",
}


def _clean_matrix(df: pd.DataFrame) -> pd.DataFrame:
    out = df.astype("float64").replace([np.inf, -np.inf], np.nan)
    return out


@dataclass
class PanelStore:
    """A bundle of ``field -> (dates x tickers)`` float matrices."""

    fields: Dict[str, pd.DataFrame]
    name: str = "panel"
    meta: dict = dc_field(default_factory=dict)
    _cache: dict = dc_field(default_factory=dict, repr=False, compare=False)

    # ------------------------------------------------------------------ #
    # construction
    # ------------------------------------------------------------------ #
    def __post_init__(self) -> None:
        if not self.fields:
            raise PanelError("PanelStore needs at least one field")

        dates: Optional[pd.DatetimeIndex] = None
        tickers: Optional[pd.Index] = None
        clean: Dict[str, pd.DataFrame] = {}

        for key, mat in self.fields.items():
            if not isinstance(mat, pd.DataFrame):
                raise PanelError(f"field {key!r} is not a DataFrame")
            m = mat.copy()
            m.index = pd.to_datetime(m.index)
            m = m.sort_index()
            m.columns = pd.Index([str(c) for c in m.columns])
            if m.index.has_duplicates:
                m = m.groupby(level=0).last()
            m = _clean_matrix(m)
            clean[key] = m
            dates = m.index if dates is None else dates.union(m.index)
            tickers = m.columns if tickers is None else tickers.union(m.columns)

        assert dates is not None and tickers is not None
        dates = pd.DatetimeIndex(sorted(dates)).rename("date")
        tickers = pd.Index(sorted(tickers), name="ticker")

        for key, m in clean.items():
            if not m.index.equals(dates) or not m.columns.equals(tickers):
                m = m.reindex(index=dates, columns=tickers)
            clean[key] = m

        self.fields = clean
        self._cache = {}
        self.meta = dict(self.meta)
        self.meta.setdefault("n_dates", len(dates))
        self.meta.setdefault("n_tickers", len(tickers))
        self.meta.setdefault("start", str(dates[0].date()) if len(dates) else None)
        self.meta.setdefault("end", str(dates[-1].date()) if len(dates) else None)

    @classmethod
    def from_dict(cls, fields: Dict[str, pd.DataFrame], **kwargs) -> "PanelStore":
        return cls(fields=fields, **kwargs)

    # ------------------------------------------------------------------ #
    # basic accessors
    # ------------------------------------------------------------------ #
    @property
    def dates(self) -> pd.DatetimeIndex:
        return next(iter(self.fields.values())).index

    @property
    def tickers(self) -> pd.Index:
        return next(iter(self.fields.values())).columns

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.dates), len(self.tickers)

    @property
    def close(self) -> pd.DataFrame:
        return self.field("close")

    def __contains__(self, name: str) -> bool:
        try:
            self.field(name)
            return True
        except PanelError:
            return False

    def has(self, name: str) -> bool:
        return name in self

    def available(self) -> List[str]:
        return sorted(self.fields)

    def field(self, name: str) -> pd.DataFrame:
        """Return a field matrix, building derived fields on demand."""
        key = ALIASES.get(name, name)
        if key in self.fields:
            return self.fields[key]
        if key in self._cache:
            return self._cache[key]

        derived = self._derive(key)
        if derived is None:
            raise PanelError(
                f"unknown field {name!r}; available: {', '.join(self.available())}"
            )
        self._cache[key] = derived
        return derived

    def _derive(self, key: str) -> Optional[pd.DataFrame]:
        if key == "returns" and "close" in self.fields:
            return self.fields["close"].pct_change(fill_method=None)
        if key == "log_returns" and "close" in self.fields:
            return np.log(self.fields["close"]).diff()
        if key == "amount" and "close" in self.fields and "volume" in self.fields:
            return self.fields["close"] * self.fields["volume"]
        if key == "vwap" and "amount" in self.fields and "volume" in self.fields:
            vol = self.fields["volume"].replace(0.0, np.nan)
            return self.fields["amount"] / vol
        if key == "adv20" and "amount" in self.fields:
            return self.fields["amount"].rolling(20, min_periods=10).mean()
        if key == "cap" and "close" in self.fields and "shares" in self.fields:
            return self.fields["close"] * self.fields["shares"]
        if key == "cap_rank" and "cap" in self.fields:
            return self.fields["cap"].rank(axis=1, pct=True)
        return None

    # ------------------------------------------------------------------ #
    # utilities
    # ------------------------------------------------------------------ #
    def subset(self, start=None, end=None) -> "PanelStore":
        idx = self.dates
        if start is not None:
            idx = idx[idx >= pd.Timestamp(start)]
        if end is not None:
            idx = idx[idx <= pd.Timestamp(end)]
        return PanelStore(
            fields={k: v.loc[idx] for k, v in self.fields.items()},
            name=self.name,
            meta=dict(self.meta),
        )

    def head(self, n: int = 5) -> "PanelStore":
        return PanelStore(
            fields={k: v.iloc[:n] for k, v in self.fields.items()},
            name=self.name,
            meta=dict(self.meta),
        )

    def describe_field(self, name: str) -> dict:
        mat = self.field(name)
        vals = mat.to_numpy(dtype=float, copy=False)
        finite = vals[np.isfinite(vals)]
        if finite.size == 0:
            return {"field": name, "coverage": 0.0}
        # lag-1 autocorrelation of the pooled time series (rough, cheap)
        a = np.nan_to_num(vals[:-1], nan=0.0)
        b = np.nan_to_num(vals[1:], nan=0.0)
        if a.std() > 0 and b.std() > 0:
            ac1 = float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
        else:
            ac1 = float("nan")
        return {
            "field": name,
            "coverage": round(float(finite.size / max(vals.size, 1)), 4),
            "mean": float(np.mean(finite)),
            "std": float(np.std(finite)),
            "min": float(np.min(finite)),
            "p01": float(np.quantile(finite, 0.01)),
            "p50": float(np.quantile(finite, 0.5)),
            "p99": float(np.quantile(finite, 0.99)),
            "max": float(np.max(finite)),
            "skew": float(pd.Series(finite).skew()),
            "kurt": float(pd.Series(finite).kurt()),
            "autocorr_1": round(ac1, 4) if np.isfinite(ac1) else None,
        }

    def summary(self, fields: Optional[Iterable[str]] = None) -> dict:
        """Compact description used in LLM prompts and reports."""
        names = list(fields) if fields else self.available()
        rets = self.field("returns") if "close" in self.fields else None
        xs_disp = None
        if rets is not None:
            xs_disp = float(rets.std(axis=1).mean(skipna=True))
        out = {
            "name": self.name,
            "n_dates": int(self.shape[0]),
            "n_tickers": int(self.shape[1]),
            "start": str(self.dates[0].date()),
            "end": str(self.dates[-1].date()),
            "fields": {name: self.describe_field(name) for name in names},
        }
        if xs_disp is not None and np.isfinite(xs_disp):
            out["mean_cross_sectional_dispersion"] = round(xs_disp, 6)
        return out

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"PanelStore(name={self.name!r}, shape={self.shape}, "
            f"fields={self.available()})"
        )

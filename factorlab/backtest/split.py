"""In-sample / out-of-sample splitting.

The protocol implemented here is deliberately simple and honest:

1. every factor matrix is computed on the **full** panel (factor values are
   causal: a value at ``t`` only uses data up to ``t``), so the OOS segment
   never benefits from future information in factor construction;
2. the grid search **selects** its best configuration using the in-sample
   segment only;
3. the selected configuration is then evaluated, untouched, on the holdout
   segment and both sets of metrics are stored and reported.

Nothing is fabricated when no split is configured: selection falls back to the
full sample and the OOS metrics are simply absent.  Fill in
:class:`factorlab.config.SampleSplit` once the real data dates are known.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from ..config import SampleSplit
from . import metrics as M

MIN_SEGMENT_DAYS = 20
COMFORTABLE_SEGMENT_DAYS = 60
MIN_TRAIN_FRAC = 0.10
MAX_TRAIN_FRAC = 0.95


class SplitError(ValueError):
    """Raised when a configured split leaves no usable segment."""


@dataclass
class SplitMasks:
    masks: dict[str, pd.Series]
    meta: dict = field(default_factory=dict)

    @property
    def has_oos(self) -> bool:
        return bool(self.meta.get("has_oos", False))

    def is_mask(self) -> pd.Series:
        return self.masks["is"]

    def oos_mask(self) -> Optional[pd.Series]:
        return self.masks.get("oos") if self.has_oos else None

    def describe(self) -> str:
        return str(self.meta.get("description", ""))


def resolve_split(dates, split: Optional[SampleSplit]) -> SplitMasks:
    dates = pd.DatetimeIndex(sorted(pd.DatetimeIndex(dates)))
    if split is None or not split.is_configured():
        return SplitMasks(
            masks={
                "is": pd.Series(True, index=dates),
                "oos": pd.Series(False, index=dates),
            },
            meta={
                "mode": "none",
                "has_oos": False,
                "n_is": int(len(dates)),
                "n_oos": 0,
                "train_frac": None,
                "is_range": [str(dates[0].date()), str(dates[-1].date())],
                "oos_range": None,
                "description": (split or SampleSplit()).describe(),
                "warnings": [],
            },
        )

    warnings: list[str] = []
    if split.train_frac is not None:
        frac = float(split.train_frac)
        if not (MIN_TRAIN_FRAC <= frac <= MAX_TRAIN_FRAC):
            raise SplitError(
                f"train_frac must be between {MIN_TRAIN_FRAC} and {MAX_TRAIN_FRAC}, got {frac}"
            )
        cut = int(round(len(dates) * frac))
        is_dates, oos_dates = dates[:cut], dates[cut:]
        mode = "fraction"
    else:
        train_start = pd.Timestamp(split.train_start) if split.train_start else dates[0]
        train_end = pd.Timestamp(split.train_end) if split.train_end else None
        test_start = pd.Timestamp(split.test_start) if split.test_start else None
        test_end = pd.Timestamp(split.test_end) if split.test_end else dates[-1]

        if train_end is None:
            if test_start is None:
                raise SplitError(
                    "a date split needs at least one of train_end / test_start"
                )
            before = dates[dates < test_start]
            if before.empty:
                raise SplitError(f"no dates before test_start={test_start.date()}")
            train_end = before[-1]
        if test_start is None:
            after = dates[dates > train_end]
            if after.empty:
                raise SplitError(f"no dates after train_end={train_end.date()}")
            test_start = after[0]

        is_mask_full = (dates >= train_start) & (dates <= train_end)
        oos_mask_full = (dates >= test_start) & (dates <= test_end)
        if (is_mask_full & oos_mask_full).any():
            raise SplitError("in-sample and out-of-sample ranges overlap")
        is_dates, oos_dates = dates[is_mask_full], dates[oos_mask_full]
        mode = "date"

    if len(is_dates) < MIN_SEGMENT_DAYS:
        raise SplitError(
            f"in-sample segment has only {len(is_dates)} days; need >= {MIN_SEGMENT_DAYS}"
        )
    if len(oos_dates) < MIN_SEGMENT_DAYS:
        raise SplitError(
            f"out-of-sample segment has only {len(oos_dates)} days; need >= {MIN_SEGMENT_DAYS}"
        )
    for label, seg in (("in-sample", is_dates), ("out-of-sample", oos_dates)):
        if len(seg) < COMFORTABLE_SEGMENT_DAYS:
            warnings.append(
                f"{label} segment has only {len(seg)} days; metrics will be noisy"
            )

    is_mask = dates.isin(is_dates)
    oos_mask = dates.isin(oos_dates)
    meta = {
        "mode": mode,
        "has_oos": True,
        "n_is": int(len(is_dates)),
        "n_oos": int(len(oos_dates)),
        "train_frac": (
            float(split.train_frac) if split.train_frac is not None else round(len(is_dates) / len(dates), 4)
        ),
        "is_range": [str(is_dates[0].date()), str(is_dates[-1].date())],
        "oos_range": [str(oos_dates[0].date()), str(oos_dates[-1].date())],
        "description": split.describe(),
        "warnings": warnings,
    }
    return SplitMasks(
        masks={
            "is": pd.Series(is_mask, index=dates),
            "oos": pd.Series(oos_mask, index=dates),
        },
        meta=meta,
    )


# --------------------------------------------------------------------------- #
# metrics per segment
# --------------------------------------------------------------------------- #
def segment_metrics(
    pnl: pd.Series,
    turnover: pd.Series,
    ic: Optional[pd.Series],
    factor: Optional[pd.DataFrame],
    masks: "SplitMasks",
    ann: int = 252,
) -> dict[str, dict]:
    """Summarise the same pnl series on the full / IS / OOS segments."""
    out: dict[str, dict] = {}
    for name, mask in masks.masks.items():
        if name == "oos" and not masks.has_oos:
            continue
        if not bool(mask.any()):
            continue
        sub_pnl = pnl.loc[mask]
        sub_to = turnover.loc[mask]
        sub_ic = ic.loc[mask] if ic is not None else None
        m = M.summarise_pnl(sub_pnl, sub_to, sub_ic, ann=ann)
        if factor is not None:
            counts = factor.loc[mask].notna().sum(axis=1)
            m["n_names"] = float(counts.reindex(sub_pnl.dropna().index).mean())
        out[name] = m
    if "is" in out and "full" not in out:
        out.setdefault("full", out["is"])
    return out


#: keys shown in tables / reports for each segment
SEGMENT_KEYS = ("sharpe", "ann_return", "turnover", "max_drawdown", "ic")


def segment_row(metrics: Optional[dict], prefix: str = "") -> dict:
    if not metrics:
        return {}
    return {
        f"{prefix}{key}": metrics.get(key)
        for key in SEGMENT_KEYS
        if key in metrics
    }

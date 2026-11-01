"""In-sample / out-of-sample / holdout splitting.

The protocol implemented here is deliberately simple and honest:

1. every factor matrix is computed on the **full** panel (factor values are
   causal: a value at ``t`` only uses data up to ``t``), so the OOS and holdout
   segments never benefit from future information in factor construction;
2. the grid search **selects** its best configuration using the in-sample
   segment only;
3. the selected configuration is then evaluated, untouched, on the validation
   (OOS) and final holdout segments, and all sets of metrics are stored.

With three segments the usual reading is: ``is`` = 2000-2020 (selection),
``oos`` = 2021-2024 (validation), ``holdout`` = 2025+ (ship / no-touch).

Nothing is fabricated when no split is configured: selection falls back to the
full sample and the extra segments are simply absent.
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
    #: always contains "is"; adds "oos" / "holdout" when those segments exist
    masks: dict[str, pd.Series]
    meta: dict = field(default_factory=dict)

    @property
    def has_oos(self) -> bool:
        return bool(self.meta.get("has_oos", False))

    @property
    def has_holdout(self) -> bool:
        return bool(self.meta.get("has_holdout", False))

    def is_mask(self) -> pd.Series:
        return self.masks["is"]

    def oos_mask(self) -> Optional[pd.Series]:
        return self.masks.get("oos") if self.has_oos else None

    def holdout_mask(self) -> Optional[pd.Series]:
        return self.masks.get("holdout") if self.has_holdout else None

    def describe(self) -> str:
        return str(self.meta.get("description", ""))


def _as_ts(value: Optional[str]) -> Optional[pd.Timestamp]:
    return pd.Timestamp(value) if value else None


def resolve_split(dates, split: Optional[SampleSplit]) -> SplitMasks:
    dates = pd.DatetimeIndex(sorted(pd.to_datetime(dates)))
    if split is None or not split.is_configured():
        return SplitMasks(
            masks={
                "is": pd.Series(True, index=dates),
            },
            meta={
                "mode": "none",
                "has_oos": False,
                "has_holdout": False,
                "n_is": int(len(dates)),
                "n_oos": 0,
                "n_holdout": 0,
                "train_frac": None,
                "is_range": [str(dates[0].date()), str(dates[-1].date())],
                "oos_range": None,
                "holdout_range": None,
                "description": (split or SampleSplit()).describe(),
                "warnings": [],
            },
        )

    warnings: list[str] = []

    # ---- 1) in-sample / validation ------------------------------------
    if split.train_frac is not None:
        frac = float(split.train_frac)
        if not (MIN_TRAIN_FRAC <= frac <= MAX_TRAIN_FRAC):
            raise SplitError(
                f"train_frac must be between {MIN_TRAIN_FRAC} and {MAX_TRAIN_FRAC}, "
                f"got {frac}"
            )
        cut = int(round(len(dates) * frac))
        is_dates, oos_dates = dates[:cut], dates[cut:]
        mode = "fraction"
    else:
        train_start = _as_ts(split.train_start) or dates[0]
        train_end = _as_ts(split.train_end)
        test_start = _as_ts(split.test_start)
        test_end = _as_ts(split.test_end) or dates[-1]

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
            raise SplitError("in-sample and validation ranges overlap")
        is_dates, oos_dates = dates[is_mask_full], dates[oos_mask_full]
        mode = "date"

    # ---- 2) carve the holdout out of the tail --------------------------
    holdout_dates = pd.DatetimeIndex([])
    if split.holdout_start or split.holdout_end:
        if split.holdout_start:
            holdout_start = _as_ts(split.holdout_start)
        elif len(oos_dates):
            after = dates[dates > oos_dates[-1]]
            if after.empty:
                raise SplitError("no dates after the validation segment for a holdout")
            holdout_start = after[0]
        else:
            raise SplitError("holdout requested but the validation segment is empty")
        holdout_end = _as_ts(split.holdout_end) or dates[-1]

        if split.test_end and holdout_start <= _as_ts(split.test_end):
            raise SplitError(
                "holdout_start must be after test_end (validation / holdout overlap)"
            )
        if len(is_dates) and holdout_start <= is_dates[-1]:
            raise SplitError("holdout_start falls inside the in-sample segment")

        holdout_mask_full = (dates >= holdout_start) & (dates <= holdout_end)
        holdout_dates = dates[holdout_mask_full]
        oos_dates = oos_dates[oos_dates < holdout_start]

    # ---- 3) validate ----------------------------------------------------
    if len(is_dates) < MIN_SEGMENT_DAYS:
        raise SplitError(
            f"in-sample segment has only {len(is_dates)} days; need >= {MIN_SEGMENT_DAYS}"
        )
    if len(oos_dates) < MIN_SEGMENT_DAYS:
        raise SplitError(
            f"validation segment has only {len(oos_dates)} days; need >= {MIN_SEGMENT_DAYS}"
        )
    if (split.holdout_start or split.holdout_end) and len(holdout_dates) < MIN_SEGMENT_DAYS:
        raise SplitError(
            f"holdout segment has only {len(holdout_dates)} days; need >= "
            f"{MIN_SEGMENT_DAYS}"
        )
    for label, seg in (
        ("in-sample", is_dates),
        ("validation", oos_dates),
        ("holdout", holdout_dates),
    ):
        if len(seg) and len(seg) < COMFORTABLE_SEGMENT_DAYS:
            warnings.append(
                f"{label} segment has only {len(seg)} days; metrics will be noisy"
            )

    masks = {
        "is": pd.Series(dates.isin(is_dates), index=dates),
        "oos": pd.Series(dates.isin(oos_dates), index=dates),
    }
    if len(holdout_dates):
        masks["holdout"] = pd.Series(dates.isin(holdout_dates), index=dates)

    meta = {
        "mode": mode,
        "has_oos": bool(len(oos_dates)),
        "has_holdout": bool(len(holdout_dates)),
        "n_is": int(len(is_dates)),
        "n_oos": int(len(oos_dates)),
        "n_holdout": int(len(holdout_dates)),
        "train_frac": (
            float(split.train_frac)
            if split.train_frac is not None
            else round(len(is_dates) / len(dates), 4)
        ),
        "is_range": [str(is_dates[0].date()), str(is_dates[-1].date())],
        "oos_range": [str(oos_dates[0].date()), str(oos_dates[-1].date())],
        "holdout_range": (
            [str(holdout_dates[0].date()), str(holdout_dates[-1].date())]
            if len(holdout_dates)
            else None
        ),
        "description": split.describe(),
        "warnings": warnings,
    }
    return SplitMasks(masks=masks, meta=meta)


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
    mode: str = "additive",
) -> dict[str, dict]:
    """Summarise the same pnl series on the full / IS / OOS / holdout segments."""
    out: dict[str, dict] = {}
    for name, mask in masks.masks.items():
        if not bool(mask.any()):
            continue
        sub_pnl = pnl.loc[mask]
        sub_to = turnover.loc[mask]
        sub_ic = ic.loc[mask] if ic is not None else None
        m = M.summarise_pnl(sub_pnl, sub_to, sub_ic, ann=ann, mode=mode)
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

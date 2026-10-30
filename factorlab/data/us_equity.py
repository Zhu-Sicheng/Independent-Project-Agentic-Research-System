"""Loader for the CRSP-style US equity extract shipped with this project.

Raw layout::

    data/raw/data/
        OHLCVolumeMktCap/s<permno>.csv      # Adj_Open/High/Low/Close/Volume/MktCap
        MASTER_UNIVERSE_sp500_membership_extended_asOf20260930_v2.csv
        permno_to_ticker_mapping.csv
        security_master_with_provisional_classifications.csv
        sp500_stocks_universe_20000101_20260930.csv

Everything is point-in-time: a stock only appears on a date when it was an
S&P 500 member on that date (``start_date``/``end_date`` intervals), so delisted
names disappear instead of silently dropping out of the sample.

Output is one parquet matrix per field, ``date x permno``, plus a metadata
folder (ticker map, membership intervals, build manifest).
"""

from __future__ import annotations

import glob
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

from ..config import SampleSplit
from .panel import PanelStore

RAW_SUBDIR = "data"
OHLC_SUBDIR = "OHLCVolumeMktCap"
UNIVERSE_FILE = "MASTER_UNIVERSE_sp500_membership_extended_asOf20260930_v2.csv"
TICKER_FILE = "permno_to_ticker_mapping.csv"
SECURITY_FILE = "security_master_with_provisional_classifications.csv"

#: raw column -> panel field
COLUMN_MAP = {
    "Adj_Open": "open",
    "Adj_High": "high",
    "Adj_Low": "low",
    "Adj_Close": "close",
    "Adj_Volume": "volume",
    "Adj_MktCap": "cap",
}
PRICE_FIELDS = ("open", "high", "low", "close")
PERMNO_RE = re.compile(r"s(\d+)")

#: the research convention for this panel: select on 2000-2020, validate on
#: 2021-2024, keep 2025+ as the final untouched holdout
DEFAULT_SPLIT = {
    "train_end": "2020-12-31",
    "test_start": "2021-01-01",
    "test_end": "2024-12-31",
    "holdout_start": "2025-01-01",
}


@dataclass
class BuildResult:
    panel: PanelStore
    stats: dict
    out_dir: Path


def _resolve_dirs(raw_dir: str | Path) -> tuple[Path, Path]:
    raw = Path(raw_dir)
    if (raw / OHLC_SUBDIR).is_dir():
        return raw, raw / OHLC_SUBDIR
    if (raw / RAW_SUBDIR / OHLC_SUBDIR).is_dir():
        return raw / RAW_SUBDIR, raw / RAW_SUBDIR / OHLC_SUBDIR
    raise FileNotFoundError(
        f"cannot find {OHLC_SUBDIR}/ under {raw}; pass the folder that contains it"
    )


def _read_prices(ohlc_dir: Path, verbose: bool = True) -> pd.DataFrame:
    files = sorted(ohlc_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"no csv files in {ohlc_dir}")
    frames = []
    for i, path in enumerate(files, 1):
        df = pd.read_csv(
            path,
            usecols=["DATE", *COLUMN_MAP],
            dtype={"DATE": "int64"},
        )
        df["permno"] = path.stem
        frames.append(df)
        if verbose and i % 200 == 0:
            print(f"  read {i}/{len(files)} files", flush=True)
    long = pd.concat(frames, ignore_index=True)
    long["date"] = pd.to_datetime(long["DATE"], format="%Y%m%d")
    long = long.rename(columns=COLUMN_MAP)
    long = long.drop(columns=["DATE"])
    long = long.sort_values(["date", "permno"]).drop_duplicates(
        subset=["date", "permno"], keep="last"
    )
    return long.reset_index(drop=True)


def _load_intervals(raw: Path) -> pd.DataFrame:
    path = raw / UNIVERSE_FILE
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["permno"] = "s" + df["permno"].astype(int).astype(str)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])
    return df


def _membership_mask(
    dates: pd.DatetimeIndex, permnos: pd.Index, intervals: pd.DataFrame
) -> pd.DataFrame:
    mask = pd.DataFrame(False, index=dates, columns=permnos)
    first, last = dates[0], dates[-1]
    for row in intervals.itertuples(index=False):
        if row.permno not in mask.columns:
            continue
        start = max(row.start_date, first)
        end = min(row.end_date, last)
        if start > end:
            continue
        mask.loc[start:end, row.permno] = True
    return mask


def _to_wide(
    long: pd.DataFrame, field: str, dates: pd.DatetimeIndex, permnos: pd.Index
) -> pd.DataFrame:
    wide = long.pivot(index="date", columns="permno", values=field)
    return wide.reindex(index=dates, columns=permnos)


def _clean_field(field: str, mat: pd.DataFrame) -> pd.DataFrame:
    if field in PRICE_FIELDS:
        mat = mat.where(mat > 0)
    elif field == "volume":
        mat = mat.where(mat > 0)
    elif field == "cap":
        mat = mat.where(mat > 0)
    return mat.replace([np.inf, -np.inf], np.nan)


def build_panel(
    raw_dir: str | Path = "data/raw",
    start: str = "2000-01-01",
    end: str = "2026-09-30",
    verbose: bool = True,
) -> PanelStore:
    raw, ohlc_dir = _resolve_dirs(raw_dir)
    if verbose:
        print(f"reading {ohlc_dir} ...", flush=True)
    long = _read_prices(ohlc_dir, verbose=verbose)
    long = long[(long["date"] >= pd.Timestamp(start)) & (long["date"] <= pd.Timestamp(end))]
    if long.empty:
        raise ValueError(f"no rows between {start} and {end}")

    intervals = _load_intervals(raw)
    permnos = pd.Index(sorted(long["permno"].unique()), name="ticker")
    dates = pd.DatetimeIndex(sorted(long["date"].unique()), name="date")
    if verbose:
        print(
            f"long rows {len(long):,}, {len(permnos)} permnos, {len(dates)} dates",
            flush=True,
        )

    mask = _membership_mask(dates, permnos, intervals)
    if verbose:
        per_date = mask.sum(axis=1)
        print(
            f"members per date: mean {per_date.mean():.0f}, min {per_date.min()}, "
            f"max {per_date.max()}",
            flush=True,
        )

    fields: dict[str, pd.DataFrame] = {}
    for raw_col, field in COLUMN_MAP.items():
        wide = _to_wide(long, field, dates, permnos)
        wide = _clean_field(field, wide)
        fields[field] = wide.where(mask)



    panel = PanelStore.from_dict(fields, name="us_sp500")
    panel.meta.update(
        {
            "source": str(raw),
            "universe": "sp500_point_in_time",
            "price_basis": "adjusted (split & dividend)",
            "start": str(dates[0].date()),
            "end": str(dates[-1].date()),
        }
    )
    return panel


def _coverage(mat: pd.DataFrame) -> dict:
    total = mat.shape[0] * mat.shape[1]
    valid = int(mat.notna().to_numpy().sum())
    return {
        "coverage": round(valid / total, 4) if total else 0.0,
        "n_valid": valid,
        "mean_names_per_date": round(float(mat.notna().sum(axis=1).mean()), 1),
    }


def build_stats(panel: PanelStore) -> dict:
    close = panel.field("close")
    rets = close.pct_change(fill_method=None)
    per_date = close.notna().sum(axis=1)
    return {
        "shape": list(panel.shape),
        "start": str(panel.dates[0].date()),
        "end": str(panel.dates[-1].date()),
        "fields": {name: _coverage(mat) for name, mat in panel.fields.items()},
        "names_per_date": {
            "mean": float(per_date.mean()),
            "min": int(per_date.min()),
            "max": int(per_date.max()),
        },
        "default_split": dict(DEFAULT_SPLIT),
        "returns": {
            "mean": float(np.nanmean(rets)),
            "std": float(np.nanstd(rets)),
            "p01": float(np.nanquantile(rets, 0.01)),
            "p99": float(np.nanquantile(rets, 0.99)),
            "max_abs": float(np.nanmax(np.abs(rets))),
            "n_over_50pct": int((np.abs(rets) > 0.5).sum().sum()),
        },
    }


def save_processed(panel: PanelStore, out_dir: str | Path, stats: dict) -> Path:
    out = Path(out_dir)
    panel_dir = out / "panel"
    meta_dir = out / "meta"
    panel_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    for name, mat in panel.fields.items():
        mat.astype("float32").to_parquet(
            panel_dir / f"{name}.parquet", compression="zstd"
        )
    pd.Series(panel.tickers, name="ticker").to_csv(meta_dir / "columns.csv", index=False)
    (meta_dir / "manifest.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return out


def save_metadata(raw_dir: str | Path, out_dir: str | Path) -> None:
    raw, _ = _resolve_dirs(raw_dir)
    out = Path(out_dir) / "meta"
    out.mkdir(parents=True, exist_ok=True)

    mapping = pd.read_csv(raw / TICKER_FILE)
    mapping = mapping.rename(columns={"PERMNO": "permno", "Ticker": "ticker"})
    mapping = mapping[["permno", "ticker"]].drop_duplicates("permno")

    sec = pd.read_csv(raw / SECURITY_FILE)
    sec["permno"] = "s" + sec["permno"].astype(int).astype(str)
    cols = [
        c
        for c in ("permno", "gvkey", "linkdt", "linkenddt", "gsector", "sector_name", "gind")
        if c in sec.columns
    ]
    sec = sec[cols].drop_duplicates("permno")

    master = mapping.merge(sec, on="permno", how="left")
    master.to_csv(out / "security_master.csv", index=False)

    intervals = pd.read_csv(raw / UNIVERSE_FILE)
    intervals["permno"] = "s" + intervals["permno"].astype(int).astype(str)
    intervals.to_csv(out / "universe_intervals.csv", index=False)


def load_processed(panel_dir: str | Path = "data/processed/panel") -> PanelStore:
    panel_dir = Path(panel_dir)
    files = sorted(panel_dir.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"no parquet files in {panel_dir}")
    fields = {f.stem: pd.read_parquet(f) for f in files}
    panel = PanelStore.from_dict(fields, name="us_sp500")

    manifest = panel_dir.parent / "meta" / "manifest.json"
    if manifest.exists():
        meta = json.loads(manifest.read_text(encoding="utf-8"))
        panel.meta["build"] = {
            k: meta.get(k) for k in ("shape", "start", "end", "names_per_date")
        }
        if meta.get("default_split"):
            panel.meta["default_split"] = SampleSplit(**meta["default_split"])
    return panel


def build_and_save(
    raw_dir: str | Path = "data/raw",
    out_dir: str | Path = "data/processed",
    start: str = "2000-01-01",
    end: str = "2026-09-30",
    verbose: bool = True,
) -> BuildResult:
    panel = build_panel(raw_dir, start=start, end=end, verbose=verbose)
    stats = build_stats(panel)
    out = Path(out_dir)
    save_processed(panel, out, stats)
    save_metadata(raw_dir, out)
    if verbose:
        print(json.dumps(stats, indent=2, ensure_ascii=False)[:1200])
    return BuildResult(panel=panel, stats=stats, out_dir=out)

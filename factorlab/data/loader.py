"""Reading raw price/volume files into a :class:`PanelStore`.

The loader is intentionally tolerant because the real dataset is not fixed yet.
It accepts

* a directory of yearly files (``*.parquet`` / ``*.csv`` / ``*.feather``),
* a single long-format file with ``date`` + ``ticker`` columns,
* a directory of wide "one file per field" files (date index x ticker columns),
* a python ``dict`` of wide matrices.

The only hard requirement is a date column (or a DatetimeIndex) and a ticker
column / column labels.  Add new sources by writing a function that returns
``dict[field, DataFrame]`` and calling :meth:`PanelStore.from_dict`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from .panel import PanelError, PanelStore

DATE_CANDIDATES = ("date", "datetime", "dt", "time", "trade_date", "tradedate", "day")
TICKER_CANDIDATES = (
    "ticker",
    "symbol",
    "code",
    "asset",
    "sid",
    "secid",
    "security_id",
    "instrument",
    "stock",
)
SUPPORTED_SUFFIXES = (".parquet", ".csv", ".feather", ".ftr")


def _read_any(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in (".feather", ".ftr"):
        return pd.read_feather(path)
    raise PanelError(f"unsupported file type: {path}")


def _list_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files = [p for p in sorted(path.iterdir()) if p.suffix.lower() in SUPPORTED_SUFFIXES]
    if not files:
        files = [
            p
            for p in sorted(path.rglob("*"))
            if p.suffix.lower() in SUPPORTED_SUFFIXES
        ]
    if not files:
        raise PanelError(f"no data files found under {path}")
    return files


def _detect(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    lowered = {str(c).strip().lower(): c for c in df.columns}
    for name in candidates:
        if name in lowered:
            return str(lowered[name])
    return None


def _to_long(
    frames: list[pd.DataFrame],
    date_col: Optional[str],
    ticker_col: Optional[str],
) -> tuple[pd.DataFrame, str, str]:
    df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0].copy()
    date_col = date_col or _detect(df, DATE_CANDIDATES)
    ticker_col = ticker_col or _detect(df, TICKER_CANDIDATES)
    if date_col is None or ticker_col is None:
        raise PanelError(
            "long-format input needs a date column and a ticker column; "
            f"got columns={list(df.columns)[:20]}"
        )
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col, ticker_col])
    df[ticker_col] = df[ticker_col].astype(str)
    df = df.sort_values([date_col, ticker_col])
    df = df.drop_duplicates(subset=[date_col, ticker_col], keep="last")
    return df.reset_index(drop=True), date_col, ticker_col


def _long_to_fields(
    df: pd.DataFrame, date_col: str, ticker_col: str, fields: Optional[Iterable[str]]
) -> dict[str, pd.DataFrame]:
    value_cols = [c for c in df.columns if c not in (date_col, ticker_col)]
    numeric = df[value_cols].select_dtypes("number").columns.tolist()
    value_cols = [c for c in numeric if fields is None or c in set(fields)]
    if not value_cols:
        raise PanelError("no numeric field columns found in the input")
    out: dict[str, pd.DataFrame] = {}
    for col in value_cols:
        wide = (
            df.pivot_table(
                index=date_col, columns=ticker_col, values=col, aggfunc="last"
            )
            .sort_index()
            .sort_index(axis=1)
        )
        out[str(col)] = wide
    return out


def load_panel(
    path: str | Path,
    fields: Optional[Iterable[str]] = None,
    date_col: Optional[str] = None,
    ticker_col: Optional[str] = None,
    name: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> PanelStore:
    """Load a panel from disk.  See module docstring for accepted layouts."""
    path = Path(path)
    files = _list_files(path)
    first = _read_any(files[0])

    looks_long = _detect(first, DATE_CANDIDATES) is not None and _detect(
        first, TICKER_CANDIDATES
    ) is not None

    if looks_long:
        frames = [_read_any(f) for f in files]
        df, dcol, tcol = _to_long(frames, date_col, ticker_col)
        field_mats = _long_to_fields(df, dcol, tcol, fields)
    else:
        if len(files) == 1:
            # single wide file whose columns are a MultiIndex (field, ticker)
            if isinstance(first.columns, pd.MultiIndex):
                field_mats = {}
                for lvl in first.columns.get_level_values(0).unique():
                    mat = first[lvl].copy()
                    field_mats[str(lvl)] = mat
                field_mats = {
                    k: v for k, v in field_mats.items() if fields is None or k in set(fields)
                }
            else:
                field_mats = {str(files[0].stem): first.copy()}
        else:
            field_mats = {}
            for f in files:
                mat = _read_any(f)
                if not isinstance(mat.index, pd.DatetimeIndex):
                    mat.index = pd.to_datetime(mat.index)
                field_mats[str(f.stem)] = mat
            if fields is not None:
                field_mats = {k: v for k, v in field_mats.items() if k in set(fields)}

    panel = PanelStore.from_dict(field_mats, name=name or path.stem)
    if start or end:
        panel = panel.subset(start, end)
    panel.meta["source"] = str(path)
    return panel


def save_panel(panel: PanelStore, out_dir: str | Path) -> Path:
    """Persist a panel in the long format understood by :func:`load_panel`."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    long_df = panel_to_long(panel)
    target = out_dir / "panel.parquet"
    long_df.to_parquet(target, index=False)
    (out_dir / "manifest.json").write_text(
        json.dumps(panel.summary(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return target


def panel_to_long(panel: PanelStore) -> pd.DataFrame:
    frames = []
    for field_name, mat in panel.fields.items():
        df = mat.rename_axis("date").reset_index()
        df = df.melt(id_vars="date", var_name="ticker", value_name=field_name)
        frames.append(df.set_index(["date", "ticker"]))
    long = pd.concat(frames, axis=1).reset_index()
    return long

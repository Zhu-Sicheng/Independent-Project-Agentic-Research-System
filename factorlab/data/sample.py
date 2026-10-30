"""Synthetic but economically structured sample data.

Real data is not available yet, so the demo needs a stand-in that (a) looks
like daily price/volume data and (b) actually contains *weak* exploitable
structure (short-term reversal, 20-day momentum, volatility, illiquidity and
volume-shock premia).

The generator is causal by construction: the expected return of day ``t`` is a
function of information observable at ``t-1`` only, so a correct backtest can
recover it and a look-ahead bug would show up as an absurdly high Sharpe.

Signal strengths are deliberately modest (daily IC around 0.01-0.02), which is
what keeps a 300-name, unit-gross book in the Sharpe 1-3 range instead of the
double digits.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from .panel import PanelStore

warnings.filterwarnings("ignore", category=RuntimeWarning)


def _zscore(x: np.ndarray) -> np.ndarray:
    mu = np.nanmean(x)
    sd = np.nanstd(x)
    if not np.isfinite(sd) or sd == 0:
        return np.zeros_like(x)
    z = (x - mu) / sd
    return np.nan_to_num(z, nan=0.0)


def _mean_20(x: np.ndarray, t: int) -> np.ndarray:
    lo = max(0, t - 20)
    return np.nanmean(x[lo:t], axis=0)


def generate_sample_panel(
    n_tickers: int = 300,
    start: str = "2018-01-01",
    end: str = "2024-12-31",
    seed: int = 7,
    beta_scale: float = 1.0,
    signal_scale: float = 1.0,
) -> PanelStore:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start=start, end=end)
    T, N = len(dates), n_tickers

    beta = np.clip(1.0 + 0.30 * rng.standard_normal(N) * beta_scale, 0.2, 2.5)
    sigma = np.clip(0.018 * np.exp(0.22 * rng.standard_normal(N)), 0.008, 0.040)
    base_volume = 4e6 * np.exp(0.8 * rng.standard_normal(N))
    shares = 6e7 * np.exp(0.9 * rng.standard_normal(N))
    close0 = 15.0 * np.exp(0.7 * rng.standard_normal(N))

    close = np.full((T, N), np.nan)
    logret = np.zeros((T, N))
    open_ = np.full((T, N), np.nan)
    high = np.full((T, N), np.nan)
    low = np.full((T, N), np.nan)
    volume = np.full((T, N), np.nan)
    amount = np.full((T, N), np.nan)

    close[0] = close0
    open_[0] = close0
    high[0] = close0
    low[0] = close0
    volume[0] = base_volume
    amount[0] = close0 * base_volume

    # a few late listings / early delistings so the panel has holes
    first_valid = np.zeros(N, dtype=int)
    last_valid = np.full(N, T - 1, dtype=int)
    late = rng.random(N) < 0.05
    first_valid[late] = rng.integers(int(0.15 * T), int(0.55 * T), size=int(late.sum()))
    early = rng.random(N) < 0.05
    last_valid[early] = rng.integers(int(0.55 * T), T - 20, size=int(early.sum()))
    last_valid = np.maximum(last_valid, first_valid + 80)

    # per-name premium loadings, so factors are not exactly separable
    load = {
        "rev1": 2.0e-4 * (1.0 + 0.3 * rng.standard_normal(N)),
        "rev5": 6.0e-5 * (1.0 + 0.3 * rng.standard_normal(N)),
        "mom": 8.0e-5 * (1.0 + 0.3 * rng.standard_normal(N)),
        "vol": -1.6e-4 * (1.0 + 0.3 * rng.standard_normal(N)),
        "illiq": -2.0e-4 * (1.0 + 0.3 * rng.standard_normal(N)),
        "vsh": -9.0e-5 * (1.0 + 0.3 * rng.standard_normal(N)),
    }

    prev_ret = np.zeros(N)
    for t in range(1, T):
        # ---- characteristics observable at t-1 -------------------------
        if t >= 2:
            rev1 = -logret[t - 1]
        else:
            rev1 = np.zeros(N)
        if t >= 6:
            with np.errstate(invalid="ignore"):
                rev5 = -(close[t - 1] / close[t - 6] - 1.0)
        else:
            rev5 = np.zeros(N)
        if t >= 21:
            with np.errstate(invalid="ignore"):
                mom = np.log(close[t - 1] / close[t - 21])
        else:
            mom = np.zeros(N)
        if t >= 20:
            vol20 = np.nanstd(logret[t - 20 : t], axis=0)
            with np.errstate(invalid="ignore", divide="ignore"):
                amt = amount[t - 20 : t]
                illiq = (
                    np.nanmean(
                        np.abs(logret[t - 20 : t]) / np.maximum(amt, 1.0), axis=0
                    )
                    * 1e9
                )
            vsh = np.log(volume[t - 1] / np.maximum(_mean_20(volume, t), 1.0))
        else:
            vol20 = sigma * 0.5
            illiq = np.full(N, 1.0)
            vsh = np.zeros(N)

        signal = (
            load["rev1"] * _zscore(rev1)
            + load["rev5"] * _zscore(rev5)
            + load["mom"] * _zscore(mom)
            + load["vol"] * _zscore(vol20)
            + load["illiq"] * _zscore(illiq)
            + load["vsh"] * _zscore(vsh)
        ) * signal_scale

        mkt = rng.standard_normal() * 0.009 * (1.0 + 0.5 * np.sin(t / 160.0))
        eps = rng.standard_t(df=5, size=N) / np.sqrt(5.0 / 3.0)
        r = beta * mkt + sigma * eps + signal

        alive = (t >= first_valid) & (t <= last_valid)
        prev_close = np.where(np.isnan(close[t - 1]), close0, close[t - 1])
        gap = 0.30 * sigma * rng.standard_normal(N)
        open_[t] = prev_close * np.exp(gap)
        close[t] = prev_close * (1.0 + r)
        logret[t] = np.log1p(r)

        spread = np.abs(rng.standard_normal(N)) * sigma * 0.6
        hi = np.maximum(open_[t], close[t]) * np.exp(spread)
        lo = np.minimum(open_[t], close[t]) * np.exp(-spread)
        high[t] = np.where(alive, hi, np.nan)
        low[t] = np.where(alive, lo, np.nan)
        open_[t] = np.where(alive, open_[t], np.nan)
        close[t] = np.where(alive, close[t], np.nan)

        vol = (
            base_volume
            * np.exp(0.45 * rng.standard_normal(N))
            * (1.0 + 4.0 * np.abs(r))
        )
        volume[t] = np.where(alive, vol, np.nan)
        amount[t] = np.where(alive, vol * close[t], np.nan)

    # random suspensions: occasional missing volume on otherwise listed names
    holes = rng.random((T, N)) < 0.001
    volume = np.where(holes, np.nan, volume)
    amount = np.where(holes, np.nan, amount)

    cap = close * shares

    def mat(a: np.ndarray) -> pd.DataFrame:
        df = pd.DataFrame(a, index=dates, columns=[f"T{i:04d}" for i in range(N)])
        df.index.name = "date"
        df.columns.name = "ticker"
        return df

    return PanelStore.from_dict(
        {
            "open": mat(open_),
            "high": mat(high),
            "low": mat(low),
            "close": mat(close),
            "volume": mat(volume),
            "amount": mat(amount),
            "shares": mat(np.tile(shares, (T, 1))),
            "cap": mat(cap),
        },
        name="sample",
        meta={"source": "synthetic", "seed": seed},
    )


def generate_sample_directory(
    out_dir: str | Path = "data/sample",
    n_tickers: int = 300,
    start: str = "2018-01-01",
    end: str = "2024-12-31",
    seed: int = 7,
    signal_scale: float = 1.0,
) -> Path:
    """Write one parquet file per year in long format, as a real feed would."""
    panel = generate_sample_panel(
        n_tickers=n_tickers, start=start, end=end, seed=seed, signal_scale=signal_scale
    )
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    for field_name, mat in panel.fields.items():
        df = mat.rename_axis("date").reset_index()
        df = df.melt(id_vars="date", var_name="ticker", value_name=field_name)
        frames.append(df.set_index(["date", "ticker"]))
    long = pd.concat(frames, axis=1).reset_index()
    long = long.dropna(subset=["close"])

    for year, chunk in long.groupby(long["date"].dt.year):
        chunk.to_parquet(out_dir / f"{year}.parquet", index=False)
    (out_dir / "manifest.json").write_text(
        json.dumps(
            {
                "n_rows": int(len(long)),
                "n_dates": int(panel.shape[0]),
                "n_tickers": int(panel.shape[1]),
                "start": str(panel.dates[0].date()),
                "end": str(panel.dates[-1].date()),
                "fields": panel.available(),
                "note": "synthetic sample data; replace with the real feed",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return out_dir

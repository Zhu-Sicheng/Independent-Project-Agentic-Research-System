# Processed US equity panel

Built from `data/raw/` by:

```powershell
python -m factorlab build-data --raw data/raw --out data/processed
```

| file | content |
|---|---|
| `panel/{open,high,low,close,volume,cap}.parquet` | `date x permno` matrices, float32 + zstd |
| `meta/security_master.csv` | permno, ticker, gvkey, GICS sector / industry |
| `meta/universe_intervals.csv` | S&P 500 membership intervals (`permno, start_date, end_date`) |
| `meta/columns.csv` | column order of the panel files |
| `meta/manifest.json` | shape, coverage, return distribution, default split |

Scale: 6726 trading days (2000-01-03 → 2026-09-30) × 1195 permnos, ~502 members per day.
`permno` is used as the column key because tickers are reused over time (43 duplicates in
this sample); join `meta/security_master.csv` to get the trading symbol.

Values are the data vendor's split- and dividend-adjusted prices (`Adj_*`). No forward
filling: outside a stock's membership window (or on a suspension) the cell is NaN.

Default research split (also stored in `manifest.json::default_split`):

| segment | range | role |
|---|---|---|
| in-sample | 2000-01-03 → 2020-12-31 | grid search selects here only |
| out-of-sample | 2021-01-04 → 2024-12-31 | validation |
| holdout | 2025-01-02 → 2026-09-30 | final untouched sample |

Load it with:

```python
from factorlab.data import load_processed
panel = load_processed("data/processed/panel")
```

# Field card: `ShrOut`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **no (raw data-contract field, historical records only)**

## EDA evidence

_no Agent-1 EDA evidence for this field (derived or not in raw data)_

## Backtest evidence (13)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| 20261031-systemv1_50 | 0 | Index turnover intensity relative to its own size as attention-driven reversal | -1 * safe_div(ts_mean(safe_div(volume, ShrOut), 20), ts_mean(safe_div(volume, ShrOut), 120)) * ts_ir(ts_returns(close, 1), 20) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 0 | Volume absorbed without intraday price movement as an absorbed-flow / fading-pressure state | -ts_mean(safe_div(abs(safe_div(close - open, open)), safe_div(volume, ShrOut)), 20) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 0 | Capitalization growth net of share-count growth as per-share value creation | safe_div(cap, ts_delta(close * ShrOut, 60)) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 1 | Volume absorbed without intraday price movement as an absorbed-flow / fading-pressure state | safe_div(ts_mean(safe_div(safe_div(volume, ShrOut), ts_mean(safe_div(volume, ShrOut), 60)), 20), ts_mean(abs(safe_div(close, open)), 20)) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 1 | Capitalization growth net of share-count growth as per-share value creation | ts_zscore(safe_div(safe_div(safe_div(cap, ts_mean(cap, 60)), safe_div(ShrOut, ts_mean(ShrOut, 60))), safe_div(safe_div(cap, ShrOut), close)), 120) | - | - | - | - | - | - | - |
| s500-c2-r002 | 0 | Share-count contraction as an index-level capital-return timing signal | -1 * safe_div(safe_div(ts_delta(ShrOut, 126), ts_mean(ShrOut, 252)), ts_mean(close, 252)) | - | - | - | - | - | - | - |
| s500-c2-r002 | 1 | Share-count contraction as an index-level capital-return timing signal | -1 * ts_zscore(safe_div(ts_delta(ShrOut, 126), ts_mean(ShrOut, 126)), 252) * ts_zscore(close, 252) | - | - | - | - | - | - | - |
| s500-c2-r002 | 2 | Share-count contraction as an index-level capital-return timing signal | -1 * ts_zscore(safe_div(ts_delta(ShrOut, 252), ts_mean(ShrOut, 252)), 252) * ts_zscore(safe_div(ts_mean(close, 21), ts_mean(close, 252)), 252) | - | - | - | - | - | - | - |
| sysv1-h5 | 0 | Index turnover intensity relative to its own size as attention-driven reversal | -1 * safe_div(ts_mean(safe_div(volume, ShrOut), 20), ts_mean(safe_div(volume, ShrOut), 120)) * ts_ir(ts_returns(close, 1), 20) | - | - | - | - | - | - | - |
| camp-c1-r001 | 0 | Volume absorbed without intraday price movement as an absorbed-flow / fading-pressure state | -ts_mean(safe_div(abs(safe_div(close - open, open)), safe_div(volume, ShrOut)), 20) | - | - | - | - | - | - | - |
| camp-c1-r001 | 0 | Capitalization growth net of share-count growth as per-share value creation | safe_div(cap, ts_delta(close * ShrOut, 60)) | - | - | - | - | - | - | - |
| camp-c1-r001 | 1 | Volume absorbed without intraday price movement as an absorbed-flow / fading-pressure state | safe_div(ts_mean(safe_div(safe_div(volume, ShrOut), ts_mean(safe_div(volume, ShrOut), 60)), 20), ts_mean(abs(safe_div(close, open)), 20)) | - | - | - | - | - | - | - |
| camp-c1-r001 | 1 | Capitalization growth net of share-count growth as per-share value creation | ts_zscore(safe_div(safe_div(safe_div(cap, ts_mean(cap, 60)), safe_div(ShrOut, ts_mean(ShrOut, 60))), safe_div(safe_div(cap, ShrOut), close)), 120) | - | - | - | - | - | - | - |

## Summary


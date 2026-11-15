# Field card: `vwretd`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **no (raw data-contract field, historical records only)**

## EDA evidence

_no Agent-1 EDA evidence for this field (derived or not in raw data)_

## Backtest evidence (13)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| 20261031-systemv1_50 | 0 | Cross-sectional dispersion regime and index reversal after wide-dispersion days | -1 * (ts_zscore(ts_sum(ewretd, 5), 60) - ts_zscore(ts_sum(vwretd, 5), 60)) * ts_ir(returns, 60) | - | - | - | - | - | - | - |
| 20261031-systemv1_50 | 0 | Index idiosyncratic-to-common volatility ratio predicts index reversal | -1 * ts_ir(returns, 20) * safe_div(ts_ir(ewretd, 20), ts_ir(vwretd, 20)) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 0 | Breadth versus capitalization weighting: equal-weighted return dominating cap-weighted return signals broad participation and continued strength | safe_div(ts_mean(ewretd, 10), ts_mean(vwretd, 20)) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 0 | Equal-weighted minus value-weighted leadership gap predicts index reversal | 0 - ts_zscore(ts_returns(safe_div(ewretd, vwretd), 5), 60) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 1 | Equal-weighted minus value-weighted leadership gap predicts index reversal | 0 - ts_zscore(ts_returns(safe_div(vwretd, ewretd), 5), 60) | - | - | - | - | - | - | - |
| s500-c1-r004 | 0 | 等权与市值权收益差收敛：横截面广度走弱后市场层面的短期修复 | -1 * ts_zscore(ts_mean(safe_div(vwretd, ewretd), 10), 60) | - | - | - | - | - | - | - |
| s500-c1-r004 | 1 | 等权与市值权收益差收敛：横截面广度走弱后市场层面的短期修复 | -1 * ts_zscore(ts_mean(safe_div(ewretd, vwretd), 10), 60) | - | - | - | - | - | - | - |
| s500-c1-r004 | 2 | 等权与市值权收益差收敛：横截面广度走弱后市场层面的短期修复 | -1 * ts_zscore(ts_mean(safe_div(ewretd, vwretd), 20), 60) | - | - | - | - | - | - | - |
| sysv1-h5 | 0 | Cross-sectional dispersion regime and index reversal after wide-dispersion days | -1 * (ts_zscore(ts_sum(ewretd, 5), 60) - ts_zscore(ts_sum(vwretd, 5), 60)) * ts_ir(returns, 60) | - | - | - | - | - | - | - |
| sysv1-h5 | 0 | Index idiosyncratic-to-common volatility ratio predicts index reversal | -1 * ts_ir(returns, 20) * safe_div(ts_ir(ewretd, 20), ts_ir(vwretd, 20)) | - | - | - | - | - | - | - |
| camp-c1-r004 | 0 | Breadth versus capitalization weighting: equal-weighted return dominating cap-weighted return signals broad participation and continued strength | safe_div(ts_mean(ewretd, 10), ts_mean(vwretd, 20)) | - | - | - | - | - | - | - |
| camp-c3-r003 | 0 | Equal-weighted minus value-weighted leadership gap predicts index reversal | 0 - ts_zscore(ts_returns(safe_div(ewretd, vwretd), 5), 60) | - | - | - | - | - | - | - |
| camp-c3-r003 | 1 | Equal-weighted minus value-weighted leadership gap predicts index reversal | 0 - ts_zscore(ts_returns(safe_div(vwretd, ewretd), 5), 60) | - | - | - | - | - | - | - |

## Summary


# Field card: `DlyPrcVol`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **no (raw data-contract field, historical records only)**

## EDA evidence

_no Agent-1 EDA evidence for this field (derived or not in raw data)_

## Backtest evidence (7)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| 20261031-systemv1_50 | 0 | 指数 ETF 的隐含平均成交价抬升作为价格过度延伸信号 | -1 * ts_zscore(safe_div(DlyPrcVol, volume), 252) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 0 | Index illiquidity (price impact per dollar traded) predicts weaker forward index returns | -1 * ts_zscore(ts_mean(safe_div(abs(returns), DlyPrcVol), 20), 60) | - | - | - | - | - | - | - |
| s500-c2-r003 | 2 | 成交金额隐含均价在当日区间中的位置作为短期反应过度代理 | -ts_mean(safe_div(DlyPrcVol, volume * (high - low)), 5) | - | - | - | - | - | - | - |
| s500-c2-r006 | 1 | Extreme dollar-volume climax days as market-level seller-exhaustion indicator | -(ts_max_diff(DlyPrcVol, 20) * ts_zscore(ts_returns(close, 60), 120) * ts_zscore(ts_mean(returns, 5), 120)) | - | - | - | - | - | - | - |
| s500-c2-r006 | 2 | Extreme dollar-volume climax days as market-level seller-exhaustion indicator | -(ts_max_diff(DlyPrcVol, 20) * ts_zscore(ts_returns(close, 20), 120) * ts_zscore(returns, 120)) | - | - | - | - | - | - | - |
| sysv1-h3 | 0 | 指数 ETF 的隐含平均成交价抬升作为价格过度延伸信号 | -1 * ts_zscore(safe_div(DlyPrcVol, volume), 252) | - | - | - | - | - | - | - |
| camp-c1-r003 | 0 | Index illiquidity (price impact per dollar traded) predicts weaker forward index returns | -1 * ts_zscore(ts_mean(safe_div(abs(returns), DlyPrcVol), 20), 60) | - | - | - | - | - | - | - |

## Summary


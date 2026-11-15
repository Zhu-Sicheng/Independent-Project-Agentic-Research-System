# Field card: `DlyAsk`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **no (raw data-contract field, historical records only)**

## EDA evidence

_no Agent-1 EDA evidence for this field (derived or not in raw data)_

## Backtest evidence (15)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| 20261031-systemv1_50 | 0 | Bid-ask spread widening as liquidity-stress predictor of index drawdowns | -1 * ts_zscore(safe_div(ts_mean(safe_div(ts_range(DlyAsk, 10), DlyBid), 10), ts_mean(safe_div(ts_range(DlyAsk, 120), DlyBid), 120)), 120) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 0 | Relative quoted spread expansion versus its own norm as a liquidity-stress state signal | ts_zscore(ts_mean(safe_div(safe_div(DlyAsk, close), safe_div(DlyBid, close)), 20), 120) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 0 | Elevated SPY quoted spread predicts weaker subsequent index returns | 0 - ts_zscore(ts_mean(ts_returns(safe_div(DlyBid, DlyAsk), 1), 5), 60) | - | - | - | - | - | - | - |
| 20261101-sysv1-campaign | 1 | Elevated SPY quoted spread predicts weaker subsequent index returns | 0 - ts_bollinger_position(safe_div(DlyBid, DlyAsk), 20) | - | - | - | - | - | - | - |
| s500-c1-r002 | 2 | 价差收窄作为流动性修复：SPY 相对价差偏离与区间位置的组合择时 | -1 * ts_min_max_diff(safe_div(DlyAsk, DlyBid), 20, 0.5) * ts_min_max_diff(close, 20, 0.5) * safe_div(high, low) | - | - | - | - | - | - | - |
| s500-c1-r007 | 0 | 报价价差压缩后的指数正收益：流动性成本下降的风险承担渠道 | ts_median(safe_div(DlyAsk, DlyBid), 250) / ts_median(safe_div(DlyAsk, DlyBid), 20) | - | - | - | - | - | - | - |
| s500-c1-r007 | 2 | 报价价差压缩后的指数正收益：流动性成本下降的风险承担渠道 | -ts_delta(safe_div(DlyAsk, DlyBid), 250) / ts_std_dev(safe_div(DlyAsk, DlyBid), 250) | - | - | - | - | - | - | - |
| s500-c3-r005 | 0 | Widening relative quoted bid-ask spread on the index proxy signals elevated risk-bearing cost and precedes higher subsequent index return | safe_div(ts_mean(safe_div(DlyAsk, DlyBid) * safe_div(DlyBid, close), 20), ts_mean(safe_div(DlyAsk, DlyBid) * safe_div(DlyBid, close), 120)) | - | - | - | - | - | - | - |
| s500-c3-r005 | 2 | Widening relative quoted bid-ask spread on the index proxy signals elevated risk-bearing cost and precedes higher subsequent index return | safe_div(ts_mean(safe_div(DlyAsk, close), 20), ts_mean(safe_div(DlyBid, close), 120)) | - | - | - | - | - | - | - |
| s500-c4-r010 | 0 | 流动性压力（报价价差相对自身基线走宽）后短期收益补偿更高 | ts_zscore(safe_div(DlyAsk, DlyBid), 63) | - | - | - | - | - | - | - |
| s500-c4-r010 | 1 | 流动性压力（报价价差相对自身基线走宽）后短期收益补偿更高 | ts_zscore(ts_mean(safe_div(DlyAsk, DlyBid), 20), 63) | - | - | - | - | - | - | - |
| sysv1-h5 | 0 | Bid-ask spread widening as liquidity-stress predictor of index drawdowns | -1 * ts_zscore(safe_div(ts_mean(safe_div(ts_range(DlyAsk, 10), DlyBid), 10), ts_mean(safe_div(ts_range(DlyAsk, 120), DlyBid), 120)), 120) | - | - | - | - | - | - | - |
| camp-c1-r001 | 0 | Relative quoted spread expansion versus its own norm as a liquidity-stress state signal | ts_zscore(ts_mean(safe_div(safe_div(DlyAsk, close), safe_div(DlyBid, close)), 20), 120) | - | - | - | - | - | - | - |
| camp-c3-r003 | 0 | Elevated SPY quoted spread predicts weaker subsequent index returns | 0 - ts_zscore(ts_mean(ts_returns(safe_div(DlyBid, DlyAsk), 1), 5), 60) | - | - | - | - | - | - | - |
| camp-c3-r003 | 1 | Elevated SPY quoted spread predicts weaker subsequent index returns | 0 - ts_bollinger_position(safe_div(DlyBid, DlyAsk), 20) | - | - | - | - | - | - | - |

## Summary


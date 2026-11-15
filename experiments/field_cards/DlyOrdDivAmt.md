# Field card: `DlyOrdDivAmt`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **no (raw data-contract field, historical records only)**

## EDA evidence

_no Agent-1 EDA evidence for this field (derived or not in raw data)_

## Backtest evidence (1)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| s500-c4-r004 | 2 | Abnormally high trailing dividend yield relative to its own history precedes weaker index returns | -1 * ts_zscore(safe_div(ts_sum(DlyOrdDivAmt, 252), close), 252) * ts_zscore(ts_mean(returns, 252), 252) | - | - | - | - | - | - | - |

## Summary


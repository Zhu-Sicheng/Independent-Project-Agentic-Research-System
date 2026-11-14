# Published results: `systemv1-500`

- runs: 8 (s500-c1-r001, s500-c1-r002, s500-c2-r001, s500-c2-r002, s500-c2-r003, s500-c3-r001, ...)
- evaluated expressions: 95 unique canonical forms
- decisions: {'abandon': 76, 'optimize': 11, nan: 5, 'accept': 3}
- data isolation: the optimisation loop and the reviewer saw in-sample only; OOS/holdout are display-only and were never fed back

## Headline statistics

| metric | value |
|---|---|
| IS Sharpe median / p90 | 0.249 / 1.102 |
| share of expressions with IS Sharpe > 1 | 12.2% |
| OOS Sharpe median | 0.079 |
| share of expressions with OOS Sharpe > 0 | 58.9% |
| holdout Sharpe median | -0.199 |
| share with both OOS and holdout positive | 32.2% (n=90) |

## Top 5 by in-sample Sharpe

| hypothesis | decision | is_sharpe | is_ann_return | is_turnover | is_rank_ic | oos_sharpe | oos_ann_return | holdout_sharpe | subuniverse_sharpe | run_id |
|---|---|---|---|---|---|---|---|---|---|---|
| Intraday order imbalance from the closing clip as a short-horizon index pressure signal | accept | 2.210 | 10.5% | 94.64 | 0.0204 | 0.150 | 0.7% | 0.629 | 2.185 | s500-c2-r002 |
| Intraday order imbalance from the closing clip as a short-horizon index pressure signal | accept | 1.898 | 8.9% | 99.44 | 0.0186 | -0.014 | -0.1% | 0.868 | 1.806 | s500-c2-r002 |
| Intraday order imbalance from the closing clip as a short-horizon index pressure signal | optimize | 1.683 | 9.4% | 53.74 | 0.0149 | 0.121 | 0.7% | -0.450 | 1.683 | s500-c2-r002 |
| Short-horizon reversal under abnormal volume | optimize | 1.280 | 7.0% | 85.14 | 0.0117 | 0.274 | 1.4% | 0.745 | 1.280 | s500-c3-r001 |
| 短期价格反转：5日收益的横截面反转为正（价格压力 vs 基本面信息） | abandon | 1.272 | 7.4% | 52.46 | 0.0113 | 0.085 | 0.5% | 0.801 | 1.272 | s500-c3-r003 |

`summary.csv` has every evaluated expression with IS, sub-universe, OOS and holdout metrics, the hypothesis and the reviewer decision.

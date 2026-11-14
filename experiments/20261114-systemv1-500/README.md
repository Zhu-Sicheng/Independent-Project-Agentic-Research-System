# Published results: `systemv1-500`

- runs: 49 (s500-c1-r001, s500-c1-r002, s500-c1-r003, s500-c1-r004, s500-c1-r005, s500-c1-r006, ...)
- evaluated expressions: 518 unique canonical forms
- decisions: {'abandon': 404, 'optimize': 82, nan: 20, 'accept': 12}
- data isolation: the optimisation loop and the reviewer saw in-sample only; OOS/holdout are display-only and were never fed back

## Headline statistics

| metric | value |
|---|---|
| IS Sharpe median / p90 | 0.254 / 1.147 |
| share of expressions with IS Sharpe > 1 | 13.7% |
| OOS Sharpe median | 0.083 |
| share of expressions with OOS Sharpe > 0 | 57.6% |
| holdout Sharpe median | 0.036 |
| share with both OOS and holdout positive | 36.2% (n=495) |

## Top 20 by in-sample Sharpe

| hypothesis | decision | is_sharpe | is_ann_return | is_turnover | is_rank_ic | oos_sharpe | oos_ann_return | holdout_sharpe | subuniverse_sharpe | run_id |
|---|---|---|---|---|---|---|---|---|---|---|
| 日内收盘位置：收盘价靠近区间低点预示短期反弹 | optimize | 2.621 | 13.2% | 94.06 | 0.0253 | 0.365 | 1.9% | 0.259 | 2.621 | s500-c4-r009 |
| Intraday order imbalance from the closing clip as a short-horizon index pressure signal | accept | 2.210 | 10.5% | 94.64 | 0.0204 | 0.150 | 0.7% | 0.629 | 2.185 | s500-c2-r002 |
| 日内收盘位置：收盘价靠近区间低点预示短期反弹 | optimize | 2.059 | 11.2% | 77.95 | 0.0193 | 0.127 | 0.7% | 0.054 | 2.059 | s500-c4-r009 |
| 收盘位于区间上沿的短期反转（日内位置效应） | abandon | 2.059 | 11.2% | 77.95 | 0.0193 | 0.127 | 0.7% | 0.054 | 2.059 | s500-c6-r003 |
| 日内收益位置：收盘在当日振幅中的相对位置（Close Location Value） | accept | 2.052 | 9.9% | 56.78 | 0.0190 | -0.070 | -0.4% | -0.491 | 2.052 | s500-c4-r005 |
| Close positioned near the session low signals short-horizon supply pressure | optimize | 1.947 | 8.8% | 67.44 | 0.0149 | 0.097 | 0.5% | 0.003 | 1.921 | s500-c7-r001 |
| Intraday order imbalance from the closing clip as a short-horizon index pressure signal | accept | 1.898 | 8.9% | 99.44 | 0.0186 | -0.014 | -0.1% | 0.868 | 1.806 | s500-c2-r002 |
| Stock-specific volatility expansion relative to its own baseline as an uncertainty-discount signal | abandon | 1.801 | 8.8% | 69.74 | 0.0139 | -0.097 | -0.5% | -0.116 | 1.801 | s500-c2-r006 |
| 收盘位于区间上沿的短期反转（日内位置效应） | optimize | 1.749 | 8.7% | 82.97 | 0.0161 | 0.089 | 0.5% | 0.564 | 1.749 | s500-c6-r003 |
| Intraday order imbalance from the closing clip as a short-horizon index pressure signal | optimize | 1.683 | 9.4% | 53.74 | 0.0149 | 0.121 | 0.7% | -0.450 | 1.683 | s500-c2-r002 |
| 收盘持续位于日内区间高位的个股短期收益回吐 | accept | 1.683 | 9.4% | 53.74 | 0.0149 | 0.121 | 0.7% | -0.450 | 1.683 | s500-c4-r010 |
| Cross-sectional short-term reversal of adjusted close over 1-5 trading days | abandon | 1.493 | 8.4% | 81.3 | 0.0166 | 0.667 | 3.8% | 0.459 | 1.493 | s500-c1-r005 |
| Market-cap repair after a drawdown: names that recovered capitalisation within a noisy window outperform | accept | 1.443 | 10.4% | 86.54 | 0.0092 | 0.438 | 3.3% | 0.082 | 1.387 | s500-c3-r007 |
| Market-cap repair after a drawdown: names that recovered capitalisation within a noisy window outperform | abandon | 1.421 | 10.1% | 90.59 | 0.0103 | 0.431 | 3.1% | 0.133 | 1.414 | s500-c3-r007 |
| 量价背离：成交量相对基线抬升而价格盘中收在区间下沿，预示走弱 | optimize | 1.413 | 6.8% | 47.64 | 0.0137 | -0.061 | -0.3% | -0.181 | 1.413 | s500-c1-r004 |
| Index drawdown from recent high as a mean-reversion timing signal (SPY) | abandon | 1.401 | 9.7% | 92.77 | 0.0118 | 0.530 | 3.8% | 0.124 | 1.401 | s500-c2-r008 |
| ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | abandon | 1.390 | 6.8% | 93.15 | 0.0158 | 0.839 | 4.3% | 0.652 | 1.390 | s500-c2-r005 |
| 近期收益的高波动放大：短窗收益/波动比作为过度反应与反转的代理 | abandon | 1.365 | 8.9% | 49.7 | 0.0112 | 0.200 | 1.3% | 0.785 | 1.365 | s500-c1-r004 |
| 近期收益的高波动放大：短窗收益/波动比作为过度反应与反转的代理 | abandon | 1.365 | 8.9% | 49.7 | 0.0112 | 0.200 | 1.3% | 0.785 | 1.365 | s500-c1-r004 |
| 日内收益位置：收盘在当日振幅中的相对位置（Close Location Value） | optimize | 1.359 | 7.0% | 39.43 | 0.0128 | 0.115 | 0.6% | -0.679 | 1.359 | s500-c4-r005 |

`summary.csv` has every evaluated expression with IS, sub-universe, OOS and holdout metrics, the hypothesis and the reviewer decision.

# Factor mining run

- run id: `20261031-083828-e2e`
- data: 6726 days x 1195 names, 2000-01-03 -> 2026-09-30
- LLM: `openai-compatible`
- hypotheses: 1, factors added: 0
- sample split: date-based: IS to 2020-12-31, OOS from 2021-01-01, OOS to 2024-12-31, holdout from 2025-01-01
  - in-sample ['2000-01-03', '2020-12-31'] (5284 days) / out-of-sample ['2021-01-04', '2024-12-31'] (1005 days) / holdout ['2025-01-02', '2026-09-30'] (437 days)

## Hypotheses and decisions

| hypothesis | attempt | decision | sharpe all | ann return | turnover | maxDD | RankIC | factor | sharpe IS | sharpe OOS | sharpe Holdout | sharpe sub |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| overnight_intraday_return_divergence | 1 | abandon | -0.46 | -2.6% | 32.9 | -52.4% | -0.008 | - | -0.49 | -0.40 | -0.23 | -0.46 |

## overnight_intraday_return_divergence

**hypothesis**: Stocks whose 20-day cumulative overnight return exceeds their 20-day cumulative intraday return (positive divergence) underperform over the next 5 trading days, and stocks with the opposite divergence outperform; the cross-sectional rank IC of the divergence factor is negative.

**economic rationale**: The overnight and intraday sessions are dominated by different clienteles: overnight moves absorb retail/attention-driven and news-gap flow (often transient), while the intraday session reflects institutional execution and price discovery that is more likely to persist. When a stock's recent cumulative overnight return strongly outpaces its intraday return, the overnight component is more likely to be sentiment-driven and mean-revert, whereas stocks whose gains came during the liquid intraday session carry more durable information. Hence the divergence between the two components should predict reversal of the overnight-driven leg.

best config: decay=0, transform=none, cap_filter=0.3, windows=[20, 20], params={}

- **decision**: abandon
- **reasoning**: The factor's best configuration has a Sharpe of -0.455 with rank IC of -0.0076, and 0% of grid evaluations produced a positive Sharpe — the sign is wrong relative to the hypothesis, which predicted a negative IC. The negative rank IC actually matches the hypothesis direction, but the long/short implementation loses money consistently across all segments (IS -0.49, OOS -0.40, holdout -0.23) and every sub-period, with turnover an extreme 33x. There is no stable edge to salvage, and the in-sample sign is already contradicted by the implementation's realized P&L.
- **diagnosis**: Signal is essentially zero (IC ~ -0.008, IR -0.05) and the sign of realized returns is opposite to the trading rule; extreme turnover (~33x) would destroy any residual edge even if present.
- **spec**: `rank(ts_sum(intraday_return, 20) - ts_sum(overnight_return, 20))`
- **sub-universe** (rank(cap) > 0.3, reference only): sharpe -0.46, return -2.6%/yr, turnover 32.9, maxDD -52.4%, RankIC -0.008 — identical to the primary book because the best config already drops the same names
- **in-sample**: sharpe -0.49, return -2.8%/yr, turnover 32.4, maxDD -47.2%, RankIC -0.008  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe -0.40, return -2.1%/yr, turnover 34.7, maxDD -12.6%, RankIC -0.004  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe -0.23, return -1.9%/yr, turnover 34.0, maxDD -11.9%, RankIC -0.009  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2000 | -10.9% | -1.19 | 30.0 | -13.2% | -0.015 |
| 2001 | -14.9% | -1.82 | 30.3 | -18.8% | -0.026 |
| 2002 | -3.4% | -0.42 | 31.5 | -10.6% | -0.009 |
| 2003 | -4.1% | -1.31 | 31.3 | -4.8% | -0.009 |
| 2004 | -2.6% | -0.94 | 28.6 | -4.3% | -0.014 |
| 2005 | -2.9% | -1.00 | 28.7 | -5.0% | -0.015 |
| 2006 | -0.3% | -0.06 | 30.4 | -3.2% | -0.003 |
| 2007 | 2.6% | 0.78 | 32.0 | -3.4% | 0.007 |
| 2008 | 0.5% | 0.09 | 34.9 | -12.4% | -0.007 |
| 2009 | -3.9% | -0.42 | 33.1 | -7.6% | -0.011 |
| 2010 | -3.0% | -0.94 | 31.2 | -4.2% | -0.004 |
| 2011 | -1.6% | -0.33 | 32.4 | -4.2% | -0.002 |
| 2012 | -1.8% | -0.65 | 33.7 | -3.1% | -0.001 |
| 2013 | -4.0% | -1.87 | 33.2 | -5.2% | -0.014 |
| 2014 | -0.6% | -0.17 | 32.8 | -3.6% | -0.008 |
| 2015 | 2.3% | 0.79 | 32.8 | -1.9% | 0.001 |
| 2016 | -2.7% | -0.71 | 33.7 | -8.4% | -0.016 |
| 2017 | 3.3% | 1.17 | 33.8 | -2.0% | 0.000 |
| 2018 | -0.4% | -0.07 | 34.4 | -2.9% | 0.000 |
| 2019 | -9.1% | -2.82 | 34.4 | -9.7% | -0.029 |
| 2020 | 0.6% | 0.12 | 37.6 | -14.1% | 0.005 |
| 2021 | 0.5% | 0.13 | 35.6 | -5.0% | 0.005 |
| 2022 | -6.8% | -1.16 | 34.8 | -10.0% | -0.010 |
| 2023 | 0.9% | 0.22 | 34.2 | -5.1% | -0.005 |
| 2024 | -3.0% | -0.71 | 34.3 | -5.3% | -0.006 |
| 2025 | 0.0% | 0.04 | 33.8 | -6.5% | -0.006 |
| 2026 | -3.3% | -0.56 | 34.3 | -5.5% | -0.013 |

holdout by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2025 | 0.0% | 0.04 | 33.8 | -6.5% | -0.006 |
| 2026 | -3.3% | -0.56 | 34.3 | -5.5% | -0.013 |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2021 | 0.5% | 0.13 | 35.6 | -5.0% | 0.005 |
| 2022 | -6.8% | -1.16 | 34.8 | -10.0% | -0.010 |
| 2023 | 0.9% | 0.22 | 34.2 | -5.1% | -0.005 |
| 2024 | -3.0% | -0.71 | 34.3 | -5.3% | -0.006 |
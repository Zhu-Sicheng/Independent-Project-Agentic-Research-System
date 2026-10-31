# Factor mining run

- run id: `20261030-122256-us`
- data: 6726 days x 1195 names, 2000-01-03 -> 2026-09-30
- LLM: `offline`
- hypotheses: 2, factors added: 0
- sample split: date-based: IS to 2020-12-31, OOS from 2021-01-01, OOS to 2024-12-31, holdout from 2025-01-01
  - in-sample ['2000-01-03', '2020-12-31'] (5284 days) / out-of-sample ['2021-01-04', '2024-12-31'] (1005 days) / holdout ['2025-01-02', '2026-09-30'] (437 days)

## Hypotheses and decisions

| hypothesis | attempt | decision | sharpe all | ann return | turnover | maxDD | IC | factor | sharpe IS | sharpe OOS | sharpe Holdout |
|---|---|---|---|---|---|---|---|---|---|---|---|
| short_term_reversal | 1 | abandon | 1.05 | 6.3% | 52.2 | -11.6% | 0.010 | - | 1.27 | 0.09 | 0.81 |
| low_volatility_anomaly | 1 | abandon | 0.17 | 1.3% | 56.7 | -37.3% | 0.007 | - | 0.33 | 0.15 | -1.29 |

## short_term_reversal

**hypothesis**: Stocks whose 5-day return is in the bottom cross-sectional decile outperform those in the top decile over the next week.

**economic rationale**: Liquidity providers demand compensation for absorbing uninformed order flow. When a stock sells off for several days, the price temporarily overshoots and partially reverts.

best config: decay=5, transform=sign, cap_filter=0.3, windows=[5], params={}

- **decision**: abandon
- **reasoning**: In-sample Sharpe 1.27 does not survive the untouched segments (out-of-sample 0.09, holdout 0.81). The configuration is selected on noise; abandon.
- **diagnosis**: turnover is very high, costs will dominate
- **spec**: `-ts_mean(returns, 5)`
- **in-sample**: sharpe 1.27, return 7.5%/yr, turnover 52.5, maxDD -11.6%, IC 0.011  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe 0.09, return 0.4%/yr, turnover 51.3, maxDD -8.3%, IC 0.003  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe 0.81, return 6.4%/yr, turnover 50.3, maxDD -7.9%, IC 0.015  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | IC |
|---|---|---|---|---|---|
| 2000 | 27.8% | 2.61 | 50.4 | -4.3% | 0.024 |
| 2001 | 17.2% | 1.51 | 52.8 | -7.3% | 0.021 |
| 2002 | 13.7% | 1.76 | 53.2 | -3.2% | 0.017 |
| 2003 | 4.0% | 1.05 | 53.3 | -1.8% | 0.007 |
| 2004 | 3.5% | 1.08 | 51.4 | -1.7% | 0.009 |
| 2005 | 4.9% | 1.59 | 51.3 | -2.2% | 0.013 |
| 2006 | 7.4% | 2.12 | 52.4 | -2.8% | 0.015 |
| 2007 | 8.0% | 2.24 | 53.8 | -1.5% | 0.014 |
| 2008 | 13.6% | 1.23 | 54.4 | -6.3% | 0.013 |
| 2009 | 14.2% | 2.05 | 53.8 | -2.5% | 0.018 |
| 2010 | 3.7% | 1.26 | 53.0 | -1.2% | 0.006 |
| 2011 | 8.0% | 1.93 | 54.3 | -2.8% | 0.009 |
| 2012 | 3.8% | 1.25 | 53.0 | -1.7% | 0.004 |
| 2013 | 3.6% | 1.85 | 51.8 | -1.1% | 0.009 |
| 2014 | 3.7% | 1.18 | 51.8 | -3.7% | 0.014 |
| 2015 | 0.2% | 0.07 | 53.2 | -4.8% | -0.000 |
| 2016 | 4.9% | 1.23 | 52.4 | -2.6% | 0.020 |
| 2017 | -0.4% | -0.11 | 49.0 | -3.7% | 0.000 |
| 2018 | 0.9% | 0.23 | 52.3 | -1.8% | 0.005 |
| 2019 | 2.5% | 0.64 | 51.0 | -3.1% | 0.013 |
| 2020 | 16.6% | 1.50 | 53.5 | -10.6% | 0.007 |
| 2021 | 0.1% | 0.05 | 50.1 | -4.2% | 0.002 |
| 2022 | 1.5% | 0.24 | 53.2 | -7.4% | -0.003 |
| 2023 | -0.9% | -0.17 | 51.3 | -3.9% | 0.002 |
| 2024 | 0.7% | 0.17 | 50.7 | -3.6% | 0.009 |
| 2025 | 2.0% | 0.31 | 50.7 | -5.0% | 0.011 |
| 2026 | 9.1% | 1.39 | 49.8 | -7.4% | 0.021 |

holdout by year:

| year | return | sharpe | turnover | maxDD | IC |
|---|---|---|---|---|---|
| 2025 | 2.0% | 0.31 | 50.7 | -5.0% | 0.011 |
| 2026 | 9.1% | 1.39 | 49.8 | -7.4% | 0.021 |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | IC |
|---|---|---|---|---|---|
| 2021 | 0.1% | 0.05 | 50.1 | -4.2% | 0.002 |
| 2022 | 1.5% | 0.24 | 53.2 | -7.4% | -0.003 |
| 2023 | -0.9% | -0.17 | 51.3 | -3.9% | 0.002 |
| 2024 | 0.7% | 0.17 | 50.7 | -3.6% | 0.009 |

## low_volatility_anomaly

**hypothesis**: Stocks with low 20-day realised volatility outperform high-volatility stocks on a risk-adjusted basis over the following month.

**economic rationale**: Leverage-constrained investors and lottery-seeking behaviour bid up high-volatility names, so low-volatility stocks earn a premium per unit of risk.

best config: decay=0, transform=none, cap_filter=0.3, windows=[5], params={}

- **decision**: abandon
- **reasoning**: In-sample Sharpe 0.33 does not survive the untouched segments (out-of-sample 0.15, holdout -1.29). The configuration is selected on noise; abandon.
- **diagnosis**: turnover is very high, costs will dominate; the drawdown is large relative to the return
- **spec**: `-ts_std(returns, 20)`
- **in-sample**: sharpe 0.33, return 3.1%/yr, turnover 56.4, maxDD -28.7%, IC 0.011  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe 0.15, return 0.8%/yr, turnover 58.7, maxDD -13.7%, IC -0.000  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe -1.29, return -17.0%/yr, turnover 56.0, maxDD -35.4%, IC -0.020  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | IC |
|---|---|---|---|---|---|
| 2000 | 26.5% | 1.43 | 54.5 | -9.7% | 0.027 |
| 2001 | 9.5% | 0.51 | 48.0 | -17.3% | 0.017 |
| 2002 | 10.0% | 0.62 | 51.7 | -21.9% | 0.026 |
| 2003 | -7.6% | -1.15 | 56.0 | -8.4% | -0.005 |
| 2004 | 4.6% | 0.79 | 56.2 | -4.2% | 0.009 |
| 2005 | -6.0% | -1.15 | 56.8 | -8.7% | -0.008 |
| 2006 | 7.3% | 1.38 | 54.0 | -3.2% | 0.021 |
| 2007 | 8.1% | 1.35 | 57.0 | -3.7% | 0.019 |
| 2008 | 9.4% | 0.49 | 53.9 | -14.8% | 0.027 |
| 2009 | -14.3% | -0.73 | 52.6 | -23.8% | -0.006 |
| 2010 | -1.1% | -0.15 | 55.5 | -5.4% | 0.010 |
| 2011 | 9.0% | 1.10 | 56.0 | -7.4% | 0.025 |
| 2012 | 0.4% | 0.10 | 56.7 | -4.2% | 0.013 |
| 2013 | 0.7% | 0.22 | 60.8 | -2.7% | 0.005 |
| 2014 | 4.6% | 1.00 | 58.1 | -2.5% | 0.014 |
| 2015 | 7.9% | 1.59 | 60.7 | -4.9% | 0.025 |
| 2016 | -3.8% | -0.51 | 56.8 | -8.8% | -0.003 |
| 2017 | 4.0% | 1.25 | 55.6 | -1.8% | 0.007 |
| 2018 | 7.7% | 1.34 | 61.1 | -3.5% | 0.010 |
| 2019 | -7.2% | -1.47 | 60.0 | -7.4% | -0.018 |
| 2020 | 2.7% | 0.28 | 61.2 | -12.3% | 0.012 |
| 2021 | 0.2% | 0.07 | 58.6 | -7.4% | -0.004 |
| 2022 | 12.8% | 1.34 | 58.7 | -4.7% | 0.027 |
| 2023 | -7.9% | -1.38 | 60.1 | -8.7% | -0.018 |
| 2024 | -0.8% | -0.10 | 57.4 | -6.5% | -0.006 |
| 2025 | -10.1% | -0.93 | 57.7 | -16.4% | -0.012 |
| 2026 | -19.4% | -1.67 | 53.8 | -22.3% | -0.031 |

holdout by year:

| year | return | sharpe | turnover | maxDD | IC |
|---|---|---|---|---|---|
| 2025 | -10.1% | -0.93 | 57.7 | -16.4% | -0.012 |
| 2026 | -19.4% | -1.67 | 53.8 | -22.3% | -0.031 |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | IC |
|---|---|---|---|---|---|
| 2021 | 0.2% | 0.07 | 58.6 | -7.4% | -0.004 |
| 2022 | 12.8% | 1.34 | 58.7 | -4.7% | 0.027 |
| 2023 | -7.9% | -1.38 | 60.1 | -8.7% | -0.018 |
| 2024 | -0.8% | -0.10 | 57.4 | -6.5% | -0.006 |
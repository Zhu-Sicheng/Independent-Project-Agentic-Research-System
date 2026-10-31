# Factor mining run

- run id: `20261031-101653-batch10c`
- data: 6726 days x 1195 names, 2000-01-03 -> 2026-09-30
- LLM: `openai-compatible`
- hypotheses: 6, factors added: 0
- sample split: date-based: IS to 2020-12-31, OOS from 2021-01-01, OOS to 2024-12-31, holdout from 2025-01-01
  - in-sample ['2000-01-03', '2020-12-31'] (5284 days) / out-of-sample ['2021-01-04', '2024-12-31'] (1005 days) / holdout ['2025-01-02', '2026-09-30'] (437 days)

## Hypotheses and decisions

| hypothesis | attempt | decision | sharpe all | ann return | turnover | maxDD | RankIC | factor | sharpe IS | sharpe OOS | sharpe Holdout | sharpe sub |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| overnight_intraday_reversal | 1 | abandon | 0.40 | 1.9% | 4.5 | -11.2% | -0.000 | - | 0.47 | 0.19 | 0.26 | 0.40 |
| close_position_persistence | 1 | abandon | 0.51 | 4.5% | 8.3 | -32.0% | 0.000 | - | 0.40 | 0.82 | 1.28 | -0.12 |
| range_contraction_breakout | 1 | abandon | 0.07 | 0.2% | 4.5 | -26.2% | 0.002 | - | 0.15 | 0.32 | -1.60 | 0.07 |
| dollar_volume_shock_reversal | 1 | abandon | 0.50 | 7.8% | 11.6 | -41.1% | - | - | 0.50 | 0.65 | 0.36 | 0.50 |
| overnight_gap_fade | 1 | abandon | 0.65 | 3.6% | 12.2 | -17.0% | 0.002 | - | 0.73 | 0.57 | 0.32 | 0.65 |
| intraday_momentum_continuation | 1 | abandon | 0.60 | 5.3% | 8.3 | -29.8% | 0.000 | - | 0.51 | 0.82 | 1.28 | -0.11 |

## overnight_intraday_reversal

**hypothesis**: Stocks whose cumulative overnight return over the past 20 days exceeds their cumulative intraday return (i.e., gains concentrated overnight) underperform over the next 5 trading days; the reverse holds for stocks whose gains are concentrated intraday.

**economic rationale**: Overnight moves are driven disproportionately by retail/less-informed order flow and liquidity-driven gaps, while intraday prices are set under fuller information and deeper liquidity. When a stock's recent overnight returns persistently outrun its intraday returns, the overnight component is likely to mean-revert as informed trading corrects the gap during the session. This creates a premium for shorting stocks with a high overnight-to-intraday return imbalance and buying the reverse.

best config: decay=60, transform=none, cap_filter=0.3, windows=[60, 20], params={}

- **decision**: abandon
- **reasoning**: The factor's rank IC is essentially zero across all segments (-0.0004 full, in-sample 0.0003, OOS -0.0012), and the best in-sample Sharpe of 0.396 does not survive out of sample (0.188) or holdout (0.258), with holdout rank IC actually negative (-0.006) despite the expected sign being negative for the traded factor — the IC sign is wrong relative to the hypothesis. Only 37.5% of grid configs had positive Sharpe and none exceeded 0.5, indicating no robust edge anywhere in the parameter space. The story is plausible but the evidence simply does not support a tradable signal, and turnover of ~4.5 with near-zero IC means costs would dominate.
- **diagnosis**: No signal: near-zero IC in every segment, unstable sign, and the modest in-sample Sharpe fails to persist OOS/holdout; the raw overnight-minus-intraday spread at 20 days carries no cross-sectional predictive content.
- **spec**: `-rank(ts_sum(overnight_return, 20) - ts_sum(intraday_return, 20))`
- **sub-universe** (rank(cap) > 0.3, reference only): sharpe 0.40, return 1.9%/yr, turnover 4.5, maxDD -11.2%, RankIC -0.000 — identical to the primary book because the best config already drops the same names
- **in-sample**: sharpe 0.47, return 2.1%/yr, turnover 4.4, maxDD -7.7%, RankIC 0.000  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe 0.19, return 0.8%/yr, turnover 4.8, maxDD -5.6%, RankIC -0.001  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe 0.26, return 1.8%/yr, turnover 4.9, maxDD -11.2%, RankIC -0.006  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2000 | 7.9% | 0.95 | 3.5 | -7.7% | 0.014 |
| 2001 | 9.3% | 1.59 | 3.8 | -3.6% | 0.003 |
| 2002 | 11.2% | 1.85 | 4.4 | -2.4% | 0.011 |
| 2003 | -1.1% | -0.42 | 4.3 | -2.3% | -0.005 |
| 2004 | 2.7% | 0.75 | 3.7 | -2.0% | 0.001 |
| 2005 | -4.7% | -1.43 | 3.7 | -5.9% | -0.019 |
| 2006 | 2.2% | 0.58 | 3.8 | -2.6% | 0.004 |
| 2007 | 1.2% | 0.45 | 4.5 | -3.2% | 0.002 |
| 2008 | 9.2% | 0.93 | 4.7 | -5.5% | 0.005 |
| 2009 | 0.7% | 0.17 | 4.4 | -4.4% | -0.003 |
| 2010 | -0.3% | -0.08 | 4.2 | -2.2% | 0.002 |
| 2011 | 3.2% | 0.90 | 4.5 | -2.2% | 0.007 |
| 2012 | 0.8% | 0.30 | 4.7 | -2.4% | 0.006 |
| 2013 | -1.0% | -0.47 | 4.9 | -3.8% | -0.002 |
| 2014 | 0.9% | 0.34 | 4.6 | -2.3% | -0.002 |
| 2015 | -4.7% | -1.48 | 4.7 | -5.2% | -0.014 |
| 2016 | 3.0% | 0.90 | 5.1 | -2.2% | -0.000 |
| 2017 | -0.6% | -0.19 | 4.5 | -4.1% | -0.008 |
| 2018 | 4.2% | 1.23 | 4.7 | -1.6% | 0.008 |
| 2019 | -0.9% | -0.31 | 5.0 | -2.8% | -0.006 |
| 2020 | 2.1% | 0.35 | 4.9 | -5.2% | 0.007 |
| 2021 | 0.3% | 0.09 | 5.0 | -4.0% | 0.004 |
| 2022 | 0.6% | 0.14 | 4.9 | -5.6% | -0.004 |
| 2023 | 4.1% | 1.13 | 4.7 | -3.2% | 0.003 |
| 2024 | -1.8% | -0.35 | 4.6 | -3.9% | -0.009 |
| 2025 | 5.7% | 0.77 | 5.1 | -4.0% | 0.002 |
| 2026 | -2.4% | -0.31 | 4.6 | -8.6% | -0.017 |

holdout by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2025 | 5.7% | 0.77 | 5.1 | -4.0% | 0.002 |
| 2026 | -2.4% | -0.31 | 4.6 | -8.6% | -0.017 |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2021 | 0.3% | 0.09 | 5.0 | -4.0% | 0.004 |
| 2022 | 0.6% | 0.14 | 4.9 | -5.6% | -0.004 |
| 2023 | 4.1% | 1.13 | 4.7 | -3.2% | 0.003 |
| 2024 | -1.8% | -0.35 | 4.6 | -3.9% | -0.009 |

## close_position_persistence

**hypothesis**: Stocks with a high average close_position (close near the daily high) over the past 20 days outperform stocks with low average close_position over the next 5 trading days.

**economic rationale**: Where a stock closes within its daily high-low range signals the balance of end-of-day order flow and the willingness of buyers to hold into the close. Stocks that repeatedly close near their highs attract trend-following and momentum flows, while persistent weak closes reflect distribution. Because this intraday positioning is slow-moving and costly to arbitrage (requires holding overnight exposure), a persistent-close-strength premium can survive.

best config: decay=60, transform=sign, cap_filter=none, windows=[20], params={}

- **decision**: abandon
- **reasoning**: The best in-sample config has a near-zero rank_ic of 0.0002 and a Sharpe of 0.511 with -32% max drawdown, and only 14% of grid evals were even positive-Sharpe — the edge is essentially absent. The sub-universe Sharpe of -0.117 (and -0.20 in-sample) shows the signal does not survive outside small caps, and the holdout rank_ic is actually negative (-0.0048). The apparent OOS/holdout Sharpe gains come from the 'sign' transform and decay=60, not from genuine cross-sectional predictive power.
- **diagnosis**: Signal is essentially noise: rank_ic ~0.0002 full-universe, negative in sub-universe and holdout; performance is driven by the sign/decay transform and small-cap exposure rather than the close-position mechanism. Turnover of ~8x makes costs a further drag.
- **spec**: `rank(ts_mean(close_position, 20))`
- **sub-universe** (rank(cap) > 0.3, reference only): sharpe -0.12, return -1.0%/yr, turnover 7.9, maxDD -42.0%, RankIC 0.001
- **in-sample**: sharpe 0.40, return 3.5%/yr, turnover 8.3, maxDD -32.0%, RankIC 0.001  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe 0.82, return 7.3%/yr, turnover 8.3, maxDD -13.6%, RankIC 0.001  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe 1.28, return 11.2%/yr, turnover 8.3, maxDD -5.5%, RankIC -0.005  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2000 | 15.4% | 1.79 | 7.0 | -4.2% | 0.006 |
| 2001 | -0.5% | -0.01 | 9.0 | -12.3% | -0.004 |
| 2002 | -3.3% | -0.19 | 8.2 | -15.0% | -0.001 |
| 2003 | 4.7% | 0.54 | 7.5 | -7.6% | -0.004 |
| 2004 | -9.6% | -0.66 | 7.4 | -18.2% | 0.001 |
| 2005 | -0.5% | -0.03 | 7.9 | -8.1% | -0.001 |
| 2006 | 6.5% | 1.30 | 8.4 | -3.8% | 0.007 |
| 2007 | -0.2% | 0.01 | 9.0 | -6.5% | 0.005 |
| 2008 | -15.8% | -0.78 | 8.4 | -26.8% | -0.001 |
| 2009 | 17.9% | 1.23 | 8.8 | -14.4% | -0.001 |
| 2010 | 7.7% | 0.93 | 7.8 | -5.3% | -0.003 |
| 2011 | 8.8% | 0.89 | 8.1 | -6.2% | 0.008 |
| 2012 | 7.8% | 1.23 | 8.4 | -5.1% | 0.000 |
| 2013 | 3.9% | 0.69 | 8.0 | -5.5% | -0.002 |
| 2014 | 10.1% | 1.85 | 8.5 | -3.3% | 0.005 |
| 2015 | -1.6% | -0.20 | 9.0 | -6.4% | 0.001 |
| 2016 | 6.7% | 0.99 | 8.8 | -4.0% | -0.002 |
| 2017 | 7.0% | 1.77 | 8.5 | -1.8% | 0.000 |
| 2018 | -4.0% | -0.42 | 7.8 | -9.0% | 0.000 |
| 2019 | 11.0% | 1.81 | 9.0 | -3.9% | 0.004 |
| 2020 | 7.9% | 0.59 | 8.0 | -15.3% | -0.008 |
| 2021 | 14.8% | 1.93 | 8.5 | -5.2% | 0.001 |
| 2022 | 8.4% | 0.86 | 8.2 | -6.2% | -0.000 |
| 2023 | -3.2% | -0.27 | 8.4 | -13.6% | -0.004 |
| 2024 | 9.9% | 1.21 | 8.1 | -4.8% | 0.006 |
| 2025 | 18.2% | 2.00 | 7.8 | -3.5% | -0.003 |
| 2026 | 1.6% | 0.30 | 8.9 | -5.5% | -0.007 |

holdout by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2025 | 18.2% | 2.00 | 7.8 | -3.5% | -0.003 |
| 2026 | 1.6% | 0.30 | 8.9 | -5.5% | -0.007 |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2021 | 14.8% | 1.93 | 8.5 | -5.2% | 0.001 |
| 2022 | 8.4% | 0.86 | 8.2 | -6.2% | -0.000 |
| 2023 | -3.2% | -0.27 | 8.4 | -13.6% | -0.004 |
| 2024 | 9.9% | 1.21 | 8.1 | -4.8% | 0.006 |

## range_contraction_breakout

**hypothesis**: Stocks whose 20-day average high-low range is low relative to their 120-day average range (range compression) outperform over the next 20 trading days, with the effect stronger when recent 20-day return is positive.

**economic rationale**: Volatility is persistent but mean-reverting, and periods of unusually narrow high-low range ('coiling') often precede directional resolution as accumulated uncertainty is released. Stocks with recently compressed ranges relative to their own history attract informed positioning ahead of catalysts, and the resolution tends to be in the direction of recent drift. This pays a premium for bearing the timing risk of breakout realization.

best config: decay=60, transform=none, cap_filter=0.3, windows=[60, 120], params={}

- **decision**: abandon
- **reasoning**: The full-universe in-sample Sharpe is essentially zero (0.065, rank IC 0.0023) and only 16.7% of the 72 grid configurations produced a positive Sharpe, so the signal is weak even before validation. Out-of-sample Sharpe is a marginal 0.32 but the holdout is decisively negative (Sharpe -1.60, rank IC -0.0117, both 2025 and 2026 negative), meaning the edge does not survive the untouched sample. The hypothesis's core prediction of IC around 0.01-0.02 is never met; the factor is overfit noise rather than a stable volatility-compression premium.
- **diagnosis**: No real signal: near-zero in-sample IC and Sharpe, sign flips across regime segments (positive in 2007/2022, deeply negative in 2009/2025), and the holdout reverses the marginal OOS result. The story may be economically plausible in principle but the implementation captures nothing stable, so the evidence contradicts the hypothesis.
- **spec**: `-zscore(ts_mean((high - low) / close, 20) / ts_mean((high - low) / close, 120))`
- **sub-universe** (rank(cap) > 0.3, reference only): sharpe 0.07, return 0.2%/yr, turnover 4.5, maxDD -26.2%, RankIC 0.002 — identical to the primary book because the best config already drops the same names
- **in-sample**: sharpe 0.15, return 0.8%/yr, turnover 4.5, maxDD -26.2%, RankIC 0.003  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe 0.32, return 1.5%/yr, turnover 4.6, maxDD -9.5%, RankIC 0.003  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe -1.60, return -9.1%/yr, turnover 4.6, maxDD -16.2%, RankIC -0.012  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2000 | 4.3% | 0.64 | 3.5 | -5.1% | 0.007 |
| 2001 | 7.0% | 0.60 | 4.5 | -11.4% | 0.006 |
| 2002 | 6.7% | 0.91 | 4.6 | -5.6% | 0.004 |
| 2003 | -2.4% | -0.75 | 4.8 | -4.9% | -0.001 |
| 2004 | -1.6% | -0.58 | 4.8 | -4.0% | -0.005 |
| 2005 | -3.2% | -1.11 | 4.5 | -5.0% | -0.012 |
| 2006 | -2.7% | -0.81 | 4.5 | -4.4% | 0.002 |
| 2007 | 11.2% | 1.99 | 4.3 | -2.5% | 0.026 |
| 2008 | 7.4% | 0.55 | 4.2 | -6.5% | 0.009 |
| 2009 | -18.1% | -1.72 | 4.6 | -20.6% | -0.006 |
| 2010 | 3.0% | 0.97 | 4.6 | -2.8% | 0.014 |
| 2011 | 1.1% | 0.25 | 4.5 | -2.5% | 0.004 |
| 2012 | -3.4% | -1.06 | 4.5 | -3.5% | -0.001 |
| 2013 | -0.1% | -0.05 | 4.5 | -4.1% | 0.007 |
| 2014 | 2.2% | 0.54 | 4.4 | -3.3% | 0.002 |
| 2015 | 0.5% | 0.14 | 4.6 | -3.9% | 0.001 |
| 2016 | -0.7% | -0.15 | 4.6 | -6.4% | -0.001 |
| 2017 | 2.2% | 0.70 | 4.5 | -2.2% | 0.009 |
| 2018 | 1.9% | 0.49 | 4.7 | -3.3% | 0.002 |
| 2019 | -0.6% | -0.19 | 4.6 | -2.5% | -0.003 |
| 2020 | 5.6% | 0.61 | 4.6 | -7.4% | 0.007 |
| 2021 | 0.2% | 0.06 | 4.5 | -4.5% | -0.001 |
| 2022 | 7.9% | 1.14 | 4.4 | -5.4% | 0.016 |
| 2023 | -4.6% | -1.08 | 4.7 | -4.7% | -0.004 |
| 2024 | 2.9% | 0.65 | 4.7 | -3.4% | 0.002 |
| 2025 | -10.3% | -1.97 | 4.8 | -12.0% | -0.014 |
| 2026 | -5.6% | -1.18 | 4.5 | -5.0% | -0.008 |

holdout by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2025 | -10.3% | -1.97 | 4.8 | -12.0% | -0.014 |
| 2026 | -5.6% | -1.18 | 4.5 | -5.0% | -0.008 |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2021 | 0.2% | 0.06 | 4.5 | -4.5% | -0.001 |
| 2022 | 7.9% | 1.14 | 4.4 | -5.4% | 0.016 |
| 2023 | -4.6% | -1.08 | 4.7 | -4.7% | -0.004 |
| 2024 | 2.9% | 0.65 | 4.7 | -3.4% | 0.002 |

## dollar_volume_shock_reversal

**hypothesis**: Stocks with abnormally high 5-day dollar volume relative to their 60-day average dollar volume underperform over the next 5 trading days.

**economic rationale**: Sudden spikes in dollar volume (amount) relative to a stock's normal trading reflect attention-driven, often retail, buying that pushes prices temporarily above fundamental value. Because liquidity providers demand compensation for absorbing these uninformed demand shocks, high volume-shock stocks subsequently underperform as the price impact decays. This is a liquidity-provision premium distinct from raw size or turnover.

best config: decay=0, transform=rank, cap_filter=0.3, windows=[60, 60], params={}

- **decision**: abandon
- **reasoning**: The hypothesis predicts a short-horizon reversal with IC around -0.02, but the realized Pearson IC is essentially zero (-0.0) and rank IC is NaN, so there is no measurable cross-sectional signal. The full-universe Sharpe of 0.50 is driven by a handful of crisis/rebound years (2001, 2003, 2009, 2013, 2022) while 2002, 2008, 2015-2016, 2019-2020 all lost money, and out-of-sample Sharpe (0.65) collapses to 0.36 in holdout with 2025 negative. Turnover of ~11.6x annualized with a -41% max drawdown and 46.7% hit rate suggests the small edge is noise, not a liquidity-provision premium.
- **diagnosis**: No real cross-sectional predictive signal (IC ~0); returns are regime-driven noise concentrated in a few rebound years, with high turnover and large drawdowns. The 5d/60d dollar-volume shock ratio does not isolate transient attention demand as claimed.
- **spec**: `-rank(ts_mean(amount, 5) / ts_mean(amount, 60))`
- **sub-universe** (rank(cap) > 0.3, reference only): sharpe 0.50, return 7.8%/yr, turnover 11.6, maxDD -41.1%, RankIC - — identical to the primary book because the best config already drops the same names
- **in-sample**: sharpe 0.50, return 8.1%/yr, turnover 11.3, maxDD -41.1%, RankIC -  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe 0.65, return 8.0%/yr, turnover 14.1, maxDD -16.4%, RankIC -  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe 0.36, return 4.0%/yr, turnover 10.2, maxDD -12.9%, RankIC -  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2000 | -0.3% | 0.08 | 22.7 | -17.4% | - |
| 2001 | 31.4% | 1.41 | 6.4 | -16.8% | - |
| 2002 | -23.8% | -0.91 | 3.4 | -37.4% | - |
| 2003 | 35.7% | 1.85 | 0.9 | -14.0% | - |
| 2004 | 16.9% | 1.40 | 5.8 | -7.9% | - |
| 2005 | 15.7% | 1.39 | 1.7 | -7.2% | - |
| 2006 | 14.5% | 1.32 | 4.7 | -8.2% | - |
| 2007 | 17.4% | 1.12 | 6.7 | -8.1% | - |
| 2008 | -26.9% | -0.64 | 29.0 | -36.4% | - |
| 2009 | 52.7% | 1.61 | 6.8 | -23.9% | - |
| 2010 | 17.4% | 0.94 | 5.3 | -15.6% | - |
| 2011 | -3.6% | -0.02 | 3.0 | -21.1% | - |
| 2012 | 16.3% | 1.22 | 1.8 | -10.5% | - |
| 2013 | 34.5% | 2.62 | 1.0 | -5.7% | - |
| 2014 | 14.5% | 1.21 | 2.9 | -7.7% | - |
| 2015 | -1.5% | -0.03 | 18.0 | -11.7% | - |
| 2016 | -4.0% | -0.26 | 17.8 | -16.6% | - |
| 2017 | 6.4% | 1.11 | 18.0 | -4.2% | - |
| 2018 | 14.1% | 0.98 | 27.3 | -10.5% | - |
| 2019 | -2.9% | -0.25 | 33.4 | -12.3% | - |
| 2020 | -17.5% | -0.43 | 20.4 | -25.6% | - |
| 2021 | 0.7% | 0.12 | 15.8 | -8.9% | - |
| 2022 | 41.6% | 1.91 | 13.7 | -8.8% | - |
| 2023 | -8.4% | -0.77 | 16.4 | -16.1% | - |
| 2024 | 4.2% | 0.50 | 10.6 | -7.5% | - |
| 2025 | -3.2% | -0.14 | 8.8 | -12.9% | - |
| 2026 | 10.6% | 1.28 | 12.0 | -5.6% | - |

holdout by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2025 | -3.2% | -0.14 | 8.8 | -12.9% | - |
| 2026 | 10.6% | 1.28 | 12.0 | -5.6% | - |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2021 | 0.7% | 0.12 | 15.8 | -8.9% | - |
| 2022 | 41.6% | 1.91 | 13.7 | -8.8% | - |
| 2023 | -8.4% | -0.77 | 16.4 | -16.1% | - |
| 2024 | 4.2% | 0.50 | 10.6 | -7.5% | - |

## overnight_gap_fade

**hypothesis**: Stocks with the largest positive overnight gaps (top of cross-sectional distribution) over the past 5 days underperform over the next 5 trading days, and stocks with the largest negative gaps outperform.

**economic rationale**: Large single-day overnight gaps are frequently driven by liquidity imbalances and news overreaction that are partially corrected during the following session and subsequent days. Because overnight gaps occur when markets are thin, the price impact overshoots fair value, and informed intraday traders profit by fading the gap. This pays a premium for providing liquidity against uninformed overnight order flow.

best config: decay=60, transform=none, cap_filter=0.3, windows=[5], params={}

- **decision**: abandon
- **reasoning**: The economic story (overnight gap fade) is coherent, but the evidence does not support it: the full-universe rank IC is essentially zero (0.0018, IC_IR 0.013) across the entire sample, and the holdout IC collapses to -0.0 while the holdout Sharpe falls to 0.32 with a -17% drawdown. The in-sample Sharpe of 0.73 is driven by a handful of crisis years (2001, 2002, 2008) and is not stable — 2005, 2007, 2012, 2013, 2015 are all negative, and the effect steadily decays from IS (0.73) to OOS (0.57) to holdout (0.32). With near-zero IC and no surviving edge out of sample, this is noise, not a liquidity-provision premium.
- **diagnosis**: Signal is essentially absent (IC ~0.002, IR ~0.01) and decays to zero in holdout; the modest Sharpe is a regime artifact concentrated in crisis years, not a persistent overnight-gap reversal effect.
- **spec**: `-rank(ts_sum(overnight_return, 5))`
- **sub-universe** (rank(cap) > 0.3, reference only): sharpe 0.65, return 3.6%/yr, turnover 12.2, maxDD -17.0%, RankIC 0.002 — identical to the primary book because the best config already drops the same names
- **in-sample**: sharpe 0.73, return 3.7%/yr, turnover 11.9, maxDD -11.8%, RankIC 0.002  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe 0.57, return 3.2%/yr, turnover 13.4, maxDD -5.5%, RankIC 0.002  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe 0.32, return 2.6%/yr, turnover 13.4, maxDD -17.0%, RankIC -0.000  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2000 | 11.3% | 1.39 | 8.6 | -6.2% | 0.011 |
| 2001 | 13.8% | 1.80 | 10.7 | -5.8% | 0.004 |
| 2002 | 11.7% | 2.12 | 11.8 | -2.7% | 0.011 |
| 2003 | 4.7% | 1.49 | 11.9 | -1.8% | 0.006 |
| 2004 | 2.6% | 0.79 | 10.1 | -1.7% | -0.002 |
| 2005 | -3.9% | -1.03 | 9.8 | -6.7% | -0.018 |
| 2006 | 3.8% | 1.09 | 10.4 | -2.8% | 0.007 |
| 2007 | -4.2% | -1.37 | 11.9 | -5.3% | -0.006 |
| 2008 | 23.4% | 2.33 | 12.0 | -4.2% | 0.007 |
| 2009 | 5.4% | 1.04 | 11.7 | -2.3% | 0.007 |
| 2010 | 2.1% | 0.70 | 11.7 | -2.0% | 0.010 |
| 2011 | 5.2% | 1.42 | 12.4 | -2.7% | 0.010 |
| 2012 | -2.3% | -0.78 | 13.2 | -3.8% | -0.005 |
| 2013 | -2.2% | -1.12 | 13.0 | -3.5% | -0.004 |
| 2014 | -0.1% | -0.01 | 12.2 | -5.1% | 0.001 |
| 2015 | -2.9% | -0.62 | 12.0 | -4.7% | -0.008 |
| 2016 | 5.5% | 1.35 | 14.2 | -2.8% | 0.011 |
| 2017 | 1.3% | 0.35 | 13.0 | -4.2% | -0.003 |
| 2018 | 4.5% | 1.26 | 13.1 | -1.7% | 0.008 |
| 2019 | 2.6% | 0.71 | 13.6 | -2.5% | 0.001 |
| 2020 | 0.1% | 0.06 | 12.8 | -11.0% | -0.005 |
| 2021 | 7.1% | 1.28 | 13.2 | -3.1% | 0.010 |
| 2022 | 5.5% | 0.81 | 13.6 | -4.8% | 0.003 |
| 2023 | 1.6% | 0.36 | 13.9 | -4.8% | 0.000 |
| 2024 | -1.2% | -0.17 | 13.0 | -5.4% | -0.008 |
| 2025 | 7.0% | 0.91 | 13.6 | -6.1% | 0.002 |
| 2026 | -2.4% | -0.25 | 13.1 | -12.5% | -0.003 |

holdout by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2025 | 7.0% | 0.91 | 13.6 | -6.1% | 0.002 |
| 2026 | -2.4% | -0.25 | 13.1 | -12.5% | -0.003 |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2021 | 7.1% | 1.28 | 13.2 | -3.1% | 0.010 |
| 2022 | 5.5% | 0.81 | 13.6 | -4.8% | 0.003 |
| 2023 | 1.6% | 0.36 | 13.9 | -4.8% | 0.000 |
| 2024 | -1.2% | -0.17 | 13.0 | -5.4% | -0.008 |

## intraday_momentum_continuation

**hypothesis**: Stocks with high cumulative intraday_return over the past 20 days outperform over the next 20 trading days.

**economic rationale**: Intraday returns reflect trading under full liquidity and information, so persistent intraday gains signal genuine informed accumulation rather than noise. Institutional buyers who work orders during the session leave a footprint of positive intraday drift that tends to continue as their remaining demand is filled over subsequent days. This is a slow-moving informed-flow premium.

best config: decay=60, transform=sign, cap_filter=none, windows=[20], params={}

- **decision**: abandon
- **reasoning**: The factor has essentially no cross-sectional discriminating power: best rank_ic is 0.0003 and pearson_ic is ~0.0, so the 'informed flow' signal is not actually present in the data. The headline Sharpe of 0.60 comes entirely from the grid choosing transform=sign with decay=60, which collapses the factor to a near-binary directional bet rather than the continuous intraday-momentum ranking the hypothesis predicts, and the sub-universe Sharpe is negative (-0.11), meaning any edge lives in small illiquid names. Only 16.7% of grid configs had positive Sharpe and just 1.4% exceeded 0.5, so the result is a selection artifact, not a robust premium. The OOS/holdout Sharpe (0.82/1.28) is not credible given a near-zero IC and a sign-based implementation, and the holdout IC actually turns negative.
- **diagnosis**: Near-zero IC indicates the intraday-return signal does not predict cross-sectional returns; the apparent Sharpe is a sign-transform/decode artifact and small-cap exposure, not a genuine informed-flow premium.
- **spec**: `rank(ts_sum(intraday_return, 20))`
- **sub-universe** (rank(cap) > 0.3, reference only): sharpe -0.11, return -0.9%/yr, turnover 7.9, maxDD -41.0%, RankIC 0.002
- **in-sample**: sharpe 0.51, return 4.5%/yr, turnover 8.3, maxDD -29.8%, RankIC 0.001  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe 0.82, return 7.3%/yr, turnover 8.3, maxDD -13.6%, RankIC 0.001  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe 1.28, return 11.2%/yr, turnover 8.3, maxDD -5.5%, RankIC -0.005  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2000 | 15.4% | 1.79 | 7.0 | -4.2% | 0.006 |
| 2001 | 0.3% | 0.08 | 8.9 | -12.3% | -0.004 |
| 2002 | -3.4% | -0.21 | 8.2 | -15.0% | -0.001 |
| 2003 | 4.7% | 0.54 | 7.5 | -7.5% | -0.005 |
| 2004 | 9.1% | 1.12 | 7.5 | -5.2% | 0.004 |
| 2005 | -0.2% | 0.01 | 8.2 | -7.8% | -0.001 |
| 2006 | 6.5% | 1.30 | 8.4 | -3.8% | 0.007 |
| 2007 | -0.2% | 0.01 | 9.0 | -6.5% | 0.005 |
| 2008 | -15.8% | -0.78 | 8.4 | -26.8% | -0.001 |
| 2009 | 17.9% | 1.23 | 8.8 | -14.4% | -0.001 |
| 2010 | 7.7% | 0.93 | 7.8 | -5.3% | -0.003 |
| 2011 | 8.8% | 0.89 | 8.1 | -6.2% | 0.008 |
| 2012 | 7.8% | 1.23 | 8.4 | -5.1% | 0.000 |
| 2013 | 3.9% | 0.69 | 8.0 | -5.5% | -0.002 |
| 2014 | 10.1% | 1.85 | 8.5 | -3.3% | 0.005 |
| 2015 | -1.6% | -0.20 | 9.0 | -6.4% | 0.001 |
| 2016 | 6.7% | 0.99 | 8.8 | -4.0% | -0.002 |
| 2017 | 7.0% | 1.77 | 8.5 | -1.8% | 0.000 |
| 2018 | -4.0% | -0.42 | 7.8 | -9.0% | 0.000 |
| 2019 | 11.0% | 1.81 | 9.0 | -3.9% | 0.004 |
| 2020 | 7.9% | 0.59 | 8.0 | -15.3% | -0.008 |
| 2021 | 14.8% | 1.93 | 8.5 | -5.2% | 0.001 |
| 2022 | 8.4% | 0.86 | 8.2 | -6.2% | -0.000 |
| 2023 | -3.2% | -0.27 | 8.4 | -13.6% | -0.004 |
| 2024 | 9.9% | 1.21 | 8.1 | -4.8% | 0.006 |
| 2025 | 18.2% | 2.00 | 7.8 | -3.5% | -0.003 |
| 2026 | 1.6% | 0.30 | 8.9 | -5.5% | -0.007 |

holdout by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2025 | 18.2% | 2.00 | 7.8 | -3.5% | -0.003 |
| 2026 | 1.6% | 0.30 | 8.9 | -5.5% | -0.007 |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | RankIC |
|---|---|---|---|---|---|
| 2021 | 14.8% | 1.93 | 8.5 | -5.2% | 0.001 |
| 2022 | 8.4% | 0.86 | 8.2 | -6.2% | -0.000 |
| 2023 | -3.2% | -0.27 | 8.4 | -13.6% | -0.004 |
| 2024 | 9.9% | 1.21 | 8.1 | -4.8% | 0.006 |
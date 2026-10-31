# Factor mining run

- run id: `20261030-165618-llm-real`
- data: 6726 days x 1195 names, 2000-01-03 -> 2026-09-30
- LLM: `openai-compatible`
- hypotheses: 1, factors added: 0
- sample split: date-based: IS to 2020-12-31, OOS from 2021-01-01, OOS to 2024-12-31, holdout from 2025-01-01
  - in-sample ['2000-01-03', '2020-12-31'] (5284 days) / out-of-sample ['2021-01-04', '2024-12-31'] (1005 days) / holdout ['2025-01-02', '2026-09-30'] (437 days)

## Hypotheses and decisions

| hypothesis | attempt | decision | sharpe all | ann return | turnover | maxDD | IC | factor | sharpe IS | sharpe OOS | sharpe Holdout |
|---|---|---|---|---|---|---|---|---|---|---|---|
| intraday_range_position_reversal | 1 | abandon | 2.08 | 11.2% | 94.6 | -7.6% | 0.021 | - | 2.62 | 0.37 | 0.26 |

## intraday_range_position_reversal

**hypothesis**: Stocks whose close sits near the top of their daily high-low range underperform stocks whose close sits near the bottom of their range over the next 5 trading days; the cross-sectional rank IC of (close-low)/(high-low) is negative.

**economic rationale**: The close's position within the day's high-low range is a proxy for order-flow imbalance and short-horizon price pressure. Stocks closing near their high have absorbed aggressive buying that tends to reverse over the next few days as liquidity providers and short-term traders unwind, while stocks closing near their low have absorbed selling that mean-reverts upward. The premium is compensation for supplying liquidity to impatient demanders at the close, and it is strongest where the close-to-range extreme reflects transient pressure rather than news (which we cannot see, so we rely on cross-sectional averaging).

best config: decay=5, transform=rank, cap_filter=0.3, windows=[], params={}

- **decision**: abandon
- **reasoning**: The factor shows a strong in-sample Sharpe of 2.62 (IC 0.025) but collapses to Sharpe 0.37 (IC 0.005) out-of-sample and 0.26 (IC 0.003) in the holdout, with hit rates near 50%. The edge is concentrated in 2000-2009 and decays monotonically, consistent with the intraday-range reversal premium being arbitraged away. Both untouched segments fail to confirm the mechanism, so this is overfit to the early sample.
- **diagnosis**: Signal decays to noise after 2020; the in-sample Sharpe was driven by the 2000-2009 regime (Sharpe 3-6), and the mechanism no longer produces a tradable edge in OOS/holdout despite stable turnover. Sign is correct but magnitude of premium has vanished.
- **spec**: `-rank((close - low) / max(high - low, 1e-9))`
- **in-sample**: sharpe 2.62, return 14.0%/yr, turnover 94.1, maxDD -6.7%, IC 0.025  (2000-01-03 .. 2020-12-31)
- **out-of-sample**: sharpe 0.37, return 1.8%/yr, turnover 96.5, maxDD -5.4%, IC 0.005  (2021-01-04 .. 2024-12-31)
- **holdout**: sharpe 0.26, return 1.4%/yr, turnover 96.8, maxDD -7.6%, IC 0.003  (2025-01-02 .. 2026-09-30)

| year | return | sharpe | turnover | maxDD | IC |
|---|---|---|---|---|---|
| 2000 | 50.9% | 4.46 | 91.5 | -3.0% | 0.051 |
| 2001 | 35.6% | 3.30 | 91.3 | -5.0% | 0.046 |
| 2002 | 34.9% | 5.40 | 94.9 | -1.5% | 0.049 |
| 2003 | 22.2% | 6.01 | 91.7 | -1.1% | 0.042 |
| 2004 | 14.9% | 5.07 | 91.8 | -0.7% | 0.035 |
| 2005 | 9.7% | 3.63 | 93.8 | -1.1% | 0.030 |
| 2006 | 14.4% | 4.85 | 94.1 | -1.1% | 0.038 |
| 2007 | 9.9% | 3.10 | 94.8 | -1.7% | 0.022 |
| 2008 | 26.2% | 2.97 | 96.9 | -6.0% | 0.030 |
| 2009 | 22.8% | 3.16 | 93.5 | -3.0% | 0.030 |
| 2010 | 5.0% | 1.85 | 90.8 | -1.1% | 0.010 |
| 2011 | 7.0% | 1.78 | 94.1 | -3.5% | 0.016 |
| 2012 | 5.6% | 2.19 | 93.2 | -1.4% | 0.013 |
| 2013 | 5.6% | 2.97 | 93.0 | -1.4% | 0.014 |
| 2014 | 1.7% | 0.69 | 94.7 | -2.1% | 0.016 |
| 2015 | 5.1% | 1.73 | 95.3 | -2.6% | 0.012 |
| 2016 | 2.1% | 0.59 | 95.4 | -2.9% | 0.009 |
| 2017 | 1.8% | 0.67 | 94.2 | -1.8% | 0.006 |
| 2018 | 2.5% | 0.72 | 95.6 | -3.4% | 0.006 |
| 2019 | 7.6% | 2.13 | 96.0 | -2.5% | 0.028 |
| 2020 | 21.3% | 2.28 | 98.4 | -6.7% | 0.029 |
| 2021 | 1.2% | 0.25 | 96.7 | -3.0% | 0.003 |
| 2022 | 2.1% | 0.36 | 96.1 | -4.1% | 0.002 |
| 2023 | 0.6% | 0.18 | 97.7 | -3.7% | 0.002 |
| 2024 | 3.2% | 0.73 | 95.7 | -3.8% | 0.014 |
| 2025 | 2.2% | 0.44 | 97.2 | -2.9% | 0.001 |
| 2026 | 0.3% | 0.10 | 96.3 | -7.6% | 0.006 |

holdout by year:

| year | return | sharpe | turnover | maxDD | IC |
|---|---|---|---|---|---|
| 2025 | 2.2% | 0.44 | 97.2 | -2.9% | 0.001 |
| 2026 | 0.3% | 0.10 | 96.3 | -7.6% | 0.006 |

out-of-sample by year:

| year | return | sharpe | turnover | maxDD | IC |
|---|---|---|---|---|---|
| 2021 | 1.2% | 0.25 | 96.7 | -3.0% | 0.003 |
| 2022 | 2.1% | 0.36 | 96.1 | -4.1% | 0.002 |
| 2023 | 0.6% | 0.18 | 97.7 | -3.7% | 0.002 |
| 2024 | 3.2% | 0.73 | 95.7 | -3.8% | 0.014 |
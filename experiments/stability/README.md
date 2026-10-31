# Stability checks

Same signal, different implementation knobs. `*_range` is the min..max Sharpe
across that group of variants; a wide range or a large drop in `min_pnl_corr`
means the result depends on the exact configuration rather than the mechanism.

| factor | run | sharpe | subuniverse | decay_range | transform_range | window_range | min_pnl_corr | max_turnover |
|---|---|---|---|---|---|---|---|---|
| volume_price_divergence | 20261031-095220-batch10 | 1.053 | 1.053 | 0.56..0.97 | 1.02..1.04 | 0.10..1.01 | 0.2759 | 63.06 |
| overnight_intraday_reversal | 20261031-095220-batch10 | 0.7498 | 0.7498 | 0.18..0.54 | 0.10..0.69 | 0.07..0.71 | 0.3372 | 46.86 |
| overnight_gap_fade | 20261031-101653-batch10c | 0.6517 | 0.6517 | 0.34..0.53 | 0.16..0.58 | 0.08..0.58 | 0.323 | 66.47 |
| intraday_momentum_continuation | 20261031-101653-batch10c | 0.6007 | -0.1082 | 0.15..0.22 | -0.09..-0.09 | 0.34..0.54 | -0.2763 | 24.28 |
| close_position_persistence | 20261031-101653-batch10c | 0.5112 | -0.1174 | 0.14..0.20 | -0.15..-0.15 | 0.34..0.55 | -0.3148 | 24.2 |
| overnight_intraday_reversal | 20261031-101653-batch10c | 0.3962 | 0.3962 | -0.05..0.30 | 0.06..0.33 | 0.05..0.45 | -0.002322 | 25.1 |
| illiquidity_shock_reversal | 20261031-095220-batch10 | 0.2905 | 0.2164 | 0.03..0.21 | -0.01..0.22 | -0.49..0.28 | 0.2456 | 103.2 |
| range_contraction_breakout | 20261031-101653-batch10c | 0.06519 | 0.06519 | -0.02..0.01 | 0.05..0.06 | -0.07..0.10 | -0.59 | 15.99 |
| range_compression_breakout | 20261031-095220-batch10 | -0.0515 | -0.0515 | -0.81..-0.18 | -0.36..-0.31 | -0.37..0.12 | 0.6383 | 27.47 |
| dollar_volume_shock_reversal | 20261031-101653-batch10c | - | - | -0.22..-0.07 | nan..nan | -0.07..0.07 | - | 66.99 |

Per-factor details live in the sub-directories (`metrics.csv`, `pnl.png`, `README.md`).
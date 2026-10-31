# Batch `p100`

- attempts: **100** across 27 sessions
- decisions: {'abandon': 100}
- accepted: 0
- with stability flags: 86

Selection uses in-sample (2000–2020) only; OOS is 2021–2024 and the 2025+
holdout has been inspected repeatedly. Costs are zero. The capital filter is
a grid dimension, so the sub-universe book can coincide with the primary one.

| hypothesis | decision | sharpe_full | sharpe_oos | sharpe_holdout | sharpe_sub | stability_flags |
|---|---|---|---|---|---|---|
| range_to_adv_illiquidity_premium | abandon | 0.595 | 1.157 | 1.283 | -0.126 | subuniverse_flips_sign,variant_pnl_decorrelates |
| intraday_range_to_adv_liquidity | abandon | 0.595 | 1.157 | 1.283 | -0.126 | subuniverse_flips_sign,variant_pnl_decorrelates |
| range_to_close_volatility_ratio | abandon | 1.066 | 1.01 | 0.59 | 1.066 | variant_pnl_decorrelates |
| overnight_return_dispersion_20d | abandon | 0.626 | 0.93 | 0.14 | -0.18 | subuniverse_flips_sign,variant_pnl_decorrelates |
| intraday_volatility_to_overnight_volatility_ratio | abandon | 0.626 | 0.93 | 0.14 | -0.18 | subuniverse_flips_sign,variant_pnl_decorrelates |
| volume_weighted_close_location | abandon | 0.486 | 0.825 | 0.28 | -0.08 | subuniverse_flips_sign,variant_pnl_decorrelates |
| close_position_weakness_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| intraday_close_position_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| intraday_close_location_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| close_position_trend_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| close_position_trend_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| close_location_trend_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| intraday_close_strength_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| intraday_momentum_vs_overnight_noise | abandon | 0.601 | 0.825 | 1.282 | -0.108 | subuniverse_flips_sign,variant_pnl_decorrelates |
| close_location_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| intraday_return_5d_momentum | abandon | 0.601 | 0.825 | 1.282 | -0.108 | subuniverse_flips_sign,variant_pnl_decorrelates |
| close_location_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| close_location_persistence | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| close_location_persistence_momentum | abandon | 0.511 | 0.825 | 1.282 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| overnight_return_persistence_20d | abandon | 0.636 | 0.825 | 1.334 | -0.099 | subuniverse_flips_sign,variant_pnl_decorrelates |
| intraday_return_autocorrelation_20d | abandon | 0.642 | 0.825 | 1.334 | -0.099 | subuniverse_flips_sign,variant_pnl_decorrelates |
| range_to_overnight_gap_ratio_20d | abandon | 0.636 | 0.825 | 1.334 | -0.099 | subuniverse_flips_sign,variant_pnl_decorrelates |
| overnight_intraday_return_divergence | abandon | 0.636 | 0.825 | 1.334 | -0.099 | subuniverse_flips_sign,variant_pnl_decorrelates |
| overnight_intraday_flow_drift | abandon | 0.636 | 0.825 | 1.334 | -0.099 | subuniverse_flips_sign,variant_pnl_decorrelates |
| intraday_momentum_overnight_reversal | abandon | 0.636 | 0.825 | 1.334 | -0.099 | subuniverse_flips_sign,variant_pnl_decorrelates |
| volume_weighted_overnight_gap_reversal | abandon | 0.557 | 0.791 | 0.041 | 0.557 | variant_pnl_decorrelates |
| range_position_momentum_consistency | abandon | 0.604 | 0.719 | 0.878 | -0.124 | subuniverse_flips_sign,variant_pnl_decorrelates |
| amount_concentration_20d | abandon | 0.312 | 0.662 | 0.672 | 0.312 | window_span_crosses_zero |
| amount_concentration_reversal | abandon | 0.303 | 0.66 | 0.681 | 0.304 | window_span_crosses_zero,variant_pnl_decorrelates |
| overnight_gap_absorption_ratio | abandon | 0.757 | 0.649 | 0.664 | 0.757 |  |
| range_contraction_breakout | abandon | 0.855 | 0.602 | -0.182 | 0.675 | window_span_crosses_zero,variant_pnl_decorrelates |
| intraday_vs_overnight_volume_imbalance | abandon | 0.499 | 0.588 | 0.433 | 0.499 | window_span_crosses_zero,variant_pnl_decorrelates |
| overnight_gap_fade_residual | abandon | 0.652 | 0.572 | 0.322 | 0.652 |  |
| illiquidity_premium_cap_adv | abandon | 0.498 | 0.559 | 0.348 | -0.117 | subuniverse_flips_sign,variant_pnl_decorrelates |
| range_compression_breakout | abandon | 0.423 | 0.512 | 0.381 | -0.072 | subuniverse_flips_sign,variant_pnl_decorrelates |
| close_location_persistence_5d | abandon | 0.395 | 0.469 | 0.559 | -0.188 | subuniverse_flips_sign,variant_pnl_decorrelates |
| overnight_intraday_reversal | abandon | 0.63 | 0.454 | 0.587 | 0.63 | variant_pnl_decorrelates |
| overnight_return_volatility_ratio | abandon | 0.241 | 0.44 | 1.419 | 0.241 |  |
| overnight_gap_absorption | abandon | 0.445 | 0.431 | 0.381 | -0.156 | subuniverse_flips_sign,variant_pnl_decorrelates |
| overnight_to_full_return_ratio_reversal_20d | abandon | 0.509 | 0.382 | -0.136 | 0.509 | window_span_crosses_zero,variant_pnl_decorrelates |

Full table: `summary.csv` (100 rows).
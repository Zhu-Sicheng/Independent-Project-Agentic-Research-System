# Published results: `systemv1-50h`

- runs: `sysv1-h1`, `sysv1-h2`, `sysv1-h3`, `sysv1-h4`, `sysv1-h5`, `sysv1-h6`, `sysv1-h7`
- evaluated expressions: 53 (51 unique canonical forms)
- data isolation: the optimisation loop and the reviewer saw in-sample only; OOS/holdout are display-only and were never fed back

## Summary

| run_id | expression | sharpe_is | turnover_is | rank_ic_is | sharpe_oos | sharpe_holdout | decision |
|---|---|---|---|---|---|---|---|
| sysv1-h2 | -1 * ts_mean(safe_div(close - low, high - low), 10) | 1.683 | 53.74 | 0.01493 | 0.1214 | -0.4495 | optimize |
| sysv1-h3 | -1 * ts_zscore(ts_returns(close, 5), 60) + -1 * safe_div(ts_mean(returns, 5), ts_std_dev(returns, 60)) | 1.079 | 80.91 | 0.01426 | -0.1123 | 0.4345 | optimize |
| sysv1-h5 | -1 * safe_div(ts_returns(close, 1), ts_std_dev(ts_returns(close, 1), 20)) | 0.9586 | 167.3 | 0.01703 | 0.7883 | 0.2251 | abandon |
| sysv1-h6 | -1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | 0.9511 | 70.21 | 0.01528 | 0.0769 | 0.4368 | optimize |
| sysv1-h7 | -( -(safe_div(ts_mean(volume, 5), ts_mean(volume, 60))) * -(ts_delta(close, 5) / close) ) | 0.9474 | 70.2 | 0.01524 | 0.0776 | 0.4417 | optimize |
| sysv1-h4 | -1 * ts_returns(close, 5, 1) | 0.9428 | 72.49 | 0.01584 | 0.1878 | 0.5439 | optimize |
| sysv1-h2 | -1 * ts_mean(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5) | 0.7446 | 61.94 | 0.002081 | 0.7533 | 1.065 | abandon |
| sysv1-h2 | -1 * ts_mean(cap, 21) | 0.6755 | 0.4298 | -1.33e-04 | -0.388 | -0.632 | abandon |
| sysv1-h4 | -1 * ts_mean(cap, 21) | 0.6755 | 0.4298 | -1.33e-04 | -0.388 | -0.632 | abandon |
| sysv1-h7 | -(safe_div(ts_delta(cap, 60), cap) * close) | 0.6362 | 19.31 | 0.00206 | 0.569 | 0.1201 | abandon |
| sysv1-h4 | -1 * (ts_mean(ts_returns(close, 1, 1) * ts_returns(close, 1, 1) * ts_returns(close, 1, 1), 63) / ts_mean(cap, 63)) | 0.5924 | 12.29 | 0.007301 | 0.2054 | -0.4987 | abandon |
| sysv1-h6 | -1 * safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120)) | 0.5717 | 21.25 | -8.34e-04 | 0.191 | 0.316 | abandon |
| sysv1-h5 | -1 * (ts_returns(cap, 60) - ts_returns(close, 60)) | 0.5386 | 11.22 | 0.002669 | 1.091 | 0.002012 | abandon |
| sysv1-h2 | safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | 0.5062 | 39.17 | 0.001843 | 0.1765 | 0.8889 | abandon |
| sysv1-h2 | -1 * safe_div(close - ts_mean(close, 120), ts_mean(close, 120)) | 0.4093 | 16.22 | -3.22e-04 | 0.2119 | 0.1418 | abandon |
| sysv1-h6 | -1 * safe_div(ts_std_dev(safe_div(high - low, close), 5), ts_std_dev(safe_div(high - low, close), 60)) | 0.3207 | 64.37 | 0.002734 | 0.5526 | -0.7621 | abandon |
| sysv1-h1 | -(ts_delta(safe_div(ts_std_dev(ts_returns(close, 1), 60), ts_std_dev(ts_returns(close, 1), 252)), 63)) | 0.2804 | 13.7 | 0.002419 | 0.2581 | -1.083 | abandon |
| sysv1-h2 | -1 * safe_div(ts_std_dev(ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 120)) | 0.2509 | 40.3 | 0.002792 | 0.4738 | -1.128 | abandon |
| sysv1-h4 | ts_returns(close, 231, 1) - ts_returns(close, 21, 1) | 0.23 | 13.39 | 0.01374 | 0.1758 | 1.046 | abandon |
| sysv1-h7 | -(safe_div(ts_mean(volume, 20) * close, cap)) | 0.2026 | 7.71 | 0.006841 | 0.2913 | -1.243 | abandon |
| sysv1-h5 | -1 * ts_mean(safe_div(ts_max(high, 10), close) * safe_div(ts_range(high, 10), ts_range(high, 60)) * safe_div(low, close), 10) | 0.2018 | 18.68 | 0.002714 | -0.3391 | 0.2141 | abandon |
| sysv1-h2 | -1 * ts_std_dev(ts_returns(close, 1), 63) | 0.1918 | 7.112 | 0.0124 | -0.07666 | -1.373 | abandon |
| sysv1-h4 | -1 * ts_std_dev(ts_returns(close, 1, 1), 63) | 0.1918 | 7.112 | 0.0124 | -0.07666 | -1.373 | abandon |
| sysv1-h7 | -ts_mean(high - low, 10) / ts_mean(close, 60) * ts_mean(volume, 5) / ts_mean(volume, 60) | 0.1644 | 33.26 | 0.007231 | 0.2376 | -1.182 | abandon |
| sysv1-h6 | -1 * ts_std_dev(ts_returns(close, 1), 120) | 0.16 | 4.798 | 0.01193 | -0.2571 | -1.339 | abandon |
| sysv1-h1 | -(safe_div(ts_std_dev(ts_returns(close, 1), 20), ts_std_dev(ts_returns(close, 1), 252))) | 0.1221 | 23.47 | 0.003654 | 0.0999 | -0.784 | abandon |
| sysv1-h1 | -(safe_div(ts_mean(safe_div(high - low, close), 20), ts_mean(safe_div(high - low, close), 120))) | 0.03906 | 24.09 | 0.002332 | 0.05391 | -0.1157 | abandon |
| sysv1-h2 | -1 * ts_mean(ts_returns(close, 1) * (safe_div(volume, ts_mean(volume, 60)) - 1), 20) | 0.01864 | 26.16 | 0.003562 | 0.4202 | -0.007583 | abandon |
| sysv1-h6 | safe_div(ts_delta(close, 231), ts_mean(close, 252)) | -0.01742 | 12.43 | 0.008903 | 0.01713 | 0.8048 | abandon |
| sysv1-h1 | -ts_mean(ts_returns(close, 1) * ts_zscore(volume, 60), 5) | -0.04132 | 64.55 | 5.49e-04 | -0.1597 | 0.3179 | abandon |
| sysv1-h4 | -1 * (ts_mean((high - low) / close, 21) / ts_mean((high - low) / close, 63)) | -0.04851 | 27.82 | 0.001182 | 0.0419 | 0.4545 | abandon |
| sysv1-h6 | -1 * safe_div(ts_mean(safe_div(volume, cap), 21), ts_mean(safe_div(volume, cap), 126)) | -0.1402 | 14.46 | 0.002162 | -0.008502 | 0.2104 | abandon |
| sysv1-h7 | ts_mean(( safe_div(close - safe_div(high + low, 2), high - low) ) * ( safe_div(close - open, abs(close - open)) ), 5) | -0.1743 | 79.3 | -0.00102 | 0.08556 | -0.03289 | abandon |
| sysv1-h1 | safe_div(ts_sum(ts_returns(close, 1), 210), ts_std_dev(ts_returns(close, 1), 210)) | -0.2186 | 12.5 | 0.007932 | 0.0219 | 0.4511 | abandon |
| sysv1-h3 | ts_bollinger_position(close, 252, 2.0) * (1 + ts_bollinger_width(close, 252, 2.0)) | -0.2395 | 13.12 | 0.004465 | 0.05583 | 0.452 | abandon |
| sysv1-h6 | safe_div(close - ts_mean(close, 200), ts_mean(close, 200)) | -0.2566 | 15.23 | 0.00215 | -0.1759 | 0.4815 | abandon |
| sysv1-h5 | ts_sum(ts_returns(close, 1), 10) / (ts_mean(ts_range(safe_div(high - low, low), 120) * low, 120)) | -0.274 | 52.68 | -0.008389 | -0.1056 | -0.03586 | abandon |
| sysv1-h4 | -1 * (ts_mean(volume / cap, 21) / ts_mean(volume / cap, 63)) | -0.3072 | 18.17 | -3.77e-04 | -0.1576 | 0.4457 | abandon |
| sysv1-h4 | -1 * (ts_mean(volume, 5) / ts_mean(volume, 63)) | -0.3259 | 44.33 | -0.00233 | 0.2082 | -0.8777 | abandon |
| sysv1-h1 | ts_mean(ts_returns(open, 1), 60) - ts_mean(ts_returns(close, 1) - ts_returns(open, 1), 60) | -0.339 | 47.8 | -4.91e-04 | -0.4049 | 0.2466 | abandon |
| sysv1-h5 | safe_div(ts_sum(ts_returns(close, 1), 120), ts_std_dev(ts_returns(close, 1), 120)) | -0.3487 | 16.26 | 0.003621 | -0.05972 | 0.004745 | abandon |
| sysv1-h6 | ts_returns(close, 20) * safe_div(ts_mean(volume, 20), ts_mean(volume, 120)) | -0.3978 | 36.92 | -0.007456 | -0.1368 | -0.09256 | abandon |
| sysv1-h1 | safe_div(close - ts_min(close, 252), ts_max(close, 252) - ts_min(close, 252)) | -0.4098 | 21.4 | 0.00295 | -0.1464 | 0.0585 | abandon |
| sysv1-h5 | ts_ir(ts_returns(close, 1) * (volume / ts_median(volume, 60)), 60) | -0.4585 | 16.87 | -0.002529 | -0.4146 | -0.184 | abandon |
| sysv1-h3 | safe_div(ts_mean(volume, 5), ts_median(volume, 252)) * safe_div(ts_returns(close, 5), abs(ts_returns(close, 5))) | -0.4808 | 70.87 | -0.006306 | 0.03069 | -0.2866 | abandon |
| sysv1-h3 | safe_div(ts_returns(close, 63), ts_std_dev(returns, 63)) | -0.533 | 21.55 | -0.001871 | -0.3909 | -0.2214 | abandon |
| sysv1-h5 | ts_ir(ts_returns(close, 1) * (volume / ts_median(volume, 20)), 20) | -0.5672 | 33.32 | -0.006501 | -0.307 | -0.2531 | abandon |
| sysv1-h3 | safe_div(ts_mean(returns, 21), ts_std_dev(returns, 21)) + ts_returns(close, 1) | -0.7242 | 43.36 | -0.008506 | -0.2513 | -0.5753 | abandon |
| sysv1-h4 | (close - ts_min(low, 63)) / (ts_max(high, 63) - ts_min(low, 63)) | -0.7599 | 33.78 | -0.004807 | -0.2944 | -0.2364 | abandon |
| sysv1-h7 | safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)) | -0.7723 | 34.59 | -0.005238 | -0.2578 | -0.2511 | abandon |
| sysv1-h5 | safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)) | -0.7723 | 34.59 | -0.005238 | -0.2578 | -0.2511 | abandon |
| sysv1-h4 | ts_returns(close, 5, 1) / ts_std_dev(ts_returns(close, 1, 1), 21) | -0.9429 | 72.37 | -0.01139 | -0.07277 | -0.568 | abandon |
| sysv1-h3 | ts_mean(safe_div(close - low, high - low), 20) | -1.083 | 35.63 | -0.007626 | -0.2523 | 0.261 | abandon |

## Figures (top by in-sample Sharpe)

| expression | run | figure |
|---|---|---|
| `-1 * ts_mean(safe_div(close - low, high - low), 10)` | `sysv1-h2` | `figures/rank01_sysv1-h2_1.png` |
| `-1 * ts_zscore(ts_returns(close, 5), 60) + -1 * safe_div(ts_mean(returns, 5), ts_std_dev(r` | `sysv1-h3` | `figures/rank02_sysv1-h3_2.png` |
| `-1 * safe_div(ts_returns(close, 1), ts_std_dev(ts_returns(close, 1), 20))` | `sysv1-h5` | `figures/rank03_sysv1-h5_3.png` |
| `-1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60))` | `sysv1-h6` | `figures/rank04_sysv1-h6_4.png` |
| `-( -(safe_div(ts_mean(volume, 5), ts_mean(volume, 60))) * -(ts_delta(close, 5) / close) )` | `sysv1-h7` | `figures/rank05_sysv1-h7_5.png` |
| `-1 * ts_returns(close, 5, 1)` | `sysv1-h4` | `figures/rank06_sysv1-h4_6.png` |
| `-1 * ts_mean(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5)` | `sysv1-h2` | `figures/rank07_sysv1-h2_7.png` |
| `-1 * ts_mean(cap, 21)` | `sysv1-h2` | `figures/rank08_sysv1-h2_8.png` |
| `-1 * ts_mean(cap, 21)` | `sysv1-h4` | `figures/rank09_sysv1-h4_9.png` |
| `-(safe_div(ts_delta(cap, 60), cap) * close)` | `sysv1-h7` | `figures/rank10_sysv1-h7_10.png` |
| `-1 * (ts_mean(ts_returns(close, 1, 1) * ts_returns(close, 1, 1) * ts_returns(close, 1, 1),` | `sysv1-h4` | `figures/rank11_sysv1-h4_11.png` |
| `-1 * safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120))` | `sysv1-h6` | `figures/rank12_sysv1-h6_12.png` |
| `-1 * (ts_returns(cap, 60) - ts_returns(close, 60))` | `sysv1-h5` | `figures/rank13_sysv1-h5_13.png` |
| `safe_div(ts_mean(volume, 5), ts_mean(volume, 60))` | `sysv1-h2` | `figures/rank14_sysv1-h2_14.png` |
| `-1 * safe_div(close - ts_mean(close, 120), ts_mean(close, 120))` | `sysv1-h2` | `figures/rank15_sysv1-h2_15.png` |
| `-1 * safe_div(ts_std_dev(safe_div(high - low, close), 5), ts_std_dev(safe_div(high - low, ` | `sysv1-h6` | `figures/rank16_sysv1-h6_16.png` |
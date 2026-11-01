# Published results: `systemv1_50`

- runs: `sysv1-h1`, `sysv1-h2`, `sysv1-h3`, `sysv1-h4`, `sysv1-h5`, `sysv1-h6`, `sysv1-h7`
- evaluated expressions: 53 (51 unique canonical forms)
- display figures: 53 (every evaluated expression unless --top is set)
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

## Figures

| rank | run | expression | IS | OOS | holdout | decision | figure |
|---|---|---|---|---|---|---|---|
| 1 | `sysv1-h2` | `-1 * ts_mean(safe_div(close - low, high - low), 10)` | 1.683 | 0.121 | -0.450 | optimize | `figures/rank001_sysv1-h2_expr_6a671f42de025b70689d.png` |
| 2 | `sysv1-h3` | `-1 * ts_zscore(ts_returns(close, 5), 60) + -1 * safe_div(ts_mean(returns, 5), ts` | 1.079 | -0.112 | 0.435 | optimize | `figures/rank002_sysv1-h3_expr_4d8ea71894c66541978e.png` |
| 3 | `sysv1-h5` | `-1 * safe_div(ts_returns(close, 1), ts_std_dev(ts_returns(close, 1), 20))` | 0.959 | 0.788 | 0.225 | abandon | `figures/rank003_sysv1-h5_expr_55c783b87cd7eaf458ce.png` |
| 4 | `sysv1-h6` | `-1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60))` | 0.951 | 0.077 | 0.437 | optimize | `figures/rank004_sysv1-h6_expr_248190f11442ff473b45.png` |
| 5 | `sysv1-h7` | `-( -(safe_div(ts_mean(volume, 5), ts_mean(volume, 60))) * -(ts_delta(close, 5) /` | 0.947 | 0.078 | 0.442 | optimize | `figures/rank005_sysv1-h7_expr_29f3976a7607441d7052.png` |
| 6 | `sysv1-h4` | `-1 * ts_returns(close, 5, 1)` | 0.943 | 0.188 | 0.544 | optimize | `figures/rank006_sysv1-h4_expr_8475b17af7e41c426202.png` |
| 7 | `sysv1-h2` | `-1 * ts_mean(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5)` | 0.745 | 0.753 | 1.065 | abandon | `figures/rank007_sysv1-h2_expr_f5c60a97a91af5c36dcd.png` |
| 8 | `sysv1-h2` | `-1 * ts_mean(cap, 21)` | 0.676 | -0.388 | -0.632 | abandon | `figures/rank008_sysv1-h2_expr_30c3b38734c5c617edb3.png` |
| 9 | `sysv1-h4` | `-1 * ts_mean(cap, 21)` | 0.676 | -0.388 | -0.632 | abandon | `figures/rank009_sysv1-h4_expr_30c3b38734c5c617edb3.png` |
| 10 | `sysv1-h7` | `-(safe_div(ts_delta(cap, 60), cap) * close)` | 0.636 | 0.569 | 0.120 | abandon | `figures/rank010_sysv1-h7_expr_90005e9107ded6b5dc19.png` |
| 11 | `sysv1-h4` | `-1 * (ts_mean(ts_returns(close, 1, 1) * ts_returns(close, 1, 1) * ts_returns(clo` | 0.592 | 0.205 | -0.499 | abandon | `figures/rank011_sysv1-h4_expr_68157494310c82e7a0f9.png` |
| 12 | `sysv1-h6` | `-1 * safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120))` | 0.572 | 0.191 | 0.316 | abandon | `figures/rank012_sysv1-h6_expr_52a91987ac50381c7a12.png` |
| 13 | `sysv1-h5` | `-1 * (ts_returns(cap, 60) - ts_returns(close, 60))` | 0.539 | 1.091 | 0.002 | abandon | `figures/rank013_sysv1-h5_expr_a836016830183e68d257.png` |
| 14 | `sysv1-h2` | `safe_div(ts_mean(volume, 5), ts_mean(volume, 60))` | 0.506 | 0.176 | 0.889 | abandon | `figures/rank014_sysv1-h2_expr_f87caff1de493ffc602c.png` |
| 15 | `sysv1-h2` | `-1 * safe_div(close - ts_mean(close, 120), ts_mean(close, 120))` | 0.409 | 0.212 | 0.142 | abandon | `figures/rank015_sysv1-h2_expr_410d59033c0867683025.png` |
| 16 | `sysv1-h6` | `-1 * safe_div(ts_std_dev(safe_div(high - low, close), 5), ts_std_dev(safe_div(hi` | 0.321 | 0.553 | -0.762 | abandon | `figures/rank016_sysv1-h6_expr_6396d68d928e483d12de.png` |
| 17 | `sysv1-h1` | `-(ts_delta(safe_div(ts_std_dev(ts_returns(close, 1), 60), ts_std_dev(ts_returns(` | 0.280 | 0.258 | -1.083 | abandon | `figures/rank017_sysv1-h1_expr_c470c52d49f3015f0950.png` |
| 18 | `sysv1-h2` | `-1 * safe_div(ts_std_dev(ts_returns(close, 1), 10), ts_std_dev(ts_returns(close,` | 0.251 | 0.474 | -1.128 | abandon | `figures/rank018_sysv1-h2_expr_4bfdd583a6727a39692e.png` |
| 19 | `sysv1-h4` | `ts_returns(close, 231, 1) - ts_returns(close, 21, 1)` | 0.230 | 0.176 | 1.046 | abandon | `figures/rank019_sysv1-h4_expr_d43a43e4d20d5f093930.png` |
| 20 | `sysv1-h7` | `-(safe_div(ts_mean(volume, 20) * close, cap))` | 0.203 | 0.291 | -1.243 | abandon | `figures/rank020_sysv1-h7_expr_bcc57e8e6d27d5582104.png` |
| 21 | `sysv1-h5` | `-1 * ts_mean(safe_div(ts_max(high, 10), close) * safe_div(ts_range(high, 10), ts` | 0.202 | -0.339 | 0.214 | abandon | `figures/rank021_sysv1-h5_expr_d3d50140cb4a529fa262.png` |
| 22 | `sysv1-h2` | `-1 * ts_std_dev(ts_returns(close, 1), 63)` | 0.192 | -0.077 | -1.373 | abandon | `figures/rank022_sysv1-h2_expr_f6bd6ac368dcb80dc177.png` |
| 23 | `sysv1-h4` | `-1 * ts_std_dev(ts_returns(close, 1, 1), 63)` | 0.192 | -0.077 | -1.373 | abandon | `figures/rank023_sysv1-h4_expr_f6bd6ac368dcb80dc177.png` |
| 24 | `sysv1-h7` | `-ts_mean(high - low, 10) / ts_mean(close, 60) * ts_mean(volume, 5) / ts_mean(vol` | 0.164 | 0.238 | -1.182 | abandon | `figures/rank024_sysv1-h7_expr_257fbfa5e1f4e8189047.png` |
| 25 | `sysv1-h6` | `-1 * ts_std_dev(ts_returns(close, 1), 120)` | 0.160 | -0.257 | -1.339 | abandon | `figures/rank025_sysv1-h6_expr_f2b5b5b6cf340cdb9f26.png` |
| 26 | `sysv1-h1` | `-(safe_div(ts_std_dev(ts_returns(close, 1), 20), ts_std_dev(ts_returns(close, 1)` | 0.122 | 0.100 | -0.784 | abandon | `figures/rank026_sysv1-h1_expr_9b07a46f7575e2c57129.png` |
| 27 | `sysv1-h1` | `-(safe_div(ts_mean(safe_div(high - low, close), 20), ts_mean(safe_div(high - low` | 0.039 | 0.054 | -0.116 | abandon | `figures/rank027_sysv1-h1_expr_a76eec433ad1789b55c5.png` |
| 28 | `sysv1-h2` | `-1 * ts_mean(ts_returns(close, 1) * (safe_div(volume, ts_mean(volume, 60)) - 1),` | 0.019 | 0.420 | -0.008 | abandon | `figures/rank028_sysv1-h2_expr_b478e3cb13da9301622e.png` |
| 29 | `sysv1-h6` | `safe_div(ts_delta(close, 231), ts_mean(close, 252))` | -0.017 | 0.017 | 0.805 | abandon | `figures/rank029_sysv1-h6_expr_f5b3118c93d772f933de.png` |
| 30 | `sysv1-h1` | `-ts_mean(ts_returns(close, 1) * ts_zscore(volume, 60), 5)` | -0.041 | -0.160 | 0.318 | abandon | `figures/rank030_sysv1-h1_expr_6943ba46c8ed4bc54853.png` |
| 31 | `sysv1-h4` | `-1 * (ts_mean((high - low) / close, 21) / ts_mean((high - low) / close, 63))` | -0.049 | 0.042 | 0.455 | abandon | `figures/rank031_sysv1-h4_expr_e9258c745a801e6e3454.png` |
| 32 | `sysv1-h6` | `-1 * safe_div(ts_mean(safe_div(volume, cap), 21), ts_mean(safe_div(volume, cap),` | -0.140 | -0.009 | 0.210 | abandon | `figures/rank032_sysv1-h6_expr_ab9f6e3170d776843bf3.png` |
| 33 | `sysv1-h7` | `ts_mean(( safe_div(close - safe_div(high + low, 2), high - low) ) * ( safe_div(c` | -0.174 | 0.086 | -0.033 | abandon | `figures/rank033_sysv1-h7_expr_a294131603521e43f315.png` |
| 34 | `sysv1-h1` | `safe_div(ts_sum(ts_returns(close, 1), 210), ts_std_dev(ts_returns(close, 1), 210` | -0.219 | 0.022 | 0.451 | abandon | `figures/rank034_sysv1-h1_expr_9b6abf9b3e15fe039127.png` |
| 35 | `sysv1-h3` | `ts_bollinger_position(close, 252, 2.0) * (1 + ts_bollinger_width(close, 252, 2.0` | -0.240 | 0.056 | 0.452 | abandon | `figures/rank035_sysv1-h3_expr_dcdbc4d75226922545ca.png` |
| 36 | `sysv1-h6` | `safe_div(close - ts_mean(close, 200), ts_mean(close, 200))` | -0.257 | -0.176 | 0.481 | abandon | `figures/rank036_sysv1-h6_expr_c53716fbad03a5eb1d61.png` |
| 37 | `sysv1-h5` | `ts_sum(ts_returns(close, 1), 10) / (ts_mean(ts_range(safe_div(high - low, low), ` | -0.274 | -0.106 | -0.036 | abandon | `figures/rank037_sysv1-h5_expr_1a53c6ab68b85973387e.png` |
| 38 | `sysv1-h4` | `-1 * (ts_mean(volume / cap, 21) / ts_mean(volume / cap, 63))` | -0.307 | -0.158 | 0.446 | abandon | `figures/rank038_sysv1-h4_expr_cdee0c858b6bd822f12f.png` |
| 39 | `sysv1-h4` | `-1 * (ts_mean(volume, 5) / ts_mean(volume, 63))` | -0.326 | 0.208 | -0.878 | abandon | `figures/rank039_sysv1-h4_expr_c2d03944c028fcedfda4.png` |
| 40 | `sysv1-h1` | `ts_mean(ts_returns(open, 1), 60) - ts_mean(ts_returns(close, 1) - ts_returns(ope` | -0.339 | -0.405 | 0.247 | abandon | `figures/rank040_sysv1-h1_expr_ccfc3239d95022ef946c.png` |
| 41 | `sysv1-h5` | `safe_div(ts_sum(ts_returns(close, 1), 120), ts_std_dev(ts_returns(close, 1), 120` | -0.349 | -0.060 | 0.005 | abandon | `figures/rank041_sysv1-h5_expr_2e29b94d54f782fb65ea.png` |
| 42 | `sysv1-h6` | `ts_returns(close, 20) * safe_div(ts_mean(volume, 20), ts_mean(volume, 120))` | -0.398 | -0.137 | -0.093 | abandon | `figures/rank042_sysv1-h6_expr_940b316d43e862b70b3b.png` |
| 43 | `sysv1-h1` | `safe_div(close - ts_min(close, 252), ts_max(close, 252) - ts_min(close, 252))` | -0.410 | -0.146 | 0.059 | abandon | `figures/rank043_sysv1-h1_expr_6b5ef147a9734bed5ea4.png` |
| 44 | `sysv1-h5` | `ts_ir(ts_returns(close, 1) * (volume / ts_median(volume, 60)), 60)` | -0.458 | -0.415 | -0.184 | abandon | `figures/rank044_sysv1-h5_expr_369d56a6bd0f915fc65a.png` |
| 45 | `sysv1-h3` | `safe_div(ts_mean(volume, 5), ts_median(volume, 252)) * safe_div(ts_returns(close` | -0.481 | 0.031 | -0.287 | abandon | `figures/rank045_sysv1-h3_expr_42f5cb12a5da4d29fa22.png` |
| 46 | `sysv1-h3` | `safe_div(ts_returns(close, 63), ts_std_dev(returns, 63))` | -0.533 | -0.391 | -0.221 | abandon | `figures/rank046_sysv1-h3_expr_cbc21111d42561e2045a.png` |
| 47 | `sysv1-h5` | `ts_ir(ts_returns(close, 1) * (volume / ts_median(volume, 20)), 20)` | -0.567 | -0.307 | -0.253 | abandon | `figures/rank047_sysv1-h5_expr_4c37e7ff29ea3f8188b6.png` |
| 48 | `sysv1-h3` | `safe_div(ts_mean(returns, 21), ts_std_dev(returns, 21)) + ts_returns(close, 1)` | -0.724 | -0.251 | -0.575 | abandon | `figures/rank048_sysv1-h3_expr_115e379fae3fb683da1e.png` |
| 49 | `sysv1-h4` | `(close - ts_min(low, 63)) / (ts_max(high, 63) - ts_min(low, 63))` | -0.760 | -0.294 | -0.236 | abandon | `figures/rank049_sysv1-h4_expr_6e18647dda1cdef6db8c.png` |
| 50 | `sysv1-h7` | `safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60))` | -0.772 | -0.258 | -0.251 | abandon | `figures/rank050_sysv1-h7_expr_23dfe8f217f8bd01b635.png` |
| 51 | `sysv1-h5` | `safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60))` | -0.772 | -0.258 | -0.251 | abandon | `figures/rank051_sysv1-h5_expr_23dfe8f217f8bd01b635.png` |
| 52 | `sysv1-h4` | `ts_returns(close, 5, 1) / ts_std_dev(ts_returns(close, 1, 1), 21)` | -0.943 | -0.073 | -0.568 | abandon | `figures/rank052_sysv1-h4_expr_d7c6d1eb2aced211c446.png` |
| 53 | `sysv1-h3` | `ts_mean(safe_div(close - low, high - low), 20)` | -1.083 | -0.252 | 0.261 | abandon | `figures/rank053_sysv1-h3_expr_d5bba96407c967f93e8c.png` |
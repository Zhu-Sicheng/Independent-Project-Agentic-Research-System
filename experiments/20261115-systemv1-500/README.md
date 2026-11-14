# Published results: `systemv1-500`

- runs: `s500-c1-r001`, `s500-c1-r002`, `s500-c1-r003`, `s500-c1-r004`, `s500-c1-r005`, `s500-c1-r006`, `s500-c1-r007`, `s500-c1-r008`, `s500-c1-r009`, `s500-c1-r010`, `s500-c2-r001`, `s500-c2-r002`, `s500-c2-r003`, `s500-c2-r004`, `s500-c2-r005`, `s500-c2-r006`, `s500-c2-r007`, `s500-c2-r008`, `s500-c3-r001`, `s500-c3-r003`, `s500-c3-r004`, `s500-c3-r005`, `s500-c3-r006`, `s500-c3-r007`, `s500-c3-r008`, `s500-c3-r009`, `s500-c3-r010`, `s500-c4-r001`, `s500-c4-r003`, `s500-c4-r004`, `s500-c4-r005`, `s500-c4-r006`, `s500-c4-r007`, `s500-c4-r008`, `s500-c4-r009`, `s500-c4-r010`, `s500-c5-r001`, `s500-c5-r002`, `s500-c5-r003`, `s500-c5-r004`, `s500-c5-r005`, `s500-c5-r006`, `s500-c5-r007`, `s500-c6-r001`, `s500-c6-r002`, `s500-c6-r003`, `s500-c7-r001`, `s500-c7-r002`, `s500-c7-r003`
- evaluated expressions: 503 (497 unique canonical forms)
- display figures: 60 (every evaluated expression unless --top is set)
- data isolation: the optimisation loop and the reviewer saw in-sample only; OOS/holdout are display-only and were never fed back

## Summary

| run_id | expression | sharpe_is | turnover_is | rank_ic_is | sharpe_oos | sharpe_holdout | decision |
|---|---|---|---|---|---|---|---|
| s500-c4-r009 | -(safe_div(close - low, high - low)) | 2.621 | 94.06 | 0.02533 | 0.3653 | 0.259 | optimize |
| s500-c2-r002 | -1 * ts_zscore(safe_div(close - low, high - low), 20) | 2.21 | 94.64 | 0.02042 | 0.15 | 0.6287 | accept |
| s500-c4-r009 | -(ts_mean(safe_div(close - low, high - low), 5)) | 2.059 | 77.95 | 0.01928 | 0.1274 | 0.0542 | optimize |
| s500-c6-r003 | -ts_mean(safe_div(close - low, high - low), 5) | 2.059 | 77.95 | 0.01928 | 0.1274 | 0.0542 | abandon |
| s500-c4-r005 | 0 - ts_zscore(ts_mean(safe_div(close - low, high - low), 10), 63) | 2.052 | 56.78 | 0.01897 | -0.07013 | -0.4911 | accept |
| s500-c7-r001 | ts_mean(safe_div(close - low, ts_range(high, 21)), 5) - ts_mean(safe_div(close - low, high - low), 5) | 1.947 | 67.44 | 0.01487 | 0.09698 | 0.002568 | optimize |
| s500-c2-r002 | -1 * ts_zscore(safe_div(close - low, high - low), 10) | 1.898 | 99.44 | 0.01856 | -0.01388 | 0.8675 | accept |
| s500-c2-r006 | -(safe_div(ts_mean(ts_max(close, 1) - ts_min(low, 1), 5), ts_mean(ts_max(high, 1) - ts_min(open, 1), 20))) | 1.801 | 69.74 | 0.0139 | -0.09654 | -0.1161 | abandon |
| s500-c6-r003 | -(ts_mean(safe_div(close - low, high - low), 5) - ts_mean(safe_div(close - low, high - low), 20)) | 1.749 | 82.97 | 0.01608 | 0.08928 | 0.5638 | optimize |
| s500-c2-r002 | -1 * ts_mean(safe_div(close - low, high - low), 10) | 1.683 | 53.74 | 0.01493 | 0.1214 | -0.4495 | optimize |
| s500-c4-r010 | -ts_mean(safe_div(close - low, high - low), 10) | 1.683 | 53.74 | 0.01493 | 0.1214 | -0.4495 | accept |
| s500-c1-r005 | -1 * safe_div(close - ts_min(close, 3), ts_max(close, 3) - ts_min(close, 3)) | 1.493 | 81.3 | 0.01664 | 0.6672 | 0.4589 | abandon |
| s500-c3-r007 | -1 * safe_div(ts_max_diff(cap, 126), ts_max(cap, 126)) * safe_div(close, ts_max(close, 126)) | 1.443 | 86.54 | 0.009216 | 0.4379 | 0.08153 | accept |
| s500-c3-r007 | -1 * ts_max_diff(cap, 63) * safe_div(close, close) | 1.421 | 90.59 | 0.01034 | 0.4314 | 0.133 | abandon |
| s500-c1-r004 | -1 * ts_mean(safe_div(volume, ts_mean(volume, 60)) * (safe_div(close - low, high - low) - 0.5), 10) | 1.413 | 47.64 | 0.01367 | -0.06063 | -0.181 | optimize |
| s500-c2-r008 | -1 * safe_div(close - ts_max(close, 60), ts_max(close, 60)) | 1.401 | 92.77 | 0.01177 | 0.5302 | 0.1243 | abandon |
| s500-c2-r005 | safe_div(volume, ts_mean(volume, 20)) * (0 - ts_zscore(ts_returns(close, 1, 1), 60)) | 1.39 | 93.15 | 0.01577 | 0.8393 | 0.6521 | abandon |
| s500-c4-r007 | -1 * ts_zscore(close, 5) | 1.385 | 64.29 | 0.01495 | 0.486 | 0.3078 | optimize |
| s500-c1-r004 | -1 * ts_ir(ts_returns(close, 1), 5) | 1.365 | 49.7 | 0.01124 | 0.2 | 0.7855 | abandon |
| s500-c1-r004 | -1 * safe_div(ts_sum(ts_returns(close, 1), 5), ts_std_dev(ts_returns(close, 1), 5)) | 1.365 | 49.7 | 0.01124 | 0.2 | 0.7855 | abandon |
| s500-c4-r005 | 0 - ts_mean(safe_div(close - low, high - low), 15) | 1.359 | 39.43 | 0.01277 | 0.1154 | -0.679 | optimize |
| s500-c5-r004 | -1 * ts_zscore(close, 5) | 1.353 | 60.76 | 0.01506 | 0.3041 | 0.6193 | optimize |
| s500-c2-r008 | -1 * safe_div(close - ts_max(close, 126), ts_max(close, 126)) | 1.327 | 87.03 | 0.008984 | 0.2678 | -0.16 | optimize |
| s500-c4-r009 | -(safe_div(close - ts_min(low, 10), ts_max(high, 10) - ts_min(low, 10))) | 1.314 | 39.34 | 0.0129 | 0.09048 | 0.4551 | optimize |
| s500-c3-r008 | -1 * safe_div(ts_returns(close, 5), ts_mean(safe_div(volume, cap), 20)) | 1.3 | 47 | 0.01197 | 0.287 | 0.8657 | optimize |
| s500-c1-r005 | -1 * ts_returns(close, 3) | 1.296 | 66.52 | 0.01188 | 0.1909 | 0.5924 | optimize |
| s500-c2-r005 | 0 - safe_div(ts_mean(volume, 5), ts_mean(volume, 63)) * ts_zscore(ts_returns(close, 1, 1), 20) / ts_std_dev(ts_returns(close, 1, 1), 60) | 1.293 | 92.35 | 0.01349 | 0.8869 | 0.7157 | abandon |
| s500-c4-r007 | -1 * safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 5), 60)) | 1.285 | 85.13 | 0.01171 | 0.2772 | 0.745 | optimize |
| s500-c2-r005 | 0 - safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) * ts_zscore(ts_returns(close, 1, 1), 20) | 1.284 | 92.41 | 0.01347 | 0.8843 | 0.7149 | abandon |
| s500-c3-r001 | -1 * ts_returns(close, 5) * ts_std_dev(ts_zscore(volume, 60), 5) | 1.28 | 85.14 | 0.01168 | 0.2742 | 0.7452 | optimize |
| s500-c3-r003 | -1 * ts_mean(ts_returns(close, 1, 1), 5) | 1.272 | 52.46 | 0.0113 | 0.08533 | 0.8013 | abandon |
| s500-c2-r005 | 0 - ts_returns(close, 5, 1) | 1.254 | 52.43 | 0.0113 | 0.07731 | 0.7732 | abandon |
| s500-c1-r005 | -1 * ts_returns(close, 5) | 1.254 | 52.43 | 0.0113 | 0.07731 | 0.7732 | optimize |
| s500-c3-r003 | -1 * ts_returns(close, 5, 1) | 1.254 | 52.43 | 0.0113 | 0.07731 | 0.7732 | optimize |
| s500-c2-r003 | -safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 5), 20)) | 1.251 | 52.24 | 0.01133 | 0.08298 | 0.7683 | optimize |
| s500-c3-r005 | -1 * safe_div(ts_sum(safe_div(close, open) - 1, 5), ts_std_dev(safe_div(close, open) - 1, 20)) | 1.25 | 78.81 | 0.01414 | 0.1944 | 0.2695 | optimize |
| s500-c2-r008 | -1 * ts_returns(close, 5) * ts_ir(volume, 20) | 1.242 | 52.29 | 0.01127 | 0.09377 | 0.7552 | optimize |
| s500-c2-r008 | -1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 20)) | 1.242 | 52.29 | 0.01127 | 0.09377 | 0.7552 | optimize |
| s500-c2-r003 | -safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 1), 20)) | 1.241 | 52.27 | 0.01127 | 0.09251 | 0.7581 | abandon |
| s500-c4-r007 | -1 * safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 1), 20)) | 1.241 | 52.27 | 0.01127 | 0.09251 | 0.7581 | optimize |
| s500-c2-r005 | 0 - ts_zscore(ts_returns(close, 5, 1), 63) | 1.237 | 51.48 | 0.01216 | -0.2682 | 0.628 | optimize |
| s500-c7-r002 | -1 * safe_div(safe_div(volume, ts_mean(volume, 20)) * safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 5), 20)), ts_std_dev(volume, 20)) | 1.232 | 85.65 | 0.01141 | 0.2783 | 0.7204 | optimize |
| s500-c1-r001 | -ts_mean(safe_div(close - low, high - low), 20) * (ts_max(high, 20) - ts_min(low, 20)) | 1.229 | 11.56 | 0.0116 | 0.6058 | -0.5414 | optimize |
| s500-c2-r003 | -ts_zscore(ts_returns(close, 5), 60) | 1.21 | 51.44 | 0.01205 | -0.2454 | 0.6771 | optimize |
| s500-c4-r003 | 0 - ts_zscore(ts_returns(close, 5), 60) * ts_mean(safe_div(volume, ts_mean(volume, 20)), 5) | 1.21 | 51.44 | 0.01205 | -0.2454 | 0.6771 | optimize |
| s500-c1-r001 | -ts_bollinger_position(close, 20, 2.0) * ts_std_dev(returns, 20) * ts_range(high, 20) * ts_range(low, 20) * safe_div(volume, ts_mean(volume, 20)) | 1.204 | 38.38 | 0.01669 | 0.6867 | -0.2564 | abandon |
| s500-c4-r005 | 0 - ts_zscore(safe_div(close - ts_mean(close, 20), ts_mean(close, 20)), 252) | 1.186 | 47.06 | 0.01679 | 0.08528 | 0.4998 | accept |
| s500-c3-r005 | -1 * ts_sum(safe_div(close, open) - 1, 5) | 1.181 | 50.46 | 0.01069 | 0.2305 | 0.3969 | abandon |
| s500-c5-r003 | -1 * safe_div(ts_returns(close, 10), safe_div(ts_mean(volume, 10), ts_mean(cap, 10))) | 1.169 | 50.25 | 0.01015 | 0.425 | 0.1568 | optimize |
| s500-c2-r005 | 0 - ts_zscore(ts_mean(ts_returns(close, 1, 1), 5), 126) | 1.165 | 51.13 | 0.01242 | -0.07129 | 0.8148 | abandon |
| s500-c2-r007 | ts_zscore((-1.0) * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)), 120) | 1.163 | 47.69 | 0.01191 | -0.0373 | 0.6515 | optimize |
| s500-c4-r005 | 0 - ts_sum(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5) | 1.14 | 59.95 | 0.003503 | 0.61 | 0.9284 | optimize |
| s500-c1-r003 | -(ts_mean(open - ts_delta(close, 1), 10) - ts_mean(close - open, 10)) | 1.139 | 2.221 | 0.003953 | 0.8458 | 0.3046 | abandon |
| s500-c1-r001 | -ts_mean(safe_div(close - low, high - low), 20) | 1.137 | 33.67 | 0.01041 | 0.08096 | -0.3902 | optimize |
| s500-c6-r003 | -(ts_sum(ts_returns(close, 1, 0), 5)) * safe_div(ts_mean(volume, 20), cap) | 1.134 | 85.75 | 0.01137 | 0.1907 | 0.6748 | abandon |
| s500-c2-r001 | -1 * safe_div(ts_mean(close - ts_min(low, 252), 21), ts_range(high, 252)) * ts_zscore(high - ts_max(high, 252), 21) | 1.098 | 46.64 | 0.01057 | 0.0425 | 0.4802 | accept |
| s500-c3-r007 | (1 - ts_scale(ts_max_diff(cap, 126), 126, 0)) * safe_div(close - ts_min(close, 126), ts_max(close, 126) - ts_min(close, 126)) | 1.093 | 86.61 | 0.00956 | -0.002711 | -0.1265 | optimize |
| s500-c6-r003 | -ts_sum(ts_returns(close, 1, 0), 5) * ts_bollinger_position(safe_div(ts_mean(volume, 20), cap), 60, 2.0) | 1.075 | 84.44 | 0.01051 | 0.2062 | 0.6823 | abandon |
| s500-c1-r004 | -1 * safe_div(ts_mean(ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 60)) | 1.073 | 56.45 | 0.01174 | 0.1345 | 0.2943 | abandon |
| s500-c2-r005 | 0 - ts_zscore(safe_div(cap, ts_mean(cap, 21)), 63) | 1.061 | 49.68 | 0.0145 | -0.077 | 0.1539 | accept |
| s500-c1-r010 | -1 * ts_mean(safe_div(close - low, high - low) * safe_div(volume, ts_mean(volume, 21)), 10) | 1.053 | 40.92 | 0.008469 | 0.1706 | -0.6209 | accept |
| s500-c1-r001 | -ts_bollinger_position(safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)), 20, 2.0) + ts_zscore(volume, 60) | 1.044 | 50.5 | 0.005915 | 0.2469 | 1.413 | optimize |
| s500-c1-r005 | -1 * safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) | 1.043 | 58.54 | 0.01363 | 0.1708 | 0.269 | optimize |
| s500-c3-r004 | -safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) | 1.043 | 58.54 | 0.01363 | 0.1708 | 0.269 | optimize |
| s500-c4-r003 | 0 - ts_zscore(ts_returns(close, 5), 20) * ts_mean(safe_div(volume, ts_mean(volume, 60)), 5) | 1.029 | 52.16 | 0.008618 | -0.1194 | 0.8695 | optimize |
| s500-c7-r003 | -ts_zscore(ts_returns(close, 5), 21) | 1.025 | 49.18 | 0.009692 | -0.06394 | 0.8797 | optimize |
| s500-c7-r003 | -ts_zscore(ts_returns(close, 5) - ts_mean(ts_returns(close, 1), 5), 21) | 1.025 | 49.18 | 0.009691 | -0.06448 | 0.8732 | optimize |
| s500-c1-r004 | -1 * ts_sum(safe_div(safe_div(close, open), safe_div(open, ts_delta(close, 1) + close)), 10) | 1.025 | 56.63 | 0.01445 | 0.2927 | -0.1408 | optimize |
| s500-c4-r009 | -(safe_div(close - ts_min(low, 21), ts_max(high, 21) - ts_min(low, 21))) | 1.024 | 57.35 | 0.01338 | 0.1657 | 0.2512 | abandon |
| s500-c3-r004 | -ts_bollinger_percent(close, 20, 2) * safe_div(ts_delta(high, 5), safe_div(ts_max(high, 20) - ts_min(low, 20), ts_mean(low, 20))) | 0.999 | 52.5 | 0.006302 | 0.106 | 0.8084 | accept |
| s500-c2-r005 | 0 - ts_zscore(cap, 21) | 0.9879 | 29.42 | 0.009825 | -0.007433 | 0.3369 | optimize |
| s500-c3-r004 | safe_div(close, ts_mean(close, 126)) * safe_div(1.0, 1.0 + ts_zscore(returns, 126)) | 0.9846 | 159.5 | 0.01332 | 0.6327 | -0.9677 | abandon |
| s500-c4-r010 | -ts_zscore(ts_mean(safe_div(close - ts_median(close, 10), high - low), 10), 252) | 0.9822 | 25.85 | 0.01026 | -0.02213 | 0.4683 | optimize |
| s500-c1-r005 | -1 * safe_div(close - ts_mean(close, 21), ts_std_dev(close, 63)) * safe_div(ts_std_dev(returns, 21), ts_std_dev(returns, 63)) | 0.9817 | 52.68 | 0.00704 | 0.4823 | 0.898 | optimize |
| s500-c5-r002 | -ts_mean(safe_div(close - low, high - low) * abs(ts_returns(close, 1)), 5) | 0.9775 | 58.03 | 0.02002 | -0.06789 | -1.221 | optimize |
| s500-c1-r003 | -(safe_div(ts_mean(open - ts_delta(close, 1), 10), ts_mean(close - open, 10))) | 0.9734 | 57.67 | 0.006964 | 0.3534 | -0.2537 | abandon |
| s500-c1-r005 | -1 * safe_div(close - ts_mean(close, 21), ts_std_dev(close, 63)) * safe_div(ts_std_dev(returns, 21), ts_std_dev(returns, 251)) | 0.9655 | 51.28 | 0.007039 | 0.5082 | 0.8926 | optimize |
| s500-c5-r004 | -1 * ts_zscore(close, 20) | 0.9646 | 30.19 | 0.009784 | -0.0108 | 0.4356 | accept |
| s500-c1-r009 | -ts_mean(safe_div(volume, ts_median(volume, 40)), 5) * (1 + ts_zscore(safe_div(close, ts_mean(close, 5)), 20)) | 0.9438 | 56.22 | 0.009855 | 0.018 | 0.6424 | optimize |
| s500-c2-r006 | -(safe_div(ts_mean((close + high + low) / open, 5), ts_mean((close + high + low) / open, 20))) | 0.9092 | 47.56 | 0.008575 | 0.06179 | 0.4666 | optimize |
| s500-c3-r008 | -1 * (ts_returns(close, 5) / (1 + abs(ts_returns(close, 5)))) * (2 / (1 + ts_zscore(safe_div(volume, cap), 20))) | 0.9077 | 63.98 | 0.007321 | -0.07311 | 0.883 | optimize |
| s500-c1-r004 | -1 * ts_mean(safe_div(volume, ts_mean(volume, 60)) * safe_div(close - low, high - low), 10) | 0.9008 | 37.1 | 0.007886 | 0.1483 | -0.4583 | abandon |
| s500-c1-r005 | -1 * safe_div(close - ts_min(low, 40), ts_max(high, 40) - ts_min(low, 40)) | 0.8744 | 43.48 | 0.01016 | 0.1318 | 0.174 | optimize |
| s500-c1-r009 | -(ts_zscore(volume, 20) - ts_zscore(safe_div(volume, close), 20)) | 0.8597 | 76.95 | 0.01127 | 0.2129 | 0.5027 | abandon |
| s500-c1-r009 | -(ts_zscore(volume, 40) - ts_zscore(safe_div(volume, close), 40)) | 0.8434 | 64.38 | 0.009263 | -0.1104 | 0.1858 | abandon |
| s500-c3-r005 | -1 * ts_zscore(safe_div(close, open) - 1, 5) | 0.8257 | 107.3 | 0.008787 | 0.7144 | 0.6786 | optimize |
| s500-c6-r003 | -ts_zscore(ts_returns(close, 20, 0), 60) * ts_bollinger_position(safe_div(volume, cap), 60, 2.0) | 0.8212 | 66.39 | 0.01078 | -0.02437 | -0.3179 | accept |
| s500-c6-r002 | 0 - safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)) | 0.8144 | 31.67 | 0.00797 | 0.1384 | 0.2157 | optimize |
| s500-c3-r010 | -1 * ts_zscore(close, 63) | 0.7905 | 32.87 | 0.00677 | 0.09211 | 0.1186 | abandon |
| s500-c3-r010 | -1 * ts_bollinger_percent(close, 63, 2) | 0.7905 | 32.87 | 0.00677 | 0.09211 | 0.1186 | optimize |
| s500-c1-r001 | ts_ir(ts_returns(close, 1), 60) - ts_ir(ts_returns(close, 1), 20) | 0.7857 | 44.3 | 0.01034 | 0.05142 | -0.2107 | optimize |
| s500-c6-r003 | -1 * ts_zscore(ts_returns(close, 20, 0), 60) * safe_div(safe_div(ts_mean(volume, 20), ts_mean(volume, 60)), safe_div(cap, ts_mean(cap, 60))) | 0.7786 | 43.45 | 0.01116 | 0.02446 | -0.3159 | optimize |
| s500-c4-r008 | -1 * ts_zscore(safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)), 126) | 0.7658 | 35.33 | 0.01188 | 0.08134 | 0.5683 | optimize |
| s500-c5-r007 | -1 * safe_div(ts_mean(safe_div(high - low, close), 5), ts_mean(safe_div(high - low, close), 60)) * ts_delta(close, 20) | 0.7599 | 34.78 | 0.007797 | 0.3881 | 0.1585 | optimize |
| s500-c2-r001 | -1 * safe_div(ts_mean(returns - ts_mean(returns, 21), 20), ts_std_dev(returns, 252)) * safe_div(returns, ts_returns(close, 1, 1)) | 0.7563 | 47.94 | 0.009905 | 0.177 | 0.3294 | abandon |
| s500-c1-r009 | -ts_mean(safe_div(volume, ts_median(volume, 40)), 3) * (1 + ts_zscore(close, 40)) | 0.7517 | 49.5 | 0.006286 | 0.2435 | 0.1665 | optimize |
| s500-c1-r001 | ts_mean(safe_div(cap, close), 20) | 0.7459 | 1.736 | 4.35e-04 | 1.268 | 1.909 | abandon |
| s500-c5-r001 | -ts_ir(ts_returns(close, 1), 40) | 0.7452 | 29.28 | 0.005741 | 0.178 | -0.1824 | optimize |
| s500-c4-r001 | -1 * ts_zscore(ts_mean(safe_div(ts_returns(close, 1), ts_std_dev(ts_returns(close, 1), 63)), 63), 252) | 0.7439 | 23.08 | 0.00794 | 0.426 | 0.4696 | abandon |
| s500-c1-r001 | -ts_bollinger_position(close, 20, 2.0) * safe_div(ts_std_dev(returns, 20) * safe_div(ts_range(high, 20), ts_range(low, 20)) * volume, ts_mean(volume, 60)) | 0.74 | 30.95 | 0.01312 | -0.009341 | -0.5206 | optimize |
| s500-c1-r009 | -(safe_div(ts_mean(volume, 5), ts_mean(volume, 20)) * (1 + ts_zscore(close, 60))) | 0.7399 | 38.45 | 0.006089 | 9.97e-05 | 0.05007 | abandon |
| s500-c4-r008 | -1 * ts_zscore(safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120)), 250) | 0.7282 | 25.31 | 0.00834 | 0.236 | 0.6685 | optimize |
| s500-c1-r001 | -ts_bollinger_position(safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)), 20, 2.0) * safe_div(volume, ts_mean(volume, 60)) | 0.7266 | 43.74 | 0.005901 | -0.06913 | 0.1941 | abandon |
| s500-c5-r007 | safe_div(ts_mean(ts_returns(close, 1, 1), 60), ts_std_dev(ts_returns(close, 1, 1), 60)) * -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | 0.7257 | 28.24 | 0.003923 | 0.2763 | 0.07538 | optimize |
| s500-c1-r001 | -safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | 0.7223 | 38.81 | 0.005776 | 0.1426 | 0.236 | abandon |
| s500-c1-r001 | -ts_bollinger_position(close, 20, 2.0) * safe_div(ts_std_dev(returns, 20) * ts_range(high, 20), ts_range(low, 20) * ts_mean(volume, 20)) * volume | 0.7223 | 31.79 | 0.01309 | 0.01634 | -0.629 | optimize |
| s500-c4-r004 | -1 * safe_div(close - ts_ema(close, 120), close * ts_std_dev(returns, 20)) * (1 + ts_zscore(ts_mean(volume, 20), 120)) | 0.7013 | 29.35 | 0.002244 | 0.1092 | 0.2469 | optimize |
| s500-c1-r010 | -1 * ts_ir(ts_returns(close, 1, 1), 60) * safe_div(cap, ts_mean(cap, 21)) | 0.6797 | 24.38 | 0.00351 | 0.3069 | 0.06656 | abandon |
| s500-c2-r003 | -safe_div(ts_max(high, 10) - ts_min(low, 10), ts_mean(ts_max(high, 10) - ts_min(low, 10), 60)) | 0.6795 | 43.07 | 0.004345 | -0.1996 | -0.09785 | optimize |
| s500-c1-r010 | -1 * ts_mean(cap, 21) * (1 + 0.000000001 * safe_div(close, ts_mean(close, 21))) | 0.6756 | 0.436 | -1.87e-04 | -0.3884 | -0.6386 | abandon |
| s500-c2-r005 | 0 - safe_div(cap, ts_mean(cap, 63)) | 0.6751 | 26.47 | 0.008763 | 0.2787 | -0.04262 | optimize |
| s500-c4-r010 | -ts_mean(cap, 20) | 0.6715 | 0.4431 | -1.77e-04 | -0.3888 | -0.6388 | optimize |
| s500-c1-r004 | -1 * safe_div(ts_mean(ts_returns(close, 1), 60), ts_std_dev(ts_returns(close, 1), 60)) | 0.6662 | 24.11 | 0.003307 | 0.3153 | 0.07688 | abandon |
| s500-c3-r009 | -ts_ir(ts_returns(close, 1), 60) | 0.6662 | 24.11 | 0.003307 | 0.3153 | 0.07688 | abandon |
| s500-c3-r001 | -1 * ts_ir(ts_returns(close, 1), 60) | 0.6662 | 24.11 | 0.003307 | 0.3153 | 0.07688 | abandon |
| s500-c4-r004 | safe_div(ts_mean(safe_div(abs(ts_returns(close, 1)), close * volume), 20), ts_median(safe_div(abs(ts_returns(close, 1)), close * volume), 20)) | 0.6654 | 44.55 | 0.002746 | 0.2718 | 0.2311 | abandon |
| s500-c1-r005 | -1 * safe_div(abs(close - ts_mean(close, 21)), ts_std_dev(close, 63)) * safe_div(ts_std_dev(returns, 63), ts_std_dev(returns, 251)) | 0.6613 | 65.11 | 0.004594 | -0.6383 | 0.07394 | abandon |
| s500-c5-r002 | -safe_div(ts_std_dev(ts_returns(close, 1), 21), ts_std_dev(ts_delta(volume, 1), 21)) | 0.6578 | 10.19 | 1.95e-04 | 0.8491 | 1.295 | abandon |
| s500-c5-r007 | safe_div(ts_returns(close, 60, 1), ts_std_dev(ts_returns(close, 1, 1), 60)) * -1 * ts_zscore(ts_mean(volume, 5), 250) | 0.6552 | 46.93 | 0.005159 | -0.1207 | -0.5184 | optimize |
| s500-c1-r003 | -(ts_mean(close * volume, 120) + (ts_mean(close * volume, 20) - ts_mean(close * volume, 120))) | 0.6539 | 3.53 | 0.005635 | -0.2027 | -1.265 | abandon |
| s500-c1-r003 | -ts_median(close * volume, 60) | 0.6513 | 1.605 | 0.005527 | -0.217 | -1.235 | abandon |
| s500-c1-r001 | -safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) * (1.0 + ts_zscore(volume, 60)) | 0.6374 | 116.1 | 0.002681 | 0.1139 | 0.04997 | abandon |
| s500-c6-r002 | 0 - safe_div(safe_div(cap, ts_delta(cap, 60)), safe_div(ts_mean(volume, 60), ts_delta(volume, 60) + ts_mean(volume, 60))) | 0.6232 | 45.16 | -2.48e-04 | 0.4015 | 0.09001 | abandon |
| s500-c3-r010 | -1 * ts_ir(ts_returns(close, 1), 63) | 0.6172 | 22.17 | 6.10e-04 | 0.4253 | 0.1002 | abandon |
| s500-c4-r005 | 0 - safe_div(close - ts_mean(close, 100), ts_mean(close, 100)) | 0.6163 | 25.14 | -0.001128 | 0.2993 | 0.1609 | abandon |
| s500-c3-r003 | ts_mean(safe_div(abs(ts_returns(close, 1, 1)), ts_mean(close * volume, 5)), 20) | 0.6109 | 32.3 | 0.003913 | 0.2913 | -0.2168 | abandon |
| s500-c4-r008 | ts_mean(safe_div(safe_div(high - low, close) + abs(ts_returns(close, 1)), close * volume), 21) | 0.6042 | 2.226 | 8.46e-04 | -0.09769 | -0.6415 | abandon |
| s500-c1-r007 | -ts_zscore(ts_mean(volume * returns, 20), 250) | 0.5978 | 19.25 | 0.007032 | 0.402 | 0.3361 | optimize |
| s500-c5-r003 | -1 * safe_div(ts_returns(close, 10), 1 + ts_zscore(safe_div(ts_mean(volume, 10), ts_mean(cap, 10)), 63)) | 0.5961 | 68.34 | 0.005844 | 0.4857 | 0.1177 | optimize |
| s500-c3-r010 | -1 * ts_zscore(close, 126) | 0.5959 | 21.97 | -4.89e-04 | 0.1989 | 0.1979 | abandon |
| s500-c3-r007 | -1 * ts_mean(ts_returns(close, 21) * safe_div(ts_std_dev(volume, 21), ts_mean(volume, 63)), 1) | 0.5894 | 34.41 | 0.009391 | 0.2593 | 0.329 | optimize |
| s500-c4-r008 | ts_median(safe_div(abs(safe_div(high - low, close)), close * volume), 21) | 0.5865 | 2.521 | 7.13e-04 | -0.1255 | -0.7393 | abandon |
| s500-c1-r009 | -(ts_zscore(volume, 40) + ts_zscore(close, 40)) | 0.5853 | 70.23 | 0.001883 | 0.3026 | 0.1757 | optimize |
| s500-c4-r006 | safe_div(ts_median(close - ts_min(low, 20), 5), ts_median(ts_max(high, 20) - ts_min(low, 20), 5)) | 0.585 | 32.56 | 0.003745 | 0.2314 | -0.2267 | abandon |
| s500-c4-r001 | -1 * ts_mean(abs(ts_returns(close, 1)), 63) * ts_zscore(ts_mean(safe_div(ts_returns(close, 1), ts_std_dev(ts_returns(close, 1), 126)), 63), 252) | 0.5835 | 22.68 | 0.00885 | 0.5098 | 0.5521 | abandon |
| s500-c3-r003 | ts_mean(safe_div(abs(ts_returns(close, 1, 1)), close * volume), 20) | 0.5787 | 3.27 | 7.46e-04 | -0.07368 | -0.5268 | abandon |
| s500-c1-r009 | -(safe_div((high - low), close)) / ts_mean(safe_div((high - low), close), 60) | 0.5767 | 159.5 | 0.004051 | -0.05146 | -0.2528 | optimize |
| s500-c4-r008 | -1 * safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120)) | 0.5717 | 21.25 | -8.34e-04 | 0.191 | 0.316 | abandon |
| s500-c4-r001 | -1 * ts_mean(safe_div(ts_returns(close, 1), ts_std_dev(ts_returns(close, 1), 63) + abs(ts_returns(close, 1))), 63) | 0.5708 | 28.6 | -0.002294 | 0.4589 | 0.2368 | abandon |
| s500-c5-r001 | safe_div(ts_sum((volume / ts_mean(volume, 60)) * ((high - low) / close), 30), ts_sum(abs(ts_returns(close, 1)), 30)) | 0.5663 | 18.11 | 8.71e-04 | -0.5504 | -1.291 | abandon |
| s500-c1-r005 | -1 * safe_div(ts_mean(close, 5) - ts_min(low, 40), ts_max(high, 40) - ts_min(low, 40)) | 0.5613 | 21.96 | 0.003134 | 0.1253 | 0.1131 | optimize |
| s500-c5-r002 | -safe_div(ts_ir(ts_returns(close, 1) * (high - low), 63), ts_mean(volume, 21)) | 0.5432 | 20.35 | 0.002706 | 0.3092 | 0.11 | abandon |
| s500-c5-r001 | ts_returns(close, 50) * (1 - safe_div(ts_median(safe_div(high - low, close), 10), ts_median(safe_div(high - low, close), 50))) | 0.5413 | 47.67 | 7.32e-04 | -0.1585 | 0.4735 | abandon |
| s500-c3-r003 | -1 * ts_mean(safe_div(ts_delta(close, 5), ts_delta(close, 1)), 1) - 1 * ts_returns(close, 5, 1) | 0.5394 | 152.2 | 0.003174 | -0.3376 | -0.9266 | optimize |
| s500-c1-r001 | -ts_bollinger_position(safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)), 60, 2.0) * safe_div(volume, ts_mean(volume, 60)) | 0.536 | 29.33 | 0.008468 | -0.1783 | -0.3249 | abandon |
| s500-c1-r007 | -(ts_mean(returns * volume, 20) / ts_mean(abs(returns) * volume, 20)) | 0.5268 | 32.68 | 0.007421 | 0.1597 | -0.1068 | abandon |
| s500-c5-r002 | -ts_std_dev(ts_returns(close, 1) * (high - low) * ts_bollinger_width(volume, 63), 63) | 0.5205 | 4.028 | 0.00991 | 0.9351 | -0.502 | optimize |
| s500-c4-r005 | 0 - ts_sum(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 10) | 0.5183 | 29.14 | 0.001325 | 0.2936 | 0.7194 | abandon |
| s500-c3-r003 | -1 * ts_zscore(safe_div(high - low, close), 60) | 0.514 | 160.3 | 0.004029 | -0.2436 | -0.3142 | abandon |
| s500-c1-r009 | -(ts_zscore(safe_div((high - low), close), 60)) | 0.514 | 160.3 | 0.004029 | -0.2436 | -0.3142 | abandon |
| s500-c3-r001 | -1 * ts_zscore(safe_div(high - low, close), 60) | 0.514 | 160.3 | 0.004029 | -0.2436 | -0.3142 | abandon |
| s500-c1-r009 | -((safe_div((high - low), close) - ts_mean(safe_div((high - low), close), 60)) / ts_std_dev(safe_div((high - low), close), 60)) | 0.514 | 160.3 | 0.004029 | -0.2436 | -0.3142 | abandon |
| s500-c1-r001 | -safe_div(ts_mean(ts_delta(open, 1) - open + close, 20), ts_mean(close, 20)) | 0.5137 | 27.25 | 0.008935 | 0.1766 | -0.001928 | abandon |
| s500-c6-r001 | safe_div(ts_returns(close, 63), ts_returns(cap, 63)) * safe_div(ts_mean(volume, 5), ts_mean(volume, 63)) | 0.5094 | 48.56 | 0.001596 | -0.1051 | 1.227 | abandon |
| s500-c1-r003 | -(safe_div(ts_zscore(close, 120), 1) * ts_mean(safe_div(high - low, close), 20)) | 0.5016 | 22.9 | -0.002991 | 0.3364 | 0.3035 | abandon |
| s500-c3-r007 | -1 * ts_mean(safe_div(close - high, high - low), 63) | 0.4942 | 18.09 | -0.002921 | 0.3463 | -0.2373 | optimize |
| s500-c1-r006 | safe_div(ts_mean(safe_div(high - low, close), 5), ts_median(safe_div(high - low, close), 60)) | 0.4899 | 31.74 | 6.45e-04 | -0.7565 | 0.1676 | abandon |
| s500-c4-r003 | ts_median(safe_div(cap, volume), 60) | 0.4899 | 31.74 | 6.45e-04 | -0.7565 | 0.1676 | abandon |
| s500-c2-r004 | ts_mean(safe_div(high - low, close), 60) | 0.4899 | 31.74 | 6.45e-04 | -0.7565 | 0.1676 | abandon |
| s500-c2-r004 | ts_ir(safe_div(high - low, close), 60) | 0.4899 | 31.74 | 6.45e-04 | -0.7565 | 0.1676 | abandon |
| s500-c1-r005 | safe_div(ts_std_dev(returns, 5), ts_std_dev(returns, 63)) * safe_div(ts_mean(close, 5), ts_mean(close, 251)) | 0.4858 | 30.14 | 0.003927 | 0.02806 | -0.1601 | abandon |
| s500-c3-r006 | ts_mean(safe_div(close - ts_min(low, 126), ts_max(high, 126) - ts_min(low, 126)), 21) | 0.4754 | 31.52 | 7.59e-04 | 0.3556 | 0.1839 | abandon |
| s500-c5-r002 | -ts_mean(ts_bollinger_position(close - low, 10) * safe_div(high - low, close), 5) | 0.4738 | 54.18 | 0.0147 | 0.08272 | -1.154 | abandon |
| s500-c6-r002 | 0 - safe_div(ts_delta(cap, 60) / ts_mean(cap, 60), ts_delta(volume, 60) / ts_mean(volume, 60)) | 0.4714 | 96.89 | 0.00173 | -0.6349 | -0.5317 | abandon |
| s500-c7-r002 | -1 * ts_bollinger_position(close, 200, 2.0) | 0.4695 | 16.65 | -0.003191 | 0.07521 | -0.03181 | abandon |
| s500-c4-r007 | ts_zscore(high - low, 10) - ts_zscore(high - low, 120) | 0.4653 | 114 | -8.17e-04 | 0.02464 | 0.4451 | abandon |
| s500-c1-r009 | -ts_zscore(safe_div((high - low), close), 20) / (1 + abs(ts_delta(safe_div((high - low), close), 5))) | 0.4625 | 164.1 | 0.003905 | -0.1993 | -0.5562 | abandon |
| s500-c1-r001 | -safe_div(ts_mean(ts_returns(close, 1) * abs(ts_returns(close, 1)), 20), ts_std_dev(ts_returns(close, 1), 20)) | 0.4483 | 30.89 | 0.009577 | 0.03678 | -0.2512 | abandon |
| s500-c3-r007 | -1 * ts_mean(ts_returns(close, 5) * safe_div(ts_std_dev(volume, 21), ts_mean(volume, 63)), 21) | 0.441 | 23.1 | 0.002643 | 0.00476 | 0.08984 | abandon |
| s500-c2-r004 | ts_zscore(safe_div(ts_mean(volume, 20), ts_mean(cap, 20)), 120) | 0.4257 | 15.28 | -0.00288 | 0.04921 | -0.04211 | optimize |
| s500-c2-r004 | ts_mean(safe_div(close - low, high - low), 20) | 0.4208 | 32.05 | 8.43e-04 | -0.395 | -0.7084 | abandon |
| s500-c2-r004 | safe_div(ts_mean(safe_div(close - low, high - low), 20), ts_std_dev(safe_div(close - low, high - low), 20)) | 0.4208 | 32.05 | 8.43e-04 | -0.395 | -0.7084 | abandon |
| s500-c3-r008 | ts_mean(safe_div(close - low, high - low), 20) * (1 - ts_mean(safe_div(high - low, close), 20)) | 0.4208 | 32.05 | 8.43e-04 | -0.395 | -0.7084 | abandon |
| s500-c3-r008 | ts_mean(safe_div(close - low, high - low), 20) | 0.4208 | 32.05 | 8.43e-04 | -0.395 | -0.7084 | abandon |
| s500-c1-r001 | safe_div(ts_mean(close, 20), ts_mean(cap, 20)) | 0.4208 | 32.05 | 8.43e-04 | -0.395 | -0.7084 | abandon |
| s500-c2-r006 | ts_mean(safe_div(close - low, ts_max(high, 1) - ts_min(low, 1)), 20) | 0.4208 | 32.05 | 8.43e-04 | -0.395 | -0.7084 | abandon |
| s500-c3-r008 | ts_mean(safe_div(close - low, high - low), 20) * ts_mean(1 - safe_div(high - low, close), 20) | 0.4208 | 32.05 | 8.43e-04 | -0.395 | -0.7084 | abandon |
| s500-c1-r009 | -(safe_div(ts_mean(volume, 5), ts_mean(volume, 20)) * safe_div(close, ts_mean(close, 20))) | 0.4187 | 52.43 | 6.24e-04 | 0.3053 | -0.4832 | abandon |
| s500-c3-r006 | ts_mean(safe_div(close - low, ts_max(high, 5) - ts_min(low, 5)), 5) | 0.4163 | 32.49 | 0.003485 | 0.1466 | -0.4752 | abandon |
| s500-c2-r004 | - ts_ir(safe_div(volume, cap), 20) | 0.4162 | 16.31 | -0.002542 | -0.5886 | 0.008035 | abandon |
| s500-c1-r001 | -safe_div(ts_mean(ts_returns(close, 1) * abs(ts_returns(close, 1)), 20), ts_mean(abs(ts_returns(close, 1)), 20)) | 0.4145 | 30.41 | 0.009132 | 0.02627 | -0.2808 | abandon |
| s500-c3-r007 | -1 * ts_mean(ts_returns(close, 5) * (safe_div(ts_mean(volume, 21), ts_mean(volume, 63)) - 1), 21) | 0.4109 | 20.48 | -5.51e-04 | 0.6305 | 0.8091 | abandon |
| s500-c1-r010 | -1 * ts_zscore(ts_range(safe_div(high - low, close), 10), 120) | 0.3972 | 26.8 | 0.003858 | 0.4459 | -1.668 | optimize |
| s500-c7-r002 | -1 * safe_div(ts_zscore(ts_mean(safe_div(high - low, close), 5), 20), ts_zscore(volume, 20)) | 0.3913 | 138.9 | 0.001829 | 0.2646 | 0.1586 | abandon |
| s500-c3-r001 | -1 * ts_returns(close, 5) * ts_zscore(volume, 60) | 0.3892 | 123.4 | 0.003351 | -0.08553 | -0.1874 | abandon |
| s500-c2-r003 | safe_div(ts_mean(abs(returns), 5), ts_mean(abs(returns), 63)) | 0.3884 | 20.17 | -1.31e-04 | 0.5777 | -0.02301 | abandon |
| s500-c2-r003 | safe_div(ts_mean(abs(returns), 10), ts_mean(abs(returns), 63)) | 0.3881 | 20.17 | -8.74e-05 | 0.5777 | -0.02301 | abandon |
| s500-c1-r001 | -ts_delta(ts_mean(safe_div(cap, close), 20), 60) | 0.3875 | 3.571 | 0.003058 | 0.8854 | -0.3556 | abandon |
| s500-c1-r005 | -1 * safe_div(abs(ts_returns(close, 5)), ts_std_dev(abs(ts_returns(close, 1)), 63)) * safe_div(ts_mean(volume, 20), ts_mean(volume, 63)) | 0.3866 | 100.7 | 0.003394 | -0.4229 | -0.3425 | abandon |
| s500-c3-r004 | -(safe_div(close, ts_mean(close, 252)) - 1) | 0.3836 | 15.85 | -0.0072 | -0.002216 | 0.006539 | abandon |
| s500-c1-r006 | -1 * ts_mean(ts_std_dev(close, 2) - ts_std_dev(close, 20), 40) | 0.3808 | 32.02 | 0.002995 | -0.1319 | -0.7885 | abandon |
| s500-c1-r005 | safe_div(ts_std_dev(returns, 21), ts_std_dev(returns, 63)) * safe_div(abs(close - ts_mean(close, 21)), ts_std_dev(close, 21)) | 0.3808 | 32.21 | 0.001665 | -0.02448 | -1.135 | abandon |
| s500-c1-r009 | -(safe_div(volume, ts_mean(volume, 40)) * safe_div(close, ts_mean(close, 40))) | 0.3785 | 126.5 | -0.004392 | 0.2412 | -0.03375 | abandon |
| s500-c1-r002 | -1 * safe_div(ts_max(volume, 20), ts_mean(volume, 20)) | 0.3734 | 24.65 | 0.002983 | 1.091 | 0.6523 | abandon |
| s500-c6-r001 | safe_div(ts_sum(safe_div(high - low, close), 21), abs(ts_returns(close, 21)) + ts_mean(safe_div(high - low, close), 21)) | 0.3719 | 61.81 | 0.005407 | -0.2784 | -0.9652 | abandon |
| s500-c2-r005 | ts_zscore(ts_mean(safe_div(high - low, close), 20), 63) | 0.3714 | 16.82 | -6.28e-04 | -0.07689 | -0.02066 | abandon |
| s500-c6-r001 | safe_div(ts_returns(close, 63), ts_returns(cap, 63)) * safe_div(ts_mean(volume, 21), ts_mean(volume, 126)) | 0.3691 | 33.63 | -2.32e-04 | -0.4438 | 0.03597 | abandon |
| s500-c2-r006 | -(ts_zscore(safe_div(ts_mean(volume, 5), ts_mean(volume, 60)), 120) * ts_zscore(safe_div(close, ts_mean(close, 60)), 120) * ts_zscore(returns, 120)) | 0.3684 | 176.5 | -0.004676 | -0.8185 | -0.09552 | abandon |
| s500-c2-r005 | 0 - ts_zscore(safe_div(ts_mean(volume, 5), ts_mean(volume, 63)), 126) * ts_returns(close, 20, 1) | 0.3657 | 53.95 | 0.00176 | -0.8456 | 0.1384 | abandon |
| s500-c4-r007 | -1 * safe_div(ts_mean(high - low, 10), ts_mean(high - low, 60)) * 1 | 0.3654 | 39.48 | 0.002429 | 0.3198 | -0.2659 | optimize |
| s500-c1-r003 | -safe_div(ts_mean(close * volume, 20), ts_std_dev(close * volume, 120)) | 0.3634 | 6.81 | -0.002891 | -0.3903 | 0.7351 | abandon |
| s500-c3-r004 | -safe_div(ts_std_dev(ts_returns(close, 1), 60), ts_scale(safe_div(volume, ts_median(volume, 60)), 60)) | 0.3594 | 84.09 | 0.009513 | 0.409 | -0.6511 | abandon |
| s500-c2-r006 | ts_mean(safe_div(close - low, ts_max(high, 1) - ts_min(low, 1)), 5) | 0.3549 | 32.73 | 7.06e-04 | 0.3794 | -0.06987 | abandon |
| s500-c3-r001 | -1 * safe_div(ts_std_dev(returns, 5), ts_std_dev(returns, 60)) | 0.3549 | 68.9 | 0.002811 | 0.291 | -0.2577 | abandon |
| s500-c2-r007 | (-1.0) * ts_zscore(safe_div(ts_min_max_diff(safe_div(high - low, close), 60), ts_mean(safe_div(high - low, close), 60)), 60) | 0.3528 | 127.4 | 0.002889 | -0.3469 | -0.06002 | abandon |
| s500-c3-r007 | ts_mean(safe_div(close - low, high - low), 126) | 0.3489 | 31.26 | 5.71e-04 | 0.3402 | 1.359 | abandon |
| s500-c5-r006 | safe_div(ts_returns(close, 250), ts_returns(cap, 250)) * safe_div(1, ts_mean(safe_div(volume * close, cap), 250)) | 0.3467 | 45.58 | 8.12e-04 | -0.4565 | 0.4804 | abandon |
| s500-c7-r001 | ts_mean(safe_div(close - low, high - low), 5) | 0.3454 | 0.1433 | 0.03535 | - | - | abandon |
| s500-c2-r005 | ts_ir(ts_mean(safe_div(high - low, close), 20), 63) | 0.345 | 32.23 | -0.001844 | 0.4304 | -0.5102 | abandon |
| s500-c3-r006 | ts_mean(safe_div(close - low, high - low), 10) | 0.3409 | 32.26 | 0.002426 | -0.06505 | 0.2491 | abandon |
| s500-c3-r001 | -1 * safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 1), 20)) * ts_zscore(ts_mean(volume, 5), 60) | 0.3374 | 91.91 | 0.001028 | -0.2573 | 0.1707 | abandon |
| s500-c7-r001 | ts_zscore(safe_div(ts_mean(safe_div(high - low, close), 63), ts_mean(abs(ts_returns(close, 1)), 63)), 252) | 0.3365 | 20.79 | 0.002565 | 0.07159 | -1.158 | abandon |
| s500-c4-r003 | safe_div(ts_mean(safe_div(volume, cap), 20), ts_mean(safe_div(volume, cap), 120)) | 0.3326 | 13.85 | -0.002762 | -0.01545 | -0.1409 | abandon |
| s500-c4-r001 | ts_zscore(ts_mean(safe_div(close - open, open - (close - ts_delta(close, 1))), 21), 252) | 0.3287 | 20.39 | 0.00213 | 0.3629 | 0.5776 | abandon |
| s500-c1-r010 | -1 * ts_zscore(ts_mean(safe_div(high - low, close), 10), 120) | 0.3215 | 37.95 | 0.002822 | -0.5164 | 0.3455 | abandon |
| s500-c3-r007 | ts_mean(safe_div(close - low, high - low), 63) | 0.3173 | 31.98 | 0.00153 | 0.105 | -0.2395 | abandon |
| s500-c4-r005 | ts_mean(safe_div(cap, volume), 63) | 0.3173 | 31.98 | 0.00153 | 0.105 | -0.2395 | abandon |
| s500-c1-r005 | safe_div(ts_std_dev(returns, 5), ts_std_dev(returns, 21)) * safe_div(close, ts_mean(close, 63)) | 0.3173 | 31.98 | 0.00153 | 0.105 | -0.2395 | abandon |
| s500-c5-r006 | safe_div(close, ts_max(high, 250)) * (1 - ts_min_max_diff(safe_div(close, ts_min(low, 250)), 60, 0.5)) | 0.3167 | 10.13 | 0.01409 | 0.3063 | -0.4737 | abandon |
| s500-c3-r006 | ts_mean(safe_div(close - ts_min(low, 63), ts_max(high, 63) - ts_min(low, 63)), 10) | 0.3147 | 32.8 | 0.001333 | 0.5018 | 0.003431 | abandon |
| s500-c5-r002 | -safe_div(ts_std_dev(ts_returns(close, 1), 21), ts_std_dev(ts_returns(volume, 21), 21)) | 0.313 | 20.39 | 0.008845 | -0.3534 | -1.604 | abandon |
| s500-c2-r003 | -(safe_div(ts_range(low, 10), ts_range(low, 120)) - safe_div(ts_range(high, 10), ts_range(high, 120))) | 0.3097 | 85.64 | -0.001816 | 1.022 | -0.4715 | abandon |
| s500-c5-r005 | 0.0 - ts_zscore(cap, 250) + ts_zscore(safe_div(cap, close), 250) | 0.3092 | 10.76 | -0.005241 | -0.1072 | 0.1437 | abandon |
| s500-c7-r002 | -1 * safe_div(safe_div(ts_mean(high - low, 5), ts_mean(close, 5)), safe_div(ts_mean(volume, 5), ts_mean(volume, 60))) | 0.3036 | 33.07 | 0.01214 | -0.0325 | -1.218 | abandon |
| s500-c2-r001 | ts_zscore(ts_std_dev(safe_div(close, cap), 21), 252) - ts_zscore(ts_mean(safe_div(safe_div(close, cap), volume), 21), 252) | 0.2979 | 13.54 | -6.83e-04 | 0.2074 | -0.3552 | abandon |
| s500-c4-r006 | -safe_div(ts_std_dev(ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 120)) | 0.2926 | 64.09 | 4.01e-04 | 0.2462 | 0.3396 | abandon |
| s500-c2-r004 | ts_zscore(ts_mean(safe_div(high - low, close), 60), 252) | 0.29 | 6.015 | -0.001946 | -0.1901 | 1.08 | abandon |
| s500-c1-r010 | -1 * ts_zscore(ts_range(safe_div(high - low, close), 20), 120) | 0.2872 | 16.74 | 0.002604 | 0.4054 | -0.5842 | abandon |
| s500-c1-r008 | -1 * ts_zscore(ts_std_dev(returns, 21), 252) | 0.2864 | 22.62 | 0.00374 | 0.1047 | -1.721 | abandon |
| s500-c2-r008 | -1 * ts_zscore(ts_std_dev(returns, 21), 252) | 0.2864 | 22.62 | 0.00374 | 0.1047 | -1.721 | abandon |
| s500-c2-r007 | (-1.0) * ts_zscore(ts_std_dev(returns, 20), 250) | 0.286 | 23.31 | 0.003499 | 0.1187 | -2.111 | abandon |
| s500-c2-r007 | (-1.0) * ts_zscore(ts_std_dev(returns, 20), 250) / (1.0 + abs(ts_zscore(ts_std_dev(returns, 20), 250))) | 0.286 | 23.31 | 0.003499 | 0.1187 | -2.111 | abandon |
| s500-c2-r007 | 0.0 + (-1.0) * ts_zscore(ts_std_dev(returns, 20), 250) | 0.286 | 23.31 | 0.003499 | 0.1187 | -2.111 | abandon |
| s500-c7-r001 | ts_mean(ts_returns(open, 1) - safe_div(close - open, open), 21) | 0.2858 | 79.34 | 0.004715 | 0.7722 | 0.2594 | abandon |
| s500-c4-r001 | ts_zscore(ts_mean(safe_div(close - open, open - (close - ts_delta(close, 1))), 10), 63) | 0.2857 | 37.49 | 4.90e-04 | -0.2906 | 0.08526 | abandon |
| s500-c2-r008 | -1 * ts_mean(safe_div(volume, safe_div(cap, close)), 21) * ts_std_dev(safe_div(high - low, close), 21) | 0.2831 | 8.398 | 0.008631 | 0.4359 | -1.38 | abandon |
| s500-c1-r009 | -(safe_div(volume, ts_mean(volume, 40)) * safe_div(close, ts_max(close, 40))) | 0.2814 | 125.1 | -0.005855 | 0.08754 | 0.2561 | abandon |
| s500-c1-r005 | -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 20)) * abs(ts_returns(close, 5)) | 0.2777 | 90.79 | 0.00564 | -0.04151 | -0.9463 | abandon |
| s500-c4-r007 | -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) * ts_std_dev(safe_div(ts_mean(volume, 5), ts_mean(volume, 60)), 60) | 0.2768 | 64.18 | 3.65e-04 | 0.3435 | 0.3559 | abandon |
| s500-c3-r004 | -safe_div(ts_std_dev(ts_returns(close, 1), 60), ts_scale(safe_div(volume, ts_median(volume, 60)), 60, 1)) | 0.2768 | 64.18 | 3.65e-04 | 0.3435 | 0.3559 | abandon |
| s500-c4-r007 | -1 * safe_div(ts_mean(volume, 10), ts_mean(volume, 120)) | 0.2766 | 64.09 | 2.38e-04 | 0.3607 | 0.396 | abandon |
| s500-c4-r003 | 0 - safe_div(ts_mean(safe_div(high - low, close), 10), ts_std_dev(safe_div(high - low, close), 120)) | 0.2766 | 64.09 | 2.38e-04 | 0.3607 | 0.396 | abandon |
| s500-c4-r003 | 0 - safe_div(ts_mean(safe_div(high - low, close), 10), ts_mean(safe_div(high - low, close), 120)) | 0.2766 | 64.09 | 2.38e-04 | 0.3607 | 0.396 | abandon |
| s500-c4-r003 | 0 - safe_div(ts_mean(safe_div(high - low, close), 20), ts_std_dev(safe_div(high - low, close), 120)) | 0.2766 | 64.09 | 2.38e-04 | 0.3607 | 0.396 | abandon |
| s500-c1-r001 | -safe_div(ts_mean(safe_div(close * volume, cap), 20), ts_mean(safe_div(close * volume, cap), 120)) | 0.2766 | 64.09 | 2.38e-04 | 0.3607 | 0.396 | abandon |
| s500-c4-r004 | -1 * ts_mean(ts_percentage(safe_div(high - low, close), 120, 0.75), 5) | 0.2755 | 64.11 | 2.58e-04 | 0.4075 | 0.2927 | abandon |
| s500-c3-r003 | -1 * ts_zscore(safe_div(cap, ts_mean(cap, 60)) - safe_div(close, ts_mean(close, 60)), 60) | 0.2705 | 17.21 | 4.59e-04 | 0.1934 | 0.8373 | abandon |
| s500-c1-r005 | -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) * safe_div(abs(ts_returns(close, 5)), ts_std_dev(abs(ts_returns(close, 1)), 60)) | 0.2671 | 99.26 | 0.002312 | -0.5978 | -0.9858 | abandon |
| s500-c1-r007 | -(ts_mean(returns * volume, 20) / ts_median(returns * volume, 250)) | 0.2661 | 83.91 | 0.001164 | 0.5052 | -0.5799 | abandon |
| s500-c4-r010 | -safe_div(ts_mean(safe_div(high - low, close), 21), ts_mean(safe_div(volume, ts_mean(volume, 63)), 21)) | 0.2608 | 64.62 | 4.10e-04 | 0.3968 | 0.1353 | abandon |
| s500-c2-r008 | -1 * ts_mean(safe_div(volume, safe_div(cap, close)), 21) * ts_mean(safe_div(high - low, close), 21) | 0.2569 | 6.016 | 0.008957 | 0.3819 | -1.339 | abandon |
| s500-c6-r002 | 0 - safe_div(close * volume, ts_mean(close * volume, 120)) | 0.256 | 117.1 | -0.004989 | 0.256 | -0.05322 | abandon |
| s500-c4-r009 | -(ts_std_dev(ts_returns(close, 1), 63) / ts_mean(ts_std_dev(ts_returns(close, 1), 5), 63)) | 0.2545 | 24.29 | 0.002145 | 0.7754 | -0.5764 | abandon |
| s500-c3-r004 | -safe_div(ts_mean(close, 21), ts_mean(close, 189)) | 0.2543 | 63.02 | 2.63e-04 | 0.5347 | 0.24 | abandon |
| s500-c1-r001 | -safe_div(ts_mean(ts_delta(open, 1) - open, 20), ts_mean(close - open, 20)) | 0.2515 | 76.83 | 0.001805 | 0.07666 | -0.5409 | abandon |
| s500-c7-r002 | -1 * ts_bollinger_position(ts_mean(close, 5), 200, 2.0) | 0.2506 | 7.778 | -0.006356 | 0.03558 | -0.05348 | optimize |
| s500-c1-r003 | -ts_zscore(ts_returns(open, 1) - ts_returns(close, 1), 60) | 0.2469 | 188.8 | -0.001182 | -0.3528 | 0.1983 | abandon |
| s500-c1-r003 | -(safe_div(close - ts_min(low, 250), ts_max(high, 250) - ts_min(low, 250)) - ts_zscore(safe_div(high - low, close), 20)) | 0.2469 | 68.05 | -0.005489 | 0.00509 | 0.6886 | abandon |
| s500-c3-r001 | -1 * ts_mean(safe_div(volume * close, cap), 60) | 0.2458 | 4.148 | 0.007534 | 0.2661 | -1.204 | optimize |
| s500-c3-r006 | -safe_div(ts_mean(safe_div(volume * close, cap), 5), ts_mean(safe_div(volume * close, cap), 63)) | 0.2457 | 64.96 | 1.52e-04 | 0.3932 | 0.08245 | abandon |
| s500-c4-r009 | -(safe_div(volume, ts_median(volume, 63))) | 0.2457 | 64.96 | 1.52e-04 | 0.3932 | 0.08245 | abandon |
| s500-c4-r009 | -(safe_div(volume, ts_mean(volume, 63))) | 0.2457 | 64.96 | 1.52e-04 | 0.3932 | 0.08245 | abandon |
| s500-c2-r008 | -1 * ts_mean(safe_div(volume, safe_div(cap, close)), 63) * ts_mean(safe_div(high - low, close), 21) | 0.2457 | 64.96 | 1.52e-04 | 0.3932 | 0.08245 | abandon |
| s500-c3-r010 | -1 * safe_div(ts_mean(volume, 5), ts_median(volume, 63)) | 0.2457 | 64.96 | 1.52e-04 | 0.3932 | 0.08245 | abandon |
| s500-c3-r010 | -1 * safe_div(ts_mean(safe_div(high - low, close), 10), ts_mean(safe_div(high - low, close), 63)) | 0.2457 | 64.96 | 1.52e-04 | 0.3932 | 0.08245 | abandon |
| s500-c4-r009 | -(ts_bollinger_width(close, 63, 2.0)) | 0.2457 | 64.96 | 1.52e-04 | 0.3932 | 0.08245 | abandon |
| s500-c3-r010 | -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 63)) | 0.2457 | 64.96 | 1.52e-04 | 0.3932 | 0.08245 | abandon |
| s500-c4-r010 | -safe_div(ts_mean(safe_div(high - low, close), 21), ts_mean(safe_div(volume, ts_mean(volume, 126)), 21)) | 0.2455 | 63.79 | 4.75e-04 | 0.3307 | 0.224 | abandon |
| s500-c3-r004 | safe_div(close, ts_mean(close, 126)) * safe_div(returns, ts_mean(returns, 126)) | 0.2431 | 202.1 | -0.007327 | -0.4197 | -0.3368 | abandon |
| s500-c4-r005 | safe_div(cap, ts_mean(volume, 21)) | 0.2395 | 32.06 | -0.001169 | 0.6678 | -1.228 | abandon |
| s500-c5-r005 | safe_div(ts_mean(safe_div(high - low, close), 20), ts_mean(safe_div(high - low, close), 60)) | 0.2383 | 17.57 | -0.001183 | 0.01514 | -0.2468 | abandon |
| s500-c3-r010 | -1 * ts_std_dev(ts_returns(close, 1), 21) | 0.2376 | 16.47 | 0.01223 | -0.1334 | -1.265 | abandon |
| s500-c7-r003 | safe_div(ts_mean(safe_div(volume, cap), 20) * safe_div(ts_mean(close, 120), ts_mean(close, 20)), ts_mean(safe_div(volume, cap), 120)) - 1 | 0.2372 | 11.2 | -0.004404 | 0.154 | -0.1494 | abandon |
| s500-c3-r004 | -ts_returns(close, 189, 1) * safe_div(ts_mean(close, 21), ts_mean(close, 189)) | 0.2334 | 16.48 | -0.007879 | -0.206 | -0.5166 | abandon |
| s500-c1-r004 | -1 * ts_std_dev(ts_returns(close, 1), 60) | 0.2333 | 64.92 | 2.61e-04 | 0.3737 | 0.2206 | abandon |
| s500-c4-r006 | -safe_div(ts_std_dev(ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 60)) | 0.2333 | 64.92 | 2.61e-04 | 0.3737 | 0.2206 | abandon |
| s500-c1-r010 | -1 * ts_std_dev(ts_returns(close, 1, 1), 60) * safe_div(ts_mean(cap, 21), ts_mean(cap, 21)) | 0.2333 | 64.92 | 2.61e-04 | 0.3737 | 0.2206 | abandon |
| s500-c5-r005 | 0.0 - (ts_std_dev(ts_returns(close, 1, 0), 20) + safe_div(ts_mean(volume, 20), ts_mean(volume, 60))) | 0.2331 | 17.7 | 0.01159 | -0.1271 | -1.154 | abandon |
| s500-c7-r003 | ts_zscore(ts_mean(safe_div((high - low), volume * close), 126), 126) | 0.233 | 8.833 | 0.001076 | -0.4189 | 0.7321 | abandon |
| s500-c5-r004 | -1 * ts_std_dev(ts_returns(close, 1, 0), 20) | 0.2315 | 17.11 | 0.01223 | -0.1112 | -1.3 | abandon |
| s500-c3-r001 | -1 * ts_std_dev(ts_returns(close, 1), 20) | 0.2315 | 17.11 | 0.01223 | -0.1112 | -1.3 | abandon |
| s500-c1-r003 | safe_div(abs(ts_delta(close, 20)), ts_sum(high - low, 20)) | 0.2313 | 34.45 | 7.68e-05 | 0.6527 | -1.355 | abandon |
| s500-c2-r003 | ts_mean(abs(returns), 10) - ts_mean(abs(returns), 63) | 0.2295 | 28.89 | -0.001376 | -0.1492 | 0.5579 | abandon |
| s500-c7-r001 | -1 * ts_mean(safe_div(volume * close, cap), 63) | 0.2286 | 4.023 | 0.007437 | 0.3135 | -1.189 | abandon |
| s500-c6-r003 | -(ts_mean(safe_div(high - low, close), 60) + ts_std_dev(safe_div(high - low, close), 60)) | 0.2218 | 5.958 | 0.01176 | 0.04034 | -1.351 | abandon |
| s500-c4-r004 | -1 * ts_mean(ts_percentage(safe_div(high - low, close), 252, 0.9), 5) | 0.2205 | 62.15 | 2.28e-04 | 0.4051 | 0.08947 | abandon |
| s500-c7-r003 | ts_mean(safe_div(close - low, high - low), 21) + ts_mean(ts_returns(close, 5), 21) * safe_div(open, close) | 0.2184 | 0.0477 | 0.09407 | - | - | abandon |
| s500-c5-r004 | -1 * ts_std_dev(ts_returns(close, 1, 0), 60) | 0.2172 | 7.426 | 0.01265 | -0.09239 | -1.355 | abandon |
| s500-c5-r005 | 0.0 - ts_std_dev(ts_returns(close, 1, 0), 20) * safe_div(ts_mean(volume, 20), ts_mean(volume, 60)) | 0.2155 | 18.09 | 0.0106 | -0.03322 | -1.028 | optimize |
| s500-c1-r006 | -1 * safe_div(ts_mean(close, 10) - ts_mean(close, 200), ts_mean(close, 200)) | 0.2137 | 6.214 | -0.007962 | -0.004651 | 0.02758 | abandon |
| s500-c7-r001 | safe_div(ts_mean(safe_div(high - low, close), 63), ts_mean(abs(ts_returns(close, 1)), 63)) | 0.2127 | 18.45 | 0.004226 | -0.5756 | -1.445 | abandon |
| s500-c4-r007 | -1 * safe_div(ts_mean(volume, 20) * close, cap) | 0.2125 | 5.969 | 0.006909 | 0.3078 | -1.184 | abandon |
| s500-c4-r007 | -1 * safe_div(ts_mean(volume, 20) * close, cap) + safe_div(ts_mean(volume, 20) * close, cap) * 0 | 0.2125 | 5.969 | 0.006909 | 0.3078 | -1.184 | abandon |
| s500-c1-r006 | -1 * safe_div(ts_mean(close, 10), ts_mean(close, 200)) | 0.2114 | 63.02 | 7.61e-05 | 0.5045 | 0.2652 | abandon |
| s500-c4-r006 | -safe_div(ts_median(safe_div(volume, cap), 21), ts_median(safe_div(volume, cap), 252)) | 0.2087 | 10.87 | 0.006029 | -0.1398 | 0.4373 | abandon |
| s500-c2-r003 | -safe_div(ts_mean(volume * close, 5), ts_mean(ts_median(volume * close, 5), 60)) | 0.2066 | 64.93 | 8.60e-05 | 0.3118 | 0.0815 | abandon |
| s500-c3-r010 | -1 * ts_std_dev(ts_returns(close, 1), 63) | 0.2066 | 64.93 | 8.60e-05 | 0.3118 | 0.0815 | abandon |
| s500-c1-r002 | -1 * ts_mean(safe_div(ts_mean(safe_div(close * volume, cap), 5), ts_mean(safe_div(close * volume, cap), 60)), 5) | 0.2066 | 64.93 | 8.60e-05 | 0.3118 | 0.0815 | abandon |
| s500-c4-r009 | -(ts_std_dev(ts_returns(close, 1), 63)) | 0.2066 | 64.93 | 8.60e-05 | 0.3118 | 0.0815 | abandon |
| s500-c3-r005 | -1 * safe_div(safe_div(volume, close), ts_mean(safe_div(volume, close), 252)) * 1000 | 0.2041 | 62.28 | 8.89e-06 | 0.5213 | 0.04841 | abandon |
| s500-c4-r010 | -safe_div(ts_mean(cap, 20), ts_mean(cap, 252)) | 0.2041 | 62.28 | 8.89e-06 | 0.5213 | 0.04841 | abandon |
| s500-c3-r006 | -safe_div(safe_div(close, ts_mean(close, 252)), cap) | 0.2041 | 62.28 | 8.89e-06 | 0.5213 | 0.04841 | abandon |
| s500-c2-r001 | -1 * safe_div(ts_mean(close, 21) - ts_min(low, 252), ts_max(high, 252)) * safe_div(ts_max(high, 21), ts_max(high, 252)) | 0.2041 | 62.28 | 8.89e-06 | 0.5213 | 0.04841 | abandon |
| s500-c4-r006 | -safe_div(ts_mean(safe_div(volume, cap), 21), ts_mean(safe_div(volume, cap), 252)) | 0.2041 | 62.28 | 8.89e-06 | 0.5213 | 0.04841 | abandon |
| s500-c3-r006 | -safe_div(safe_div(close, ts_mean(close, 252)), safe_div(cap, ts_mean(cap, 252))) | 0.2041 | 62.28 | 8.89e-06 | 0.5213 | 0.04841 | abandon |
| s500-c1-r003 | -(ts_bollinger_position(close, 250, 2.0) - ts_zscore(safe_div(high - low, close), 20)) | 0.2038 | 67.85 | -0.002662 | 0.1326 | 0.7913 | abandon |
| s500-c5-r004 | -1 * ts_ema(safe_div(high - low, close), 20) | 0.2014 | 15.14 | 0.01212 | -0.01631 | -1.378 | abandon |
| s500-c4-r010 | -ts_zscore(safe_div(ts_mean(safe_div(high - low, close), 21), ts_mean(safe_div(volume, ts_mean(volume, 63)), 21)), 252) | 0.1998 | 13.13 | 0.001318 | -0.1176 | -1.238 | abandon |
| s500-c3-r009 | safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120)) | 0.1969 | 38.53 | 3.59e-04 | -0.4821 | -0.1866 | abandon |
| s500-c1-r001 | -ts_mean(safe_div(ts_delta(open, 1) - open, close - open), 20) | 0.1944 | 19.8 | 0.001027 | -0.7816 | 1.109 | abandon |
| s500-c3-r006 | safe_div(close - ts_min(low, 126), ts_max(high, 126) - ts_min(low, 126)) | 0.1915 | 38.18 | 2.29e-04 | -0.2952 | 0.9421 | abandon |
| s500-c4-r008 | ts_zscore(ts_mean(safe_div(abs(safe_div(high - low, close)), close * volume), 21), 126) | 0.1904 | 10.5 | -0.002796 | 0.1642 | 0.3715 | abandon |
| s500-c1-r006 | -1 * safe_div(ts_mean(safe_div(close * volume, cap), 20), ts_median(safe_div(close * volume, cap), 250)) | 0.1897 | 62.21 | -2.86e-06 | 0.4979 | 0.1965 | abandon |
| s500-c3-r001 | -1 * ts_mean(safe_div(volume * close, cap), 250) | 0.1897 | 62.21 | -2.86e-06 | 0.4979 | 0.1965 | abandon |
| s500-c2-r003 | -safe_div(ts_mean(volume * close, 5), ts_mean(volume * close, 60)) | 0.1879 | 64.98 | 2.03e-04 | 0.472 | 0.3401 | abandon |
| s500-c2-r006 | -(ts_mean(volume, 5) / ts_mean(volume, 60)) | 0.1879 | 64.98 | 2.03e-04 | 0.472 | 0.3401 | abandon |
| s500-c2-r003 | -safe_div(ts_mean(volume / close, 5), ts_mean(volume / close, 60)) | 0.1879 | 64.98 | 2.03e-04 | 0.472 | 0.3401 | abandon |
| s500-c3-r009 | -safe_div(ts_median(volume, 60), ts_median(cap, 60)) | 0.1879 | 64.98 | 2.03e-04 | 0.472 | 0.3401 | abandon |
| s500-c3-r005 | -1 * safe_div(ts_mean(safe_div(volume, close), 5), ts_mean(safe_div(volume, close), 60)) | 0.1879 | 64.98 | 2.03e-04 | 0.472 | 0.3401 | abandon |
| s500-c1-r009 | -safe_div(ts_mean(safe_div((high - low), close), 5), ts_mean(safe_div((high - low), close), 60)) | 0.1879 | 64.98 | 2.03e-04 | 0.472 | 0.3401 | abandon |
| s500-c4-r007 | -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | 0.1879 | 64.98 | 2.03e-04 | 0.472 | 0.3401 | abandon |
| s500-c1-r002 | -1 * safe_div(ts_mean(safe_div(close * volume, cap), 5), ts_mean(safe_div(close * volume, cap), 60)) | 0.1879 | 64.98 | 2.03e-04 | 0.472 | 0.3401 | abandon |
| s500-c1-r008 | -1 * safe_div(ts_std_dev(returns, 21), ts_std_dev(returns, 252)) | 0.1846 | 62.31 | -2.87e-05 | 0.463 | 0.03085 | abandon |
| s500-c4-r006 | -safe_div(ts_std_dev(ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 252)) | 0.1846 | 62.31 | -2.87e-05 | 0.463 | 0.03085 | abandon |
| s500-c3-r010 | safe_div(ts_delta(close, 252), ts_mean(close, 21)) | 0.1826 | 6.289 | 0.01152 | -0.05163 | 0.7485 | abandon |
| s500-c6-r002 | ts_sum(close / open, 20) - ts_sum(open / ts_delta(open, 1), 20) | 0.1817 | 22.76 | 1.98e-04 | 0.3228 | -0.1091 | abandon |
| s500-c4-r004 | -1 * ts_zscore(ts_mean(safe_div(abs(ts_returns(close, 1)), close * volume), 20), 120) | 0.1813 | 16.64 | 0.002528 | -0.03447 | -0.5201 | abandon |
| s500-c1-r010 | -1 * safe_div(ts_mean(cap, 21), ts_mean(close, 21)) | 0.1812 | 65.26 | 3.03e-04 | 0.2861 | 0.4286 | abandon |
| s500-c1-r010 | -1 * ts_mean(safe_div(cap, close), 21) | 0.1812 | 65.26 | 3.03e-04 | 0.2861 | 0.4286 | abandon |
| s500-c3-r005 | -1 * safe_div(safe_div(volume, close), ts_mean(safe_div(volume, close), 20)) | 0.1809 | 65.31 | 1.48e-04 | 0.3038 | 0.2999 | abandon |
| s500-c3-r004 | -safe_div(ts_mean(close, 20) - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) | 0.1809 | 65.31 | 1.48e-04 | 0.3038 | 0.2999 | abandon |
| s500-c3-r009 | -safe_div(ts_mean(volume, 20), ts_mean(cap, 20)) | 0.1809 | 65.31 | 1.48e-04 | 0.3038 | 0.2999 | abandon |
| s500-c5-r004 | ts_returns(close, 120, 0) - ts_returns(close, 10, 0) | 0.1778 | 9.237 | 0.008918 | -0.006498 | 0.6478 | abandon |
| s500-c3-r001 | -1 * safe_div(ts_std_dev(ts_returns(close, 1), 20), ts_std_dev(ts_returns(close, 1), 250)) | 0.1745 | 62.15 | -1.06e-04 | 0.5005 | 0.2869 | abandon |
| s500-c3-r001 | -1 * safe_div(ts_std_dev(returns, 20), ts_std_dev(returns, 250)) | 0.1745 | 62.15 | -1.06e-04 | 0.5005 | 0.2869 | abandon |
| s500-c7-r003 | ts_zscore(ts_median(safe_div(safe_div(high - low, close), volume), 63), 252) | 0.1742 | 6.049 | 0.001495 | -0.09536 | 1.168 | abandon |
| s500-c2-r003 | -safe_div(safe_div(ts_range(high, 10), ts_range(low, 10)), ts_mean(safe_div(ts_max(high, 8), ts_min(low, 8)), 60)) | 0.1735 | 64.93 | -6.43e-05 | 0.2785 | -0.03267 | abandon |
| s500-c2-r008 | -1 * ts_zscore(ts_std_dev(returns, 63), 252) | 0.173 | 11.67 | 0.001614 | 0.4508 | -1.786 | abandon |
| s500-c4-r004 | (close - ts_ema(close, 120)) * safe_div(ts_mean(volume, 20), volume) / safe_div(ts_std_dev(returns, 20), ts_median(ts_std_dev(returns, 120), 60)) | 0.1725 | 14.97 | 0.002054 | -0.3965 | -0.1169 | optimize |
| s500-c7-r003 | -(safe_div(ts_std_dev(ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 60)) - 1) | 0.1716 | 42.61 | 0.00154 | 0.2512 | -0.8955 | abandon |
| s500-c2-r008 | -1 * ts_returns(close, 5) * ts_zscore(volume, 20) | 0.1704 | 153.7 | 9.90e-04 | -0.5472 | -0.1498 | abandon |
| s500-c6-r002 | 0 - safe_div(ts_max(close * volume, 20), ts_mean(close * volume, 120)) | 0.162 | 17.11 | 0.002011 | 0.977 | 0.3359 | abandon |
| s500-c3-r005 | -1 * safe_div(ts_sum(ts_returns(open, 1) - ts_returns(close, 1), 20), ts_sum(ts_returns(open, 1) + ts_returns(close, 1), 20)) | 0.1616 | 107.9 | 6.52e-04 | -0.2321 | -0.7961 | abandon |
| s500-c1-r001 | -safe_div(ts_mean(safe_div(close - low, high - low), 20), ts_mean(ts_range(high - low, 20), 20)) | 0.1606 | 65.28 | -1.85e-04 | 0.3453 | 0.21 | abandon |
| s500-c3-r003 | -1 * ts_zscore(ts_mean(safe_div(high - low, close), 20), 60) | 0.16 | 29.67 | 0.001937 | -0.1882 | -0.5234 | abandon |
| s500-c2-r007 | 0.0 + (-1.0) * ts_zscore(ts_mean(safe_div(high - low, close), 20), 60) | 0.16 | 29.67 | 0.001937 | -0.1882 | -0.5234 | abandon |
| s500-c2-r008 | -1 * safe_div(ts_std_dev(returns, 63), ts_mean(ts_std_dev(returns, 63), 252)) | 0.1568 | 10.77 | 0.004248 | 0.008425 | -1.676 | abandon |
| s500-c2-r001 | -1 * safe_div(ts_std_dev(abs(returns) - returns, 20), ts_std_dev(abs(returns) - returns, 252)) * safe_div(returns, ts_returns(close, 1)) | 0.1562 | 48.25 | 4.11e-05 | 0.1686 | -0.2303 | abandon |
| s500-c3-r008 | safe_div(ts_ema(returns, 60) - ts_ema(returns, 120), ts_std_dev(returns, 20)) * (1 / (1 + ts_zscore(ts_std_dev(returns, 20), 120))) | 0.1557 | 64.54 | -0.004596 | -0.3954 | 0.7849 | abandon |
| s500-c1-r008 | -1 * ts_zscore(ts_std_dev(returns, 10), 63) | 0.1497 | 45.57 | 0.001687 | 0.254 | -1.239 | abandon |
| s500-c5-r001 | ts_zscore(safe_div(ts_std_dev(ts_returns(close, 1), 40), abs(ts_returns(close, 40))), 250) | 0.1492 | 39.69 | 9.89e-04 | -0.06608 | -0.6953 | abandon |
| s500-c2-r003 | ts_zscore(safe_div(ts_mean(abs(returns), 5), ts_mean(abs(returns), 63)), 252) | 0.1459 | 20.81 | -2.25e-04 | -0.1352 | 0.2822 | abandon |
| s500-c2-r001 | ts_av_diff(safe_div(close - ts_mean(close, 21), ts_std_dev(close, 21)) * safe_div(close, ts_returns(close, 21, 1)), 126) | 0.1385 | 39.47 | 1.95e-04 | 0.6707 | 1.164 | abandon |
| s500-c1-r009 | -ts_bollinger_position(ts_mean(safe_div((high - low), close), 20), 60, 1) | 0.1272 | 24.89 | 7.14e-04 | -0.2906 | -0.3828 | abandon |
| s500-c3-r003 | -1 * ts_sum((safe_div(volume, ts_mean(volume, 20)) - 1) * ts_returns(close, 1, 1), 20) | 0.1246 | 17.73 | 0.00424 | 0.4404 | -0.272 | abandon |
| s500-c4-r008 | ts_zscore(safe_div(ts_mean(safe_div(high - low, close), 20), ts_std_dev(safe_div(high - low, close), 60)), 126) | 0.1243 | 23.79 | 4.36e-04 | 0.5451 | -0.2492 | abandon |
| s500-c3-r003 | -1 * ts_zscore(ts_returns(cap, 60, 1) - safe_div(ts_delta(close, 60), close), 120) | 0.1227 | 27.09 | 0.002354 | -0.4393 | -0.3437 | abandon |
| s500-c7-r002 | safe_div(ts_mean(safe_div(abs(ts_returns(close, 1)), close * volume), 21), ts_median(safe_div(abs(ts_returns(close, 1)), close * volume), 126)) | 0.1207 | 13.08 | -0.003012 | -0.1166 | 0.3512 | abandon |
| s500-c5-r006 | ts_mean(safe_div(volume, ts_median(volume, 60)) * safe_div(high - low, close), 10) | 0.1202 | 21.81 | -0.01026 | 0.1624 | 1.29 | abandon |
| s500-c1-r010 | ts_mean(safe_div(close - low, high - low) * safe_div(volume, ts_mean(volume, 21)), 10) | 0.1145 | 32.59 | -0.003067 | 0.3156 | 0.4154 | abandon |
| s500-c7-r003 | -(ts_zscore(ts_mean(safe_div(volume, cap), 120), 252) + ts_zscore(ts_std_dev(ts_returns(close, 5), 120), 252)) | 0.108 | 6.845 | 0.005261 | 0.1294 | 0.2798 | abandon |
| s500-c7-r002 | safe_div(ts_mean(safe_div(abs(ts_returns(close, 1)), close * volume), 21), ts_mean(safe_div(abs(ts_returns(close, 1)), close * volume), 252)) | 0.1073 | 20.72 | -0.006076 | -0.1677 | 0.326 | abandon |
| s500-c2-r001 | ts_sum(safe_div(open, ts_delta(close, 1)) - 1, 63) - ts_sum(safe_div(close, open) - 1, 63) | 0.1053 | 14.62 | 4.86e-04 | 0.1089 | -0.6014 | abandon |
| s500-c2-r001 | ts_ir(safe_div(open, ts_delta(close, 1)) - safe_div(close, open), 63) | 0.1053 | 14.62 | 4.86e-04 | 0.1089 | -0.6014 | abandon |
| s500-c4-r007 | safe_div(ts_mean(high - low, 10), ts_mean(high - low, 120)) | 0.1044 | 32.01 | 2.89e-04 | -0.09736 | -0.1274 | abandon |
| s500-c4-r003 | ts_median(safe_div(cap, volume), 120) | 0.1044 | 32.01 | 2.89e-04 | -0.09736 | -0.1274 | abandon |
| s500-c5-r003 | ts_sum(ts_returns(close, 1) * safe_div(volume, ts_mean(volume, 42)), 21) * (1 + ts_zscore(safe_div(ts_mean(volume, 21), ts_mean(cap, 21)), 63)) | 0.1022 | 19.99 | -0.00168 | -0.3117 | 0.1452 | abandon |
| s500-c1-r006 | -1 * safe_div(ts_returns(ts_mean(close, 10), 10), ts_returns(ts_std_dev(close, 20), 20)) | 0.09627 | 73.27 | -9.23e-04 | 0.0819 | -0.2869 | abandon |
| s500-c3-r009 | safe_div(ts_std_dev(ts_returns(close, 1), 20), ts_std_dev(ts_returns(close, 1), 120)) | 0.09015 | 15.87 | -0.002189 | -0.05867 | 0.3303 | abandon |
| s500-c1-r001 | ts_ir(ts_returns(close, 1), 120) | 0.08535 | 3.197 | 0.01055 | -0.2668 | 0.1702 | abandon |
| s500-c3-r010 | -1 * ts_zscore(safe_div(ts_mean(safe_div(high - low, close), 10), ts_mean(safe_div(high - low, close), 63)), 126) | 0.08333 | 27.77 | 0.001561 | 0.2377 | -0.07205 | abandon |
| s500-c1-r010 | safe_div(ts_returns(close, 126, 1) - ts_returns(close, 5, 1), ts_std_dev(ts_returns(close, 1, 1), 126)) | 0.08281 | 7.5 | 0.01103 | -0.03402 | 0.4646 | abandon |
| s500-c1-r001 | -safe_div(ts_zscore(ts_mean(safe_div(close * volume, cap), 20), 60), ts_std_dev(safe_div(close * volume, cap), 60)) | 0.0815 | 7.199 | 0.001772 | 0.1133 | -0.2656 | abandon |
| s500-c1-r001 | -ts_zscore(ts_mean(safe_div(close * volume, cap), 20), 60) * ts_percentage(safe_div(close * volume, cap), 60, 0.9) | 0.07884 | 7.051 | -4.01e-04 | 0.5899 | -0.09322 | abandon |
| s500-c5-r006 | -1 * safe_div(ts_mean(safe_div(high - low, close), 20), ts_mean(safe_div(high - low, close), 120)) | 0.07525 | 18.02 | 0.001921 | 0.1207 | -0.2686 | abandon |
| s500-c1-r007 | -ts_zscore(ts_ema(close * volume, 20), 250) | 0.06875 | 18.41 | -0.00307 | 0.2603 | -0.5478 | abandon |
| s500-c3-r009 | ts_std_dev(ts_returns(close, 1), 20) * safe_div(ts_std_dev(ts_returns(close, 1), 20), ts_std_dev(ts_returns(close, 1), 120)) | 0.06744 | 31.92 | -3.11e-04 | 0.3764 | 0.05525 | abandon |
| s500-c3-r005 | -1 * safe_div(ts_sum(ts_returns(open, 1) - ts_returns(close, 1), 60), ts_sum(ts_returns(open, 1) + ts_returns(close, 1), 60)) | 0.06337 | 99.96 | -0.001594 | 0.634 | 0.4801 | abandon |
| s500-c1-r004 | -1 * ts_mean((safe_div(volume, ts_mean(volume, 60)) - 1) * (safe_div(close - low, high - low) - 0.5), 10) | 0.0633 | 29.64 | 0.003283 | 0.2482 | 0.8493 | abandon |
| s500-c3-r001 | -1 * ts_zscore(ts_mean(safe_div(volume * close, cap), 60), 250) | 0.0534 | 8.209 | 0.001506 | 0.6053 | 0.5232 | abandon |
| s500-c3-r008 | -1 * ts_zscore(safe_div(volume, cap), 60) * ts_returns(close, 5) / (1 + abs(ts_returns(close, 5))) | 0.04629 | 120.8 | 2.26e-04 | 0.1078 | -0.122 | abandon |
| s500-c3-r008 | ts_mean(returns, 120) * (2 - ts_zscore(ts_std_dev(returns, 20), 120)) | 0.04533 | 12.13 | 0.004591 | 0.2791 | 0.9458 | abandon |
| s500-c2-r005 | 0 - ts_zscore(safe_div(ts_mean(volume * close, 5), ts_mean(volume * close, 63)), 126) | 0.03308 | 40.41 | -1.17e-04 | 0.1104 | -0.1601 | abandon |
| s500-c2-r007 | (-1.0) * ts_zscore(ts_mean(safe_div(high - low, close), 20), 120) | 0.02295 | 26.18 | 0.00197 | 0.01423 | -0.5729 | abandon |
| s500-c3-r001 | -1 * ts_delta(ts_mean(safe_div(high - low, close), 5), 20) | 0.02074 | 60.56 | 0.001739 | -0.3533 | -0.6767 | abandon |
| s500-c6-r003 | -safe_div(ts_std_dev(safe_div(high - low, close), 60), ts_mean(safe_div(high - low, close), 60)) | 0.008816 | 13.24 | -5.17e-04 | 1.09 | -0.3553 | abandon |
| s500-c7-r002 | -1 * ts_zscore(safe_div(volume, ts_mean(volume, 60)), 20) * ts_returns(close, 5) | 0.006685 | 151.4 | -3.64e-04 | -0.5704 | -0.122 | abandon |
| s500-c7-r003 | -(ts_zscore(ts_mean(safe_div(volume, cap), 120), 60) + ts_zscore(ts_std_dev(ts_returns(close, 1), 120), 60)) | 0.005095 | 15.78 | 0.003344 | 0.06196 | -0.9872 | abandon |
| s500-c2-r005 | ts_returns(close, 63, 1) - ts_returns(close, 5, 1) | 0.002096 | 12.41 | 0.002318 | -0.388 | 0.3057 | abandon |
| s500-c5-r006 | -1 * safe_div(ts_mean(safe_div(volume * close, cap), 20), ts_mean(safe_div(volume * close, cap), 250)) | 1.91e-04 | 12.47 | 0.001819 | 0.1712 | 0.1884 | abandon |
| s500-c2-r006 | -(ts_zscore(ts_mean(volume, 5), 60) * ts_zscore(ts_returns(close, 20), 60) * ts_zscore(ts_mean(returns, 5), 60)) | -0.003016 | 86.54 | -2.25e-04 | -0.002557 | 1.024 | abandon |
| s500-c4-r001 | ts_zscore(ts_mean(safe_div(close - low, high - low), 10), 252) * ts_zscore(safe_div(ts_mean(volume, 10), ts_mean(volume, 60)), 252) | -0.009415 | 38.27 | -5.98e-04 | -0.001322 | -0.1324 | abandon |
| s500-c2-r004 | - ts_zscore(safe_div(ts_mean(volume, 20), ts_mean(cap, 20)), 120) | -0.01233 | 12.73 | 0.002763 | 0.2138 | -0.02897 | abandon |
| s500-c5-r003 | ts_returns(close, 42) * ts_zscore(safe_div(ts_mean(volume, 42), ts_mean(cap, 42)), 63) | -0.01383 | 17.83 | 0.002009 | -0.7601 | -1.344 | abandon |
| s500-c1-r001 | -ts_zscore(ts_mean(safe_div(close * volume, cap), 20), 60) | -0.01753 | 7.907 | 7.94e-04 | 0.04106 | -0.3272 | abandon |
| s500-c2-r001 | ts_zscore(safe_div(close, cap), 21) - ts_zscore(ts_median(volume, 21), 252) | -0.01885 | 29.83 | 0.002913 | 0.2577 | 0.3925 | abandon |
| s500-c5-r007 | -1 * ts_zscore(safe_div(ts_mean(safe_div(high - low, close), 5), ts_mean(safe_div(high - low, close), 60)), 60) | -0.01978 | 59.95 | 6.98e-04 | -0.02429 | -0.4957 | abandon |
| s500-c4-r005 | 0 - ts_zscore(safe_div(ts_mean(volume, 21), cap), 252) | -0.03519 | 11.16 | 0.004184 | 0.001473 | 0.3402 | abandon |
| s500-c7-r001 | -1 * ts_mean(ts_zscore(safe_div(volume * close, cap), 252), 21) | -0.05474 | 14.05 | 0.001609 | -0.2761 | 0.1015 | abandon |
| s500-c1-r001 | ts_ir(ts_returns(close, 1), 60) | -0.05481 | 4.221 | 0.006887 | -0.2534 | -0.2328 | abandon |
| s500-c2-r007 | safe_div(ts_zscore(ts_sum(ts_returns(close, 5) * ts_returns(volume, 5), 60), 60), 0.001) | -0.0651 | 9.426 | -0.002884 | -0.3099 | -0.3182 | abandon |
| s500-c4-r006 | safe_div(ts_returns(close, 200), ts_std_dev(ts_returns(close, 1), 50)) | -0.06512 | 6.888 | 0.01011 | 0.05741 | 0.4066 | abandon |
| s500-c1-r001 | -ts_zscore(ts_std_dev(safe_div(close * volume, cap), 20), 120) | -0.06528 | 21.97 | 0.001563 | 0.4234 | 0.5904 | abandon |
| s500-c4-r008 | -1 * ts_zscore(safe_div(ts_mean(close * volume, 10), ts_mean(close * volume, 120)), 120) | -0.07063 | 25.62 | 4.14e-04 | 0.259 | 0.3053 | abandon |
| s500-c3-r004 | -(safe_div(volume, ts_median(volume, 60)) - ts_mean(safe_div(volume, ts_median(volume, 60)), 20)) * safe_div(close, close) | -0.0815 | 126.4 | -0.006869 | -0.01224 | -0.4231 | abandon |
| s500-c5-r001 | -safe_div(ts_mean(safe_div(volume, ts_mean(volume, 60)) * safe_div(high - low, close), 30), ts_mean(abs(ts_returns(close, 1)), 30)) | -0.08948 | 14.23 | -8.24e-04 | 0.7988 | 1.306 | abandon |
| s500-c2-r007 | 0.0 + (-1.0) * ts_returns(close, 5) * ts_zscore(safe_div(ts_mean(volume, 5), ts_mean(volume, 60)), 60) | -0.08958 | 50.98 | -0.002331 | -0.3709 | 0.386 | abandon |
| s500-c5-r004 | ts_returns(close, 120, 0) | -0.09111 | 8.744 | 0.005719 | -0.03336 | 0.5486 | abandon |
| s500-c1-r007 | safe_div(close - ts_min(close, 60), ts_range(close, 60)) * safe_div(ts_range(close, 250), ts_range(close, 60)) | -0.09179 | 29.37 | 7.87e-04 | -0.0558 | -0.9209 | abandon |
| s500-c4-r008 | -1 * ts_zscore(ts_mean(safe_div(high - low, close), 5), 60) | -0.09379 | 63.33 | 5.92e-04 | -0.1452 | -0.2963 | abandon |
| s500-c3-r001 | -1 * ts_zscore(ts_mean(safe_div(high - low, close), 5), 60) | -0.09379 | 63.33 | 5.92e-04 | -0.1452 | -0.2963 | abandon |
| s500-c4-r008 | -1 * (ts_mean(safe_div(high - low, close), 5) - ts_mean(safe_div(high - low, close), 60)) | -0.0998 | 57.88 | 6.66e-04 | 0.118 | -2.27e-04 | abandon |
| s500-c3-r008 | ts_mean(returns, 120) * safe_div(ts_std_dev(returns, 60), ts_std_dev(returns, 20)) | -0.1003 | 10.13 | 0.004436 | -0.011 | 0.5936 | abandon |
| s500-c1-r002 | -1 * (ts_sum(safe_div(close - open, open), 10) - ts_sum(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 10)) | -0.106 | 30.05 | -1.44e-04 | -0.2654 | -0.3355 | abandon |
| s500-c1-r002 | -1 * ts_sum(safe_div(close - open, open), 10) + ts_sum(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 10) | -0.106 | 30.05 | -1.44e-04 | -0.2654 | -0.3355 | abandon |
| s500-c3-r004 | -ts_zscore(safe_div(volume, ts_median(volume, 60)), 60) * ts_percentage(close, 21, 0.5) | -0.108 | 48.08 | -0.003912 | -0.5939 | -0.6152 | abandon |
| s500-c6-r003 | safe_div(close, ts_mean(close, 200)) - ts_mean(safe_div(high - low, close), 20) | -0.1146 | 0.6319 | 0.008539 | - | - | abandon |
| s500-c5-r006 | safe_div(close - ts_min(low, 250), ts_max(high, 250) - ts_min(low, 250)) | -0.1327 | 16.82 | -0.002084 | -0.755 | 0.6667 | abandon |
| s500-c1-r010 | safe_div(ts_returns(close, 63, 1) - ts_returns(close, 5, 1), ts_std_dev(ts_returns(close, 1, 1), 63)) | -0.1415 | 12.4 | 0.003346 | -0.3943 | -0.04083 | abandon |
| s500-c2-r005 | 0 - ts_zscore(ts_returns(close, 5, 1), 63) * ts_zscore(ts_mean(safe_div(volume, ts_mean(volume, 63)), 5), 63) | -0.1435 | 78.63 | -0.0015 | 0.03936 | 0.6171 | abandon |
| s500-c2-r007 | ts_zscore(ts_sum(ts_returns(close, 1) * safe_div(volume - ts_mean(volume, 60), ts_std_dev(volume, 60)), 60), 120) | -0.1513 | 16.23 | -0.003947 | -0.2475 | -0.4027 | abandon |
| s500-c1-r010 | safe_div(safe_div(ts_delta(close, 63) - ts_delta(close, 5), ts_mean(close, 63)), ts_std_dev(ts_returns(close, 1, 1), 63)) | -0.1537 | 12.33 | 0.003445 | -0.394 | -0.08068 | abandon |
| s500-c4-r006 | safe_div(close - ts_min(low, 40), ts_max(high, 40) - ts_min(low, 40)) | -0.157 | 42.25 | -0.00205 | -0.7406 | -1.268 | abandon |
| s500-c3-r010 | safe_div(close - ts_mean(close, 21), ts_mean(close, 21)) - safe_div(ts_mean(close, 21) - ts_mean(close, 126), ts_mean(close, 126)) | -0.1628 | 10.96 | -0.009808 | 0.007052 | -0.1587 | abandon |
| s500-c6-r001 | -1 * safe_div(ts_sum(high - low, 21), ts_range(close, 21)) | -0.1716 | 23.7 | -0.004817 | 0.826 | 1.215 | abandon |
| s500-c4-r003 | ts_mean(ts_returns(close, 20) * ts_mean(safe_div(volume, ts_mean(volume, 60)), 20), 5) | -0.1782 | 16.11 | -0.002638 | -0.07956 | 0.1947 | abandon |
| s500-c1-r008 | safe_div(close - ts_mean(close, 252), ts_std_dev(close, 252)) | -0.1791 | 9.339 | 0.007764 | -0.01567 | 0.00769 | abandon |
| s500-c3-r006 | -ts_zscore(safe_div(safe_div(close, ts_mean(close, 252)), safe_div(cap, ts_mean(cap, 252))), 63) | -0.1823 | 8.499 | 2.90e-04 | 0.1525 | -0.08023 | abandon |
| s500-c1-r010 | safe_div(safe_div(close, ts_mean(close, 200)) - 1, ts_std_dev(returns, 200) * (1 + abs(ts_zscore(ts_mean(volume, 10), 200)))) | -0.1833 | 10.09 | 0.006302 | -0.106 | 0.0986 | abandon |
| s500-c5-r006 | -1 * ts_zscore(safe_div(ts_mean(safe_div(volume * close, cap), 20), ts_mean(safe_div(volume * close, cap), 250)), 60) | -0.1962 | 19.23 | -6.72e-05 | 0.5413 | 0.3741 | abandon |
| s500-c5-r001 | safe_div(ts_returns(close, 120), ts_median(safe_div(high - low, close), 120)) | -0.2015 | 8.78 | 0.006096 | -0.07808 | 0.2662 | abandon |
| s500-c4-r006 | safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) | -0.2176 | 43.62 | -0.00302 | -0.89 | -1.255 | abandon |
| s500-c4-r006 | safe_div(close - ts_mean(close, 200), ts_mean(ts_range(close, 50), 1) * 0 + ts_std_dev(ts_returns(close, 1), 50) * close) | -0.2215 | 10.15 | 0.007033 | -0.07671 | -0.105 | abandon |
| s500-c4-r006 | safe_div(close - ts_mean(close, 200), ts_std_dev(ts_returns(close, 1), 50) * close) | -0.2215 | 10.15 | 0.007033 | -0.07671 | -0.105 | abandon |
| s500-c2-r008 | ts_delta(safe_div(close, ts_max(close, 60)), 1) | -0.2248 | 164 | -0.01098 | -0.5976 | -0.321 | abandon |
| s500-c5-r006 | ts_mean(safe_div(volume, ts_median(volume, 60)), 10) * ts_mean(safe_div(close - low, high - low), 10) | -0.2266 | 23.29 | -0.004194 | -0.6637 | 0.8034 | abandon |
| s500-c3-r006 | -ts_zscore(safe_div(ts_mean(volume, 5) * close, cap), 63) | -0.2302 | 44.11 | -0.002148 | -0.0926 | -0.974 | abandon |
| s500-c5-r006 | -1 * ts_zscore(safe_div(ts_mean(safe_div(high - low, close), 20), ts_median(safe_div(high - low, close), 120)), 120) | -0.2308 | 25.64 | -8.91e-04 | -0.02259 | 0.1627 | abandon |
| s500-c6-r001 | safe_div(ts_median(close, 21), safe_div(cap, ts_median(close, 21))) | -0.2348 | 1.323 | -0.001517 | 0.1466 | -1.354 | abandon |
| s500-c3-r010 | -1 * (safe_div(ts_mean(volume, 5), ts_mean(volume, 63)) - 1) | -0.2348 | 44.32 | -0.001693 | -0.03093 | -1.023 | abandon |
| s500-c6-r003 | safe_div(close, ts_mean(close, 200)) - safe_div(ts_mean(high - low, 20), ts_mean(high - low, 120)) | -0.2352 | 28.28 | 0.002201 | -0.03417 | 0.3633 | abandon |
| s500-c1-r010 | safe_div(safe_div(close, ts_mean(close, 200)) - 1, ts_std_dev(returns, 50)) * ts_zscore(ts_mean(volume, 10), 200) | -0.2448 | 19.54 | -0.00312 | -0.2403 | -0.01408 | abandon |
| s500-c1-r008 | safe_div(close - ts_mean(close, 126), ts_std_dev(close, 126)) | -0.2451 | 12.7 | 0.00401 | -0.1466 | -0.4113 | abandon |
| s500-c2-r005 | ts_zscore(ts_av_diff(ts_returns(close, 73, 1), 63), 252) | -0.2468 | 15.97 | -0.004119 | -0.3781 | -0.672 | abandon |
| s500-c3-r005 | -1 * ts_sum(safe_div(open, close) - safe_div(close, open), 20) | -0.2509 | 20.15 | -0.006994 | -0.2567 | 0.4263 | abandon |
| s500-c2-r006 | -(safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) - ts_mean(safe_div(ts_mean(volume, 5), ts_mean(volume, 60)), 60)) | -0.2514 | 30.7 | -0.001982 | 0.02307 | -0.8364 | abandon |
| s500-c4-r004 | ts_mean(ts_returns(close, 1) * (safe_div(volume, ts_median(volume, 60)) - 1), 60) | -0.2574 | 8.156 | -0.004682 | -0.5741 | 0.6646 | abandon |
| s500-c2-r002 | ts_zscore(safe_div(ts_returns(close, 126), ts_std_dev(ts_returns(close, 1), 126)), 252) | -0.2646 | 10.46 | -7.58e-05 | -0.1836 | -0.5741 | abandon |
| s500-c3-r004 | -ts_zscore(ts_mean(safe_div(volume, ts_median(volume, 60)), 120), 60) * safe_div(ts_std_dev(close, 60), ts_median(close, 60)) | -0.2689 | 14 | -0.001331 | 0.3879 | -0.3955 | abandon |
| s500-c2-r007 | ts_zscore(ts_sum(ts_returns(close, 1) * (volume / ts_mean(volume, 60)), 60), 60) | -0.2692 | 13.07 | -0.004811 | -0.4938 | -0.03721 | abandon |
| s500-c3-r010 | ts_zscore(ts_delta(close, 21), 147) - ts_zscore(ts_delta(close, 1), 21) | -0.27 | 36.74 | -0.002825 | -0.09992 | -0.1807 | abandon |
| s500-c3-r006 | -ts_zscore(safe_div(volume * close, cap), 63) | -0.2769 | 126.2 | -0.005828 | -0.449 | -1.103 | abandon |
| s500-c1-r001 | ts_ir(ts_returns(close, 1), 60) - ts_ir(ts_returns(close, 1), 120) | -0.2846 | 5.53 | -0.0021 | -0.1998 | -1.069 | abandon |
| s500-c4-r009 | -(ts_zscore(volume, 21) + ts_zscore(volume, 63)) | -0.2848 | 132.5 | -0.006068 | -0.4467 | -1.161 | abandon |
| s500-c1-r004 | -1 * safe_div(ts_sum(ts_returns(open, 1) - ts_returns(close, 1), 20), ts_std_dev(ts_returns(close, 1), 20)) | -0.2849 | 157.3 | -0.00865 | -0.03514 | -0.5528 | abandon |
| s500-c2-r002 | -1 * ts_zscore(safe_div(volume * close, cap), 126) | -0.2902 | 120.5 | -0.005357 | -0.2925 | -1.446 | abandon |
| s500-c2-r006 | -(ts_zscore(safe_div(ts_mean(volume, 5), ts_mean(volume, 60)), 60)) | -0.2958 | 42.66 | -0.002769 | -0.1027 | -0.523 | abandon |
| s500-c1-r006 | -1 * ts_zscore(safe_div(close * volume, cap), 60) | -0.2969 | 126.2 | -0.00598 | -0.3995 | -1.019 | abandon |
| s500-c4-r004 | ts_mean(ts_returns(close, 1) * safe_div(volume, ts_median(volume, 60)), 60) | -0.3018 | 9.087 | -0.003764 | -0.5539 | 0.5881 | abandon |
| s500-c4-r001 | ts_zscore(ts_mean(safe_div(close - low, high - low) * safe_div(volume, ts_mean(volume, 60)), 10), 252) | -0.303 | 22.98 | -0.005135 | -0.2546 | 0.795 | abandon |
| s500-c6-r001 | -1 * ts_zscore(ts_median(close, 21), 252) * ts_zscore(ts_mean(cap, 21), 252) | -0.3032 | 6.512 | -0.003814 | 0.1366 | -0.1486 | abandon |
| s500-c2-r005 | ts_zscore(ts_returns(close, 63, 1) - ts_returns(close, 5, 1), 126) | -0.3075 | 15.37 | -0.004043 | -0.2969 | -0.8706 | abandon |
| s500-c2-r002 | ts_zscore(ts_ir(ts_returns(close, 1), 126), 252) | -0.3131 | 10.52 | -1.89e-04 | -0.1725 | -0.4878 | abandon |
| s500-c4-r003 | ts_mean(ts_returns(close, 1) * ts_scale(volume, 20) / ts_std_dev(ts_returns(close, 1), 20), 20) | -0.3381 | 33.27 | -0.003888 | -0.5434 | -0.3474 | abandon |
| s500-c5-r001 | ts_returns(close, 60) * safe_div(ts_mean((high - low) / close, 10), ts_mean((high - low) / close, 60)) | -0.3453 | 12.95 | -0.001893 | -0.4126 | 0.2083 | abandon |
| s500-c2-r007 | (-1.0) * ts_returns(close, 5) * ts_zscore(ts_std_dev(volume, 5) / ts_mean(volume, 60), 60) | -0.3489 | 52.2 | -0.002692 | -0.2966 | 0.5717 | abandon |
| s500-c4-r001 | ts_zscore(ts_mean(safe_div(close - open, open - ts_delta(close, 1)), 21), 63) | -0.3645 | 22.83 | -0.006145 | -0.164 | 0.2464 | abandon |
| s500-c2-r002 | -1 * ts_zscore(safe_div(ts_ema(volume * close, 5), ts_ema(close * cap, 5)), 120) | -0.3646 | 28.64 | 5.28e-04 | -0.2319 | -0.6106 | abandon |
| s500-c5-r005 | safe_div(ts_mean(safe_div(high - low, close), 60), ts_mean(safe_div(high - low, close), 20)) * ts_bollinger_position(close, 20, 2.0) | -0.3699 | 90.32 | -0.005894 | 0.3631 | -0.1245 | abandon |
| s500-c4-r003 | ts_mean(safe_div(ts_returns(close, 1) * ts_scale(volume, 20), ts_std_dev(ts_returns(close, 1), 20)), 21) | -0.3707 | 18.01 | -0.004586 | -0.2601 | -0.1266 | abandon |
| s500-c4-r008 | -1 * ts_zscore(safe_div(volume - ts_mean(volume, 60), close), 120) | -0.3821 | 119.9 | -0.006724 | -0.1421 | -1.292 | abandon |
| s500-c5-r006 | ts_mean(safe_div(volume * close, ts_median(volume * close, 60)) * safe_div(close - low, high - low), 10) | -0.3828 | 22.45 | -0.00434 | -0.6611 | 0.6057 | abandon |
| s500-c4-r001 | safe_div(ts_returns(close, 63), ts_sum(abs(ts_returns(close, 1)), 63)) | -0.3837 | 14.86 | 0.001777 | -0.3344 | -0.2642 | abandon |
| s500-c2-r002 | -1 * ts_zscore(safe_div(ts_ema(volume * close, 5), cap), 60) | -0.3852 | 51.94 | -0.00279 | -0.1933 | -0.3228 | abandon |
| s500-c5-r006 | -1 * ts_mean(safe_div(volume, ts_median(volume, 60)), 10) * ts_mean(safe_div(volume, safe_div(high - low, close)), 10) | -0.4066 | 8.735 | -0.001704 | -0.7483 | -1.95 | abandon |
| s500-c4-r008 | -1 * ts_zscore(safe_div(ts_mean(safe_div(volume, close), 10), ts_mean(safe_div(volume, close), 120)), 120) | -0.4132 | 24.92 | -0.003002 | 0.1384 | -1.279 | abandon |
| s500-c4-r001 | safe_div(ts_returns(close, 21), ts_sum(abs(ts_returns(close, 1)), 21)) | -0.4224 | 45.91 | -0.00309 | -0.3006 | -0.3906 | abandon |
| s500-c1-r003 | safe_div(ts_delta(close, 20), ts_sum(high - low, 20)) | -0.4256 | 47.12 | -0.004126 | -0.2623 | -0.1117 | abandon |
| s500-c1-r008 | safe_div(close - ts_mean(close, 63), ts_mean(close, 63)) | -0.4369 | 13.09 | -0.002597 | -0.1403 | 0.03944 | abandon |
| s500-c1-r004 | -1 * safe_div(ts_sum(ts_returns(open, 1) - ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 10)) | -0.4623 | 157.7 | -0.008212 | -0.3337 | -0.6785 | abandon |
| s500-c6-r002 | safe_div(ts_sum(volume * ts_returns(close, 1), 60), ts_sum(volume * abs(ts_returns(close, 1)), 60)) | -0.4636 | 9.891 | -0.002637 | -0.3419 | -0.04993 | abandon |
| s500-c6-r002 | safe_div(ts_sum(volume * (ts_returns(close, 1) + abs(ts_returns(close, 1))), 60), ts_sum(volume * abs(ts_returns(close, 1)), 60)) | -0.4695 | 9.428 | -0.001551 | -0.3502 | -0.02942 | abandon |
| s500-c5-r005 | safe_div(ts_returns(close, 15, 0), safe_div(ts_mean(volume, 15), ts_mean(volume, 60))) | -0.4705 | 24.12 | -0.006397 | -0.2056 | -0.1151 | abandon |
| s500-c5-r005 | ts_returns(close, 15, 0) * safe_div(1.0, 1.0 + ts_mean(volume, 15) / ts_mean(volume, 60)) | -0.4756 | 23.87 | -0.006472 | -0.1856 | -0.1433 | abandon |
| s500-c2-r001 | ts_delta(safe_div(close, ts_mean(close, 126)), 63) | -0.4949 | 10.07 | -0.006818 | -0.4828 | -0.5997 | abandon |
| s500-c5-r001 | ts_zscore(safe_div(ts_returns(close, 120), ts_median(safe_div(high - low, close), 120)), 250) | -0.4988 | 9.233 | -0.002327 | 0.00182 | -0.6337 | abandon |
| s500-c4-r001 | ts_zscore(safe_div(ts_returns(close, 63), ts_sum(abs(ts_returns(close, 1)), 63)), 252) | -0.5187 | 13.8 | -0.002482 | -0.472 | -0.4865 | abandon |
| s500-c6-r002 | safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)) | -0.5277 | 37.1 | -0.006374 | 0.05696 | -0.6685 | abandon |
| s500-c3-r008 | -1 * ts_zscore(safe_div(volume, cap), 60) * (1 - ts_zscore(close, 20) * 0.25) | -0.5396 | 123.1 | -0.007256 | -0.4976 | -0.763 | abandon |
| s500-c5-r004 | ts_returns(close, 5, 0) * ts_mean(safe_div(volume, ts_mean(volume, 20)), 5) | -0.5411 | 78.22 | -0.01245 | 0.1805 | -0.9094 | abandon |
| s500-c7-r001 | ts_zscore(ts_sum(safe_div(open - close, close), 21) * -1, 252) | -0.5615 | 40.57 | -0.007966 | -0.4043 | -0.4778 | abandon |
| s500-c5-r004 | ts_returns(close, 5, 0) * safe_div(ts_mean(volume, 5), ts_mean(volume, 20)) | -0.5747 | 78.46 | -0.01259 | 0.11 | -0.9532 | abandon |
| s500-c3-r009 | safe_div(close - ts_max(close, 60), ts_max(high, 60) - ts_min(low, 60)) | -0.6133 | 14.86 | -0.002122 | -0.2142 | -0.248 | abandon |
| s500-c3-r008 | -1 * ts_zscore(safe_div(volume, cap), 60) + 0.5 * ts_zscore(close, 60) | -0.6535 | 37.96 | -0.0035 | -0.2276 | -0.4965 | abandon |
| s500-c3-r001 | -1 * (ts_zscore(returns, 5) - ts_zscore(returns, 250)) | -0.6611 | 139.6 | -0.009338 | -0.4487 | -0.7967 | abandon |
| s500-c3-r008 | -1 * ts_zscore(safe_div(volume, cap), 60) * (1 - ts_std_dev(ts_returns(close, 5), 5)) | -0.6682 | 123 | -0.00787 | -0.4927 | -1.019 | abandon |
| s500-c1-r003 | ts_ir(safe_div(ts_delta(close, 1), ts_sum(high - low, 1)), 20) | -0.6786 | 25.17 | -0.00143 | -0.2527 | -0.5047 | abandon |
| s500-c4-r009 | -(0.5 + safe_div(close - ts_min(low, 5), close - ts_max(high, 5))) | -0.7417 | 54.66 | -0.01201 | -0.7823 | -0.3542 | abandon |
| s500-c5-r004 | ts_mean(safe_div(close, open) - 1, 5) | -0.7431 | 45.99 | -0.01018 | -0.4566 | -0.1125 | abandon |
| s500-c2-r004 | ts_zscore(ts_mean(safe_div(close - low, high - low), 20), 120) | -0.7917 | 23.08 | -0.007313 | -0.1585 | -0.09522 | abandon |
| s500-c4-r005 | 0 - ts_zscore(ts_sum(safe_div(open - close, close), 5), 63) | -1.004 | 45.77 | -0.01012 | -0.1154 | -0.2833 | abandon |
| s500-c2-r006 | ts_mean(safe_div(2 * close - high - low, ts_max(high, 1) - ts_min(low, 1)), 10) | -1.11 | 27.79 | -0.006495 | -0.217 | 0.7684 | abandon |
| s500-c3-r006 | ts_mean(ts_zscore(safe_div(close - low, high - low), 20), 10) | -1.317 | 37.12 | -0.007687 | -0.3246 | -0.04439 | optimize |

## Figures

| rank | factor | hypothesis | run | IS | OOS | holdout | decision | figure |
|---|---|---|---|---|---|---|---|---|
| 1 | `H03-F02` | 日内收盘位置：收盘价靠近区间低点预示短期反弹 | `s500-c4-r009` | 2.621 | 0.365 | 0.259 | optimize | `figures/rank001_s500-c4-r009_H03-F02.png` |
| 2 | `H03-F02` | Intraday order imbalance from the closing clip as a short-horizon inde | `s500-c2-r002` | 2.210 | 0.150 | 0.629 | accept | `figures/rank002_s500-c2-r002_H03-F02.png` |
| 3 | `H03-F01` | 日内收盘位置：收盘价靠近区间低点预示短期反弹 | `s500-c4-r009` | 2.059 | 0.127 | 0.054 | optimize | `figures/rank003_s500-c4-r009_H03-F01.png` |
| 4 | `H04-F01` | 收盘位于区间上沿的短期反转（日内位置效应） | `s500-c6-r003` | 2.059 | 0.127 | 0.054 | abandon | `figures/rank004_s500-c6-r003_H04-F01.png` |
| 5 | `H01-F02` | 日内收益位置：收盘在当日振幅中的相对位置（Close Location Value） | `s500-c4-r005` | 2.052 | -0.070 | -0.491 | accept | `figures/rank005_s500-c4-r005_H01-F02.png` |
| 6 | `H03-F02` | Close positioned near the session low signals short-horizon supply pre | `s500-c7-r001` | 1.947 | 0.097 | 0.003 | optimize | `figures/rank006_s500-c7-r001_H03-F02.png` |
| 7 | `H03-F01` | Intraday order imbalance from the closing clip as a short-horizon inde | `s500-c2-r002` | 1.898 | -0.014 | 0.868 | accept | `figures/rank007_s500-c2-r002_H03-F01.png` |
| 8 | `H05-F02` | Stock-specific volatility expansion relative to its own baseline as an | `s500-c2-r006` | 1.801 | -0.097 | -0.116 | abandon | `figures/rank008_s500-c2-r006_H05-F02.png` |
| 9 | `H04-F02` | 收盘位于区间上沿的短期反转（日内位置效应） | `s500-c6-r003` | 1.749 | 0.089 | 0.564 | optimize | `figures/rank009_s500-c6-r003_H04-F02.png` |
| 10 | `H03-F03` | Intraday order imbalance from the closing clip as a short-horizon inde | `s500-c2-r002` | 1.683 | 0.121 | -0.450 | optimize | `figures/rank010_s500-c2-r002_H03-F03.png` |
| 11 | `H04-F01` | 收盘持续位于日内区间高位的个股短期收益回吐 | `s500-c4-r010` | 1.683 | 0.121 | -0.450 | accept | `figures/rank011_s500-c4-r010_H04-F01.png` |
| 12 | `H01-F02` | Cross-sectional short-term reversal of adjusted close over 1-5 trading | `s500-c1-r005` | 1.493 | 0.667 | 0.459 | abandon | `figures/rank012_s500-c1-r005_H01-F02.png` |
| 13 | `H02-F02` | Market-cap repair after a drawdown: names that recovered capitalisatio | `s500-c3-r007` | 1.443 | 0.438 | 0.082 | accept | `figures/rank013_s500-c3-r007_H02-F02.png` |
| 14 | `H02-F01` | Market-cap repair after a drawdown: names that recovered capitalisatio | `s500-c3-r007` | 1.421 | 0.431 | 0.133 | abandon | `figures/rank014_s500-c3-r007_H02-F01.png` |
| 15 | `H02-F02` | 量价背离：成交量相对基线抬升而价格盘中收在区间下沿，预示走弱 | `s500-c1-r004` | 1.413 | -0.061 | -0.181 | optimize | `figures/rank015_s500-c1-r004_H02-F02.png` |
| 16 | `H03-F03` | Index drawdown from recent high as a mean-reversion timing signal (SPY | `s500-c2-r008` | 1.401 | 0.530 | 0.124 | abandon | `figures/rank016_s500-c2-r008_H03-F03.png` |
| 17 | `H02-F01` | ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | `s500-c2-r005` | 1.390 | 0.839 | 0.652 | abandon | `figures/rank017_s500-c2-r005_H02-F01.png` |
| 18 | `H01-F03` | Short-horizon reversal: recent 5-day return negatively predicts next-w | `s500-c4-r007` | 1.385 | 0.486 | 0.308 | optimize | `figures/rank018_s500-c4-r007_H01-F03.png` |
| 19 | `H01-F02` | 近期收益的高波动放大：短窗收益/波动比作为过度反应与反转的代理 | `s500-c1-r004` | 1.365 | 0.200 | 0.785 | abandon | `figures/rank019_s500-c1-r004_H01-F02.png` |
| 20 | `H01-F01` | 近期收益的高波动放大：短窗收益/波动比作为过度反应与反转的代理 | `s500-c1-r004` | 1.365 | 0.200 | 0.785 | abandon | `figures/rank020_s500-c1-r004_H01-F01.png` |
| 21 | `H01-F01` | 日内收益位置：收盘在当日振幅中的相对位置（Close Location Value） | `s500-c4-r005` | 1.359 | 0.115 | -0.679 | optimize | `figures/rank021_s500-c4-r005_H01-F01.png` |
| 22 | `H01-F01` | 短期上涨与价格偏离后的反转 | `s500-c5-r004` | 1.353 | 0.304 | 0.619 | optimize | `figures/rank022_s500-c5-r004_H01-F01.png` |
| 23 | `H03-F02` | Index drawdown from recent high as a mean-reversion timing signal (SPY | `s500-c2-r008` | 1.327 | 0.268 | -0.160 | optimize | `figures/rank023_s500-c2-r008_H03-F02.png` |
| 24 | `H04-F02` | 市场区间恐慌度：大盘区间位置贴近低位预示短期反弹 | `s500-c4-r009` | 1.314 | 0.090 | 0.455 | optimize | `figures/rank024_s500-c4-r009_H04-F02.png` |
| 25 | `H03-F01` | Short-horizon overreaction in illiquid names reverses more strongly | `s500-c3-r008` | 1.300 | 0.287 | 0.866 | optimize | `figures/rank025_s500-c3-r008_H03-F01.png` |
| 26 | `H01-F03` | Cross-sectional short-term reversal of adjusted close over 1-5 trading | `s500-c1-r005` | 1.296 | 0.191 | 0.592 | optimize | `figures/rank026_s500-c1-r005_H01-F03.png` |
| 27 | `H02-F02` | ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | `s500-c2-r005` | 1.293 | 0.887 | 0.716 | abandon | `figures/rank027_s500-c2-r005_H02-F02.png` |
| 28 | `H01-F02` | Short-horizon reversal: recent 5-day return negatively predicts next-w | `s500-c4-r007` | 1.285 | 0.277 | 0.745 | optimize | `figures/rank028_s500-c4-r007_H01-F02.png` |
| 29 | `H02-F03` | ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | `s500-c2-r005` | 1.284 | 0.884 | 0.715 | abandon | `figures/rank029_s500-c2-r005_H02-F03.png` |
| 30 | `H01-F02` | Short-horizon reversal under abnormal volume | `s500-c3-r001` | 1.280 | 0.274 | 0.745 | optimize | `figures/rank030_s500-c3-r001_H01-F02.png` |
| 31 | `H01-F03` | 短期价格反转：5日收益的横截面反转为正（价格压力 vs 基本面信息） | `s500-c3-r003` | 1.272 | 0.085 | 0.801 | abandon | `figures/rank031_s500-c3-r003_H01-F03.png` |
| 32 | `H01-F03` | ETF 反转：短期急涨后回落（SPY 日频短期反转） | `s500-c2-r005` | 1.254 | 0.077 | 0.773 | abandon | `figures/rank032_s500-c2-r005_H01-F03.png` |
| 33 | `H01-F01` | Cross-sectional short-term reversal of adjusted close over 1-5 trading | `s500-c1-r005` | 1.254 | 0.077 | 0.773 | optimize | `figures/rank033_s500-c1-r005_H01-F01.png` |
| 34 | `H01-F01` | 短期价格反转：5日收益的横截面反转为正（价格压力 vs 基本面信息） | `s500-c3-r003` | 1.254 | 0.077 | 0.773 | optimize | `figures/rank034_s500-c3-r003_H01-F01.png` |
| 35 | `H02-F03` | Short-horizon return reversal within the mega-cap cross-section | `s500-c2-r003` | 1.251 | 0.083 | 0.768 | optimize | `figures/rank035_s500-c2-r003_H02-F03.png` |
| 36 | `H02-F03` | Open-to-close intraday return over a week predicts reversal: persisten | `s500-c3-r005` | 1.250 | 0.194 | 0.270 | optimize | `figures/rank036_s500-c3-r005_H02-F03.png` |
| 37 | `H01-F02` | Cross-sectional abnormal-volume price shock reversal | `s500-c2-r008` | 1.242 | 0.094 | 0.755 | optimize | `figures/rank037_s500-c2-r008_H01-F02.png` |
| 38 | `H01-F03` | Cross-sectional abnormal-volume price shock reversal | `s500-c2-r008` | 1.242 | 0.094 | 0.755 | optimize | `figures/rank038_s500-c2-r008_H01-F03.png` |
| 39 | `H02-F01` | Short-horizon return reversal within the mega-cap cross-section | `s500-c2-r003` | 1.241 | 0.093 | 0.758 | abandon | `figures/rank039_s500-c2-r003_H02-F01.png` |
| 40 | `H01-F01` | Short-horizon reversal: recent 5-day return negatively predicts next-w | `s500-c4-r007` | 1.241 | 0.093 | 0.758 | optimize | `figures/rank040_s500-c4-r007_H01-F01.png` |
| 41 | `H01-F01` | ETF 反转：短期急涨后回落（SPY 日频短期反转） | `s500-c2-r005` | 1.237 | -0.268 | 0.628 | optimize | `figures/rank041_s500-c2-r005_H01-F01.png` |
| 42 | `H04-F02` | Attention-Driven Volume Surge with Recent Price Strength as a Short-Ho | `s500-c7-r002` | 1.232 | 0.278 | 0.720 | optimize | `figures/rank042_s500-c7-r002_H04-F02.png` |
| 43 | `H02-F03` | Range asymmetry: close near the session low after a wide range signals | `s500-c1-r001` | 1.229 | 0.606 | -0.541 | optimize | `figures/rank043_s500-c1-r001_H02-F03.png` |
| 44 | `H02-F02` | Short-horizon return reversal within the mega-cap cross-section | `s500-c2-r003` | 1.210 | -0.245 | 0.677 | optimize | `figures/rank044_s500-c2-r003_H02-F02.png` |
| 45 | `H02-F01` | Short-horizon overreaction reversal on elevated-volume extremes | `s500-c4-r003` | 1.210 | -0.245 | 0.677 | optimize | `figures/rank045_s500-c4-r003_H02-F01.png` |
| 46 | `H04-F01` | Index overextension reverses only in stressed-volatility states | `s500-c1-r001` | 1.204 | 0.687 | -0.256 | abandon | `figures/rank046_s500-c1-r001_H04-F01.png` |
| 47 | `H03-F02` | 指数趋势位置：SPY 价格相对长期均线的相对乖离 | `s500-c4-r005` | 1.186 | 0.085 | 0.500 | accept | `figures/rank047_s500-c4-r005_H03-F02.png` |
| 48 | `H02-F01` | Open-to-close intraday return over a week predicts reversal: persisten | `s500-c3-r005` | 1.181 | 0.230 | 0.397 | abandon | `figures/rank048_s500-c3-r005_H02-F01.png` |
| 49 | `H01-F01` | Short-horizon reversal conditioned on turnover intensity: low-particip | `s500-c5-r003` | 1.169 | 0.425 | 0.157 | optimize | `figures/rank049_s500-c5-r003_H01-F01.png` |
| 50 | `H01-F02` | ETF 反转：短期急涨后回落（SPY 日频短期反转） | `s500-c2-r005` | 1.165 | -0.071 | 0.815 | abandon | `figures/rank050_s500-c2-r005_H01-F02.png` |
| 51 | `H01-F03` | 放量下跌后的短期反应不足：量价确认型反转 | `s500-c2-r007` | 1.163 | -0.037 | 0.652 | optimize | `figures/rank051_s500-c2-r007_H01-F03.png` |
| 52 | `H04-F01` | 隔夜跳空累积：近一周开盘相对前收盘的累计偏离的反转 | `s500-c4-r005` | 1.140 | 0.610 | 0.928 | optimize | `figures/rank052_s500-c4-r005_H04-F01.png` |
| 53 | `H03-F02` | 隔夜与日内收益的分离：指数层“隔夜缺口回补”的短期反转候选 | `s500-c1-r003` | 1.139 | 0.846 | 0.305 | abandon | `figures/rank053_s500-c1-r003_H03-F02.png` |
| 54 | `H02-F01` | Range asymmetry: close near the session low after a wide range signals | `s500-c1-r001` | 1.137 | 0.081 | -0.390 | optimize | `figures/rank054_s500-c1-r001_H02-F01.png` |
| 55 | `H01-F01` | 短期反转：极端收益后的过度反应修正 | `s500-c6-r003` | 1.134 | 0.191 | 0.675 | abandon | `figures/rank055_s500-c6-r003_H01-F01.png` |
| 56 | `H03-F02` | Range-position asymmetry within a stock's own yearly band predicts wea | `s500-c2-r001` | 1.098 | 0.043 | 0.480 | accept | `figures/rank056_s500-c2-r001_H03-F02.png` |
| 57 | `H02-F03` | Market-cap repair after a drawdown: names that recovered capitalisatio | `s500-c3-r007` | 1.093 | -0.003 | -0.126 | optimize | `figures/rank057_s500-c3-r007_H02-F03.png` |
| 58 | `H01-F02` | 短期反转：极端收益后的过度反应修正 | `s500-c6-r003` | 1.075 | 0.206 | 0.682 | abandon | `figures/rank058_s500-c6-r003_H01-F02.png` |
| 59 | `H01-F03` | 近期收益的高波动放大：短窗收益/波动比作为过度反应与反转的代理 | `s500-c1-r004` | 1.073 | 0.135 | 0.294 | abandon | `figures/rank059_s500-c1-r004_H01-F03.png` |
| 60 | `H04-F03` | 横截面：小市值与相对规模的负向收益预测 | `s500-c2-r005` | 1.061 | -0.077 | 0.154 | accept | `figures/rank060_s500-c2-r005_H04-F03.png` |
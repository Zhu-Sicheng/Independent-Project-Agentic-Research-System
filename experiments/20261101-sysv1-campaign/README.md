# Published results: `sysv1-campaign`

- runs: `camp-c1-r001`, `camp-c1-r002`, `camp-c1-r003`, `camp-c1-r004`, `camp-c1-r005`, `camp-c2-r001`, `camp-c2-r002`, `camp-c2-r003`, `camp-c2-r004`, `camp-c2-r005`, `camp-c2-r006`, `camp-c2-r007`, `camp-c3-r001`, `camp-c3-r002`, `camp-c3-r003`, `camp-c3-r004`, `camp-c4-r001`, `camp-c4-r002`, `camp-c4-r003`
- evaluated expressions: 275 (256 unique canonical forms)
- display figures: 275 (every evaluated expression unless --top is set)
- data isolation: the optimisation loop and the reviewer saw in-sample only; OOS/holdout are display-only and were never fed back

## Summary

| run_id | expression | sharpe_is | turnover_is | rank_ic_is | sharpe_oos | sharpe_holdout | decision |
|---|---|---|---|---|---|---|---|
| camp-c2-r002 | -1 * ts_mean(safe_div(close - low, high - low), 5) | 2.059 | 77.95 | 0.01928 | 0.1274 | 0.0542 | optimize |
| camp-c3-r004 | -1 * ts_mean(safe_div(close, open) * safe_div(close - low, high - low), 5) | 2.05 | 78.15 | 0.01967 | 0.1446 | 0.05866 | abandon |
| camp-c1-r003 | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 10), 60) | 2.004 | 56.95 | 0.0186 | -0.07749 | -0.4701 | accept |
| camp-c4-r001 | ts_mean(safe_div(close - low, high - low), 20) - ts_mean(safe_div(close - low, high - low), 5) | 1.749 | 82.97 | 0.01608 | 0.08928 | 0.5638 | optimize |
| camp-c3-r002 | -1 * ts_mean(safe_div(close - low, high - low), 10) | 1.683 | 53.74 | 0.01493 | 0.1214 | -0.4495 | optimize |
| camp-c3-r002 | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 20), 120) | 1.492 | 35.44 | 0.01604 | -0.02619 | -0.1765 | accept |
| camp-c3-r004 | safe_div(ts_mean(safe_div(low, close), 10), ts_mean(safe_div(close, high), 10)) | 1.446 | 49.54 | 0.01789 | 0.1441 | -0.5162 | accept |
| camp-c3-r002 | -1 * ts_mean(close, 5) | 1.254 | 2.754 | 0.004679 | 0.9016 | 0.4537 | abandon |
| camp-c3-r003 | ts_mean(-close, 20) | 1.161 | 0.8097 | 0.003424 | 0.7298 | 0.504 | accept |
| camp-c1-r003 | -1 * ts_mean(safe_div(close - low, high - low), 20) | 1.137 | 33.67 | 0.01041 | 0.08096 | -0.3902 | optimize |
| camp-c2-r002 | -1 * ts_mean(safe_div(close - low, high - low), 20) | 1.137 | 33.67 | 0.01041 | 0.08096 | -0.3902 | optimize |
| camp-c2-r007 | -1 * safe_div(ts_returns(close, 5), ts_mean(ts_std_dev(ts_returns(close, 1), 21), 1)) | 1.115 | 80.57 | 0.01311 | -0.02804 | 0.539 | optimize |
| camp-c2-r006 | ts_mean(-1 * safe_div(close - low, high - low), 21) | 1.101 | 32.79 | 0.009937 | 0.1518 | -0.2869 | optimize |
| camp-c4-r001 | safe_div(safe_div(open, close) - 1, ts_std_dev(safe_div(close, open) - 1, 20)) | 1.093 | 165.6 | 0.01538 | 0.7467 | 0.1931 | optimize |
| camp-c3-r002 | -1 * ts_zscore(safe_div(close - ts_mean(close, 20), ts_mean(close, 20)), 60) | 1.057 | 51.15 | 0.01422 | -0.1081 | 0.1661 | optimize |
| camp-c2-r007 | -1 * ts_zscore(ts_returns(close, 5), 63) | 1.028 | 80.36 | 0.0142 | -0.1469 | 0.3803 | abandon |
| camp-c2-r006 | -1 * (close / ts_mean(close, 5) - 1) | 1.017 | 92.38 | 0.02003 | 0.5561 | 0.5379 | optimize |
| camp-c3-r001 | -1 * ts_returns(close, 3, 1) | 1.005 | 94.07 | 0.01863 | 0.3851 | 0.3697 | optimize |
| camp-c4-r003 | -1 * safe_div(close, ts_mean(close, 6)) | 0.9866 | 83.09 | 0.01921 | 0.459 | 0.5237 | optimize |
| camp-c4-r001 | -1 * ts_returns(close, 3) * safe_div(volume, ts_mean(volume, 20)) | 0.9566 | 95.18 | 0.01711 | 0.3562 | 0.339 | optimize |
| camp-c4-r001 | -1 * safe_div(ts_returns(close, 3), safe_div(ts_mean(volume, 20), volume)) | 0.9566 | 95.18 | 0.01711 | 0.3562 | 0.339 | optimize |
| camp-c1-r003 | -1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | 0.9511 | 70.21 | 0.01528 | 0.0769 | 0.4368 | optimize |
| camp-c3-r001 | -1 * ts_returns(close, 5, 1) | 0.9428 | 72.49 | 0.01584 | 0.1878 | 0.5439 | optimize |
| camp-c2-r002 | -1 * ts_returns(close, 5, 1) | 0.9428 | 72.49 | 0.01584 | 0.1878 | 0.5439 | optimize |
| camp-c1-r005 | -1 * ts_returns(close, 5, 1) | 0.9428 | 72.49 | 0.01584 | 0.1878 | 0.5439 | optimize |
| camp-c4-r003 | -1 * ts_returns(close, 5) | 0.9428 | 72.49 | 0.01584 | 0.1878 | 0.5439 | optimize |
| camp-c2-r005 | -1 * ts_returns(close, 5, 1) | 0.9428 | 72.49 | 0.01584 | 0.1878 | 0.5439 | optimize |
| camp-c2-r002 | -1 * ts_mean(ts_returns(close, 1, 1), 5) | 0.9424 | 72.49 | 0.016 | 0.1986 | 0.53 | optimize |
| camp-c1-r005 | -1 * ts_sum(ts_returns(close, 1, 1), 5) | 0.9424 | 72.49 | 0.016 | 0.1986 | 0.53 | optimize |
| camp-c2-r002 | -1 * ts_bollinger_position(close, 20, 2.0) | 0.9079 | 56.29 | 0.01195 | 0.158 | 0.4936 | abandon |
| camp-c4-r003 | -1 * ts_scale(cap, 20) | 0.9049 | 52.61 | 0.01025 | 0.3068 | 0.733 | optimize |
| camp-c2-r006 | -1 * (close / ts_mean(close, 20) - 1) | 0.8616 | 48.59 | 0.01455 | 0.1695 | 0.3854 | optimize |
| camp-c2-r002 | -1 * ts_bollinger_percent(close, 40, 2.0) | 0.8232 | 41.34 | 0.009169 | 0.01254 | 0.1679 | optimize |
| camp-c3-r002 | -1 * ts_zscore(safe_div(ts_delta(cap, 60), ts_mean(cap, 250)), 250) | 0.8218 | 22.83 | 0.009383 | 0.5134 | 0.2863 | abandon |
| camp-c1-r002 | -(safe_div(ts_delta(close, 20), ts_delta(close, 1)) - 1) | 0.8119 | 162.6 | 0.004803 | -0.8749 | -0.6409 | optimize |
| camp-c1-r004 | -safe_div(close - ts_min(low, 63), ts_max(high, 63) - ts_min(low, 63)) | 0.794 | 29.32 | 0.004807 | 0.2519 | 0.2193 | abandon |
| camp-c3-r001 | -1 * cap | 0.7845 | 1.538 | 6.35e-04 | -0.4022 | -0.5445 | abandon |
| camp-c1-r004 | -safe_div(ts_mean(abs(returns) + returns, 42), ts_mean(abs(returns) - returns, 42)) | 0.7625 | 28.73 | 0.005558 | 0.2759 | -0.2645 | abandon |
| camp-c1-r004 | -safe_div(2 * ts_mean(abs(returns) + returns, 42), 2 * ts_mean(abs(returns) - returns, 42)) | 0.7625 | 28.73 | 0.005558 | 0.2759 | -0.2645 | abandon |
| camp-c3-r004 | safe_div(ts_mean(close, 126), ts_mean(close, 252)) * safe_div(ts_mean(volume, 21), ts_mean(cap, 21)) * safe_div(close, open) | 0.7554 | 3.863 | -0.002237 | -0.05862 | 1.34 | abandon |
| camp-c3-r003 | 0 - ts_mean(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5) | 0.7446 | 61.94 | 0.002081 | 0.7533 | 1.065 | abandon |
| camp-c4-r003 | -1 * ts_mean(cap, 5) | 0.7235 | 0.7704 | 1.46e-04 | -0.4056 | -0.5669 | optimize |
| camp-c3-r003 | ts_mean(-cap, 5) | 0.7235 | 0.7704 | 1.46e-04 | -0.4056 | -0.5669 | abandon |
| camp-c1-r004 | -safe_div(ts_mean(cap, 21), ts_mean(volume, 252)) | 0.693 | 0.5346 | -0.002392 | 0.2432 | 1.788 | abandon |
| camp-c4-r002 | -ts_mean(cap, 21) | 0.6755 | 0.4298 | -1.33e-04 | -0.388 | -0.632 | abandon |
| camp-c3-r001 | -1 * ts_mean(cap, 21) | 0.6755 | 0.4298 | -1.33e-04 | -0.388 | -0.632 | abandon |
| camp-c2-r007 | -1 * ts_mean(cap, 21) | 0.6755 | 0.4298 | -1.33e-04 | -0.388 | -0.632 | abandon |
| camp-c2-r001 | -(ts_mean(cap, 20)) | 0.6678 | 0.4376 | -1.50e-04 | -0.3864 | -0.6318 | abandon |
| camp-c3-r004 | safe_div(ts_mean(safe_div(high - low, close), 5), ts_mean(safe_div(high - low, close), 60)) * safe_div(ts_min(low, 60), close) | 0.6642 | 51.29 | 0.005514 | 0.4055 | -0.5617 | abandon |
| camp-c1-r004 | -ts_returns(close, 21) | 0.6406 | 39.56 | 0.01049 | 0.2362 | 0.02509 | optimize |
| camp-c2-r001 | ts_mean(safe_div(abs(ts_returns(close, 1)), volume * close), 60) | 0.634 | 2.316 | 9.42e-04 | -0.04872 | -0.5944 | abandon |
| camp-c2-r007 | ts_mean(safe_div(abs(ts_returns(close, 1)), volume * close), 63) | 0.6217 | 2.22 | 9.32e-04 | -0.03818 | -0.5969 | abandon |
| camp-c1-r002 | -ts_returns(close, 20) | 0.6195 | 40.43 | 0.01031 | 0.2169 | -0.2413 | optimize |
| camp-c3-r003 | 0 - ts_returns(close, 20) | 0.6195 | 40.43 | 0.01031 | 0.2169 | -0.2413 | optimize |
| camp-c3-r002 | -1 * safe_div(ts_delta(close, 20), ts_mean(close, 20)) | 0.5891 | 36.36 | 0.01031 | 0.1814 | -0.03185 | optimize |
| camp-c2-r007 | ts_mean(safe_div(abs(ts_returns(close, 1)), ts_mean(close * volume, 21)), 63) | 0.5843 | 2.434 | 5.69e-04 | -0.06051 | -0.5635 | abandon |
| camp-c1-r002 | -safe_div(safe_div(high, low), ts_min(safe_div(high, low), 63)) | 0.5729 | 142.2 | 0.009904 | -0.01252 | -0.982 | optimize |
| camp-c2-r006 | -1 * safe_div(close - ts_min(low, 126), ts_max(high, 126) - ts_min(low, 126)) | 0.563 | 20.73 | -0.001207 | 0.1526 | 0.2807 | abandon |
| camp-c1-r004 | ts_mean(safe_div(open, close) - 1, 21) | 0.5569 | 34.14 | 0.009781 | 0.2999 | 0.3298 | optimize |
| camp-c2-r005 | -1 * safe_div(low - ts_min(low, 20), ts_range(high, 20) + ts_range(low, 20)) | 0.5552 | 50.86 | 0.003872 | 0.1814 | 0.6208 | abandon |
| camp-c2-r005 | -1 * safe_div(low - ts_min(low, 20), ts_range(high, 20)) | 0.5418 | 55.63 | 0.005442 | 0.1576 | 0.3854 | abandon |
| camp-c3-r001 | -1 * ts_zscore(safe_div(high - low, close), 120) | 0.5153 | 156.2 | 0.004475 | -0.1704 | -0.5282 | abandon |
| camp-c2-r003 | 0 - ts_zscore(safe_div(high - low, close), 60) | 0.514 | 160.3 | 0.004029 | -0.2436 | -0.3142 | optimize |
| camp-c2-r006 | -1 * ts_mean(safe_div(close - low, high - low), 63) | 0.4942 | 18.09 | -0.002921 | 0.3463 | -0.2373 | abandon |
| camp-c2-r003 | 0 - safe_div(ts_mean(safe_div(safe_div(volume * close, close), cap), 63), ts_std_dev(safe_div(safe_div(volume * close, close), cap), 63)) | 0.4843 | 8.188 | -0.002082 | -0.874 | 0.8288 | abandon |
| camp-c1-r004 | ts_mean(safe_div(open, ts_mean(close, 2)), 21) | 0.4813 | 30.32 | 0.00574 | 0.6702 | 0.1911 | abandon |
| camp-c1-r002 | -safe_div(safe_div(high, low), ts_median(safe_div(high, low), 63)) | 0.4801 | 157.7 | 0.003313 | -0.01092 | -0.3765 | abandon |
| camp-c2-r006 | -1 * safe_div(close - ts_min(low, 252), ts_max(high, 252) - ts_min(low, 252)) | 0.4796 | 18.41 | -0.005334 | 0.1629 | -0.06918 | abandon |
| camp-c1-r001 | 0 - safe_div(safe_div(abs(ts_returns(close, 20)), ts_sum(abs(ts_returns(close, 1)), 20)), ts_mean(safe_div(volume, ts_mean(volume, 20)), 20)) | 0.4448 | 63.12 | 0.004453 | 0.1099 | -0.6149 | abandon |
| camp-c2-r003 | 0 - ts_mean(safe_div(safe_div(open, cap) - safe_div(ts_delta(close, 1), cap), safe_div(ts_delta(close, 1), cap)), 21) | 0.4351 | 26.51 | 0.001206 | 0.03327 | 0.6551 | abandon |
| camp-c1-r005 | -1 * safe_div(ts_sum(ts_returns(close, 1, 1), 63), cap) * ts_std_dev(ts_returns(close, 1, 1), 252) | 0.4291 | 21.14 | 0.001031 | -0.1682 | 0.06927 | abandon |
| camp-c1-r005 | -1 * ts_sum(ts_returns(close, 1, 1), 63) * safe_div(ts_std_dev(ts_returns(close, 1, 1), 252), cap) | 0.4291 | 21.14 | 0.001031 | -0.1682 | 0.06927 | abandon |
| camp-c1-r002 | -safe_div(ts_std_dev(ts_returns(close, 1), 5), ts_mean(ts_std_dev(ts_returns(close, 1), 5), 126)) | 0.4196 | 67.15 | 0.00379 | 0.4442 | -0.3662 | abandon |
| camp-c4-r001 | -1 * (ts_mean(safe_div(volume, cap), 20) - ts_mean(safe_div(volume, cap), 120)) | 0.4166 | 15.07 | 0.001304 | 0.2442 | 1.093 | abandon |
| camp-c4-r003 | ts_delta(close, 147) - ts_delta(close, 21) | 0.4063 | 16.91 | 0.00976 | -0.1486 | 0.3003 | abandon |
| camp-c3-r004 | ts_bollinger_position(close, 120, 2) * ts_returns(returns, 63) * safe_div(ts_max(high, 120), ts_min(low, 120)) | 0.3876 | 150.3 | 0.001896 | 0.2418 | 0.2157 | abandon |
| camp-c3-r001 | -1 * (safe_div(close, ts_max(high, 252)) - 1) | 0.3865 | 16.39 | -0.006421 | 0.2731 | 0.5659 | abandon |
| camp-c4-r002 | -safe_div(ts_max(ts_returns(close, 1), 63), ts_std_dev(ts_returns(close, 1), 63)) | 0.3784 | 11.55 | 0.004408 | 0.257 | -0.4758 | abandon |
| camp-c4-r002 | -ts_min(ts_returns(close, 1), 5) | 0.3743 | 51.94 | -0.001725 | 0.03172 | 1.442 | abandon |
| camp-c4-r002 | -safe_div(ts_max(ts_returns(close, 1), 63), ts_mean(abs(ts_returns(close, 1)), 63)) | 0.3686 | 12.3 | 0.004673 | 0.314 | -0.4831 | abandon |
| camp-c4-r002 | -safe_div(ts_std_dev(ts_returns(close, 1), 5), ts_std_dev(ts_returns(close, 1), 63)) | 0.3565 | 68.83 | 0.002991 | 0.3102 | -0.2225 | abandon |
| camp-c1-r001 | 0 - ts_zscore(safe_div(ts_max(high, 20) - ts_min(low, 20), ts_mean(close, 20)), 60) | 0.351 | 29.66 | 0.00495 | -0.2344 | -0.1926 | optimize |
| camp-c1-r001 | ts_zscore(ts_mean(safe_div(safe_div(returns, returns), safe_div(close, ts_mean(close, 60))), 60), 120) | 0.3399 | 6.953 | 0.002093 | 0.3415 | 0.803 | abandon |
| camp-c3-r003 | 0 - ts_zscore(ts_mean(abs(returns), 5), 60) | 0.3248 | 72.39 | 0.003616 | 0.04944 | -0.6046 | abandon |
| camp-c1-r002 | ts_returns(close, 126) * (1 - safe_div(ts_std_dev(ts_returns(close, 1), 21), ts_std_dev(ts_returns(close, 1), 252))) | 0.3163 | 23.61 | 9.02e-04 | 0.5071 | 0.7795 | abandon |
| camp-c4-r002 | -safe_div(ts_mean(cap, 21), ts_mean(cap, 63)) | 0.3053 | 6.812 | -4.69e-04 | 0.3505 | -0.15 | abandon |
| camp-c2-r006 | -1 * safe_div(ts_mean(cap, 21) / close, ts_mean(cap, 63) / close) | 0.3053 | 6.812 | -4.69e-04 | 0.3505 | -0.15 | abandon |
| camp-c2-r007 | -1 * safe_div(ts_mean(cap, 21), ts_mean(cap, 63)) | 0.3053 | 6.812 | -4.69e-04 | 0.3505 | -0.15 | abandon |
| camp-c1-r001 | 0 - ts_zscore(safe_div(ts_max(high, 20), ts_mean(close, 60)) / safe_div(ts_min(low, 20), ts_mean(close, 60)), 60) | 0.304 | 29.45 | 0.004738 | -0.1737 | -0.228 | optimize |
| camp-c1-r003 | ts_returns(close, 250) - ts_returns(close, 20) | 0.2931 | 12.85 | 0.01512 | 0.08207 | 1.152 | optimize |
| camp-c3-r002 | -1 * ts_bollinger_position(ts_std_dev(returns, 10), 250, 2) | 0.289 | 39.5 | 0.003461 | 0.4897 | -2.138 | abandon |
| camp-c1-r001 | 0 - ts_mean(safe_div(cap, ts_max(cap, 250)), 5) | 0.2764 | 7.577 | -0.009133 | 0.2704 | 0.3991 | abandon |
| camp-c1-r005 | ts_returns(close, 252, 1) - ts_returns(close, 21, 1) | 0.2681 | 12.83 | 0.01497 | 0.1957 | 1.197 | abandon |
| camp-c2-r006 | ts_returns(close, 252, 1) - ts_returns(close, 21, 1) | 0.2681 | 12.83 | 0.01497 | 0.1957 | 1.197 | optimize |
| camp-c1-r002 | ts_returns(close, 252) - ts_returns(close, 21) | 0.2681 | 12.83 | 0.01497 | 0.1957 | 1.197 | abandon |
| camp-c1-r001 | 0 - ts_mean(safe_div(ts_sum(abs(ts_returns(close, 1)), 20), safe_div(volume, ts_mean(volume, 20))), 20) | 0.2665 | 10.4 | 0.01166 | -0.1237 | -1.338 | abandon |
| camp-c3-r002 | -1 * safe_div(ts_delta(cap, 250), ts_mean(cap, 250)) | 0.2546 | 9.937 | -0.009478 | 0.05596 | -0.7309 | abandon |
| camp-c3-r003 | 0 - ts_zscore(safe_div(volume * close, ts_mean(volume * close, 60)), 60) | 0.2424 | 122.4 | -0.002791 | -0.4597 | -0.7434 | abandon |
| camp-c1-r002 | safe_div(close, ts_delta(close, 21)) * safe_div(close, ts_delta(close, 252)) - 1 | 0.239 | 68.54 | 0.00299 | 0.309 | -0.6714 | abandon |
| camp-c2-r005 | -1 * ts_std_dev(ts_returns(close, 1, 1), 21) | 0.2376 | 16.47 | 0.01223 | -0.1334 | -1.265 | abandon |
| camp-c2-r002 | -1 * ts_std_dev(ts_returns(close, 1, 1), 21) | 0.2376 | 16.47 | 0.01223 | -0.1334 | -1.265 | abandon |
| camp-c1-r004 | -ts_std_dev(ts_returns(close, 1), 21) | 0.2376 | 16.47 | 0.01223 | -0.1334 | -1.265 | abandon |
| camp-c3-r002 | -1 * ts_zscore(ts_std_dev(returns, 10), 250) | 0.2354 | 39.53 | 0.003035 | 0.5979 | -1.519 | abandon |
| camp-c3-r002 | -1 * ts_std_dev(ts_returns(close, 1, 1), 40) | 0.2341 | 9.997 | 0.01248 | -0.07997 | -1.268 | abandon |
| camp-c3-r002 | -1 * ts_std_dev(ts_returns(close, 1, 1), 20) | 0.2315 | 17.11 | 0.01223 | -0.1112 | -1.3 | abandon |
| camp-c3-r003 | 0 - ts_mean(ts_returns(safe_div(open, ts_delta(close, 1)), 1), 20) | 0.2307 | 27.07 | 6.23e-04 | -0.2952 | 0.64 | abandon |
| camp-c3-r004 | safe_div(close, ts_max(high, 120)) * safe_div(close, ts_min(low, 120)) * ts_returns(returns, 63) | 0.2305 | 162.1 | 7.51e-04 | 0.2585 | -0.103 | abandon |
| camp-c1-r002 | -safe_div(ts_std_dev(ts_returns(close, 1), 21), ts_std_dev(ts_returns(close, 1), 126)) | 0.2234 | 24.88 | 0.003193 | 0.1927 | -0.1918 | abandon |
| camp-c4-r003 | -1 * ts_mean(safe_div(high - low, close), 60) | 0.2152 | 5.357 | 0.01225 | -0.04695 | -1.348 | abandon |
| camp-c3-r001 | -1 * ts_mean(safe_div(close * volume, cap), 20) | 0.2135 | 7.7 | 0.006853 | 0.2906 | -1.241 | abandon |
| camp-c1-r003 | ts_std_dev(abs(returns), 60) - ts_std_dev(returns, 60) | 0.2133 | 10.57 | 0.01067 | -0.2196 | -1.319 | abandon |
| camp-c2-r007 | -1 * ts_mean(safe_div(high - low, close), 63) | 0.207 | 5.168 | 0.01211 | -0.03431 | -1.337 | abandon |
| camp-c4-r003 | safe_div(ts_mean(close, 21), ts_mean(close, 147)) - safe_div(ts_mean(close, 21), ts_mean(close, 126)) | 0.2043 | 5.607 | 0.01004 | -0.2018 | 0.6488 | abandon |
| camp-c3-r004 | safe_div(ts_mean(safe_div(high - low, close), 5), ts_mean(safe_div(high - low, close), 60)) | 0.2019 | 55.33 | -0.001551 | -0.01555 | 0.4133 | abandon |
| camp-c4-r001 | -1 * ts_mean(safe_div(high - low, close), 10) | 0.1996 | 20.59 | 0.01157 | 2.69e-04 | -1.422 | abandon |
| camp-c2-r003 | 0 - (ts_std_dev(ts_returns(close, 1), 63) + ts_mean(safe_div(safe_div(high, cap) - safe_div(low, cap), safe_div(close, cap)), 63)) | 0.1946 | 5.807 | 0.01248 | -0.05178 | -1.371 | abandon |
| camp-c1-r005 | -1 * ts_zscore(safe_div(close - ts_min(low, 21), ts_range(high, 21) - ts_range(low, 21)), 63) * ts_zscore(volume, 63) | 0.1944 | 112.9 | 8.07e-04 | -0.4761 | -0.706 | abandon |
| camp-c2-r003 | 0 - safe_div(ts_std_dev(ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 63)) | 0.1942 | 42.45 | 0.001862 | 0.2905 | -0.8334 | abandon |
| camp-c4-r003 | -1 * ts_mean(safe_div(high - low, close), 20) | 0.1935 | 11.75 | 0.01195 | -0.03597 | -1.295 | abandon |
| camp-c2-r006 | -1 * ts_std_dev(ts_returns(close, 1, 1), 63) | 0.1918 | 7.112 | 0.0124 | -0.07666 | -1.373 | abandon |
| camp-c4-r003 | -1 * ts_std_dev(ts_returns(close, 1), 63) | 0.1918 | 7.112 | 0.0124 | -0.07666 | -1.373 | abandon |
| camp-c1-r004 | -ts_std_dev(ts_returns(close, 1), 63) | 0.1918 | 7.112 | 0.0124 | -0.07666 | -1.373 | abandon |
| camp-c2-r005 | -1 * ts_std_dev(ts_returns(close, 1, 1), 63) | 0.1918 | 7.112 | 0.0124 | -0.07666 | -1.373 | abandon |
| camp-c3-r001 | -1 * ts_max(ts_returns(close, 1, 1), 20) | 0.1865 | 15.51 | 0.01198 | -0.3187 | -1.505 | abandon |
| camp-c3-r003 | 0 - ts_zscore(ts_std_dev(returns, 10), 60) | 0.1749 | 45.77 | 0.001757 | 0.2171 | -1.217 | abandon |
| camp-c2-r006 | safe_div(ts_mean(close, 252), ts_mean(close, 21)) - 1 | 0.1737 | 3.014 | -0.01101 | -0.338 | -0.4278 | abandon |
| camp-c4-r003 | -1 * safe_div(ts_std_dev(returns, 10), ts_std_dev(returns, 60)) | 0.1716 | 42.61 | 0.00154 | 0.2512 | -0.8955 | abandon |
| camp-c4-r001 | -1 * safe_div(ts_std_dev(returns, 10), ts_std_dev(returns, 60)) | 0.1716 | 42.61 | 0.00154 | 0.2512 | -0.8955 | abandon |
| camp-c4-r003 | -1 * (safe_div(ts_std_dev(returns, 10), ts_std_dev(returns, 60)) - 1) | 0.1716 | 42.61 | 0.00154 | 0.2512 | -0.8955 | abandon |
| camp-c3-r004 | -1 * safe_div(ts_mean(cap, 21), ts_mean(cap, 252)) * safe_div(close, close) * safe_div(volume, volume) | 0.1689 | 2.879 | -0.01007 | -0.04778 | -0.3686 | abandon |
| camp-c2-r005 | -1 * ts_std_dev(ts_returns(close, 1, 1), 126) | 0.1676 | 4.646 | 0.01189 | -0.2595 | -1.328 | abandon |
| camp-c1-r002 | -ts_std_dev(ts_returns(close, 1), 126) | 0.1676 | 4.646 | 0.01189 | -0.2595 | -1.328 | optimize |
| camp-c1-r004 | -ts_std_dev(ts_returns(close, 1), 126) | 0.1676 | 4.646 | 0.01189 | -0.2595 | -1.328 | abandon |
| camp-c2-r006 | -1 * ts_std_dev(ts_returns(close, 1, 1), 126) | 0.1676 | 4.646 | 0.01189 | -0.2595 | -1.328 | abandon |
| camp-c1-r003 | -1 * ts_std_dev(returns, 60) + ts_std_dev(returns * safe_div(returns, abs(returns)), 60) | 0.1628 | 12.42 | 0.01016 | -0.2063 | -1.324 | abandon |
| camp-c2-r003 | safe_div(safe_div(close, cap), ts_max(safe_div(high, cap), 252)) | 0.1528 | 3.787 | 0.006137 | 0.06021 | -0.8477 | abandon |
| camp-c2-r003 | ts_mean(safe_div(abs(ts_returns(close, 1)), safe_div(volume * close, cap)), 63) | 0.1527 | 5.344 | 0.002074 | 0.1344 | 0.6494 | abandon |
| camp-c2-r007 | ts_ir(ts_returns(close, 21), 231) | 0.136 | 3.825 | 0.01402 | 0.05271 | 0.7341 | abandon |
| camp-c2-r001 | safe_div(ts_std_dev(ts_returns(close, 1), 60), ts_mean(safe_div(volume * close, cap), 60)) | 0.1295 | 5.583 | 0.00108 | 0.1645 | 0.7489 | abandon |
| camp-c4-r002 | ts_mean(safe_div(abs(ts_returns(close, 1) - ts_returns(open, 1)), ts_returns(high, 1) - ts_returns(low, 1)), 21) | 0.1276 | 21.07 | 5.95e-04 | -0.3515 | 0.2769 | abandon |
| camp-c4-r002 | ts_mean(safe_div(ts_returns(close, 1) - ts_returns(open, 1), ts_returns(high, 1) - ts_returns(low, 1)), 21) | 0.122 | 21.96 | -0.001167 | -0.1536 | -0.884 | abandon |
| camp-c2-r002 | -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) * ts_std_dev(ts_returns(close, 1, 1), 20) | 0.1154 | 30.31 | 0.007961 | 0.1639 | -0.9669 | abandon |
| camp-c4-r002 | -ts_zscore(ts_std_dev(ts_returns(close, 1), 21), 63) | 0.1103 | 31.14 | 0.002119 | 0.02597 | -0.198 | abandon |
| camp-c1-r003 | ts_returns(close, 120) - ts_returns(close, 5) | 0.1058 | 17.88 | 0.007527 | -0.01545 | 0.597 | abandon |
| camp-c4-r001 | -1 * ts_zscore(safe_div(ts_std_dev(returns, 10), ts_std_dev(returns, 60)), 60) | 0.09851 | 43.94 | 0.001 | -1.49e-04 | -1.057 | abandon |
| camp-c2-r001 | ts_mean(ts_zscore(safe_div(abs(ts_returns(close, 1)), volume * close), 250), 60) | 0.0899 | 9.147 | -0.007562 | -0.2389 | 0.3706 | abandon |
| camp-c3-r004 | safe_div(ts_max(high, 120), close) * ts_std_dev(returns, 20) * safe_div(ts_min(low, 120), ts_max(high, 120)) | 0.08715 | 15.91 | -0.01221 | 0.327 | 1.215 | abandon |
| camp-c4-r002 | ts_min(ts_returns(close, 1), 5) | 0.08446 | 55.75 | -3.85e-04 | 0.279 | -1.451 | abandon |
| camp-c2-r001 | -(ts_zscore(ts_mean(volume * close, 20), 250)) | 0.07106 | 13.81 | -0.002551 | 0.1977 | -0.2905 | abandon |
| camp-c3-r001 | ts_zscore(ts_std_dev(returns, 20), 252) | 0.06719 | 22.23 | -0.003634 | -0.05404 | 1.145 | abandon |
| camp-c2-r002 | ts_returns(close, 21, 1) * (safe_div(volume, ts_mean(volume, 126)) - 1) * (1 + abs(safe_div(volume, ts_mean(volume, 126)) - 1)) | 0.06636 | 140.5 | -0.002959 | 0.06956 | -0.1526 | abandon |
| camp-c4-r003 | -1 * ts_zscore(ts_std_dev(ts_returns(close, 1), 63), 252) | 0.06202 | 12.59 | 0.00266 | 0.3417 | -1.663 | abandon |
| camp-c1-r005 | -1 * ts_zscore(ts_std_dev(ts_returns(close, 1, 1), 63), 252) | 0.06202 | 12.59 | 0.00266 | 0.3417 | -1.663 | abandon |
| camp-c2-r006 | -1 * ts_zscore(ts_std_dev(returns, 63), 252) | 0.06202 | 12.59 | 0.00266 | 0.3417 | -1.663 | abandon |
| camp-c3-r003 | 0 - ts_zscore(safe_div(ts_mean(volume * close, 5), ts_mean(volume * close, 60)), 60) | 0.0602 | 40.59 | -1.74e-04 | -0.2685 | -1.07 | abandon |
| camp-c2-r002 | ts_zscore(ts_std_dev(returns, 10), 126) + safe_div(ts_std_dev(returns, 10), ts_mean(ts_std_dev(returns, 63), 126)) | 0.05972 | 37.64 | -0.002747 | -0.2806 | 1.639 | abandon |
| camp-c2-r001 | -(ts_zscore(ts_mean(cap, 20), 250)) | 0.05556 | 3.792 | -0.009699 | 0.1245 | -0.2799 | abandon |
| camp-c2-r001 | -(safe_div(ts_mean(volume * close, 20), ts_mean(volume * close, 60))) | 0.05251 | 19.67 | 7.27e-04 | 0.3021 | 0.2136 | abandon |
| camp-c4-r002 | -safe_div(ts_mean(safe_div(high - low, close), 21), ts_mean(safe_div(high - low, close), 252)) | 0.05017 | 20.11 | 0.003118 | 0.002861 | -0.7692 | abandon |
| camp-c2-r001 | safe_div(ts_std_dev(ts_returns(close, 1), 60), ts_mean(ts_zscore(safe_div(volume * close, cap), 250), 60)) | 0.04736 | 141.1 | 3.94e-04 | -0.355 | 0.4362 | abandon |
| camp-c3-r001 | -1 * safe_div(ts_mean(safe_div(high - low, close), 10), ts_mean(safe_div(high - low, close), 120)) | 0.04489 | 36.92 | 0.002092 | 0.1824 | -0.5676 | abandon |
| camp-c3-r004 | -1 * ts_zscore(ts_mean(safe_div(volume, cap), 10), 60) * safe_div(volume * close, cap) | 0.04397 | 57.24 | -0.002409 | 0.5633 | 0.7938 | abandon |
| camp-c2-r007 | -1 * safe_div(ts_mean(safe_div(high - low, close), 21), ts_mean(safe_div(high - low, close), 126)) | 0.04014 | 23.21 | 0.00258 | 0.1388 | -0.2606 | abandon |
| camp-c3-r002 | -1 * safe_div(ts_std_dev(ts_returns(close, 1, 1), 20), ts_std_dev(ts_returns(close, 1, 1), 60)) | 0.03104 | 29.36 | 0.001262 | -0.03979 | 0.1224 | abandon |
| camp-c1-r004 | -ts_std_dev(ts_returns(close, 1), 252) | 0.0307 | 3.127 | 0.01001 | -0.3308 | -1.113 | abandon |
| camp-c1-r005 | -1 * ts_zscore(safe_div(close - ts_min(low, 21), ts_range(high, 21)), 63) * ts_zscore(volume, 21) | 0.03015 | 120.4 | 8.33e-04 | 0.09482 | -0.02781 | abandon |
| camp-c1-r001 | ts_mean(safe_div(safe_div(close, ts_min(low, 1)), safe_div(ts_max(high, 1), ts_min(low, 1))), 20) | 0.02853 | 17.44 | 0.005471 | -0.0139 | -1.148 | abandon |
| camp-c2-r002 | safe_div(ts_std_dev(returns, 10), ts_mean(ts_std_dev(returns, 10), 126)) | 0.009463 | 37.35 | -0.003144 | -0.2638 | 1.366 | abandon |
| camp-c1-r005 | -1 * ts_zscore(ts_ema(ts_std_dev(returns, 10), 63), 252) | 0.009425 | 8.831 | 0.002306 | 0.2325 | -1.703 | abandon |
| camp-c2-r002 | -1 * safe_div(ts_std_dev(ts_returns(close, 1, 1), 21), ts_mean(ts_returns(close, 1, 1), 63)) | 0.007157 | 184.5 | -0.002823 | 0.4238 | -1.377 | abandon |
| camp-c2-r003 | 0 - safe_div(ts_mean(safe_div(safe_div(high - low, cap), safe_div(close, cap)), 63), ts_std_dev(ts_returns(close, 1), 63)) | -0.005694 | 13.02 | -0.00383 | 0.2924 | 1.402 | abandon |
| camp-c2-r006 | -1 * safe_div(ts_mean(volume, 21), ts_mean(volume, 252)) | -0.01117 | 14.06 | 0.00225 | 0.2004 | 0.4437 | abandon |
| camp-c2-r006 | -1 * (ts_mean(volume, 21) / ts_mean(volume, 252) - 1) | -0.01117 | 14.06 | 0.00225 | 0.2004 | 0.4437 | abandon |
| camp-c2-r005 | ts_delta(close, 231) / ts_delta(close, 21) - 1 | -0.01958 | 63.67 | 0.001718 | 0.1581 | -0.6655 | abandon |
| camp-c4-r002 | -safe_div(ts_mean(safe_div(high - low, close), 21), ts_mean(safe_div(high - low, close), 63)) | -0.04851 | 27.82 | 0.001182 | 0.0419 | 0.4545 | abandon |
| camp-c1-r004 | -ts_mean(cap, 21) * ts_zscore(ts_mean(volume, 21), 126) | -0.04959 | 15.37 | 7.15e-04 | 0.5542 | 1.279 | abandon |
| camp-c4-r003 | -1 * safe_div(ts_mean(safe_div(high - low, close), 10), ts_mean(safe_div(high - low, close), 60)) | -0.0518 | 40.36 | 7.82e-04 | 0.1074 | -0.2462 | abandon |
| camp-c4-r001 | -1 * safe_div(ts_mean(safe_div(high - low, close), 10), ts_mean(safe_div(high - low, close), 60)) | -0.0518 | 40.36 | 7.82e-04 | 0.1074 | -0.2462 | abandon |
| camp-c1-r005 | ts_sum(ts_returns(close, 1, 1), 231) | -0.05292 | 12.74 | 0.007262 | 0.09228 | 0.965 | abandon |
| camp-c1-r001 | ts_mean(safe_div(cap, ts_max(cap, 250)), 5) | -0.06162 | 7.253 | 0.007352 | -0.3173 | -0.4148 | abandon |
| camp-c2-r003 | ts_mean(safe_div(abs(ts_returns(close, 1)), safe_div(volume * close, cap)), 21) | -0.07014 | 14.45 | 6.95e-04 | -0.03322 | 0.6907 | abandon |
| camp-c2-r006 | ts_returns(close, 21, 1) * (ts_mean(volume, 21) / ts_mean(volume, 252) - 1) | -0.07042 | 37.25 | -0.00228 | -0.1376 | -0.5174 | abandon |
| camp-c4-r003 | -1 * safe_div(ts_mean(safe_div(high - low, close), 20), ts_mean(safe_div(high - low, close), 60)) | -0.08541 | 28.73 | 7.43e-04 | -0.01967 | 0.5014 | abandon |
| camp-c3-r003 | 0 - ts_zscore(ts_mean(safe_div(high - low, close), 5), 60) | -0.09379 | 63.33 | 5.92e-04 | -0.1452 | -0.2963 | abandon |
| camp-c3-r003 | 0 - ts_zscore(ts_mean(safe_div(high, close) - safe_div(low, close), 5), 60) | -0.09379 | 63.33 | 5.92e-04 | -0.1452 | -0.2963 | abandon |
| camp-c4-r003 | safe_div(close, ts_mean(close, 200)) + safe_div(ts_mean(close, 50), ts_mean(close, 200)) | -0.09853 | 9.732 | 0.005832 | -0.1347 | 0.5682 | abandon |
| camp-c1-r004 | -ts_zscore(ts_mean(volume, 5), 60) * (-ts_returns(close, 10)) | -0.0998 | 72.72 | -3.62e-04 | 0.2503 | -0.8981 | abandon |
| camp-c1-r004 | ts_zscore(ts_mean(volume, 5), 60) * ts_returns(close, 10) | -0.0998 | 72.72 | -3.62e-04 | 0.2503 | -0.8981 | abandon |
| camp-c1-r003 | -1 * ts_zscore(ts_mean(safe_div(high - low, close), 20), 120) | -0.1032 | 26.1 | 0.00151 | 0.00306 | 0.1278 | abandon |
| camp-c4-r003 | (safe_div(close, ts_mean(close, 60)) - 1) * (safe_div(ts_mean(volume, 20), ts_median(volume, 60)) - 1) | -0.1075 | 29.12 | -0.001814 | 0.1409 | -0.3545 | abandon |
| camp-c1-r002 | -(safe_div(volume, ts_mean(volume, 60)) - 1) | -0.1199 | 124.3 | -0.006402 | 0.07963 | -0.496 | abandon |
| camp-c3-r002 | -1 * ts_extreme_ratio(ts_returns(close, 1, 1), 60) | -0.142 | 10.32 | -0.003567 | -0.3147 | 0.7004 | abandon |
| camp-c2-r002 | ts_returns(close, 126, 1) | -0.1569 | 16.82 | 0.004831 | -0.09897 | 0.6642 | abandon |
| camp-c4-r002 | ts_returns(close, 126) | -0.1569 | 16.82 | 0.004831 | -0.09897 | 0.6642 | abandon |
| camp-c2-r002 | ts_returns(close, 126, 1) - ts_mean(ts_returns(close, 1, 1), 126) | -0.157 | 16.82 | 0.00484 | -0.09991 | 0.6638 | abandon |
| camp-c3-r001 | safe_div(close, ts_max(high, 252)) | -0.169 | 14.74 | 0.003757 | -0.2755 | -0.601 | abandon |
| camp-c2-r002 | -1 * ts_mean(safe_div(ts_mean(volume, 5) - ts_mean(volume, 60), ts_std_dev(volume, 60)) + ts_returns(close, 5, 1), 5) | -0.1913 | 31.79 | -7.94e-04 | 0.357 | -0.5018 | abandon |
| camp-c1-r002 | -safe_div(ts_std_dev(ts_returns(close, 1), 126), ts_mean(ts_std_dev(ts_returns(close, 1), 21), 63)) | -0.1936 | 12.1 | -0.001 | 0.09128 | 0.4691 | abandon |
| camp-c2-r003 | ts_bollinger_position(safe_div(close - open, safe_div(high - low, high)), 20, 2.0) * safe_div(volume, ts_mean(volume, 20)) | -0.1981 | 154.4 | -0.00539 | -0.2603 | 0.4466 | abandon |
| camp-c1-r005 | safe_div(ts_sum(ts_returns(close, 1, 1), 126), safe_div(ts_mean(volume, 21), ts_mean(volume, 252))) | -0.2195 | 16.84 | 0.002991 | -0.01215 | 0.8078 | abandon |
| camp-c2-r007 | -1 * safe_div(ts_mean(safe_div(volume, cap), 10), ts_mean(safe_div(volume, cap), 126)) | -0.2197 | 23.4 | 4.37e-04 | 0.1709 | -0.1767 | abandon |
| camp-c2-r005 | safe_div(ts_returns(close, 126, 1), ts_std_dev(ts_returns(close, 1, 1), 126)) | -0.2268 | 15.78 | 0.005417 | -0.1014 | 0.2654 | abandon |
| camp-c4-r001 | -1 * (ts_returns(volume, 10) - ts_returns(close, 10)) | -0.2523 | 131.2 | -0.006219 | -0.06208 | -0.924 | abandon |
| camp-c3-r002 | safe_div(close - ts_mean(close, 200), ts_mean(close, 200)) | -0.2566 | 15.23 | 0.00215 | -0.1759 | 0.4815 | abandon |
| camp-c1-r004 | safe_div(close - ts_mean(close, 200), ts_mean(close, 200)) | -0.2566 | 15.23 | 0.00215 | -0.1759 | 0.4815 | abandon |
| camp-c1-r004 | safe_div(close, ts_mean(close, 200)) - 1 | -0.2566 | 15.23 | 0.00215 | -0.1759 | 0.4815 | abandon |
| camp-c2-r005 | safe_div(close, ts_mean(close, 200)) - 1 | -0.2566 | 15.23 | 0.00215 | -0.1759 | 0.4815 | abandon |
| camp-c4-r003 | safe_div(close, ts_mean(close, 200)) - 1 | -0.2566 | 15.23 | 0.00215 | -0.1759 | 0.4815 | abandon |
| camp-c1-r005 | safe_div(ts_returns(close, 126, 1), safe_div(ts_mean(volume, 126), ts_mean(volume, 252))) | -0.258 | 16.47 | 0.003741 | -0.08415 | 0.6307 | abandon |
| camp-c1-r003 | -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) * safe_div(0.10, 0.10 + abs(ts_returns(close, 20))) | -0.268 | 52.6 | -0.009339 | 0.1809 | 1.075 | abandon |
| camp-c3-r001 | -1 * ts_zscore(volume, 60) | -0.2709 | 126.3 | -0.005876 | -0.3637 | -1.012 | abandon |
| camp-c4-r002 | ts_ir(ts_returns(close, 1), 126) | -0.2719 | 15.84 | 0.00492 | -0.09236 | 0.2987 | abandon |
| camp-c4-r003 | -1 * ts_zscore(safe_div(volume, safe_div(cap, close)), 60) | -0.2969 | 126.2 | -0.00598 | -0.3995 | -1.019 | abandon |
| camp-c3-r003 | 0 - ts_zscore(safe_div(volume, ts_median(volume, 60)), 20) | -0.297 | 131.7 | -0.005641 | -0.4908 | -1.178 | abandon |
| camp-c4-r002 | safe_div(close - ts_ema(close, 200), ts_ema(close, 200)) | -0.297 | 17.45 | 0.001494 | -0.2089 | 0.4164 | abandon |
| camp-c1-r002 | -ts_zscore(safe_div(volume, ts_mean(volume, 60)), 60) | -0.3071 | 122.5 | -0.006207 | -0.6676 | -1.047 | abandon |
| camp-c2-r005 | safe_div(ts_mean(volume, 5), ts_mean(volume, 21)) * (1 + ts_returns(close, 21, 1)) | -0.3226 | 45.38 | -8.31e-04 | -0.3707 | 0.3138 | abandon |
| camp-c3-r003 | 0 - ts_scale(ts_mean(safe_div(volume, cap), 20), 20) | -0.3334 | 27.83 | -0.001792 | -0.3091 | 0.211 | abandon |
| camp-c4-r001 | safe_div(ts_delta(open, 1), ts_std_dev(ts_delta(close, 1), 20)) | -0.3352 | 183.3 | -0.006463 | 0.01663 | -0.8277 | abandon |
| camp-c3-r002 | -1 * ts_zscore(ts_mean(safe_div(volume * close, cap), 20), 120) | -0.3361 | 17.79 | 2.36e-04 | 0.1894 | 0.0568 | abandon |
| camp-c4-r002 | -safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | -0.3404 | 44.41 | -0.002473 | 0.2289 | -0.8496 | abandon |
| camp-c3-r001 | -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | -0.3404 | 44.41 | -0.002473 | 0.2289 | -0.8496 | abandon |
| camp-c2-r005 | -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | -0.3404 | 44.41 | -0.002473 | 0.2289 | -0.8496 | abandon |
| camp-c2-r006 | safe_div(close, ts_mean(close, 126)) - 1 | -0.3432 | 19.1 | -0.00177 | -0.2216 | 0.09198 | abandon |
| camp-c4-r003 | -1 * ts_zscore(safe_div(volume, safe_div(cap, close)), 20) | -0.3479 | 134.7 | -0.006278 | -0.5228 | -1.235 | abandon |
| camp-c4-r001 | -1 * (safe_div(ts_mean(volume, 10), ts_mean(volume, 60)) - 1 - abs(ts_returns(close, 10))) | -0.369 | 31.49 | -0.003345 | 0.7328 | -0.1878 | abandon |
| camp-c2-r006 | ts_returns(close, 21, 1) * (1 + safe_div(ts_mean(volume, 21) - ts_mean(volume, 252), ts_mean(volume, 252))) | -0.3695 | 35.01 | -0.007556 | -0.01832 | -0.2813 | abandon |
| camp-c2-r003 | 0 - ts_mean(safe_div(safe_div(open, cap), safe_div(close, cap)), 21) | -0.3923 | 37.9 | -0.009781 | -0.3112 | -0.06968 | abandon |
| camp-c3-r002 | -1 * ts_zscore(ts_mean(safe_div(volume * close, cap), 5), 20) | -0.3961 | 55.45 | -0.002881 | -0.4179 | -1.525 | abandon |
| camp-c2-r005 | -1 * ts_mean(safe_div(volume, cap), 21) | -0.4068 | 5.165 | 8.98e-04 | -0.268 | -0.9887 | abandon |
| camp-c2-r006 | -1 * safe_div(ts_mean(cap, 63), ts_mean(close, 63)) | -0.4091 | 0.1965 | -0.002399 | -1.073 | -1.819 | abandon |
| camp-c2-r002 | ts_returns(close, 21, 1) * safe_div(volume, ts_mean(volume, 63)) | -0.4234 | 64.95 | -0.007655 | -0.05701 | -0.6031 | abandon |
| camp-c1-r002 | -ts_mean(safe_div(volume, cap), 60) | -0.4299 | 3.746 | 0.001322 | -0.2796 | -1.108 | abandon |
| camp-c3-r003 | 0 - ts_zscore(ts_mean(safe_div(volume, cap), 20), 60) | -0.4331 | 20.35 | -6.43e-04 | -0.00607 | 0.1557 | abandon |
| camp-c2-r005 | safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) * ts_returns(close, 21, 1) | -0.4367 | 39.83 | -0.007758 | -0.008716 | -0.4288 | abandon |
| camp-c2-r003 | -ts_mean(safe_div(safe_div(volume * close, cap), close), 63) | -0.4376 | 3.688 | 0.001308 | -0.2577 | -1.109 | abandon |
| camp-c1-r003 | -1 * ts_zscore(ts_mean(volume, 5), 60) * safe_div(1, 1 + abs(ts_returns(close, 20))) | -0.4398 | 42.5 | -0.002477 | -0.2979 | -1.527 | abandon |
| camp-c1-r002 | -safe_div(ts_sum(volume, 60), ts_mean(cap, 60)) | -0.4455 | 3.72 | 0.001271 | -0.2904 | -1.071 | abandon |
| camp-c3-r002 | safe_div(close - ts_mean(close, 100), ts_mean(close, 100)) | -0.4505 | 21.43 | -0.004301 | -0.216 | 0.02785 | abandon |
| camp-c1-r003 | -1 * ts_mean(safe_div(cap, close), 20) | -0.4538 | 0.2059 | -0.002379 | -1.103 | -1.727 | abandon |
| camp-c4-r003 | ts_returns(close, 60) * safe_div(ts_mean(volume, 20), ts_median(volume, 60)) | -0.4561 | 23.82 | -0.004375 | -0.4209 | 0.1019 | abandon |
| camp-c1-r004 | ts_returns(close, 63) * safe_div(ts_mean(volume, 21), ts_mean(volume, 252)) | -0.4641 | 22.1 | -0.004317 | -0.6118 | 0.05158 | abandon |
| camp-c1-r001 | ts_zscore(safe_div(ts_mean(abs(ts_returns(close, 1)), 60), safe_div(volume, ts_mean(volume, 60))), 120) | -0.4715 | 106.9 | -0.006914 | -0.7666 | -0.5472 | abandon |
| camp-c3-r002 | ts_returns(close, 60, 1) | -0.4983 | 23.83 | -0.004327 | -0.3571 | 0.2058 | abandon |
| camp-c3-r001 | ts_returns(close, 60, 1) | -0.4983 | 23.83 | -0.004327 | -0.3571 | 0.2058 | abandon |
| camp-c4-r001 | -1 * ts_zscore(safe_div(volume, cap), 120) | -0.5109 | 115.5 | -0.005926 | -0.3335 | -1.132 | abandon |
| camp-c3-r004 | (1 + ts_returns(close, 126)) * safe_div(ts_mean(safe_div(volume, cap), 21), ts_mean(safe_div(volume, cap), 252)) * safe_div(close, open) | -0.5183 | 20.25 | -0.004833 | -0.2414 | -0.6317 | abandon |
| camp-c1-r004 | ts_returns(close, 63) * ts_zscore(ts_mean(volume, 21), 126) | -0.5495 | 27.75 | -0.003363 | -0.4559 | -0.7793 | abandon |
| camp-c3-r004 | -1 * ts_zscore(ts_mean(safe_div(volume, cap), 10), 60) + 0 * safe_div(close, close) | -0.555 | 29.26 | -0.002681 | 0.0732 | -0.4439 | abandon |
| camp-c1-r004 | ts_ir(ts_returns(close, 1), 63) | -0.5705 | 21.6 | -0.002198 | -0.4012 | -0.1916 | abandon |
| camp-c1-r004 | safe_div(ts_mean(ts_returns(close, 1), 63), ts_std_dev(ts_returns(close, 1), 63)) | -0.5705 | 21.6 | -0.002198 | -0.4012 | -0.1916 | abandon |
| camp-c3-r002 | ts_sum(ts_returns(close, 1, 1), 55) | -0.579 | 23.31 | -0.004693 | -0.217 | 0.1827 | abandon |
| camp-c3-r001 | safe_div(close, ts_mean(close, 60)) - 1 | -0.5958 | 23.25 | -0.006045 | -0.2512 | -0.1278 | abandon |
| camp-c3-r004 | safe_div(ts_mean(cap, 252), ts_mean(cap, 21)) * safe_div(ts_mean(cap, 21), ts_mean(volume, 21)) * safe_div(close, close) | -0.5999 | 3.445 | 1.56e-04 | -0.3192 | -1.898 | abandon |
| camp-c4-r001 | safe_div(ts_mean(ts_returns(close, 1), 60) - ts_mean(abs(ts_returns(close, 1)), 60), ts_mean(abs(ts_returns(close, 1)), 60)) | -0.6006 | 20.44 | -0.001281 | -0.3819 | -0.08582 | abandon |
| camp-c4-r001 | -1 * safe_div(ts_mean(abs(ts_returns(close, 1)), 60) - ts_mean(ts_returns(close, 1), 60), ts_mean(abs(ts_returns(close, 1)), 60)) | -0.6006 | 20.44 | -0.001281 | -0.3819 | -0.08582 | abandon |
| camp-c1-r005 | safe_div(ts_mean(safe_div(close, open) - 1, 21), ts_std_dev(safe_div(close, open) - 1, 21)) | -0.6309 | 33.61 | -0.006667 | -0.4594 | -0.2765 | abandon |
| camp-c1-r001 | ts_zscore(safe_div(safe_div(ts_mean(abs(ts_returns(close, 1)), 60), safe_div(volume, ts_mean(volume, 60))), ts_mean(abs(ts_returns(close, 1)), 120)), 120) | -0.6555 | 111.3 | -0.00686 | -0.5938 | -1.155 | abandon |
| camp-c2-r005 | safe_div(close, ts_mean(close, 21) ) - 1 | -0.6842 | 45.76 | -0.01142 | -0.1342 | -0.5152 | optimize |
| camp-c2-r003 | 0 - ts_zscore(ts_mean(safe_div(safe_div(volume * close, cap), close), 5), 63) | -0.7273 | 43.6 | -0.002884 | -0.116 | -0.9519 | abandon |
| camp-c4-r002 | ts_mean(safe_div(ts_returns(close, 1), abs(ts_returns(close, 1))) * safe_div(volume, ts_mean(volume, 20)), 20) | -0.7354 | 37.29 | -0.005933 | -0.4584 | -0.2223 | abandon |
| camp-c1-r005 | ts_mean(safe_div(close, open) - 1, 10) | -0.748 | 54.61 | -0.01053 | -0.4861 | 0.2612 | abandon |
| camp-c2-r003 | 0 - ts_mean(ts_zscore(safe_div(safe_div(volume * close, cap), close), 63), 5) | -0.75 | 42.59 | -0.003004 | -0.1285 | -0.8517 | abandon |
| camp-c3-r004 | ts_mean(safe_div(close, open), 5) * safe_div(high, high) * safe_div(low, low) | -0.8034 | 78.69 | -0.01306 | -0.6616 | -0.5171 | abandon |
| camp-c2-r007 | ts_sum(safe_div(ts_returns(close, 1), abs(ts_returns(close, 1))) * safe_div(volume, ts_mean(volume, 21)), 10) | -0.8933 | 52.37 | -0.007325 | -0.5896 | -0.4975 | abandon |
| camp-c2-r007 | ts_ir(safe_div(ts_returns(close, 1), abs(ts_returns(close, 1))) * safe_div(volume, ts_mean(volume, 21)), 10) | -0.9582 | 53.85 | -0.007643 | -0.6844 | -0.505 | optimize |
| camp-c2-r003 | safe_div(safe_div(close - open, high - low), safe_div(volume, ts_mean(volume, 20))) | -0.9708 | 174.7 | -0.015 | -0.5978 | -0.1721 | abandon |
| camp-c2-r007 | ts_zscore(ts_returns(close, 231), 21) | -1.006 | 52.2 | -0.01275 | -0.4674 | -1.121 | optimize |
| camp-c1-r001 | ts_mean(safe_div(close - low, high - low), 20) | -1.083 | 35.63 | -0.007626 | -0.2523 | 0.261 | abandon |
| camp-c3-r001 | ts_mean(safe_div(close - low, high - low), 20) | -1.083 | 35.63 | -0.007626 | -0.2523 | 0.261 | abandon |
| camp-c3-r001 | ts_mean(safe_div(close - low, high - low), 10) | -1.56 | 52.62 | -0.01166 | -0.2628 | 0.3346 | abandon |
| camp-c4-r001 | ts_mean(safe_div(close - low, high - low), 10) | -1.56 | 52.62 | -0.01166 | -0.2628 | 0.3346 | optimize |
| camp-c1-r001 | ts_mean(safe_div(safe_div(returns, close), safe_div(returns, close)), 60) | - | 0 | - | - | - | abandon |
| camp-c2-r001 | safe_div(ts_sum(returns, 20), ts_sum(returns, 20)) | - | 0 | - | - | - | abandon |
| camp-c2-r001 | ts_mean(safe_div(returns, returns), 20) | - | 0 | - | - | - | abandon |

## Figures

| rank | factor | hypothesis | run | IS | OOS | holdout | decision | figure |
|---|---|---|---|---|---|---|---|---|
| 1 | `H04-F01` | Range-position (close location within high-low band) as short-term sen | `camp-c2-r002` | 2.059 | 0.127 | 0.054 | optimize | `figures/rank001_camp-c2-r002_H04-F01.png` |
| 2 | `H07-F02` | Persistent close-over-open bid as a continuation signal | `camp-c3-r004` | 2.050 | 0.145 | 0.059 | abandon | `figures/rank002_camp-c3-r004_H07-F02.png` |
| 3 | `H07-F02` | Persistent closing near the daily high indicates crowded pressure and  | `camp-c1-r003` | 2.004 | -0.077 | -0.470 | accept | `figures/rank003_camp-c1-r003_H07-F02.png` |
| 4 | `H03-F02` | Closing-location persistence: close near daily high predicts positive  | `camp-c4-r001` | 1.749 | 0.089 | 0.564 | optimize | `figures/rank004_camp-c4-r001_H03-F02.png` |
| 5 | `H05-F01` | 日内价格位置低点：收盘价靠近日低点的持续弱势 | `camp-c3-r002` | 1.683 | 0.121 | -0.450 | optimize | `figures/rank005_camp-c3-r002_H05-F01.png` |
| 6 | `H05-F02` | 日内价格位置低点：收盘价靠近日低点的持续弱势 | `camp-c3-r002` | 1.492 | -0.026 | -0.176 | accept | `figures/rank006_camp-c3-r002_H05-F02.png` |
| 7 | `H08-F01` | Repeated close-at-band-floor as a mean-reversion setup | `camp-c3-r004` | 1.446 | 0.144 | -0.516 | accept | `figures/rank007_camp-c3-r004_H08-F01.png` |
| 8 | `H06-F01` | 日收益率偏度的彩票效应 | `camp-c3-r002` | 1.254 | 0.902 | 0.454 | abandon | `figures/rank008_camp-c3-r002_H06-F01.png` |
| 9 | `H11-F01` | High nominal price predicts lower subsequent returns within the index  | `camp-c3-r003` | 1.161 | 0.730 | 0.504 | accept | `figures/rank009_camp-c3-r003_H11-F01.png` |
| 10 | `H07-F01` | Persistent closing near the daily high indicates crowded pressure and  | `camp-c1-r003` | 1.137 | 0.081 | -0.390 | optimize | `figures/rank010_camp-c1-r003_H07-F01.png` |
| 11 | `H04-F02` | Range-position (close location within high-low band) as short-term sen | `camp-c2-r002` | 1.137 | 0.081 | -0.390 | optimize | `figures/rank011_camp-c2-r002_H04-F02.png` |
| 12 | `H02-F01` | 短期价格超涨的均值回复 | `camp-c2-r007` | 1.115 | -0.028 | 0.539 | optimize | `figures/rank012_camp-c2-r007_H02-F01.png` |
| 13 | `H06-F01` | Intraday close-location: closes in the top of the daily range predict  | `camp-c2-r006` | 1.101 | 0.152 | -0.287 | optimize | `figures/rank013_camp-c2-r006_H06-F01.png` |
| 14 | `H02-F01` | Overnight gap information slow-drift over multi-week horizon | `camp-c4-r001` | 1.093 | 0.747 | 0.193 | optimize | `figures/rank014_camp-c4-r001_H02-F01.png` |
| 15 | `H01-F02` | 20日横截面短期反转强度（偏离自身均价的幅度） | `camp-c3-r002` | 1.057 | -0.108 | 0.166 | optimize | `figures/rank015_camp-c3-r002_H01-F02.png` |
| 16 | `H02-F02` | 短期价格超涨的均值回复 | `camp-c2-r007` | 1.028 | -0.147 | 0.380 | abandon | `figures/rank016_camp-c2-r007_H02-F02.png` |
| 17 | `H02-F01` | Short-horizon reversal after sharp multi-day price moves | `camp-c2-r006` | 1.017 | 0.556 | 0.538 | optimize | `figures/rank017_camp-c2-r006_H02-F01.png` |
| 18 | `H01-F02` | 近期收益反转：5日收益偏高的股票随后相对落后 | `camp-c3-r001` | 1.005 | 0.385 | 0.370 | optimize | `figures/rank018_camp-c3-r001_H01-F02.png` |
| 19 | `H02-F02` | Short-horizon cross-sectional reversal of 5-day returns | `camp-c4-r003` | 0.987 | 0.459 | 0.524 | optimize | `figures/rank019_camp-c4-r003_H02-F02.png` |
| 20 | `H01-F01` | Cross-sectional volume-shock amplification of short-horizon reversal | `camp-c4-r001` | 0.957 | 0.356 | 0.339 | optimize | `figures/rank020_camp-c4-r001_H01-F01.png` |
| 21 | `H01-F02` | Cross-sectional volume-shock amplification of short-horizon reversal | `camp-c4-r001` | 0.957 | 0.356 | 0.339 | optimize | `figures/rank021_camp-c4-r001_H01-F02.png` |
| 22 | `H01-F01` | Short-horizon reversal amplified by elevated recent turnover | `camp-c1-r003` | 0.951 | 0.077 | 0.437 | optimize | `figures/rank022_camp-c1-r003_H01-F01.png` |
| 23 | `H01-F01` | 近期收益反转：5日收益偏高的股票随后相对落后 | `camp-c3-r001` | 0.943 | 0.188 | 0.544 | optimize | `figures/rank023_camp-c3-r001_H01-F01.png` |
| 24 | `H01-F01` | Short-horizon reversal of recent multi-day return in S&P 500 members | `camp-c2-r002` | 0.943 | 0.188 | 0.544 | optimize | `figures/rank024_camp-c2-r002_H01-F01.png` |
| 25 | `H02-F02` | Short-horizon reversal of the most recent week of adjusted-close retur | `camp-c1-r005` | 0.943 | 0.188 | 0.544 | optimize | `figures/rank025_camp-c1-r005_H02-F02.png` |
| 26 | `H02-F01` | Short-horizon cross-sectional reversal of 5-day returns | `camp-c4-r003` | 0.943 | 0.188 | 0.544 | optimize | `figures/rank026_camp-c4-r003_H02-F01.png` |
| 27 | `H02-F01` | Short-horizon price reversal within large caps | `camp-c2-r005` | 0.943 | 0.188 | 0.544 | optimize | `figures/rank027_camp-c2-r005_H02-F01.png` |
| 28 | `H01-F02` | Short-horizon reversal of recent multi-day return in S&P 500 members | `camp-c2-r002` | 0.942 | 0.199 | 0.530 | optimize | `figures/rank028_camp-c2-r002_H01-F02.png` |
| 29 | `H02-F01` | Short-horizon reversal of the most recent week of adjusted-close retur | `camp-c1-r005` | 0.942 | 0.199 | 0.530 | optimize | `figures/rank029_camp-c1-r005_H02-F01.png` |
| 30 | `H07-F01` | Index distance from its rolling price band as an overextension reversa | `camp-c2-r002` | 0.908 | 0.158 | 0.494 | abandon | `figures/rank030_camp-c2-r002_H07-F01.png` |
| 31 | `H10-F01` | Market-cap-relative size band signal: small-cap overweight within the  | `camp-c4-r003` | 0.905 | 0.307 | 0.733 | optimize | `figures/rank031_camp-c4-r003_H10-F01.png` |
| 32 | `H02-F02` | Short-horizon reversal after sharp multi-day price moves | `camp-c2-r006` | 0.862 | 0.170 | 0.385 | optimize | `figures/rank032_camp-c2-r006_H02-F02.png` |
| 33 | `H07-F02` | Index distance from its rolling price band as an overextension reversa | `camp-c2-r002` | 0.823 | 0.013 | 0.168 | optimize | `figures/rank033_camp-c2-r002_H07-F02.png` |
| 34 | `H08-F02` | 市值规模的长期漂移：对数市值偏离自身趋势 | `camp-c3-r002` | 0.822 | 0.513 | 0.286 | abandon | `figures/rank034_camp-c3-r002_H08-F02.png` |
| 35 | `H02-F02` | 短期反转：最近20个交易日收益的过度反应回吐 | `camp-c1-r002` | 0.812 | -0.875 | -0.641 | optimize | `figures/rank035_camp-c1-r002_H02-F02.png` |
| 36 | `H05-F01` | Position within the recent trading range: stocks near the low end of t | `camp-c1-r004` | 0.794 | 0.252 | 0.219 | abandon | `figures/rank036_camp-c1-r004_H05-F01.png` |
| 37 | `H06-F01` | 小盘溢价：相对市值偏小的股票随后收益较高 | `camp-c3-r001` | 0.785 | -0.402 | -0.544 | abandon | `figures/rank037_camp-c3-r001_H06-F01.png` |
| 38 | `H11-F02` | Skew and drawdown asymmetry: index returns after stretches of one-side | `camp-c1-r004` | 0.763 | 0.276 | -0.265 | abandon | `figures/rank038_camp-c1-r004_H11-F02.png` |
| 39 | `H11-F01` | Skew and drawdown asymmetry: index returns after stretches of one-side | `camp-c1-r004` | 0.763 | 0.276 | -0.265 | abandon | `figures/rank039_camp-c1-r004_H11-F01.png` |
| 40 | `H01-F02` | Volume-confirmed 12-1 style momentum in SP500 constituents | `camp-c3-r004` | 0.755 | -0.059 | 1.340 | abandon | `figures/rank040_camp-c3-r004_H01-F02.png` |
| 41 | `H05-F01` | Persistent positive overnight gaps reverse over the next trading week | `camp-c3-r003` | 0.745 | 0.753 | 1.065 | abandon | `figures/rank041_camp-c3-r003_H05-F01.png` |
| 42 | `H10-F02` | Market-cap-relative size band signal: small-cap overweight within the  | `camp-c4-r003` | 0.724 | -0.406 | -0.567 | optimize | `figures/rank042_camp-c4-r003_H10-F02.png` |
| 43 | `H03-F01` | Lower-cap / smaller size tilts within the S&P universe earn higher sub | `camp-c3-r003` | 0.724 | -0.406 | -0.567 | abandon | `figures/rank043_camp-c3-r003_H03-F01.png` |
| 44 | `H07-F01` | Smaller-cap tilt within the S&P universe: lower market cap names carry | `camp-c1-r004` | 0.693 | 0.243 | 1.788 | abandon | `figures/rank044_camp-c1-r004_H07-F01.png` |
| 45 | `H04-F01` | Size premium within large-cap universe (smaller-half outperformance) | `camp-c4-r002` | 0.676 | -0.388 | -0.632 | abandon | `figures/rank045_camp-c4-r002_H04-F01.png` |
| 46 | `H06-F02` | 小盘溢价：相对市值偏小的股票随后收益较高 | `camp-c3-r001` | 0.676 | -0.388 | -0.632 | abandon | `figures/rank046_camp-c3-r001_H06-F02.png` |
| 47 | `H06-F01` | 规模溢价：相对市值更小的成分股表现更好 | `camp-c2-r007` | 0.676 | -0.388 | -0.632 | abandon | `figures/rank047_camp-c2-r007_H06-F01.png` |
| 48 | `H07-F01` | 横截面市值规模溢价：小市值相对大市值的正向收益差 | `camp-c2-r001` | 0.668 | -0.386 | -0.632 | abandon | `figures/rank048_camp-c2-r001_H07-F01.png` |
| 49 | `H02-F02` | Intraday range expansion as a short-horizon risk-premium signal | `camp-c3-r004` | 0.664 | 0.405 | -0.562 | abandon | `figures/rank049_camp-c3-r004_H02-F02.png` |
| 50 | `H01-F01` | Short-horizon oversold rebound: recent 1-month loser reversal within t | `camp-c1-r004` | 0.641 | 0.236 | 0.025 | optimize | `figures/rank050_camp-c1-r004_H01-F01.png` |
| 51 | `H02-F01` | 价格冲击成本代理：低流动性的横截面溢价 | `camp-c2-r001` | 0.634 | -0.049 | -0.594 | abandon | `figures/rank051_camp-c2-r001_H02-F01.png` |
| 52 | `H03-F01` | 非流动性风险补偿：单位成交额的日价格冲击 | `camp-c2-r007` | 0.622 | -0.038 | -0.597 | abandon | `figures/rank052_camp-c2-r007_H03-F01.png` |
| 53 | `H02-F01` | 短期反转：最近20个交易日收益的过度反应回吐 | `camp-c1-r002` | 0.620 | 0.217 | -0.241 | optimize | `figures/rank053_camp-c1-r002_H02-F01.png` |
| 54 | `H04-F01` | One-month past return reverses over the following two weeks | `camp-c3-r003` | 0.620 | 0.217 | -0.241 | optimize | `figures/rank054_camp-c3-r003_H04-F01.png` |
| 55 | `H01-F01` | 20日横截面短期反转强度（偏离自身均价的幅度） | `camp-c3-r002` | 0.589 | 0.181 | -0.032 | optimize | `figures/rank055_camp-c3-r002_H01-F01.png` |
| 56 | `H03-F02` | 非流动性风险补偿：单位成交额的日价格冲击 | `camp-c2-r007` | 0.584 | -0.061 | -0.563 | abandon | `figures/rank056_camp-c2-r007_H03-F02.png` |
| 57 | `H06-F02` | 日内高低区间压缩：区间收窄后的低波动延续与区间未收窄的相对落后 | `camp-c1-r002` | 0.573 | -0.013 | -0.982 | optimize | `figures/rank057_camp-c1-r002_H06-F02.png` |
| 58 | `H05-F01` | Range-position regime: closes near the top of a long range signal exha | `camp-c2-r006` | 0.563 | 0.153 | 0.281 | abandon | `figures/rank058_camp-c2-r006_H05-F01.png` |
| 59 | `H06-F01` | Overnight versus intraday decomposition: names repeatedly gapping down | `camp-c1-r004` | 0.557 | 0.300 | 0.330 | optimize | `figures/rank059_camp-c1-r004_H06-F01.png` |
| 60 | `H07-F01` | Recent range-position extreme as overbought overreaction | `camp-c2-r005` | 0.555 | 0.181 | 0.621 | abandon | `figures/rank060_camp-c2-r005_H07-F01.png` |
| 61 | `H07-F02` | Recent range-position extreme as overbought overreaction | `camp-c2-r005` | 0.542 | 0.158 | 0.385 | abandon | `figures/rank061_camp-c2-r005_H07-F02.png` |
| 62 | `H04-F02` | 振幅挤压：高低价区间相对自身历史收窄后波动扩张带来正收益 | `camp-c3-r001` | 0.515 | -0.170 | -0.528 | abandon | `figures/rank062_camp-c3-r001_H04-F02.png` |
| 63 | `H02-F01` | 日内振幅异常尖峰后的短期回补 | `camp-c2-r003` | 0.514 | -0.244 | -0.314 | optimize | `figures/rank063_camp-c2-r003_H02-F01.png` |
| 64 | `H06-F02` | Intraday close-location: closes in the top of the daily range predict  | `camp-c2-r006` | 0.494 | 0.346 | -0.237 | abandon | `figures/rank064_camp-c2-r006_H06-F02.png` |
| 65 | `H08-F02` | 换手率水平与稳定性（持股结构投机度） | `camp-c2-r003` | 0.484 | -0.874 | 0.829 | abandon | `figures/rank065_camp-c2-r003_H08-F02.png` |
| 66 | `H06-F02` | Overnight versus intraday decomposition: names repeatedly gapping down | `camp-c1-r004` | 0.481 | 0.670 | 0.191 | abandon | `figures/rank066_camp-c1-r004_H06-F02.png` |
| 67 | `H06-F01` | 日内高低区间压缩：区间收窄后的低波动延续与区间未收窄的相对落后 | `camp-c1-r002` | 0.480 | -0.011 | -0.377 | abandon | `figures/rank067_camp-c1-r002_H06-F01.png` |
| 68 | `H05-F02` | Range-position regime: closes near the top of a long range signal exha | `camp-c2-r006` | 0.480 | 0.163 | -0.069 | abandon | `figures/rank068_camp-c2-r006_H05-F02.png` |
| 69 | `H04-F02` | Volume-expansion-without-price-progress as an unresolved-disagreement  | `camp-c1-r001` | 0.445 | 0.110 | -0.615 | abandon | `figures/rank069_camp-c1-r001_H04-F02.png` |
| 70 | `H07-F02` | 隔夜与日间收益分歧的短期修正 | `camp-c2-r003` | 0.435 | 0.033 | 0.655 | abandon | `figures/rank070_camp-c2-r003_H07-F02.png` |
| 71 | `H07-F01` | Market-state-conditioned relative strength: high market-sensitivity na | `camp-c1-r005` | 0.429 | -0.168 | 0.069 | abandon | `figures/rank071_camp-c1-r005_H07-F01.png` |
| 72 | `H07-F02` | Market-state-conditioned relative strength: high market-sensitivity na | `camp-c1-r005` | 0.429 | -0.168 | 0.069 | abandon | `figures/rank072_camp-c1-r005_H07-F02.png` |
| 73 | `H08-F02` | 横截面离散度上升后的动量反转风险：市场层面状态过滤 | `camp-c1-r002` | 0.420 | 0.444 | -0.366 | abandon | `figures/rank073_camp-c1-r002_H08-F02.png` |
| 74 | `H04-F01` | Turnover intensity versus own long baseline: attention saturation pred | `camp-c4-r001` | 0.417 | 0.244 | 1.093 | abandon | `figures/rank074_camp-c4-r001_H04-F01.png` |
| 75 | `H01-F01` | Cross-sectional 6-1 month total price momentum after skipping the most | `camp-c4-r003` | 0.406 | -0.149 | 0.300 | abandon | `figures/rank075_camp-c4-r003_H01-F01.png` |
| 76 | `H06-F02` | Index time-series momentum conditioned on range position | `camp-c3-r004` | 0.388 | 0.242 | 0.216 | abandon | `figures/rank076_camp-c3-r004_H06-F02.png` |
| 77 | `H08-F02` | 指数回撤状态：SPY自252日高点深度回撤后前景收益偏弱到转强的状态切换 | `camp-c3-r001` | 0.387 | 0.273 | 0.566 | abandon | `figures/rank077_camp-c3-r001_H08-F02.png` |
| 78 | `H10-F02` | Right-skew of recent daily returns as overpricing proxy | `camp-c4-r002` | 0.378 | 0.257 | -0.476 | abandon | `figures/rank078_camp-c4-r002_H10-F02.png` |
| 79 | `H01-F02` | Short-horizon reversal after sharp single-day decline (overshoot corre | `camp-c4-r002` | 0.374 | 0.032 | 1.442 | abandon | `figures/rank079_camp-c4-r002_H01-F02.png` |
| 80 | `H10-F01` | Right-skew of recent daily returns as overpricing proxy | `camp-c4-r002` | 0.369 | 0.314 | -0.483 | abandon | `figures/rank080_camp-c4-r002_H10-F01.png` |
| 81 | `H09-F01` | Index volatility-regime escalation as near-term drag | `camp-c4-r002` | 0.357 | 0.310 | -0.223 | abandon | `figures/rank081_camp-c4-r002_H09-F01.png` |
| 82 | `H06-F01` | Extreme-to-extreme trading range compression versus its long-run norm  | `camp-c1-r001` | 0.351 | -0.234 | -0.193 | optimize | `figures/rank082_camp-c1-r001_H06-F01.png` |
| 83 | `H09-F02` | Accumulated distribution carry over the window versus its own norm as  | `camp-c1-r001` | 0.340 | 0.341 | 0.803 | abandon | `figures/rank083_camp-c1-r001_H09-F02.png` |
| 84 | `H07-F02` | Unusually low recent realized index volatility precedes higher short-h | `camp-c3-r003` | 0.325 | 0.049 | -0.605 | abandon | `figures/rank084_camp-c3-r003_H07-F02.png` |
| 85 | `H07-F01` | 波动窗口压缩后的趋势延续：低波状态下的动量更稳（条件动量） | `camp-c1-r002` | 0.316 | 0.507 | 0.779 | abandon | `figures/rank085_camp-c1-r002_H07-F01.png` |
| 86 | `H04-F02` | Size premium within large-cap universe (smaller-half outperformance) | `camp-c4-r002` | 0.305 | 0.351 | -0.150 | abandon | `figures/rank086_camp-c4-r002_H04-F02.png` |
| 87 | `H09-F01` | Size-tier contrast: small-cap names outperform large-cap names cross-s | `camp-c2-r006` | 0.305 | 0.351 | -0.150 | abandon | `figures/rank087_camp-c2-r006_H09-F01.png` |
| 88 | `H06-F02` | 规模溢价：相对市值更小的成分股表现更好 | `camp-c2-r007` | 0.305 | 0.351 | -0.150 | abandon | `figures/rank088_camp-c2-r007_H06-F02.png` |
| 89 | `H06-F02` | Extreme-to-extreme trading range compression versus its long-run norm  | `camp-c1-r001` | 0.304 | -0.174 | -0.228 | optimize | `figures/rank089_camp-c1-r001_H06-F02.png` |
| 90 | `H03-F01` | Persistence of the intermediate-horizon trend (cross-sectional momentu | `camp-c1-r003` | 0.293 | 0.082 | 1.152 | optimize | `figures/rank090_camp-c1-r003_H03-F01.png` |
| 91 | `H09-F02` | 指数波动率长期分位：市场状态的风险负载信号 | `camp-c3-r002` | 0.289 | 0.490 | -2.138 | abandon | `figures/rank091_camp-c3-r002_H09-F02.png` |
| 92 | `H02-F02` | Close-to-rolling-peak proximity in capitalization space as a slow-arbi | `camp-c1-r001` | 0.276 | 0.270 | 0.399 | abandon | `figures/rank092_camp-c1-r001_H02-F02.png` |
| 93 | `H01-F02` | Cross-sectional medium-term price momentum from adjusted close over 6– | `camp-c1-r005` | 0.268 | 0.196 | 1.197 | abandon | `figures/rank093_camp-c1-r005_H01-F02.png` |
| 94 | `H01-F01` | Cross-sectional medium-horizon momentum in pooled SP500 OHLCV names | `camp-c2-r006` | 0.268 | 0.196 | 1.197 | optimize | `figures/rank094_camp-c2-r006_H01-F01.png` |
| 95 | `H01-F01` | 中期横截面价格动量：12月至1月累积收益的延续效应 | `camp-c1-r002` | 0.268 | 0.196 | 1.197 | abandon | `figures/rank095_camp-c1-r002_H01-F01.png` |
| 96 | `H04-F01` | Volume-expansion-without-price-progress as an unresolved-disagreement  | `camp-c1-r001` | 0.267 | -0.124 | -1.338 | abandon | `figures/rank096_camp-c1-r001_H04-F01.png` |
| 97 | `H08-F01` | 市值规模的长期漂移：对数市值偏离自身趋势 | `camp-c3-r002` | 0.255 | 0.056 | -0.731 | abandon | `figures/rank097_camp-c3-r002_H08-F01.png` |
| 98 | `H09-F02` | Abnormally heavy index turnover predicts subsequent index underperform | `camp-c3-r003` | 0.242 | -0.460 | -0.743 | abandon | `figures/rank098_camp-c3-r003_H09-F02.png` |
| 99 | `H01-F02` | 中期横截面价格动量：12月至1月累积收益的延续效应 | `camp-c1-r002` | 0.239 | 0.309 | -0.671 | abandon | `figures/rank099_camp-c1-r002_H01-F02.png` |
| 100 | `H09-F02` | Elevated index volatility predicts weak next-month index returns | `camp-c2-r005` | 0.238 | -0.133 | -1.265 | abandon | `figures/rank100_camp-c2-r005_H09-F02.png` |
| 101 | `H03-F01` | Idiosyncratic volatility drag on forward returns within S&P 500 member | `camp-c2-r002` | 0.238 | -0.133 | -1.265 | abandon | `figures/rank101_camp-c2-r002_H03-F01.png` |
| 102 | `H10-F01` | Volatility regime drag: elevated index realized volatility predicts we | `camp-c1-r004` | 0.238 | -0.133 | -1.265 | abandon | `figures/rank102_camp-c1-r004_H10-F01.png` |
| 103 | `H09-F01` | 指数波动率长期分位：市场状态的风险负载信号 | `camp-c3-r002` | 0.235 | 0.598 | -1.519 | abandon | `figures/rank103_camp-c3-r002_H09-F01.png` |
| 104 | `H03-F01` | 实现波动率厌恶：个股20日收益波动率的低波异象 | `camp-c3-r002` | 0.234 | -0.080 | -1.268 | abandon | `figures/rank104_camp-c3-r002_H03-F01.png` |
| 105 | `H03-F02` | 实现波动率厌恶：个股20日收益波动率的低波异象 | `camp-c3-r002` | 0.231 | -0.111 | -1.300 | abandon | `figures/rank105_camp-c3-r002_H03-F02.png` |
| 106 | `H05-F02` | Persistent positive overnight gaps reverse over the next trading week | `camp-c3-r003` | 0.231 | -0.295 | 0.640 | abandon | `figures/rank106_camp-c3-r003_H05-F02.png` |
| 107 | `H06-F01` | Index time-series momentum conditioned on range position | `camp-c3-r004` | 0.230 | 0.259 | -0.103 | abandon | `figures/rank107_camp-c3-r004_H06-F01.png` |
| 108 | `H08-F01` | 横截面离散度上升后的动量反转风险：市场层面状态过滤 | `camp-c1-r002` | 0.223 | 0.193 | -0.192 | abandon | `figures/rank108_camp-c1-r002_H08-F01.png` |
| 109 | `H08-F02` | SPY average daily range as an uncertainty-proxy level predicting weake | `camp-c4-r003` | 0.215 | -0.047 | -1.348 | abandon | `figures/rank109_camp-c4-r003_H08-F02.png` |
| 110 | `H07-F01` | 成交额-市值失衡：成交额相对市值异常偏低时后续表现落后 | `camp-c3-r001` | 0.214 | 0.291 | -1.241 | abandon | `figures/rank110_camp-c3-r001_H07-F01.png` |
| 111 | `H06-F02` | Index-level downside volatility asymmetry predicts weaker forward inde | `camp-c1-r003` | 0.213 | -0.220 | -1.319 | abandon | `figures/rank111_camp-c1-r003_H06-F02.png` |
| 112 | `H04-F01` | 基于日内幅度的高波动折价 | `camp-c2-r007` | 0.207 | -0.034 | -1.337 | abandon | `figures/rank112_camp-c2-r007_H04-F01.png` |
| 113 | `H01-F02` | Cross-sectional 6-1 month total price momentum after skipping the most | `camp-c4-r003` | 0.204 | -0.202 | 0.649 | abandon | `figures/rank113_camp-c4-r003_H01-F02.png` |
| 114 | `H02-F01` | Intraday range expansion as a short-horizon risk-premium signal | `camp-c3-r004` | 0.202 | -0.016 | 0.413 | abandon | `figures/rank114_camp-c3-r004_H02-F01.png` |
| 115 | `H07-F01` | Intraday range expansion without directional follow-through signals in | `camp-c4-r001` | 0.200 | 0.000 | -1.422 | abandon | `figures/rank115_camp-c4-r001_H07-F01.png` |
| 116 | `H09-F01` | 彩票型高波动股票的过度定价回落 | `camp-c2-r003` | 0.195 | -0.052 | -1.371 | abandon | `figures/rank116_camp-c2-r003_H09-F01.png` |
| 117 | `H05-F01` | Price-range congestion on elevated volume predicts lower near-term ret | `camp-c1-r005` | 0.194 | -0.476 | -0.706 | abandon | `figures/rank117_camp-c1-r005_H05-F01.png` |
| 118 | `H04-F01` | 指数短期波动率相对长期基准的抬升（SPY） | `camp-c2-r003` | 0.194 | 0.291 | -0.833 | abandon | `figures/rank118_camp-c2-r003_H04-F01.png` |
| 119 | `H08-F01` | SPY average daily range as an uncertainty-proxy level predicting weake | `camp-c4-r003` | 0.193 | -0.036 | -1.295 | abandon | `figures/rank119_camp-c4-r003_H08-F01.png` |
| 120 | `H04-F01` | Low realized volatility names earn a cross-sectional premium | `camp-c2-r006` | 0.192 | -0.077 | -1.373 | abandon | `figures/rank120_camp-c2-r006_H04-F01.png` |
| 121 | `H03-F01` | Low volatility anomaly: trailing realized volatility vs forward return | `camp-c4-r003` | 0.192 | -0.077 | -1.373 | abandon | `figures/rank121_camp-c4-r003_H03-F01.png` |
| 122 | `H10-F02` | Volatility regime drag: elevated index realized volatility predicts we | `camp-c1-r004` | 0.192 | -0.077 | -1.373 | abandon | `figures/rank122_camp-c1-r004_H10-F02.png` |
| 123 | `H09-F01` | Elevated index volatility predicts weak next-month index returns | `camp-c2-r005` | 0.192 | -0.077 | -1.373 | abandon | `figures/rank123_camp-c2-r005_H09-F01.png` |
| 124 | `H10-F01` | 极端单日收益抑制：近20日出现极端上涨日后收益平庸的股票后续偏弱 | `camp-c3-r001` | 0.187 | -0.319 | -1.505 | abandon | `figures/rank124_camp-c3-r001_H10-F01.png` |
| 125 | `H07-F01` | Unusually low recent realized index volatility precedes higher short-h | `camp-c3-r003` | 0.175 | 0.217 | -1.217 | abandon | `figures/rank125_camp-c3-r003_H07-F01.png` |
| 126 | `H01-F02` | Cross-sectional medium-horizon momentum in pooled SP500 OHLCV names | `camp-c2-r006` | 0.174 | -0.338 | -0.428 | abandon | `figures/rank126_camp-c2-r006_H01-F02.png` |
| 127 | `H06-F01` | SPY volatility-regime signal: expanding recent realized volatility pre | `camp-c4-r003` | 0.172 | 0.251 | -0.895 | abandon | `figures/rank127_camp-c4-r003_H06-F01.png` |
| 128 | `H06-F01` | Index volatility term-structure stress: short-vol over long-vol predic | `camp-c4-r001` | 0.172 | 0.251 | -0.895 | abandon | `figures/rank128_camp-c4-r001_H06-F01.png` |
| 129 | `H06-F02` | SPY volatility-regime signal: expanding recent realized volatility pre | `camp-c4-r003` | 0.172 | 0.251 | -0.895 | abandon | `figures/rank129_camp-c4-r003_H06-F02.png` |
| 130 | `H04-F01` | Relative market-cap rank as a neglected-size premium in a large-cap pa | `camp-c3-r004` | 0.169 | -0.048 | -0.369 | abandon | `figures/rank130_camp-c3-r004_H04-F01.png` |
| 131 | `H05-F01` | Low realized-volatility stocks outperform high-volatility stocks | `camp-c2-r005` | 0.168 | -0.259 | -1.328 | abandon | `figures/rank131_camp-c2-r005_H05-F01.png` |
| 132 | `H05-F01` | 特质波动率低波异象：高预期波动股票的相对落后 | `camp-c1-r002` | 0.168 | -0.259 | -1.328 | optimize | `figures/rank132_camp-c1-r002_H05-F01.png` |
| 133 | `H04-F01` | Low realized volatility premium: quiet stocks earn higher risk-adjuste | `camp-c1-r004` | 0.168 | -0.259 | -1.328 | abandon | `figures/rank133_camp-c1-r004_H04-F01.png` |
| 134 | `H04-F02` | Low realized volatility names earn a cross-sectional premium | `camp-c2-r006` | 0.168 | -0.259 | -1.328 | abandon | `figures/rank134_camp-c2-r006_H04-F02.png` |
| 135 | `H06-F01` | Index-level downside volatility asymmetry predicts weaker forward inde | `camp-c1-r003` | 0.163 | -0.206 | -1.324 | abandon | `figures/rank135_camp-c1-r003_H06-F01.png` |
| 136 | `H03-F01` | 贴近历史高点程度（参照点与上方供给） | `camp-c2-r003` | 0.153 | 0.060 | -0.848 | abandon | `figures/rank136_camp-c2-r003_H03-F01.png` |
| 137 | `H01-F01` | 成交额相对规模的交易冲击成本溢价（Amihud 型非流动性） | `camp-c2-r003` | 0.153 | 0.134 | 0.649 | abandon | `figures/rank137_camp-c2-r003_H01-F01.png` |
| 138 | `H01-F01` | 中期价格趋势持续性（12-1 型时序收益斜率） | `camp-c2-r007` | 0.136 | 0.053 | 0.734 | abandon | `figures/rank138_camp-c2-r007_H01-F01.png` |
| 139 | `H08-F01` | 换手-波动弹性：低换手高波动股票的横截面溢价 | `camp-c2-r001` | 0.130 | 0.165 | 0.749 | abandon | `figures/rank139_camp-c2-r001_H08-F01.png` |
| 140 | `H06-F02` | Overnight gap absorption versus intraday body stability | `camp-c4-r002` | 0.128 | -0.351 | 0.277 | abandon | `figures/rank140_camp-c4-r002_H06-F02.png` |
| 141 | `H06-F01` | Overnight gap absorption versus intraday body stability | `camp-c4-r002` | 0.122 | -0.154 | -0.884 | abandon | `figures/rank141_camp-c4-r002_H06-F01.png` |
| 142 | `H02-F02` | Volume-shock reaction: abnormal turnover intensity predicts weaker for | `camp-c2-r002` | 0.115 | 0.164 | -0.967 | abandon | `figures/rank142_camp-c2-r002_H02-F02.png` |
| 143 | `H09-F02` | Index volatility-regime escalation as near-term drag | `camp-c4-r002` | 0.110 | 0.026 | -0.198 | abandon | `figures/rank143_camp-c4-r002_H09-F02.png` |
| 144 | `H03-F02` | Persistence of the intermediate-horizon trend (cross-sectional momentu | `camp-c1-r003` | 0.106 | -0.015 | 0.597 | abandon | `figures/rank144_camp-c1-r003_H03-F02.png` |
| 145 | `H06-F02` | Index volatility term-structure stress: short-vol over long-vol predic | `camp-c4-r001` | 0.099 | -0.000 | -1.057 | abandon | `figures/rank145_camp-c4-r001_H06-F02.png` |
| 146 | `H02-F02` | 价格冲击成本代理：低流动性的横截面溢价 | `camp-c2-r001` | 0.090 | -0.239 | 0.371 | abandon | `figures/rank146_camp-c2-r001_H02-F02.png` |
| 147 | `H05-F01` | Index stress state: realized volatility plus Bollinger position as a m | `camp-c3-r004` | 0.087 | 0.327 | 1.215 | abandon | `figures/rank147_camp-c3-r004_H05-F01.png` |
| 148 | `H01-F01` | Short-horizon reversal after sharp single-day decline (overshoot corre | `camp-c4-r002` | 0.084 | 0.279 | -1.451 | abandon | `figures/rank148_camp-c4-r002_H01-F01.png` |
| 149 | `H01-F02` | 成交额换手强度：高换手（高关注）组合的横截面低收益 | `camp-c2-r001` | 0.071 | 0.198 | -0.290 | abandon | `figures/rank149_camp-c2-r001_H01-F02.png` |
| 150 | `H09-F01` | 市场波动闸门：SPY短期波动偏高时个股反转信号更强（条件假设） | `camp-c3-r001` | 0.067 | -0.054 | 1.145 | abandon | `figures/rank150_camp-c3-r001_H09-F01.png` |
| 151 | `H08-F02` | Index volume-thrust confirmation: rising price on expanding volume pre | `camp-c2-r002` | 0.066 | 0.070 | -0.153 | abandon | `figures/rank151_camp-c2-r002_H08-F02.png` |
| 152 | `H03-F02` | Low volatility anomaly: trailing realized volatility vs forward return | `camp-c4-r003` | 0.062 | 0.342 | -1.663 | abandon | `figures/rank152_camp-c4-r003_H03-F02.png` |
| 153 | `H04-F01` | Own-return dispersion is penalised: high-volatility stocks earn lower  | `camp-c1-r005` | 0.062 | 0.342 | -1.663 | abandon | `figures/rank153_camp-c1-r005_H04-F01.png` |
| 154 | `H08-F01` | Index realized volatility regime predicts weaker near-term index retur | `camp-c2-r006` | 0.062 | 0.342 | -1.663 | abandon | `figures/rank154_camp-c2-r006_H08-F01.png` |
| 155 | `H09-F01` | Abnormally heavy index turnover predicts subsequent index underperform | `camp-c3-r003` | 0.060 | -0.268 | -1.070 | abandon | `figures/rank155_camp-c3-r003_H09-F01.png` |
| 156 | `H06-F02` | Index realized-volatility mean reversion as a forward-return state sig | `camp-c2-r002` | 0.060 | -0.281 | 1.639 | abandon | `figures/rank156_camp-c2-r002_H06-F02.png` |
| 157 | `H07-F02` | 横截面市值规模溢价：小市值相对大市值的正向收益差 | `camp-c2-r001` | 0.056 | 0.125 | -0.280 | abandon | `figures/rank157_camp-c2-r001_H07-F02.png` |
| 158 | `H01-F01` | 成交额换手强度：高换手（高关注）组合的横截面低收益 | `camp-c2-r001` | 0.053 | 0.302 | 0.214 | abandon | `figures/rank158_camp-c2-r001_H01-F01.png` |
| 159 | `H07-F01` | Intraday range dispersion as lottery-uncertainty proxy | `camp-c4-r002` | 0.050 | 0.003 | -0.769 | abandon | `figures/rank159_camp-c4-r002_H07-F01.png` |
| 160 | `H08-F02` | 换手-波动弹性：低换手高波动股票的横截面溢价 | `camp-c2-r001` | 0.047 | -0.355 | 0.436 | abandon | `figures/rank160_camp-c2-r001_H08-F02.png` |
| 161 | `H04-F01` | 振幅挤压：高低价区间相对自身历史收窄后波动扩张带来正收益 | `camp-c3-r001` | 0.045 | 0.182 | -0.568 | abandon | `figures/rank161_camp-c3-r001_H04-F01.png` |
| 162 | `H03-F02` | Abnormal turnover per unit of market cap as a short-horizon reversal s | `camp-c3-r004` | 0.044 | 0.563 | 0.794 | abandon | `figures/rank162_camp-c3-r004_H03-F02.png` |
| 163 | `H08-F01` | 波动率聚集导致的短期风险溢价压缩 | `camp-c2-r007` | 0.040 | 0.139 | -0.261 | abandon | `figures/rank163_camp-c2-r007_H08-F01.png` |
| 164 | `H07-F01` | 个股波动率相对指数波动率的溢价 | `camp-c3-r002` | 0.031 | -0.040 | 0.122 | abandon | `figures/rank164_camp-c3-r002_H07-F01.png` |
| 165 | `H04-F02` | Low realized volatility premium: quiet stocks earn higher risk-adjuste | `camp-c1-r004` | 0.031 | -0.331 | -1.113 | abandon | `figures/rank165_camp-c1-r004_H04-F02.png` |
| 166 | `H05-F02` | Price-range congestion on elevated volume predicts lower near-term ret | `camp-c1-r005` | 0.030 | 0.095 | -0.028 | abandon | `figures/rank166_camp-c1-r005_H05-F02.png` |
| 167 | `H03-F02` | Intraday rebound within the same session as a same-day liquidity-provi | `camp-c1-r001` | 0.029 | -0.014 | -1.148 | abandon | `figures/rank167_camp-c1-r001_H03-F02.png` |
| 168 | `H06-F01` | Index realized-volatility mean reversion as a forward-return state sig | `camp-c2-r002` | 0.009 | -0.264 | 1.366 | abandon | `figures/rank168_camp-c2-r002_H06-F01.png` |
| 169 | `H08-F01` | Index return volatility regime relative to its own norm predicts short | `camp-c1-r005` | 0.009 | 0.232 | -1.703 | abandon | `figures/rank169_camp-c1-r005_H08-F01.png` |
| 170 | `H03-F02` | Idiosyncratic volatility drag on forward returns within S&P 500 member | `camp-c2-r002` | 0.007 | 0.424 | -1.377 | abandon | `figures/rank170_camp-c2-r002_H03-F02.png` |
| 171 | `H09-F02` | 彩票型高波动股票的过度定价回落 | `camp-c2-r003` | -0.006 | 0.292 | 1.402 | abandon | `figures/rank171_camp-c2-r003_H09-F02.png` |
| 172 | `H10-F02` | Turnover intensity: names trading unusually heavy relative to their ow | `camp-c2-r006` | -0.011 | 0.200 | 0.444 | abandon | `figures/rank172_camp-c2-r006_H10-F02.png` |
| 173 | `H10-F01` | Turnover intensity: names trading unusually heavy relative to their ow | `camp-c2-r006` | -0.011 | 0.200 | 0.444 | abandon | `figures/rank173_camp-c2-r006_H10-F01.png` |
| 174 | `H01-F01` | 12-month skip-month price momentum within S&P 500 constituents | `camp-c2-r005` | -0.020 | 0.158 | -0.666 | abandon | `figures/rank174_camp-c2-r005_H01-F01.png` |
| 175 | `H07-F02` | Intraday range dispersion as lottery-uncertainty proxy | `camp-c4-r002` | -0.049 | 0.042 | 0.455 | abandon | `figures/rank175_camp-c4-r002_H07-F02.png` |
| 176 | `H07-F02` | Smaller-cap tilt within the S&P universe: lower market cap names carry | `camp-c1-r004` | -0.050 | 0.554 | 1.279 | abandon | `figures/rank176_camp-c1-r004_H07-F02.png` |
| 177 | `H07-F01` | SPY intraday range compression precedes higher forward market returns | `camp-c4-r003` | -0.052 | 0.107 | -0.246 | abandon | `figures/rank177_camp-c4-r003_H07-F01.png` |
| 178 | `H07-F02` | Intraday range expansion without directional follow-through signals in | `camp-c4-r001` | -0.052 | 0.107 | -0.246 | abandon | `figures/rank178_camp-c4-r001_H07-F02.png` |
| 179 | `H01-F01` | Cross-sectional medium-term price momentum from adjusted close over 6– | `camp-c1-r005` | -0.053 | 0.092 | 0.965 | abandon | `figures/rank179_camp-c1-r005_H01-F01.png` |
| 180 | `H02-F01` | Close-to-rolling-peak proximity in capitalization space as a slow-arbi | `camp-c1-r001` | -0.062 | -0.317 | -0.415 | abandon | `figures/rank180_camp-c1-r001_H02-F01.png` |
| 181 | `H01-F02` | 成交额相对规模的交易冲击成本溢价（Amihud 型非流动性） | `camp-c2-r003` | -0.070 | -0.033 | 0.691 | abandon | `figures/rank181_camp-c2-r003_H01-F02.png` |
| 182 | `H03-F01` | Volume-confirmed move: abnormal turnover intensity amplifies trend per | `camp-c2-r006` | -0.070 | -0.138 | -0.517 | abandon | `figures/rank182_camp-c2-r006_H03-F01.png` |
| 183 | `H07-F02` | SPY intraday range compression precedes higher forward market returns | `camp-c4-r003` | -0.085 | -0.020 | 0.501 | abandon | `figures/rank183_camp-c4-r003_H07-F02.png` |
| 184 | `H01-F01` | Short-horizon range contraction (narrowing high-low spread) precedes p | `camp-c3-r003` | -0.094 | -0.145 | -0.296 | abandon | `figures/rank184_camp-c3-r003_H01-F01.png` |
| 185 | `H01-F02` | Short-horizon range contraction (narrowing high-low spread) precedes p | `camp-c3-r003` | -0.094 | -0.145 | -0.296 | abandon | `figures/rank185_camp-c3-r003_H01-F02.png` |
| 186 | `H05-F02` | Market trend following on SPY: price above slow moving average | `camp-c4-r003` | -0.099 | -0.135 | 0.568 | abandon | `figures/rank186_camp-c4-r003_H05-F02.png` |
| 187 | `H03-F01` | Turnover surge under weak price: a divergence signal from abnormally h | `camp-c1-r004` | -0.100 | 0.250 | -0.898 | abandon | `figures/rank187_camp-c1-r004_H03-F01.png` |
| 188 | `H03-F02` | Turnover surge under weak price: a divergence signal from abnormally h | `camp-c1-r004` | -0.100 | 0.250 | -0.898 | abandon | `figures/rank188_camp-c1-r004_H03-F02.png` |
| 189 | `H02-F01` | Intraday high-low range expansion predicts subsequent negative returns | `camp-c1-r003` | -0.103 | 0.003 | 0.128 | abandon | `figures/rank189_camp-c1-r003_H02-F01.png` |
| 190 | `H09-F02` | Momentum confirmed by volume: price trend plus above-median relative v | `camp-c4-r003` | -0.107 | 0.141 | -0.354 | abandon | `figures/rank190_camp-c4-r003_H09-F02.png` |
| 191 | `H03-F01` | 异常成交量冲击后的短期修复：成交量相对基线的极端抬升 | `camp-c1-r002` | -0.120 | 0.080 | -0.496 | abandon | `figures/rank191_camp-c1-r002_H03-F01.png` |
| 192 | `H06-F02` | 日收益率偏度的彩票效应 | `camp-c3-r002` | -0.142 | -0.315 | 0.700 | abandon | `figures/rank192_camp-c3-r002_H06-F02.png` |
| 193 | `H05-F01` | Index trend-persistence: multi-month price strength conditioning on su | `camp-c2-r002` | -0.157 | -0.099 | 0.664 | abandon | `figures/rank193_camp-c2-r002_H05-F01.png` |
| 194 | `H03-F01` | Medium-term cross-sectional momentum in large-cap universe | `camp-c4-r002` | -0.157 | -0.099 | 0.664 | abandon | `figures/rank194_camp-c4-r002_H03-F01.png` |
| 195 | `H05-F02` | Index trend-persistence: multi-month price strength conditioning on su | `camp-c2-r002` | -0.157 | -0.100 | 0.664 | abandon | `figures/rank195_camp-c2-r002_H05-F02.png` |
| 196 | `H08-F01` | 指数回撤状态：SPY自252日高点深度回撤后前景收益偏弱到转强的状态切换 | `camp-c3-r001` | -0.169 | -0.275 | -0.601 | abandon | `figures/rank196_camp-c3-r001_H08-F01.png` |
| 197 | `H02-F01` | Volume-shock reaction: abnormal turnover intensity predicts weaker for | `camp-c2-r002` | -0.191 | 0.357 | -0.502 | abandon | `figures/rank197_camp-c2-r002_H02-F01.png` |
| 198 | `H05-F02` | 特质波动率低波异象：高预期波动股票的相对落后 | `camp-c1-r002` | -0.194 | 0.091 | 0.469 | abandon | `figures/rank198_camp-c1-r002_H05-F02.png` |
| 199 | `H05-F01` | 低开后的日内收回强度（SPY 指数层） | `camp-c2-r003` | -0.198 | -0.260 | 0.447 | abandon | `figures/rank199_camp-c2-r003_H05-F01.png` |
| 200 | `H03-F01` | Abnormal-volume-confirmed price trend: medium-term price trend scaled  | `camp-c1-r005` | -0.219 | -0.012 | 0.808 | abandon | `figures/rank200_camp-c1-r005_H03-F01.png` |
| 201 | `H05-F01` | 换手率激增与注意力驱动的价格回落 | `camp-c2-r007` | -0.220 | 0.171 | -0.177 | abandon | `figures/rank201_camp-c2-r007_H05-F01.png` |
| 202 | `H06-F01` | Volatility-scaled price momentum as risk-adjusted trend | `camp-c2-r005` | -0.227 | -0.101 | 0.265 | abandon | `figures/rank202_camp-c2-r005_H06-F01.png` |
| 203 | `H08-F02` | Volume-price divergence: rising market participation without price pro | `camp-c4-r001` | -0.252 | -0.062 | -0.924 | abandon | `figures/rank203_camp-c4-r001_H08-F02.png` |
| 204 | `H10-F01` | 指数中期趋势相对200日均线的偏离度 | `camp-c3-r002` | -0.257 | -0.176 | 0.481 | abandon | `figures/rank204_camp-c3-r002_H10-F01.png` |
| 205 | `H09-F01` | Index trend regime: the price path relative to its own long moving ave | `camp-c1-r004` | -0.257 | -0.176 | 0.481 | abandon | `figures/rank205_camp-c1-r004_H09-F01.png` |
| 206 | `H09-F02` | Index trend regime: the price path relative to its own long moving ave | `camp-c1-r004` | -0.257 | -0.176 | 0.481 | abandon | `figures/rank206_camp-c1-r004_H09-F02.png` |
| 207 | `H08-F01` | Index price relative to long moving average predicts next-month direct | `camp-c2-r005` | -0.257 | -0.176 | 0.481 | abandon | `figures/rank207_camp-c2-r005_H08-F01.png` |
| 208 | `H05-F01` | Market trend following on SPY: price above slow moving average | `camp-c4-r003` | -0.257 | -0.176 | 0.481 | abandon | `figures/rank208_camp-c4-r003_H05-F01.png` |
| 209 | `H03-F02` | Abnormal-volume-confirmed price trend: medium-term price trend scaled  | `camp-c1-r005` | -0.258 | -0.084 | 0.631 | abandon | `figures/rank209_camp-c1-r005_H03-F02.png` |
| 210 | `H04-F01` | Abnormal volume spikes precede negative short-term drift in the absenc | `camp-c1-r003` | -0.268 | 0.181 | 1.075 | abandon | `figures/rank210_camp-c1-r003_H04-F01.png` |
| 211 | `H03-F02` | 换手冲击：相对自身基准的成交量异常偏高预示后续收益走弱 | `camp-c3-r001` | -0.271 | -0.364 | -1.012 | abandon | `figures/rank211_camp-c3-r001_H03-F02.png` |
| 212 | `H03-F02` | Medium-term cross-sectional momentum in large-cap universe | `camp-c4-r002` | -0.272 | -0.092 | 0.299 | abandon | `figures/rank212_camp-c4-r002_H03-F02.png` |
| 213 | `H04-F01` | Abnormal turnover surge predicts short-horizon reversal | `camp-c4-r003` | -0.297 | -0.400 | -1.019 | abandon | `figures/rank213_camp-c4-r003_H04-F01.png` |
| 214 | `H02-F01` | Abnormal volume surge predicts negative near-term returns (attention-d | `camp-c3-r003` | -0.297 | -0.491 | -1.178 | abandon | `figures/rank214_camp-c3-r003_H02-F01.png` |
| 215 | `H08-F01` | Index trend-above-long-run-mean as market timing signal | `camp-c4-r002` | -0.297 | -0.209 | 0.416 | abandon | `figures/rank215_camp-c4-r002_H08-F01.png` |
| 216 | `H03-F02` | 异常成交量冲击后的短期修复：成交量相对基线的极端抬升 | `camp-c1-r002` | -0.307 | -0.668 | -1.047 | abandon | `figures/rank216_camp-c1-r002_H03-F02.png` |
| 217 | `H12-F02` | Volume-confirmed demand pressure around membership additions | `camp-c2-r005` | -0.323 | -0.371 | 0.314 | abandon | `figures/rank217_camp-c2-r005_H12-F02.png` |
| 218 | `H10-F02` | High share turnover names underperform over the following month | `camp-c3-r003` | -0.333 | -0.309 | 0.211 | abandon | `figures/rank218_camp-c3-r003_H10-F02.png` |
| 219 | `H02-F02` | Overnight gap information slow-drift over multi-week horizon | `camp-c4-r001` | -0.335 | 0.017 | -0.828 | abandon | `figures/rank219_camp-c4-r001_H02-F02.png` |
| 220 | `H04-F02` | 成交额相对自身规模：市值调整后的换手活跃度 | `camp-c3-r002` | -0.336 | 0.189 | 0.057 | abandon | `figures/rank220_camp-c3-r002_H04-F02.png` |
| 221 | `H02-F01` | Abnormal-volume dry-up versus recent average (attention decay) | `camp-c4-r002` | -0.340 | 0.229 | -0.850 | abandon | `figures/rank221_camp-c4-r002_H02-F01.png` |
| 222 | `H03-F01` | 换手冲击：相对自身基准的成交量异常偏高预示后续收益走弱 | `camp-c3-r001` | -0.340 | 0.229 | -0.850 | abandon | `figures/rank222_camp-c3-r001_H03-F01.png` |
| 223 | `H03-F01` | Abnormal volume surge as distribution signal | `camp-c2-r005` | -0.340 | 0.229 | -0.850 | abandon | `figures/rank223_camp-c2-r005_H03-F01.png` |
| 224 | `H07-F01` | Index trend (SPY time-series momentum) as a market-state signal for la | `camp-c2-r006` | -0.343 | -0.222 | 0.092 | abandon | `figures/rank224_camp-c2-r006_H07-F01.png` |
| 225 | `H04-F02` | Abnormal turnover surge predicts short-horizon reversal | `camp-c4-r003` | -0.348 | -0.523 | -1.235 | abandon | `figures/rank225_camp-c4-r003_H04-F02.png` |
| 226 | `H08-F01` | Volume-price divergence: rising market participation without price pro | `camp-c4-r001` | -0.369 | 0.733 | -0.188 | abandon | `figures/rank226_camp-c4-r001_H08-F01.png` |
| 227 | `H03-F02` | Volume-confirmed move: abnormal turnover intensity amplifies trend per | `camp-c2-r006` | -0.370 | -0.018 | -0.281 | abandon | `figures/rank227_camp-c2-r006_H03-F02.png` |
| 228 | `H07-F01` | 隔夜与日间收益分歧的短期修正 | `camp-c2-r003` | -0.392 | -0.311 | -0.070 | abandon | `figures/rank228_camp-c2-r003_H07-F01.png` |
| 229 | `H04-F01` | 成交额相对自身规模：市值调整后的换手活跃度 | `camp-c3-r002` | -0.396 | -0.418 | -1.525 | abandon | `figures/rank229_camp-c3-r002_H04-F01.png` |
| 230 | `H04-F01` | High turnover names underperform low turnover names | `camp-c2-r005` | -0.407 | -0.268 | -0.989 | abandon | `figures/rank230_camp-c2-r005_H04-F01.png` |
| 231 | `H09-F02` | Size-tier contrast: small-cap names outperform large-cap names cross-s | `camp-c2-r006` | -0.409 | -1.073 | -1.819 | abandon | `figures/rank231_camp-c2-r006_H09-F02.png` |
| 232 | `H08-F01` | Index volume-thrust confirmation: rising price on expanding volume pre | `camp-c2-r002` | -0.423 | -0.057 | -0.603 | abandon | `figures/rank232_camp-c2-r002_H08-F01.png` |
| 233 | `H04-F01` | 换手率驱动的流动性溢价：高换手股票的相对落后 | `camp-c1-r002` | -0.430 | -0.280 | -1.108 | abandon | `figures/rank233_camp-c1-r002_H04-F01.png` |
| 234 | `H10-F01` | High share turnover names underperform over the following month | `camp-c3-r003` | -0.433 | -0.006 | 0.156 | abandon | `figures/rank234_camp-c3-r003_H10-F01.png` |
| 235 | `H12-F01` | Volume-confirmed demand pressure around membership additions | `camp-c2-r005` | -0.437 | -0.009 | -0.429 | abandon | `figures/rank235_camp-c2-r005_H12-F01.png` |
| 236 | `H08-F01` | 换手率水平与稳定性（持股结构投机度） | `camp-c2-r003` | -0.438 | -0.258 | -1.109 | abandon | `figures/rank236_camp-c2-r003_H08-F01.png` |
| 237 | `H04-F02` | Abnormal volume spikes precede negative short-term drift in the absenc | `camp-c1-r003` | -0.440 | -0.298 | -1.527 | abandon | `figures/rank237_camp-c1-r003_H04-F02.png` |
| 238 | `H04-F02` | 换手率驱动的流动性溢价：高换手股票的相对落后 | `camp-c1-r002` | -0.445 | -0.290 | -1.071 | abandon | `figures/rank238_camp-c1-r002_H04-F02.png` |
| 239 | `H10-F02` | 指数中期趋势相对200日均线的偏离度 | `camp-c3-r002` | -0.451 | -0.216 | 0.028 | abandon | `figures/rank239_camp-c3-r002_H10-F02.png` |
| 240 | `H05-F01` | Small-cap premium within the sampled universe | `camp-c1-r003` | -0.454 | -1.103 | -1.727 | abandon | `figures/rank240_camp-c1-r003_H05-F01.png` |
| 241 | `H09-F01` | Momentum confirmed by volume: price trend plus above-median relative v | `camp-c4-r003` | -0.456 | -0.421 | 0.102 | abandon | `figures/rank241_camp-c4-r003_H09-F01.png` |
| 242 | `H02-F01` | Volume-confirmed intermediate momentum: abnormal turnover alongside a  | `camp-c1-r004` | -0.464 | -0.612 | 0.052 | abandon | `figures/rank242_camp-c1-r004_H02-F01.png` |
| 243 | `H01-F01` | Turnover-normalized downside asymmetry as a loss-distribution tail sig | `camp-c1-r001` | -0.472 | -0.767 | -0.547 | abandon | `figures/rank243_camp-c1-r001_H01-F01.png` |
| 244 | `H02-F02` | 中期动量：60日累计收益的持续性 | `camp-c3-r002` | -0.498 | -0.357 | 0.206 | abandon | `figures/rank244_camp-c3-r002_H02-F02.png` |
| 245 | `H02-F01` | 中期趋势延续：60日收益偏高的股票随后表现较好 | `camp-c3-r001` | -0.498 | -0.357 | 0.206 | abandon | `figures/rank245_camp-c3-r001_H02-F01.png` |
| 246 | `H04-F02` | Turnover intensity versus own long baseline: attention saturation pred | `camp-c4-r001` | -0.511 | -0.334 | -1.132 | abandon | `figures/rank246_camp-c4-r001_H04-F02.png` |
| 247 | `H01-F01` | Volume-confirmed 12-1 style momentum in SP500 constituents | `camp-c3-r004` | -0.518 | -0.241 | -0.632 | abandon | `figures/rank247_camp-c3-r004_H01-F01.png` |
| 248 | `H02-F02` | Volume-confirmed intermediate momentum: abnormal turnover alongside a  | `camp-c1-r004` | -0.550 | -0.456 | -0.779 | abandon | `figures/rank248_camp-c1-r004_H02-F02.png` |
| 249 | `H03-F01` | Abnormal turnover per unit of market cap as a short-horizon reversal s | `camp-c3-r004` | -0.555 | 0.073 | -0.444 | abandon | `figures/rank249_camp-c3-r004_H03-F01.png` |
| 250 | `H08-F02` | Return signal-to-noise: names with positive but erratic recent returns | `camp-c1-r004` | -0.570 | -0.401 | -0.192 | abandon | `figures/rank250_camp-c1-r004_H08-F02.png` |
| 251 | `H08-F01` | Return signal-to-noise: names with positive but erratic recent returns | `camp-c1-r004` | -0.570 | -0.401 | -0.192 | abandon | `figures/rank251_camp-c1-r004_H08-F01.png` |
| 252 | `H02-F01` | 中期动量：60日累计收益的持续性 | `camp-c3-r002` | -0.579 | -0.217 | 0.183 | abandon | `figures/rank252_camp-c3-r002_H02-F01.png` |
| 253 | `H02-F02` | 中期趋势延续：60日收益偏高的股票随后表现较好 | `camp-c3-r001` | -0.596 | -0.251 | -0.128 | abandon | `figures/rank253_camp-c3-r001_H02-F02.png` |
| 254 | `H04-F02` | Relative market-cap rank as a neglected-size premium in a large-cap pa | `camp-c3-r004` | -0.600 | -0.319 | -1.898 | abandon | `figures/rank254_camp-c3-r004_H04-F02.png` |
| 255 | `H05-F02` | Downside-share-of-volatility risk premium within the panel | `camp-c4-r001` | -0.601 | -0.382 | -0.086 | abandon | `figures/rank255_camp-c4-r001_H05-F02.png` |
| 256 | `H05-F01` | Downside-share-of-volatility risk premium within the panel | `camp-c4-r001` | -0.601 | -0.382 | -0.086 | abandon | `figures/rank256_camp-c4-r001_H05-F01.png` |
| 257 | `H06-F01` | Persistent intraday (open-to-close) strength proxies for institutional | `camp-c1-r005` | -0.631 | -0.459 | -0.276 | abandon | `figures/rank257_camp-c1-r005_H06-F01.png` |
| 258 | `H01-F02` | Turnover-normalized downside asymmetry as a loss-distribution tail sig | `camp-c1-r001` | -0.656 | -0.594 | -1.155 | abandon | `figures/rank258_camp-c1-r001_H01-F02.png` |
| 259 | `H01-F02` | 12-month skip-month price momentum within S&P 500 constituents | `camp-c2-r005` | -0.684 | -0.134 | -0.515 | optimize | `figures/rank259_camp-c2-r005_H01-F02.png` |
| 260 | `H06-F01` | 成交量相对基线的突发放大（注意力冲击） | `camp-c2-r003` | -0.727 | -0.116 | -0.952 | abandon | `figures/rank260_camp-c2-r003_H06-F01.png` |
| 261 | `H05-F01` | Volume-signed price pressure (accumulation vs distribution imbalance) | `camp-c4-r002` | -0.735 | -0.458 | -0.222 | abandon | `figures/rank261_camp-c4-r002_H05-F01.png` |
| 262 | `H06-F02` | Persistent intraday (open-to-close) strength proxies for institutional | `camp-c1-r005` | -0.748 | -0.486 | 0.261 | abandon | `figures/rank262_camp-c1-r005_H06-F02.png` |
| 263 | `H06-F02` | 成交量相对基线的突发放大（注意力冲击） | `camp-c2-r003` | -0.750 | -0.128 | -0.852 | abandon | `figures/rank263_camp-c2-r003_H06-F02.png` |
| 264 | `H07-F01` | Persistent close-over-open bid as a continuation signal | `camp-c3-r004` | -0.803 | -0.662 | -0.517 | abandon | `figures/rank264_camp-c3-r004_H07-F01.png` |
| 265 | `H07-F01` | 价格-成交量同向的净买卖压力持续性 | `camp-c2-r007` | -0.893 | -0.590 | -0.498 | abandon | `figures/rank265_camp-c2-r007_H07-F01.png` |
| 266 | `H07-F02` | 价格-成交量同向的净买卖压力持续性 | `camp-c2-r007` | -0.958 | -0.684 | -0.505 | optimize | `figures/rank266_camp-c2-r007_H07-F02.png` |
| 267 | `H05-F02` | 低开后的日内收回强度（SPY 指数层） | `camp-c2-r003` | -0.971 | -0.598 | -0.172 | abandon | `figures/rank267_camp-c2-r003_H05-F02.png` |
| 268 | `H01-F02` | 中期价格趋势持续性（12-1 型时序收益斜率） | `camp-c2-r007` | -1.006 | -0.467 | -1.121 | optimize | `figures/rank268_camp-c2-r007_H01-F02.png` |
| 269 | `H03-F01` | Intraday rebound within the same session as a same-day liquidity-provi | `camp-c1-r001` | -1.083 | -0.252 | 0.261 | abandon | `figures/rank269_camp-c1-r001_H03-F01.png` |
| 270 | `H05-F01` | 收盘位置强度：收盘价位于近期区间高位的股票后续相对领先 | `camp-c3-r001` | -1.083 | -0.252 | 0.261 | abandon | `figures/rank270_camp-c3-r001_H05-F01.png` |
| 271 | `H05-F02` | 收盘位置强度：收盘价位于近期区间高位的股票后续相对领先 | `camp-c3-r001` | -1.560 | -0.263 | 0.335 | abandon | `figures/rank271_camp-c3-r001_H05-F02.png` |
| 272 | `H03-F01` | Closing-location persistence: close near daily high predicts positive  | `camp-c4-r001` | -1.560 | -0.263 | 0.335 | optimize | `figures/rank272_camp-c4-r001_H03-F01.png` |
| 273 | `H09-F01` | Accumulated distribution carry over the window versus its own norm as  | `camp-c1-r001` | nan | nan | nan | abandon | `figures/rank273_camp-c1-r001_H09-F01.png` |
| 274 | `H06-F01` | 分红现金回流窗口：除息后被动再投资的温和正向漂移 | `camp-c2-r001` | nan | nan | nan | abandon | `figures/rank274_camp-c2-r001_H06-F01.png` |
| 275 | `H06-F02` | 分红现金回流窗口：除息后被动再投资的温和正向漂移 | `camp-c2-r001` | nan | nan | nan | abandon | `figures/rank275_camp-c2-r001_H06-F02.png` |
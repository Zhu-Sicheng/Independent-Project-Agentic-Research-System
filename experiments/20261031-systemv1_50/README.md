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

| rank | factor | hypothesis | run | IS | OOS | holdout | decision | figure |
|---|---|---|---|---|---|---|---|---|
| 1 | `H01-F01` | 日内收盘位置与短期反转：日收益分布在当日高低区间中的位置对后续1周收益的预测 | `sysv1-h2` | 1.683 | 0.121 | -0.450 | optimize | `figures/rank001_sysv1-h2_H01-F01.png` |
| 2 | `H04-F01` | 指数 ETF 短期超卖反转：极端收益的均值回归 | `sysv1-h3` | 1.079 | -0.112 | 0.435 | optimize | `figures/rank002_sysv1-h3_H04-F01.png` |
| 3 | `H03-F01` | Short-horizon overreaction reversal after standardized single-day shoc | `sysv1-h5` | 0.959 | 0.788 | 0.225 | abandon | `figures/rank003_sysv1-h5_H03-F01.png` |
| 4 | `H06-F01` | 放量急跌后的流动性冲击回补：高冲击强度股票短期反弹 | `sysv1-h6` | 0.951 | 0.077 | 0.437 | optimize | `figures/rank004_sysv1-h6_H06-F01.png` |
| 5 | `H01-F01` | 相对成交量的短期脉冲式均值回归（噪声交易者过度反应） | `sysv1-h7` | 0.947 | 0.078 | 0.442 | optimize | `figures/rank005_sysv1-h7_H01-F01.png` |
| 6 | `H02-F01` | 短期收益反转：最近 5 日涨幅最高的股票在未来 2-10 个交易日跑输 | `sysv1-h4` | 0.943 | 0.188 | 0.544 | optimize | `figures/rank006_sysv1-h4_H02-F01.png` |
| 7 | `H05-F01` | 跳空缺口回补：开盘相对前日收盘的跳空幅度对后续收益的预测 | `sysv1-h2` | 0.745 | 0.753 | 1.065 | abandon | `figures/rank007_sysv1-h2_H05-F01.png` |
| 8 | `H07-F01` | 市值规模溢价：横截面市值水平对中期收益的预测 | `sysv1-h2` | 0.676 | -0.388 | -0.632 | abandon | `figures/rank008_sysv1-h2_H07-F01.png` |
| 9 | `H06-F01` | 规模溢价：横截面中市值相对较低的股票在未来1个月相对跑赢 | `sysv1-h4` | 0.676 | -0.388 | -0.632 | abandon | `figures/rank009_sysv1-h4_H06-F01.png` |
| 10 | `H06-F01` | 大盘股内部的规模倾斜：相对市值分位与季度收益 | `sysv1-h7` | 0.636 | 0.569 | 0.120 | abandon | `figures/rank010_sysv1-h7_H06-F01.png` |
| 11 | `H09-F01` | 彩票型偏好：近期出现大幅单日上涨（右尾收益）的股票在未来1个月相对跑输 | `sysv1-h4` | 0.592 | 0.205 | -0.499 | abandon | `figures/rank011_sysv1-h4_H09-F01.png` |
| 12 | `H03-F01` | 区间位置反转：位于 120 日高低区间上沿的股票短期回吐 | `sysv1-h6` | 0.572 | 0.191 | 0.316 | abandon | `figures/rank012_sysv1-h6_H03-F01.png` |
| 13 | `H12-F01` | Volume-driven valuation expansion signals subsequent index underperfor | `sysv1-h5` | 0.539 | 1.091 | 0.002 | abandon | `figures/rank013_sysv1-h5_H12-F01.png` |
| 14 | `H02-F01` | 成交量异常放大后的价格延续：相对历史均量的量能冲击对短期收益的预测 | `sysv1-h2` | 0.506 | 0.176 | 0.889 | abandon | `figures/rank014_sysv1-h2_H02-F01.png` |
| 15 | `H08-F01` | 中期趋势偏离：价格相对长期均线的偏离程度对后续2-4周收益的预测 | `sysv1-h2` | 0.409 | 0.212 | 0.142 | abandon | `figures/rank015_sysv1-h2_H08-F01.png` |
| 16 | `H08-F01` | 指数短期波动率抬升：SPY 5 日已实现波动相对 60 日常态比率的短期负向预示 | `sysv1-h6` | 0.321 | 0.553 | -0.762 | abandon | `figures/rank016_sysv1-h6_H08-F01.png` |
| 17 | `H07-F01` | Rising conditional market beta predicts weaker forward returns (beta-i | `sysv1-h1` | 0.280 | 0.258 | -1.083 | abandon | `figures/rank017_sysv1-h1_H07-F01.png` |
| 18 | `H04-F01` | 波动率扩张与收缩：短期/长期波动率比值对后续收益的预测（波动率状态变化） | `sysv1-h2` | 0.251 | 0.474 | -1.128 | abandon | `figures/rank018_sysv1-h2_H04-F01.png` |
| 19 | `H01-F01` | 中期价格动量的延续：6-12个月累计收益排名靠前的股票在未来1个月继续跑赢 | `sysv1-h4` | 0.230 | 0.176 | 1.046 | abandon | `figures/rank019_sysv1-h4_H01-F01.png` |
| 20 | `H02-F01` | 横截面换手率（成交额/市值）的流动性溢价 | `sysv1-h7` | 0.203 | 0.291 | -1.243 | abandon | `figures/rank020_sysv1-h7_H02-F01.png` |
| 21 | `H11-F01` | Index high-low range expansion asymmetry as directional exhaustion | `sysv1-h5` | 0.202 | -0.339 | 0.214 | abandon | `figures/rank021_sysv1-h5_H11-F01.png` |
| 22 | `H03-F01` | 低波动偏好：已实现波动率水平对横截面中期收益的预测 | `sysv1-h2` | 0.192 | -0.077 | -1.373 | abandon | `figures/rank022_sysv1-h2_H03-F01.png` |
| 23 | `H03-F01` | 低波动异象：已实现波动率高的股票在未来1个月相对跑输 | `sysv1-h4` | 0.192 | -0.077 | -1.373 | abandon | `figures/rank023_sysv1-h4_H03-F01.png` |
| 24 | `H04-F01` | 波动率压缩后的突破：低区制波动后的短周期表现 | `sysv1-h7` | 0.164 | 0.238 | -1.182 | abandon | `figures/rank024_sysv1-h7_H04-F01.png` |
| 25 | `H05-F01` | 低波动率异象：高日收益波动率的股票随后收益落后 | `sysv1-h6` | 0.160 | -0.257 | -1.339 | abandon | `figures/rank025_sysv1-h6_H05-F01.png` |
| 26 | `H02-F01` | Volatility-of-volatility instability: recent volatility expanding rela | `sysv1-h1` | 0.122 | 0.100 | -0.784 | abandon | `figures/rank026_sysv1-h1_H02-F01.png` |
| 27 | `H05-F01` | Index intraday-range stress: a self-normalized high-low range expansio | `sysv1-h1` | 0.039 | 0.054 | -0.116 | abandon | `figures/rank027_sysv1-h1_H05-F01.png` |
| 28 | `H06-F01` | 量价配合度：收益与成交量方向的日内一致性与后续收益的反转关系 | `sysv1-h2` | 0.019 | 0.420 | -0.008 | abandon | `figures/rank028_sysv1-h2_H06-F01.png` |
| 29 | `H01-F01` | 12-1 月动量：剔除最近一个月收益后的中期累计回报横截面排序 | `sysv1-h6` | -0.017 | 0.017 | 0.805 | abandon | `figures/rank029_sysv1-h6_H01-F01.png` |
| 30 | `H01-F01` | Short-horizon volume-shock reversal: abnormal turnover after an up mov | `sysv1-h1` | -0.041 | -0.160 | 0.318 | abandon | `figures/rank030_sysv1-h1_H01-F01.png` |
| 31 | `H08-F01` | 市场波动状态条件：SPY 日内区间宽度相对历史抬升时未来一月预期收益偏低 | `sysv1-h4` | -0.049 | 0.042 | 0.455 | abandon | `figures/rank031_sysv1-h4_H08-F01.png` |
| 32 | `H04-F01` | 相对换手热度的时间序列异常：成交额占市值比显著高于自身常态的股票随后走弱 | `sysv1-h6` | -0.140 | -0.009 | 0.210 | abandon | `figures/rank032_sysv1-h6_H04-F01.png` |
| 33 | `H05-F01` | 日内上影线优势：收盘相对高低中点的持续偏离作为短期需求压力信号 | `sysv1-h7` | -0.174 | 0.086 | -0.033 | abandon | `figures/rank033_sysv1-h7_H05-F01.png` |
| 34 | `H04-F01` | Cross-sectional intermediate-horizon momentum residualized against mar | `sysv1-h1` | -0.219 | 0.022 | 0.451 | abandon | `figures/rank034_sysv1-h1_H04-F01.png` |
| 35 | `H05-F01` | 指数 ETF 在长区间中的布林带位置与突破持续性 | `sysv1-h3` | -0.240 | 0.056 | 0.452 | abandon | `figures/rank035_sysv1-h3_H05-F01.png` |
| 36 | `H07-F01` | 指数长期均线状态：SPY 相对 200 日均线的偏离度对随后指数的方向性预示 | `sysv1-h6` | -0.257 | -0.176 | 0.481 | abandon | `figures/rank036_sysv1-h6_H07-F01.png` |
| 37 | `H06-F01` | Index volatility-compression then expansion continuation | `sysv1-h5` | -0.274 | -0.106 | -0.036 | abandon | `figures/rank037_sysv1-h5_H06-F01.png` |
| 38 | `H10-F01` | 高换手率折价：换手率相对自身历史抬升的股票在未来1个月相对跑输 | `sysv1-h4` | -0.307 | -0.158 | 0.446 | abandon | `figures/rank038_sysv1-h4_H10-F01.png` |
| 39 | `H04-F01` | 异常放量后的回吐：近端成交量显著高于自身基准的股票在未来两周相对跑输 | `sysv1-h4` | -0.326 | 0.208 | -0.878 | abandon | `figures/rank039_sysv1-h4_H04-F01.png` |
| 40 | `H03-F01` | Overnight-versus-intraday return decomposition: persistent overnight d | `sysv1-h1` | -0.339 | -0.405 | 0.247 | abandon | `figures/rank040_sysv1-h1_H03-F01.png` |
| 41 | `H02-F01` | Variance-ratio style trend persistence: medium-horizon return spread r | `sysv1-h5` | -0.349 | -0.060 | 0.005 | abandon | `figures/rank041_sysv1-h5_H02-F01.png` |
| 42 | `H02-F01` | 成交量相对强度：价格趋势中“放量上涨”相对“缩量上涨”的差异 | `sysv1-h6` | -0.398 | -0.137 | -0.093 | abandon | `figures/rank042_sysv1-h6_H02-F01.png` |
| 43 | `H08-F01` | Position within trailing yearly range: proximity to the 52-week extrem | `sysv1-h1` | -0.410 | -0.146 | 0.059 | abandon | `figures/rank043_sysv1-h1_H08-F01.png` |
| 44 | `H04-F01` | Abnormal-volume-days trend confirmation: return accumulated on volume- | `sysv1-h5` | -0.458 | -0.415 | -0.184 | abandon | `figures/rank044_sysv1-h5_H04-F01.png` |
| 45 | `H02-F01` | 指数 ETF 成交量的相对活跃度与价格确认 | `sysv1-h3` | -0.481 | 0.031 | -0.287 | abandon | `figures/rank045_sysv1-h3_H02-F01.png` |
| 46 | `H01-F01` | S&P 500 指数 ETF 中期时间序列动量的波动率调整趋势信号 | `sysv1-h3` | -0.533 | -0.391 | -0.221 | abandon | `figures/rank046_sysv1-h3_H01-F01.png` |
| 47 | `H07-F01` | Volume-concentrated up-days predict continued index gains | `sysv1-h5` | -0.567 | -0.307 | -0.253 | abandon | `figures/rank047_sysv1-h5_H07-F01.png` |
| 48 | `H03-F01` | 指数 ETF 日收益方向强度：均值与波动率之比的持续性 | `sysv1-h3` | -0.724 | -0.251 | -0.575 | abandon | `figures/rank048_sysv1-h3_H03-F01.png` |
| 49 | `H05-F01` | 区间位置惯性：收盘价接近近月高低区间上沿的股票在未来两周相对跑赢 | `sysv1-h4` | -0.760 | -0.294 | -0.236 | abandon | `figures/rank049_sysv1-h4_H05-F01.png` |
| 50 | `H03-F01` | 日内位置动量：收盘价在近期高低区间中的持续位置 | `sysv1-h7` | -0.772 | -0.258 | -0.251 | abandon | `figures/rank050_sysv1-h7_H03-F01.png` |
| 51 | `H05-F01` | Close location in recent high-low envelope as supply/demand pressure | `sysv1-h5` | -0.772 | -0.258 | -0.251 | abandon | `figures/rank051_sysv1-h5_H05-F01.png` |
| 52 | `H07-F01` | 指数短期均值回复：SPY 近5日急跌后未来一周偏向反弹（作为横截面策略的条件变量） | `sysv1-h4` | -0.943 | -0.073 | -0.568 | abandon | `figures/rank052_sysv1-h4_H07-F01.png` |
| 53 | `H08-F01` | 个股日内收盘位置作为订单流压力代理 | `sysv1-h3` | -1.083 | -0.252 | 0.261 | abandon | `figures/rank053_sysv1-h3_H08-F01.png` |
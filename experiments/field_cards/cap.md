# Field card: `cap`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **yes**

## EDA evidence

| source_field | dataset_id | semantic_role | factor_usage | unit | missing_fraction | blocking_reasons |
|---|---|---|---|---|---|---|
| Adj_MktCap | ds_86999418bce1 | market_cap | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;not_approved_in_reviewed_config;full_selected_dataset_not_successfully_profiled |
| DlyCap | ds_bd2eab70d3b9 | market_cap | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;not_approved_in_reviewed_config |

## Backtest evidence (214)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| s500-c3-r007 | 1 | Market-cap repair after a drawdown: names that recovered capitalisation within a noisy window outperform | -1 * safe_div(ts_max_diff(cap, 126), ts_max(cap, 126)) * safe_div(close, ts_max(close, 126)) | accept | 1.443 | 86.5 | 0.0092 | 0.438 | 0.082 | 1.387 |
| s500-c3-r007 | 0 | Market-cap repair after a drawdown: names that recovered capitalisation within a noisy window outperform | -1 * ts_max_diff(cap, 63) * safe_div(close, close) | abandon | 1.421 | 90.6 | 0.0103 | 0.431 | 0.133 | 1.414 |
| s500-c3-r008 | 0 | Short-horizon overreaction in illiquid names reverses more strongly | -1 * safe_div(ts_returns(close, 5), ts_mean(safe_div(volume, cap), 20)) | optimize | 1.300 | 47.0 | 0.0120 | 0.287 | 0.866 | 1.300 |
| s500-c5-r003 | 0 | Short-horizon reversal conditioned on turnover intensity: low-participation losers recover within two weeks | -1 * safe_div(ts_returns(close, 10), safe_div(ts_mean(volume, 10), ts_mean(cap, 10))) | optimize | 1.169 | 50.2 | 0.0102 | 0.425 | 0.157 | 1.083 |
| s500-c6-r003 | 0 | 短期反转：极端收益后的过度反应修正 | -(ts_sum(ts_returns(close, 1, 0), 5)) * safe_div(ts_mean(volume, 20), cap) | abandon | 1.134 | 85.8 | 0.0114 | 0.191 | 0.675 | 1.134 |
| s500-c3-r007 | 2 | Market-cap repair after a drawdown: names that recovered capitalisation within a noisy window outperform | (1 - ts_scale(ts_max_diff(cap, 126), 126, 0)) * safe_div(close - ts_min(close, 126), ts_max(close, 126) - ts_min(close, 126)) | optimize | 1.093 | 86.6 | 0.0096 | -0.003 | -0.126 | 1.093 |
| s500-c6-r003 | 1 | 短期反转：极端收益后的过度反应修正 | -ts_sum(ts_returns(close, 1, 0), 5) * ts_bollinger_position(safe_div(ts_mean(volume, 20), cap), 60, 2.0) | abandon | 1.075 | 84.4 | 0.0105 | 0.206 | 0.682 | 1.075 |
| s500-c2-r005 | 2 | 横截面：小市值与相对规模的负向收益预测 | 0 - ts_zscore(safe_div(cap, ts_mean(cap, 21)), 63) | accept | 1.061 | 49.7 | 0.0145 | -0.077 | 0.154 | 1.061 |
| s500-c2-r005 | 0 | 横截面：小市值与相对规模的负向收益预测 | 0 - ts_zscore(cap, 21) | optimize | 0.988 | 29.4 | 0.0098 | -0.007 | 0.337 | 0.988 |
| s500-c3-r008 | 2 | Short-horizon overreaction in illiquid names reverses more strongly | -1 * (ts_returns(close, 5) / (1 + abs(ts_returns(close, 5)))) * (2 / (1 + ts_zscore(safe_div(volume, cap), 20))) | optimize | 0.908 | 64.0 | 0.0073 | -0.073 | 0.883 | 0.908 |
| 20261101-sysv1-campaign | 0 | Market-cap-relative size band signal: small-cap overweight within the sampled panel | -1 * ts_scale(cap, 20) | optimize | 0.905 | 52.6 | 0.0102 | 0.307 | 0.733 | 0.886 |
| camp-c4-r003 | 0 | Market-cap-relative size band signal: small-cap overweight within the sampled panel | -1 * ts_scale(cap, 20) | optimize | 0.905 | 52.6 | 0.0102 | 0.307 | 0.733 | 0.886 |
| camp-c3-r002 | 1 | 市值规模的长期漂移：对数市值偏离自身趋势 | -1 * ts_zscore(safe_div(ts_delta(cap, 60), ts_mean(cap, 250)), 250) | abandon | 0.822 | 22.8 | 0.0094 | 0.513 | 0.286 | 0.822 |
| 20261101-sysv1-campaign | 1 | 市值规模的长期漂移：对数市值偏离自身趋势 | -1 * ts_zscore(safe_div(ts_delta(cap, 60), ts_mean(cap, 250)), 250) | abandon | 0.822 | 22.8 | 0.0094 | 0.513 | 0.286 | 0.822 |
| s500-c6-r003 | 1 | 异常成交量后的情绪回归：量能放大的价格走势更易反转 | -ts_zscore(ts_returns(close, 20, 0), 60) * ts_bollinger_position(safe_div(volume, cap), 60, 2.0) | accept | 0.821 | 66.4 | 0.0108 | -0.024 | -0.318 | 0.821 |
| 20261101-sysv1-campaign | 0 | 小盘溢价：相对市值偏小的股票随后收益较高 | -1 * cap | abandon | 0.785 | 1.5 | 0.0006 | -0.402 | -0.544 | 0.709 |
| camp-c3-r001 | 0 | 小盘溢价：相对市值偏小的股票随后收益较高 | -1 * cap | abandon | 0.785 | 1.5 | 0.0006 | -0.402 | -0.544 | 0.709 |
| s500-c6-r003 | 0 | 异常成交量后的情绪回归：量能放大的价格走势更易反转 | -1 * ts_zscore(ts_returns(close, 20, 0), 60) * safe_div(safe_div(ts_mean(volume, 20), ts_mean(volume, 60)), safe_div(cap, ts_mean(cap, 60))) | optimize | 0.779 | 43.4 | 0.0112 | 0.024 | -0.316 | 0.779 |
| camp-c3-r004 | 1 | Volume-confirmed 12-1 style momentum in SP500 constituents | safe_div(ts_mean(close, 126), ts_mean(close, 252)) * safe_div(ts_mean(volume, 21), ts_mean(cap, 21)) * safe_div(close, open) | abandon | 0.755 | 3.9 | -0.0022 | -0.059 | 1.340 | 0.727 |
| 20261101-sysv1-campaign | 1 | Volume-confirmed 12-1 style momentum in SP500 constituents | safe_div(ts_mean(close, 126), ts_mean(close, 252)) * safe_div(ts_mean(volume, 21), ts_mean(cap, 21)) * safe_div(close, open) | abandon | 0.755 | 3.9 | -0.0022 | -0.059 | 1.340 | 0.727 |
| s500-c1-r001 | 1 | Implied float breadth from price and capitalization as a neglect-premium signal | ts_mean(safe_div(cap, close), 20) | abandon | 0.746 | 1.7 | 0.0004 | 1.268 | 1.909 | 0.746 |
| 20261101-sysv1-campaign | 1 | Market-cap-relative size band signal: small-cap overweight within the sampled panel | -1 * ts_mean(cap, 5) | optimize | 0.724 | 0.8 | 0.0001 | -0.406 | -0.567 | 0.626 |
| 20261101-sysv1-campaign | 0 | Lower-cap / smaller size tilts within the S&P universe earn higher subsequent returns | ts_mean(-cap, 5) | abandon | 0.724 | 0.8 | 0.0001 | -0.406 | -0.567 | 0.626 |
| camp-c3-r003 | 0 | Lower-cap / smaller size tilts within the S&P universe earn higher subsequent returns | ts_mean(-cap, 5) | abandon | 0.724 | 0.8 | 0.0001 | -0.406 | -0.567 | 0.626 |
| camp-c4-r003 | 1 | Market-cap-relative size band signal: small-cap overweight within the sampled panel | -1 * ts_mean(cap, 5) | optimize | 0.724 | 0.8 | 0.0001 | -0.406 | -0.567 | 0.626 |
| 20261101-sysv1-campaign | 0 | Smaller-cap tilt within the S&P universe: lower market cap names carry a size premium after controlling for liquidity | -safe_div(ts_mean(cap, 21), ts_mean(volume, 252)) | abandon | 0.693 | 0.5 | -0.0024 | 0.243 | 1.788 | 0.596 |
| camp-c1-r004 | 0 | Smaller-cap tilt within the S&P universe: lower market cap names carry a size premium after controlling for liquidity | -safe_div(ts_mean(cap, 21), ts_mean(volume, 252)) | abandon | 0.693 | 0.5 | -0.0024 | 0.243 | 1.788 | 0.596 |
| s500-c1-r010 | 1 | 横截面低波动异象：近期已实现波动率越低的股票未来相对收益越高 | -1 * ts_ir(ts_returns(close, 1, 1), 60) * safe_div(cap, ts_mean(cap, 21)) | abandon | 0.680 | 24.4 | 0.0035 | 0.307 | 0.067 | 0.680 |
| s500-c1-r010 | 0 | 横截面市值分位：小市值股票的横截面收益差(规模溢价) | -1 * ts_mean(cap, 21) * (1 + 0.000000001 * safe_div(close, ts_mean(close, 21))) | abandon | 0.676 | 0.4 | -0.0002 | -0.388 | -0.639 | 0.590 |
| camp-c3-r001 | 1 | 小盘溢价：相对市值偏小的股票随后收益较高 | -1 * ts_mean(cap, 21) | abandon | 0.676 | 0.4 | -0.0001 | -0.388 | -0.632 | 0.548 |
| sysv1-h4 | 0 | 规模溢价：横截面中市值相对较低的股票在未来1个月相对跑赢 | -1 * ts_mean(cap, 21) | abandon | 0.676 | 0.4 | -0.0001 | -0.388 | -0.632 | 0.548 |
| camp-c2-r007 | 0 | 规模溢价：相对市值更小的成分股表现更好 | -1 * ts_mean(cap, 21) | abandon | 0.676 | 0.4 | -0.0001 | -0.388 | -0.632 | 0.548 |
| sysv1-h2 | 0 | 市值规模溢价：横截面市值水平对中期收益的预测 | -1 * ts_mean(cap, 21) | abandon | 0.676 | 0.4 | -0.0001 | -0.388 | -0.632 | 0.548 |
| camp-c4-r002 | 0 | Size premium within large-cap universe (smaller-half outperformance) | -ts_mean(cap, 21) | abandon | 0.676 | 0.4 | -0.0001 | -0.388 | -0.632 | 0.548 |
| 20261101-sysv1-campaign | 1 | 小盘溢价：相对市值偏小的股票随后收益较高 | -1 * ts_mean(cap, 21) | abandon | 0.676 | 0.4 | -0.0001 | -0.388 | -0.632 | 0.548 |
| 20261101-sysv1-campaign | 0 | Size premium within large-cap universe (smaller-half outperformance) | -ts_mean(cap, 21) | abandon | 0.676 | 0.4 | -0.0001 | -0.388 | -0.632 | 0.548 |
| 20261031-systemv1_50 | 0 | 规模溢价：横截面中市值相对较低的股票在未来1个月相对跑赢 | -1 * ts_mean(cap, 21) | abandon | 0.676 | 0.4 | -0.0001 | -0.388 | -0.632 | 0.548 |
| s500-c2-r005 | 1 | 横截面：小市值与相对规模的负向收益预测 | 0 - safe_div(cap, ts_mean(cap, 63)) | optimize | 0.675 | 26.5 | 0.0088 | 0.279 | -0.043 | 0.675 |
| s500-c4-r010 | 0 | 小市值/低流动性容量标的后续截面收益更高（规模—流动性补偿） | -ts_mean(cap, 20) | optimize | 0.671 | 0.4 | -0.0002 | -0.389 | -0.639 | 0.584 |
| camp-c2-r001 | 0 | 横截面市值规模溢价：小市值相对大市值的正向收益差 | -(ts_mean(cap, 20)) | abandon | 0.668 | 0.4 | -0.0002 | -0.386 | -0.632 | 0.540 |
| 20261101-sysv1-campaign | 0 | 横截面市值规模溢价：小市值相对大市值的正向收益差 | -(ts_mean(cap, 20)) | abandon | 0.668 | 0.4 | -0.0002 | -0.386 | -0.632 | 0.540 |
| sysv1-h7 | 0 | 大盘股内部的规模倾斜：相对市值分位与季度收益 | -(safe_div(ts_delta(cap, 60), cap) * close) | abandon | 0.636 | 19.3 | 0.0021 | 0.569 | 0.120 | 0.619 |
| 20261031-systemv1_50 | 0 | 大盘股内部的规模倾斜：相对市值分位与季度收益 | -(safe_div(ts_delta(cap, 60), cap) * close) | abandon | 0.636 | 19.3 | 0.0021 | 0.569 | 0.120 | 0.619 |
| s500-c6-r002 | 0 | Size-graded range compression: extreme volume-scaled cap deciles mean-revert | 0 - safe_div(safe_div(cap, ts_delta(cap, 60)), safe_div(ts_mean(volume, 60), ts_delta(volume, 60) + ts_mean(volume, 60))) | abandon | 0.623 | 45.2 | -0.0002 | 0.401 | 0.090 | 0.587 |
| s500-c5-r003 | 1 | Short-horizon reversal conditioned on turnover intensity: low-participation losers recover within two weeks | -1 * safe_div(ts_returns(close, 10), 1 + ts_zscore(safe_div(ts_mean(volume, 10), ts_mean(cap, 10)), 63)) | optimize | 0.596 | 68.3 | 0.0058 | 0.486 | 0.118 | 0.596 |
| sysv1-h4 | 0 | 彩票型偏好：近期出现大幅单日上涨（右尾收益）的股票在未来1个月相对跑输 | -1 * (ts_mean(ts_returns(close, 1, 1) * ts_returns(close, 1, 1) * ts_returns(close, 1, 1), 63) / ts_mean(cap, 63)) | abandon | 0.592 | 12.3 | 0.0073 | 0.205 | -0.499 | 0.592 |
| 20261031-systemv1_50 | 0 | 彩票型偏好：近期出现大幅单日上涨（右尾收益）的股票在未来1个月相对跑输 | -1 * (ts_mean(ts_returns(close, 1, 1) * ts_returns(close, 1, 1) * ts_returns(close, 1, 1), 63) / ts_mean(cap, 63)) | abandon | 0.592 | 12.3 | 0.0073 | 0.205 | -0.499 | 0.592 |
| sysv1-h5 | 0 | Volume-driven valuation expansion signals subsequent index underperformance | -1 * (ts_returns(cap, 60) - ts_returns(close, 60)) | abandon | 0.539 | 11.2 | 0.0027 | 1.091 | 0.002 | 0.539 |
| 20261031-systemv1_50 | 0 | Volume-driven valuation expansion signals subsequent index underperformance | -1 * (ts_returns(cap, 60) - ts_returns(close, 60)) | abandon | 0.539 | 11.2 | 0.0027 | 1.091 | 0.002 | 0.539 |
| s500-c6-r001 | 0 | Rising implied share count (net issuance) predicts lower future returns | safe_div(ts_returns(close, 63), ts_returns(cap, 63)) * safe_div(ts_mean(volume, 5), ts_mean(volume, 63)) | abandon | 0.509 | 48.6 | 0.0016 | -0.105 | 1.227 | 0.321 |
| s500-c4-r003 | 0 | Turnover-adjusted illiquidity premium (traded value relative to market cap) | ts_median(safe_div(cap, volume), 60) | abandon | 0.490 | 31.7 | 0.0006 | -0.756 | 0.168 | -0.188 |
| camp-c2-r003 | 1 | 换手率水平与稳定性（持股结构投机度） | 0 - safe_div(ts_mean(safe_div(safe_div(volume * close, close), cap), 63), ts_std_dev(safe_div(safe_div(volume * close, close), cap), 63)) | abandon | 0.484 | 8.2 | -0.0021 | -0.874 | 0.829 | 0.277 |
| 20261101-sysv1-campaign | 1 | 换手率水平与稳定性（持股结构投机度） | 0 - safe_div(ts_mean(safe_div(safe_div(volume * close, close), cap), 63), ts_std_dev(safe_div(safe_div(volume * close, close), cap), 63)) | abandon | 0.484 | 8.2 | -0.0021 | -0.874 | 0.829 | 0.277 |
| s500-c6-r002 | 1 | Size-graded range compression: extreme volume-scaled cap deciles mean-revert | 0 - safe_div(ts_delta(cap, 60) / ts_mean(cap, 60), ts_delta(volume, 60) / ts_mean(volume, 60)) | abandon | 0.471 | 96.9 | 0.0017 | -0.635 | -0.532 | 0.471 |
| 20261101-sysv1-campaign | 1 | 隔夜与日间收益分歧的短期修正 | 0 - ts_mean(safe_div(safe_div(open, cap) - safe_div(ts_delta(close, 1), cap), safe_div(ts_delta(close, 1), cap)), 21) | abandon | 0.435 | 26.5 | 0.0012 | 0.033 | 0.655 | 0.435 |
| camp-c2-r003 | 1 | 隔夜与日间收益分歧的短期修正 | 0 - ts_mean(safe_div(safe_div(open, cap) - safe_div(ts_delta(close, 1), cap), safe_div(ts_delta(close, 1), cap)), 21) | abandon | 0.435 | 26.5 | 0.0012 | 0.033 | 0.655 | 0.435 |
| camp-c1-r005 | 0 | Market-state-conditioned relative strength: high market-sensitivity names with weak recent relative return underperform | -1 * safe_div(ts_sum(ts_returns(close, 1, 1), 63), cap) * ts_std_dev(ts_returns(close, 1, 1), 252) | abandon | 0.429 | 21.1 | 0.0010 | -0.168 | 0.069 | 0.276 |
| 20261101-sysv1-campaign | 0 | Market-state-conditioned relative strength: high market-sensitivity names with weak recent relative return underperform | -1 * safe_div(ts_sum(ts_returns(close, 1, 1), 63), cap) * ts_std_dev(ts_returns(close, 1, 1), 252) | abandon | 0.429 | 21.1 | 0.0010 | -0.168 | 0.069 | 0.276 |
| 20261101-sysv1-campaign | 1 | Market-state-conditioned relative strength: high market-sensitivity names with weak recent relative return underperform | -1 * ts_sum(ts_returns(close, 1, 1), 63) * safe_div(ts_std_dev(ts_returns(close, 1, 1), 252), cap) | abandon | 0.429 | 21.1 | 0.0010 | -0.168 | 0.069 | 0.276 |
| camp-c1-r005 | 1 | Market-state-conditioned relative strength: high market-sensitivity names with weak recent relative return underperform | -1 * ts_sum(ts_returns(close, 1, 1), 63) * safe_div(ts_std_dev(ts_returns(close, 1, 1), 252), cap) | abandon | 0.429 | 21.1 | 0.0010 | -0.168 | 0.069 | 0.276 |
| s500-c2-r004 | 0 | 异常换手（注意力过度交易）：相对自身基线换手抬升的股票在随后数周跑输 | ts_zscore(safe_div(ts_mean(volume, 20), ts_mean(cap, 20)), 120) | optimize | 0.426 | 15.3 | -0.0029 | 0.049 | -0.042 | 0.289 |
| s500-c1-r001 | 0 | Implied float breadth from price and capitalization as a neglect-premium signal | safe_div(ts_mean(close, 20), ts_mean(cap, 20)) | abandon | 0.421 | 32.1 | 0.0008 | -0.395 | -0.708 | -0.181 |
| 20261101-sysv1-campaign | 0 | Turnover intensity versus own long baseline: attention saturation predicts underperformance | -1 * (ts_mean(safe_div(volume, cap), 20) - ts_mean(safe_div(volume, cap), 120)) | abandon | 0.417 | 15.1 | 0.0013 | 0.244 | 1.093 | 0.417 |
| camp-c4-r001 | 0 | Turnover intensity versus own long baseline: attention saturation predicts underperformance | -1 * (ts_mean(safe_div(volume, cap), 20) - ts_mean(safe_div(volume, cap), 120)) | abandon | 0.417 | 15.1 | 0.0013 | 0.244 | 1.093 | 0.417 |
| s500-c2-r004 | 2 | 异常换手（注意力过度交易）：相对自身基线换手抬升的股票在随后数周跑输 | - ts_ir(safe_div(volume, cap), 20) | abandon | 0.416 | 16.3 | -0.0025 | -0.589 | 0.008 | 0.219 |
| s500-c1-r001 | 2 | Implied float breadth from price and capitalization as a neglect-premium signal | -ts_delta(ts_mean(safe_div(cap, close), 20), 60) | abandon | 0.388 | 3.6 | 0.0031 | 0.885 | -0.356 | 0.388 |
| s500-c6-r001 | 1 | Rising implied share count (net issuance) predicts lower future returns | safe_div(ts_returns(close, 63), ts_returns(cap, 63)) * safe_div(ts_mean(volume, 21), ts_mean(volume, 126)) | abandon | 0.369 | 33.6 | -0.0002 | -0.444 | 0.036 | 0.148 |
| s500-c5-r006 | 0 | 价格涨幅相对市值涨幅的偏离（隐含股本变动）预示中期收益 | safe_div(ts_returns(close, 250), ts_returns(cap, 250)) * safe_div(1, ts_mean(safe_div(volume * close, cap), 250)) | abandon | 0.347 | 45.6 | 0.0008 | -0.457 | 0.480 | 0.162 |
| s500-c4-r003 | 2 | Turnover-adjusted illiquidity premium (traded value relative to market cap) | safe_div(ts_mean(safe_div(volume, cap), 20), ts_mean(safe_div(volume, cap), 120)) | abandon | 0.333 | 13.9 | -0.0028 | -0.015 | -0.141 | 0.145 |
| s500-c4-r005 | 1 | 换手成本代理：成交量相对流通/总市值的强度（Amihud 型非流动性倾向） | ts_mean(safe_div(cap, volume), 63) | abandon | 0.317 | 32.0 | 0.0015 | 0.105 | -0.239 | -0.246 |
| s500-c5-r005 | 1 | 市值漂移速度的横截面反转：相对自身历史的规模排名过快上升后回吐 | 0.0 - ts_zscore(cap, 250) + ts_zscore(safe_div(cap, close), 250) | abandon | 0.309 | 10.8 | -0.0052 | -0.107 | 0.144 | 0.243 |
| camp-c4-r002 | 1 | Size premium within large-cap universe (smaller-half outperformance) | -safe_div(ts_mean(cap, 21), ts_mean(cap, 63)) | abandon | 0.305 | 6.8 | -0.0005 | 0.351 | -0.150 | 0.294 |
| 20261101-sysv1-campaign | 1 | 规模溢价：相对市值更小的成分股表现更好 | -1 * safe_div(ts_mean(cap, 21), ts_mean(cap, 63)) | abandon | 0.305 | 6.8 | -0.0005 | 0.351 | -0.150 | 0.294 |
| 20261101-sysv1-campaign | 0 | Size-tier contrast: small-cap names outperform large-cap names cross-sectionally | -1 * safe_div(ts_mean(cap, 21) / close, ts_mean(cap, 63) / close) | abandon | 0.305 | 6.8 | -0.0005 | 0.351 | -0.150 | 0.294 |
| 20261101-sysv1-campaign | 1 | Size premium within large-cap universe (smaller-half outperformance) | -safe_div(ts_mean(cap, 21), ts_mean(cap, 63)) | abandon | 0.305 | 6.8 | -0.0005 | 0.351 | -0.150 | 0.294 |
| camp-c2-r006 | 0 | Size-tier contrast: small-cap names outperform large-cap names cross-sectionally | -1 * safe_div(ts_mean(cap, 21) / close, ts_mean(cap, 63) / close) | abandon | 0.305 | 6.8 | -0.0005 | 0.351 | -0.150 | 0.294 |
| camp-c2-r007 | 1 | 规模溢价：相对市值更小的成分股表现更好 | -1 * safe_div(ts_mean(cap, 21), ts_mean(cap, 63)) | abandon | 0.305 | 6.8 | -0.0005 | 0.351 | -0.150 | 0.294 |
| s500-c2-r001 | 1 | Spread-and-volume friction state predicts higher forward returns for S&P constituents | ts_zscore(ts_std_dev(safe_div(close, cap), 21), 252) - ts_zscore(ts_mean(safe_div(safe_div(close, cap), volume), 21), 252) | abandon | 0.298 | 13.5 | -0.0007 | 0.207 | -0.355 | 0.221 |
| s500-c2-r008 | 0 | High turnover-and-range activity names underperform after speculative attention | -1 * ts_mean(safe_div(volume, safe_div(cap, close)), 21) * ts_std_dev(safe_div(high - low, close), 21) | abandon | 0.283 | 8.4 | 0.0086 | 0.436 | -1.380 | 0.283 |
| s500-c1-r001 | 0 | Abnormal dollar-turnover intensity versus own norm signals attention overhang | -safe_div(ts_mean(safe_div(close * volume, cap), 20), ts_mean(safe_div(close * volume, cap), 120)) | abandon | 0.277 | 64.1 | 0.0002 | 0.361 | 0.396 | 0.277 |
| camp-c1-r001 | 1 | Close-to-rolling-peak proximity in capitalization space as a slow-arbitrage value signal | 0 - ts_mean(safe_div(cap, ts_max(cap, 250)), 5) | abandon | 0.276 | 7.6 | -0.0091 | 0.270 | 0.399 | 0.150 |
| 20261101-sysv1-campaign | 1 | Close-to-rolling-peak proximity in capitalization space as a slow-arbitrage value signal | 0 - ts_mean(safe_div(cap, ts_max(cap, 250)), 5) | abandon | 0.276 | 7.6 | -0.0091 | 0.270 | 0.399 | 0.150 |
| s500-c3-r003 | 2 | 市值口径漂移：市值的超额扩张（含股本/价格混杂）被市场修复 | -1 * ts_zscore(safe_div(cap, ts_mean(cap, 60)) - safe_div(close, ts_mean(close, 60)), 60) | abandon | 0.270 | 17.2 | 0.0005 | 0.193 | 0.837 | 0.270 |
| s500-c2-r008 | 2 | High turnover-and-range activity names underperform after speculative attention | -1 * ts_mean(safe_div(volume, safe_div(cap, close)), 21) * ts_mean(safe_div(high - low, close), 21) | abandon | 0.257 | 6.0 | 0.0090 | 0.382 | -1.339 | 0.257 |
| camp-c3-r002 | 0 | 市值规模的长期漂移：对数市值偏离自身趋势 | -1 * safe_div(ts_delta(cap, 250), ts_mean(cap, 250)) | abandon | 0.255 | 9.9 | -0.0095 | 0.056 | -0.731 | 0.014 |
| 20261101-sysv1-campaign | 0 | 市值规模的长期漂移：对数市值偏离自身趋势 | -1 * safe_div(ts_delta(cap, 250), ts_mean(cap, 250)) | abandon | 0.255 | 9.9 | -0.0095 | 0.056 | -0.731 | 0.014 |
| s500-c3-r001 | 0 | Low-liquidity premium measured by own turnover-to-size | -1 * ts_mean(safe_div(volume * close, cap), 60) | optimize | 0.246 | 4.1 | 0.0075 | 0.266 | -1.204 | 0.246 |
| s500-c3-r006 | 2 | 成交额相对市值的换手异常抬升预示横截面收益偏弱 | -safe_div(ts_mean(safe_div(volume * close, cap), 5), ts_mean(safe_div(volume * close, cap), 63)) | abandon | 0.246 | 65.0 | 0.0002 | 0.393 | 0.082 | 0.246 |
| s500-c2-r008 | 1 | High turnover-and-range activity names underperform after speculative attention | -1 * ts_mean(safe_div(volume, safe_div(cap, close)), 63) * ts_mean(safe_div(high - low, close), 21) | abandon | 0.246 | 65.0 | 0.0002 | 0.393 | 0.082 | 0.246 |
| s500-c4-r005 | 0 | 换手成本代理：成交量相对流通/总市值的强度（Amihud 型非流动性倾向） | safe_div(cap, ts_mean(volume, 21)) | abandon | 0.240 | 32.1 | -0.0012 | 0.668 | -1.228 | -0.181 |
| s500-c7-r003 | 0 | High-volume return premium: turnover surge predicts multi-week continuation | safe_div(ts_mean(safe_div(volume, cap), 20) * safe_div(ts_mean(close, 120), ts_mean(close, 20)), ts_mean(safe_div(volume, cap), 120)) - 1 | abandon | 0.237 | 11.2 | -0.0044 | 0.154 | -0.149 | 0.111 |
| s500-c1-r010 | 2 | 横截面低波动异象：近期已实现波动率越低的股票未来相对收益越高 | -1 * ts_std_dev(ts_returns(close, 1, 1), 60) * safe_div(ts_mean(cap, 21), ts_mean(cap, 21)) | abandon | 0.233 | 64.9 | 0.0003 | 0.374 | 0.221 | 0.233 |
| s500-c7-r001 | 0 | Turnover-normalized dollar volume as an illiquidity premium in a large-cap panel | -1 * ts_mean(safe_div(volume * close, cap), 63) | abandon | 0.229 | 4.0 | 0.0074 | 0.314 | -1.189 | 0.229 |
| 20261101-sysv1-campaign | 0 | 成交额-市值失衡：成交额相对市值异常偏低时后续表现落后 | -1 * ts_mean(safe_div(close * volume, cap), 20) | abandon | 0.214 | 7.7 | 0.0069 | 0.291 | -1.241 | 0.214 |
| camp-c3-r001 | 0 | 成交额-市值失衡：成交额相对市值异常偏低时后续表现落后 | -1 * ts_mean(safe_div(close * volume, cap), 20) | abandon | 0.214 | 7.7 | 0.0069 | 0.291 | -1.241 | 0.214 |
| s500-c4-r007 | 2 | Trading intensity per unit of market value as an attention/illiquidity signal | -1 * safe_div(ts_mean(volume, 20) * close, cap) + safe_div(ts_mean(volume, 20) * close, cap) * 0 | abandon | 0.212 | 6.0 | 0.0069 | 0.308 | -1.184 | 0.212 |
| s500-c4-r007 | 0 | Trading intensity per unit of market value as an attention/illiquidity signal | -1 * safe_div(ts_mean(volume, 20) * close, cap) | abandon | 0.212 | 6.0 | 0.0069 | 0.308 | -1.184 | 0.212 |
| s500-c4-r006 | 2 | 异常换手拥挤度：近期换手率相对自身一年常态抬升越多，随后收益越弱 | -safe_div(ts_median(safe_div(volume, cap), 21), ts_median(safe_div(volume, cap), 252)) | abandon | 0.209 | 10.9 | 0.0060 | -0.140 | 0.437 | 0.209 |
| s500-c1-r002 | 0 | 交易活跃度逆势：相对市值异常的换手率（成交额/市值）预示短期回落 | -1 * ts_mean(safe_div(ts_mean(safe_div(close * volume, cap), 5), ts_mean(safe_div(close * volume, cap), 60)), 5) | abandon | 0.207 | 64.9 | 0.0001 | 0.312 | 0.081 | 0.207 |
| s500-c4-r006 | 0 | 异常换手拥挤度：近期换手率相对自身一年常态抬升越多，随后收益越弱 | -safe_div(ts_mean(safe_div(volume, cap), 21), ts_mean(safe_div(volume, cap), 252)) | abandon | 0.204 | 62.3 | 0.0000 | 0.521 | 0.048 | 0.204 |
_showing top 100 of 214 backtests by IS Sharpe; the full history is in `cap.json`_

## Summary

- backtests: 214, median IS Sharpe 0.199, p90 0.726
- best IS Sharpe 1.443: `-1 * safe_div(ts_max_diff(cap, 126), ts_max(cap, 126)) * safe_div(close, ts_max(close, 126))`
- share of expressions with OOS Sharpe > 0: 51.0% (n=210)

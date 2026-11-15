# Field card: `volume`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **yes**

## EDA evidence

| source_field | dataset_id | semantic_role | factor_usage | unit | missing_fraction | blocking_reasons |
|---|---|---|---|---|---|---|
| Adj_Volume | ds_86999418bce1 | volume | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;not_approved_in_reviewed_config;full_selected_dataset_not_successfully_profiled |
| DlyVol | ds_bd2eab70d3b9 | volume | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;not_approved_in_reviewed_config |

## Backtest evidence (396)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| s500-c1-r004 | 1 | 量价背离：成交量相对基线抬升而价格盘中收在区间下沿，预示走弱 | -1 * ts_mean(safe_div(volume, ts_mean(volume, 60)) * (safe_div(close - low, high - low) - 0.5), 10) | optimize | 1.413 | 47.6 | 0.0137 | -0.061 | -0.181 | 1.413 |
| s500-c2-r005 | 0 | ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | safe_div(volume, ts_mean(volume, 20)) * (0 - ts_zscore(ts_returns(close, 1, 1), 60)) | abandon | 1.390 | 93.1 | 0.0158 | 0.839 | 0.652 | 1.390 |
| s500-c3-r008 | 0 | Short-horizon overreaction in illiquid names reverses more strongly | -1 * safe_div(ts_returns(close, 5), ts_mean(safe_div(volume, cap), 20)) | optimize | 1.300 | 47.0 | 0.0120 | 0.287 | 0.866 | 1.300 |
| s500-c2-r005 | 1 | ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | 0 - safe_div(ts_mean(volume, 5), ts_mean(volume, 63)) * ts_zscore(ts_returns(close, 1, 1), 20) / ts_std_dev(ts_returns(close, 1, 1), 60) | abandon | 1.293 | 92.3 | 0.0135 | 0.887 | 0.716 | 1.293 |
| s500-c2-r005 | 2 | ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | 0 - safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) * ts_zscore(ts_returns(close, 1, 1), 20) | abandon | 1.284 | 92.4 | 0.0135 | 0.884 | 0.715 | 1.284 |
| s500-c3-r001 | 1 | Short-horizon reversal under abnormal volume | -1 * ts_returns(close, 5) * ts_std_dev(ts_zscore(volume, 60), 5) | optimize | 1.280 | 85.1 | 0.0117 | 0.274 | 0.745 | 1.280 |
| s500-c2-r008 | 1 | Cross-sectional abnormal-volume price shock reversal | -1 * ts_returns(close, 5) * ts_ir(volume, 20) | optimize | 1.242 | 52.3 | 0.0113 | 0.094 | 0.755 | 1.242 |
| s500-c2-r008 | 2 | Cross-sectional abnormal-volume price shock reversal | -1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 20)) | optimize | 1.242 | 52.3 | 0.0113 | 0.094 | 0.755 | 1.242 |
| s500-c7-r002 | 1 | Attention-Driven Volume Surge with Recent Price Strength as a Short-Horizon Reversal | -1 * safe_div(safe_div(volume, ts_mean(volume, 20)) * safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 5), 20)), ts_std_dev(volume, 20)) | optimize | 1.232 | 85.6 | 0.0114 | 0.278 | 0.720 | 1.232 |
| s500-c4-r003 | 0 | Short-horizon overreaction reversal on elevated-volume extremes | 0 - ts_zscore(ts_returns(close, 5), 60) * ts_mean(safe_div(volume, ts_mean(volume, 20)), 5) | optimize | 1.210 | 51.4 | 0.0120 | -0.245 | 0.677 | 1.210 |
| s500-c1-r001 | 1 | Index overextension reverses only in stressed-volatility states | -ts_bollinger_position(close, 20, 2.0) * ts_std_dev(returns, 20) * ts_range(high, 20) * ts_range(low, 20) * safe_div(volume, ts_mean(volume, 20)) | abandon | 1.204 | 38.4 | 0.0167 | 0.687 | -0.256 | 1.204 |
| s500-c5-r003 | 0 | Short-horizon reversal conditioned on turnover intensity: low-participation losers recover within two weeks | -1 * safe_div(ts_returns(close, 10), safe_div(ts_mean(volume, 10), ts_mean(cap, 10))) | optimize | 1.169 | 50.2 | 0.0102 | 0.425 | 0.157 | 1.083 |
| s500-c2-r007 | 2 | 放量下跌后的短期反应不足：量价确认型反转 | ts_zscore((-1.0) * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)), 120) | optimize | 1.163 | 47.7 | 0.0119 | -0.037 | 0.652 | 1.163 |
| s500-c6-r003 | 0 | 短期反转：极端收益后的过度反应修正 | -(ts_sum(ts_returns(close, 1, 0), 5)) * safe_div(ts_mean(volume, 20), cap) | abandon | 1.134 | 85.8 | 0.0114 | 0.191 | 0.675 | 1.134 |
| s500-c6-r003 | 1 | 短期反转：极端收益后的过度反应修正 | -ts_sum(ts_returns(close, 1, 0), 5) * ts_bollinger_position(safe_div(ts_mean(volume, 20), cap), 60, 2.0) | abandon | 1.075 | 84.4 | 0.0105 | 0.206 | 0.682 | 1.075 |
| s500-c1-r010 | 1 | 日内区间位置与成交量共振的短期反弹：放量收在区间下沿的股票未来数周相对收益更高 | -1 * ts_mean(safe_div(close - low, high - low) * safe_div(volume, ts_mean(volume, 21)), 10) | accept | 1.053 | 40.9 | 0.0085 | 0.171 | -0.621 | 1.053 |
| s500-c1-r001 | 1 | Short-horizon close-strength reversal conditioned on elevated turnover | -ts_bollinger_position(safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)), 20, 2.0) + ts_zscore(volume, 60) | optimize | 1.044 | 50.5 | 0.0059 | 0.247 | 1.413 | 0.971 |
| s500-c4-r003 | 1 | Short-horizon overreaction reversal on elevated-volume extremes | 0 - ts_zscore(ts_returns(close, 5), 20) * ts_mean(safe_div(volume, ts_mean(volume, 60)), 5) | optimize | 1.029 | 52.2 | 0.0086 | -0.119 | 0.869 | 1.029 |
| 20261101-sysv1-campaign | 0 | Cross-sectional volume-shock amplification of short-horizon reversal | -1 * ts_returns(close, 3) * safe_div(volume, ts_mean(volume, 20)) | optimize | 0.957 | 95.2 | 0.0171 | 0.356 | 0.339 | 0.957 |
| camp-c4-r001 | 0 | Cross-sectional volume-shock amplification of short-horizon reversal | -1 * ts_returns(close, 3) * safe_div(volume, ts_mean(volume, 20)) | optimize | 0.957 | 95.2 | 0.0171 | 0.356 | 0.339 | 0.957 |
| camp-c4-r001 | 1 | Cross-sectional volume-shock amplification of short-horizon reversal | -1 * safe_div(ts_returns(close, 3), safe_div(ts_mean(volume, 20), volume)) | optimize | 0.957 | 95.2 | 0.0171 | 0.356 | 0.339 | 0.957 |
| 20261101-sysv1-campaign | 1 | Cross-sectional volume-shock amplification of short-horizon reversal | -1 * safe_div(ts_returns(close, 3), safe_div(ts_mean(volume, 20), volume)) | optimize | 0.957 | 95.2 | 0.0171 | 0.356 | 0.339 | 0.957 |
| 20261101-sysv1-campaign | 0 | Short-horizon reversal amplified by elevated recent turnover | -1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | optimize | 0.951 | 70.2 | 0.0153 | 0.077 | 0.437 | 0.951 |
| sysv1-h6 | 0 | 放量急跌后的流动性冲击回补：高冲击强度股票短期反弹 | -1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | optimize | 0.951 | 70.2 | 0.0153 | 0.077 | 0.437 | 0.951 |
| camp-c1-r003 | 0 | Short-horizon reversal amplified by elevated recent turnover | -1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | optimize | 0.951 | 70.2 | 0.0153 | 0.077 | 0.437 | 0.951 |
| 20261031-systemv1_50 | 0 | 放量急跌后的流动性冲击回补：高冲击强度股票短期反弹 | -1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | optimize | 0.951 | 70.2 | 0.0153 | 0.077 | 0.437 | 0.951 |
| 20261031-systemv1_50 | 0 | 相对成交量的短期脉冲式均值回归（噪声交易者过度反应） | -( -(safe_div(ts_mean(volume, 5), ts_mean(volume, 60))) * -(ts_delta(close, 5) / close) ) | optimize | 0.947 | 70.2 | 0.0152 | 0.078 | 0.442 | 0.947 |
| sysv1-h7 | 0 | 相对成交量的短期脉冲式均值回归（噪声交易者过度反应） | -( -(safe_div(ts_mean(volume, 5), ts_mean(volume, 60))) * -(ts_delta(close, 5) / close) ) | optimize | 0.947 | 70.2 | 0.0152 | 0.078 | 0.442 | 0.947 |
| s500-c1-r009 | 2 | 成交量相对自身基线的异常放大与短期反转 | -ts_mean(safe_div(volume, ts_median(volume, 40)), 5) * (1 + ts_zscore(safe_div(close, ts_mean(close, 5)), 20)) | optimize | 0.944 | 56.2 | 0.0099 | 0.018 | 0.642 | 0.944 |
| s500-c3-r008 | 2 | Short-horizon overreaction in illiquid names reverses more strongly | -1 * (ts_returns(close, 5) / (1 + abs(ts_returns(close, 5)))) * (2 / (1 + ts_zscore(safe_div(volume, cap), 20))) | optimize | 0.908 | 64.0 | 0.0073 | -0.073 | 0.883 | 0.908 |
| s500-c1-r004 | 0 | 量价背离：成交量相对基线抬升而价格盘中收在区间下沿，预示走弱 | -1 * ts_mean(safe_div(volume, ts_mean(volume, 60)) * safe_div(close - low, high - low), 10) | abandon | 0.901 | 37.1 | 0.0079 | 0.148 | -0.458 | 0.901 |
| s500-c1-r009 | 2 | 大盘指数成交量相对基线的异常放量与随后短期收益反转 | -(ts_zscore(volume, 20) - ts_zscore(safe_div(volume, close), 20)) | abandon | 0.860 | 76.9 | 0.0113 | 0.213 | 0.503 | 0.860 |
| s500-c1-r009 | 2 | 成交量相对自身基线的异常放大与短期反转 | -(ts_zscore(volume, 40) - ts_zscore(safe_div(volume, close), 40)) | abandon | 0.843 | 64.4 | 0.0093 | -0.110 | 0.186 | 0.843 |
| s500-c6-r003 | 1 | 异常成交量后的情绪回归：量能放大的价格走势更易反转 | -ts_zscore(ts_returns(close, 20, 0), 60) * ts_bollinger_position(safe_div(volume, cap), 60, 2.0) | accept | 0.821 | 66.4 | 0.0108 | -0.024 | -0.318 | 0.821 |
| s500-c6-r003 | 0 | 异常成交量后的情绪回归：量能放大的价格走势更易反转 | -1 * ts_zscore(ts_returns(close, 20, 0), 60) * safe_div(safe_div(ts_mean(volume, 20), ts_mean(volume, 60)), safe_div(cap, ts_mean(cap, 60))) | optimize | 0.779 | 43.4 | 0.0112 | 0.024 | -0.316 | 0.779 |
| 20261101-sysv1-campaign | 1 | Volume-confirmed 12-1 style momentum in SP500 constituents | safe_div(ts_mean(close, 126), ts_mean(close, 252)) * safe_div(ts_mean(volume, 21), ts_mean(cap, 21)) * safe_div(close, open) | abandon | 0.755 | 3.9 | -0.0022 | -0.059 | 1.340 | 0.727 |
| camp-c3-r004 | 1 | Volume-confirmed 12-1 style momentum in SP500 constituents | safe_div(ts_mean(close, 126), ts_mean(close, 252)) * safe_div(ts_mean(volume, 21), ts_mean(cap, 21)) * safe_div(close, open) | abandon | 0.755 | 3.9 | -0.0022 | -0.059 | 1.340 | 0.727 |
| s500-c1-r009 | 1 | 成交量相对自身基线的异常放大与短期反转 | -ts_mean(safe_div(volume, ts_median(volume, 40)), 3) * (1 + ts_zscore(close, 40)) | optimize | 0.752 | 49.5 | 0.0063 | 0.244 | 0.166 | 0.752 |
| s500-c1-r001 | 5 | Index overextension reverses only in stressed-volatility states | -ts_bollinger_position(close, 20, 2.0) * safe_div(ts_std_dev(returns, 20) * safe_div(ts_range(high, 20), ts_range(low, 20)) * volume, ts_mean(volume, 60)) | optimize | 0.740 | 31.0 | 0.0131 | -0.009 | -0.521 | 0.740 |
| s500-c1-r009 | 1 | 大盘指数成交量相对基线的异常放量与随后短期收益反转 | -(safe_div(ts_mean(volume, 5), ts_mean(volume, 20)) * (1 + ts_zscore(close, 60))) | abandon | 0.740 | 38.5 | 0.0061 | 0.000 | 0.050 | 0.740 |
| s500-c1-r001 | 3 | Short-horizon close-strength reversal conditioned on elevated turnover | -ts_bollinger_position(safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)), 20, 2.0) * safe_div(volume, ts_mean(volume, 60)) | abandon | 0.727 | 43.7 | 0.0059 | -0.069 | 0.194 | 0.727 |
| s500-c5-r007 | 1 | 量能萎缩下的趋势延续：单位成交量支撑的价格漂移 | safe_div(ts_mean(ts_returns(close, 1, 1), 60), ts_std_dev(ts_returns(close, 1, 1), 60)) * -1 * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | optimize | 0.726 | 28.2 | 0.0039 | 0.276 | 0.075 | 0.726 |
| s500-c1-r001 | 5 | Short-horizon close-strength reversal conditioned on elevated turnover | -safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | abandon | 0.722 | 38.8 | 0.0058 | 0.143 | 0.236 | 0.722 |
| s500-c1-r001 | 4 | Index overextension reverses only in stressed-volatility states | -ts_bollinger_position(close, 20, 2.0) * safe_div(ts_std_dev(returns, 20) * ts_range(high, 20), ts_range(low, 20) * ts_mean(volume, 20)) * volume | optimize | 0.722 | 31.8 | 0.0131 | 0.016 | -0.629 | 0.722 |
| s500-c4-r004 | 2 | Volatile breaks below a long-run index reference level precede further weakness | -1 * safe_div(close - ts_ema(close, 120), close * ts_std_dev(returns, 20)) * (1 + ts_zscore(ts_mean(volume, 20), 120)) | optimize | 0.701 | 29.3 | 0.0022 | 0.109 | 0.247 | 0.701 |
| 20261101-sysv1-campaign | 0 | Smaller-cap tilt within the S&P universe: lower market cap names carry a size premium after controlling for liquidity | -safe_div(ts_mean(cap, 21), ts_mean(volume, 252)) | abandon | 0.693 | 0.5 | -0.0024 | 0.243 | 1.788 | 0.596 |
| camp-c1-r004 | 0 | Smaller-cap tilt within the S&P universe: lower market cap names carry a size premium after controlling for liquidity | -safe_div(ts_mean(cap, 21), ts_mean(volume, 252)) | abandon | 0.693 | 0.5 | -0.0024 | 0.243 | 1.788 | 0.596 |
| s500-c4-r004 | 1 | Dollar-volume illiquidity premium: names with high price impact per traded dollar underperform after liquidity shocks | safe_div(ts_mean(safe_div(abs(ts_returns(close, 1)), close * volume), 20), ts_median(safe_div(abs(ts_returns(close, 1)), close * volume), 20)) | abandon | 0.665 | 44.5 | 0.0027 | 0.272 | 0.231 | 0.504 |
| s500-c5-r002 | 0 | 收益方差与成交量方差的错配：关注度驱动的过反应修正 | -safe_div(ts_std_dev(ts_returns(close, 1), 21), ts_std_dev(ts_delta(volume, 1), 21)) | abandon | 0.658 | 10.2 | 0.0002 | 0.849 | 1.295 | 0.658 |
| s500-c5-r007 | 0 | 量能萎缩下的趋势延续：单位成交量支撑的价格漂移 | safe_div(ts_returns(close, 60, 1), ts_std_dev(ts_returns(close, 1, 1), 60)) * -1 * ts_zscore(ts_mean(volume, 5), 250) | optimize | 0.655 | 46.9 | 0.0052 | -0.121 | -0.518 | 0.655 |
| s500-c1-r003 | 0 | 成交额（金额流动性）的低水平与压缩：流动性风险溢价的横截面候选 | -(ts_mean(close * volume, 120) + (ts_mean(close * volume, 20) - ts_mean(close * volume, 120))) | abandon | 0.654 | 3.5 | 0.0056 | -0.203 | -1.265 | 0.447 |
| s500-c1-r003 | 1 | 成交额（金额流动性）的低水平与压缩：流动性风险溢价的横截面候选 | -ts_median(close * volume, 60) | abandon | 0.651 | 1.6 | 0.0055 | -0.217 | -1.235 | 0.440 |
| s500-c1-r001 | 0 | Short-horizon close-strength reversal conditioned on elevated turnover | -safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) * (1.0 + ts_zscore(volume, 60)) | abandon | 0.637 | 116.1 | 0.0027 | 0.114 | 0.050 | 0.637 |
| camp-c2-r001 | 0 | 价格冲击成本代理：低流动性的横截面溢价 | ts_mean(safe_div(abs(ts_returns(close, 1)), volume * close), 60) | abandon | 0.634 | 2.3 | 0.0009 | -0.049 | -0.594 | 0.488 |
| 20261101-sysv1-campaign | 0 | 价格冲击成本代理：低流动性的横截面溢价 | ts_mean(safe_div(abs(ts_returns(close, 1)), volume * close), 60) | abandon | 0.634 | 2.3 | 0.0009 | -0.049 | -0.594 | 0.488 |
| s500-c6-r002 | 0 | Size-graded range compression: extreme volume-scaled cap deciles mean-revert | 0 - safe_div(safe_div(cap, ts_delta(cap, 60)), safe_div(ts_mean(volume, 60), ts_delta(volume, 60) + ts_mean(volume, 60))) | abandon | 0.623 | 45.2 | -0.0002 | 0.401 | 0.090 | 0.587 |
| camp-c2-r007 | 0 | 非流动性风险补偿：单位成交额的日价格冲击 | ts_mean(safe_div(abs(ts_returns(close, 1)), volume * close), 63) | abandon | 0.622 | 2.2 | 0.0009 | -0.038 | -0.597 | 0.464 |
| 20261101-sysv1-campaign | 0 | 非流动性风险补偿：单位成交额的日价格冲击 | ts_mean(safe_div(abs(ts_returns(close, 1)), volume * close), 63) | abandon | 0.622 | 2.2 | 0.0009 | -0.038 | -0.597 | 0.464 |
| s500-c3-r003 | 1 | 非流动性溢价：单位成交额带来的价格冲击越大，后续补偿收益越高 | ts_mean(safe_div(abs(ts_returns(close, 1, 1)), ts_mean(close * volume, 5)), 20) | abandon | 0.611 | 32.3 | 0.0039 | 0.291 | -0.217 | -0.192 |
| s500-c4-r008 | 1 | 流动性压力：单位成交额换手偏高（高波动低换手）的股票存在规模内收益溢价 | ts_mean(safe_div(safe_div(high - low, close) + abs(ts_returns(close, 1)), close * volume), 21) | abandon | 0.604 | 2.2 | 0.0008 | -0.098 | -0.641 | 0.483 |
| s500-c1-r007 | 2 | 资金效率恶化：成交额-收益耦合强度抬升后的短期弱市倾向 | -ts_zscore(ts_mean(volume * returns, 20), 250) | optimize | 0.598 | 19.3 | 0.0070 | 0.402 | 0.336 | 0.598 |
| s500-c5-r003 | 1 | Short-horizon reversal conditioned on turnover intensity: low-participation losers recover within two weeks | -1 * safe_div(ts_returns(close, 10), 1 + ts_zscore(safe_div(ts_mean(volume, 10), ts_mean(cap, 10)), 63)) | optimize | 0.596 | 68.3 | 0.0058 | 0.486 | 0.118 | 0.596 |
| s500-c3-r007 | 2 | Rally without participation: price moves not echoed by a turnover expansion fade over the next month | -1 * ts_mean(ts_returns(close, 21) * safe_div(ts_std_dev(volume, 21), ts_mean(volume, 63)), 1) | optimize | 0.589 | 34.4 | 0.0094 | 0.259 | 0.329 | 0.589 |
| s500-c4-r008 | 2 | 流动性压力：单位成交额换手偏高（高波动低换手）的股票存在规模内收益溢价 | ts_median(safe_div(abs(safe_div(high - low, close)), close * volume), 21) | abandon | 0.586 | 2.5 | 0.0007 | -0.125 | -0.739 | 0.459 |
| s500-c1-r009 | 0 | 成交量相对自身基线的异常放大与短期反转 | -(ts_zscore(volume, 40) + ts_zscore(close, 40)) | optimize | 0.585 | 70.2 | 0.0019 | 0.303 | 0.176 | 0.585 |
| camp-c2-r007 | 1 | 非流动性风险补偿：单位成交额的日价格冲击 | ts_mean(safe_div(abs(ts_returns(close, 1)), ts_mean(close * volume, 21)), 63) | abandon | 0.584 | 2.4 | 0.0006 | -0.061 | -0.563 | 0.428 |
| 20261101-sysv1-campaign | 1 | 非流动性风险补偿：单位成交额的日价格冲击 | ts_mean(safe_div(abs(ts_returns(close, 1)), ts_mean(close * volume, 21)), 63) | abandon | 0.584 | 2.4 | 0.0006 | -0.061 | -0.563 | 0.428 |
| s500-c3-r003 | 0 | 非流动性溢价：单位成交额带来的价格冲击越大，后续补偿收益越高 | ts_mean(safe_div(abs(ts_returns(close, 1, 1)), close * volume), 20) | abandon | 0.579 | 3.3 | 0.0007 | -0.074 | -0.527 | 0.456 |
| s500-c5-r001 | 0 | Intrabar volume absorption: a high share of daily volume arriving on wide-range days predicts lower forward return | safe_div(ts_sum((volume / ts_mean(volume, 60)) * ((high - low) / close), 30), ts_sum(abs(ts_returns(close, 1)), 30)) | abandon | 0.566 | 18.1 | 0.0009 | -0.550 | -1.291 | 0.357 |
| s500-c5-r002 | 1 | 横截面成交额加权波动率：高换手波动股的短期收益折价 | -safe_div(ts_ir(ts_returns(close, 1) * (high - low), 63), ts_mean(volume, 21)) | abandon | 0.543 | 20.3 | 0.0027 | 0.309 | 0.110 | 0.512 |
| s500-c1-r001 | 2 | Short-horizon close-strength reversal conditioned on elevated turnover | -ts_bollinger_position(safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)), 60, 2.0) * safe_div(volume, ts_mean(volume, 60)) | abandon | 0.536 | 29.3 | 0.0085 | -0.178 | -0.325 | 0.536 |
| s500-c1-r007 | 1 | 资金效率恶化：成交额-收益耦合强度抬升后的短期弱市倾向 | -(ts_mean(returns * volume, 20) / ts_mean(abs(returns) * volume, 20)) | abandon | 0.527 | 32.7 | 0.0074 | 0.160 | -0.107 | 0.527 |
| s500-c5-r002 | 0 | 横截面成交额加权波动率：高换手波动股的短期收益折价 | -ts_std_dev(ts_returns(close, 1) * (high - low) * ts_bollinger_width(volume, 63), 63) | optimize | 0.520 | 4.0 | 0.0099 | 0.935 | -0.502 | 0.520 |
| s500-c6-r001 | 0 | Rising implied share count (net issuance) predicts lower future returns | safe_div(ts_returns(close, 63), ts_returns(cap, 63)) * safe_div(ts_mean(volume, 5), ts_mean(volume, 63)) | abandon | 0.509 | 48.6 | 0.0016 | -0.105 | 1.227 | 0.321 |
| 20261031-systemv1_50 | 0 | 成交量异常放大后的价格延续：相对历史均量的量能冲击对短期收益的预测 | safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | abandon | 0.506 | 39.2 | 0.0018 | 0.176 | 0.889 | 0.429 |
| sysv1-h2 | 0 | 成交量异常放大后的价格延续：相对历史均量的量能冲击对短期收益的预测 | safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | abandon | 0.506 | 39.2 | 0.0018 | 0.176 | 0.889 | 0.429 |
| s500-c4-r003 | 0 | Turnover-adjusted illiquidity premium (traded value relative to market cap) | ts_median(safe_div(cap, volume), 60) | abandon | 0.490 | 31.7 | 0.0006 | -0.756 | 0.168 | -0.188 |
| camp-c2-r003 | 1 | 换手率水平与稳定性（持股结构投机度） | 0 - safe_div(ts_mean(safe_div(safe_div(volume * close, close), cap), 63), ts_std_dev(safe_div(safe_div(volume * close, close), cap), 63)) | abandon | 0.484 | 8.2 | -0.0021 | -0.874 | 0.829 | 0.277 |
| 20261101-sysv1-campaign | 1 | 换手率水平与稳定性（持股结构投机度） | 0 - safe_div(ts_mean(safe_div(safe_div(volume * close, close), cap), 63), ts_std_dev(safe_div(safe_div(volume * close, close), cap), 63)) | abandon | 0.484 | 8.2 | -0.0021 | -0.874 | 0.829 | 0.277 |
| s500-c6-r002 | 1 | Size-graded range compression: extreme volume-scaled cap deciles mean-revert | 0 - safe_div(ts_delta(cap, 60) / ts_mean(cap, 60), ts_delta(volume, 60) / ts_mean(volume, 60)) | abandon | 0.471 | 96.9 | 0.0017 | -0.635 | -0.532 | 0.471 |
| camp-c1-r001 | 1 | Volume-expansion-without-price-progress as an unresolved-disagreement signal | 0 - safe_div(safe_div(abs(ts_returns(close, 20)), ts_sum(abs(ts_returns(close, 1)), 20)), ts_mean(safe_div(volume, ts_mean(volume, 20)), 20)) | abandon | 0.445 | 63.1 | 0.0045 | 0.110 | -0.615 | 0.378 |
| 20261101-sysv1-campaign | 1 | Volume-expansion-without-price-progress as an unresolved-disagreement signal | 0 - safe_div(safe_div(abs(ts_returns(close, 20)), ts_sum(abs(ts_returns(close, 1)), 20)), ts_mean(safe_div(volume, ts_mean(volume, 20)), 20)) | abandon | 0.445 | 63.1 | 0.0045 | 0.110 | -0.615 | 0.378 |
| s500-c3-r007 | 0 | Rally without participation: price moves not echoed by a turnover expansion fade over the next month | -1 * ts_mean(ts_returns(close, 5) * safe_div(ts_std_dev(volume, 21), ts_mean(volume, 63)), 21) | abandon | 0.441 | 23.1 | 0.0026 | 0.005 | 0.090 | 0.441 |
| s500-c2-r004 | 0 | 异常换手（注意力过度交易）：相对自身基线换手抬升的股票在随后数周跑输 | ts_zscore(safe_div(ts_mean(volume, 20), ts_mean(cap, 20)), 120) | optimize | 0.426 | 15.3 | -0.0029 | 0.049 | -0.042 | 0.289 |
| s500-c1-r009 | 0 | 大盘指数成交量相对基线的异常放量与随后短期收益反转 | -(safe_div(ts_mean(volume, 5), ts_mean(volume, 20)) * safe_div(close, ts_mean(close, 20))) | abandon | 0.419 | 52.4 | 0.0006 | 0.305 | -0.483 | 0.419 |
| camp-c4-r001 | 0 | Turnover intensity versus own long baseline: attention saturation predicts underperformance | -1 * (ts_mean(safe_div(volume, cap), 20) - ts_mean(safe_div(volume, cap), 120)) | abandon | 0.417 | 15.1 | 0.0013 | 0.244 | 1.093 | 0.417 |
| 20261101-sysv1-campaign | 0 | Turnover intensity versus own long baseline: attention saturation predicts underperformance | -1 * (ts_mean(safe_div(volume, cap), 20) - ts_mean(safe_div(volume, cap), 120)) | abandon | 0.417 | 15.1 | 0.0013 | 0.244 | 1.093 | 0.417 |
| s500-c2-r004 | 2 | 异常换手（注意力过度交易）：相对自身基线换手抬升的股票在随后数周跑输 | - ts_ir(safe_div(volume, cap), 20) | abandon | 0.416 | 16.3 | -0.0025 | -0.589 | 0.008 | 0.219 |
| s500-c3-r007 | 1 | Rally without participation: price moves not echoed by a turnover expansion fade over the next month | -1 * ts_mean(ts_returns(close, 5) * (safe_div(ts_mean(volume, 21), ts_mean(volume, 63)) - 1), 21) | abandon | 0.411 | 20.5 | -0.0006 | 0.631 | 0.809 | 0.411 |
| s500-c7-r002 | 1 | Volume-Normalized Intraday Price Range as an Attention/Uncertainty Overreaction Signal | -1 * safe_div(ts_zscore(ts_mean(safe_div(high - low, close), 5), 20), ts_zscore(volume, 20)) | abandon | 0.391 | 138.9 | 0.0018 | 0.265 | 0.159 | 0.181 |
| s500-c3-r001 | 0 | Short-horizon reversal under abnormal volume | -1 * ts_returns(close, 5) * ts_zscore(volume, 60) | abandon | 0.389 | 123.4 | 0.0034 | -0.086 | -0.187 | 0.389 |
| s500-c1-r005 | 1 | Volume-shock exhaustion: abnormal volume without price confirmation predicts underperformance | -1 * safe_div(abs(ts_returns(close, 5)), ts_std_dev(abs(ts_returns(close, 1)), 63)) * safe_div(ts_mean(volume, 20), ts_mean(volume, 63)) | abandon | 0.387 | 100.7 | 0.0034 | -0.423 | -0.342 | 0.216 |
| s500-c1-r009 | 0 | 成交量相对自身基线的异常放大与短期反转 | -(safe_div(volume, ts_mean(volume, 40)) * safe_div(close, ts_mean(close, 40))) | abandon | 0.379 | 126.5 | -0.0044 | 0.241 | -0.034 | 0.379 |
| s500-c1-r002 | 0 | 极端成交日集中度：窗口内最活跃单日占比过高的股票短期偏弱 | -1 * safe_div(ts_max(volume, 20), ts_mean(volume, 20)) | abandon | 0.373 | 24.7 | 0.0030 | 1.091 | 0.652 | 0.373 |
| s500-c6-r001 | 1 | Rising implied share count (net issuance) predicts lower future returns | safe_div(ts_returns(close, 63), ts_returns(cap, 63)) * safe_div(ts_mean(volume, 21), ts_mean(volume, 126)) | abandon | 0.369 | 33.6 | -0.0002 | -0.444 | 0.036 | 0.148 |
| s500-c2-r006 | 2 | Aggregate index volume shock relative to its own baseline as a market-level reversal signal | -(ts_zscore(safe_div(ts_mean(volume, 5), ts_mean(volume, 60)), 120) * ts_zscore(safe_div(close, ts_mean(close, 60)), 120) * ts_zscore(returns, 120)) | abandon | 0.368 | 176.5 | -0.0047 | -0.819 | -0.096 | 0.336 |
| s500-c2-r005 | 1 | 横截面：换手率异常（量能相对自身基线放大）与后续收益 | 0 - ts_zscore(safe_div(ts_mean(volume, 5), ts_mean(volume, 63)), 126) * ts_returns(close, 20, 1) | abandon | 0.366 | 53.9 | 0.0018 | -0.846 | 0.138 | 0.366 |
| s500-c1-r003 | 2 | 成交额（金额流动性）的低水平与压缩：流动性风险溢价的横截面候选 | -safe_div(ts_mean(close * volume, 20), ts_std_dev(close * volume, 120)) | abandon | 0.363 | 6.8 | -0.0029 | -0.390 | 0.735 | 0.069 |
| s500-c3-r004 | 0 | Idiosyncratic path instability per unit of exit liquidity and its medium-horizon premium | -safe_div(ts_std_dev(ts_returns(close, 1), 60), ts_scale(safe_div(volume, ts_median(volume, 60)), 60)) | abandon | 0.359 | 84.1 | 0.0095 | 0.409 | -0.651 | 0.359 |
| s500-c5-r006 | 0 | 价格涨幅相对市值涨幅的偏离（隐含股本变动）预示中期收益 | safe_div(ts_returns(close, 250), ts_returns(cap, 250)) * safe_div(1, ts_mean(safe_div(volume * close, cap), 250)) | abandon | 0.347 | 45.6 | 0.0008 | -0.457 | 0.480 | 0.162 |
_showing top 100 of 396 backtests by IS Sharpe; the full history is in `volume.json`_

## Summary

- backtests: 396, median IS Sharpe 0.066, p90 0.740
- best IS Sharpe 1.413: `-1 * ts_mean(safe_div(volume, ts_mean(volume, 60)) * (safe_div(close - low, high - low) - 0.5), 10)`
- share of expressions with OOS Sharpe > 0: 49.1% (n=387)

# Field card: `low`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **yes**

## EDA evidence

| source_field | dataset_id | semantic_role | factor_usage | unit | missing_fraction | blocking_reasons |
|---|---|---|---|---|---|---|
| Adj_Low | ds_86999418bce1 | price | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;price_adjustment_convention_unknown;not_approved_in_reviewed_config;full_selected_dataset_not_successfully_profiled |
| DlyLow | ds_bd2eab70d3b9 | price | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;price_adjustment_convention_unknown;not_approved_in_reviewed_config |

## Backtest evidence (295)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| s500-c4-r009 | 1 | 日内收盘位置：收盘价靠近区间低点预示短期反弹 | -(safe_div(close - low, high - low)) | optimize | 2.621 | 94.1 | 0.0253 | 0.365 | 0.259 | 2.621 |
| s500-c2-r002 | 1 | Intraday order imbalance from the closing clip as a short-horizon index pressure signal | -1 * ts_zscore(safe_div(close - low, high - low), 20) | accept | 2.210 | 94.6 | 0.0204 | 0.150 | 0.629 | 2.185 |
| camp-c2-r002 | 0 | Range-position (close location within high-low band) as short-term sentiment proxy | -1 * ts_mean(safe_div(close - low, high - low), 5) | optimize | 2.059 | 78.0 | 0.0193 | 0.127 | 0.054 | 2.059 |
| s500-c6-r003 | 0 | 收盘位于区间上沿的短期反转（日内位置效应） | -ts_mean(safe_div(close - low, high - low), 5) | abandon | 2.059 | 78.0 | 0.0193 | 0.127 | 0.054 | 2.059 |
| s500-c4-r009 | 0 | 日内收盘位置：收盘价靠近区间低点预示短期反弹 | -(ts_mean(safe_div(close - low, high - low), 5)) | optimize | 2.059 | 78.0 | 0.0193 | 0.127 | 0.054 | 2.059 |
| 20261101-sysv1-campaign | 0 | Range-position (close location within high-low band) as short-term sentiment proxy | -1 * ts_mean(safe_div(close - low, high - low), 5) | optimize | 2.059 | 78.0 | 0.0193 | 0.127 | 0.054 | 2.059 |
| s500-c4-r005 | 1 | 日内收益位置：收盘在当日振幅中的相对位置（Close Location Value） | 0 - ts_zscore(ts_mean(safe_div(close - low, high - low), 10), 63) | accept | 2.052 | 56.8 | 0.0190 | -0.070 | -0.491 | 2.052 |
| 20261101-sysv1-campaign | 1 | Persistent close-over-open bid as a continuation signal | -1 * ts_mean(safe_div(close, open) * safe_div(close - low, high - low), 5) | abandon | 2.050 | 78.2 | 0.0197 | 0.145 | 0.059 | 2.050 |
| camp-c3-r004 | 1 | Persistent close-over-open bid as a continuation signal | -1 * ts_mean(safe_div(close, open) * safe_div(close - low, high - low), 5) | abandon | 2.050 | 78.2 | 0.0197 | 0.145 | 0.059 | 2.050 |
| camp-c1-r003 | 1 | Persistent closing near the daily high indicates crowded pressure and precedes weaker returns | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 10), 60) | accept | 2.004 | 57.0 | 0.0186 | -0.077 | -0.470 | 2.004 |
| 20261101-sysv1-campaign | 1 | Persistent closing near the daily high indicates crowded pressure and precedes weaker returns | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 10), 60) | accept | 2.004 | 57.0 | 0.0186 | -0.077 | -0.470 | 2.004 |
| s500-c7-r001 | 1 | Close positioned near the session low signals short-horizon supply pressure | ts_mean(safe_div(close - low, ts_range(high, 21)), 5) - ts_mean(safe_div(close - low, high - low), 5) | optimize | 1.947 | 67.4 | 0.0149 | 0.097 | 0.003 | 1.921 |
| s500-c2-r002 | 0 | Intraday order imbalance from the closing clip as a short-horizon index pressure signal | -1 * ts_zscore(safe_div(close - low, high - low), 10) | accept | 1.898 | 99.4 | 0.0186 | -0.014 | 0.868 | 1.806 |
| s500-c2-r006 | 2 | Stock-specific volatility expansion relative to its own baseline as an uncertainty-discount signal | -(safe_div(ts_mean(ts_max(close, 1) - ts_min(low, 1), 5), ts_mean(ts_max(high, 1) - ts_min(open, 1), 20))) | abandon | 1.801 | 69.7 | 0.0139 | -0.097 | -0.116 | 1.801 |
| s500-c6-r003 | 1 | 收盘位于区间上沿的短期反转（日内位置效应） | -(ts_mean(safe_div(close - low, high - low), 5) - ts_mean(safe_div(close - low, high - low), 20)) | optimize | 1.749 | 83.0 | 0.0161 | 0.089 | 0.564 | 1.749 |
| 20261101-sysv1-campaign | 1 | Closing-location persistence: close near daily high predicts positive forward drift | ts_mean(safe_div(close - low, high - low), 20) - ts_mean(safe_div(close - low, high - low), 5) | optimize | 1.749 | 83.0 | 0.0161 | 0.089 | 0.564 | 1.749 |
| camp-c4-r001 | 1 | Closing-location persistence: close near daily high predicts positive forward drift | ts_mean(safe_div(close - low, high - low), 20) - ts_mean(safe_div(close - low, high - low), 5) | optimize | 1.749 | 83.0 | 0.0161 | 0.089 | 0.564 | 1.749 |
| 20261031-systemv1_50 | 0 | 日内收盘位置与短期反转：日收益分布在当日高低区间中的位置对后续1周收益的预测 | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| s500-c4-r010 | 0 | 收盘持续位于日内区间高位的个股短期收益回吐 | -ts_mean(safe_div(close - low, high - low), 10) | accept | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| camp-c3-r002 | 0 | 日内价格位置低点：收盘价靠近日低点的持续弱势 | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| 20261101-sysv1-campaign | 0 | 日内价格位置低点：收盘价靠近日低点的持续弱势 | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| sysv1-h2 | 0 | 日内收盘位置与短期反转：日收益分布在当日高低区间中的位置对后续1周收益的预测 | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| s500-c2-r002 | 2 | Intraday order imbalance from the closing clip as a short-horizon index pressure signal | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| 20261101-sysv1-campaign | 1 | 日内价格位置低点：收盘价靠近日低点的持续弱势 | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 20), 120) | accept | 1.492 | 35.4 | 0.0160 | -0.026 | -0.176 | 1.492 |
| camp-c3-r002 | 1 | 日内价格位置低点：收盘价靠近日低点的持续弱势 | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 20), 120) | accept | 1.492 | 35.4 | 0.0160 | -0.026 | -0.176 | 1.492 |
| camp-c3-r004 | 0 | Repeated close-at-band-floor as a mean-reversion setup | safe_div(ts_mean(safe_div(low, close), 10), ts_mean(safe_div(close, high), 10)) | accept | 1.446 | 49.5 | 0.0179 | 0.144 | -0.516 | 1.446 |
| 20261101-sysv1-campaign | 0 | Repeated close-at-band-floor as a mean-reversion setup | safe_div(ts_mean(safe_div(low, close), 10), ts_mean(safe_div(close, high), 10)) | accept | 1.446 | 49.5 | 0.0179 | 0.144 | -0.516 | 1.446 |
| s500-c1-r004 | 1 | 量价背离：成交量相对基线抬升而价格盘中收在区间下沿，预示走弱 | -1 * ts_mean(safe_div(volume, ts_mean(volume, 60)) * (safe_div(close - low, high - low) - 0.5), 10) | optimize | 1.413 | 47.6 | 0.0137 | -0.061 | -0.181 | 1.413 |
| s500-c4-r005 | 0 | 日内收益位置：收盘在当日振幅中的相对位置（Close Location Value） | 0 - ts_mean(safe_div(close - low, high - low), 15) | optimize | 1.359 | 39.4 | 0.0128 | 0.115 | -0.679 | 1.359 |
| s500-c4-r009 | 1 | 市场区间恐慌度：大盘区间位置贴近低位预示短期反弹 | -(safe_div(close - ts_min(low, 10), ts_max(high, 10) - ts_min(low, 10))) | optimize | 1.314 | 39.3 | 0.0129 | 0.090 | 0.455 | 1.314 |
| s500-c1-r001 | 2 | Range asymmetry: close near the session low after a wide range signals unresolved selling pressure | -ts_mean(safe_div(close - low, high - low), 20) * (ts_max(high, 20) - ts_min(low, 20)) | optimize | 1.229 | 11.6 | 0.0116 | 0.606 | -0.541 | 1.012 |
| s500-c1-r001 | 1 | Index overextension reverses only in stressed-volatility states | -ts_bollinger_position(close, 20, 2.0) * ts_std_dev(returns, 20) * ts_range(high, 20) * ts_range(low, 20) * safe_div(volume, ts_mean(volume, 20)) | abandon | 1.204 | 38.4 | 0.0167 | 0.687 | -0.256 | 1.204 |
| 20261101-sysv1-campaign | 1 | Range-position (close location within high-low band) as short-term sentiment proxy | -1 * ts_mean(safe_div(close - low, high - low), 20) | optimize | 1.137 | 33.7 | 0.0104 | 0.081 | -0.390 | 1.137 |
| camp-c1-r003 | 0 | Persistent closing near the daily high indicates crowded pressure and precedes weaker returns | -1 * ts_mean(safe_div(close - low, high - low), 20) | optimize | 1.137 | 33.7 | 0.0104 | 0.081 | -0.390 | 1.137 |
| s500-c1-r001 | 0 | Range asymmetry: close near the session low after a wide range signals unresolved selling pressure | -ts_mean(safe_div(close - low, high - low), 20) | optimize | 1.137 | 33.7 | 0.0104 | 0.081 | -0.390 | 1.137 |
| camp-c2-r002 | 1 | Range-position (close location within high-low band) as short-term sentiment proxy | -1 * ts_mean(safe_div(close - low, high - low), 20) | optimize | 1.137 | 33.7 | 0.0104 | 0.081 | -0.390 | 1.137 |
| 20261101-sysv1-campaign | 0 | Intraday close-location: closes in the top of the daily range predict weaker next-month returns | ts_mean(-1 * safe_div(close - low, high - low), 21) | optimize | 1.101 | 32.8 | 0.0099 | 0.152 | -0.287 | 1.101 |
| camp-c2-r006 | 0 | Intraday close-location: closes in the top of the daily range predict weaker next-month returns | ts_mean(-1 * safe_div(close - low, high - low), 21) | optimize | 1.101 | 32.8 | 0.0099 | 0.152 | -0.287 | 1.101 |
| s500-c2-r001 | 1 | Range-position asymmetry within a stock's own yearly band predicts weaker forward returns | -1 * safe_div(ts_mean(close - ts_min(low, 252), 21), ts_range(high, 252)) * ts_zscore(high - ts_max(high, 252), 21) | accept | 1.098 | 46.6 | 0.0106 | 0.043 | 0.480 | 0.991 |
| s500-c1-r010 | 1 | 日内区间位置与成交量共振的短期反弹：放量收在区间下沿的股票未来数周相对收益更高 | -1 * ts_mean(safe_div(close - low, high - low) * safe_div(volume, ts_mean(volume, 21)), 10) | accept | 1.053 | 40.9 | 0.0085 | 0.171 | -0.621 | 1.053 |
| s500-c1-r001 | 1 | Short-horizon close-strength reversal conditioned on elevated turnover | -ts_bollinger_position(safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)), 20, 2.0) + ts_zscore(volume, 60) | optimize | 1.044 | 50.5 | 0.0059 | 0.247 | 1.413 | 0.971 |
| s500-c1-r005 | 0 | Range-position mean reversion: closes pinned to the top of a 20-day high-low range underperform | -1 * safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) | optimize | 1.043 | 58.5 | 0.0136 | 0.171 | 0.269 | 1.043 |
| s500-c3-r004 | 0 | Within-range price position as a short-horizon overreaction signal | -safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) | optimize | 1.043 | 58.5 | 0.0136 | 0.171 | 0.269 | 1.043 |
| s500-c4-r009 | 0 | 市场区间恐慌度：大盘区间位置贴近低位预示短期反弹 | -(safe_div(close - ts_min(low, 21), ts_max(high, 21) - ts_min(low, 21))) | abandon | 1.024 | 57.4 | 0.0134 | 0.166 | 0.251 | 1.024 |
| s500-c3-r004 | 2 | Within-range price position as a short-horizon overreaction signal | -ts_bollinger_percent(close, 20, 2) * safe_div(ts_delta(high, 5), safe_div(ts_max(high, 20) - ts_min(low, 20), ts_mean(low, 20))) | accept | 0.999 | 52.5 | 0.0063 | 0.106 | 0.808 | 0.976 |
| s500-c4-r010 | 2 | 收盘持续位于日内区间高位的个股短期收益回吐 | -ts_zscore(ts_mean(safe_div(close - ts_median(close, 10), high - low), 10), 252) | optimize | 0.982 | 25.8 | 0.0103 | -0.022 | 0.468 | 0.982 |
| s500-c5-r002 | 0 | 日内位置偏高的过量波动：高开低走后的短期反转 | -ts_mean(safe_div(close - low, high - low) * abs(ts_returns(close, 1)), 5) | optimize | 0.978 | 58.0 | 0.0200 | -0.068 | -1.221 | 0.978 |
| s500-c2-r006 | 1 | Stock-specific volatility expansion relative to its own baseline as an uncertainty-discount signal | -(safe_div(ts_mean((close + high + low) / open, 5), ts_mean((close + high + low) / open, 20))) | optimize | 0.909 | 47.6 | 0.0086 | 0.062 | 0.467 | 0.909 |
| s500-c1-r004 | 0 | 量价背离：成交量相对基线抬升而价格盘中收在区间下沿，预示走弱 | -1 * ts_mean(safe_div(volume, ts_mean(volume, 60)) * safe_div(close - low, high - low), 10) | abandon | 0.901 | 37.1 | 0.0079 | 0.148 | -0.458 | 0.901 |
| s500-c1-r005 | 2 | Range-position mean reversion: closes pinned to the top of a 20-day high-low range underperform | -1 * safe_div(close - ts_min(low, 40), ts_max(high, 40) - ts_min(low, 40)) | optimize | 0.874 | 43.5 | 0.0102 | 0.132 | 0.174 | 0.874 |
| s500-c6-r002 | 0 | Range-position extremes predict reversal of multi-week price trends | 0 - safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)) | optimize | 0.814 | 31.7 | 0.0080 | 0.138 | 0.216 | 0.814 |
| camp-c1-r004 | 0 | Position within the recent trading range: stocks near the low end of their own 63-day range outperform | -safe_div(close - ts_min(low, 63), ts_max(high, 63) - ts_min(low, 63)) | abandon | 0.794 | 29.3 | 0.0048 | 0.252 | 0.219 | 0.786 |
| 20261101-sysv1-campaign | 0 | Position within the recent trading range: stocks near the low end of their own 63-day range outperform | -safe_div(close - ts_min(low, 63), ts_max(high, 63) - ts_min(low, 63)) | abandon | 0.794 | 29.3 | 0.0048 | 0.252 | 0.219 | 0.786 |
| s500-c4-r008 | 2 | 区间位置回归：多周区间内的价格位置过高后出现反转 | -1 * ts_zscore(safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)), 126) | optimize | 0.766 | 35.3 | 0.0119 | 0.081 | 0.568 | 0.766 |
| s500-c5-r007 | 1 | 短期波动耗竭：日内振幅相对自身基线的压缩预示相对收益 | -1 * safe_div(ts_mean(safe_div(high - low, close), 5), ts_mean(safe_div(high - low, close), 60)) * ts_delta(close, 20) | optimize | 0.760 | 34.8 | 0.0078 | 0.388 | 0.158 | 0.741 |
| s500-c1-r001 | 5 | Index overextension reverses only in stressed-volatility states | -ts_bollinger_position(close, 20, 2.0) * safe_div(ts_std_dev(returns, 20) * safe_div(ts_range(high, 20), ts_range(low, 20)) * volume, ts_mean(volume, 60)) | optimize | 0.740 | 31.0 | 0.0131 | -0.009 | -0.521 | 0.740 |
| s500-c4-r008 | 1 | 区间位置回归：多周区间内的价格位置过高后出现反转 | -1 * ts_zscore(safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120)), 250) | optimize | 0.728 | 25.3 | 0.0083 | 0.236 | 0.668 | 0.728 |
| s500-c1-r001 | 3 | Short-horizon close-strength reversal conditioned on elevated turnover | -ts_bollinger_position(safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)), 20, 2.0) * safe_div(volume, ts_mean(volume, 60)) | abandon | 0.727 | 43.7 | 0.0059 | -0.069 | 0.194 | 0.727 |
| s500-c1-r001 | 5 | Short-horizon close-strength reversal conditioned on elevated turnover | -safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) | abandon | 0.722 | 38.8 | 0.0058 | 0.143 | 0.236 | 0.722 |
| s500-c1-r001 | 4 | Index overextension reverses only in stressed-volatility states | -ts_bollinger_position(close, 20, 2.0) * safe_div(ts_std_dev(returns, 20) * ts_range(high, 20), ts_range(low, 20) * ts_mean(volume, 20)) * volume | optimize | 0.722 | 31.8 | 0.0131 | 0.016 | -0.629 | 0.722 |
| s500-c2-r003 | 2 | Rapid multi-day high-low range expansion precedes index mean reversion | -safe_div(ts_max(high, 10) - ts_min(low, 10), ts_mean(ts_max(high, 10) - ts_min(low, 10), 60)) | optimize | 0.680 | 43.1 | 0.0043 | -0.200 | -0.098 | 0.605 |
| camp-c3-r004 | 1 | Intraday range expansion as a short-horizon risk-premium signal | safe_div(ts_mean(safe_div(high - low, close), 5), ts_mean(safe_div(high - low, close), 60)) * safe_div(ts_min(low, 60), close) | abandon | 0.664 | 51.3 | 0.0055 | 0.405 | -0.562 | 0.664 |
| 20261101-sysv1-campaign | 1 | Intraday range expansion as a short-horizon risk-premium signal | safe_div(ts_mean(safe_div(high - low, close), 5), ts_mean(safe_div(high - low, close), 60)) * safe_div(ts_min(low, 60), close) | abandon | 0.664 | 51.3 | 0.0055 | 0.405 | -0.562 | 0.664 |
| s500-c1-r001 | 0 | Short-horizon close-strength reversal conditioned on elevated turnover | -safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) * (1.0 + ts_zscore(volume, 60)) | abandon | 0.637 | 116.1 | 0.0027 | 0.114 | 0.050 | 0.637 |
| s500-c4-r008 | 1 | 流动性压力：单位成交额换手偏高（高波动低换手）的股票存在规模内收益溢价 | ts_mean(safe_div(safe_div(high - low, close) + abs(ts_returns(close, 1)), close * volume), 21) | abandon | 0.604 | 2.2 | 0.0008 | -0.098 | -0.641 | 0.483 |
| s500-c4-r008 | 2 | 流动性压力：单位成交额换手偏高（高波动低换手）的股票存在规模内收益溢价 | ts_median(safe_div(abs(safe_div(high - low, close)), close * volume), 21) | abandon | 0.586 | 2.5 | 0.0007 | -0.125 | -0.739 | 0.459 |
| s500-c4-r006 | 1 | 日内价格区间占比回落：收盘价在近期高低区间中的相对位置越低，随后收益越弱（弱式趋势确认不足） | safe_div(ts_median(close - ts_min(low, 20), 5), ts_median(ts_max(high, 20) - ts_min(low, 20), 5)) | abandon | 0.585 | 32.6 | 0.0037 | 0.231 | -0.227 | -0.182 |
| s500-c1-r009 | 0 | 行业/成分内日内价格区间压缩与后续短期收益 | -(safe_div((high - low), close)) / ts_mean(safe_div((high - low), close), 60) | optimize | 0.577 | 159.5 | 0.0041 | -0.051 | -0.253 | 0.577 |
| 20261101-sysv1-campaign | 1 | 日内高低区间压缩：区间收窄后的低波动延续与区间未收窄的相对落后 | -safe_div(safe_div(high, low), ts_min(safe_div(high, low), 63)) | optimize | 0.573 | 142.2 | 0.0099 | -0.013 | -0.982 | 0.573 |
| camp-c1-r002 | 1 | 日内高低区间压缩：区间收窄后的低波动延续与区间未收窄的相对落后 | -safe_div(safe_div(high, low), ts_min(safe_div(high, low), 63)) | optimize | 0.573 | 142.2 | 0.0099 | -0.013 | -0.982 | 0.573 |
| sysv1-h6 | 0 | 区间位置反转：位于 120 日高低区间上沿的股票短期回吐 | -1 * safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120)) | abandon | 0.572 | 21.2 | -0.0008 | 0.191 | 0.316 | 0.526 |
| 20261031-systemv1_50 | 0 | 区间位置反转：位于 120 日高低区间上沿的股票短期回吐 | -1 * safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120)) | abandon | 0.572 | 21.2 | -0.0008 | 0.191 | 0.316 | 0.526 |
| s500-c4-r008 | 0 | 区间位置回归：多周区间内的价格位置过高后出现反转 | -1 * safe_div(close - ts_min(low, 120), ts_max(high, 120) - ts_min(low, 120)) | abandon | 0.572 | 21.2 | -0.0008 | 0.191 | 0.316 | 0.526 |
| s500-c5-r001 | 0 | Intrabar volume absorption: a high share of daily volume arriving on wide-range days predicts lower forward return | safe_div(ts_sum((volume / ts_mean(volume, 60)) * ((high - low) / close), 30), ts_sum(abs(ts_returns(close, 1)), 30)) | abandon | 0.566 | 18.1 | 0.0009 | -0.550 | -1.291 | 0.357 |
| 20261101-sysv1-campaign | 0 | Range-position regime: closes near the top of a long range signal exhaustion, not strength | -1 * safe_div(close - ts_min(low, 126), ts_max(high, 126) - ts_min(low, 126)) | abandon | 0.563 | 20.7 | -0.0012 | 0.153 | 0.281 | 0.520 |
| camp-c2-r006 | 0 | Range-position regime: closes near the top of a long range signal exhaustion, not strength | -1 * safe_div(close - ts_min(low, 126), ts_max(high, 126) - ts_min(low, 126)) | abandon | 0.563 | 20.7 | -0.0012 | 0.153 | 0.281 | 0.520 |
| s500-c1-r005 | 1 | Range-position mean reversion: closes pinned to the top of a 20-day high-low range underperform | -1 * safe_div(ts_mean(close, 5) - ts_min(low, 40), ts_max(high, 40) - ts_min(low, 40)) | optimize | 0.561 | 22.0 | 0.0031 | 0.125 | 0.113 | 0.561 |
| camp-c2-r005 | 0 | Recent range-position extreme as overbought overreaction | -1 * safe_div(low - ts_min(low, 20), ts_range(high, 20) + ts_range(low, 20)) | abandon | 0.555 | 50.9 | 0.0039 | 0.181 | 0.621 | 0.551 |
| 20261101-sysv1-campaign | 0 | Recent range-position extreme as overbought overreaction | -1 * safe_div(low - ts_min(low, 20), ts_range(high, 20) + ts_range(low, 20)) | abandon | 0.555 | 50.9 | 0.0039 | 0.181 | 0.621 | 0.551 |
| s500-c5-r002 | 1 | 横截面成交额加权波动率：高换手波动股的短期收益折价 | -safe_div(ts_ir(ts_returns(close, 1) * (high - low), 63), ts_mean(volume, 21)) | abandon | 0.543 | 20.3 | 0.0027 | 0.309 | 0.110 | 0.512 |
| 20261101-sysv1-campaign | 1 | Recent range-position extreme as overbought overreaction | -1 * safe_div(low - ts_min(low, 20), ts_range(high, 20)) | abandon | 0.542 | 55.6 | 0.0054 | 0.158 | 0.385 | 0.542 |
| camp-c2-r005 | 1 | Recent range-position extreme as overbought overreaction | -1 * safe_div(low - ts_min(low, 20), ts_range(high, 20)) | abandon | 0.542 | 55.6 | 0.0054 | 0.158 | 0.385 | 0.542 |
| s500-c5-r001 | 1 | Volatility trough versus recent churn: a compressed high-low range after active trading predicts continuation in the direction of the pre-compression drift | ts_returns(close, 50) * (1 - safe_div(ts_median(safe_div(high - low, close), 10), ts_median(safe_div(high - low, close), 50))) | abandon | 0.541 | 47.7 | 0.0007 | -0.159 | 0.474 | 0.541 |
| s500-c1-r001 | 2 | Short-horizon close-strength reversal conditioned on elevated turnover | -ts_bollinger_position(safe_div(close - ts_min(low, 60), ts_max(high, 60) - ts_min(low, 60)), 60, 2.0) * safe_div(volume, ts_mean(volume, 60)) | abandon | 0.536 | 29.3 | 0.0085 | -0.178 | -0.325 | 0.536 |
| s500-c5-r002 | 0 | 横截面成交额加权波动率：高换手波动股的短期收益折价 | -ts_std_dev(ts_returns(close, 1) * (high - low) * ts_bollinger_width(volume, 63), 63) | optimize | 0.520 | 4.0 | 0.0099 | 0.935 | -0.502 | 0.520 |
| 20261101-sysv1-campaign | 1 | 振幅挤压：高低价区间相对自身历史收窄后波动扩张带来正收益 | -1 * ts_zscore(safe_div(high - low, close), 120) | abandon | 0.515 | 156.2 | 0.0045 | -0.170 | -0.528 | 0.515 |
| camp-c3-r001 | 1 | 振幅挤压：高低价区间相对自身历史收窄后波动扩张带来正收益 | -1 * ts_zscore(safe_div(high - low, close), 120) | abandon | 0.515 | 156.2 | 0.0045 | -0.170 | -0.528 | 0.515 |
| s500-c1-r009 | 0 | 日内价格区间压缩程度与后续短期收益 | -(ts_zscore(safe_div((high - low), close), 60)) | abandon | 0.514 | 160.3 | 0.0040 | -0.244 | -0.314 | 0.514 |
| s500-c3-r003 | 0 | 日内振幅压缩：低波动收敛区间之后的突破释放 | -1 * ts_zscore(safe_div(high - low, close), 60) | abandon | 0.514 | 160.3 | 0.0040 | -0.244 | -0.314 | 0.514 |
| camp-c2-r003 | 0 | 日内振幅异常尖峰后的短期回补 | 0 - ts_zscore(safe_div(high - low, close), 60) | optimize | 0.514 | 160.3 | 0.0040 | -0.244 | -0.314 | 0.514 |
| 20261101-sysv1-campaign | 0 | 日内振幅异常尖峰后的短期回补 | 0 - ts_zscore(safe_div(high - low, close), 60) | optimize | 0.514 | 160.3 | 0.0040 | -0.244 | -0.314 | 0.514 |
| s500-c1-r009 | 1 | 行业/成分内日内价格区间压缩与后续短期收益 | -((safe_div((high - low), close) - ts_mean(safe_div((high - low), close), 60)) / ts_std_dev(safe_div((high - low), close), 60)) | abandon | 0.514 | 160.3 | 0.0040 | -0.244 | -0.314 | 0.514 |
| s500-c3-r001 | 0 | Intraday range expansion as post-shock volatility drag | -1 * ts_zscore(safe_div(high - low, close), 60) | abandon | 0.514 | 160.3 | 0.0040 | -0.244 | -0.314 | 0.514 |
| s500-c1-r003 | 2 | 指数层价格相对位置的波动率状态：已实现波动低位时的回调风险候选 | -(safe_div(ts_zscore(close, 120), 1) * ts_mean(safe_div(high - low, close), 20)) | abandon | 0.502 | 22.9 | -0.0030 | 0.336 | 0.304 | 0.406 |
| camp-c2-r006 | 1 | Intraday close-location: closes in the top of the daily range predict weaker next-month returns | -1 * ts_mean(safe_div(close - low, high - low), 63) | abandon | 0.494 | 18.1 | -0.0029 | 0.346 | -0.237 | 0.345 |
| 20261101-sysv1-campaign | 1 | Intraday close-location: closes in the top of the daily range predict weaker next-month returns | -1 * ts_mean(safe_div(close - low, high - low), 63) | abandon | 0.494 | 18.1 | -0.0029 | 0.346 | -0.237 | 0.345 |
| s500-c3-r007 | 2 | Daily downside path asymmetry: names whose typical session trades near the low of its intraday range lag next month | -1 * ts_mean(safe_div(close - high, high - low), 63) | optimize | 0.494 | 18.1 | -0.0029 | 0.346 | -0.237 | 0.345 |
| s500-c1-r006 | 0 | 日内区间扩张后的波动率均值回归（大中盘成分股） | safe_div(ts_mean(safe_div(high - low, close), 5), ts_median(safe_div(high - low, close), 60)) | abandon | 0.490 | 31.7 | 0.0006 | -0.756 | 0.168 | -0.188 |
| s500-c2-r004 | 2 | 短期已实现波动幅度的“低波动补偿”：极端日内振幅组合承担更高预期波动 | ts_ir(safe_div(high - low, close), 60) | abandon | 0.490 | 31.7 | 0.0006 | -0.756 | 0.168 | -0.188 |
| s500-c2-r004 | 0 | 短期已实现波动幅度的“低波动补偿”：极端日内振幅组合承担更高预期波动 | ts_mean(safe_div(high - low, close), 60) | abandon | 0.490 | 31.7 | 0.0006 | -0.756 | 0.168 | -0.188 |
_showing top 100 of 295 backtests by IS Sharpe; the full history is in `low.json`_

## Summary

- backtests: 295, median IS Sharpe 0.277, p90 1.297
- best IS Sharpe 2.621: `-(safe_div(close - low, high - low))`
- share of expressions with OOS Sharpe > 0: 54.1% (n=290)

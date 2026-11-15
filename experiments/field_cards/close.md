# Field card: `close`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **yes**

## EDA evidence

| source_field | dataset_id | semantic_role | factor_usage | unit | missing_fraction | blocking_reasons |
|---|---|---|---|---|---|---|
| Adj_Close | ds_86999418bce1 | price | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;price_adjustment_convention_unknown;not_approved_in_reviewed_config;full_selected_dataset_not_successfully_profiled |
| DlyPrc | ds_bd2eab70d3b9 | price | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;price_adjustment_convention_unknown;not_approved_in_reviewed_config |
| DlyClose | ds_bd2eab70d3b9 | price | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;price_adjustment_convention_unknown;not_approved_in_reviewed_config |

## Backtest evidence (979)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| s500-c4-r009 | 1 | 日内收盘位置：收盘价靠近区间低点预示短期反弹 | -(safe_div(close - low, high - low)) | optimize | 2.621 | 94.1 | 0.0253 | 0.365 | 0.259 | 2.621 |
| s500-c2-r002 | 1 | Intraday order imbalance from the closing clip as a short-horizon index pressure signal | -1 * ts_zscore(safe_div(close - low, high - low), 20) | accept | 2.210 | 94.6 | 0.0204 | 0.150 | 0.629 | 2.185 |
| camp-c2-r002 | 0 | Range-position (close location within high-low band) as short-term sentiment proxy | -1 * ts_mean(safe_div(close - low, high - low), 5) | optimize | 2.059 | 78.0 | 0.0193 | 0.127 | 0.054 | 2.059 |
| s500-c4-r009 | 0 | 日内收盘位置：收盘价靠近区间低点预示短期反弹 | -(ts_mean(safe_div(close - low, high - low), 5)) | optimize | 2.059 | 78.0 | 0.0193 | 0.127 | 0.054 | 2.059 |
| 20261101-sysv1-campaign | 0 | Range-position (close location within high-low band) as short-term sentiment proxy | -1 * ts_mean(safe_div(close - low, high - low), 5) | optimize | 2.059 | 78.0 | 0.0193 | 0.127 | 0.054 | 2.059 |
| s500-c6-r003 | 0 | 收盘位于区间上沿的短期反转（日内位置效应） | -ts_mean(safe_div(close - low, high - low), 5) | abandon | 2.059 | 78.0 | 0.0193 | 0.127 | 0.054 | 2.059 |
| s500-c4-r005 | 1 | 日内收益位置：收盘在当日振幅中的相对位置（Close Location Value） | 0 - ts_zscore(ts_mean(safe_div(close - low, high - low), 10), 63) | accept | 2.052 | 56.8 | 0.0190 | -0.070 | -0.491 | 2.052 |
| camp-c3-r004 | 1 | Persistent close-over-open bid as a continuation signal | -1 * ts_mean(safe_div(close, open) * safe_div(close - low, high - low), 5) | abandon | 2.050 | 78.2 | 0.0197 | 0.145 | 0.059 | 2.050 |
| 20261101-sysv1-campaign | 1 | Persistent close-over-open bid as a continuation signal | -1 * ts_mean(safe_div(close, open) * safe_div(close - low, high - low), 5) | abandon | 2.050 | 78.2 | 0.0197 | 0.145 | 0.059 | 2.050 |
| 20261101-sysv1-campaign | 1 | Persistent closing near the daily high indicates crowded pressure and precedes weaker returns | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 10), 60) | accept | 2.004 | 57.0 | 0.0186 | -0.077 | -0.470 | 2.004 |
| camp-c1-r003 | 1 | Persistent closing near the daily high indicates crowded pressure and precedes weaker returns | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 10), 60) | accept | 2.004 | 57.0 | 0.0186 | -0.077 | -0.470 | 2.004 |
| s500-c7-r001 | 1 | Close positioned near the session low signals short-horizon supply pressure | ts_mean(safe_div(close - low, ts_range(high, 21)), 5) - ts_mean(safe_div(close - low, high - low), 5) | optimize | 1.947 | 67.4 | 0.0149 | 0.097 | 0.003 | 1.921 |
| s500-c2-r002 | 0 | Intraday order imbalance from the closing clip as a short-horizon index pressure signal | -1 * ts_zscore(safe_div(close - low, high - low), 10) | accept | 1.898 | 99.4 | 0.0186 | -0.014 | 0.868 | 1.806 |
| s500-c2-r006 | 2 | Stock-specific volatility expansion relative to its own baseline as an uncertainty-discount signal | -(safe_div(ts_mean(ts_max(close, 1) - ts_min(low, 1), 5), ts_mean(ts_max(high, 1) - ts_min(open, 1), 20))) | abandon | 1.801 | 69.7 | 0.0139 | -0.097 | -0.116 | 1.801 |
| s500-c6-r003 | 1 | 收盘位于区间上沿的短期反转（日内位置效应） | -(ts_mean(safe_div(close - low, high - low), 5) - ts_mean(safe_div(close - low, high - low), 20)) | optimize | 1.749 | 83.0 | 0.0161 | 0.089 | 0.564 | 1.749 |
| 20261101-sysv1-campaign | 1 | Closing-location persistence: close near daily high predicts positive forward drift | ts_mean(safe_div(close - low, high - low), 20) - ts_mean(safe_div(close - low, high - low), 5) | optimize | 1.749 | 83.0 | 0.0161 | 0.089 | 0.564 | 1.749 |
| camp-c4-r001 | 1 | Closing-location persistence: close near daily high predicts positive forward drift | ts_mean(safe_div(close - low, high - low), 20) - ts_mean(safe_div(close - low, high - low), 5) | optimize | 1.749 | 83.0 | 0.0161 | 0.089 | 0.564 | 1.749 |
| 20261101-sysv1-campaign | 0 | 日内价格位置低点：收盘价靠近日低点的持续弱势 | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| s500-c2-r002 | 2 | Intraday order imbalance from the closing clip as a short-horizon index pressure signal | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| sysv1-h2 | 0 | 日内收盘位置与短期反转：日收益分布在当日高低区间中的位置对后续1周收益的预测 | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| s500-c4-r010 | 0 | 收盘持续位于日内区间高位的个股短期收益回吐 | -ts_mean(safe_div(close - low, high - low), 10) | accept | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| camp-c3-r002 | 0 | 日内价格位置低点：收盘价靠近日低点的持续弱势 | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| 20261031-systemv1_50 | 0 | 日内收盘位置与短期反转：日收益分布在当日高低区间中的位置对后续1周收益的预测 | -1 * ts_mean(safe_div(close - low, high - low), 10) | optimize | 1.683 | 53.7 | 0.0149 | 0.121 | -0.450 | 1.683 |
| s500-c1-r005 | 1 | Cross-sectional short-term reversal of adjusted close over 1-5 trading days | -1 * safe_div(close - ts_min(close, 3), ts_max(close, 3) - ts_min(close, 3)) | abandon | 1.493 | 81.3 | 0.0166 | 0.667 | 0.459 | 1.493 |
| camp-c3-r002 | 1 | 日内价格位置低点：收盘价靠近日低点的持续弱势 | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 20), 120) | accept | 1.492 | 35.4 | 0.0160 | -0.026 | -0.176 | 1.492 |
| 20261101-sysv1-campaign | 1 | 日内价格位置低点：收盘价靠近日低点的持续弱势 | -1 * ts_zscore(ts_mean(safe_div(close - low, high - low), 20), 120) | accept | 1.492 | 35.4 | 0.0160 | -0.026 | -0.176 | 1.492 |
| camp-c3-r004 | 0 | Repeated close-at-band-floor as a mean-reversion setup | safe_div(ts_mean(safe_div(low, close), 10), ts_mean(safe_div(close, high), 10)) | accept | 1.446 | 49.5 | 0.0179 | 0.144 | -0.516 | 1.446 |
| 20261101-sysv1-campaign | 0 | Repeated close-at-band-floor as a mean-reversion setup | safe_div(ts_mean(safe_div(low, close), 10), ts_mean(safe_div(close, high), 10)) | accept | 1.446 | 49.5 | 0.0179 | 0.144 | -0.516 | 1.446 |
| s500-c3-r007 | 1 | Market-cap repair after a drawdown: names that recovered capitalisation within a noisy window outperform | -1 * safe_div(ts_max_diff(cap, 126), ts_max(cap, 126)) * safe_div(close, ts_max(close, 126)) | accept | 1.443 | 86.5 | 0.0092 | 0.438 | 0.082 | 1.387 |
| s500-c3-r007 | 0 | Market-cap repair after a drawdown: names that recovered capitalisation within a noisy window outperform | -1 * ts_max_diff(cap, 63) * safe_div(close, close) | abandon | 1.421 | 90.6 | 0.0103 | 0.431 | 0.133 | 1.414 |
| s500-c1-r004 | 1 | 量价背离：成交量相对基线抬升而价格盘中收在区间下沿，预示走弱 | -1 * ts_mean(safe_div(volume, ts_mean(volume, 60)) * (safe_div(close - low, high - low) - 0.5), 10) | optimize | 1.413 | 47.6 | 0.0137 | -0.061 | -0.181 | 1.413 |
| s500-c2-r008 | 2 | Index drawdown from recent high as a mean-reversion timing signal (SPY) | -1 * safe_div(close - ts_max(close, 60), ts_max(close, 60)) | abandon | 1.401 | 92.8 | 0.0118 | 0.530 | 0.124 | 1.401 |
| s500-c2-r005 | 0 | ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | safe_div(volume, ts_mean(volume, 20)) * (0 - ts_zscore(ts_returns(close, 1, 1), 60)) | abandon | 1.390 | 93.1 | 0.0158 | 0.839 | 0.652 | 1.390 |
| s500-c4-r007 | 2 | Short-horizon reversal: recent 5-day return negatively predicts next-week return | -1 * ts_zscore(close, 5) | optimize | 1.385 | 64.3 | 0.0149 | 0.486 | 0.308 | 1.385 |
| s500-c1-r004 | 1 | 近期收益的高波动放大：短窗收益/波动比作为过度反应与反转的代理 | -1 * ts_ir(ts_returns(close, 1), 5) | abandon | 1.365 | 49.7 | 0.0112 | 0.200 | 0.785 | 1.365 |
| s500-c1-r004 | 0 | 近期收益的高波动放大：短窗收益/波动比作为过度反应与反转的代理 | -1 * safe_div(ts_sum(ts_returns(close, 1), 5), ts_std_dev(ts_returns(close, 1), 5)) | abandon | 1.365 | 49.7 | 0.0112 | 0.200 | 0.785 | 1.365 |
| s500-c4-r005 | 0 | 日内收益位置：收盘在当日振幅中的相对位置（Close Location Value） | 0 - ts_mean(safe_div(close - low, high - low), 15) | optimize | 1.359 | 39.4 | 0.0128 | 0.115 | -0.679 | 1.359 |
| s500-c5-r004 | 0 | 短期上涨与价格偏离后的反转 | -1 * ts_zscore(close, 5) | optimize | 1.353 | 60.8 | 0.0151 | 0.304 | 0.619 | 1.353 |
| s500-c2-r008 | 1 | Index drawdown from recent high as a mean-reversion timing signal (SPY) | -1 * safe_div(close - ts_max(close, 126), ts_max(close, 126)) | optimize | 1.327 | 87.0 | 0.0090 | 0.268 | -0.160 | 1.325 |
| s500-c4-r009 | 1 | 市场区间恐慌度：大盘区间位置贴近低位预示短期反弹 | -(safe_div(close - ts_min(low, 10), ts_max(high, 10) - ts_min(low, 10))) | optimize | 1.314 | 39.3 | 0.0129 | 0.090 | 0.455 | 1.314 |
| s500-c3-r008 | 0 | Short-horizon overreaction in illiquid names reverses more strongly | -1 * safe_div(ts_returns(close, 5), ts_mean(safe_div(volume, cap), 20)) | optimize | 1.300 | 47.0 | 0.0120 | 0.287 | 0.866 | 1.300 |
| s500-c1-r005 | 2 | Cross-sectional short-term reversal of adjusted close over 1-5 trading days | -1 * ts_returns(close, 3) | optimize | 1.296 | 66.5 | 0.0119 | 0.191 | 0.592 | 1.296 |
| s500-c2-r005 | 1 | ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | 0 - safe_div(ts_mean(volume, 5), ts_mean(volume, 63)) * ts_zscore(ts_returns(close, 1, 1), 20) / ts_std_dev(ts_returns(close, 1, 1), 60) | abandon | 1.293 | 92.3 | 0.0135 | 0.887 | 0.716 | 1.293 |
| s500-c4-r007 | 1 | Short-horizon reversal: recent 5-day return negatively predicts next-week return | -1 * safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 5), 60)) | optimize | 1.285 | 85.1 | 0.0117 | 0.277 | 0.745 | 1.285 |
| s500-c2-r005 | 2 | ETF 高量下跌的抛压吸收：放量下跌后短期反弹 | 0 - safe_div(ts_mean(volume, 5), ts_mean(volume, 60)) * ts_zscore(ts_returns(close, 1, 1), 20) | abandon | 1.284 | 92.4 | 0.0135 | 0.884 | 0.715 | 1.284 |
| s500-c3-r001 | 1 | Short-horizon reversal under abnormal volume | -1 * ts_returns(close, 5) * ts_std_dev(ts_zscore(volume, 60), 5) | optimize | 1.280 | 85.1 | 0.0117 | 0.274 | 0.745 | 1.280 |
| s500-c3-r003 | 2 | 短期价格反转：5日收益的横截面反转为正（价格压力 vs 基本面信息） | -1 * ts_mean(ts_returns(close, 1, 1), 5) | abandon | 1.272 | 52.5 | 0.0113 | 0.085 | 0.801 | 1.272 |
| camp-c3-r002 | 0 | 日收益率偏度的彩票效应 | -1 * ts_mean(close, 5) | abandon | 1.254 | 2.8 | 0.0047 | 0.902 | 0.454 | 1.254 |
| 20261101-sysv1-campaign | 0 | 日收益率偏度的彩票效应 | -1 * ts_mean(close, 5) | abandon | 1.254 | 2.8 | 0.0047 | 0.902 | 0.454 | 1.254 |
| s500-c1-r005 | 0 | Cross-sectional short-term reversal of adjusted close over 1-5 trading days | -1 * ts_returns(close, 5) | optimize | 1.254 | 52.4 | 0.0113 | 0.077 | 0.773 | 1.254 |
| s500-c2-r005 | 2 | ETF 反转：短期急涨后回落（SPY 日频短期反转） | 0 - ts_returns(close, 5, 1) | abandon | 1.254 | 52.4 | 0.0113 | 0.077 | 0.773 | 1.254 |
| s500-c3-r003 | 0 | 短期价格反转：5日收益的横截面反转为正（价格压力 vs 基本面信息） | -1 * ts_returns(close, 5, 1) | optimize | 1.254 | 52.4 | 0.0113 | 0.077 | 0.773 | 1.254 |
| s500-c2-r003 | 2 | Short-horizon return reversal within the mega-cap cross-section | -safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 5), 20)) | optimize | 1.251 | 52.2 | 0.0113 | 0.083 | 0.768 | 1.251 |
| s500-c3-r005 | 2 | Open-to-close intraday return over a week predicts reversal: persistent intraday drift from liquidity demand is corrected over the following month | -1 * safe_div(ts_sum(safe_div(close, open) - 1, 5), ts_std_dev(safe_div(close, open) - 1, 20)) | optimize | 1.250 | 78.8 | 0.0141 | 0.194 | 0.270 | 1.250 |
| s500-c2-r008 | 2 | Cross-sectional abnormal-volume price shock reversal | -1 * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 20)) | optimize | 1.242 | 52.3 | 0.0113 | 0.094 | 0.755 | 1.242 |
| s500-c2-r008 | 1 | Cross-sectional abnormal-volume price shock reversal | -1 * ts_returns(close, 5) * ts_ir(volume, 20) | optimize | 1.242 | 52.3 | 0.0113 | 0.094 | 0.755 | 1.242 |
| s500-c2-r003 | 0 | Short-horizon return reversal within the mega-cap cross-section | -safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 1), 20)) | abandon | 1.241 | 52.3 | 0.0113 | 0.093 | 0.758 | 1.241 |
| s500-c4-r007 | 0 | Short-horizon reversal: recent 5-day return negatively predicts next-week return | -1 * safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 1), 20)) | optimize | 1.241 | 52.3 | 0.0113 | 0.093 | 0.758 | 1.241 |
| s500-c2-r005 | 0 | ETF 反转：短期急涨后回落（SPY 日频短期反转） | 0 - ts_zscore(ts_returns(close, 5, 1), 63) | optimize | 1.237 | 51.5 | 0.0122 | -0.268 | 0.628 | 1.237 |
| s500-c7-r002 | 1 | Attention-Driven Volume Surge with Recent Price Strength as a Short-Horizon Reversal | -1 * safe_div(safe_div(volume, ts_mean(volume, 20)) * safe_div(ts_returns(close, 5), ts_std_dev(ts_returns(close, 5), 20)), ts_std_dev(volume, 20)) | optimize | 1.232 | 85.6 | 0.0114 | 0.278 | 0.720 | 1.232 |
| s500-c1-r001 | 2 | Range asymmetry: close near the session low after a wide range signals unresolved selling pressure | -ts_mean(safe_div(close - low, high - low), 20) * (ts_max(high, 20) - ts_min(low, 20)) | optimize | 1.229 | 11.6 | 0.0116 | 0.606 | -0.541 | 1.012 |
| s500-c2-r003 | 1 | Short-horizon return reversal within the mega-cap cross-section | -ts_zscore(ts_returns(close, 5), 60) | optimize | 1.210 | 51.4 | 0.0120 | -0.245 | 0.677 | 1.210 |
| s500-c4-r003 | 0 | Short-horizon overreaction reversal on elevated-volume extremes | 0 - ts_zscore(ts_returns(close, 5), 60) * ts_mean(safe_div(volume, ts_mean(volume, 20)), 5) | optimize | 1.210 | 51.4 | 0.0120 | -0.245 | 0.677 | 1.210 |
| s500-c1-r001 | 1 | Index overextension reverses only in stressed-volatility states | -ts_bollinger_position(close, 20, 2.0) * ts_std_dev(returns, 20) * ts_range(high, 20) * ts_range(low, 20) * safe_div(volume, ts_mean(volume, 20)) | abandon | 1.204 | 38.4 | 0.0167 | 0.687 | -0.256 | 1.204 |
| s500-c4-r005 | 1 | 指数趋势位置：SPY 价格相对长期均线的相对乖离 | 0 - ts_zscore(safe_div(close - ts_mean(close, 20), ts_mean(close, 20)), 252) | accept | 1.186 | 47.1 | 0.0168 | 0.085 | 0.500 | 1.186 |
| s500-c3-r005 | 0 | Open-to-close intraday return over a week predicts reversal: persistent intraday drift from liquidity demand is corrected over the following month | -1 * ts_sum(safe_div(close, open) - 1, 5) | abandon | 1.181 | 50.5 | 0.0107 | 0.230 | 0.397 | 1.181 |
| s500-c5-r003 | 0 | Short-horizon reversal conditioned on turnover intensity: low-participation losers recover within two weeks | -1 * safe_div(ts_returns(close, 10), safe_div(ts_mean(volume, 10), ts_mean(cap, 10))) | optimize | 1.169 | 50.2 | 0.0102 | 0.425 | 0.157 | 1.083 |
| s500-c2-r005 | 1 | ETF 反转：短期急涨后回落（SPY 日频短期反转） | 0 - ts_zscore(ts_mean(ts_returns(close, 1, 1), 5), 126) | abandon | 1.165 | 51.1 | 0.0124 | -0.071 | 0.815 | 1.165 |
| s500-c2-r007 | 2 | 放量下跌后的短期反应不足：量价确认型反转 | ts_zscore((-1.0) * ts_returns(close, 5) * safe_div(ts_mean(volume, 5), ts_mean(volume, 60)), 120) | optimize | 1.163 | 47.7 | 0.0119 | -0.037 | 0.652 | 1.163 |
| 20261101-sysv1-campaign | 0 | High nominal price predicts lower subsequent returns within the index universe | ts_mean(-close, 20) | accept | 1.161 | 0.8 | 0.0034 | 0.730 | 0.504 | 1.146 |
| camp-c3-r003 | 0 | High nominal price predicts lower subsequent returns within the index universe | ts_mean(-close, 20) | accept | 1.161 | 0.8 | 0.0034 | 0.730 | 0.504 | 1.146 |
| s500-c4-r005 | 0 | 隔夜跳空累积：近一周开盘相对前收盘的累计偏离的反转 | 0 - ts_sum(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5) | optimize | 1.140 | 59.9 | 0.0035 | 0.610 | 0.928 | 1.042 |
| s500-c1-r003 | 1 | 隔夜与日内收益的分离：指数层“隔夜缺口回补”的短期反转候选 | -(ts_mean(open - ts_delta(close, 1), 10) - ts_mean(close - open, 10)) | abandon | 1.139 | 2.2 | 0.0040 | 0.846 | 0.305 | 1.139 |
| 20261101-sysv1-campaign | 1 | Range-position (close location within high-low band) as short-term sentiment proxy | -1 * ts_mean(safe_div(close - low, high - low), 20) | optimize | 1.137 | 33.7 | 0.0104 | 0.081 | -0.390 | 1.137 |
| s500-c1-r001 | 0 | Range asymmetry: close near the session low after a wide range signals unresolved selling pressure | -ts_mean(safe_div(close - low, high - low), 20) | optimize | 1.137 | 33.7 | 0.0104 | 0.081 | -0.390 | 1.137 |
| camp-c2-r002 | 1 | Range-position (close location within high-low band) as short-term sentiment proxy | -1 * ts_mean(safe_div(close - low, high - low), 20) | optimize | 1.137 | 33.7 | 0.0104 | 0.081 | -0.390 | 1.137 |
| camp-c1-r003 | 0 | Persistent closing near the daily high indicates crowded pressure and precedes weaker returns | -1 * ts_mean(safe_div(close - low, high - low), 20) | optimize | 1.137 | 33.7 | 0.0104 | 0.081 | -0.390 | 1.137 |
| s500-c6-r003 | 0 | 短期反转：极端收益后的过度反应修正 | -(ts_sum(ts_returns(close, 1, 0), 5)) * safe_div(ts_mean(volume, 20), cap) | abandon | 1.134 | 85.8 | 0.0114 | 0.191 | 0.675 | 1.134 |
| camp-c2-r007 | 0 | 短期价格超涨的均值回复 | -1 * safe_div(ts_returns(close, 5), ts_mean(ts_std_dev(ts_returns(close, 1), 21), 1)) | optimize | 1.115 | 80.6 | 0.0131 | -0.028 | 0.539 | 1.115 |
| 20261101-sysv1-campaign | 0 | 短期价格超涨的均值回复 | -1 * safe_div(ts_returns(close, 5), ts_mean(ts_std_dev(ts_returns(close, 1), 21), 1)) | optimize | 1.115 | 80.6 | 0.0131 | -0.028 | 0.539 | 1.115 |
| 20261101-sysv1-campaign | 0 | Intraday close-location: closes in the top of the daily range predict weaker next-month returns | ts_mean(-1 * safe_div(close - low, high - low), 21) | optimize | 1.101 | 32.8 | 0.0099 | 0.152 | -0.287 | 1.101 |
| camp-c2-r006 | 0 | Intraday close-location: closes in the top of the daily range predict weaker next-month returns | ts_mean(-1 * safe_div(close - low, high - low), 21) | optimize | 1.101 | 32.8 | 0.0099 | 0.152 | -0.287 | 1.101 |
| s500-c2-r001 | 1 | Range-position asymmetry within a stock's own yearly band predicts weaker forward returns | -1 * safe_div(ts_mean(close - ts_min(low, 252), 21), ts_range(high, 252)) * ts_zscore(high - ts_max(high, 252), 21) | accept | 1.098 | 46.6 | 0.0106 | 0.043 | 0.480 | 0.991 |
| camp-c4-r001 | 0 | Overnight gap information slow-drift over multi-week horizon | safe_div(safe_div(open, close) - 1, ts_std_dev(safe_div(close, open) - 1, 20)) | optimize | 1.093 | 165.6 | 0.0154 | 0.747 | 0.193 | 0.953 |
| 20261101-sysv1-campaign | 0 | Overnight gap information slow-drift over multi-week horizon | safe_div(safe_div(open, close) - 1, ts_std_dev(safe_div(close, open) - 1, 20)) | optimize | 1.093 | 165.6 | 0.0154 | 0.747 | 0.193 | 0.953 |
| s500-c3-r007 | 2 | Market-cap repair after a drawdown: names that recovered capitalisation within a noisy window outperform | (1 - ts_scale(ts_max_diff(cap, 126), 126, 0)) * safe_div(close - ts_min(close, 126), ts_max(close, 126) - ts_min(close, 126)) | optimize | 1.093 | 86.6 | 0.0096 | -0.003 | -0.126 | 1.093 |
| 20261031-systemv1_50 | 0 | 指数 ETF 短期超卖反转：极端收益的均值回归 | -1 * ts_zscore(ts_returns(close, 5), 60) + -1 * safe_div(ts_mean(returns, 5), ts_std_dev(returns, 60)) | optimize | 1.079 | 80.9 | 0.0143 | -0.112 | 0.435 | 1.079 |
| sysv1-h3 | 0 | 指数 ETF 短期超卖反转：极端收益的均值回归 | -1 * ts_zscore(ts_returns(close, 5), 60) + -1 * safe_div(ts_mean(returns, 5), ts_std_dev(returns, 60)) | optimize | 1.079 | 80.9 | 0.0143 | -0.112 | 0.435 | 1.079 |
| s500-c6-r003 | 1 | 短期反转：极端收益后的过度反应修正 | -ts_sum(ts_returns(close, 1, 0), 5) * ts_bollinger_position(safe_div(ts_mean(volume, 20), cap), 60, 2.0) | abandon | 1.075 | 84.4 | 0.0105 | 0.206 | 0.682 | 1.075 |
| s500-c1-r004 | 2 | 近期收益的高波动放大：短窗收益/波动比作为过度反应与反转的代理 | -1 * safe_div(ts_mean(ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 60)) | abandon | 1.073 | 56.4 | 0.0117 | 0.135 | 0.294 | 1.073 |
| 20261101-sysv1-campaign | 1 | 20日横截面短期反转强度（偏离自身均价的幅度） | -1 * ts_zscore(safe_div(close - ts_mean(close, 20), ts_mean(close, 20)), 60) | optimize | 1.057 | 51.1 | 0.0142 | -0.108 | 0.166 | 1.057 |
| camp-c3-r002 | 1 | 20日横截面短期反转强度（偏离自身均价的幅度） | -1 * ts_zscore(safe_div(close - ts_mean(close, 20), ts_mean(close, 20)), 60) | optimize | 1.057 | 51.1 | 0.0142 | -0.108 | 0.166 | 1.057 |
| s500-c1-r010 | 1 | 日内区间位置与成交量共振的短期反弹：放量收在区间下沿的股票未来数周相对收益更高 | -1 * ts_mean(safe_div(close - low, high - low) * safe_div(volume, ts_mean(volume, 21)), 10) | accept | 1.053 | 40.9 | 0.0085 | 0.171 | -0.621 | 1.053 |
| s500-c1-r001 | 1 | Short-horizon close-strength reversal conditioned on elevated turnover | -ts_bollinger_position(safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)), 20, 2.0) + ts_zscore(volume, 60) | optimize | 1.044 | 50.5 | 0.0059 | 0.247 | 1.413 | 0.971 |
| s500-c1-r005 | 0 | Range-position mean reversion: closes pinned to the top of a 20-day high-low range underperform | -1 * safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) | optimize | 1.043 | 58.5 | 0.0136 | 0.171 | 0.269 | 1.043 |
| s500-c3-r004 | 0 | Within-range price position as a short-horizon overreaction signal | -safe_div(close - ts_min(low, 20), ts_max(high, 20) - ts_min(low, 20)) | optimize | 1.043 | 58.5 | 0.0136 | 0.171 | 0.269 | 1.043 |
| s500-c4-r003 | 1 | Short-horizon overreaction reversal on elevated-volume extremes | 0 - ts_zscore(ts_returns(close, 5), 20) * ts_mean(safe_div(volume, ts_mean(volume, 60)), 5) | optimize | 1.029 | 52.2 | 0.0086 | -0.119 | 0.869 | 1.029 |
| camp-c2-r007 | 1 | 短期价格超涨的均值回复 | -1 * ts_zscore(ts_returns(close, 5), 63) | abandon | 1.028 | 80.4 | 0.0142 | -0.147 | 0.380 | 1.028 |
| 20261101-sysv1-campaign | 1 | 短期价格超涨的均值回复 | -1 * ts_zscore(ts_returns(close, 5), 63) | abandon | 1.028 | 80.4 | 0.0142 | -0.147 | 0.380 | 1.028 |
| s500-c7-r003 | 0 | Residual short-term reversal: market-demeaned 1-week losers rebound | -ts_zscore(ts_returns(close, 5), 21) | optimize | 1.025 | 49.2 | 0.0097 | -0.064 | 0.880 | 1.025 |
_showing top 100 of 979 backtests by IS Sharpe; the full history is in `close.json`_

## Summary

- backtests: 979, median IS Sharpe 0.202, p90 1.036
- best IS Sharpe 2.621: `-(safe_div(close - low, high - low))`
- share of expressions with OOS Sharpe > 0: 51.2% (n=953)

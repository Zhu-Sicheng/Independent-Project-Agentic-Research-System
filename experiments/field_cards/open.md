# Field card: `open`

_updated 2026-11-15 23:53:39_

- in current panel vocabulary: **yes**

## EDA evidence

| source_field | dataset_id | semantic_role | factor_usage | unit | missing_fraction | blocking_reasons |
|---|---|---|---|---|---|---|
| Adj_Open | ds_86999418bce1 | price | candidate_requires_confirmation | - | 1.67e-04 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;price_adjustment_convention_unknown;not_approved_in_reviewed_config;full_selected_dataset_not_successfully_profiled |
| DlyOpen | ds_bd2eab70d3b9 | price | candidate_requires_confirmation | - | 0 | point_in_time_not_verified;earliest_availability_unknown;unit_unknown;price_adjustment_convention_unknown;not_approved_in_reviewed_config |

## Backtest evidence (78)

| run_id | round | hypothesis | expression | decision | is_sharpe | is_turnover | is_rank_ic | oos_sharpe | holdout_sharpe | subuniverse_sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| camp-c3-r004 | 1 | Persistent close-over-open bid as a continuation signal | -1 * ts_mean(safe_div(close, open) * safe_div(close - low, high - low), 5) | abandon | 2.050 | 78.2 | 0.0197 | 0.145 | 0.059 | 2.050 |
| 20261101-sysv1-campaign | 1 | Persistent close-over-open bid as a continuation signal | -1 * ts_mean(safe_div(close, open) * safe_div(close - low, high - low), 5) | abandon | 2.050 | 78.2 | 0.0197 | 0.145 | 0.059 | 2.050 |
| s500-c2-r006 | 2 | Stock-specific volatility expansion relative to its own baseline as an uncertainty-discount signal | -(safe_div(ts_mean(ts_max(close, 1) - ts_min(low, 1), 5), ts_mean(ts_max(high, 1) - ts_min(open, 1), 20))) | abandon | 1.801 | 69.7 | 0.0139 | -0.097 | -0.116 | 1.801 |
| s500-c3-r005 | 2 | Open-to-close intraday return over a week predicts reversal: persistent intraday drift from liquidity demand is corrected over the following month | -1 * safe_div(ts_sum(safe_div(close, open) - 1, 5), ts_std_dev(safe_div(close, open) - 1, 20)) | optimize | 1.250 | 78.8 | 0.0141 | 0.194 | 0.270 | 1.250 |
| s500-c3-r005 | 0 | Open-to-close intraday return over a week predicts reversal: persistent intraday drift from liquidity demand is corrected over the following month | -1 * ts_sum(safe_div(close, open) - 1, 5) | abandon | 1.181 | 50.5 | 0.0107 | 0.230 | 0.397 | 1.181 |
| s500-c4-r005 | 0 | 隔夜跳空累积：近一周开盘相对前收盘的累计偏离的反转 | 0 - ts_sum(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5) | optimize | 1.140 | 59.9 | 0.0035 | 0.610 | 0.928 | 1.042 |
| s500-c1-r003 | 1 | 隔夜与日内收益的分离：指数层“隔夜缺口回补”的短期反转候选 | -(ts_mean(open - ts_delta(close, 1), 10) - ts_mean(close - open, 10)) | abandon | 1.139 | 2.2 | 0.0040 | 0.846 | 0.305 | 1.139 |
| 20261101-sysv1-campaign | 0 | Overnight gap information slow-drift over multi-week horizon | safe_div(safe_div(open, close) - 1, ts_std_dev(safe_div(close, open) - 1, 20)) | optimize | 1.093 | 165.6 | 0.0154 | 0.747 | 0.193 | 0.953 |
| camp-c4-r001 | 0 | Overnight gap information slow-drift over multi-week horizon | safe_div(safe_div(open, close) - 1, ts_std_dev(safe_div(close, open) - 1, 20)) | optimize | 1.093 | 165.6 | 0.0154 | 0.747 | 0.193 | 0.953 |
| s500-c1-r004 | 1 | 日内与隔夜收益分解：开盘缺口后日内走弱的“日内反转”股票未来继续偏弱 | -1 * ts_sum(safe_div(safe_div(close, open), safe_div(open, ts_delta(close, 1) + close)), 10) | optimize | 1.025 | 56.6 | 0.0144 | 0.293 | -0.141 | 1.025 |
| s500-c1-r003 | 0 | 隔夜与日内收益的分离：指数层“隔夜缺口回补”的短期反转候选 | -(safe_div(ts_mean(open - ts_delta(close, 1), 10), ts_mean(close - open, 10))) | abandon | 0.973 | 57.7 | 0.0070 | 0.353 | -0.254 | 0.957 |
| s500-c2-r006 | 1 | Stock-specific volatility expansion relative to its own baseline as an uncertainty-discount signal | -(safe_div(ts_mean((close + high + low) / open, 5), ts_mean((close + high + low) / open, 20))) | optimize | 0.909 | 47.6 | 0.0086 | 0.062 | 0.467 | 0.909 |
| s500-c3-r005 | 1 | Open-to-close intraday return over a week predicts reversal: persistent intraday drift from liquidity demand is corrected over the following month | -1 * ts_zscore(safe_div(close, open) - 1, 5) | optimize | 0.826 | 107.3 | 0.0088 | 0.714 | 0.679 | 0.669 |
| camp-c3-r004 | 1 | Volume-confirmed 12-1 style momentum in SP500 constituents | safe_div(ts_mean(close, 126), ts_mean(close, 252)) * safe_div(ts_mean(volume, 21), ts_mean(cap, 21)) * safe_div(close, open) | abandon | 0.755 | 3.9 | -0.0022 | -0.059 | 1.340 | 0.727 |
| 20261101-sysv1-campaign | 1 | Volume-confirmed 12-1 style momentum in SP500 constituents | safe_div(ts_mean(close, 126), ts_mean(close, 252)) * safe_div(ts_mean(volume, 21), ts_mean(cap, 21)) * safe_div(close, open) | abandon | 0.755 | 3.9 | -0.0022 | -0.059 | 1.340 | 0.727 |
| camp-c3-r003 | 0 | Persistent positive overnight gaps reverse over the next trading week | 0 - ts_mean(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5) | abandon | 0.745 | 61.9 | 0.0021 | 0.753 | 1.065 | 0.728 |
| sysv1-h2 | 0 | 跳空缺口回补：开盘相对前日收盘的跳空幅度对后续收益的预测 | -1 * ts_mean(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5) | abandon | 0.745 | 61.9 | 0.0021 | 0.753 | 1.065 | 0.728 |
| 20261101-sysv1-campaign | 0 | Persistent positive overnight gaps reverse over the next trading week | 0 - ts_mean(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5) | abandon | 0.745 | 61.9 | 0.0021 | 0.753 | 1.065 | 0.728 |
| 20261031-systemv1_50 | 0 | 跳空缺口回补：开盘相对前日收盘的跳空幅度对后续收益的预测 | -1 * ts_mean(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 5) | abandon | 0.745 | 61.9 | 0.0021 | 0.753 | 1.065 | 0.728 |
| 20261101-sysv1-campaign | 0 | Overnight versus intraday decomposition: names repeatedly gapping down at the open underperform | ts_mean(safe_div(open, close) - 1, 21) | optimize | 0.557 | 34.1 | 0.0098 | 0.300 | 0.330 | 0.557 |
| camp-c1-r004 | 0 | Overnight versus intraday decomposition: names repeatedly gapping down at the open underperform | ts_mean(safe_div(open, close) - 1, 21) | optimize | 0.557 | 34.1 | 0.0098 | 0.300 | 0.330 | 0.557 |
| s500-c4-r005 | 1 | 隔夜跳空累积：近一周开盘相对前收盘的累计偏离的反转 | 0 - ts_sum(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 10) | abandon | 0.518 | 29.1 | 0.0013 | 0.294 | 0.719 | 0.518 |
| s500-c1-r001 | 0 | Overnight versus intraday return decoupling as a sentiment-release signal | -safe_div(ts_mean(ts_delta(open, 1) - open + close, 20), ts_mean(close, 20)) | abandon | 0.514 | 27.2 | 0.0089 | 0.177 | -0.002 | 0.514 |
| camp-c1-r004 | 1 | Overnight versus intraday decomposition: names repeatedly gapping down at the open underperform | ts_mean(safe_div(open, ts_mean(close, 2)), 21) | abandon | 0.481 | 30.3 | 0.0057 | 0.670 | 0.191 | 0.455 |
| 20261101-sysv1-campaign | 1 | Overnight versus intraday decomposition: names repeatedly gapping down at the open underperform | ts_mean(safe_div(open, ts_mean(close, 2)), 21) | abandon | 0.481 | 30.3 | 0.0057 | 0.670 | 0.191 | 0.455 |
| camp-c2-r003 | 1 | 隔夜与日间收益分歧的短期修正 | 0 - ts_mean(safe_div(safe_div(open, cap) - safe_div(ts_delta(close, 1), cap), safe_div(ts_delta(close, 1), cap)), 21) | abandon | 0.435 | 26.5 | 0.0012 | 0.033 | 0.655 | 0.435 |
| 20261101-sysv1-campaign | 1 | 隔夜与日间收益分歧的短期修正 | 0 - ts_mean(safe_div(safe_div(open, cap) - safe_div(ts_delta(close, 1), cap), safe_div(ts_delta(close, 1), cap)), 21) | abandon | 0.435 | 26.5 | 0.0012 | 0.033 | 0.655 | 0.435 |
| s500-c4-r001 | 0 | Overnight-to-intraday price tension: gap that intraday trading fails to confirm | ts_zscore(ts_mean(safe_div(close - open, open - (close - ts_delta(close, 1))), 21), 252) | abandon | 0.329 | 20.4 | 0.0021 | 0.363 | 0.578 | 0.329 |
| s500-c7-r001 | 0 | Overnight gap accumulation versus intraday drift as divergent investor-clienteles | ts_mean(ts_returns(open, 1) - safe_div(close - open, open), 21) | abandon | 0.286 | 79.3 | 0.0047 | 0.772 | 0.259 | 0.118 |
| s500-c4-r001 | 1 | Overnight-to-intraday price tension: gap that intraday trading fails to confirm | ts_zscore(ts_mean(safe_div(close - open, open - (close - ts_delta(close, 1))), 10), 63) | abandon | 0.286 | 37.5 | 0.0005 | -0.291 | 0.085 | 0.198 |
| s500-c1-r001 | 2 | Overnight versus intraday return decoupling as a sentiment-release signal | -safe_div(ts_mean(ts_delta(open, 1) - open, 20), ts_mean(close - open, 20)) | abandon | 0.251 | 76.8 | 0.0018 | 0.077 | -0.541 | 0.251 |
| s500-c1-r003 | 2 | 隔夜与日内收益的分离：指数层“隔夜缺口回补”的短期反转候选 | -ts_zscore(ts_returns(open, 1) - ts_returns(close, 1), 60) | abandon | 0.247 | 188.8 | -0.0012 | -0.353 | 0.198 | 0.247 |
| camp-c3-r003 | 1 | Persistent positive overnight gaps reverse over the next trading week | 0 - ts_mean(ts_returns(safe_div(open, ts_delta(close, 1)), 1), 20) | abandon | 0.231 | 27.1 | 0.0006 | -0.295 | 0.640 | 0.231 |
| 20261101-sysv1-campaign | 1 | Persistent positive overnight gaps reverse over the next trading week | 0 - ts_mean(ts_returns(safe_div(open, ts_delta(close, 1)), 1), 20) | abandon | 0.231 | 27.1 | 0.0006 | -0.295 | 0.640 | 0.231 |
| s500-c7-r003 | 0 | Overnight gap continuation: close-location strength signals informed overnight demand | ts_mean(safe_div(close - low, high - low), 21) + ts_mean(ts_returns(close, 5), 21) * safe_div(open, close) | abandon | 0.218 | 0.0 | 0.0941 | nan | nan | 0.218 |
| s500-c1-r001 | 1 | Overnight versus intraday return decoupling as a sentiment-release signal | -ts_mean(safe_div(ts_delta(open, 1) - open, close - open), 20) | abandon | 0.194 | 19.8 | 0.0010 | -0.782 | 1.109 | 0.194 |
| s500-c6-r002 | 0 | Intraday open-to-close strength with weak overnight gap signals drift | ts_sum(close / open, 20) - ts_sum(open / ts_delta(open, 1), 20) | abandon | 0.182 | 22.8 | 0.0002 | 0.323 | -0.109 | 0.182 |
| s500-c3-r005 | 1 | Overnight-to-intraday decomposition: stocks whose recent gains accrued overnight rather than intraday earn lower subsequent relative returns | -1 * safe_div(ts_sum(ts_returns(open, 1) - ts_returns(close, 1), 20), ts_sum(ts_returns(open, 1) + ts_returns(close, 1), 20)) | abandon | 0.162 | 107.9 | 0.0007 | -0.232 | -0.796 | 0.066 |
| 20261101-sysv1-campaign | 1 | Overnight gap absorption versus intraday body stability | ts_mean(safe_div(abs(ts_returns(close, 1) - ts_returns(open, 1)), ts_returns(high, 1) - ts_returns(low, 1)), 21) | abandon | 0.128 | 21.1 | 0.0006 | -0.351 | 0.277 | 0.089 |
| camp-c4-r002 | 1 | Overnight gap absorption versus intraday body stability | ts_mean(safe_div(abs(ts_returns(close, 1) - ts_returns(open, 1)), ts_returns(high, 1) - ts_returns(low, 1)), 21) | abandon | 0.128 | 21.1 | 0.0006 | -0.351 | 0.277 | 0.089 |
| 20261101-sysv1-campaign | 0 | Overnight gap absorption versus intraday body stability | ts_mean(safe_div(ts_returns(close, 1) - ts_returns(open, 1), ts_returns(high, 1) - ts_returns(low, 1)), 21) | abandon | 0.122 | 22.0 | -0.0012 | -0.154 | -0.884 | 0.122 |
| camp-c4-r002 | 0 | Overnight gap absorption versus intraday body stability | ts_mean(safe_div(ts_returns(close, 1) - ts_returns(open, 1), ts_returns(high, 1) - ts_returns(low, 1)), 21) | abandon | 0.122 | 22.0 | -0.0012 | -0.154 | -0.884 | 0.122 |
| s500-c2-r001 | 1 | Overnight-versus-intraday return divergence as a slow-diffusion continuation signal among S&P constituents | ts_ir(safe_div(open, ts_delta(close, 1)) - safe_div(close, open), 63) | abandon | 0.105 | 14.6 | 0.0005 | 0.109 | -0.601 | 0.105 |
| s500-c2-r001 | 0 | Overnight-versus-intraday return divergence as a slow-diffusion continuation signal among S&P constituents | ts_sum(safe_div(open, ts_delta(close, 1)) - 1, 63) - ts_sum(safe_div(close, open) - 1, 63) | abandon | 0.105 | 14.6 | 0.0005 | 0.109 | -0.601 | 0.105 |
| s500-c3-r005 | 2 | Overnight-to-intraday decomposition: stocks whose recent gains accrued overnight rather than intraday earn lower subsequent relative returns | -1 * safe_div(ts_sum(ts_returns(open, 1) - ts_returns(close, 1), 60), ts_sum(ts_returns(open, 1) + ts_returns(close, 1), 60)) | abandon | 0.063 | 100.0 | -0.0016 | 0.634 | 0.480 | -0.103 |
| s500-c1-r002 | 1 | 缺口回补：日内收益相对隔夜跳空的强势预示回落 | -1 * (ts_sum(safe_div(close - open, open), 10) - ts_sum(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 10)) | abandon | -0.106 | 30.1 | -0.0001 | -0.265 | -0.336 | -0.194 |
| s500-c1-r002 | 0 | 缺口回补：日内收益相对隔夜跳空的强势预示回落 | -1 * ts_sum(safe_div(close - open, open), 10) + ts_sum(safe_div(open - ts_delta(close, 1), ts_delta(close, 1)), 10) | abandon | -0.106 | 30.1 | -0.0001 | -0.265 | -0.336 | -0.194 |
| sysv1-h7 | 0 | 日内上影线优势：收盘相对高低中点的持续偏离作为短期需求压力信号 | ts_mean(( safe_div(close - safe_div(high + low, 2), high - low) ) * ( safe_div(close - open, abs(close - open)) ), 5) | abandon | -0.174 | 79.3 | -0.0010 | 0.086 | -0.033 | -0.174 |
| 20261031-systemv1_50 | 0 | 日内上影线优势：收盘相对高低中点的持续偏离作为短期需求压力信号 | ts_mean(( safe_div(close - safe_div(high + low, 2), high - low) ) * ( safe_div(close - open, abs(close - open)) ), 5) | abandon | -0.174 | 79.3 | -0.0010 | 0.086 | -0.033 | -0.174 |
| 20261101-sysv1-campaign | 0 | 低开后的日内收回强度（SPY 指数层） | ts_bollinger_position(safe_div(close - open, safe_div(high - low, high)), 20, 2.0) * safe_div(volume, ts_mean(volume, 20)) | abandon | -0.198 | 154.4 | -0.0054 | -0.260 | 0.447 | -0.198 |
| camp-c2-r003 | 0 | 低开后的日内收回强度（SPY 指数层） | ts_bollinger_position(safe_div(close - open, safe_div(high - low, high)), 20, 2.0) * safe_div(volume, ts_mean(volume, 20)) | abandon | -0.198 | 154.4 | -0.0054 | -0.260 | 0.447 | -0.198 |
| s500-c3-r005 | 0 | Overnight-to-intraday decomposition: stocks whose recent gains accrued overnight rather than intraday earn lower subsequent relative returns | -1 * ts_sum(safe_div(open, close) - safe_div(close, open), 20) | abandon | -0.251 | 20.2 | -0.0070 | -0.257 | 0.426 | -0.251 |
| s500-c1-r004 | 2 | 日内与隔夜收益分解：开盘缺口后日内走弱的“日内反转”股票未来继续偏弱 | -1 * safe_div(ts_sum(ts_returns(open, 1) - ts_returns(close, 1), 20), ts_std_dev(ts_returns(close, 1), 20)) | abandon | -0.285 | 157.3 | -0.0086 | -0.035 | -0.553 | -0.285 |
| camp-c4-r001 | 1 | Overnight gap information slow-drift over multi-week horizon | safe_div(ts_delta(open, 1), ts_std_dev(ts_delta(close, 1), 20)) | abandon | -0.335 | 183.3 | -0.0065 | 0.017 | -0.828 | -0.519 |
| 20261101-sysv1-campaign | 1 | Overnight gap information slow-drift over multi-week horizon | safe_div(ts_delta(open, 1), ts_std_dev(ts_delta(close, 1), 20)) | abandon | -0.335 | 183.3 | -0.0065 | 0.017 | -0.828 | -0.519 |
| 20261031-systemv1_50 | 0 | Overnight-versus-intraday return decomposition: persistent overnight drift predicts forward returns | ts_mean(ts_returns(open, 1), 60) - ts_mean(ts_returns(close, 1) - ts_returns(open, 1), 60) | abandon | -0.339 | 47.8 | -0.0005 | -0.405 | 0.247 | -0.339 |
| sysv1-h1 | 0 | Overnight-versus-intraday return decomposition: persistent overnight drift predicts forward returns | ts_mean(ts_returns(open, 1), 60) - ts_mean(ts_returns(close, 1) - ts_returns(open, 1), 60) | abandon | -0.339 | 47.8 | -0.0005 | -0.405 | 0.247 | -0.339 |
| s500-c4-r001 | 2 | Overnight-to-intraday price tension: gap that intraday trading fails to confirm | ts_zscore(ts_mean(safe_div(close - open, open - ts_delta(close, 1)), 21), 63) | abandon | -0.365 | 22.8 | -0.0061 | -0.164 | 0.246 | -0.462 |
| camp-c2-r003 | 0 | 隔夜与日间收益分歧的短期修正 | 0 - ts_mean(safe_div(safe_div(open, cap), safe_div(close, cap)), 21) | abandon | -0.392 | 37.9 | -0.0098 | -0.311 | -0.070 | -0.392 |
| 20261101-sysv1-campaign | 0 | 隔夜与日间收益分歧的短期修正 | 0 - ts_mean(safe_div(safe_div(open, cap), safe_div(close, cap)), 21) | abandon | -0.392 | 37.9 | -0.0098 | -0.311 | -0.070 | -0.392 |
| s500-c1-r004 | 0 | 日内与隔夜收益分解：开盘缺口后日内走弱的“日内反转”股票未来继续偏弱 | -1 * safe_div(ts_sum(ts_returns(open, 1) - ts_returns(close, 1), 10), ts_std_dev(ts_returns(close, 1), 10)) | abandon | -0.462 | 157.7 | -0.0082 | -0.334 | -0.678 | -0.462 |
| camp-c3-r004 | 0 | Volume-confirmed 12-1 style momentum in SP500 constituents | (1 + ts_returns(close, 126)) * safe_div(ts_mean(safe_div(volume, cap), 21), ts_mean(safe_div(volume, cap), 252)) * safe_div(close, open) | abandon | -0.518 | 20.3 | -0.0048 | -0.241 | -0.632 | -0.536 |
| 20261101-sysv1-campaign | 0 | Volume-confirmed 12-1 style momentum in SP500 constituents | (1 + ts_returns(close, 126)) * safe_div(ts_mean(safe_div(volume, cap), 21), ts_mean(safe_div(volume, cap), 252)) * safe_div(close, open) | abandon | -0.518 | 20.3 | -0.0048 | -0.241 | -0.632 | -0.536 |
| s500-c7-r001 | 1 | Overnight gap accumulation versus intraday drift as divergent investor-clienteles | ts_zscore(ts_sum(safe_div(open - close, close), 21) * -1, 252) | abandon | -0.562 | 40.6 | -0.0080 | -0.404 | -0.478 | -0.562 |
| 20261101-sysv1-campaign | 0 | Persistent intraday (open-to-close) strength proxies for institutional accumulation | safe_div(ts_mean(safe_div(close, open) - 1, 21), ts_std_dev(safe_div(close, open) - 1, 21)) | abandon | -0.631 | 33.6 | -0.0067 | -0.459 | -0.276 | -0.638 |
| camp-c1-r005 | 0 | Persistent intraday (open-to-close) strength proxies for institutional accumulation | safe_div(ts_mean(safe_div(close, open) - 1, 21), ts_std_dev(safe_div(close, open) - 1, 21)) | abandon | -0.631 | 33.6 | -0.0067 | -0.459 | -0.276 | -0.638 |
| s500-c5-r004 | 0 | 日内买入压力的短期延续 | ts_mean(safe_div(close, open) - 1, 5) | abandon | -0.743 | 46.0 | -0.0102 | -0.457 | -0.113 | -0.881 |
| 20261101-sysv1-campaign | 1 | Persistent intraday (open-to-close) strength proxies for institutional accumulation | ts_mean(safe_div(close, open) - 1, 10) | abandon | -0.748 | 54.6 | -0.0105 | -0.486 | 0.261 | -0.894 |
| camp-c1-r005 | 1 | Persistent intraday (open-to-close) strength proxies for institutional accumulation | ts_mean(safe_div(close, open) - 1, 10) | abandon | -0.748 | 54.6 | -0.0105 | -0.486 | 0.261 | -0.894 |
| 20261101-sysv1-campaign | 0 | Persistent close-over-open bid as a continuation signal | ts_mean(safe_div(close, open), 5) * safe_div(high, high) * safe_div(low, low) | abandon | -0.803 | 78.7 | -0.0131 | -0.662 | -0.517 | -0.944 |
| camp-c3-r004 | 0 | Persistent close-over-open bid as a continuation signal | ts_mean(safe_div(close, open), 5) * safe_div(high, high) * safe_div(low, low) | abandon | -0.803 | 78.7 | -0.0131 | -0.662 | -0.517 | -0.944 |
| 20261101-sysv1-campaign | 1 | 低开后的日内收回强度（SPY 指数层） | safe_div(safe_div(close - open, high - low), safe_div(volume, ts_mean(volume, 20))) | abandon | -0.971 | 174.7 | -0.0150 | -0.598 | -0.172 | -0.971 |
| camp-c2-r003 | 1 | 低开后的日内收回强度（SPY 指数层） | safe_div(safe_div(close - open, high - low), safe_div(volume, ts_mean(volume, 20))) | abandon | -0.971 | 174.7 | -0.0150 | -0.598 | -0.172 | -0.971 |
| s500-c4-r005 | 2 | 隔夜跳空累积：近一周开盘相对前收盘的累计偏离的反转 | 0 - ts_zscore(ts_sum(safe_div(open - close, close), 5), 63) | abandon | -1.004 | 45.8 | -0.0101 | -0.115 | -0.283 | -1.192 |
| 20261101-sysv1-campaign | 0 | Volume absorbed without intraday price movement as an absorbed-flow / fading-pressure state | -ts_mean(safe_div(abs(safe_div(close - open, open)), safe_div(volume, ShrOut)), 20) | - | nan | nan | nan | nan | nan | nan |
| 20261101-sysv1-campaign | 1 | Volume absorbed without intraday price movement as an absorbed-flow / fading-pressure state | safe_div(ts_mean(safe_div(safe_div(volume, ShrOut), ts_mean(safe_div(volume, ShrOut), 60)), 20), ts_mean(abs(safe_div(close, open)), 20)) | - | nan | nan | nan | nan | nan | nan |
| camp-c1-r001 | 0 | Volume absorbed without intraday price movement as an absorbed-flow / fading-pressure state | -ts_mean(safe_div(abs(safe_div(close - open, open)), safe_div(volume, ShrOut)), 20) | - | nan | nan | nan | nan | nan | nan |
| camp-c1-r001 | 1 | Volume absorbed without intraday price movement as an absorbed-flow / fading-pressure state | safe_div(ts_mean(safe_div(safe_div(volume, ShrOut), ts_mean(safe_div(volume, ShrOut), 60)), 20), ts_mean(abs(safe_div(close, open)), 20)) | - | nan | nan | nan | nan | nan | nan |

## Summary

- backtests: 78, median IS Sharpe 0.172, p90 1.093
- best IS Sharpe 2.050: `-1 * ts_mean(safe_div(close, open) * safe_div(close - low, high - low), 5)`
- share of expressions with OOS Sharpe > 0: 47.9% (n=73)

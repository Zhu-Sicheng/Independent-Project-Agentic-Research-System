<!-- Reference implementation supplied by XY-creator (2026-10). The approved
     time-series operators in factorlab/expr/ops.py follow these definitions for
     the overlapping set; operators we added ourselves keep our own semantics. -->

# 时序运算符

## 运算符列表

```text
ts_arg_max
ts_arg_min
ts_av_diff
ts_bollinger_percent
ts_bollinger_position
ts_bollinger_width
ts_count_nans
ts_decay_linear
ts_delta
ts_ema
ts_entropy
ts_extreme_ratio
ts_gain_loss_ratio
ts_hhi
ts_ir
ts_mad
ts_max
ts_max_diff
ts_max_drawdown
ts_mean
ts_median
ts_min
ts_min_diff
ts_min_max_diff
ts_percentage
ts_positive_ratio
ts_product
ts_quantile
ts_range
ts_rank
ts_returns
ts_scale
ts_std_dev
ts_sum
ts_zscore
```

## 函数定义

### `ts_arg_max`

```python
def ts_arg_max(x, d):
    result = pd.DataFrame(index=x.index, columns=x.columns, dtype=float)
    for col in tqdm(x.columns, desc=f"ts_arg_max(window={d})", leave=False):
        result[col] = _rolling_argmax_numba(x[col].values.astype(np.float64), d)
    return result
```

### `ts_arg_min`

```python
def ts_arg_min(x, d):
    result = pd.DataFrame(index=x.index, columns=x.columns, dtype=float)
    for col in tqdm(x.columns, desc=f"ts_arg_min(window={d})", leave=False):
        result[col] = _rolling_argmin_numba(x[col].values.astype(np.float64), d)
    return result
```

### `ts_av_diff`

```python
def ts_av_diff(x, d):
    return x - ts_mean(x, d)
```

### `ts_bollinger_percent`

```python
def ts_bollinger_percent(x, d, k=2.0):
    ma = ts_mean(x, d)
    std = ts_std_dev(x, d)
    upper = ma + float(k) * std
    lower = ma - float(k) * std
    diff = upper - lower
    return (x - lower) / diff
```

### `ts_bollinger_position`

```python
def ts_bollinger_position(x, d, k=2.0):
    ma = ts_mean(x, d)
    std = ts_std_dev(x, d)
    upper = ma + float(k) * std
    lower = ma - float(k) * std
    diff = upper - lower
    result = (x - lower) / diff
    result = result.clip(0, 1)
    return result
```

### `ts_bollinger_width`

```python
def ts_bollinger_width(x, d, k=2.0):
    ma = ts_mean(x, d)
    std = ts_std_dev(x, d)
    denom = ma.abs().where(ma.abs() > 1e-12)
    return 2.0 * float(k) * std / denom
```

### `ts_count_nans`

```python
def ts_count_nans(x, d):
    result = pd.DataFrame(index=x.index, columns=x.columns, dtype=float)
    for col in tqdm(x.columns, desc=f"ts_count_nans(window={d})", leave=False):
        result[col] = x[col].isna().rolling(window=d, min_periods=1).sum()
    return result
```

### `ts_decay_linear`

```python
def ts_decay_linear(x, d):
    arr = _rolling_decay_linear_2d(x.values.astype(np.float64), int(d))
    return pd.DataFrame(arr, index=x.index, columns=x.columns)
```

### `ts_delta`

```python
def ts_delta(x, d):
    return x - x.shift(d)
```

### `ts_ema`

```python
def ts_ema(x, d):
    return x.ewm(span=int(d), adjust=False, min_periods=max(1, int(d) // 5)).mean()
```

### `ts_entropy`

```python
def ts_entropy(x, d):
    arr = _rolling_entropy_2d(x.values.astype(np.float64), int(d))
    return pd.DataFrame(arr, index=x.index, columns=x.columns)
```

### `ts_extreme_ratio`

```python
def ts_extreme_ratio(x, d):
    denom = ts_min(x, d)
    denom = denom.where(denom.abs() > 1e-12)
    return ts_max(x, d) / denom
```

### `ts_gain_loss_ratio`

```python
def ts_gain_loss_ratio(x, d):
    arr = _rolling_gain_loss_ratio_2d(x.values.astype(np.float64), int(d))
    return pd.DataFrame(arr, index=x.index, columns=x.columns)
```

### `ts_hhi`

```python
def ts_hhi(x, d):
    arr = _rolling_hhi_2d(x.values.astype(np.float64), int(d))
    return pd.DataFrame(arr, index=x.index, columns=x.columns)
```

### `ts_ir`

```python
def ts_ir(x, d):
    mean_val = ts_mean(x, d)
    std_val = ts_std_dev(x, d)
    std_val[std_val < 1e-10] = np.nan
    return mean_val / std_val
```

### `ts_mad`

```python
def ts_mad(x, d):
    arr = _rolling_mad_2d(x.values.astype(np.float64), int(d))
    return pd.DataFrame(arr, index=x.index, columns=x.columns)
```

### `ts_max`

```python
def ts_max(x, d):
    return x.rolling(window=int(d), min_periods=1).max()
```

### `ts_max_diff`

```python
def ts_max_diff(x, d):
    return x - ts_max(x, d)
```

### `ts_max_drawdown`

```python
def ts_max_drawdown(x, d):
    arr = _rolling_max_drawdown_2d(x.values.astype(np.float64), int(d))
    return pd.DataFrame(arr, index=x.index, columns=x.columns)
```

### `ts_mean`

```python
def ts_mean(x, d):
    return x.rolling(window=int(d), min_periods=1).mean()
```

### `ts_median`

```python
def ts_median(x, d):
    return x.rolling(window=int(d), min_periods=1).median()
```

### `ts_min`

```python
def ts_min(x, d):
    return x.rolling(window=int(d), min_periods=1).min()
```

### `ts_min_diff`

```python
def ts_min_diff(x, d):
    return x - ts_min(x, d)
```

### `ts_min_max_diff`

```python
def ts_min_max_diff(x, d, f=0.5):
    return x - f * (ts_min(x, d) + ts_max(x, d))
```

### `ts_percentage`

```python
def ts_percentage(x, d, percentage=0.5):
    return x.rolling(window=int(d), min_periods=1).quantile(float(percentage))
```

### `ts_positive_ratio`

```python
def ts_positive_ratio(x, d):
    arr = _rolling_positive_ratio_2d(x.values.astype(np.float64), int(d))
    return pd.DataFrame(arr, index=x.index, columns=x.columns)
```

### `ts_product`

```python
def ts_product(x, d):
    result = pd.DataFrame(index=x.index, columns=x.columns, dtype=float)
    for col in tqdm(x.columns, desc=f"ts_product(window={d})", leave=False):
        result[col] = _rolling_product_numba(x[col].values.astype(np.float64), d)
    return result
```

### `ts_quantile`

```python
def ts_quantile(x, d, driver="gaussian"):
    rank_vals = ts_rank(x, d, constant=1)
    if driver == "gaussian":
        rank_vals_clipped = rank_vals.clip(1e-10, 0.9999999999)
        result_data = np.where(pd.notna(rank_vals_clipped), stats.norm.ppf(rank_vals_clipped.values), np.nan)
        return pd.DataFrame(result_data, index=rank_vals_clipped.index, columns=rank_vals_clipped.columns)
    if driver == "uniform":
        return rank_vals
    raise ValueError(f"Unknown driver: {driver}")
```

### `ts_range`

```python
def ts_range(x, d):
    return ts_max(x, d) - ts_min(x, d)
```

### `ts_rank`

```python
def ts_rank(x, d, constant=0):
    pct = float(constant) == 1.0
    arr = _rolling_rank_2d(x.values.astype(np.float64), int(d), pct)
    return pd.DataFrame(arr, index=x.index, columns=x.columns)
```

### `ts_returns`

```python
def ts_returns(x, d, mode=1):
    shifted = x.shift(d)
    res = (x - shifted) / shifted
    if mode == 0:
        res = res * 100
    return res
```

### `ts_scale`

```python
def ts_scale(x, d, constant=0):
    rmin = x.rolling(window=int(d), min_periods=1).min()
    rmax = x.rolling(window=int(d), min_periods=1).max()
    diff = rmax - rmin
    result = (x - rmin) / diff + float(constant)
    return result.where(diff > 1e-10)
```

### `ts_std_dev`

```python
def ts_std_dev(x, d):
    return x.rolling(window=int(d), min_periods=2).std(ddof=0)
```

### `ts_sum`

```python
def ts_sum(x, d):
    return x.rolling(window=int(d), min_periods=1).sum()
```

### `ts_zscore`

```python
def ts_zscore(x, d):
    mean = ts_mean(x, d)
    std = ts_std_dev(x, d)
    zero_mask = (std < 1e-14) & std.notna()
    res = (x - mean) / std
    return res.mask(zero_mask, 0.0)
```

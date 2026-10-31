# Approved operators

Agent 2.2 may only write expressions built from the set below. The list is
declared in `factorlab/expr/approved.py`; the validator rejects anything else
and suggests a replacement. The registry in `factorlab/expr/ops.py` stays larger
for scripts, tests and future extensions — being registered is not the same as
being approved.

Source of the time-series list: `ts_operators.md` (2026-10), 35 operators.

## Policy

- **Adding an operator**: implement it in `ops.py` (register with
  `Arg("d", "window")` for economically meaningful lookbacks or
  `Arg("d", "lag")` for pure lags), then append the name to `TS_OPERATORS` in
  `approved.py` and add a row here. `missing_from_registry()` must stay empty.
- **Relaxing the rule for one run**: `FactorSpec.validate(panel, strict_operators=False)`
  or `validate_expression(expr, panel, approved_only=False)`.
- **Window rule**: every `window` argument must be one of `5, 20, 60, 120, 240`.
  Lags (`ts_delta`) accept any integer >= 1 and are not grid-searched.

## Time-series operators

`x`, `y` are `date x ticker` matrices; `d` is the window; `k`, `f`,
`percentage`, `constant`, `mode` are scalars.

| operator | signature | definition |
|---|---|---|
| `ts_arg_max` | `(x, d)` | days since the window maximum, 0 = today |
| `ts_arg_min` | `(x, d)` | days since the window minimum, 0 = today |
| `ts_av_diff` | `(x, d)` | `x - ts_mean(x, d)` |
| `ts_bollinger_percent` | `(x, d, k=2)` | `(x - lower) / (upper - lower)`, bands `mean ± k·std` |
| `ts_bollinger_position` | `(x, d, k=2)` | `ts_bollinger_percent` clipped to `[0, 1]` |
| `ts_bollinger_width` | `(x, d, k=2)` | `2k·std / |mean|` |
| `ts_count_nans` | `(x, d)` | number of NaNs in the window |
| `ts_decay_linear` | `(x, d)` | weighted mean, weights `d, d-1, …, 1` (today heaviest) |
| `ts_delta` | `(x, d)` | `x - delay(x, d)`; `d` is a lag (>= 1) |
| `ts_ema` | `(x, d)` | exponential mean, `span=d`, `adjust=False` |
| `ts_entropy` | `(x, d)` | Shannon entropy of `|x|` shares inside the window |
| `ts_extreme_ratio` | `(x, d)` | `ts_max(x, d) / ts_min(x, d)` |
| `ts_gain_loss_ratio` | `(x, d)` | `Σ positive changes / Σ |negative changes|` |
| `ts_hhi` | `(x, d)` | Herfindahl index `Σ share²` of `|x|` |
| `ts_ir` | `(x, d)` | `mean / std` |
| `ts_mad` | `(x, d)` | mean absolute deviation from the window mean |
| `ts_max` | `(x, d)` | rolling maximum |
| `ts_max_diff` | `(x, d)` | `x - ts_max(x, d)` |
| `ts_max_drawdown` | `(x, d)` | worst drawdown `min(x / running_max - 1)` in the window |
| `ts_mean` | `(x, d)` | rolling mean |
| `ts_median` | `(x, d)` | rolling median |
| `ts_min` | `(x, d)` | rolling minimum |
| `ts_min_diff` | `(x, d)` | `x - ts_min(x, d)` |
| `ts_min_max_diff` | `(x, d, f=0.5)` | `x - f·(ts_min + ts_max)` |
| `ts_percentage` | `(x, d, p=0.5)` | rolling quantile at `p` |
| `ts_positive_ratio` | `(x, d)` | fraction of positive values |
| `ts_product` | `(x, d)` | rolling product |
| `ts_quantile` | `(x, d, driver="gaussian")` | percentile rank mapped through the normal quantile (`uniform` = raw rank) |
| `ts_range` | `(x, d)` | `ts_max - ts_min` |
| `ts_rank` | `(x, d, constant=0)` | integer rank in `1..d`; `constant=1` → percentile rank |
| `ts_returns` | `(x, d, mode=1)` | `(x - delay(x, d)) / delay(x, d)`; `mode=0` → percent |
| `ts_scale` | `(x, d, constant=0)` | `(x - min) / (max - min) + constant` |
| `ts_std_dev` | `(x, d)` | rolling std with `ddof=0` |
| `ts_sum` | `(x, d)` | rolling sum |
| `ts_zscore` | `(x, d)` | `(x - mean) / std`, zero std → 0 |

Reference alignment: the overlapping time-series operators follow the
**vetted implementation** in `factorlab/agents/research/operators.py` (supplied
by XY-creator), not the helper code in the markdown. That registry enables 23 of
the 35 documented operators; our implementations of those 23 match it bit for
bit (values and NaN pattern), and `tests/test_operator_reference.py` pins the
parity. The 12 operators the vetted registry leaves disabled (e.g. `ts_rank`,
`ts_quantile`, `ts_arg_max`) keep our semantics. Non-time-series operators are
ours.

Implementation notes:

- every rolling window requires a **full valid window**
  (`min_periods=d`), deliberately stricter than the partial windows in the
  markdown; warm-up rows stay missing.
- `ts_ema` uses `span=d, adjust=False, min_periods=d` and masks incomplete
  spans; `ts_std_dev` / `ts_zscore` / `ts_ir` need at least two observations.
- division uses the reference `safe_div`: near-zero denominators become NaN
  (`ts_ir` at `1e-10`, `ts_zscore` at `1e-14`, `ts_scale` at `1e-10`,
  `ts_returns` at `1e-12`). `ts_zscore` returns 0 for zero dispersion.
- `ts_rank` without `constant=1` returns a count, not a percentile.
- string literals are supported for mode arguments: `ts_quantile(x, 20, "uniform")`.
- `safe_div(x, y)` is Agent 3's masked division (|y| <= 1e-12 -> NaN); it is
  registered as an approved non-time-series operator so its canonical expressions
  can be re-evaluated by our backtester.
- a machine-readable snapshot is exported by
  `python -m factorlab.expr.catalog --out operators.json` (stable fingerprint).
- `ts_arg_max` / `ts_arg_min` return **days since** the extreme (BRAIN
  convention), not a normalised position.

## Non-time-series operators (always approved)

| category | operators |
|---|---|
| element-wise | `abs`, `sign`, `log`, `log1p`, `sqrt`, `exp`, `signed_power`, `clip`, `nan_to_num`, `max`, `min`, `safe_div` |
| cross-sectional | `rank`, `zscore`, `demean`, `scale`, `winsorize` |
| conditional | `if_else`, `mask` |
| infix | `+ - * / ^`, `> < >= <= == !=`, `& | !` |

## Legacy operators (registered, **not** approved)

`ts_std`, `ts_corr`, `ts_cov`, `ts_skew`, `ts_kurt`, `ts_argmax`, `ts_argmin`,
`delay`, `delta`. They stay callable for scripts and old notebooks but an agent
expression using them fails validation with a replacement hint.

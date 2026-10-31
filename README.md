# factorlab

Agentic factor mining on US equity price/volume panels.

**[English](#english) · [中文](#chinese)**

---

<a id="english"></a>

## English

From several years of daily price/volume data to a curated factor pool:

```
panel
  │
  ▼
Agent 2.1  economist (natural language, no code)
  │
  ▼
Agent 2.2  implementer (expression DSL or per-day python script)
  │
  ▼
backtest + grid search (decay / rank|sign / cap filter / windows)
  │
  ▼
Agent 3  research director (accept / optimize / abandon)
  │
  ▼
factor pool (expression + matrix + performance + correlations)
```

The real dataset is wired in: daily OHLCV and market cap for S&P 500 members,
2000-2026, with point-in-time membership filtering and a three-way sample split
(2000-2020 selection / 2021-2024 validation / 2025+ holdout). Without an LLM key
the pipeline falls back to rule-based agents behind exactly the same interface.

### 1. Quick start

```powershell
# 0) real data: raw CSVs -> cleaned panel (~20 s, writes data/processed/)
python -m factorlab build-data --raw data/raw --out data/processed

# 1) mine on the real panel (uses 2000-2020 IS / 2021-2024 OOS / 2025+ holdout)
python -m factorlab run --data data/processed/panel --hypotheses 3 --rounds 2 --max-evals 120 --offline

# 2) inspect the pool and correlations
python -m factorlab pool

# 3) every attempt (accepted or not) in one table
python -m factorlab ledger --rebuild
```

Outputs:

```
runs/<run_id>/report.md      # hypotheses, attempts, best config, yearly stats, pool
runs/<run_id>/attempts.jsonl # full JSON record of every attempt
runs/<run_id>/equity.png     # cumulative pnl of the accepted factors
pool/                        # factor pool (see section 7)
```

Single-expression backtest:

```powershell
python -m factorlab expr --expression="-rank(ts_mean(returns,5))" --transform none
python -m factorlab expr --expression="ts_std_dev(returns,20)" --grid     # full grid
```

> In PowerShell an expression starting with `-` needs the `--expression="..."` form,
> otherwise it is parsed as a flag.
> Tests: `python -m unittest discover -s tests` (77 cases).

### 2. Layout

```
factorlab/
  config.py            # backtest settings, grid space, LLM config, mining loop
  data/
    panel.py           # PanelStore: date x ticker container + derived fields
    loader.py          # long / wide / per-year files -> PanelStore
    us_equity.py       # real data: per-ticker CSV + membership intervals -> panel
  expr/
    ops.py             # operator registry (implementation + docs)
    approved.py        # the whitelist agents may use (ts_operators.md)
    parser.py          # tokenizer + recursive-descent parser + AST rewriting
    evaluator.py       # AST evaluation on a panel
    validate.py        # static checks: fields, operators, windows, complexity
    script.py          # validation and restricted execution of per-day scripts
    spec.py            # FactorSpec: the expression/script carrier
  backtest/
    engine.py          # factor matrix -> weights -> daily pnl + yearly stats
    metrics.py         # sharpe / turnover / maxdd / IC / xs spearman / pnl pearson
    grid.py            # grid search + window substitution + ranking
    split.py           # is / oos / holdout segments and per-segment metrics
  agents/
    llm.py             # OpenAI-compatible / Anthropic / offline clients
    prompts.py         # system and user prompts for the three agents
    hypothesis.py      # Agent 2.1 economist: data -> hypothesis
    implementer.py     # Agent 2.2 implementer: hypothesis -> expression/script
    critic.py          # Agent 3 research director: accept / optimize / abandon
    fallback.py        # rule-based research library used without an LLM
  pool/
    pool.py            # factor pool storage + correlations
  orchestrator.py      # mining loop, logging, report, equity plot
  cli.py               # command line entry point
docs/
  agent_contracts.md   # JSON contracts between 2.1 / 2.2 / 3
  operators.md         # approved operator signatures and definitions
experiments/
  ledger.csv           # every attempt across runs, with IS/OOS/holdout metrics
  reports/<run_id>.md  # per-run report (hypothesis, decision, yearly tables)
  records/<run_id>/    # archived attempts.jsonl / run.json / hypotheses.json
  batch10/             # ten-attempt audit: summary, plots, daily pnl, yearly tables
```

### 3. Data

#### 3.1 Real data (CRSP-style US equities)

Raw files live in `data/raw/`: 1200 CSVs — one `s<permno>.csv` per security
(`Adj_Open/High/Low/Close/Volume/MktCap`), plus
`MASTER_UNIVERSE_sp500_membership_extended_asOf20260930_v2.csv` (membership
intervals), `permno_to_ticker_mapping.csv`, a GICS security master and SPY bars.

One command turns them into a research panel:

```powershell
python -m factorlab build-data --raw data/raw --out data/processed
```

Output:

```
data/processed/
  panel/
    open.parquet high.parquet low.parquet close.parquet volume.parquet cap.parquet
  meta/
    security_master.csv          # permno / ticker / gvkey / GICS
    universe_intervals.csv       # permno, start_date, end_date (point-in-time)
    manifest.json                # shape, coverage, return distribution, default split
```

Each parquet is a **date x permno** matrix, float32 + zstd. Current scale:
**6726 trading days (2000-01-03 → 2026-09-30) x 1195 permnos**, ~502 members per
day, field coverage 42% (denominator: every stock that ever appears; numerator:
actually a member on that date).

**Cleaning rules** (`factorlab/data/us_equity.py`):

| step | treatment |
|---|---|
| price basis | the vendor's `Adj_*` (split and dividend adjusted), no second adjustment |
| universe | keep a stock only while `start_date <= t <= end_date`; delisted names disappear, **no survivorship bias** |
| invalid values | `close/high/low/open <= 0`, `volume <= 0`, `cap <= 0` → NaN; there are no zero volumes left |
| duplicates | drop duplicate `(permno, date)`, keep the last |
| missing data | **no forward filling**; suspensions and pre-IPO dates stay NaN |
| identifiers | columns are permnos (stable); tickers are reused (43 duplicates), mapping in `meta/security_master.csv` |
| derived fields | `returns`, `log_returns`, `amount = close*volume`, `adv20`, `cap_rank` on demand in `PanelStore` |

Health check (full numbers in `manifest.json`): 498–508 members per day; daily
return mean 0.048%, std 2.4%; 90 observations with `|ret| > 50%` (0.003% of
3.4M), concentrated in the 2008 crisis and a few M&A / squeeze days. They are
kept — truncation is a backtest convention, not something to hide in the data
layer.

#### 3.2 Reading it

```python
from factorlab.data import load_processed

panel = load_processed("data/processed/panel")   # PanelStore
panel.field("close")                             # DataFrame(date x permno)
panel.field("returns")                           # derived
panel.summary()
panel.meta["default_split"]                      # the split convention shipped with the data
```

Available fields (15; agents may use any of them in an expression):

| field | definition | |
|---|---|---|
| `open high low close` | vendor adjusted prices | stored |
| `volume` | shares traded | stored |
| `cap` | market cap, **thousands of USD** (CRSP convention) | stored |
| `returns` | `close_t / close_{t-1} - 1` | derived |
| `log_returns` | `log(close)` diff | derived |
| `amount` | `close * volume` (dollar volume) | derived |
| `adv20` | 20-day average share volume | derived |
| `cap_rank` | cross-sectional rank of `cap` (0-1) | derived |
| `range` | `high - low` | derived |
| `close_position` | `(close - low) / (high - low)` | derived |
| `intraday_return` | `close / open - 1` | derived |
| `overnight_return` | `open / close_{t-1} - 1` | derived |

Derived fields are built on first use and cached; `cap` is rank-invariant so its
unit does not affect the cap filter or `cap_rank`, only dollar-value arithmetic.

Generic formats (long table / wide files / per-year files) still go through
`load_panel()`:

```python
from factorlab.data import load_panel
panel = load_panel("data/other")     # date+ticker long table, or one file per field
```

`y` (the prediction target) defaults to `close_to_close`, i.e.
`close_t / close_{t-1} - 1`; `BacktestSettings(y=...)` accepts any price field
(pct_change is applied).

#### 3.3 Sample split (already configured)

The data carries a `default_split`, which `MiningLoop` picks up automatically:

| segment | range | role |
|---|---|---|
| in-sample `is` | 2000-01-03 → 2020-12-31 (5284 days) | **only** segment used to select configs |
| out-of-sample `oos` | 2021-01-04 → 2024-12-31 (1005 days) | validation, not used for selection |
| holdout | 2025-01-02 → 2026-09-30 (437 days) | final untouched sample |

Override explicitly:
`--train-end 2020-12-31 --oos-start 2021-01-01 --oos-end 2024-12-31 --holdout-start 2025-01-01`.

### 4. The expression language

#### 4.1 Syntax

- arithmetic: `+ - * / ^`, unary `-`, comparisons `> < >= <= == !=`, logic `& | !`
- constants: `nan`, `inf`, `true`, `false`
- function calls: `rank(x)`, `ts_mean(x, 20)`, `if_else(cond, a, b)`

Examples:

```text
-ts_mean(returns, 5)
-rank(ts_std_dev(returns, 20))
ts_returns(close, 20) / ts_std_dev(returns, 60)
if_else(rank(cap) > 0.3, -ts_mean(returns, 20), nan)
-ts_rank(ts_returns(close, 5), 20) * ts_rank(volume / ts_mean(volume, 20), 20)
```

#### 4.2 Approved operators (the only ones Agent 2.2 may use)

The 35 time-series operators follow `ts_operators.md`; implementations of the
23 the collaborator's vetted registry enables match it bit for bit
([`docs/operators.md`](docs/operators.md)):

| family | operators |
|---|---|
| position / extremes | `ts_arg_max ts_arg_min ts_max ts_min ts_max_diff ts_min_diff ts_min_max_diff ts_range ts_extreme_ratio ts_max_drawdown` |
| centre / dispersion | `ts_mean ts_median ts_std_dev ts_mad ts_zscore ts_ir ts_ema` |
| change / return | `ts_delta ts_returns ts_sum ts_product ts_av_diff ts_decay_linear` |
| rank / distribution | `ts_rank ts_percentage ts_quantile ts_scale ts_count_nans ts_positive_ratio ts_entropy ts_hhi` |
| shape | `ts_bollinger_percent ts_bollinger_position ts_bollinger_width ts_gain_loss_ratio` |

Non-time-series operators (all approved):

| family | operators |
|---|---|
| element-wise | `abs sign log log1p sqrt exp signed_power clip nan_to_num max min` |
| cross-sectional | `rank zscore demean scale winsorize` |
| conditional | `if_else mask` |

The validator (`factorlab/expr/validate.py`) rejects anything else and suggests a
replacement, e.g. `ts_std` → `use ts_std_dev`, `delay` → `use ts_delta / ts_returns`.
The whitelist lives in `factorlab/expr/approved.py`; adding an operator is two
steps (register it in `ops.py`, append it to `TS_OPERATORS`). Passing
`strict_operators=False` relaxes the rule for one call.

For the overlapping set the implementations follow the **vetted**
`research/operators.py` registry supplied by the collaborator (full valid
windows, reference `safe_div`, `ts_ir` → NaN and `ts_zscore` → 0 for zero
dispersion; parity is pinned by a differential test). The 12 operators that
registry leaves disabled keep our semantics, as do the non-time-series
operators above. String mode arguments such as `ts_quantile(x, 20, "uniform")`
are supported. A machine-readable catalog with a stable fingerprint is exported
for the agent pipeline:

```powershell
python -m factorlab.expr.catalog --out operators.json [--approved-only]
```

`rank` is cross-sectional per day; `ts_*` roll per stock. Except for `ts_delta`
(a lag, 1 is allowed), window arguments follow 4.3.

#### 4.3 Window rule

Only `5 / 20 / 60 / 120 / 240` days (`config.ALLOWED_WINDOWS`). Any other window
fails validation, and the grid only substitutes within this set. Script factors
get a warning (non-window parameters are allowed in `param_grid`).

#### 4.4 Per-day python scripts

When a factor needs cross-sectional iteration that the expression language cannot
express, Agent 2.2 may submit a script:

```python
def generate(panel, params):
    window = int(params.get("window", 5))
    r = panel.field("returns")
    rel = panel.field("volume") / panel.field("volume").rolling(20).mean()
    num = (r * rel).rolling(window, min_periods=max(2, window // 2)).sum()
    den = rel.rolling(window, min_periods=max(2, window // 2)).sum()
    return -(num / den)
```

Contract:

- must define `generate(panel, params)` (or `generate(panel)`) returning a
  date x ticker DataFrame;
- the namespace holds only `pd`, `np`, `math`, `PARAMS` and a few safe builtins;
  **no imports, file or network access, no dunder access**;
- tunable windows go in `param_grid`, e.g. `{"window": [5, 20, 60]}`, and the grid
  iterates over them;
- the output is aligned to the panel dates/tickers; non-numeric or non-DataFrame
  outputs are rejected.

> This is a guard-rail, not a sandbox: it stops the usual LLM overreach but not a
> determined attacker. Run untrusted code in a container.

### 5. Backtest and grid search

#### 5.1 Conventions

```
raw factor
  → cap filter      if_else(rank(cap) > 0.3, f, nan)     # drop the smallest 30%
  → cross-section   none / rank / sign / zscore
  → time decay      linear, most recent day weighted most
  → demean          w = f - mean(f)                      # dollar neutral
  → normalise       w = w / sum(|w|)                     # 1x gross
  → pnl             pnl_t = Σ w_{t-1,i} · r_{t,i}        # delay=1, no look-ahead
```

- one-way turnover = `0.5 * Σ|w_t - w_{t-1}|`, annualised by 252;
- cost = `cost_bps/1e4 * Σ|Δw|` (0 by default);
- `y` is **close-to-close**: `r_t = close_t / close_{t-1} - 1`;
- metrics: `sharpe ann_return ann_vol total_return max_drawdown turnover hit_rate n_names`,
  plus two information coefficients: `rank_ic` (mean daily cross-sectional
  Spearman, the primary one, also kept as `ic`) with `rank_ic_ir` /
  `rank_ic_positive_ratio`, and `pearson_ic` with `pearson_ic_ir`;
- **per-year** return / sharpe / turnover / maxdd / RankIC;
- **sub-universe reference**: the same factor is re-run on
  `if_else(rank(cap) > 0.3, factor, nan)` (smallest 30% removed) and reported as
  `sub_sharpe / sub_ann_return / sub_turnover / sub_max_drawdown / sub_rank_ic`.
  Acceptance is still driven by the **full-universe** numbers; the sub-universe is
  a liquidity check ("does the edge survive outside micro caps?"). Disable it with
  `--no-subuniverse`, move the cut with `--subuniverse-threshold 0.2`;
- `fitness = sharpe * sqrt(|ann_return| / max(turnover, 0.125))` (BRAIN convention).

#### 5.2 Grid space

| dimension | values |
|---|---|
| decay | `0, 5, 20, 60` (0 = no decay) |
| cross-section | `none, rank, sign` (`zscore` optional) |
| cap filter | `none`, or drop the smallest 30% (`cap_filter=0.3`) |
| expression windows | every window slot re-drawn from `5, 20, 60, 120, 240` |
| script parameters | declared by `param_grid` |

`max_evals=200` by default. When there are too many window combinations the
search first does a "base + single-window coordinate sweep" and then fills the
budget at random; every configuration is a full backtest, ranked by `sharpe`
(ties broken by lower turnover). IC is recomputed only for the top configurations.

#### 5.3 In-sample / out-of-sample / holdout

Three segments, all **inclusive date ranges**:

| segment | key | range | role |
|---|---|---|---|
| in-sample | `is` | 2000-01-03 → 2020-12-31 | **only** segment used for selection |
| out-of-sample | `oos` | 2021-01-04 → 2024-12-31 | validation |
| holdout | `holdout` | 2025-01-02 → 2026-09-30 | final untouched sample |

The dates live in `data/processed/meta/manifest.json::default_split` and are read
by `MiningLoop`; they can also be passed explicitly:

```python
from factorlab.config import SampleSplit

SampleSplit(
    train_end="2020-12-31",
    test_start="2021-01-01", test_end="2024-12-31",
    holdout_start="2025-01-01",
)
# or fractionally: SampleSplit(train_frac=0.8, holdout_start="2025-01-01")
```

```powershell
python -m factorlab run --data data/processed/panel --hypotheses 5 `
  --train-end 2020-12-31 --oos-start 2021-01-01 --oos-end 2024-12-31 --holdout-start 2025-01-01
```

Protocol (`factorlab/backtest/split.py`):

1. the factor matrix is always computed on the **full** panel; factors are causal
   (row t uses data up to t), so neither OOS nor holdout can leak future data;
2. windows / decay / rank / sign / cap filter are scored **in-sample only**;
3. the selected configuration is re-run unchanged on the other two segments, and
   all three sets of metrics are stored and reported;
4. the split is applied to the **pnl series**, not by recomputing a sub-panel, so
   there is no rolling warm-up loss and the first OOS day's turnover reflects the
   real position change;
5. without a split, selection falls back to the full sample and the extra segments
   stay empty — nothing is fabricated.

Where it is stored:

- grid table: `sharpe_is` / `sharpe_oos` / `sharpe_holdout` (plus `ann_return_*`,
  `turnover_*`, `max_drawdown_*`, `ic_*`)
- pool: `segments.is` / `segments.oos` / `segments.holdout` in `meta.json`;
  `pool summary` gains the matching columns
- report: `sharpe IS` / `sharpe OOS` / `sharpe Holdout` columns, per-factor metrics
  for all three segments and per-segment yearly tables

Agent 3 judges on **in-sample** and uses the other two as an overfitting check: if
either segment is negative, or the average gives back more than 60% of the
in-sample edge, the factor is abandoned. The LLM prompt says the same.

### 6. The three agents (2.1 / 2.2 / 3)

| agent | class | input | output |
|---|---|---|---|
| **2.1 economist** | `HypothesisAgent` | data profile (coverage / distribution / autocorrelation), existing pool, previously tried names | hypotheses: mechanism, direction, horizon, falsifiable prediction, natural-language recipe |
| **2.2 implementer** | `ImplementationAgent` | the 2.1 hypothesis + field table + operator catalog + window rule | `FactorSpec`: expression or script + explanation; retried with validator errors |
| **3 research director** | `CriticAgent` | hypothesis + implementation + grid summary + yearly stats + attempt history | `accept / optimize / abandon` + diagnosis + at most one structural change |

**Boundary between 2.1 and 2.2**: 2.1 produces the economic story and the natural
language recipe and **writes no code**; 2.2 owns every implementation decision
(expression vs script, which fields / operators / windows). The split lets either
side be replaced or retried independently: changing the economist does not touch
the execution layer, and changing the execution layer (e.g. a future WorldQuant
BRAIN dialect) does not touch the research logic. The JSON schema is in
`docs/agent_contracts.md`.

Agent 3 may only change the **factor's structure** — decay / rank / sign / cap
filter have already been searched by the grid. `optimize` sends the new spec back
to Agent 2.2 and re-runs, up to `max_rounds` times.

#### 6.1 Connecting an LLM

```powershell
$env:DEEPSEEK_API_KEY="sk-..."                 # or OPENAI_API_KEY / ANTHROPIC_API_KEY
$env:FACTORLAB_LLM_PROVIDER="openai"           # openai | anthropic | offline | auto
$env:FACTORLAB_LLM_BASE_URL="https://api.deepseek.com/v1"
$env:FACTORLAB_LLM_MODEL="deepseek-chat"
python -m factorlab run --hypotheses 5 --rounds 2
```

With `provider=auto` the provider follows the available key; with no key the
rule-based library is used. Interfaces, validation and logging are identical, so
the offline run and the LLM run are the same pipeline.

Keys can also live in a local `.env` (gitignored, see `.env.example`); it is read
automatically and exported variables take precedence:

```
DEEPSEEK_API_KEY=sk-...
FACTORLAB_LLM_PROVIDER=openai
FACTORLAB_LLM_BASE_URL=https://api.deepseek.com/v1
FACTORLAB_LLM_MODEL=deepseek-chat
```

#### 6.2 The offline library

`agents/fallback.py` holds eight hand-written hypotheses (short-term reversal,
low volatility, Amihud illiquidity, volume shock, volume-weighted reversal as a
script, overnight gap, range compression, price/volume divergence) with
implementation templates and review thresholds. It exists so the pipeline can be
tested and demonstrated without a key — not as a stub.

### 7. The factor pool

```
pool/
  index.json                     # every record (spec / hypothesis / metrics / yearly / config / corr)
  correlations.csv               # pairwise correlations
  factors/<name>-<fingerprint>/
      meta.json                  # full record
      factor.parquet             # factor matrix under the best config (float32)
      pnl.parquet                # daily pnl + turnover
      grid.parquet               # grid detail (first 100 rows)
```

Factor id = `name-slug + first 8 hex of the spec sha1`; re-adding the same spec is
idempotent.

**Both correlations are computed and stored, with no threshold**:

- cross-sectional: mean daily Spearman between the two factor matrices
  (`xs_spearman_mean`, plus std and day count);
- time series: Pearson of the two daily pnl series (`pnl_pearson`, on common dates).

Adding a factor compares it with every factor in the pool and writes the result
**both ways** (each side's meta gets `max_abs_xs_corr` / `max_abs_pnl_corr`);
`pool.recompute_correlations()` refreshes everything. Whether to reject on high
correlation is left to a later policy or a human.

```python
from factorlab.pool import FactorPool
pool = FactorPool("pool")
pool.summary()                     # DataFrame: id/name/sharpe/turnover/IC/max_corr...
pool.load_factor(fid)              # factor matrix
pool.load_pnl(fid)                 # daily pnl
pool.correlations()                # pairwise
pool.report()                      # markdown
```

Correlations are computed on whatever is in the pool: two factors give one row,
n factors give n(n-1)/2. High correlation is flagged, not auto-rejected.

### 8. Experiment records

Each run writes `runs/<run_id>/`:

| file | content |
|---|---|
| `attempts.jsonl` | one JSON per attempt, appended as it happens |
| `run.json` | final summary, including all attempts |
| `report.md` | human-readable report |
| `panel_summary.json` | data-profile snapshot at run start |
| `equity.png` | cumulative pnl, only when a factor is accepted |

Every attempt — accepted **or abandoned** — is also flattened into one tracked
table, `experiments/ledger.csv`, with full-sample, in-sample, out-of-sample,
holdout and sub-universe metrics side by side. Real out-of-sample performance is
therefore recorded even for rejected ideas. The ledger is rebuilt after each run
and can be refreshed or queried on demand:

```powershell
python -m factorlab ledger --rebuild
python -m factorlab ledger --sort sharpe_oos --top 20
```

Inspect one experiment (rebuilds the factor from its spec, re-runs the backtest,
and plots equity / drawdown / yearly sharpe / yearly return while printing the segment
tables):

```powershell
python -m factorlab view                 # list the ledger
python -m factorlab view --run 20261031-083828-e2e
python -m factorlab view --run <run_id> --hypothesis <name> --no-plot
```

Alongside the CSV, `--rebuild` copies each run's `report.md` to
`experiments/reports/<run_id>.md`, so the narrative conclusions (hypothesis,
rationale, decision, per-year tables) are versioned and visible on GitHub while
the raw `runs/` directory stays local.

A long batch can be driven by `factorlab.run_batch` (repeated short sessions,
optionally several workers) and summarised with `factorlab.batch_report`, which
reads the archived attempts and writes one table — no replay:

```powershell
python -m factorlab.run_batch --worker a --sessions 5 --hypotheses 5 --max-evals 48
python -m factorlab.batch_report --prefix p100 --out experiments/batch100
```

For batches that must be readable end-to-end, archive the structured artifacts
too:

```powershell
python -m factorlab.archive_runs --runs <run_id> [<run_id> ...] `
  --logs batch.log --batch experiments/batch10
```

This copies `attempts.jsonl` / `run.json` / `report.md` / `panel_summary.json`
into `experiments/records/<run_id>/`, recovers the natural-language hypotheses
(from the report or from the run log) into `hypotheses.json`, and regenerates the
batch `README.md` with the hypothesis text next to every result.

#### Stability checks

The mining loop reports the *best* configuration; a factor that only works for one
decay, one transform or one window is fragile. A dedicated module re-runs the same
signal under every check and plots the resulting pnl against the baseline:

| check | variants |
|---|---|
| universe | `if_else(rank(cap) > 0.3, factor, nan)`; cap filter on / off |
| cross-section | `none` / `rank` / `sign` |
| decay | `0 / 5 / 20 / 60` |
| windows | every literal window in the expression replaced one slot at a time |

```powershell
python -m factorlab.stability --run <run_id> --hypothesis <name>
python -m factorlab.stability --run <run_id> --all
python -m factorlab.stability --index        # rebuild the summary table
```

The mining loop runs the same battery automatically on the best configuration and
hands the compact summary (`subuniverse_sharpe`, the transform / decay / window
Sharpe spans, `min_pnl_corr`, `flags`) to Agent 3, which is instructed never to
accept a factor whose sub-universe flips sign or whose variants decorrelate.
Disable it for a run with `--no-stability`.

Outputs go to `experiments/stability/<run_id>__<factor>/`: `pnl.png` puts the
baseline and every check on a single axes (colour-coded by check group),
plus `metrics.csv`, `meta.json` (expression + baseline config) and `README.md`. They never overwrite the
batch figures or the single-run view.

#### Merged pipeline: collaborator agents + our evaluation

The three research agents (`factorlab/agents/agent1|agent2|agent3` plus the shared
`research` package) can drive a complete run, with everything after the
expression produced by our stack:

```
Agent 1  raw data -> EDA -> data contract
Agent 2  contract -> natural-language hypotheses (ideas.json)
Agent 3  ideas -> constrained expressions + numerical preview (expressions.json)
   |  field translation: Adj_Close -> close, Adj_Volume -> volume, ...
   v
ours: GridSearch (decay / transform / cap filter / windows, IS selection)
      + stability battery (subuniverse / cap / transform / decay / windows)
      + reviewer (accept / optimize / abandon) + factor pool
```

```powershell
python -m factorlab.xy_pipeline --mode offline --max-files 40 --max-evals 16
python -m factorlab.xy_pipeline --mode llm --max-files 40          # AGENTn_* env vars
```

Outputs go to `experiments/xy/<run_id>/` (gitignored): `agent1|2|3/` artifacts,
`stability/<expression_id>/` figures, `evaluations.json`, `run.json`,
`report.md`. The translator also accepts Agent-3 lookbacks outside our grid
horizons (`ts_returns(x, 1)`); the grid still only substitutes the configured
window set.

Notes for this first local run: Agent 1 was given a 40-files-per-dataset budget,
so its contract marks fields as `candidate_requires_confirmation` and Agent 3
returns expressions with status `research_validated_requires_metadata`; the
pipeline evaluates those as research candidates and records the metadata
blockers instead of silently promoting the fields.

### 9. Known limitations / next steps

1. **Only price/volume**: no sector, size neutralisation or fundamentals;
   `group_*` operators and industry neutralisation are the obvious extensions.
2. **Costs**: 0 by default, `cost_bps` can be set; the grid does not run a cost
   sensitivity analysis.
3. **Statistics**: a single OOS split is supported (5.3) but there is no
   walk-forward validation and no multiple-testing correction (Deflated Sharpe /
   White's Reality Check); searching 200 configurations inflates the best Sharpe,
   so a selection-bias penalty is still missing.
4. **Script sandbox**: static checks plus restricted builtins, not isolation — use
   a container for untrusted code.
5. **Concurrency**: the grid is serial; a single factor with 200 backtests takes
   seconds on the real panel, but a larger library wants parallelism and caching.
6. **Agent memory**: only the pool and the hypotheses tried in this run are fed to
   Agent 2.1; failures across runs are not persisted.

---

<a id="chinese"></a>

## 中文

从「若干年的量价数据」出发，自动完成：

```
数据面板
   │
   ▼
Agent 2.1 经济学假设（自然语言，不写代码）
   │
   ▼
Agent 2.2 因子实现（表达式 DSL 或逐日 python 脚本）
   │
   ▼
回测 + 网格搜索（decay / rank|sign / 市值过滤 / 时间窗口）
   │
   ▼
Agent 3 评审：接受 / 优化 / 放弃（结合假设合理性）
   │
   ▼
因子池（表达式 + 矩阵 + 绩效 + 截面/时序相关性）
```

真实数据已经接入：S&P 500 成分股 2000-2026 的日频量价与市值面板，point-in-time 成分过滤，
样本切分为 2000-2020（选择）/ 2021-2024（样本外）/ 2025+（真正样本外）。
没有 LLM key 时会自动退回规则版 agent，流程与接 LLM 后完全一致。

### 1. 快速开始

```powershell
# 0) 真实数据：原始 CSV -> 清洗后的面板（约 20 秒，输出 data/processed/）
python -m factorlab build-data --raw data/raw --out data/processed

# 1) 在真实数据上挖掘（自动使用 2000-2020 样本内 / 2021-2024 样本外 / 2025+ holdout）
python -m factorlab run --data data/processed/panel --hypotheses 3 --rounds 2 --max-evals 120 --offline

# 2) 查看因子池与相关性
python -m factorlab pool

# 3) 所有尝试（无论是否入池）汇总到一张表
python -m factorlab ledger --rebuild
```

产物：

```
runs/<run_id>/report.md      # 假设、每次尝试、网格最优配置、分年绩效、因子池
runs/<run_id>/attempts.jsonl # 每次尝试的完整 JSON 记录
runs/<run_id>/equity.png     # 入池因子的累计净值
pool/                        # 因子池（见第 7 节）
```

单表达式快速回测：

```powershell
python -m factorlab expr --expression="-rank(ts_mean(returns,5))" --transform none
python -m factorlab expr --expression="ts_std_dev(returns,20)" --grid     # 走完整网格
```

> PowerShell 里以 `-` 开头的表达式要用 `--expression="..."` 的等号写法，否则会被当成参数名。
> 测试：`python -m unittest discover -s tests`（77 个用例）。

### 2. 目录结构

```
factorlab/
  config.py            # 全部可调参数：回测设置、网格空间、LLM、挖掘循环
  data/
    panel.py           # PanelStore：date x ticker 矩阵容器 + 派生字段
    loader.py          # 长表 / 宽表 / 按年分文件 的读取，统一成 PanelStore
    us_equity.py       # 真实数据：逐票 CSV + 成分股区间 -> 面板 + 元数据
  expr/
    ops.py             # 算子注册表（实现 + 说明）
    approved.py        # Agent 只能使用的算子白名单（ts_operators.md）
    parser.py          # 表达式 tokenizer + 递归下降解析器 + AST 改写
    evaluator.py       # AST 在面板上求值
    validate.py        # 静态校验：字段、算子、窗口、复杂度
    script.py          # 逐日 python 脚本的校验与受限执行
    spec.py            # FactorSpec：表达式/脚本的统一载体（可哈希、可序列化）
  backtest/
    engine.py          # 因子矩阵 -> 权重 -> 日频 pnl，含分年绩效
    metrics.py         # sharpe / turnover / maxdd / IC / 截面 spearman / 时序 pearson
    grid.py            # 网格搜索 + 窗口替换 + 结果排名
    split.py           # 样本内 / 样本外 / holdout 切分与分段绩效
  agents/
    llm.py             # OpenAI 兼容 / Anthropic / 离线 三种客户端
    prompts.py         # 三个 agent 的 system / user prompt 模板
    hypothesis.py      # Agent 2.1 经济学家：数据 -> 假设
    implementer.py     # Agent 2.2 实现者：假设 -> 表达式/脚本
    critic.py          # Agent 3 研究总监：接受 / 优化 / 放弃
    fallback.py        # 无 LLM 时的规则版研究库
  pool/
    pool.py            # 因子池存储 + 相关性计算
  orchestrator.py      # 挖掘主循环、日志、报告、净值图
  cli.py               # 命令行入口
docs/
  agent_contracts.md   # 2.1 / 2.2 / 3 的 JSON 接口契约
  operators.md         # 白名单算子的签名与定义
experiments/
  ledger.csv           # 跨 run 的全部尝试，含 IS/OOS/holdout 指标
  reports/<run_id>.md  # 每次 run 的报告（假设、决策、分年表）
  records/<run_id>/    # 归档的 attempts.jsonl / run.json / hypotheses.json
  batch10/             # 十次实验审计：汇总、图、日频 pnl、分年表
```

### 3. 数据模块

#### 3.1 真实数据（CRSP 风格美股）

原始数据在 `data/raw/`：1200 个 CSV，逐票 `s<permno>.csv`（`Adj_Open/High/Low/Close/Volume/MktCap`），
外加 `MASTER_UNIVERSE_sp500_membership_extended_asOf20260930_v2.csv`（成分股进出区间）、
`permno_to_ticker_mapping.csv`（permno → ticker）、`security_master...csv`（GICS 行业）和 SPY 行情。

一条命令把原始文件清洗成研究面板：

```powershell
python -m factorlab build-data --raw data/raw --out data/processed
```

输出：

```
data/processed/
  panel/
    open.parquet high.parquet low.parquet close.parquet volume.parquet cap.parquet
  meta/
    security_master.csv          # permno / ticker / gvkey / GICS
    universe_intervals.csv       # permno, start_date, end_date（point-in-time）
    manifest.json                # 规模、覆盖率、收益分布、默认切分
```

每个 parquet 就是一张 **index=日期、columns=permno** 的矩阵，float32 + zstd。
当前规模：**6726 个交易日（2000-01-03 → 2026-09-30）× 1195 只股票**，每日约 502 只在成分内，
字段覆盖率 42%（分母是"全历史出现过的股票"，分子是"当天确实是成分股"）。

**清洗规则**（`factorlab/data/us_equity.py`）：

| 步骤 | 处理 |
|---|---|
| 价格口径 | 直接用数据商的 `Adj_*`（已做拆股与分红调整），不再二次复权 |
| 成分股 | 只在 `start_date <= t <= end_date` 的区间内保留该股票，退市后自然消失，**无幸存者偏差** |
| 非法值 | `close/high/low/open <= 0`、`volume <= 0`、`cap <= 0` 置 NaN；表内已无零成交量 |
| 重复 | 同一 `(permno, date)` 去重保留最后一条 |
| 缺失 | **不做前向填充**；停牌/未上市就是 NaN，由因子和回测按缺失处理 |
| 代码变更 | 列用 permno（稳定），ticker 会复用（43 个重名），映射表放 `meta/security_master.csv` |
| 派生字段 | `returns`、`log_returns`、`amount = close*volume`、`adv20`、`cap_rank` 在 `PanelStore` 中按需生成 |

数据体检（`manifest.json` 里有完整结果）：每日 498–508 只成分股；日收益均值 0.048%、标准差 2.4%；
`|ret| > 50%` 的样本 90 个（占 3.4M 的 0.003%），集中在 2008 年金融危机与个别并购/逼空日，
保留了未删除——是否要截尾应该在回测口径里决定，而不是在数据层偷偷改。

#### 3.2 读取

```python
from factorlab.data import load_processed

panel = load_processed("data/processed/panel")   # PanelStore
panel.field("close")                             # DataFrame(date x permno)
panel.field("returns")                           # 派生
panel.summary()
panel.meta["default_split"]                      # 数据自带的切分约定
```

可用字段（15 个，agent 可以在表达式里直接用）：

| 字段 | 定义 | 来源 |
|---|---|---|
| `open high low close` | 数据商复权价 | 存储 |
| `volume` | 成交量（股） | 存储 |
| `cap` | 市值，**千美元**（CRSP 口径） | 存储 |
| `returns` | `close_t / close_{t-1} - 1` | 派生 |
| `log_returns` | `log(close)` 差分 | 派生 |
| `amount` | `close * volume`（成交额） | 派生 |
| `adv20` | 20 日平均成交量（股） | 派生 |
| `cap_rank` | 市值逐日截面排名（0-1） | 派生 |
| `range` | `high - low` | 派生 |
| `close_position` | `(close - low) / (high - low)` | 派生 |
| `intraday_return` | `close / open - 1` | 派生 |
| `overnight_return` | `open / close_{t-1} - 1` | 派生 |

派生字段首次访问时计算并缓存；`cap` 的单位只影响金额类运算，不影响市值过滤与 `cap_rank`。

通用格式（长表 / 宽表 / 按年分文件）仍然走 `load_panel()`：

```python
from factorlab.data import load_panel
panel = load_panel("data/other")     # date+ticker 长表，或一个字段一个文件
```

`y`（预测目标）默认 `close_to_close`，即 `close_t / close_{t-1} - 1`；
在 `BacktestSettings(y=...)` 里可以换成任意价格字段（会取 pct_change）。

#### 3.3 样本切分（已按约定设好）

数据自带 `default_split`，`MiningLoop` 会自动使用：

| 段 | 区间 | 用途 |
|---|---|---|
| 样本内 `is` | 2000-01-03 → 2020-12-31（5284 天） | **唯一**用于网格搜索选参数 |
| 样本外 `oos` | 2021-01-04 → 2024-12-31（1005 天） | 验证，不参与选择 |
| 真正样本外 `holdout` | 2025-01-02 → 2026-09-30（437 天） | 最后一关，平时不看 |

想显式覆盖：`--train-end 2020-12-31 --oos-start 2021-01-01 --oos-end 2024-12-31 --holdout-start 2025-01-01`。

### 4. 因子表达式语言

#### 4.1 语法

- 算术：`+ - * / ^`，一元 `-`，比较 `> < >= <= == !=`，逻辑 `& | !`（也可写 `&& ||`）
- 常量：`nan`、`inf`、`true`、`false`
- 函数调用：`rank(x)`、`ts_mean(x, 20)`、`if_else(cond, a, b)`

示例：

```text
-ts_mean(returns, 5)
-rank(ts_std_dev(returns, 20))
ts_returns(close, 20) / ts_std_dev(returns, 60)
if_else(rank(cap) > 0.3, -ts_mean(returns, 20), nan)
-ts_rank(ts_returns(close, 5), 20) * ts_rank(volume / ts_mean(volume, 20), 20)
```

#### 4.2 算子白名单（Agent 2.2 只能使用这些）

时序算子以 `ts_operators.md` 为准，共 35 个：

| 类别 | 算子 |
|---|---|
| 位置/极值 | `ts_arg_max ts_arg_min ts_max ts_min ts_max_diff ts_min_diff ts_min_max_diff ts_range ts_extreme_ratio ts_max_drawdown` |
| 中心/离散 | `ts_mean ts_median ts_std_dev ts_mad ts_zscore ts_ir ts_ema` |
| 变化/收益 | `ts_delta ts_returns ts_sum ts_product ts_av_diff ts_decay_linear` |
| 排名/分布 | `ts_rank ts_percentage ts_quantile ts_scale ts_count_nans ts_positive_ratio ts_entropy ts_hhi` |
| 形态 | `ts_bollinger_percent ts_bollinger_position ts_bollinger_width ts_gain_loss_ratio` |

非时序算子沿用原注册表，全部放行：

| 类别 | 算子 |
|---|---|
| element-wise | `abs sign log log1p sqrt exp signed_power clip nan_to_num max min` |
| cross-sectional | `rank zscore demean scale winsorize` |
| conditional | `if_else mask` |

校验器（`factorlab/expr/validate.py`）会拒绝白名单外的算子，并给出替换提示，例如
`ts_std` → `use ts_std_dev`、`delay` → `use ts_delta / ts_returns`。
白名单定义在 `factorlab/expr/approved.py`，新增算子时「在 `ops.py` 注册 + 追加到 `TS_OPERATORS`」两步即可；
确有必要放开限制时传 `strict_operators=False`。

`rank` 是按日截面排名，`ts_*` 是逐股票滚动。除 `ts_delta`（lag，可为 1）外，窗口参数受 4.3 约束。

#### 4.3 时间窗口规则

只允许 `5 / 20 / 60 / 120 / 240` 天（`config.ALLOWED_WINDOWS`）。
表达式中出现其他窗口会在校验阶段直接报错，网格搜索也只会在这几个值里替换。
脚本因子的 `param_grid` 若不是这几个值，会给 warning（允许非窗口参数）。

#### 4.4 逐日 python 脚本因子

当因子需要表达式表达不了的截面迭代逻辑时，Agent 2.2 可以交脚本：

```python
def generate(panel, params):
    window = int(params.get("window", 5))
    r = panel.field("returns")
    rel = panel.field("volume") / panel.field("volume").rolling(20).mean()
    num = (r * rel).rolling(window, min_periods=max(2, window // 2)).sum()
    den = rel.rolling(window, min_periods=max(2, window // 2)).sum()
    return -(num / den)
```

约定：

- 必须定义 `generate(panel, params)`（或 `generate(panel)`），返回 `date x ticker` 的 DataFrame；
- 命名空间里只有 `pd`、`np`、`math`、`PARAMS` 和少量安全 builtin；**禁止 import、文件、网络、dunder 访问**；
- 可调窗口写在 `param_grid`，例如 `{"window": [5, 20, 60]}`，网格会遍历；
- 输出会按面板的日期/股票对齐，非数值列和非 DataFrame 返回值直接报错。

> 这是「护栏」不是「沙箱」：能防住 LLM 的常见越界，但挡不住蓄意攻击。真要跑不可信代码，请把整个进程放进容器。

### 5. 回测与网格搜索

#### 5.1 口径

```
原始因子
  → 市值过滤    if_else(rank(cap) > 0.3, f, nan)     # 丢掉最小 30%
  → 截面变换    none / rank / sign / zscore
  → 时间衰减    linear decay，最近一天权重最大
  → 截面去均值  w = f - mean(f)                     # 美元中性
  → 归一化      w = w / sum(|w|)                    # 1 倍总敞口
  → pnl         pnl_t = Σ w_{t-1,i} · r_{t,i}       # delay=1，无未来函数
```

- turnover（单边）= `0.5 * Σ|w_t - w_{t-1}|`，指标里乘 252 年化；
- 成本 = `cost_bps/1e4 * Σ|Δw|`（默认 0，可设）；
- `y` 固定为 **close-to-close**：`r_t = close_t / close_{t-1} - 1`；
- 指标：`sharpe ann_return ann_vol total_return max_drawdown turnover hit_rate n_names`，
  以及两个信息系数：`rank_ic`（逐日截面 Spearman 均值，主口径，同时保留别名 `ic`）及
  `rank_ic_ir` / `rank_ic_positive_ratio`，`pearson_ic` 及 `pearson_ic_ir`；
- **分年**的 return / sharpe / turnover / maxdd / RankIC；
- **子全集参考回测**：同一因子在 `if_else(rank(cap) > 0.3, factor, nan)`（剔除最小 30%）上
  重跑一遍，报告 `sub_sharpe / sub_ann_return / sub_turnover / sub_max_drawdown / sub_rank_ic`。
  是否接受仍以**全样本**指标为准，子全集只作流动性参考（"alpha 是否只活在小市值里"）。
  `--no-subuniverse` 关闭，`--subuniverse-threshold 0.2` 改切点；
- `fitness = sharpe * sqrt(|ann_return| / max(turnover, 0.125))`（BRAIN 口径，便于横向比较）。

#### 5.2 网格空间

| 维度 | 取值 |
|---|---|
| decay | `0, 5, 20, 60`（0 = 不衰减） |
| 截面变换 | `none, rank, sign`（`zscore` 可选） |
| 市值过滤 | `none`，或丢掉最小 30%（`cap_filter=0.3`） |
| 表达式窗口 | 每个窗口槽位在 `5, 20, 60, 120, 240` 中重取 |
| 脚本参数 | 由 `param_grid` 声明 |

默认 `max_evals=200`：窗口组合过多时先做「基准 + 单窗口坐标扫描」，再随机补足；
每个配置都完整回测，按 `sharpe` 排序（同分看 turnover）。IC 只在排名靠前的配置上重算，用于提速。

#### 5.3 样本内 / 样本外 / 真正样本外

三段切分，全部是**日期闭区间**：

| 段 | 字段 | 区间 | 用途 |
|---|---|---|---|
| 样本内 | `is` | 2000-01-03 → 2020-12-31 | **唯一**参与网格搜索选参数 |
| 样本外 | `oos` | 2021-01-04 → 2024-12-31 | 验证，不参与选择 |
| 真正样本外 | `holdout` | 2025-01-02 → 2026-09-30 | 最后一关 |

这组日期写在 `data/processed/meta/manifest.json::default_split` 里，`MiningLoop` 自动读取；
也可以显式覆盖：

```python
from factorlab.config import SampleSplit

SampleSplit(
    train_end="2020-12-31",
    test_start="2021-01-01", test_end="2024-12-31",
    holdout_start="2025-01-01",
)
# 或按比例：SampleSplit(train_frac=0.8, holdout_start="2025-01-01")
```

```powershell
python -m factorlab run --data data/processed/panel --hypotheses 5 `
  --train-end 2020-12-31 --oos-start 2021-01-01 --oos-end 2024-12-31 --holdout-start 2025-01-01
```

协议（`factorlab/backtest/split.py`）：

1. 因子矩阵始终在**全样本**上计算。因子是因果的（第 t 行只用 ≤t 的数据），
   所以样本外/真正样本外不会因为「因子在这段上算」而偷看未来；
2. 网格搜索的窗口/decay/rank/sign/市值过滤**只在样本内**打分排序；
3. 选出的配置原封不动地在另外两段重跑，三段指标都存、都报；
4. 切的是 **pnl 序列**而不是重算子面板，因此没有 rolling 预热损耗，
   样本外第一天的换手也按真实持仓变化计算；
5. 不切分时退回全样本选择，额外两段为空——不会编造。

落库位置：

- 网格表：`sharpe_is` / `sharpe_oos` / `sharpe_holdout`（以及 `ann_return_*`、`turnover_*`、`max_drawdown_*`、`ic_*`）
- 因子池：`meta.json` 的 `segments.is` / `segments.oos` / `segments.holdout`，`pool summary` 多出对应两列
- 报告：决策表多 `sharpe IS` / `sharpe OOS` / `sharpe Holdout` 三列，每个因子下面三段指标 + 分段分年表

Agent 3 以**样本内**做判断，用另外两段做过拟合检查：两段中任意一段为负、或平均回吐超过样本内优势的 60%，
直接判过拟合并放弃。LLM 的 prompt 同样写明「holdout 是最后一关，样本内好看但样本外塌掉的必须放弃」。

### 6. 三个 Agent（2.1 / 2.2 / 3）

| Agent | 类 | 输入 | 输出 |
|---|---|---|---|
| **2.1 经济学家** | `HypothesisAgent` | 数据画像（字段覆盖率/分布/自相关）、因子池已有因子、已试过并失败的假设 | 若干条假设：机制、方向、horizon、可证伪预测、自然语言因子配方 |
| **2.2 实现者** | `ImplementationAgent` | 2.1 的假设 + 字段表 + 算子说明书 + 窗口规则 | `FactorSpec`：表达式或脚本 + 解释；校验失败会带着错误信息重试 |
| **3 研究总监** | `CriticAgent` | 2.1 的假设 + 2.2 的实现 + 网格汇总 + 分年绩效 + 历史尝试 | `accept / optimize / abandon` + 诊断 + 最多一个结构性修改（改符号、换窗口、平滑） |

**2.1 与 2.2 的边界**：2.1 只产出经济学故事和自然语言配方，**不写任何代码**；
2.2 承担全部实现问题（表达式还是脚本、选哪些字段/算子/窗口）。
这样拆的收益是两者可以独立替换与独立重试：换经济学家不动执行层，
换执行层（比如以后接 WorldQuant BRAIN 的表达式方言）不动研究逻辑。
接口契约（JSON schema）见 `docs/agent_contracts.md`。

Agent 3 的修改只作用于**表达式结构**——decay / rank / sign / 市值过滤已经由网格搜索过了，不重复建议。
`optimize` 会带着新 spec 回到 Agent 2.2 → 重新回测，最多 `max_rounds` 轮。

#### 6.1 接 LLM

```powershell
$env:DEEPSEEK_API_KEY="sk-..."                 # 或 OPENAI_API_KEY / ANTHROPIC_API_KEY
$env:FACTORLAB_LLM_PROVIDER="openai"           # openai | anthropic | offline | auto
$env:FACTORLAB_LLM_BASE_URL="https://api.deepseek.com/v1"
$env:FACTORLAB_LLM_MODEL="deepseek-chat"
python -m factorlab run --hypotheses 5 --rounds 2
```

`provider=auto` 时会按 key 自动选择；没有任何 key 时自动退回离线规则库，
三个 agent 的接口、校验、日志完全一致，所以离线跑出来的流程和接 LLM 后是同一条。

key 也可以放在本地 `.env`（已 gitignore，格式见 `.env.example`），程序会自动读取，
环境变量优先级更高：

```
DEEPSEEK_API_KEY=sk-...
FACTORLAB_LLM_PROVIDER=openai
FACTORLAB_LLM_BASE_URL=https://api.deepseek.com/v1
FACTORLAB_LLM_MODEL=deepseek-chat
```

#### 6.2 离线规则库

`agents/fallback.py` 里是 8 条手写的经济学假设（短期反转、低波动、Amihud 非流动性、成交量冲击、
成交量加权反转（脚本）、隔夜跳空、区间压缩、量价背离），配套实现模板和评审阈值。
它的作用是让整条流水线在没有 key 时可测试、可演示——不是给 LLM 擦屁股的假实现。

### 7. 因子池

```
pool/
  index.json                     # 所有因子记录（spec / 假设 / 绩效 / 分年 / 配置 / 相关性）
  correlations.csv               # 两两相关性长表
  factors/<name>-<fingerprint>/
      meta.json                  # 单因子完整记录
      factor.parquet             # 最优配置下的原始因子矩阵（float32）
      pnl.parquet                # 日 pnl + turnover
      grid.parquet               # 网格搜索明细（前 100 行）
```

因子 id = `名字-slug + spec 内容 sha1 前 8 位`，同一份 spec 重复入库是幂等的。

**两种相关性都会算、都会存，但不设阈值**：

- 截面：两个因子矩阵逐日截面 Spearman 的均值（`xs_spearman_mean`，另有 std / 天数）；
- 时序：两条日 pnl 的 Pearson（`pnl_pearson`，按共同交易日）。

新增因子时会和池内每个因子算一遍并**双向**写回（两侧 meta 都更新 `max_abs_xs_corr` / `max_abs_pnl_corr`），
同时 `pool.recompute_correlations()` 可全量重算。是否因为相关性高而拒绝，留给后续策略/人来定。

```python
from factorlab.pool import FactorPool
pool = FactorPool("pool")
pool.summary()                     # DataFrame：id/name/sharpe/turnover/IC/max_corr...
pool.load_factor(fid)              # 因子矩阵
pool.load_pnl(fid)                 # 日 pnl
pool.correlations()                # 两两相关性
pool.report()                      # markdown
```

相关性对池内任意两个因子都计算：两个因子一行，n 个因子 n(n-1)/2 行。相关性高只标记、不自动拒绝。

### 8. 实验记录

每次 run 写入 `runs/<run_id>/`：

| 文件 | 内容 |
|---|---|
| `attempts.jsonl` | 每次尝试一条 JSON，逐条追加 |
| `run.json` | 最终汇总（含全部 attempts） |
| `report.md` | 人类可读报告 |
| `panel_summary.json` | run 开始时的数据画像快照 |
| `equity.png` | 入池因子的累计净值（仅当有因子被接受） |

所有尝试——**无论接受还是放弃**——还会被拍平成一张受版本管理的表
`experiments/ledger.csv`，把全样本、样本内、样本外、holdout、子全集的指标并排放：
即使因子被否，真实的样本外表现也留档。每次 run 结束自动重建，也可手动刷新/查询：

```powershell
python -m factorlab ledger --rebuild
python -m factorlab ledger --sort sharpe_oos --top 20
```

查看单个实验（按 spec 重建因子并重跑回测，画出净值 / 回撤 / 分年 Sharpe / 分年收益四联图，同时打印分段与分年统计表）：

```powershell
python -m factorlab view                 # 列出 ledger
python -m factorlab view --run 20261031-083828-e2e
python -m factorlab view --run <run_id> --hypothesis <name> --no-plot
```

`--rebuild` 同时把每次 run 的 `report.md` 复制到 `experiments/reports/<run_id>.md`，
于是「假设—理由—决策—分年表」这些文字结论也进 git、在 GitHub 上可见，而原始 `runs/` 仍留在本地。

长批次可以用 `factorlab.run_batch` 驱动（重复多个短 session，可多进程并行），
再用 `factorlab.batch_report` 从归档的 attempts 直接汇总成一张表（不重跑回测）：

```powershell
python -m factorlab.run_batch --worker a --sessions 5 --hypotheses 5 --max-evals 48
python -m factorlab.batch_report --prefix p100 --out experiments/batch100
```

需要完整留档一个批次时，用归档命令：

```powershell
python -m factorlab.archive_runs --runs <run_id> [<run_id> ...] `
  --logs batch.log --batch experiments/batch10
```

它把 `attempts.jsonl` / `run.json` / `report.md` / `panel_summary.json` 复制到
`experiments/records/<run_id>/`，从报告或日志里恢复自然语言假设写入 `hypotheses.json`，
并重新生成批次 `README.md`（每条结果旁边附假设原文）。

#### 稳定性检验

网格搜索只报告**最优配置**，但只在某个 decay / 某个截面变换 / 某个窗口下有效的因子是脆弱的。
独立模块把同一信号在每个检验下重跑一遍，与原配置的 pnl 画在一起：

| 检验 | 变体 |
|---|---|
| 股票池 | `if_else(rank(cap) > 0.3, factor, nan)`；市值过滤开 / 关 |
| 截面变换 | `none` / `rank` / `sign` |
| 时间衰减 | `0 / 5 / 20 / 60` |
| 时间窗口 | 表达式里每个窗口槽位逐一替换 |

```powershell
python -m factorlab.stability --run <run_id> --hypothesis <name>
python -m factorlab.stability --run <run_id> --all
python -m factorlab.stability --index        # 重建汇总表
```

挖掘循环会对最优配置自动跑同一套检验，把精简结果（`subuniverse_sharpe`、transform / decay /
window 的 Sharpe 区间、`min_pnl_corr`、`flags`）交给 Agent 3；评审规则明确：子全集翻转符号、
或变体 PnL 失去相关性的因子不得 accept。单次运行可用 `--no-stability` 关闭。

结果写到 `experiments/stability/<run_id>__<factor>/`（`pnl.png` 把原配置与所有检验曲线画在
同一张图上、按检验组用颜色区分，另有 `metrics.csv`、`meta.json`（表达式与基线配置）、
`README.md`），**不覆盖**批次图与单次 run 的图。

#### 合并流水线：对方的三段 agent + 我们的评估

三个研究 agent（`factorlab/agents/agent1|agent2|agent3` 与共享的 `research` 包）负责
数据理解 → 自然语言假设 → 约束表达式，表达式之后全部走我们的栈：

```
Agent 1 原始数据 -> EDA -> 数据契约
Agent 2 契约 -> 假设（ideas.json）
Agent 3 假设 -> 表达式 + 数值预览（expressions.json）
   |  字段翻译：Adj_Close -> close、Adj_Volume -> volume ...
   v
我们的：GridSearch（decay / transform / cap / 窗口，IS 选优）
       + 稳定性检验（子全集 / cap / transform / decay / 窗口）
       + 评审（accept / optimize / abandon）+ 因子池
```

```powershell
python -m factorlab.xy_pipeline --mode offline --max-files 40 --max-evals 16
python -m factorlab.xy_pipeline --mode llm --max-files 40          # 需要 AGENTn_* 环境变量
```

结果写到 `experiments/xy/<run_id>/`（已 gitignore）：`agent1|2|3/` 产物、
`stability/<expression_id>/` 图、`evaluations.json`、`run.json`、`report.md`。
翻译层接受对方的任意 lookback（如 `ts_returns(x, 1)`），网格仍只替换我们配置的窗口集。

首次本地说明：Agent 1 只给了每数据集 40 个文件的预算，因此字段契约标记为
`candidate_requires_confirmation`、Agent 3 输出状态为
`research_validated_requires_metadata`；流水线把这些当作研究候选继续评估，并记录
字段阻塞原因，不会静默提升为正式数据。

### 9. 已知限制 / 下一步

1. **只有量价**：没有行业、市值中性化、财务因子；`group_*` 类算子和行业中性化是明确的扩展点。
2. **成本**：默认 0，`cost_bps` 可开；网格目前不对成本做敏感性分析。
3. **统计**：单次样本外切分已支持（见 5.3），但还没有 walk-forward 滚动验证，
   也没有多重检验校正（Deflated Sharpe / White's Reality Check）；
   网格 200 次搜索本身就会抬高最优 Sharpe，后续应加入选择偏差惩罚。
4. **脚本沙箱**：静态检查 + 受限 builtins，非强隔离，生产环境请用容器。
5. **并发**：网格是串行的；单因子 200 次回测在真实面板上约 2 分钟，因子多了可以并行/缓存。
6. **Agent 记忆**：目前只把「已入库因子 + 本次已试假设」喂给 Agent 2.1，跨 run 的失败经验还没有持久化。

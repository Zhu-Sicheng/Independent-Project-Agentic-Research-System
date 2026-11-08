# Datasets and field vocabulary

The idea contract references a `dataset_id` and a list of `required_fields` from
that dataset. The Agent-1 data contract is the source of truth; the lists below
are the vocabulary for the datasets used by this project.

## Dataset: `market_ohlcv` (cross-sectional US equity panel)

Stored fields (one matrix per field: dates x securities):

| field | meaning |
|---|---|
| `open` | opening price, split/dividend adjusted |
| `high` | daily high, adjusted |
| `low` | daily low, adjusted |
| `close` | closing price, adjusted |
| `volume` | shares traded |

Derived fields (built on demand by the panel):

| field | meaning | depends on |
|---|---|---|
| `returns` | close-to-close simple return | `close` |
| `log_returns` | log of gross return | `close` |
| `amount` | dollar volume | `close`, `volume` |
| `adv20` | 20-day average dollar volume | `volume` |
| `cap` | market capitalisation | `close`, shares |
| `cap_rank` | cross-sectional percentile of `cap` | `cap` |
| `range` | daily high-low range | `high`, `low` |
| `close_position` | where the close sits inside the daily range | `high`, `low`, `close` |
| `intraday_return` | open-to-close return | `open`, `close` |
| `overnight_return` | previous close-to-open return | `open`, `close` |

Coverage notes:

* `cap` needs the shares/security-master input; if a contract marks it as
  blocked, avoid size-conditioned ideas for that dataset.
* `amount` and `adv20` are the liquidity vocabulary; use them instead of raw
  share volume when the idea is about dollar liquidity.
* Cross-sectional ideas need a universe with enough names per date.

## Dataset: `etf_ohlcv` (single instrument, e.g. SPY)

Fields: `open`, `high`, `low`, `close`, `volume`, plus the same derived fields
(`returns`, `range`, `close_position`, `intraday_return`, `overnight_return`).

Ideas for a single instrument are **time-series** hypotheses: expected direction
describes whether the signal state predicts the instrument's own forward return.
Cross-sectional dispersion ideas do not apply here; regime and path-dependence
ideas do.

## Field roles to keep in mind

* **Price level vs path**: raw levels are non-stationary; concepts should be
  relative to a baseline (recent mean, range, cross-section).
* **Directional decomposition**: `intraday_return` and `overnight_return` are
  separate channels with different participants; mixing them loses the story.
* **Position in range**: `close_position` describes where buyers/sellers left the
  price inside the day; it is a behavioural state variable, not momentum.
* **Activity vs aggressiveness**: `volume`, `amount` and `adv20` measure activity;
  they do not reveal buy/sell aggressiveness, so avoid claiming order-flow
  direction from them.

When the Agent-1 contract lists a field as `candidate_requires_confirmation`,
state that limitation in `applicability` instead of assuming full coverage.

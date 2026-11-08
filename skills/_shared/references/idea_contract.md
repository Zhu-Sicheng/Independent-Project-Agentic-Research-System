# Idea contract (Agent 2 interface)

Every idea emitted by this skill pack must be a single JSON object that the
project's ideation interface can ingest unchanged. The contract has 15 fields.

| field | type | rule |
|---|---|---|
| `title` | string | one sentence, names the mechanism and the signal |
| `family` | string | snake_case mechanism family, e.g. `liquidity_shock_reversal` |
| `dataset_id` | string | one of the dataset ids in the Agent-1 data contract |
| `mechanism` | string | prose: who trades, why, which friction, why the effect persists |
| `signal_concept` | string | prose: the measurable quantity and its economic meaning |
| `required_fields` | array[string] | 1+ fields from the dataset vocabulary |
| `expected_return_direction` | `"positive"` or `"negative"` | direction of the raw signal concept vs forward returns |
| `forecast_horizon_days` | integer 1..252 | holding horizon in trading days |
| `lookback_hint_days` | array[integer] | 1-3 plausible lookback lengths |
| `applicability` | array[string] | 1+ limits: market, universe, regime, data requirements |
| `failure_modes` | array[string] | 1+ concrete ways the mechanism breaks |
| `evidence_ids` | array[string] | 1+ evidence items from the Agent-1 bundle |
| `history_record_ids` | array[string] | prior memory records consulted (may be empty) |
| `novelty_rationale` | string | what is new relative to the consulted history |
| `required_operators` | array[string] | operator families needed (may be empty) |

## Hard rules enforced by the ideation interface

1. `mechanism` and `signal_concept` are prose. They must not contain formulas
   (no `ts_` function calls) and must not contain code fences. Describe the
   concept, not its implementation.
2. `required_fields` must be a subset of the chosen dataset's fields.
3. `expected_return_direction` describes the **raw** signal concept; the later
   implementation may flip the sign, so do not pre-negate the story.
4. At least one item each in `applicability`, `failure_modes` and `evidence_ids`.
5. `forecast_horizon_days` is an integer between 1 and 252.
6. Ideas are de-duplicated later on
   `(family, dataset_id, required_fields, expected_return_direction,
   forecast_horizon_days, lookback_hint_days)` — two ideas that differ only in
   wording collapse to one, so vary the mechanism and the role fields.

## What a good idea looks like

* The mechanism names the agents (retail, institutions, market makers), their
  incentives and the friction that prevents immediate arbitrage.
* The signal concept is measurable with the stated fields and has an
  unambiguous sign expectation.
* The horizon matches the mechanism: intraday positioning decays in days,
  liquidity/attention effects in weeks, behavioural anchoring in months.
* The failure modes are specific: which regime, which universe, which data
  condition would break it.
* The novelty rationale states what was already consulted and why this differs.

## Template (fill every field)

```json
{
  "title": "Liquidity-shock reversal: abnormally high trading activity after an up move predicts lower forward returns",
  "family": "liquidity_shock_reversal",
  "dataset_id": "market_ohlcv",
  "mechanism": "Attention-driven retail buying creates temporary price pressure when trading activity spikes after a price rise; because the pressure is inventory-driven rather than information-driven, it decays over subsequent days as market makers re-hedge and early buyers take profit.",
  "signal_concept": "Recent trading activity relative to its own recent baseline, measured after an up move; higher abnormal activity marks stronger temporary pressure and a larger expected pullback.",
  "required_fields": ["close", "volume", "returns"],
  "expected_return_direction": "negative",
  "forecast_horizon_days": 5,
  "lookback_hint_days": [5, 20, 60],
  "applicability": ["US large-cap equities with at least 60 trading days of history"],
  "failure_modes": ["strong earnings-news regimes where the volume spike is informative", "genuinely illiquid names where the baseline activity is noisy"],
  "evidence_ids": ["evidence:volume_price_relationship"],
  "history_record_ids": [],
  "novelty_rationale": "Consulted history reports generic short-term reversal; this idea isolates the volume-shock conditioning and the post-up-move state, not the unconditional reversal.",
  "required_operators": ["time-series", "element-wise"]
}
```

Keep fields and mechanism prose consistent: if a field is not needed to measure
the concept, do not list it.

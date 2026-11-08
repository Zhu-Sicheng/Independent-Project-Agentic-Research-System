---
name: event-theme-radar
description: Turn a macro event, news theme or market regime shift into cross-sectional or time-series factor hypotheses for the project's data. Use when the user shares news, a policy change, an earnings season observation or a market theme and wants factor ideas from it.
---

# Event and theme radar

Convert a real-world event, policy change, news theme or regime shift into
mechanism hypotheses that the available fields can measure. Output is idea JSON
only.

## When to use

* The user shares news, a policy decision, a sector theme or a macro observation.
* The user asks "what does this imply for factor ideas?".
* A regime change requires a new set of conditioning hypotheses.
* The user wants ideas tied to a current theme instead of a catalogue sweep.

## Inputs

* The event/theme description and, when available, dated news items.
* The Agent-1 data contract (datasets, fields, coverage).
* `../_shared/references/idea_contract.md`, `panel_fields.md` and optionally
  `anomaly_catalog.md` for mechanism primitives.
* Recent research memory for novelty.

## Workflow

1. **Classify the event** into a transmission channel:
   flow/liquidity, attention/sentiment, volatility/uncertainty, or
   fundamentals/earnings expectations.
2. **Ask who is forced to trade or rebalance** because of the event: which
   participants face mandates, redemptions, tax deadlines, futures expiry or
   index changes.
3. **Derive a measurable state** from the available fields that marks exposure to
   that channel. If the channel requires flows the fields cannot see, state the
   gap and stop.
4. **State the transmission chain** in prose: event -> participant behaviour ->
   price pressure or risk premium -> expected direction.
5. **Pick a horizon** matching the event's decay: an auction/expiry effect lasts
   days, an attention wave weeks, a policy regime months.
6. **Emit 3-6 ideas** across at least two transmission channels. Mark time-series
   ideas for the single-instrument dataset explicitly.
7. **Add regime labels** in applicability: define the state in which the idea is
   expected to hold and the state in which it should not.

## Output

Idea JSON array satisfying `../_shared/references/idea_contract.md`, plus a short
transmission map for the user: channel -> participants -> field used -> expected
direction -> horizon.

## Quality checklist

- [ ] The transmission chain has forced or incentive-driven participants, not
      generic sentiment.
- [ ] The measured state is derivable from listed fields.
- [ ] The event's decay matches the horizon.
- [ ] Regime assumptions are explicit in applicability.
- [ ] At least two different channels are represented in a batch.
- [ ] No formulas, code or operator names in prose fields.
- [ ] Novelty is checked against recent memory.

## Anti-patterns

* "The theme is hot, so buy related names" without a transmission mechanism.
* Claiming order-flow or holdings effects that the fields cannot observe.
* Using undated or future information in the hypothesis (look-ahead in the
  story).
* One channel repeated for every idea in the batch.
* Mapping a macro event directly to a single-name signal with no cross-section.

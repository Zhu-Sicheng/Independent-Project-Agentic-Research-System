---
name: anomaly-taxonomy
description: Choose documented market anomalies by mechanism and map them to the available data fields, then emit contract-ready idea JSON. Use when the user wants ideas grounded in known anomalies or needs family-level diversification for an existing idea set.
---

# Anomaly taxonomy

Use the shared mechanism catalogue to generate hypotheses that are grounded in
published market behaviour **and** measurable with the project's fields.

## When to use

* The user wants ideas with documented economic backing.
* An idea batch is clustered in one family and needs a systematic sweep.
* A new dataset requires a menu of mechanisms that the fields can express.
* The user asks "which anomalies can we test with what we have?".

## Inputs

* `../_shared/references/anomaly_catalog.md` — mechanism seeds with direction,
  horizon, fields and failure modes.
* The Agent-1 data contract — which datasets and fields are available.
* Recent research memory — which catalogue rows were already used.

## Workflow

1. **Filter the catalogue by fields.** Keep only rows whose required fields are
   available in the contract. Note rows that become feasible with derived fields.
2. **Filter by memory.** Drop rows whose mechanism family was already tried in
   the recent idea records unless the user explicitly asks for a revisit with a
   new conditioning state.
3. **Rank by fit.** Prefer rows where the available fields measure the mechanism
   directly (e.g. `close_position` for intraday demand absorption) over rows
   that need proxies.
4. **Write the mechanism in local terms.** Replace generic actors with the
   universe's actual participants and frictions; add one market-specific
   failure mode.
5. **Emit 4-8 ideas** as contract JSON, one per chosen row or pair of rows.
6. **Record provenance in evidence context**, not in the mechanism text: note the
   origin reference in the idea's support notes so the reviewer can find it, but
   keep the mechanism statement self-contained.

## Selection rules

* At most two ideas from the same family per batch.
* Mix horizons: at least one short (<= 10 trading days) and one medium
  (>= 1 month) horizon per batch.
* Mix field types: at least one idea that uses price geometry, one that uses
  activity (volume or dollar volume), one that uses volatility or dispersion.
* Prefer a modest, well-identified mechanism over a dramatic story with a weak
  field mapping.

## Output

JSON array of idea objects satisfying `../_shared/references/idea_contract.md`.
Include a compact `family` value matching the catalogue row family (snake_case),
and `required_fields` limited to what the mechanism needs.

## Quality checklist

- [ ] Every idea traces to a catalogue row whose mechanism the fields can measure.
- [ ] Mechanism text is local, not copied from the catalogue.
- [ ] Direction, horizon and lookbacks follow the mechanism.
- [ ] Failure modes include the catalogue caveat plus one market-specific case.
- [ ] Family and field set differ across the batch.
- [ ] No formulas, code or operator names in the prose fields.

## Anti-patterns

* Copying catalogue rows verbatim as ideas.
* Using a row whose fields are blocked in the contract.
* Ten ideas from one family with different lookbacks.
* Claiming a mechanism that needs order-flow or fundamentals that are absent.

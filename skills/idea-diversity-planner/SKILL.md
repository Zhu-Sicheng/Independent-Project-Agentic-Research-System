---
name: idea-diversity-planner
description: Plan a factor-idea batch across mechanism families, datasets and horizons and avoid clustering or repetition against recent memory. Use when the user asks for N new ideas, a diverse idea batch, or to plan the next ideation round.
---

# Idea diversity planner

Plan **what kinds of ideas** a batch should contain before writing them, so the
batch is diverse and non-repetitive. Planning only; each planned cell is then
filled with a contract idea via `factor-idea-scout` or `hypothesis-formalizer`.

## When to use

* The user asks for a specific number of new ideas.
* The previous batch was clustered in one family or one dataset.
* The user asks how to organise the next ideation round.
* Research memory shows many near-duplicate records.

## Inputs

* The target count and the batch budget (how many ideas the interface accepts).
* The Agent-1 data contract (datasets and fields).
* Recent research memory: families, fields, directions, horizons already used.
* `../_shared/references/anomaly_catalog.md` for the family menu.

## Workflow

1. **Build the coverage matrix**: rows = mechanism families from the catalogue,
   columns = datasets, and a horizon band per cell (short <= 10 days, medium
   1-6 weeks, long >= 1 month).
2. **Mark exhausted cells** using memory: a cell is exhausted when the same
   mechanism and field set were already used with the same direction and
   horizon; wording changes do not count.
3. **Choose cells** for the batch: prefer unused cells, then partly used cells
   with a new conditioning state, and only then revisits justified by a new
   participant story.
4. **Enforce quotas**: no more than ~25% of the batch from one family, at least
   two distinct horizons, at least two distinct field groups (price geometry,
   activity, volatility, size).
5. **Write a one-line plan per idea** before the full record: family, dataset,
   role fields, direction, horizon, conditioning state, difference from memory.
6. **Fill the plan** with complete idea JSON records (delegate to the scout or
   formalizer workflows).
7. **Re-check the batch** after writing: count families, horizons and field
   groups; replace the weakest duplicate.

## Output

* A batch plan table (family, dataset, fields, direction, horizon, novelty
  note).
* Idea JSON array satisfying `../_shared/references/idea_contract.md`.
* A diversity summary for the user: distribution by family, horizon and field
  group, plus the records consulted.

## Quality checklist

- [ ] No family exceeds the quota.
- [ ] At least two horizons and two field groups represented.
- [ ] Every idea has a stated difference from the closest memory record.
- [ ] Contract-valid JSON for every idea.
- [ ] The batch is internally varied, not variations of one formula.

## Anti-patterns

* Filling the batch by changing one lookback per idea.
* Planning in terms of formulas rather than mechanisms.
* Ignoring memory and repeating recent records.
* Planning ideas the available fields cannot express.
* Maximising count over coverage.

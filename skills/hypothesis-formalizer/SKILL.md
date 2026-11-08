---
name: hypothesis-formalizer
description: Turn a rough thesis, note or draft idea into a contract-valid Agent-2 idea JSON record with explicit direction, horizon, fields, applicability and failure modes. Use when the user has a draft idea or a philosophy note that must become a formal, testable hypothesis.
---

# Hypothesis formalizer

Take an informal thesis and make it a **complete, contract-valid idea record**.
This skill does not judge whether the idea is good; it makes the idea precise,
falsifiable and ingestible by the project's ideation interface.

## When to use

* The user gives a rough idea in chat or notes and wants it recorded properly.
* A batch of ideas must be normalised to the contract before ingestion.
* A thesis lacks direction, horizon, fields or failure modes.
* The user asks "is this idea well specified?".

## Inputs

* The rough thesis and any supporting notes.
* `../_shared/references/idea_contract.md` — field-by-field rules.
* `../_shared/references/panel_fields.md` — the field vocabulary.
* The Agent-1 data contract for dataset ids and coverage.

## Workflow

1. **Extract the claim**: what predicts what, in which direction, over which
   horizon.
2. **Write the mechanism** in prose with actors, incentives and the friction that
   keeps the effect alive. Remove any formula or implementation term.
3. **Write the signal concept** as the measurable quantity, its conditioning
   state and the expected direction. If the thesis implies a formula, describe
   the quantity instead.
4. **Choose the minimum field set** from the panel vocabulary. For each field,
   say in one clause why it is needed.
5. **Set the direction**: `positive` if higher raw signal means higher forward
   return, `negative` otherwise. Do not pre-negate the story.
6. **Set the horizon** from the mechanism and list 1-3 plausible lookbacks.
7. **Write applicability** as concrete limits (universe, market, regime, data
   coverage) and **failure modes** as concrete break conditions.
8. **Write the novelty rationale**: what was consulted and what is genuinely
   different.
9. **Validate the record** with `python skills/validate.py --idea <file>` and fix
   every finding before returning.

## Output

One idea JSON object (or an array when several mechanisms are being formalised)
that passes the contract checks. Include a one-line note of what was ambiguous in
the original thesis and how it was resolved.

## Field mapping hints

| thesis language | likely field family |
|---|---|
| "price is stretched above its recent average" | `close`, `returns` |
| "buyers closed the day in control" | `close_position`, `high`, `low`, `close` |
| "participation is abnormally high" | `volume`, `amount`, `adv20` |
| "the move happened overnight" | `overnight_return`, `open`, `close` |
| "small names are ignored" | `cap`, `cap_rank` |
| "the daily path was noisy" | `range`, `returns`, `high`, `low` |

## Quality checklist

- [ ] All 15 contract fields present and correctly typed.
- [ ] Mechanism and signal concept contain no formula, code or operator name.
- [ ] Direction, horizon and lookbacks match the mechanism.
- [ ] Required fields are available and minimal.
- [ ] Applicability and failure modes are concrete, not generic.
- [ ] The record validates with `validate.py`.
- [ ] The claim is falsifiable: an observation could contradict it.

## Anti-patterns

* Dropping ambiguous parts of the thesis to make a clean record.
* Writing a mechanism that is a restatement of the signal.
* Listing many fields "for flexibility".
* Pretending a blocked field is available.
* Leaving direction or horizon to be inferred later.

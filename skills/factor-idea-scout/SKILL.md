---
name: factor-idea-scout
description: Mechanism-first factor idea generation from a data contract or EDA summary. Use when the user asks for new factor ideas, a fresh hypothesis batch, or more diverse mechanisms for an existing idea set; emits Agent-2-compatible idea JSON and stops at the idea layer.
---

# Factor idea scout

Turn data understanding into **testable, mechanism-first hypotheses**. This skill
produces idea records only; implementation and any performance work stay with the
project's existing pipeline.

## When to use

* The user asks "what factors can we mine from this data?" or "give me new ideas".
* A batch needs more mechanisms instead of variations of one idea.
* A completed batch shows clustering in one family and needs diversification.
* A new dataset or data contract has just been described and needs idea seeds.

Do not use this skill to write expressions, code, or to judge results.

## Inputs to read first

1. The Agent-1 data contract (datasets, fields, coverage, blockers).
2. The recent research memory snapshot (idea families already tried, rejected
   ideas, their stated failure modes).
3. `../_shared/references/idea_contract.md` — the output contract and its rules.
4. `../_shared/references/panel_fields.md` — the dataset and field vocabulary.
5. `../_shared/references/anomaly_catalog.md` — mechanism seeds.

If a required input is missing, say what is missing and proceed with the fields
and memory you do have; never invent dataset names or field coverage.

## Workflow

1. **Inventory the fields.** List the stored and derived fields that are actually
   available and mark any blocked ones.
2. **Pick 2-4 mechanism families** that fit those fields and are under-used in the
   recent memory. Prefer families with different horizons (days vs months) and
   different participant stories (retail attention vs institutional execution).
3. **For each family, write the mechanism first** in 2-4 sentences: who trades,
   why they trade, which friction stops arbitrage, why the effect persists.
   No formulas, no operator names, no code.
4. **Derive the signal concept** from the mechanism: the measurable quantity, the
   conditioning state, and the expected direction of the raw signal.
5. **Choose horizon and lookbacks** consistent with the mechanism:
   attention/liquidity effects 3-20 trading days, behavioural anchoring 1-6
   months, overnight channels 1-5 days.
6. **Map to fields.** Use the minimum set of fields that measures the concept.
   Prefer a directionally clean field (e.g. `close_position`) over a bundle of
   proxies; avoid fields whose coverage is blocked.
7. **Write failure modes** specific to the universe and the mechanism: which
   regime, which data condition, which participant behaviour would break it.
8. **Emit 4-8 ideas** as JSON objects following the contract. Use a distinctive
   mechanism sentence and signal concept for each; wording variations are not
   diversity.
9. **Self-check** with the checklist below before returning.

## Output

Return a JSON array of idea objects. Every object must satisfy
`../_shared/references/idea_contract.md`; include `history_record_ids` for the
memory records actually consulted. Add one short note per idea explaining why it
is different from the closest record in memory.

## Quality checklist

- [ ] Mechanism names agents, incentives and the friction that prevents arbitrage.
- [ ] Signal concept is measurable with the listed fields and has a clear sign.
- [ ] Mechanism and signal concept are prose: no formulas, no code, no operator
      names.
- [ ] Horizon and lookbacks follow from the mechanism, not from convention.
- [ ] At least one applicability limit and one failure mode are concrete.
- [ ] Field list is minimal and available; no blocked fields.
- [ ] Family and required fields differ from the closest recent memory record;
      a wording-only change is not novelty.
- [ ] The idea can be disproved: state what observation would make you drop it.

## Anti-patterns

* **Formula-first**: starting from an expression family and inventing a story
  afterwards. The mechanism must be able to fail on its own terms.
* **Template centre**: every idea is the same direction of the same mechanism
  with a different window. Rotate families and horizons instead.
* **Generic market lore**: "buy low, sell high" without agents or frictions.
* **Unmeasurable concept**: a story that needs order-flow or fundamentals the
  contract does not provide.
* **Tautology**: signal and horizon defined by the same future price path.
* **Vanity applicability**: "works in all markets" instead of real limits.

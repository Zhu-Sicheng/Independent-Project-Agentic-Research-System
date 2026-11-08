---
name: paper-to-hypothesis
description: Convert a research paper, report or article finding into a testable cross-sectional or time-series factor hypothesis and contract-ready idea JSON. Use when the user provides a paper, abstract, blog post or finding and wants factor ideas from it.
---

# Paper to hypothesis

Turn a published finding into a **testable mechanism hypothesis** for this
project's data. The output is idea JSON plus evidence notes; no implementation.

## When to use

* The user pastes a paper abstract, finding, figure caption or report section.
* The user asks "can we turn this into a factor?".
* A literature scan should produce a batch of hypotheses.

## Inputs

* The source text (paper, report, article) — read the finding and the sample.
* The Agent-1 data contract — which fields can measure the concept.
* `../_shared/references/idea_contract.md` and `panel_fields.md`.
* Recent research memory — novelty check.

## Workflow

1. **Extract the finding** in one sentence: what predicts what, in which
   direction, over which horizon, and in which sample.
2. **Extract the mechanism**: the economic or behavioural reason the authors
   give, plus any competing explanation. If the paper only reports a
   correlation, say so and treat the mechanism as a conjecture.
3. **Check applicability**: market, universe, period, data frequency and field
   definitions. Note where the project's data differs.
4. **Operationalise the signal concept** with the available fields: the
   conditioning state, the measured quantity and the sign. Keep the paper's
   direction; do not pre-negate.
5. **Choose a horizon** consistent with the reported effect and the project's
   data resolution.
6. **State falsification conditions**: which observation would contradict the
   hypothesis.
7. **Emit 1-3 idea JSONs** (if the paper supports several distinct mechanisms,
   one per mechanism; otherwise a single idea).
8. **Write evidence notes**: paper title/authors/year/section in plain text, the
   quoted finding, the sample, and the caveats. Cite sources as text, never as
   a link that an agent must open.

## Output

* Idea JSON array satisfying `../_shared/references/idea_contract.md`.
* A short evidence note per idea: source, finding, sample, difference from this
  project's data, and what the user must confirm before implementation.

## Quality checklist

- [ ] The finding is quoted or paraphrased precisely; no invented statistics.
- [ ] Mechanism and signal concept are prose: no formulas or code.
- [ ] Required fields can measure the concept with the contract's data.
- [ ] Horizon matches the reported horizon; lookbacks are plausible.
- [ ] Applicability lists the sample difference and any blockers.
- [ ] Failure modes cover the competing explanation and the data gap.
- [ ] Evidence note tells the user where the finding came from.

## Anti-patterns

* Treating a correlation as a mechanism without saying it is a conjecture.
* Importing a multi-factor finding into a single-field idea and hiding the gap.
* Assuming the paper's universe and period apply to this project.
* Fabricating citations or sample details.
* Turning the finding into an expression in the idea text.

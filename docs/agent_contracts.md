# Agent contracts

Three agents sit on one data contract (`PanelStore`) and two JSON contracts
(hypothesis, factor spec). Everything below is what actually crosses the
boundary — the orchestrator only ever exchanges these objects, so any agent can
be replaced by a different model, a different prompt, or a rule-based module.

```
PanelStore ──► 2.1 HypothesisAgent ──► hypothesis dict
                                          │
                                          ▼
                                   2.2 ImplementationAgent ──► FactorSpec
                                                                  │
                                                                  ▼
                                            backtest + grid search (evidence)
                                                                  │
                                                                  ▼
                                                      3 CriticAgent ──► decision
```

## Agent 2.1 — hypothesis

**In**: `panel.summary()` (date range, per-field coverage / distribution /
autocorrelation), the current pool summary, the names already tried and
rejected, free-text feedback from a previous round.

**Out**: a list of hypothesis objects. Required keys are `name`, `hypothesis`,
`factor_description`; the rest are strongly recommended.

```json
{
  "name": "short_term_reversal",
  "economic_rationale": "why a premium should exist (2-4 sentences)",
  "hypothesis": "falsifiable statement with direction and horizon",
  "factor_description": "exact recipe in words, including any rank/zscore",
  "data_fields": ["close", "volume"],
  "horizon_days": 5,
  "expected_sign": "positive",
  "testable_prediction": "what a successful backtest would look like",
  "novelty": "how it differs from the existing pool"
}
```

`expected_sign` is the expected **IC sign** (positive = high factor values
outperform), not the sign of the raw price. 2.1 is not allowed to emit code: if
the description cannot be implemented, it is 2.2's (or 3's) problem.

## Agent 2.2 — implementation

**In**: one hypothesis object, the field catalog, the operator catalog
(generated from the registry), the allowed window set, and — on a retry — the
validator errors plus the rejected spec.

**Out**: a `FactorSpec`, i.e. one of

```json
{"kind": "expression", "expression": "-rank(ts_mean(returns, 5))",
 "explanation": "why this formula expresses the mechanism"}
```

```json
{"kind": "script",
 "script": "def generate(panel, params): ... return df",
 "params": {"window": 5},
 "param_grid": {"window": [5, 20, 60]},
 "explanation": "why the expression language is not enough here"}
```

The spec is validated against the panel (fields exist, operators known, windows
economically meaningful, script passes the static checks) and materialised into
a `date x ticker` matrix. 2.2 never sees the backtest: it is a translation
layer, so a bad result cannot tempt it to shop for a formula that fits.

## Agent 3 — review

**In**: the hypothesis, the spec, the grid summary (`best`, `in_sample`,
`out_of_sample`, `holdout`, per-year tables, share of configurations with
positive Sharpe) and the history of attempts on the same hypothesis. The
selection only ever saw `in_sample`; the other two are untouched.

**Out**:

```json
{"decision": "accept | optimize | abandon",
 "confidence": 0.0,
 "reasoning": "references the numbers",
 "diagnosis": "signal / costs / regime / sign",
 "hypothesis_supported": true,
 "suggested_changes": ["one concrete change"],
 "revised": {"kind": "expression", "expression": "...", "explanation": "..."}}
```

`revised` is only read when the decision is `optimize`, and must differ from the
current spec. Changes to decay / rank / sign / cap filter are rejected by
construction because the grid already searched them; 3 may only change the
factor's structure (sign flip, a different economically meaningful window,
smoothing, a different normalisation).

## Orchestration loop

```
for hypothesis in 2.1.propose(...):
    spec = 2.2.implement(hypothesis)
    for round in 1..max_rounds:
        validate(spec)                    # reject -> log, next hypothesis
        evidence = grid_search(spec)      # decay x transform x cap x windows
        decision = 3.review(hypothesis, spec, evidence)  # is / oos / holdout
        if accept:    pool.add(...); break
        if optimize:  spec = decision.revised; continue
        if abandon:   break
```

## Extension points

- **New agent (2.3)**: implement `implement(hypothesis, panel) -> FactorSpec`
  and insert it between 2.2 and the backtester; nothing else changes.
- **New operator**: register it in `factorlab/expr/ops.py`; the catalog handed
  to 2.2 and the validator update automatically.
- **New data source**: return a `dict[field, DataFrame]` and build a
  `PanelStore`; every agent sees it through `panel.summary()`.
- **New selection metric**: set `GridConfig.objective`; the critic's evidence
  block follows.

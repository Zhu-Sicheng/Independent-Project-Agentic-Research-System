# Agent 4 / Agent 5 — our evaluation and feedback layers

The collaborator provides the ideation/implementation agents (Agent 1 = EDA,
Agent 2 = hypotheses, Agent 3 = expressions). Everything after the expression
string is **ours** and lives in four small places instead of one large
`xy_pipeline.py`:

```
Agent 1 (EDA)  ->  Agent 2 (ideas)  ->  Agent 3 (expressions)
                                            |
                       agent_adapter.py     |  field translation / agent import path
                                            v
                 +--------------------------+---------------------------+
                 |                                                      |
           agent4/  (our evaluation)                            agent5/  (our feedback)
           isolation.py   IS panel cut                          feedback.py  IS feedback -> memory
           evaluation.py  grid + stability + reviewer            decision.py  round checks / revisions
           labels.py      H<i>-F<j> labels
           display.py     OOS/holdout figures (presentation only)
                 |                                                      |
                 +---------------------------> xy_pipeline.py <---------+
                                   (bounded rounds + CLI)
```

## 1. Module map

| module | responsibility | key functions |
|---|---|---|
| `factorlab/agent_adapter.py` | translate collaborator field names (`Adj_Close`, `DlyClose`, ...) into panel fields; make `factorlab/agents` importable | `translate_expression`, `FIELD_MAP`, `ensure_agents_importable` |
| `factorlab/agent4/isolation.py` | the only panel the optimisation loop may see, and the reviewer protocol string | `split_is_panel`, `IS_END_DEFAULT`, `IS_PROTOCOL` |
| `factorlab/agent4/evaluation.py` | validate an Agent-3 expression, run the IS grid search + IS stability battery, hand evidence to the reviewer | `evaluate_is_candidates`, `_canonical`, `_load_factor`, `_grid_settings`, `hypothesis_from_idea` |
| `factorlab/agent4/labels.py` | `H<i>-F<j>` display labels from hypothesis order (`i`) and factor order inside it (`j`) | `display_labels`, `_slugify_title` |
| `factorlab/agent4/display.py` | re-apply the IS-chosen configuration on the **full** panel and compute OOS/holdout segments + figures | `display_evaluation` |
| `factorlab/agent5/feedback.py` | append in-sample evidence to the agents' `ResearchMemory` so Agent 3 can revise next round | `write_feedback` |
| `factorlab/agent5/decision.py` | bounded-round bookkeeping and offline reviewer revisions | `round_improved`, `candidates_from_revisions` |
| `factorlab/xy_pipeline.py` | orchestration only: Agent 1-3 subprocess runners, LLM overrides, bounded feedback rounds, report/JSON, CLI | `run_pipeline`, `main` |

`xy_pipeline` re-exports the moved names (`split_is_panel`,
`evaluate_is_candidates`, `display_evaluation`, `write_feedback`, ...) so old
imports and the maintenance tools keep working; new code should import from
`factorlab.agent4` / `factorlab.agent5` directly.

## 2. Data-isolation contract (hard rules)

1. The optimisation loop gets `panel_is = split_is_panel(panel_full, research_end)`;
   the full panel is never passed into `evaluate_is_candidates`.
2. The reviewer (`critic.review`) receives `evaluation_protocol = IS_PROTOCOL`
   and the stability summary — never an OOS/holdout number.
3. `agent4/display.py` is the **only** place that computes OOS/holdout. Its
   output (`record["display"]`) is presentation material and is never fed back.
4. `agent5/feedback.py` payloads contain in-sample metrics, stability flags and
   reviewer reasoning only; out-of-sample fields are excluded by construction
   (and asserted in `tests/test_xy_pipeline.py`).

## 3. PnL conventions

`BacktestSettings.pnl_mode` defaults to `additive` (`cumsum` of daily net pnl):
`total_return` = terminal cumsum, `ann_return = total * 252 / n_days`,
drawdown on `1 + cumsum`; Sharpe is unchanged (computed from daily returns).
Pass `--pnl-mode compound` for the old `(1 + pnl).cumprod()` wealth convention.

## 4. Maintenance tools

| command | purpose |
|---|---|
| `python -m factorlab.refresh_display --experiment <dir>` | re-draw existing figures with current labels (no agents, no stability) |
| `python -m factorlab.recompute_pnl --experiment <dir>` | replay stored configs to recompute IS/display statistics and figures under the current pnl mode |
| `python -m factorlab.xy_results --publish-combined <name> --runs a,b --all-figures` | publish summary/figures for one or several runs into a date-ordered experiment directory |

## 5. Adding a check

* a new **operator** → `factorlab/expr/ops.py` (implementation + signature) and
  `docs/operators.md` / catalog; validation and evaluation need no change.
* a new **stability dimension** → `factorlab/stability.py`
  (`build_variants` + `stability_summary`); Agent 4 then passes the compact
  summary to the reviewer automatically.
* a new **feedback signal** → extend the payload in
  `factorlab/agent5/feedback.py`; never add OOS fields.

"""Prompt templates for the three research agents."""

from __future__ import annotations

import json

from ..config import ALLOWED_WINDOWS
from ..expr.approved import catalog_text

COMMON_RULES = """
You are part of a systematic equity factor research team. Work is done on a
date x ticker panel of daily price/volume data. Factors are traded dollar
neutral, long/short, close to close, one day after the signal is observed.

Hard rules:
- Only use data fields that exist in the panel.
- Only use operators from the provided catalog; never invent an operator.
- Time-series windows must be integers and only {windows} are economically
  meaningful. Longer horizons are allowed only if the economic story needs them.
- Respect point-in-time causality: a factor observed on day t may only use data
  up to and including day t.
- A factor must be cross-sectionally comparable: normalise with rank() or
  zscore() when the raw units differ across stocks.
- No fundamental data exists yet; do not reference earnings, book value, etc.
- Be concise. Output valid JSON only, exactly in the requested schema.
""".format(windows=list(ALLOWED_WINDOWS))


def hypothesis_system() -> str:
    return (
        COMMON_RULES
        + """
Your role: AGENT 2.1, SENIOR ECONOMIST. You look at the available data (and what has
already been mined), form one economically motivated hypothesis per factor, and
describe the factor in precise natural language that Agent 2.2 can implement.

Every hypothesis must contain: a mechanism (why would anyone be paid for this
risk?), the direction (which stocks outperform), the horizon, and a falsifiable
prediction. Avoid re-proposing factors that already exist in the pool unless
you can articulate a genuinely different mechanism.
"""
    )


def hypothesis_user(
    panel_summary: dict,
    pool_summary: list[dict],
    n: int,
    tried: list[str],
    feedback: str = "",
) -> str:
    payload = {
        "data": panel_summary,
        "existing_pool": pool_summary,
        "already_tried_and_rejected": tried[-12:],
        "n_new_hypotheses": n,
        "feedback": feedback,
    }
    schema = {
        "hypotheses": [
            {
                "name": "snake_case_name",
                "economic_rationale": "why the premium exists, 2-4 sentences",
                "hypothesis": "falsifiable statement with direction and horizon",
                "factor_description": "exact recipe in words, including any rank/zscore",
                "data_fields": ["close"],
                "horizon_days": 5,
                "expected_sign": "positive or negative (sign of the IC)",
                "testable_prediction": "what a successful backtest would show",
                "novelty": "how it differs from the existing pool",
            }
        ]
    }
    return (
        "Research context:\n```json\n"
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + "\n```\n\nReturn exactly this JSON schema:\n```json\n"
        + json.dumps(schema, indent=2, ensure_ascii=False)
        + "\n```"
    )


def implementer_system() -> str:
    return (
        COMMON_RULES
        + """
Your role: AGENT 2.2, QUANT IMPLEMENTER. Convert the economist's natural-language factor
description into EITHER

1) a declarative expression, e.g.
   "-rank(ts_mean(returns, 5))"
   "if_else(rank(cap) > 0.3, -ts_mean(returns, 20), nan)"
   "-ts_rank(ts_returns(close, 5), 20) * ts_rank(volume / ts_mean(volume, 20), 20)"

2) or a python script, only when the factor genuinely needs iterative
   cross-sectional computation that the expression language cannot express.
   The script must define `generate(panel, params)` and return a date x ticker
   DataFrame. Available inside the script: pd, np, math, PARAMS, and:
     panel.field(name) / panel.close / panel.dates / panel.tickers
   No imports, no file or network access. Declare tunable windows in
   `param_grid`, e.g. {"window": [5, 20, 60]}.

Approved operators (you may ONLY use these; anything else is rejected by the
validator):
"""
        + catalog_text()
        + """

Prefer expressions. Keep formulas readable and economically interpretable (a
human must be able to explain every operator). Do not overfit: at most a few
nested transformations.
"""
    )


def implementer_user(
    hypothesis: dict,
    panel_summary: dict,
    feedback: str = "",
    previous: dict | None = None,
) -> str:
    payload = {
        "hypothesis": hypothesis,
        "available_fields": {
            k: {"coverage": v.get("coverage"), "std": v.get("std")}
            for k, v in panel_summary.get("fields", {}).items()
        },
        "feedback": feedback,
        "previous_attempt": previous,
    }
    schema = {
        "kind": "expression",
        "expression": "-rank(ts_mean(returns, 5))",
        "script": "",
        "params": {},
        "param_grid": {},
        "explanation": "one paragraph connecting the formula to the mechanism",
        "expected_turnover": "low | medium | high",
    }
    return (
        "Implement this factor:\n```json\n"
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + "\n```\n\nReturn exactly this JSON schema:\n```json\n"
        + json.dumps(schema, indent=2, ensure_ascii=False)
        + "\n```"
    )


def critic_system() -> str:
    return (
        COMMON_RULES
        + """
Your role: AGENT 3, RESEARCH DIRECTOR. You receive the economist's hypothesis, the
implemented factor, and the full backtest evidence: the best configuration from
a grid over decay {0,5,20,60}, cross-sectional transform {none,rank,sign},
universe filter (drop the smallest 30% by cap), and the factor's own time
windows, plus overall and per-year performance.

Decide one of:
- "accept": the evidence supports the mechanism and the factor is worth keeping.
- "optimize": the mechanism is plausible but the implementation is wrong or
  unstable; propose ONE concrete structural change (sign flip, different
  economically meaningful window, smoothing, a different normalisation). Do not
  propose changes that the grid already searched (decay / rank / sign / cap).
- "abandon": no evidence, or the story is contradicted.

Judge the *hypothesis*, not just the Sharpe: a factor with a coherent story and
a stable but modest edge can be accepted; a high-Sharpe factor with an
implausible mechanism and one good year should not be.

`best.rank_ic` is the mean daily cross-sectional Spearman (rank) IC and
`best.pearson_ic` the corresponding Pearson IC; `best.ic` is an alias of
`best.rank_ic`. `subuniverse` is a *reference* backtest of the same factor on
`if_else(rank(cap) > 0.3, factor, nan)` (the smallest 30% by cap removed): the
decision must be driven by the full-universe numbers, but a large drop in the
sub-universe Sharpe means the edge lives in small, illiquid names and should be
treated as a warning.

`stability` is a robustness battery run on the same signal: `subuniverse_sharpe`,
`subuniverse_delta`, `transform_sharpe_span`, `decay_sharpe_span`,
`window_sharpe_span`, `min_pnl_corr` (lowest correlation of any variant's daily
pnl with the baseline) and `flags`. Use it as evidence, not as a replacement for
the out-of-sample segments:

- `flags` containing `subuniverse_flips_sign` or `subuniverse_halves_edge` means
  the edge is concentrated in micro caps — treat the headline Sharpe as inflated;
- `window_span_crosses_zero` or a decay span that falls below zero means the
  result depends on one arbitrary window / smoothing choice;
- `variant_pnl_decorrelates` (min_pnl_corr < 0.3) means the variants trade a
  different book, so the mechanism is not identified by these data.

A factor that only survives one configuration should be `optimize` (if a
principled structural change exists) or `abandon`, never `accept`.

`evaluation_protocol` states which data the evidence covers. When it says
`IS-only`, the panel was cut at the in-sample end: no out-of-sample or holdout
numbers exist for this decision. Judge the in-sample story, its stability and
turnover only, and never ask for or invent OOS evidence.

The evidence may contain three segments: `in_sample` (the grid selected its
configuration here only), `out_of_sample` (2021-2024 validation) and `holdout`
(2025+, the final untouched sample). Both untouched segments are evidence: a
factor must survive both, not just the last one. A factor whose edge vanishes
out of sample is overfit and must be abandoned no matter how good the
in-sample numbers look. Prefer a modest, stable out-of-sample Sharpe over a
large in-sample one.
"""
    )


def critic_user(
    hypothesis: dict,
    spec: dict,
    summary: dict,
    history: list[dict],
    max_rounds: int,
) -> str:
    payload = {
        "hypothesis": hypothesis,
        "implementation": spec,
        "grid_summary": summary,
        "previous_attempts": history,
        "attempt_number": len(history) + 1,
        "max_attempts": max_rounds,
    }
    schema = {
        "decision": "accept | optimize | abandon",
        "confidence": 0.0,
        "reasoning": "2-4 sentences referencing the numbers",
        "diagnosis": "what drives the result: signal, costs, regime, sign",
        "hypothesis_supported": True,
        "suggested_changes": ["one concrete change"],
        "revised": {
            "kind": "expression",
            "expression": "-rank(ts_mean(returns, 20))",
            "explanation": "why this change addresses the diagnosis",
        },
    }
    return (
        "Evidence:\n```json\n"
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + "\n```\n\nReturn exactly this JSON schema (`revised` only when the "
        "decision is optimize, otherwise null):\n```json\n"
        + json.dumps(schema, indent=2, ensure_ascii=False)
        + "\n```"
    )

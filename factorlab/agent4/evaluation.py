"""Agent 4a -- in-sample factor evaluation.

Runs the approved expression through the in-sample grid search, the in-sample
stability battery and hands the compact evidence to the reviewer. It cannot see
any out-of-sample date (``panel_is`` is the cut panel).
"""

from __future__ import annotations

from typing import Iterable, Optional

from ..agent_adapter import translate_expression
from .isolation import IS_PROTOCOL

def _canonical(expression: str) -> str:
    from factorlab.expr import parser as P

    return P.to_string(P.parse(expression))


def _load_factor(panel, expression: str, windows: Optional[list[int]] = None):
    """Evaluate ``expression`` on ``panel`` with the given window substitution."""
    from factorlab.expr import parser as P
    from factorlab.expr.evaluator import evaluate

    ast = P.parse(expression)
    slots = P.collect_windows(ast)
    if windows and len(slots) == len(windows):
        ast = P.substitute_windows(ast, [int(w) for w in windows])
    return evaluate(ast, panel)


def _grid_settings(grid_summary: dict, pnl_mode: str = "additive"):
    import math

    from factorlab.config import BacktestSettings

    best = grid_summary.get("best") or {}
    cap = best.get("cap_filter")
    try:
        cap = None if cap is None else float(cap)
    except (TypeError, ValueError):
        cap = None
    if cap is not None and not math.isfinite(cap):
        cap = None  # the grid stores the "no cap filter" cell as NaN in a DataFrame
    return BacktestSettings(
        decay=int(best.get("decay") or 0),
        transform=str(best.get("transform") or "none"),
        cap_filter=cap,
        pnl_mode=pnl_mode,
    )


def hypothesis_from_idea(idea: dict) -> dict:
    direction = idea.get("expected_return_direction", "positive")
    return {
        "name": idea.get("title") or idea.get("idea_id", "idea"),
        "mechanism": idea.get("mechanism", ""),
        "signal_concept": idea.get("signal_concept", ""),
        "family": idea.get("family", ""),
        "expected_sign": "positive" if direction == "positive" else "negative",
        "forecast_horizon_days": idea.get("forecast_horizon_days"),
        "source": "xy_agent2",
    }


def evaluate_is_candidates(
    panel_is,
    candidates: Iterable[dict],
    ideas: dict,
    seen: set,
    run_id: str,
    round_index: int,
    grid,
    critic,
    max_rounds: int = 1,
    verbose: bool = True,
) -> list[dict]:
    """Evaluate new Agent-3 expressions with IS data only.

    Returns records with the in-sample grid evidence, the stability battery on
    the IS panel and the reviewer decision. Nothing here can see an
    out-of-sample date.
    """
    from factorlab.expr.spec import FactorSpec
    from factorlab.expr.validate import validate_expression
    from factorlab.stability import stability_summary

    records: list[dict] = []
    for candidate in candidates:
        status = str(candidate.get("status", ""))
        if not (
            candidate.get("ready_for_agent4_factor_evaluation")
            or status.startswith("research_validated")
            or status.startswith("critic_revision")
        ):
            continue
        idea = ideas.get(candidate.get("idea_id", ""), {})
        hypothesis = candidate.get("hypothesis") or hypothesis_from_idea(idea)
        record = {
            "round": round_index,
            "expression_id": candidate.get("expression_id"),
            "idea_id": candidate.get("idea_id"),
            "hypothesis": hypothesis.get("name"),
            "expression_raw": candidate.get("expression"),
            "status": "rejected_before_backtest",
        }
        try:
            expression = translate_expression(candidate["expression"])
            canonical = _canonical(expression)
            if canonical in seen:
                continue
            seen.add(canonical)
            record["expression"] = expression
            report = validate_expression(expression, panel_is, strict_windows=False, min_window=1)
            if not report.ok:
                record["error"] = "; ".join(report.errors)
                records.append(record)
                continue
            spec = FactorSpec(kind="expression", expression=expression)
            if verbose:
                print(f"  [IS] grid: {expression}", flush=True)
            grid_result = grid.run_spec(spec)
            summary = grid_result.summary()
            record["is"] = {
                "n_evals": grid_result.n_evals,
                "metrics": grid_result.best.metrics,
                "config": summary.get("best"),
            }
        except Exception as exc:  # pragma: no cover - defensive
            record["error"] = f"{type(exc).__name__}: {exc}"
            records.append(record)
            continue

        stability = None
        try:
            attempt_like = {
                "hypothesis": candidate.get("expression_id"),
                "spec": spec.to_dict(),
                "grid": summary,
            }
            stability = stability_summary(panel_is, attempt_like)
            record["stability_is"] = stability
        except Exception as exc:  # pragma: no cover - defensive
            record["stability_error"] = f"{type(exc).__name__}: {exc}"

        review = critic.review(
            hypothesis,
            spec,
            grid_result,
            [],
            panel_is,
            max_rounds=max_rounds,
            stability=stability,
            extra={"evaluation_protocol": IS_PROTOCOL, "round": round_index},
        )
        record["decision"] = review.get("decision")
        record["reasoning"] = review.get("reasoning", "")
        record["review_source"] = review.get("source")
        record["suggested_changes"] = review.get("suggested_changes", [])
        revised = review.get("revised")
        if isinstance(revised, dict) and revised.get("expression"):
            record["revised_expression"] = str(revised["expression"])
            record["revised_explanation"] = revised.get("explanation", "")
        record["status"] = "evaluated"
        if verbose:
            print(f"    {record['decision']}: {str(record['reasoning'])[:120]}", flush=True)
        records.append(record)
    return records

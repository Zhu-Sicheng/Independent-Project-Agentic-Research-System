"""Agent 5a -- feedback channel back to the idea/implementation agents.

Every evaluated factor is written to the collaborator's ``ResearchMemory`` as a
``feedback`` record with in-sample metrics, stability flags and the reviewer
reasoning. Agent 3 reads these records in the next round. Out-of-sample numbers
never enter this payload.
"""

from __future__ import annotations

from pathlib import Path

from ..agent_adapter import ensure_agents_importable

def write_feedback(memory_db: Path, records: list[dict], run_id: str, research_end: str) -> int:
    """Append the in-sample evidence to the shared research memory.

    Agent 3 reads these records through ``search_memory`` on the next round and
    can revise the expressions accordingly. Only IS numbers are written.
    """
    ensure_agents_importable()
    from research.memory import ResearchMemory

    written = 0
    memory = ResearchMemory(memory_db)
    try:
        for record in records:
            if record.get("status") != "evaluated":
                continue
            is_metrics = ((record.get("is") or {}).get("metrics")) or {}
            stability = record.get("stability_is") or {}
            flags = ", ".join(stability.get("flags") or []) or "none"
            notes = (
                f"Expression: {record.get('expression')}. "
                f"Reviewer: {record.get('decision')} - {str(record.get('reasoning'))[:600]} "
                f"Stability flags: {flags}. These are in-sample numbers only; revise to "
                f"improve them and remove the flags. Do not assume any out-of-sample result."
            )
            payload = {
                # fields Agent 3's memory observation keeps in its prompt
                "evaluation_id": f"{record.get('expression_id')}_is_r{record.get('round', 0)}",
                "expression_id": record.get("expression_id"),
                "evaluation_end": research_end,
                "split": "development",
                "outcome": "inconclusive",
                "failure_type": flags,
                "metrics": {
                    key: is_metrics.get(key)
                    for key in (
                        "sharpe",
                        "ann_return",
                        "turnover",
                        "max_drawdown",
                        "rank_ic",
                        "pearson_ic",
                    )
                },
                "notes": notes,
                "verification": "ours_in_sample_backtest_and_stability",
                # extra provenance for our own tooling
                "stage": f"ours_is_evaluation_round_{record.get('round', 0)}",
                "expression": record.get("expression"),
                "in_sample": {
                    key: is_metrics.get(key)
                    for key in (
                        "sharpe",
                        "ann_return",
                        "ann_vol",
                        "turnover",
                        "max_drawdown",
                        "rank_ic",
                        "pearson_ic",
                    )
                },
                "stability": {
                    key: stability.get(key)
                    for key in (
                        "baseline_sharpe",
                        "subuniverse_sharpe",
                        "subuniverse_delta",
                        "decay_sharpe_span",
                        "transform_sharpe_span",
                        "window_sharpe_span",
                        "min_pnl_corr",
                        "flags",
                    )
                },
                "reviewer": {
                    "decision": record.get("decision"),
                    "reasoning": record.get("reasoning"),
                    "suggested_changes": record.get("suggested_changes", []),
                },
            }
            memory.append(
                kind="feedback",
                run_id=run_id,
                logical_id=f"{record.get('expression_id')}_is_feedback",
                dataset_id=record.get("_dataset_id") or "ds_market",
                family=record.get("_family") or "unknown",
                data_end=research_end,
                split="development",
                outcome="inconclusive",
                payload=payload,
            )
            written += 1
    finally:
        memory.close()
    return written

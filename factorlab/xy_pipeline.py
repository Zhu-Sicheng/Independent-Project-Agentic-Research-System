"""Merged pipeline: the collaborator's Agents 1-3 + our factor evaluation.

The three research agents (data understanding -> natural-language hypotheses ->
constrained expressions) come from ``factorlab/agents/agent{1,2,3}`` and the
shared ``research`` package. Everything after the expression is ours.

Data isolation (strict):

* **optimisation loop** -- the panel is cut at ``research_end`` (the in-sample
  end). The grid selects on in-sample Sharpe, the stability battery runs on the
  same IS panel, and the reviewer decides on IS evidence only. Out-of-sample and
  holdout dates never enter this loop; the agents only see IS metrics.
* **display layer** -- after the loop, the IS-chosen configuration is re-applied
  to the full panel. OOS/holdout metrics are computed here and are drawn in the
  figures, but they are never written back into any agent feedback.

Feedback to the agents: after each round, the in-sample evidence (metrics +
stability flags + the reviewer's reasoning) is appended to the shared research
memory database, which Agent 3 reads through ``search_memory`` when it revises
the expressions. In offline mode Agent 3 only emits fixed templates, so the
loop falls back to the reviewer's own ``optimize`` suggestion (sign flip /
smoothing) instead.

``python -m factorlab.xy_pipeline --mode offline --max-files 40 --max-evals 16``
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = PROJECT_ROOT / "factorlab" / "agents"
EXPERIMENTS = PROJECT_ROOT / "experiments"

# --------------------------------------------------------------------------- #
# layer boundaries: our Agent 4 (evaluation) and Agent 5 (feedback) modules
# --------------------------------------------------------------------------- #
from .agent_adapter import FIELD_MAP, ensure_agents_importable, translate_expression
from .agent4 import (
    IS_END_DEFAULT,
    IS_PROTOCOL,
    _canonical,
    _grid_settings,
    _load_factor,
    _slugify_title,
    display_evaluation,
    display_labels,
    evaluate_is_candidates,
    hypothesis_from_idea,
    split_is_panel,
)
from .agent5 import candidates_from_revisions, round_improved, write_feedback



def load_agent_document(name: str) -> dict:
    base = AGENTS_ROOT / f"{name}.example.json"
    return json.loads(base.read_text(encoding="utf-8-sig"))


def apply_llm_overrides(
    values: dict,
    max_turns: Optional[int] = None,
    max_tool_calls: Optional[int] = None,
    token_budget: Optional[int] = None,
) -> dict:
    """Point his LLM config at an OpenAI-compatible endpoint (DeepSeek/OpenAI).

    His examples default to Azure-style ``auth_header: api-key``; DeepSeek and
    OpenAI need ``Authorization: Bearer``. Chat-completion providers re-send the
    whole conversation on every turn, so the per-run token budget is the number
    that usually stops a run first; it is raised from the Azure-era default.
    """
    import os

    llm = dict(values.get("llm") or {})
    llm["auth_header"] = os.getenv("FACTORLAB_AGENT_AUTH_HEADER", "Authorization")
    llm["timeout_seconds"] = int(
        os.getenv("FACTORLAB_LLM_TIMEOUT", llm.get("timeout_seconds", 120))
    )
    llm.setdefault("max_retries", 2)
    llm["max_total_tokens"] = int(
        token_budget
        or os.getenv("FACTORLAB_AGENT_TOKEN_BUDGET", str(llm.get("max_total_tokens") or 400000))
    )
    if max_turns is not None:
        values["max_turns"] = int(max_turns)
    if max_tool_calls is not None:
        values["max_tool_calls"] = int(max_tool_calls)
    values["llm"] = llm
    return values


# --------------------------------------------------------------------------- #
# his agents
# --------------------------------------------------------------------------- #
def run_agent1(
    output_root: Path,
    data_root: Path,
    research_end: str,
    mode: str = "offline",
    max_files: int = 40,
    max_rows: int = 20000,
    plots: bool = False,
    llm_max_turns: Optional[int] = None,
    llm_tool_calls: Optional[int] = None,
    llm_token_budget: Optional[int] = None,
) -> tuple[Path, dict]:
    ensure_agents_importable()
    from agent1.agent import EDAAgent
    from agent1.core import Config, discover
    from agent1.llm import ChatClient
    from agent1.reporting import publish
    from agent1.runtime import RunContext, create_run_dir

    values = load_agent_document("agent1")
    if mode == "llm":
        values = apply_llm_overrides(values, llm_max_turns, llm_tool_calls, llm_token_budget)
    # his CLI resolves these two before validation; do the same for in-process use
    data_root = Path(data_root).resolve()
    output_root = Path(output_root).resolve()
    values.update(
        {
            "data_root": str(data_root),
            "output_root": str(output_root),
            "research_end": research_end,
            "mode": mode,
            "max_files_per_dataset": int(max_files),
            "max_rows_per_file": int(max_rows),
            "plots": bool(plots),
        }
    )
    config = Config.from_dict(values)
    manifest = discover(config)
    context = RunContext(config, manifest, create_run_dir(config))
    client = ChatClient(config.llm) if mode == "llm" else None
    EDAAgent(context, client).run()
    report = publish(context)
    return context.run_dir, report


def run_agent2(
    agent1_run: Path,
    output_root: Path,
    memory_db: Path,
    operator_file: Path,
    mode: str = "offline",
    min_ideas: int = 2,
    max_ideas: int = 6,
    max_ideas_per_dataset: int = 6,
    max_ideas_per_family: int = 2,
    knowledge_cutoff: Optional[str] = None,
    llm_max_turns: Optional[int] = None,
    llm_tool_calls: Optional[int] = None,
    llm_token_budget: Optional[int] = None,
) -> tuple[Path, dict]:
    ensure_agents_importable()
    from agent2.agent import IdeaAgent
    from research.common import IdeaConfig

    values = load_agent_document("agent2")
    if mode == "llm":
        values = apply_llm_overrides(values, llm_max_turns, llm_tool_calls, llm_token_budget)
    agent1_run = Path(agent1_run).resolve()
    output_root = Path(output_root).resolve()
    memory_db = Path(memory_db).resolve()
    operator_file = Path(operator_file).resolve()
    values.update(
        {
            "agent1_run": str(agent1_run),
            "output_root": str(output_root),
            "memory_db": str(memory_db),
            "operator_file": str(operator_file),
            "mode": mode,
            "min_ideas": int(min_ideas),
            "max_ideas": int(max_ideas),
            "max_ideas_per_dataset": int(max_ideas_per_dataset),
            "max_ideas_per_family": int(max_ideas_per_family),
            "knowledge_cutoff": knowledge_cutoff,
        }
    )
    config = IdeaConfig.from_dict(values)
    agent = IdeaAgent(config)
    result = agent.run()
    return agent.artifacts.root, result


def run_agent3(
    agent1_run: Path,
    agent2_run: Path,
    output_root: Path,
    memory_db: Path,
    operator_file: Path,
    mode: str = "offline",
    max_expressions_per_idea: int = 1,
    validation_max_files: int = 8,
    knowledge_cutoff: Optional[str] = None,
    llm_max_turns: Optional[int] = None,
    llm_tool_calls: Optional[int] = None,
    llm_token_budget: Optional[int] = None,
) -> tuple[Path, dict]:
    ensure_agents_importable()
    from agent3.agent import ExpressionAgent
    from research.common import ExpressionConfig

    values = load_agent_document("agent3")
    if mode == "llm":
        values = apply_llm_overrides(values, llm_max_turns, llm_tool_calls, llm_token_budget)
    agent1_run = Path(agent1_run).resolve()
    agent2_run = Path(agent2_run).resolve()
    output_root = Path(output_root).resolve()
    memory_db = Path(memory_db).resolve()
    operator_file = Path(operator_file).resolve()
    values.update(
        {
            "agent1_run": str(agent1_run),
            "agent2_run": str(agent2_run),
            "output_root": str(output_root),
            "memory_db": str(memory_db),
            "operator_file": str(operator_file),
            "mode": mode,
            "max_expressions_per_idea": int(max_expressions_per_idea),
            "max_attempts_per_idea": max(6, int(max_expressions_per_idea) * 2),
            "validation_max_files": int(validation_max_files),
            "allow_unapproved_dry_run": True,
            "knowledge_cutoff": knowledge_cutoff,
        }
    )
    config = ExpressionConfig.from_dict(values)
    agent = ExpressionAgent(config)
    result = agent.run()
    return agent.artifacts.root, result


def _json_safe(value):
    """Replace NaN/Inf with None so the record file is strict JSON."""
    import math

    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def evaluations_path(output_root: Path) -> Path:
    return Path(output_root) / "evaluations.json"


def load_incremental(path: Path) -> tuple[list[dict], set]:
    """Resume an existing run: previous records plus the canonical expressions."""
    from .xy_results import load_evaluations

    records = load_evaluations(path)
    seen = {
        _canonical(record["expression"])
        for record in records
        if record.get("expression")
    }
    return records, seen


def merge_records(previous: list[dict], new: list[dict]) -> list[dict]:
    """Append new records, dropping duplicates by canonical expression."""
    merged = list(previous)
    known = {
        _canonical(record["expression"])
        for record in previous
        if record.get("expression")
    }
    for record in new:
        expression = record.get("expression")
        if expression:
            canonical = _canonical(expression)
            if canonical in known:
                continue
            known.add(canonical)
        merged.append(record)
    return merged


# --------------------------------------------------------------------------- #
# orchestration
# --------------------------------------------------------------------------- #
def run_pipeline(
    mode: str = "offline",
    experiment_name: Optional[str] = None,
    max_files: int = 40,
    max_rows: int = 20000,
    plots: bool = False,
    research_end: str = IS_END_DEFAULT,
    max_evals: int = 16,
    max_expressions_per_idea: int = 1,
    rounds: int = 3,
    pnl_mode: str = "additive",
    agent_modes: Optional[dict] = None,
    min_ideas: int = 2,
    max_ideas: int = 6,
    max_ideas_per_dataset: int = 6,
    max_ideas_per_family: int = 2,
    llm_max_turns: Optional[int] = None,
    llm_tool_calls: Optional[int] = None,
    llm_token_budget: Optional[int] = None,
    incremental: bool = True,
    force: bool = False,
    data_root: Optional[Path] = None,
    panel_dir: Optional[Path] = None,
    run_id: Optional[str] = None,
    out_root: Optional[Path] = None,
    verbose: bool = True,
) -> dict:
    from factorlab.agents.critic import CriticAgent
    from factorlab.agents.llm import build_client
    from factorlab.backtest.grid import GridSearch
    from factorlab.config import BacktestSettings, GridConfig, LLMSettings
    from factorlab.data import load_processed
    from factorlab.expr.spec import FactorSpec
    from factorlab.markdown import md_table
    from factorlab.pool.pool import FactorPool

    modes = {"agent1": mode, "agent2": mode, "agent3": mode}
    modes.update(agent_modes or {})
    if any(value == "llm" for value in modes.values()):
        _export_agent_llm_env()

    started = time.time()
    run_id = run_id or time.strftime("%Y%m%d-%H%M%S-xy")
    if out_root is not None:
        output_root = Path(out_root) / run_id
    else:
        from .experiments_store import date_of, dated_experiment_dir, find_run_dir

        existing = find_run_dir(run_id)
        if existing is not None:
            output_root = existing
        else:
            slug = experiment_name or run_id.split("-", 2)[-1]
            output_root = dated_experiment_dir(slug, date_of(run_id))
    output_root.mkdir(parents=True, exist_ok=True)
    data_root = data_root or PROJECT_ROOT / "data" / "raw" / "data"
    panel_dir = panel_dir or PROJECT_ROOT / "data" / "processed" / "panel"
    operator_file = PROJECT_ROOT / "docs" / "ts_operators.md"
    memory_db = output_root / "research_memory.sqlite3"
    log: list[str] = []

    def say(message: str) -> None:
        log.append(message)
        if verbose:
            print(message, flush=True)

    say(f"run {run_id}: agents={modes}, max_rounds={rounds}, research_end={research_end}")
    say(f"data: {data_root}")

    # ---- his agents: data understanding + ideas (cutoff = IS end) ----
    agent1_dir, agent1_report = run_agent1(
        output_root / "agent1", data_root, research_end, mode=modes["agent1"],
        max_files=max_files, max_rows=max_rows, plots=plots,
        llm_max_turns=llm_max_turns, llm_tool_calls=llm_tool_calls,
        llm_token_budget=llm_token_budget,
    )
    say(f"agent1: {agent1_dir.name} status={agent1_report.get('status')}")
    agent2_dir, agent2_result = run_agent2(
        agent1_dir, output_root / "agent2", memory_db, operator_file,
        mode=modes["agent2"], min_ideas=min_ideas, max_ideas=max_ideas,
        max_ideas_per_dataset=max_ideas_per_dataset,
        max_ideas_per_family=max_ideas_per_family,
        llm_max_turns=llm_max_turns, llm_tool_calls=llm_tool_calls,
        llm_token_budget=llm_token_budget,
    )
    ideas_list = agent2_result.get("ideas", [])
    ideas = {idea["idea_id"]: idea for idea in ideas_list}
    say(f"agent2: {agent2_dir.name} status={agent2_result.get('status')} ideas={len(ideas_list)}")

    # ---- our in-sample-only optimisation loop ----
    panel_full = load_processed(panel_dir)
    panel_is = split_is_panel(panel_full, research_end)
    say(f"panel: full {panel_full.shape} -> IS only {panel_is.shape} (cut at {research_end})")
    grid = GridSearch(
        panel_is, GridConfig(max_evals=max_evals), BacktestSettings(pnl_mode=pnl_mode), split=None
    )
    critic = CriticAgent(build_client(LLMSettings.from_env()))

    agent3_runs: list[str] = []
    eval_path = evaluations_path(output_root)
    previous_records: list[dict] = []
    seen: set[str] = set()
    if incremental and not force:
        previous_records, seen = load_incremental(eval_path)
        if previous_records:
            say(
                f"incremental: resumed {len(previous_records)} previous evaluations "
                f"({len(seen)} expressions already known)"
            )
    records: list[dict] = list(previous_records)
    candidates: list[dict] = []
    agent3_result: dict = {}

    def annotate(new_records: list[dict]) -> None:
        for record in new_records:
            idea = ideas.get(record.get("idea_id", ""), {})
            record["_dataset_id"] = idea.get("dataset_id", "ds_market")
            record["_family"] = idea.get("family", "unknown")

    round_index = 0
    best_is_sharpe = float("-inf")
    stop_reason = "max_rounds_reached"
    round_history: list[dict] = []
    max_rounds = max(1, rounds)
    feedback_mode = modes["agent3"] == "llm"
    pending_revisions: list[dict] = []

    while round_index < max_rounds:
        if pending_revisions:
            candidates = pending_revisions
            pending_revisions = []
            say(f"round {round_index}: {len(candidates)} reviewer revisions (no Agent 3 call)")
        else:
            say(f"round {round_index}: agent3 ({modes['agent3']}) ...")
            agent3_dir, agent3_result = run_agent3(
                agent1_dir, agent2_dir, output_root / f"agent3_round{round_index}",
                memory_db, operator_file, mode=modes["agent3"],
                max_expressions_per_idea=max_expressions_per_idea,
                llm_max_turns=llm_max_turns, llm_tool_calls=llm_tool_calls,
                llm_token_budget=llm_token_budget,
            )
            agent3_runs.append(str(agent3_dir))
            candidates = agent3_result.get("expressions", [])
            say(
                f"round {round_index}: agent3 {agent3_dir.name} status={agent3_result.get('status')} "
                f"expressions={len(candidates)}"
            )
        for candidate in candidates:
            idea = ideas.get(candidate.get("idea_id", ""), {})
            candidate.setdefault("_dataset_id", idea.get("dataset_id"))
            candidate.setdefault("_family", idea.get("family"))
        new_records = evaluate_is_candidates(
            panel_is, candidates, ideas, seen, run_id, round_index, grid, critic,
            max_rounds=max_rounds, verbose=verbose,
        )
        annotate(new_records)
        records.extend(new_records)
        evaluated = [
            record
            for record in new_records
            if record.get("status") == "evaluated"
            and isinstance((record.get("is") or {}).get("metrics", {}).get("sharpe"), (int, float))
        ]
        round_best = max(
            ((record["is"]["metrics"]["sharpe"] for record in evaluated)), default=float("-inf")
        )
        improved = round_improved(round_best, best_is_sharpe)
        if improved:
            best_is_sharpe = round_best
        round_history.append(
            {
                "round": round_index,
                "candidates": len(candidates),
                "new_evaluations": len(evaluated),
                "round_best_is_sharpe": None if round_best == float("-inf") else round_best,
                "improved": improved,
            }
        )
        say(
            f"round {round_index}: {len(new_records)} new evaluations (IS only); "
            f"round best IS Sharpe {round_best if round_best != float('-inf') else float('nan'):.3f}"
        )

        if not candidates:
            stop_reason = "no_candidates"
            say(f"round {round_index}: no candidates; stopping")
            break
        if round_index + 1 >= max_rounds:
            stop_reason = "max_rounds_reached"
            break

        if feedback_mode:
            written = write_feedback(memory_db, new_records, run_id, research_end)
            say(f"round {round_index}: wrote {written} in-sample feedback records to memory")
            round_index += 1
            continue
        # offline: chain the reviewer's own revisions, one per round
        pending_revisions = candidates_from_revisions(new_records)
        if not pending_revisions:
            stop_reason = "no_offline_revisions"
            say(f"round {round_index}: no offline revisions; stopping the loop")
            break
        say(
            f"round {round_index}: {len(pending_revisions)} reviewer revisions queued "
            f"for round {round_index + 1}"
        )
        round_index += 1

    # ---- display layer: OOS/holdout computed and drawn here, never fed back ----
    labels = display_labels(ideas, records)
    records = display_evaluation(
        panel_full, records, run_id, output_root, verbose=verbose,
        only_missing=incremental and not force, labels=labels, pnl_mode=pnl_mode,
    )
    from .xy_results import EVENTS_PATH, record_events, rebuild_index, upsert_evaluations

    store_stats = upsert_evaluations(eval_path, records, run_id)
    events_written = record_events(EVENTS_PATH, run_id, records)
    index_stats = rebuild_index()
    say(
        f"results store: inserted {store_stats['inserted']}, updated {store_stats['updated']}, "
        f"unchanged {store_stats['unchanged']}; {events_written} events; "
        f"index {index_stats['n_records']} records"
    )

    # ---- factor pool for accepted candidates (IS-selected configuration) ----
    pool = FactorPool(output_root / "pool")
    accepted = 0
    for record in records:
        if record.get("decision") != "accept" or not record.get("expression"):
            continue
        try:
            spec = FactorSpec(kind="expression", expression=record["expression"])
            hypothesis = hypothesis_from_idea(ideas.get(record.get("idea_id", ""), {}))
            grid_result = grid.run_spec(spec)
            display = record.get("display") or {}
            rec = pool.add(
                spec=spec,
                hypothesis=hypothesis,
                grid=grid_result,
                run_id=run_id,
                name=f"{hypothesis.get('family') or 'xy'}_{record['expression_id']}",
                tags=["xy_agent2", record.get("review_source", "unknown")],
                notes=(
                    f"IS-only decision ({record.get('round')} rounds). "
                    f"Display: OOS {display.get('oos_sharpe')}, "
                    f"holdout {display.get('holdout_sharpe')} (presentation only)."
                ),
            )
            record["factor_id"] = rec.id
            accepted += 1
        except Exception as exc:  # pragma: no cover - defensive
            record["pool_error"] = f"{type(exc).__name__}: {exc}"

    summary = {
        "run_id": run_id,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "elapsed_s": round(time.time() - started, 1),
        "mode": mode,
        "agent_modes": modes,
        "max_rounds": max_rounds,
        "stop_reason": stop_reason,
        "round_history": round_history,
        "incremental": {
            "enabled": bool(incremental and not force),
            "previous_evaluations": len(previous_records),
            "total_evaluations": sum(1 for r in records if r.get("status") == "evaluated"),
        },
        "results_store": {**store_stats, "events_written": events_written, **index_stats},
        "research_end": research_end,
        "data_isolation": {
            "optimisation": "in-sample only (panel cut at research_end; grid selects on IS)",
            "stability_loop": "in-sample panel",
            "display": "full panel; OOS/holdout metrics and figures only",
        },
        "agent1_run": str(agent1_dir),
        "agent2_run": str(agent2_dir),
        "agent3_runs": agent3_runs,
        "agent1_status": agent1_report.get("status"),
        "agent2_status": agent2_result.get("status"),
        "agent3_status": agent3_result.get("status"),
        "n_ideas": len(ideas_list),
        "n_evaluated": sum(1 for r in records if r.get("status") == "evaluated"),
        "n_displayed": sum(1 for r in records if r.get("display")),
        "n_accepted": accepted,
        "n_rounds_run": len(agent3_runs),
        "panel_is": list(panel_is.shape),
        "panel_full": list(panel_full.shape),
    }
    (output_root / "run.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    def _fmt(value) -> str:
        if value is None:
            return "-"
        try:
            return f"{float(value):.3f}"
        except (TypeError, ValueError):
            return str(value)

    is_rows, display_rows = [], []
    for record in records:
        metrics = ((record.get("is") or {}).get("metrics")) or {}
        stability = record.get("stability_is") or {}
        is_rows.append(
            {
                "round": record.get("round"),
                "expression": f"`{str(record.get('expression', record.get('expression_raw', '')))[:60]}`",
                "sharpe_is": _fmt(metrics.get("sharpe")),
                "ann_is": _fmt(metrics.get("ann_return")),
                "turnover_is": _fmt(metrics.get("turnover")),
                "rank_ic_is": _fmt(metrics.get("rank_ic")),
                "stability_flags": ", ".join(stability.get("flags") or []) or "-",
                "decision": record.get("decision") or "-",
                "error": (record.get("error") or "")[:80],
            }
        )
        display = record.get("display") or {}
        segments = display.get("segments") or {}
        display_rows.append(
            {
                "expression": f"`{str(record.get('expression', record.get('expression_raw', '')))[:60]}`",
                "IS": _fmt((segments.get("is") or {}).get("sharpe")),
                "OOS": _fmt((segments.get("oos") or {}).get("sharpe")),
                "holdout": _fmt((segments.get("holdout") or {}).get("sharpe")),
                "figure": f"`{display.get('figure', '')}`" if display.get("figure") else "-",
            }
        )

    lines = [
        f"# Merged pipeline run `{run_id}`",
        "",
        f"- agent modes: {modes}; max feedback rounds: {max_rounds}; "
        f"stopped: `{stop_reason}`; elapsed {summary['elapsed_s']}s",
        f"- incremental: {summary['incremental']['enabled']} "
        f"(resumed {summary['incremental']['previous_evaluations']} evaluations, "
        f"{summary['incremental']['total_evaluations']} total); "
        f"results store: inserted {summary['results_store']['inserted']}, "
        f"updated {summary['results_store']['updated']}, "
        f"index {summary['results_store']['n_records']} records",
        f"- **data isolation**: the optimisation loop sees **in-sample only** "
        f"(panel cut at {research_end}, {panel_is.shape[0]} of {panel_full.shape[0]} days); "
        f"OOS/holdout are computed only in the display layer below",
        f"- agent1: `{agent1_dir}` (status {summary['agent1_status']})",
        f"- agent2: `{agent2_dir}` (status {summary['agent2_status']}, {summary['n_ideas']} ideas)",
        f"- agent3 runs: {len(agent3_runs)}; evaluated: {summary['n_evaluated']}; "
        f"accepted: {summary['n_accepted']}; displayed: {summary['n_displayed']}",
        "",
        "## Optimisation evidence (in-sample only; what the agents and reviewer see)",
        "",
        md_table(is_rows),
        "",
        "## Display layer (OOS/holdout computed after the loop; presentation only)",
        "",
        md_table(display_rows),
        "",
        "## Feedback rounds (in-sample only; early stop = no improvement)",
        "",
        md_table(round_history) if round_history else "_none_",
        "",
        "## Agent logs",
        "",
    ] + [f"- {entry}" for entry in log]
    (output_root / "report.md").write_text("\n".join(lines), encoding="utf-8")
    say(f"written: {output_root / 'report.md'}")
    return summary


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["offline", "llm"], default="offline",
                        help="default mode for all three agents")
    parser.add_argument("--agent1-mode", choices=["offline", "llm"], default=None)
    parser.add_argument("--agent2-mode", choices=["offline", "llm"], default=None)
    parser.add_argument("--agent3-mode", choices=["offline", "llm"], default=None)
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--panel", default=None)
    parser.add_argument("--out-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--experiment-name", default=None,
                        help="slug for experiments/<YYYYMMDD>-<slug>/ (default: run id tag)")
    parser.add_argument(
        "--research-end", default=IS_END_DEFAULT,
        help="in-sample end; the optimisation loop never sees dates after it",
    )
    parser.add_argument("--rounds", type=int, default=3, help="feedback rounds to run")
    parser.add_argument("--pnl-mode", choices=("additive", "compound"), default="additive",
                        help="cumulative pnl convention (default: additive cumsum)")
    parser.add_argument("--incremental", dest="incremental", action="store_true", default=True,
                        help="resume an existing run and only evaluate new expressions (default)")
    parser.add_argument("--no-incremental", dest="incremental", action="store_false",
                        help="recompute every expression from scratch")
    parser.add_argument("--force", action="store_true",
                        help="re-evaluate records that already exist (implies no resume)")
    parser.add_argument("--min-ideas", type=int, default=2)
    parser.add_argument("--max-ideas", type=int, default=6)
    parser.add_argument("--max-ideas-per-dataset", type=int, default=6)
    parser.add_argument("--max-ideas-per-family", type=int, default=2)
    parser.add_argument("--llm-max-turns", type=int, default=None, help="per-agent turn cap in LLM mode")
    parser.add_argument("--llm-tool-calls", type=int, default=None, help="per-agent tool-call cap in LLM mode")
    parser.add_argument("--llm-token-budget", type=int, default=None,
                        help="per-run reported-token budget (chat APIs resend the context each turn)")
    parser.add_argument("--max-files", type=int, default=40, help="Agent-1 per-dataset file cap (0 = all)")
    parser.add_argument("--max-rows", type=int, default=20000)
    parser.add_argument("--max-evals", type=int, default=16)
    parser.add_argument("--max-expressions-per-idea", type=int, default=1)
    parser.add_argument("--plots", action="store_true")
    args = parser.parse_args(argv)
    agent_modes = {
        name: value
        for name, value in (
            ("agent1", args.agent1_mode),
            ("agent2", args.agent2_mode),
            ("agent3", args.agent3_mode),
        )
        if value
    }
    if args.mode == "llm" or any(value == "llm" for value in agent_modes.values()):
        _export_agent_llm_env()
    summary = run_pipeline(
        mode=args.mode,
        max_files=args.max_files,
        max_rows=args.max_rows,
        plots=args.plots,
        research_end=args.research_end,
        max_evals=args.max_evals,
        max_expressions_per_idea=args.max_expressions_per_idea,
        rounds=args.rounds,
        pnl_mode=args.pnl_mode,
        incremental=args.incremental,
        force=args.force,
        agent_modes=agent_modes,
        min_ideas=args.min_ideas,
        max_ideas=args.max_ideas,
        max_ideas_per_dataset=args.max_ideas_per_dataset,
        max_ideas_per_family=args.max_ideas_per_family,
        llm_max_turns=args.llm_max_turns,
        llm_tool_calls=args.llm_tool_calls,
        llm_token_budget=args.llm_token_budget,
        data_root=Path(args.data_root) if args.data_root else None,
        panel_dir=Path(args.panel) if args.panel else None,
        run_id=args.run_id,
        experiment_name=args.experiment_name,
        out_root=Path(args.out_root) if args.out_root else None,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def _export_agent_llm_env() -> None:
    """Map our DeepSeek/OpenAI credentials to the AGENTn_* variables."""
    from factorlab.config import LLMSettings

    settings = LLMSettings.from_env()
    key = os.getenv(settings.api_key_env) if settings.api_key_env else ""
    if not key:
        key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    base = settings.base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = settings.model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    for index in (1, 2, 3):
        os.environ[f"AGENT{index}_BASE_URL"] = base
        os.environ[f"AGENT{index}_API_KEY"] = key
        os.environ[f"AGENT{index}_MODEL"] = model


if __name__ == "__main__":
    main()

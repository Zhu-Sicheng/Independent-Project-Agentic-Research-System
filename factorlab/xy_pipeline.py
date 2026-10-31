"""Merged pipeline: the collaborator's Agents 1-3 + our factor evaluation.

The three research agents (data understanding -> natural-language hypotheses ->
constrained expressions) come from ``factorlab/agents/agent{1,2,3}`` and the
shared ``research`` package. They produce expressions; everything after that
(backtest grid, IS/OOS/holdout split, stability battery, factor pool, reviewer)
is ours.

Flow::

    agent1 (EDA, data contract)  -> agent2 (ideas.json) -> agent3 (expressions.json)
        -> translate contract field names to panel fields
        -> our GridSearch (decay / transform / cap filter / windows, IS selection)
        -> our stability battery
        -> our reviewer (accept / optimize / abandon) -> our factor pool

``python -m factorlab.xy_pipeline --mode offline --max-files 40 --max-evals 24``
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Iterable, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = PROJECT_ROOT / "factorlab" / "agents"
EXPERIMENTS = PROJECT_ROOT / "experiments" / "xy"

#: mapping from the raw column names Agent 1 sees to our panel fields
FIELD_MAP: dict[str, str] = {
    "Adj_Open": "open",
    "Adj_High": "high",
    "Adj_Low": "low",
    "Adj_Close": "close",
    "Adj_Volume": "volume",
    "Adj_MktCap": "cap",
    "DlyOpen": "open",
    "DlyHigh": "high",
    "DlyLow": "low",
    "DlyClose": "close",
    "DlyPrc": "close",
    "DlyVol": "volume",
    "DlyCap": "cap",
    "Close": "close",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Volume": "volume",
    "MarketCap": "cap",
    "market_cap": "cap",
    "close": "close",
    "open": "open",
    "high": "high",
    "low": "low",
    "volume": "volume",
    "cap": "cap",
    "returns": "returns",
    "log_returns": "log_returns",
    "amount": "amount",
    "adv20": "adv20",
    "cap_rank": "cap_rank",
    "range": "range",
    "close_position": "close_position",
    "intraday_return": "intraday_return",
    "overnight_return": "overnight_return",
}

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_FIELD_CALL_RE = re.compile(r'field\(\s*"([^"]+)"\s*\)')


def ensure_agents_importable() -> None:
    """His modules import ``agent1.core`` / ``research.common`` absolutely."""
    if str(AGENTS_ROOT) not in sys.path:
        sys.path.insert(0, str(AGENTS_ROOT))


def translate_expression(expression: str) -> str:
    """Rewrite Agent-3 contract field names into our panel field names."""

    def field_call(match: re.Match) -> str:
        name = match.group(1)
        if name not in FIELD_MAP:
            raise KeyError(f"field {name!r} has no panel mapping")
        return FIELD_MAP[name]

    def identifier(match: re.Match) -> str:
        token = match.group(0)
        return FIELD_MAP.get(token, token)

    rewritten = _FIELD_CALL_RE.sub(field_call, expression)
    return _IDENT_RE.sub(identifier, rewritten)


def load_agent_document(name: str) -> dict:
    base = AGENTS_ROOT / f"{name}.example.json"
    return json.loads(base.read_text(encoding="utf-8-sig"))


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
) -> tuple[Path, dict]:
    ensure_agents_importable()
    from agent1.agent import EDAAgent
    from agent1.core import Config, discover
    from agent1.llm import ChatClient
    from agent1.reporting import publish
    from agent1.runtime import RunContext, create_run_dir

    values = load_agent_document("agent1")
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
    knowledge_cutoff: Optional[str] = None,
) -> tuple[Path, dict]:
    ensure_agents_importable()
    from agent2.agent import IdeaAgent
    from research.common import IdeaConfig

    values = load_agent_document("agent2")
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
) -> tuple[Path, dict]:
    ensure_agents_importable()
    from agent3.agent import ExpressionAgent
    from research.common import ExpressionConfig

    values = load_agent_document("agent3")
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


# --------------------------------------------------------------------------- #
# our evaluation
# --------------------------------------------------------------------------- #
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


def evaluate_candidates(
    panel,
    candidates: Iterable[dict],
    ideas: dict,
    run_id: str,
    output_root: Path,
    max_evals: int = 24,
    max_rounds: int = 1,
    run_stability_checks: bool = True,
    verbose: bool = True,
) -> list[dict]:
    """Run every accepted Agent-3 expression through our grid, stability and reviewer."""
    from factorlab.agents.critic import CriticAgent
    from factorlab.agents.llm import build_client
    from factorlab.backtest.grid import GridSearch
    from factorlab.config import BacktestSettings, GridConfig, LLMSettings, US_EQUITY_SPLIT
    from factorlab.expr.spec import FactorSpec
    from factorlab.expr.validate import validate_expression
    from factorlab.pool.pool import FactorPool
    from factorlab.stability import run_stability, stability_summary

    grid_config = GridConfig(max_evals=max_evals)
    grid = GridSearch(panel, grid_config, BacktestSettings(), split=US_EQUITY_SPLIT)
    critic = CriticAgent(build_client(LLMSettings.from_env()))
    pool = FactorPool(output_root / "pool")

    records: list[dict] = []
    for candidate in candidates:
        status = str(candidate.get("status", ""))
        if not (candidate.get("ready_for_agent4_factor_evaluation") or status.startswith("research_validated")):
            continue
        idea = ideas.get(candidate["idea_id"], {})
        hypothesis = hypothesis_from_idea(idea)
        record = {
            "expression_id": candidate["expression_id"],
            "idea_id": candidate["idea_id"],
            "hypothesis": hypothesis["name"],
            "expression_raw": candidate["expression"],
            "status": "rejected_before_backtest",
        }
        rows: list[dict] = []
        try:
            expression = translate_expression(candidate["expression"])
            record["expression"] = expression
            # Agent 3 may use any integer lookback (its budget allows 1..252); keep
            # those windows as given instead of forcing our grid horizons.
            report = validate_expression(expression, panel, strict_windows=False, min_window=1)
            if not report.ok:
                record["error"] = "; ".join(report.errors)
                records.append(record)
                continue
            spec = FactorSpec(kind="expression", expression=expression)
            if verbose:
                print(f"  grid: {expression}", flush=True)
            grid_result = grid.run_spec(spec)
            grid_summary = grid_result.summary()
            record["grid"] = {
                "n_evals": grid_result.n_evals,
                "best": grid_result.best.metrics,
                "in_sample": (grid_result.best.segments or {}).get("in_sample"),
                "out_of_sample": (grid_result.best.segments or {}).get("oos"),
                "holdout": (grid_result.best.segments or {}).get("holdout"),
                "config": {
                    key: grid_summary.get("best", {}).get(key)
                    for key in ("decay", "transform", "cap_filter", "windows")
                },
            }
        except Exception as exc:  # pragma: no cover - defensive
            record["error"] = f"{type(exc).__name__}: {exc}"
            records.append(record)
            continue

        # stability battery (same signal, different implementation knobs)
        stability = None
        try:
            attempt_like = {
                # keep the plot title ASCII: Agent-2 titles are Chinese and the
                # plotting font has no CJK glyphs
                "hypothesis": candidate["expression_id"],
                "spec": spec.to_dict(),
                "grid": grid_summary,
            }
            stability = stability_summary(panel, attempt_like)
            record["stability"] = stability
            if run_stability_checks:
                stability_dir = output_root / "stability" / candidate["expression_id"]
                run_stability(panel, attempt_like, run_id, out_dir=stability_dir)
                record["stability_dir"] = str(stability_dir)
        except Exception as exc:  # pragma: no cover - defensive
            record["stability_error"] = f"{type(exc).__name__}: {exc}"

        review = critic.review(
            hypothesis,
            spec,
            grid_result,
            [],
            panel,
            max_rounds=max_rounds,
            stability=stability,
        )
        record["decision"] = review.get("decision")
        record["reasoning"] = review.get("reasoning", "")
        record["review_source"] = review.get("source")
        record["status"] = "evaluated"

        if review.get("decision") == "accept":
            rec = pool.add(
                spec=spec,
                hypothesis=hypothesis,
                grid=grid_result,
                run_id=run_id,
                name=f"{hypothesis.get('family') or 'xy'}_{candidate['expression_id']}",
                tags=["xy_agent2", review.get("source", "unknown")],
                notes=review.get("reasoning", ""),
            )
            record["factor_id"] = rec.id
            if verbose:
                print(f"    accepted -> {rec.id}", flush=True)
        elif verbose:
            print(f"    {review.get('decision')}: {record['reasoning'][:120]}", flush=True)
        records.append(record)

    return records


# --------------------------------------------------------------------------- #
# orchestration
# --------------------------------------------------------------------------- #
def run_pipeline(
    mode: str = "offline",
    max_files: int = 40,
    max_rows: int = 20000,
    plots: bool = False,
    research_end: str = "2020-12-31",
    max_evals: int = 24,
    max_expressions_per_idea: int = 1,
    run_stability_checks: bool = True,
    data_root: Optional[Path] = None,
    panel_dir: Optional[Path] = None,
    run_id: Optional[str] = None,
    out_root: Optional[Path] = None,
    verbose: bool = True,
) -> dict:
    from factorlab.data import load_processed
    from factorlab.markdown import md_table

    started = time.time()
    run_id = run_id or time.strftime("%Y%m%d-%H%M%S-xy")
    output_root = (out_root or EXPERIMENTS) / run_id
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

    say(f"run {run_id}: mode={mode}, data={data_root}")
    # ---- his agents ----
    agent1_dir, agent1_report = run_agent1(
        output_root / "agent1", data_root, research_end, mode=mode,
        max_files=max_files, max_rows=max_rows, plots=plots,
    )
    say(f"agent1: {agent1_dir} status={agent1_report.get('status')}")

    agent2_dir, agent2_result = run_agent2(
        agent1_dir, output_root / "agent2", memory_db, operator_file, mode=mode,
    )
    say(f"agent2: {agent2_dir} status={agent2_result.get('status')} ideas={len(agent2_result.get('ideas', []))}")

    agent3_dir, agent3_result = run_agent3(
        agent1_dir, agent2_dir, output_root / "agent3", memory_db, operator_file,
        mode=mode, max_expressions_per_idea=max_expressions_per_idea,
    )
    say(
        f"agent3: {agent3_dir} status={agent3_result.get('status')} "
        f"expressions={len(agent3_result.get('expressions', []))}"
    )

    # ---- our evaluation ----
    panel = load_processed(panel_dir)
    ideas = {idea["idea_id"]: idea for idea in agent2_result.get("ideas", [])}
    records = evaluate_candidates(
        panel,
        agent3_result.get("expressions", []),
        ideas,
        run_id,
        output_root,
        max_evals=max_evals,
        run_stability_checks=run_stability_checks,
        verbose=verbose,
    )

    (output_root / "evaluations.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    summary = {
        "run_id": run_id,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "elapsed_s": round(time.time() - started, 1),
        "mode": mode,
        "agent1_run": str(agent1_dir),
        "agent2_run": str(agent2_dir),
        "agent3_run": str(agent3_dir),
        "agent1_status": agent1_report.get("status"),
        "agent2_status": agent2_result.get("status"),
        "agent3_status": agent3_result.get("status"),
        "n_ideas": len(agent2_result.get("ideas", [])),
        "n_expressions": len(agent3_result.get("expressions", [])),
        "n_evaluated": sum(1 for r in records if r.get("status") == "evaluated"),
        "n_accepted": sum(1 for r in records if r.get("factor_id")),
    }
    (output_root / "run.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Merged pipeline run `{run_id}`",
        "",
        f"- mode: `{mode}`; elapsed {summary['elapsed_s']}s",
        f"- agent1: `{agent1_dir}` (status {summary['agent1_status']})",
        f"- agent2: `{agent2_dir}` (status {summary['agent2_status']}, {summary['n_ideas']} ideas)",
        f"- agent3: `{agent3_dir}` (status {summary['agent3_status']}, {summary['n_expressions']} expressions)",
        f"- evaluated: {summary['n_evaluated']}; accepted into the pool: {summary['n_accepted']}",
        "",
        "## Evaluated expressions",
        "",
    ]
    table_rows = []
    for record in records:
        best = (record.get("grid") or {}).get("best") or {}
        oos = (record.get("grid") or {}).get("out_of_sample") or {}
        table_rows.append(
            {
                "idea": record.get("idea_id"),
                "expression": f"`{str(record.get('expression', record.get('expression_raw', '')))[:70]}`",
                "sharpe": best.get("sharpe"),
                "ann_return": best.get("ann_return"),
                "turnover": best.get("turnover"),
                "sharpe_oos": oos.get("sharpe") if isinstance(oos, dict) else None,
                "decision": record.get("decision"),
                "error": record.get("error", ""),
            }
        )
    lines.append(md_table(table_rows))
    lines += ["", "## Agent logs", ""] + [f"- {entry}" for entry in log]
    (output_root / "report.md").write_text("\n".join(lines), encoding="utf-8")
    say(f"written: {output_root / 'report.md'}")
    return summary


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
        os.environ.setdefault(f"AGENT{index}_BASE_URL", base)
        os.environ.setdefault(f"AGENT{index}_API_KEY", key)
        os.environ.setdefault(f"AGENT{index}_MODEL", model)


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["offline", "llm"], default="offline")
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--panel", default=None)
    parser.add_argument("--out-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--research-end", default="2020-12-31")
    parser.add_argument("--max-files", type=int, default=40, help="Agent-1 per-dataset file cap (0 = all)")
    parser.add_argument("--max-rows", type=int, default=20000)
    parser.add_argument("--max-evals", type=int, default=24)
    parser.add_argument("--max-expressions-per-idea", type=int, default=1)
    parser.add_argument("--plots", action="store_true")
    parser.add_argument("--no-stability", action="store_true")
    args = parser.parse_args(argv)
    if args.mode == "llm":
        _export_agent_llm_env()
    summary = run_pipeline(
        mode=args.mode,
        max_files=args.max_files,
        max_rows=args.max_rows,
        plots=args.plots,
        research_end=args.research_end,
        max_evals=args.max_evals,
        max_expressions_per_idea=args.max_expressions_per_idea,
        run_stability_checks=not args.no_stability,
        data_root=Path(args.data_root) if args.data_root else None,
        panel_dir=Path(args.panel) if args.panel else None,
        run_id=args.run_id,
        out_root=Path(args.out_root) if args.out_root else None,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

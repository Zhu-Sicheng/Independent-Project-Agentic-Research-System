"""Expression specialist. Implements ideas without inventing data or backtest results."""

from __future__ import annotations

import collections
import difflib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from agent1.core import dump_json, read_json, sha256_file
from agent1.llm import ChatClient
from research.common import Artifacts, EDABundle, ExpressionConfig, PROJECT_ROOT, digest, latest_run, string_list, text
from research.expressions import ExpressionCompiler
from research.loop import run_loop, tool
from research.memory import ResearchMemory
from research.operators import OperatorRegistry
from research.priors import expression_templates
from research.validation import FactorValidator, export_preview, write_expression_job


class ExpressionAgent:
    def __init__(self, config: ExpressionConfig, client=None):
        self.config = config
        config.validate()
        self.client = client or (ChatClient(config.llm) if config.mode == "llm" else None)
        self.bundle = EDABundle(config.agent1_run)
        self.idea_root = latest_run("agent2") if config.agent2_run == "latest" else Path(config.agent2_run).resolve()
        self.upstream = read_json(self.idea_root / "ideas.json")
        if self.upstream.get("status") != "completed" or self.upstream.get("source_agent1_run_id") != self.bundle.run_id or self.upstream.get("research_end") != self.bundle.research_end:
            raise ValueError("Agent 2 must be completed and reference this exact Agent 1 run/cutoff")
        if read_json(self.idea_root / "input_snapshot.json")["sha256"] != self.bundle.fingerprints:
            raise ValueError("Agent 1 artifacts changed after hypothesis generation")
        self.ideas = {idea["idea_id"]: idea for idea in self.upstream["ideas"]}
        if len(self.ideas) != len(self.upstream["ideas"]) or not self.ideas:
            raise ValueError("Agent 2 ideas must be nonempty and uniquely identified")
        self.registry = OperatorRegistry(config.operator_file)
        if self.upstream.get("operator_fingerprint") != self.registry.fingerprint:
            raise ValueError("Operator capabilities changed after Agent 2; regenerate hypotheses with current capabilities")
        self.compiler = ExpressionCompiler(self.registry, config)
        self.validator = FactorValidator(self.bundle, self.registry, config)
        self.artifacts = Artifacts("agent3", config, self.bundle)
        dump_json(self.artifacts.root / "ideas_input.json", self.upstream)
        dump_json(self.artifacts.root / "agent2_snapshot.json", {"agent2_run": str(self.idea_root), "ideas_sha256": sha256_file(self.idea_root / "ideas.json")})
        self.memory = ResearchMemory(config.memory_db)
        self.snapshot = self.memory.snapshot(self.bundle.research_end, config.knowledge_cutoff or self.artifacts.started_at, config.memory_limit)
        dump_json(self.artifacts.root / "memory_snapshot.json", self.snapshot.as_dict())
        dump_json(self.artifacts.root / "operator_registry.json", self.registry.describe())
        self.candidates, self.attempts, self.dispositions, self.followups = [], [], {}, []
        self.accepted_panels = {}
        self.finished = False
        self.llm_status = "not_requested" if config.mode == "offline" else "pending"
        self.prompt = (PROJECT_ROOT / "prompts" / "agent3_system.md").read_text(encoding="utf-8")
        (self.artifacts.root / "agent_system_prompt.md").write_text(self.prompt, encoding="utf-8")
        self.artifacts.state("running")

    def idea(self, identity):
        if identity not in self.ideas:
            raise ValueError("Unknown idea_id")
        return self.ideas[identity]

    def remember_failed_attempt(self, idea, attempt, outcome="implementation_error"):
        self.memory.append(kind="attempt", run_id=self.artifacts.run_id, logical_id=attempt["attempt_id"],
            dataset_id=idea["dataset_id"], family=idea["family"], data_end=self.bundle.research_end, outcome=outcome,
            payload={**attempt, "interpretation": "Implementation/numerical evidence only; this does not refute the economic hypothesis."})

    def construct(self, arguments):
        required = {"idea_id", "expression", "construction_rationale", "alignment_explanation"}
        if set(arguments) != required:
            raise ValueError(f"Expression proposal requires exactly {sorted(required)}")
        idea = self.idea(arguments["idea_id"])
        if idea["idea_id"] in self.dispositions:
            raise ValueError("This idea was already explicitly deferred")
        used = sum(attempt["idea_id"] == idea["idea_id"] for attempt in self.attempts)
        accepted = [candidate for candidate in self.candidates if candidate["idea_id"] == idea["idea_id"]]
        if used >= self.config.max_attempts_per_idea or len(accepted) >= self.config.max_expressions_per_idea:
            raise ValueError("Per-idea attempt/expression budget exhausted")
        attempt = {"attempt_id": f"attempt_{len(self.attempts) + 1:03d}", "idea_id": idea["idea_id"],
                   "expression": str(arguments.get("expression", ""))[:1200]}
        self.attempts.append(attempt)
        try:
            rationale = text(arguments["construction_rationale"], "construction_rationale")
            alignment = text(arguments["alignment_explanation"], "alignment_explanation")
            compiled = self.compiler.compile(arguments["expression"], self.bundle.fields[idea["dataset_id"]], idea["required_fields"])
            if compiled.info.fields != set(idea["required_fields"]):
                raise ValueError("Every required hypothesis field must be used; do not silently simplify the mechanism")
            identity = "expr_" + digest([idea["dataset_id"], compiled.metadata["structural_hash"]])[:20]
            if any(candidate["expression_id"] == identity for candidate in self.candidates):
                raise ValueError("An identical normalized expression already exists in this batch")
            blocked = {name: self.bundle.fields[idea["dataset_id"]][name]["blocking_reasons"] for name in compiled.info.fields
                       if self.bundle.fields[idea["dataset_id"]][name]["factor_usage"] != "eligible"}
            if blocked and not self.config.allow_unapproved_dry_run:
                raise ValueError("Field approvals block numerical computation under this configuration")
            validation, panel = self.validator.evaluate(compiled, idea["dataset_id"])
            history_matches = []
            for record in self.snapshot.records:
                payload = record["payload"]
                if record["kind"] == "expression" and record["dataset_id"] == idea["dataset_id"]:
                    canonical = payload.get("canonical", "")
                    similarity = difflib.SequenceMatcher(None, compiled.metadata["canonical"], canonical).ratio()
                    if similarity >= 0.8:
                        history_matches.append({"record_id": record["record_id"], "canonical": canonical, "textual_ast_similarity": similarity,
                            "same_registry": payload.get("registry_fingerprint") == self.registry.fingerprint,
                            "outcome": record["outcome"]})
            correlations = []
            for previous_id, (previous_dataset, previous_idea, previous) in self.accepted_panels.items():
                if previous_dataset != idea["dataset_id"]:
                    continue
                common_dates = panel.index.intersection(previous.index)
                common_entities = panel.columns.intersection(previous.columns)
                left = panel.loc[common_dates, common_entities].to_numpy().ravel()
                right = previous.loc[common_dates, common_entities].to_numpy().ravel()
                mask = np.isfinite(left) & np.isfinite(right)
                if mask.sum() < self.config.min_validation_points or np.std(left[mask]) == 0 or np.std(right[mask]) == 0:
                    continue
                correlation = float(np.corrcoef(left[mask], right[mask])[0, 1])
                if abs(correlation) >= self.config.duplicate_correlation:
                    correlations.append({"expression_id": previous_id, "correlation": correlation, "paired_points": int(mask.sum()),
                                         "same_idea": previous_idea == idea["idea_id"]})
            if any(item["same_idea"] for item in correlations):
                validation["passed"] = False
                validation["failure_reasons"].append("near_duplicate_variant_within_idea")
            if not validation["passed"]:
                attempt.update(status="rejected_numerical", validation=validation, behavioral_duplicates=correlations)
                self.remember_failed_attempt(idea, attempt, "redundant" if correlations else "data_error")
                self.artifacts.log("expression_rejected", attempt=attempt)
                dump_json(self.artifacts.root / "attempts.in_progress.json", self.attempts)
                return {"accepted": False, **attempt}
            candidate = {"expression_id": identity, "idea_id": idea["idea_id"], "dataset_id": idea["dataset_id"], "family": idea["family"],
                "expression": arguments["expression"], **compiled.metadata, "construction_rationale": rationale, "alignment_explanation": alignment,
                "alignment_status": "offline_template_rule_matched" if self.config.mode == "offline" else "llm_explained_not_independently_proven",
                "orientation": "higher_factor_higher_hypothesized_future_return", "forecast_horizon_days": idea["forecast_horizon_days"],
                "research_end": self.bundle.research_end, "source_agent1_run_id": self.bundle.run_id,
                "numerical_validation": validation, "field_blockers": blocked,
                "status": "research_validated_requires_metadata" if blocked else "numerically_validated",
                "ready_for_agent4_factor_evaluation": not blocked, "portfolio_backtest_ready": False,
                "remaining_execution_requirements": ["Agent 4 must apply historical universe, actual trade timing, costs and evaluation split controls.",
                    "Numerical preview covers selected files/entities only; full-universe validation remains required."],
                "historical_matches": history_matches[:8], "behavioral_similarity_flags": correlations,
                "novelty_status": "historical_design_reused" if any(m["same_registry"] and m["canonical"] == compiled.metadata["canonical"] for m in history_matches) else "no_exact_match_in_bounded_memory",
                "prediction_status": "unmeasured_not_backtested"}
            candidate["replay_script"] = write_expression_job(self.artifacts.root, self.bundle, self.registry, self.config, idea, candidate)
            preview_path = self.artifacts.root / "previews" / f"{identity}.csv"
            candidate["preview_rows_written"] = export_preview(panel, preview_path, self.config.preview_rows)
            candidate["preview_artifact"] = f"previews/{identity}.csv" if self.config.preview_rows else None
            dump_json(self.artifacts.root / "validation" / f"{identity}.json", validation)
            memory_id = self.memory.append(kind="expression", run_id=self.artifacts.run_id, logical_id=identity,
                dataset_id=idea["dataset_id"], family=idea["family"], data_end=self.bundle.research_end, payload=candidate)
            self.candidates.append(candidate)
            self.accepted_panels[identity] = (idea["dataset_id"], idea["idea_id"], panel)
            attempt.update(status="accepted", expression_id=identity)
            self.artifacts.log("expression_accepted", candidate=candidate, memory_record_id=memory_id)
            dump_json(self.artifacts.root / "expressions.in_progress.json", self.candidates)
            return {"accepted": True, "candidate": candidate}
        except Exception as error:
            attempt.update(status="rejected_static_or_execution", reason=f"{type(error).__name__}: {error}")
            self.remember_failed_attempt(idea, attempt)
            self.artifacts.log("expression_rejected", attempt=attempt)
            dump_json(self.artifacts.root / "attempts.in_progress.json", self.attempts)
            return {"accepted": False, **attempt}

    def defer(self, arguments):
        if set(arguments) != {"idea_id", "reason", "missing_requirements"}:
            raise ValueError("Defer requires idea_id, reason, missing_requirements")
        idea = self.idea(arguments["idea_id"])
        if any(candidate["idea_id"] == idea["idea_id"] for candidate in self.candidates):
            raise ValueError("An already constructed idea cannot be silently replaced by a defer record")
        disposition = {"idea_id": idea["idea_id"], "status": "deferred", "reason": text(arguments["reason"], "defer reason"),
                       "missing_requirements": string_list(arguments["missing_requirements"], "missing_requirements", 1, 12)}
        self.dispositions[idea["idea_id"]] = disposition
        self.artifacts.log("idea_deferred", **disposition)
        return disposition

    def dispatch(self, name, arguments):
        if name == "construct_expression":
            result = self.construct(arguments)
            if result["accepted"]:
                candidate = result["candidate"]
                return {"accepted": True, "candidate": {key: candidate[key] for key in ("expression_id", "idea_id", "expression", "status", "field_blockers", "novelty_status", "behavioral_similarity_flags")},
                    "validation": {key: candidate["numerical_validation"][key] for key in ("passed", "finite_count", "coverage", "first_finite_signal_date", "execution_lag")}}
            return {key: value for key, value in result.items() if key != "validation"} | ({"validation": {
                key: result["validation"][key] for key in ("passed", "failure_reasons", "finite_count", "coverage")}} if "validation" in result else {})
        if name == "defer_idea":
            return self.defer(arguments)
        if name == "inspect_idea":
            if set(arguments) != {"idea_id"}:
                raise ValueError("Expected idea_id")
            idea = self.idea(arguments["idea_id"])
            return {"idea": idea, "fields": {name: self.bundle.fields[idea["dataset_id"]][name] for name in idea["required_fields"]},
                    "evidence": [self.bundle.evidence[identity] for identity in idea["evidence_ids"]]}
        if name == "search_memory":
            if set(arguments) != {"query", "dataset_id", "family", "limit"}:
                raise ValueError("Expected query, dataset_id, family, limit")
            if arguments["dataset_id"] is not None and arguments["dataset_id"] not in self.bundle.datasets:
                raise ValueError("Unknown dataset_id")
            return self.snapshot.search(**arguments)
        if name == "finish_expressions":
            if set(arguments) != {"recommended_followups"}:
                raise ValueError("Expected recommended_followups")
            handled = {candidate["idea_id"] for candidate in self.candidates} | set(self.dispositions)
            if handled != set(self.ideas):
                raise ValueError("Every idea needs >=1 accepted expression or an explicit defer reason")
            self.followups = string_list(arguments["recommended_followups"], "recommended_followups", 0, 20)
            self.finished = True
            return {"accepted_expressions": len(self.candidates), "deferred_ideas": len(self.dispositions)}
        raise ValueError(f"Unknown Agent 3 tool: {name}")

    def tools(self):
        strict = bool(self.config.llm.get("strict_tools", False))
        return [tool("inspect_idea", "Read an idea, exact field contract and EDA evidence.", {"idea_id": {"type": "string"}}, strict),
            tool("search_memory", "Read time-filtered historical expression and evaluator records; final tests are excluded.", {
                "query": {"type": "string"}, "dataset_id": {"type": ["string", "null"]}, "family": {"type": ["string", "null"]}, "limit": {"type": "integer"}}, strict),
            tool("construct_expression", "Compile and numerically check one expression. Use every required field. High output must correspond to higher hypothesized future returns. Error results allow bounded repairs.", {
                "idea_id": {"type": "string"}, "expression": {"type": "string"}, "construction_rationale": {"type": "string"}, "alignment_explanation": {"type": "string"}}, strict),
            tool("defer_idea", "Explicitly explain an idea that cannot be implemented with available data/operators; never invent a formula just to satisfy a count.", {
                "idea_id": {"type": "string"}, "reason": {"type": "string"}, "missing_requirements": {"type": "array", "items": {"type": "string"}}}, strict),
            tool("finish_expressions", "Finish once every idea has accepted expressions or an explicit defer record.", {
                "recommended_followups": {"type": "array", "items": {"type": "string"}}}, strict)]

    def offline(self):
        for idea in self.ideas.values():
            if idea.get("missing_operators"):
                self.defer({"idea_id": idea["idea_id"], "reason": "所需算子尚未有经过批准的实现。", "missing_requirements": idea["missing_operators"]})
                continue
            template_error = None
            try:
                templates = expression_templates(idea)
            except ValueError as error:
                template_error = str(error)
                templates = []
            for expression, explanation in templates[:self.config.max_expressions_per_idea]:
                self.construct({"idea_id": idea["idea_id"], "expression": expression, "construction_rationale": "显式离线模板，用于验证实现链路；不代表模型发现或收益检验。", "alignment_explanation": explanation})
            if not any(candidate["idea_id"] == idea["idea_id"] for candidate in self.candidates):
                reason = template_error or ("当前机制族没有可用的离线模板；可使用 LLM 模式提出受约束实现。" if not templates else "没有通过静态与数值检查的离线实现；查看 attempts.json，或使用 LLM 模式提出其他实现。")
                self.defer({"idea_id": idea["idea_id"], "reason": reason, "missing_requirements": ["a_valid_distinct_implementation"]})
        self.followups = ["解决字段元数据限制，完整验证股票池和执行时点，再交给 Agent 4。", "预览通过不代表有效因子；需要成本、开发/验证划分和独立测试。"]
        self.finished = True

    def run(self):
        try:
            if self.config.mode == "offline":
                self.offline()
            else:
                self.llm_status = run_loop(self, self.client, self.prompt, {"task": "为每个可实现假设构造一至多个不同的因子表达式，并根据工具错误修复。", "research_end": self.bundle.research_end,
                    "ideas": list(self.ideas.values()), "operator_registry": self.registry.describe(), "initial_memory": self.snapshot.search(limit=8),
                    "budgets": {"max_expressions_per_idea": self.config.max_expressions_per_idea, "max_attempts_per_idea": self.config.max_attempts_per_idea,
                                "max_window": self.config.max_window, "execution_lag": self.config.execution_lag}}, self.tools())
        except Exception as error:
            self.llm_status = "error" if self.config.mode == "llm" else self.llm_status
            self.artifacts.errors.append(f"{type(error).__name__}: {error}")
        try:
            return self.publish()
        finally:
            self.memory.close()

    def publish(self):
        status = "completed" if self.finished and not self.artifacts.errors else "partial" if self.candidates or self.dispositions else "failed"
        handled = {candidate["idea_id"] for candidate in self.candidates} | set(self.dispositions)
        result = {"schema_version": "1.0", "agent": "agent3", "run_id": self.artifacts.run_id, "mode": self.config.mode,
            "status": status, "llm_status": self.llm_status, "research_end": self.bundle.research_end,
            "source_agent1_run_id": self.bundle.run_id, "source_agent2_run_id": self.upstream["run_id"],
            "registry_fingerprint": self.registry.fingerprint, "expressions": self.candidates, "idea_dispositions": list(self.dispositions.values()),
            "unhandled_idea_ids": sorted(set(self.ideas) - handled), "followups": self.followups, "errors": self.artifacts.errors}
        dump_json(self.artifacts.root / "expressions.json", result)
        dump_json(self.artifacts.root / "attempts.json", self.attempts)
        dump_json(self.artifacts.root / "next_agent_payload.json", {**result, "producer": "agent3", "consumer": "agent4",
            "ready_expressions": [candidate for candidate in self.candidates if candidate["ready_for_agent4_factor_evaluation"]],
            "research_only_previews": True, "constraints": self.bundle.contract["global_constraints"]})
        lines = [f"模式：{self.config.mode}；状态：{status}；观察截止日：{self.bundle.research_end}。", "",
            "角色：把假设实现为受约束的数学表达式，并检查时间、形状和数值可用性。数值试算不是回测；字段限制不会被自动解除。", "",
            f"接受表达式：{len(self.candidates)}；明确延后假设：{len(self.dispositions)}；正式因子评估就绪：{sum(candidate['ready_for_agent4_factor_evaluation'] for candidate in self.candidates)}。", ""]
        for candidate in self.candidates:
            validation = candidate["numerical_validation"]
            lines += [f"## {candidate['expression_id']} / {candidate['idea_id']}", "", f"`{candidate['expression']}`", "",
                f"- 对齐说明：{candidate['alignment_explanation']}", f"- 输入：{', '.join(candidate['fields'])}；预热：{candidate['warmup_rows_before_execution_lag']} 行；执行滞后：{candidate['execution_lag']} 行。",
                f"- 有效值：{validation['finite_count']}；覆盖率：{validation['coverage']:.2%}；状态：{candidate['status']}。",
                f"- 字段阻塞：{json.dumps(candidate['field_blockers'], ensure_ascii=False)}",
                f"- 历史/行为相似：{candidate['novelty_status']}；{json.dumps(candidate['behavioral_similarity_flags'], ensure_ascii=False)}",
                f"- 重跑脚本：{candidate['replay_script']}；预览：{candidate['preview_artifact']}。", ""]
        lines += ["## 延后与未完成", ""] + ["- " + json.dumps(item, ensure_ascii=False) for item in self.dispositions.values()]
        lines += ["- " + item for item in self.artifacts.errors] + ["", "## 下一步", ""] + ["- " + item for item in self.followups]
        self.artifacts.report("Agent 3 因子表达式与验证", lines)
        self.artifacts.state(status, accepted_expressions=len(self.candidates), deferred_ideas=len(self.dispositions), llm_status=self.llm_status)
        return result

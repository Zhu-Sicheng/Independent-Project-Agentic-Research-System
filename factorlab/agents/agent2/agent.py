"""Hypothesis generation with feasibility, evidence, diversity, and memory checks."""

from __future__ import annotations

import collections
import json
import re

from agent1.core import dump_json
from agent1.llm import ChatClient
from research.common import Artifacts, EDABundle, IdeaConfig, PROJECT_ROOT, bounded_int, digest, now_utc, string_list, text
from research.loop import run_loop, tool
from research.memory import ResearchMemory
from research.operators import OperatorRegistry
from research.priors import FAMILIES, role_fields

IDEA_PROPERTIES = {
    "title": {"type": "string"}, "family": {"type": "string"}, "dataset_id": {"type": "string"},
    "mechanism": {"type": "string"}, "signal_concept": {"type": "string"},
    "required_fields": {"type": "array", "items": {"type": "string"}},
    "expected_return_direction": {"type": "string", "enum": ["positive", "negative"]},
    "forecast_horizon_days": {"type": "integer"}, "lookback_hint_days": {"type": "array", "items": {"type": "integer"}},
    "applicability": {"type": "array", "items": {"type": "string"}}, "failure_modes": {"type": "array", "items": {"type": "string"}},
    "evidence_ids": {"type": "array", "items": {"type": "string"}}, "history_record_ids": {"type": "array", "items": {"type": "string"}},
    "novelty_rationale": {"type": "string"}, "required_operators": {"type": "array", "items": {"type": "string"}},
}


class IdeaAgent:
    def __init__(self, config: IdeaConfig, client=None):
        self.config = config
        config.validate()
        self.client = client or (ChatClient(config.llm) if config.mode == "llm" else None)
        self.bundle = EDABundle(config.agent1_run)
        self.registry = OperatorRegistry(config.operator_file)
        self.artifacts = Artifacts("agent2", config, self.bundle)
        self.memory = ResearchMemory(config.memory_db)
        self.snapshot = self.memory.snapshot(self.bundle.research_end, config.knowledge_cutoff or self.artifacts.started_at, config.memory_limit)
        self.ideas, self.rejections, self.followups = [], [], []
        self.finished = False
        self.llm_status = "not_requested" if config.mode == "offline" else "pending"
        self.prompt = (PROJECT_ROOT / "prompts" / "agent2_system.md").read_text(encoding="utf-8")
        dump_json(self.artifacts.root / "memory_snapshot.json", self.snapshot.as_dict())
        dump_json(self.artifacts.root / "operator_capabilities.json", self.registry.describe())
        (self.artifacts.root / "agent_system_prompt.md").write_text(self.prompt, encoding="utf-8")
        self.artifacts.state("running")

    def submit(self, proposal: dict) -> dict:
        if not isinstance(proposal, dict) or set(proposal) != set(IDEA_PROPERTIES):
            raise ValueError(f"Idea requires exactly {sorted(IDEA_PROPERTIES)}")
        proposal = dict(proposal)
        dataset_id = proposal["dataset_id"]
        if dataset_id not in self.bundle.datasets:
            raise ValueError("Unknown dataset_id")
        for name in ("title", "family", "mechanism", "signal_concept", "novelty_rationale"):
            proposal[name] = text(proposal[name], name, 2500)
        if not re.fullmatch(r"[a-z][a-z0-9_]{1,63}", proposal["family"]):
            raise ValueError("family must be a short lowercase snake_case label")
        if any(re.search(r"\bts_\w+\s*\(|```", proposal[name]) for name in ("mechanism", "signal_concept")):
            raise ValueError("Agent 2 must describe hypotheses in natural language, without factor formulas")
        for name, minimum in (("required_fields", 1), ("applicability", 1), ("failure_modes", 1), ("evidence_ids", 1), ("history_record_ids", 0), ("required_operators", 0)):
            proposal[name] = string_list(proposal[name], name, minimum, 12)
        candidates = self.bundle.candidate_fields(dataset_id)
        if any(name not in candidates for name in proposal["required_fields"]):
            raise ValueError("Required fields must be existing permitted numerical candidates; missing data belongs in followups")
        self.bundle.validate_evidence(proposal["evidence_ids"], dataset_id)
        if any(identity not in self.snapshot.by_id for identity in proposal["history_record_ids"]):
            raise ValueError("History references must belong to this time-filtered memory snapshot")
        if proposal["expected_return_direction"] not in {"positive", "negative"}:
            raise ValueError("Expected return direction must be positive or negative for the raw signal concept")
        bounded_int(proposal["forecast_horizon_days"], "forecast_horizon_days", 1, 252)
        windows = proposal["lookback_hint_days"]
        if not isinstance(windows, list) or not 1 <= len(windows) <= 5:
            raise ValueError("Provide 1..5 lookback hints")
        for window in windows:
            bounded_int(window, "lookback hint", 1, 252)
        family_counts = collections.Counter(idea["family"] for idea in self.ideas)
        dataset_counts = collections.Counter(idea["dataset_id"] for idea in self.ideas)
        if len(self.ideas) >= self.config.max_ideas or family_counts[proposal["family"]] >= self.config.max_ideas_per_family or dataset_counts[dataset_id] >= self.config.max_ideas_per_dataset:
            raise ValueError("Idea count/diversity budget exceeded")
        fingerprint = digest({key: proposal[key] for key in ("family", "dataset_id", "required_fields", "expected_return_direction", "forecast_horizon_days", "lookback_hint_days")})
        if any(idea["fingerprint"] == fingerprint for idea in self.ideas):
            raise ValueError("An identical research design already exists in this batch")
        previous_designs = [record for record in self.snapshot.records if record["kind"] == "idea" and record["payload"].get("fingerprint") == fingerprint]
        missing_operators = [name for name in proposal["required_operators"] if name not in self.registry.enabled and name not in {"abs", "safe_div"}]
        blockers = {name: candidates[name]["blocking_reasons"] for name in proposal["required_fields"] if candidates[name]["factor_usage"] != "eligible"}
        idea = {**proposal, "idea_id": "idea_" + fingerprint[:20], "fingerprint": fingerprint,
            "source_agent1_run_id": self.bundle.run_id, "research_end": self.bundle.research_end,
            "status": "needs_operators" if missing_operators else "needs_metadata" if blockers else "research_ready",
            "field_blockers": blockers, "missing_operators": missing_operators,
            "prediction_status": "untested_hypothesis_not_measured_alpha",
            "prior_source": "explicit_offline_template" if self.config.mode == "offline" else "llm_generated_hypothesis",
            "novelty_status": "historical_design_reused" if previous_designs else "no_exact_design_in_bounded_memory",
            "reused_design_record_ids": [record["record_id"] for record in previous_designs[:8]],
            "evidence_interpretation": "EDA supports data feasibility/quality only; it does not establish this predictive mechanism."}
        memory_id = self.memory.append(kind="idea", run_id=self.artifacts.run_id, logical_id=idea["idea_id"], dataset_id=dataset_id,
            family=idea["family"], data_end=self.bundle.research_end, payload=idea)
        self.ideas.append(idea)
        self.artifacts.log("idea_accepted", idea=idea, memory_record_id=memory_id)
        dump_json(self.artifacts.root / "ideas.in_progress.json", self.ideas)
        return idea

    def dispatch(self, name, arguments):
        if name == "submit_idea":
            return self.submit(arguments)
        if name == "inspect_dataset":
            if set(arguments) != {"dataset_id"} or arguments["dataset_id"] not in self.bundle.datasets:
                raise ValueError("Expected one known dataset_id")
            identity = arguments["dataset_id"]
            return {"dataset": self.bundle.datasets[identity], "evidence_index": [
                {"evidence_id": evidence["evidence_id"], "category": evidence["category"], "column": evidence["metrics"].get("column")}
                for evidence in self.bundle.evidence.values() if evidence["dataset_id"] == identity]}
        if name == "read_evidence":
            if set(arguments) != {"evidence_ids"}:
                raise ValueError("Expected evidence_ids")
            ids = string_list(arguments["evidence_ids"], "evidence_ids", 1, 12)
            if any(identity not in self.bundle.evidence for identity in ids):
                raise ValueError("Unknown evidence ID")
            return [self.bundle.evidence[identity] for identity in ids]
        if name == "search_memory":
            if set(arguments) != {"query", "dataset_id", "family", "limit"}:
                raise ValueError("Expected query, dataset_id, family, limit")
            if arguments["dataset_id"] is not None and arguments["dataset_id"] not in self.bundle.datasets:
                raise ValueError("Unknown dataset_id")
            return self.snapshot.search(**arguments)
        if name == "finish_ideas":
            if set(arguments) != {"recommended_followups"}:
                raise ValueError("Expected recommended_followups")
            if len(self.ideas) < self.config.min_ideas:
                raise ValueError("Not enough accepted ideas; continue or let the bounded run report partial")
            self.followups = string_list(arguments["recommended_followups"], "recommended_followups", 0, 20)
            self.finished = True
            return {"accepted": len(self.ideas)}
        raise ValueError(f"Unknown Agent 2 tool: {name}")

    def tools(self):
        strict = bool(self.config.llm.get("strict_tools", False))
        return [tool("inspect_dataset", "Inspect one dataset contract and evidence IDs; no new field approval.", {"dataset_id": {"type": "string"}}, strict),
            tool("read_evidence", "Read computed EDA evidence before citing it.", {"evidence_ids": {"type": "array", "items": {"type": "string"}}}, strict),
            tool("search_memory", "Search only the frozen, time-filtered research memory. Includes successes and failures; excludes final tests.", {
                "query": {"type": "string"}, "dataset_id": {"type": ["string", "null"]}, "family": {"type": ["string", "null"]}, "limit": {"type": "integer"}}, strict),
            tool("submit_idea", "Submit one testable natural-language hypothesis. EDA citations establish feasibility, not alpha. No formula.", IDEA_PROPERTIES, strict),
            tool("finish_ideas", "Finish after enough checked ideas; list unresolved data and research requirements.", {"recommended_followups": {"type": "array", "items": {"type": "string"}}}, strict)]

    def offline(self):
        for dataset_id, dataset in self.bundle.datasets.items():
            candidates = self.bundle.candidate_fields(dataset_id)
            roles = role_fields(candidates)
            for prior in FAMILIES:
                if len(self.ideas) >= self.config.max_ideas:
                    break
                if any(not roles.get(role) for role in prior["roles"]):
                    continue
                if prior["family"] == "size_premium" and ((dataset.get("quality") or {}).get("entity_count") or 0) < 2:
                    continue
                required = [roles[role] for role in prior["roles"]]
                history = self.snapshot.search(prior["family"], dataset_id, prior["family"], 4)
                proposal = {"title": prior["title"], "family": prior["family"], "dataset_id": dataset_id,
                    "mechanism": prior["mechanism"], "signal_concept": prior["concept"], "required_fields": required,
                    "expected_return_direction": prior["direction"], "forecast_horizon_days": prior["horizon"],
                    "lookback_hint_days": prior["windows"], "applicability": ["按稳定证券标识和交易日对齐，确认必要字段的单位、复权和首次可得时点。"],
                    "failure_modes": [prior["failure"], "当前尚未测量未来收益关系；需要开发期评估和独立测试。"],
                    "evidence_ids": self.bundle.field_evidence(dataset_id, required), "history_record_ids": [r["record_id"] for r in history],
                    "novelty_rationale": "这是公开标识的离线先验模板；同批次重复会拒绝，历史设计复用会标记，不声称经济机制原创。",
                    "required_operators": prior["operators"]}
                try:
                    self.submit(proposal)
                except ValueError as error:
                    self.rejections.append({"dataset_id": dataset_id, "family": prior["family"], "reason": str(error)})
        self.followups = ["按字段契约解决元数据限制，再决定哪些表达式可以进入正式评估。", "在固定尝试预算下比较不同机制，并记录成功、失效和实现问题；封存最终测试结果。"]
        self.finished = len(self.ideas) >= self.config.min_ideas

    def run(self):
        try:
            if self.config.mode == "offline":
                self.offline()
            else:
                self.llm_status = run_loop(self, self.client, self.prompt, {"task": "生成有证据、有失败条件的多样化自然语言因子假设。", "research_end": self.bundle.research_end,
                    "datasets": self.bundle.catalog(), "operator_capabilities": self.registry.describe(),
                    "initial_memory": self.snapshot.search(limit=8), "budgets": {"min_ideas": self.config.min_ideas, "max_ideas": self.config.max_ideas,
                    "max_per_dataset": self.config.max_ideas_per_dataset, "max_per_family": self.config.max_ideas_per_family}}, self.tools())
        except Exception as error:
            self.llm_status = "error" if self.config.mode == "llm" else self.llm_status
            self.artifacts.errors.append(f"{type(error).__name__}: {error}")
        try:
            return self.publish()
        finally:
            self.memory.close()

    def publish(self):
        status = "completed" if self.finished and not self.artifacts.errors else "partial" if self.ideas else "failed"
        result = {"schema_version": "1.0", "agent": "agent2", "run_id": self.artifacts.run_id, "mode": self.config.mode,
            "status": status, "llm_status": self.llm_status, "agent1_run": str(self.bundle.root), "source_agent1_run_id": self.bundle.run_id,
            "research_end": self.bundle.research_end, "knowledge_cutoff": self.snapshot.knowledge_cutoff,
            "operator_fingerprint": self.registry.fingerprint, "ideas": self.ideas, "rejections": self.rejections,
            "followups": self.followups, "errors": self.artifacts.errors}
        dump_json(self.artifacts.root / "ideas.json", result)
        dump_json(self.artifacts.root / "next_agent_payload.json", {**result, "producer": "agent2", "consumer": "agent3",
            "input_fingerprints": self.bundle.fingerprints, "operator_capabilities_artifact": "operator_capabilities.json"})
        lines = [f"模式：{self.config.mode}；状态：{status}；观察截止日：{self.bundle.research_end}。", "",
            "角色：从 EDA、字段约束与历史记录提出可检验假设。所有方向均未经过收益检验；离线模板不代表 LLM 自主发现。", ""]
        for idea in self.ideas:
            lines += [f"## {idea['title']} ({idea['idea_id']})", "", f"- 数据集：{idea['dataset_id']}；状态：{idea['status']}；机制族：{idea['family']}",
                f"- 信号概念：{idea['signal_concept']}；原始概念与未来收益预期关系：{idea['expected_return_direction']}；预测期：{idea['forecast_horizon_days']} 个交易观察日。",
                f"- 机制：{idea['mechanism']}", f"- 必要字段：{', '.join(idea['required_fields'])}", f"- 失效条件：{'；'.join(idea['failure_modes'])}",
                f"- EDA 证据：{', '.join(idea['evidence_ids'])}；历史记录：{', '.join(idea['history_record_ids']) or '无'}",
                f"- 字段阻塞：{json.dumps(idea['field_blockers'], ensure_ascii=False)}", ""]
        lines += ["## 下一步", ""] + ["- " + item for item in self.followups]
        lines += ["", "## 未完成项", ""] + ["- " + item for item in self.artifacts.errors]
        self.artifacts.report("Agent 2 因子研究假设", lines)
        self.artifacts.state(status, accepted_ideas=len(self.ideas), llm_status=self.llm_status)
        return result

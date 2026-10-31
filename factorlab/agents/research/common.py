"""Configuration and immutable upstream artifact boundaries for Agents 2 and 3."""

from __future__ import annotations

import dataclasses
import datetime as dt
import hashlib
import json
import uuid
from pathlib import Path

from agent1.core import Config as EDAConfig
from agent1.core import clean_json, dump_json, is_forward_label, read_json, sha256_file

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def timestamp(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Timestamp must be an ISO string with a timezone")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp requires an explicit timezone")
    return parsed.astimezone(dt.timezone.utc).isoformat()


def digest(value) -> str:
    return hashlib.sha256(json.dumps(clean_json(value), sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def bounded_int(value, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum}, {maximum}]")
    return value


def text(value, name: str, maximum: int = 2500) -> str:
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= maximum:
        raise ValueError(f"{name} must be nonempty text, at most {maximum} characters")
    return value.strip()


def string_list(value, name: str, minimum: int = 0, maximum: int = 20) -> list[str]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ValueError(f"{name} must contain {minimum}..{maximum} strings")
    values = [text(item, name, 1500) for item in value]
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must not contain duplicates")
    return values


@dataclasses.dataclass
class BaseConfig:
    agent1_run: str = "latest"
    memory_db: str = "research_database/research.sqlite3"
    operator_file: str = "ts_operators.md"
    output_root: str = "outputs/research"
    mode: str = "offline"
    knowledge_cutoff: str | None = None
    max_turns: int = 20
    max_tool_calls: int = 48
    memory_limit: int = 1000
    llm: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, values: dict):
        if not isinstance(values, dict):
            raise ValueError("Configuration must be a JSON object")
        unknown = set(values) - {item.name for item in dataclasses.fields(cls)}
        if unknown:
            raise ValueError(f"Unknown configuration keys: {sorted(unknown)}")
        config = cls(**values)
        config.validate()
        return config

    def validate(self):
        if self.mode not in {"offline", "llm"}:
            raise ValueError("mode must be offline or llm")
        for name in ("max_turns", "max_tool_calls", "memory_limit"):
            bounded_int(getattr(self, name), name, 1, 10000)
        if self.knowledge_cutoff is not None:
            self.knowledge_cutoff = timestamp(self.knowledge_cutoff)
        # Reuse the credential-safe LLM settings validation without changing Agent 1.
        EDAConfig.from_dict({"research_end": "2000-01-01", "llm": self.llm})
        for name in ("agent1_run", "memory_db", "operator_file", "output_root"):
            text(getattr(self, name), name, 2000)


@dataclasses.dataclass
class IdeaConfig(BaseConfig):
    output_root: str = "outputs/agent2"
    min_ideas: int = 4
    max_ideas: int = 8
    max_ideas_per_dataset: int = 6
    max_ideas_per_family: int = 2

    def validate(self):
        super().validate()
        for name in ("min_ideas", "max_ideas", "max_ideas_per_dataset", "max_ideas_per_family"):
            bounded_int(getattr(self, name), name, 1, 40)
        if self.min_ideas > self.max_ideas:
            raise ValueError("min_ideas must not exceed max_ideas")


@dataclasses.dataclass
class ExpressionConfig(BaseConfig):
    output_root: str = "outputs/agent3"
    agent2_run: str = "latest"
    max_expressions_per_idea: int = 3
    max_attempts_per_idea: int = 6
    max_nodes: int = 48
    max_depth: int = 9
    max_window: int = 252
    max_warmup_rows: int = 1000
    execution_lag: int = 1
    validation_max_files: int = 8
    validation_max_entities: int = 8
    min_validation_points: int = 30
    min_coverage: float = 0.5
    duplicate_correlation: float = 0.995
    preview_rows: int = 5000
    allow_unapproved_dry_run: bool = True

    def validate(self):
        super().validate()
        text(self.agent2_run, "agent2_run", 2000)
        for name, lo, hi in (("max_expressions_per_idea", 1, 10), ("max_attempts_per_idea", 1, 30),
                             ("max_nodes", 3, 200), ("max_depth", 2, 20), ("max_window", 1, 1000),
                             ("max_warmup_rows", 2, 5000), ("execution_lag", 1, 20),
                             ("validation_max_files", 1, 1000), ("validation_max_entities", 1, 500),
                             ("min_validation_points", 2, 10000), ("preview_rows", 0, 100000)):
            bounded_int(getattr(self, name), name, lo, hi)
        if self.max_attempts_per_idea < self.max_expressions_per_idea:
            raise ValueError("max_attempts_per_idea must cover max_expressions_per_idea")
        for name in ("min_coverage", "duplicate_correlation"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value <= 1:
                raise ValueError(f"{name} must be in (0, 1]")
        if not isinstance(self.allow_unapproved_dry_run, bool):
            raise ValueError("allow_unapproved_dry_run must be boolean")


def latest_run(agent: str) -> Path:
    candidates = []
    for path in (PROJECT_ROOT / "outputs" / agent).glob("*"):
        state = path / "run_state.json"
        if state.is_file():
            try:
                if read_json(state).get("status") == "completed":
                    candidates.append(path)
            except (OSError, ValueError):
                continue
    if not candidates:
        raise ValueError(f"No completed {agent} run found; specify --{agent}-run explicitly")
    return sorted(candidates)[-1].resolve()


class EDABundle:
    def __init__(self, run: str | Path):
        self.root = latest_run("agent1") if str(run) == "latest" else Path(run).resolve()
        self.contract = read_json(self.root / "data_contract.json")
        self.eda = read_json(self.root / "eda_results.json")
        self.manifest = read_json(self.root / "input_manifest.json")
        self.eda_config = EDAConfig.from_dict(read_json(self.root / "resolved_config.json"))
        if self.eda.get("status") != "completed":
            raise ValueError("Use a completed Agent 1 run; partial/failed upstream EDA is not silently accepted")
        self.research_end = self.contract["research_end"]
        self.run_id = self.contract["run_id"]
        if self.eda["run_id"] != self.run_id or self.eda["research_end"] != self.research_end or self.manifest["research_end"] != self.research_end or self.eda_config.research_end != self.research_end:
            raise ValueError("Upstream run identity or research cutoff mismatch")
        self.datasets = {d["dataset_id"]: d for d in self.contract["datasets"]}
        self.source_datasets = {d["dataset_id"]: d for d in self.manifest["datasets"]}
        if len(self.datasets) != len(self.contract["datasets"]) or set(self.datasets) != set(self.source_datasets):
            raise ValueError("Duplicate/mismatched upstream dataset IDs")
        self.evidence = {e["evidence_id"]: e for e in self.eda["evidence"]}
        if len(self.evidence) != len(self.eda["evidence"]):
            raise ValueError("Upstream evidence IDs must be unique")
        self.fields = {}
        for dataset_id, dataset in self.datasets.items():
            if set(f["name"] for f in dataset["fields"]) != set(self.source_datasets[dataset_id]["columns"]):
                raise ValueError("Upstream field contract differs from source schema")
            self.fields[dataset_id] = {f["name"]: f for f in dataset["fields"]}
        for evidence in self.evidence.values():
            if evidence["dataset_id"] not in self.datasets:
                raise ValueError("Evidence references an unknown dataset")
        self.fingerprints = {name: sha256_file(self.root / name) for name in (
            "data_contract.json", "eda_results.json", "input_manifest.json", "resolved_config.json")}

    def candidate_fields(self, dataset_id: str) -> dict:
        return {name: field for name, field in self.fields[dataset_id].items()
                if field["factor_usage"] in {"eligible", "candidate_requires_confirmation"} and not is_forward_label(name)}

    def validate_evidence(self, evidence_ids: list[str], dataset_id: str):
        for identity in evidence_ids:
            if identity not in self.evidence or self.evidence[identity]["dataset_id"] != dataset_id:
                raise ValueError("Evidence must exist and belong to the idea's dataset")

    def field_evidence(self, dataset_id: str, fields: list[str]) -> list[str]:
        matches = [e["evidence_id"] for e in self.evidence.values() if e["dataset_id"] == dataset_id
                   and e["category"] == "field_profile" and e["metrics"].get("column") in fields]
        return matches[-len(fields):] if matches else [e["evidence_id"] for e in self.evidence.values()
                    if e["dataset_id"] == dataset_id and e["category"] == "coverage"][-1:]

    def catalog(self) -> list[dict]:
        return [{"dataset_id": identity, "name": dataset["name"], "kind": dataset["kind"],
                 "scope": dataset["scope"], "date_range": dataset["date_range"],
                 "candidate_fields": [{k: field.get(k) for k in ("name", "semantic_role", "factor_usage", "unit", "blocking_reasons")}
                                      for field in self.candidate_fields(identity).values()]}
                for identity, dataset in self.datasets.items()]


class Artifacts:
    def __init__(self, agent: str, config: BaseConfig, bundle: EDABundle):
        self.agent, self.config, self.bundle = agent, config, bundle
        name = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
        self.root = Path(config.output_root).resolve() / name
        source = Path(bundle.eda_config.data_root).resolve()
        if self.root.is_relative_to(source):
            raise ValueError("Research output must be outside original data_root")
        if Path(config.memory_db).resolve().is_relative_to(source):
            raise ValueError("Research database must be outside the original data_root")
        self.root.mkdir(parents=True, exist_ok=False)
        self.started_at = now_utc()
        self.errors = []
        dump_json(self.root / "resolved_config.json", config)
        dump_json(self.root / "input_snapshot.json", {"agent1_run": str(bundle.root), "run_id": bundle.run_id,
            "research_end": bundle.research_end, "sha256": bundle.fingerprints})

    @property
    def run_id(self):
        return self.root.name

    def log(self, event: str, **values):
        with (self.root / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(clean_json({"time_utc": now_utc(), "event": event, **values}), ensure_ascii=False, allow_nan=False) + "\n")

    def state(self, status: str, **values):
        dump_json(self.root / "run_state.json", {"schema_version": "1.0", "agent": self.agent, "run_id": self.run_id,
            "status": status, "mode": self.config.mode, "started_at_utc": self.started_at, "updated_at_utc": now_utc(),
            "research_end": self.bundle.research_end, "errors": self.errors, **values})

    def report(self, title: str, lines: list[str]):
        import html
        markdown = f"# {title}\n\n" + "\n".join(lines) + "\n"
        (self.root / "report.md").write_text(markdown, encoding="utf-8")
        (self.root / "report.html").write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>' + html.escape(title) +
            '</title><style>body{max-width:1100px;margin:30px auto;padding:0 20px;font:15px/1.7 system-ui;color:#20333d}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><pre>' + html.escape(markdown) + "</pre></html>", encoding="utf-8")

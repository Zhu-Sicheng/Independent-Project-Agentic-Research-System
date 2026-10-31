"""Append-only SQLite research records with data-time and knowledge-time filtering."""

from __future__ import annotations

import datetime as dt
import json
import re
import sqlite3
from pathlib import Path

from agent1.core import clean_json, read_json
from .common import bounded_int, digest, now_utc, text, timestamp

KINDS = {"idea", "expression", "attempt", "feedback"}
OUTCOMES = {"unmeasured", "positive", "negative", "inconclusive", "implementation_error", "data_error", "redundant"}


class ResearchMemory:
    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, timeout=30)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS records (
            row_id INTEGER PRIMARY KEY AUTOINCREMENT, record_id TEXT NOT NULL UNIQUE,
            kind TEXT NOT NULL, run_id TEXT NOT NULL, logical_id TEXT NOT NULL,
            dataset_id TEXT NOT NULL, family TEXT NOT NULL, data_end TEXT NOT NULL,
            available_at TEXT NOT NULL, created_at TEXT NOT NULL, split TEXT NOT NULL,
            outcome TEXT NOT NULL, fingerprint TEXT NOT NULL, payload_json TEXT NOT NULL)""")
        self.connection.execute("CREATE INDEX IF NOT EXISTS visible_records ON records(data_end, available_at, dataset_id, family)")
        self.connection.commit()

    def close(self):
        self.connection.close()

    def append(self, *, kind: str, run_id: str, logical_id: str, dataset_id: str, family: str,
               data_end: str, payload: dict, outcome: str = "unmeasured", split: str = "research", available_at: str | None = None) -> str:
        if kind not in KINDS or outcome not in OUTCOMES or split not in {"research", "development", "validation", "final_test"}:
            raise ValueError("Invalid research record kind/outcome/split")
        if kind in {"idea", "expression"} and (outcome != "unmeasured" or split != "research"):
            raise ValueError("Agents 2/3 cannot label a proposed idea or expression as a measured investment success")
        if kind == "attempt" and (outcome not in {"implementation_error", "data_error", "redundant", "inconclusive"} or split != "research"):
            raise ValueError("Attempt records describe implementation evidence, never financial performance")
        for name, value in (("run_id", run_id), ("logical_id", logical_id), ("dataset_id", dataset_id), ("family", family)):
            text(value, name, 2000)
        dt.date.fromisoformat(data_end)
        available = timestamp(available_at or now_utc())
        if available[:10] < data_end:
            raise ValueError("Record cannot be available before its evaluated data end")
        record_id = "mem_" + digest([kind, run_id, logical_id])[:24]
        encoded = json.dumps(clean_json(payload), sort_keys=True, ensure_ascii=False, allow_nan=False)
        fingerprint = digest(payload)
        existing = self.connection.execute("SELECT * FROM records WHERE record_id=?", (record_id,)).fetchone()
        if existing:
            same_headers = (existing["dataset_id"], existing["family"], existing["data_end"], existing["split"], existing["outcome"]) == (dataset_id, family, data_end, split, outcome)
            same_availability = available_at is None or existing["available_at"] == available
            if existing["fingerprint"] != fingerprint or not same_headers or not same_availability:
                raise ValueError("Append-only record identity already exists with different content")
            return record_id
        with self.connection:
            self.connection.execute("INSERT INTO records(record_id,kind,run_id,logical_id,dataset_id,family,data_end,available_at,created_at,split,outcome,fingerprint,payload_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (record_id, kind, run_id, logical_id, dataset_id, family, data_end, available, now_utc(), split, outcome, fingerprint, encoded))
        return record_id

    def snapshot(self, research_end: str, knowledge_cutoff: str, limit: int = 1000) -> "MemorySnapshot":
        bounded_int(limit, "memory limit", 1, 10000)
        dt.date.fromisoformat(research_end)
        cutoff = timestamp(knowledge_cutoff)
        rows = self.connection.execute("SELECT * FROM records WHERE data_end<=? AND available_at<=? AND split!='final_test' ORDER BY row_id DESC LIMIT ?", (research_end, cutoff, limit)).fetchall()
        records = []
        for row in rows:
            record = dict(row)
            record["payload"] = json.loads(record.pop("payload_json"))
            records.append(record)
        return MemorySnapshot(research_end, cutoff, records, limit)

    def import_feedback(self, payload: dict, source_path: Path) -> str:
        required = {"evaluation_id", "expression_id", "dataset_id", "family", "evaluation_end", "available_at", "split", "outcome", "failure_type", "metrics", "notes"}
        if not isinstance(payload, dict) or set(payload) != required:
            raise ValueError(f"Feedback requires exactly {sorted(required)}")
        if payload["split"] not in {"development", "validation", "final_test"} or payload["outcome"] == "unmeasured":
            raise ValueError("Feedback requires an evaluated split and measured outcome")
        if not isinstance(payload["metrics"], dict):
            raise ValueError("Feedback metrics must be an object")
        if payload["outcome"] in {"positive", "negative"} and not payload["metrics"]:
            raise ValueError("Performance feedback requires measured metrics")
        text(payload["failure_type"], "failure_type", 200)
        for key, value in payload["metrics"].items():
            if not isinstance(key, str) or isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("Metric values must be finite numbers")
            import math
            if not math.isfinite(value):
                raise ValueError("Metric values must be finite numbers")
        text(payload["notes"], "feedback notes")
        return self.append(kind="feedback", run_id="external_" + text(payload["evaluation_id"], "evaluation_id", 200),
            logical_id=text(payload["expression_id"], "expression_id", 200), dataset_id=payload["dataset_id"], family=payload["family"],
            data_end=payload["evaluation_end"], available_at=payload["available_at"], split=payload["split"], outcome=payload["outcome"],
            payload={**payload, "source_artifact": str(source_path.resolve()), "verification": "external_feedback_imported_not_recomputed"})


class MemorySnapshot:
    def __init__(self, research_end, knowledge_cutoff, records, limit):
        self.research_end, self.knowledge_cutoff, self.records, self.limit = research_end, knowledge_cutoff, records, limit
        self.by_id = {record["record_id"]: record for record in records}

    def as_dict(self):
        return {"research_end": self.research_end, "knowledge_cutoff": self.knowledge_cutoff,
                "record_limit": self.limit, "bounded_snapshot": True, "records": self.records,
                "policy": "Evaluated data end and availability must both fit the run. Final-test feedback is excluded. Current-run writes do not change this snapshot."}

    @staticmethod
    def observation(record: dict) -> dict:
        """Keep model context bounded; full provenance remains in the frozen artifact."""
        common = {key: record[key] for key in ("record_id", "kind", "dataset_id", "family", "data_end", "available_at", "split", "outcome")}
        payload = record["payload"]
        fields = {
            "idea": ("idea_id", "title", "mechanism", "signal_concept", "required_fields", "expected_return_direction", "forecast_horizon_days", "failure_modes", "status", "field_blockers", "prediction_status", "novelty_status"),
            "expression": ("expression_id", "idea_id", "expression", "canonical", "fields", "registry_fingerprint", "forecast_horizon_days", "status", "field_blockers", "alignment_explanation", "prediction_status", "novelty_status"),
            "attempt": ("attempt_id", "idea_id", "expression", "status", "reason", "interpretation"),
            "feedback": ("evaluation_id", "expression_id", "evaluation_end", "split", "outcome", "failure_type", "metrics", "notes", "verification"),
        }
        summarized = {key: payload[key] for key in fields[record["kind"]] if key in payload}
        validation = payload.get("numerical_validation", payload.get("validation"))
        if isinstance(validation, dict):
            summarized["numerical_validation"] = {key: validation[key] for key in ("passed", "failure_reasons", "finite_count", "coverage") if key in validation}
        common["payload"] = summarized
        return common

    def search(self, query: str = "", dataset_id: str | None = None, family: str | None = None, limit: int = 8) -> list[dict]:
        bounded_int(limit, "search limit", 1, 20)
        tokens = set(re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", query.lower()))
        candidates = [r for r in self.records if (dataset_id is None or r["dataset_id"] == dataset_id) and (family is None or r["family"] == family)]
        def score(record):
            body = json.dumps(record["payload"], ensure_ascii=False).lower()
            return sum(token in body for token in tokens), record["row_id"]
        candidates.sort(key=score, reverse=True)
        # Reserve room for differing outcomes instead of returning only historical winners.
        chosen = []
        for group in ({"positive"}, {"negative", "implementation_error", "data_error", "redundant"}, {"unmeasured", "inconclusive"}):
            match = next((record for record in candidates if record["outcome"] in group and record not in chosen), None)
            if match and len(chosen) < limit:
                chosen.append(match)
        for record in candidates:
            if record not in chosen and len(chosen) < limit:
                chosen.append(record)
        return [self.observation(record) for record in chosen]

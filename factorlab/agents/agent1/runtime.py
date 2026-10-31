"""Compile validated analysis specifications into replayable Python scripts."""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

from . import __version__
from .core import Config, clean_json, dump_json, read_json, sha256_file, source_path, validate_spec


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


class RunContext:
    def __init__(self, config: Config, manifest: dict, run_dir: Path):
        self.config, self.manifest, self.run_dir = config, manifest, run_dir
        self.datasets = {d["dataset_id"]: d for d in manifest["datasets"]}
        self.results: list[dict] = []
        self.failures: list[dict] = []
        self.interpretations: list[dict] = []
        self.followups: list[str] = []
        self.scripts_used = 0
        self.active_analysis = None
        self.tool_calls = 0
        self.llm_usage: list[dict] = []
        self.llm_status = "not_requested" if config.mode == "offline" else "pending"
        self.started_at = utc_now()
        self.project_root = Path(__file__).resolve().parent.parent
        for name in ("scripts", "jobs", "analysis", "logs"):
            (run_dir / name).mkdir(parents=True, exist_ok=True)
        dump_json(run_dir / "input_manifest.json", manifest)
        dump_json(run_dir / "resolved_config.json", config)
        self.save_state("running")

    def log(self, event: str, **values) -> None:
        record = {"time_utc": utc_now(), "event": event, **values}
        with (self.run_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(clean_json(record), ensure_ascii=False, allow_nan=False) + "\n")

    def save_state(self, status: str) -> None:
        dump_json(self.run_dir / "run_state.json", {"schema_version": "1.0", "version": __version__, "status": status,
            "started_at": self.started_at, "updated_at": utc_now(), "mode": self.config.mode,
            "scripts_used": self.scripts_used, "tool_calls": self.tool_calls, "llm_status": self.llm_status,
            "active_analysis": self.active_analysis,
            "completed_analyses": [r["analysis_id"] for r in self.results], "failures": self.failures,
            "llm_usage": self.llm_usage})

    def run_analysis(self, arguments: dict) -> dict:
        dataset = self.datasets.get(arguments.get("dataset_id"))
        if dataset is None:
            raise ValueError("Unknown dataset_id; use IDs in the input manifest")
        spec = validate_spec(arguments, dataset)
        if self.scripts_used >= self.config.max_scripts:
            raise ValueError("Script execution budget exhausted")
        for result in self.results:
            if result["dataset_id"] == spec["dataset_id"] and result["spec"]["analyses"] == spec["analyses"] and result["spec"]["columns"] == spec["columns"]:
                return {"cached": True, **self.result_observation(result)}
        self.scripts_used += 1
        analysis_id = f"eda_{self.scripts_used:03d}"
        job_path = self.run_dir / "jobs" / f"{analysis_id}.json"
        result_path = self.run_dir / "analysis" / f"{analysis_id}.json"
        script_path = self.run_dir / "scripts" / f"{analysis_id}.py"
        code_files = [Path(__file__).with_name(name) for name in ("core.py", "analysis.py")]
        code_hashes = {str(p): sha256_file(p) for p in code_files}
        frozen_dataset = {**dataset, "selected_files": [
            {**item, "sha256": sha256_file(source_path(Path(self.config.data_root), item["path"]))}
            for item in dataset["selected_files"]]}
        job = {"analysis_id": analysis_id, "config": dataclasses.asdict(self.config), "dataset": frozen_dataset,
               "spec": spec, "output_path": str(result_path), "code_sha256": code_hashes}
        dump_json(job_path, job)
        # Model-supplied values are JSON data, never interpolated as executable code.
        script = (
            '"""Generated EDA script: inspect the job JSON for its specification and rationale.\n'
            'Replay with the same data and installed project dependencies.\n"""\n'
            'import sys\nimport os\nfrom pathlib import Path\n'
            f'sys.path.insert(0, {str(self.project_root)!r})\n'
            'from agent1.core import read_json, sha256_file\n'
            'from agent1.analysis import execute_job\n'
            f'job_path = Path({str(job_path)!r})\n'
            'os.environ["MPLCONFIGDIR"] = str(job_path.parent.parent / ".matplotlib")\n'
            'job = read_json(job_path)\n'
            'for source, expected in job["code_sha256"].items():\n'
            '    if sha256_file(Path(source)) != expected:\n'
            '        raise RuntimeError("Analysis implementation changed; create a new run instead of silently replaying different code")\n'
            'execute_job(job_path)\n'
        )
        script_path.write_text(script, encoding="utf-8")
        self.log("analysis_started", analysis_id=analysis_id, spec=spec, script=str(script_path))
        self.active_analysis = analysis_id
        self.save_state("running")
        print(f"[{analysis_id}] {dataset['name']}: {', '.join(spec['analyses'])}", flush=True)
        # This is a restricted recipe executor, not a security sandbox for arbitrary Python.
        allowed_env = {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "LANG", "LC_ALL", "APPDATA", "LOCALAPPDATA", "USERPROFILE"}
        environment = {key: value for key, value in os.environ.items() if key.upper() in allowed_env}
        environment["MPLCONFIGDIR"] = str(self.run_dir / ".matplotlib")
        environment["OMP_NUM_THREADS"] = "1"
        try:
            with (self.run_dir / "logs" / f"{analysis_id}.stdout.txt").open("w", encoding="utf-8") as stdout, (self.run_dir / "logs" / f"{analysis_id}.stderr.txt").open("w", encoding="utf-8") as stderr:
                with subprocess.Popen([sys.executable, "-P", str(script_path)], cwd=self.run_dir, env=environment, stdout=stdout, stderr=stderr) as process:
                    try:
                        returncode = process.wait(timeout=self.config.script_timeout_seconds)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                        raise TimeoutError(f"Analysis exceeded {self.config.script_timeout_seconds}s; see logs/{analysis_id}.stdout.txt") from None
            if returncode:
                raise RuntimeError(f"Analysis process exited {returncode}; see logs/{analysis_id}.stderr.txt")
            result = read_json(result_path)
            if result["analysis_id"] != analysis_id or result["dataset_id"] != dataset["dataset_id"]:
                raise ValueError("Analysis output identity mismatch")
            self.results.append(result)
            self.active_analysis = None
            self.log("analysis_completed", analysis_id=analysis_id, status=result["status"], scope=result["scope"])
            self.save_state("running")
            return self.result_observation(result)
        except Exception as error:
            failure = {"analysis_id": analysis_id, "dataset_id": dataset["dataset_id"], "error": f"{type(error).__name__}: {error}"}
            self.failures.append(failure)
            self.active_analysis = None
            self.log("analysis_failed", **failure)
            self.save_state("running")
            return {"ok": False, **failure}

    @staticmethod
    def result_observation(result: dict) -> dict:
        # Large daily sequences and source lists stay on disk instead of filling model context.
        return {"ok": result["status"] != "failed", "analysis_id": result["analysis_id"], "dataset_id": result["dataset_id"],
            "status": result["status"], "scope": result["scope"], "quality": result["quality"], "date_range": result["date_range"],
            "warnings": result["warnings"], "evidence_index": [
                {"evidence_id": e["evidence_id"], "category": e["category"], "column": e["metrics"].get("column")}
                for e in result["evidence"]]}

    def evidence(self) -> dict[str, dict]:
        return {e["evidence_id"]: e for result in self.results for e in result["evidence"]}


def create_run_dir(config: Config) -> Path:
    source, output = Path(config.data_root).resolve(), Path(config.output_root).resolve()
    if output == source or output.is_relative_to(source):
        raise ValueError("output_root must be outside data_root to keep source discovery read-only and unambiguous")
    run_name = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    run_dir = output / run_name
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir

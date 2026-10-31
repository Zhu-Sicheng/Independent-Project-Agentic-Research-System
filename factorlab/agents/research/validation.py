"""Cutoff-filtered numerical previews and replayable factor-computation jobs."""

from __future__ import annotations

import dataclasses
import math
from pathlib import Path

import numpy as np
import pandas as pd

from agent1.core import dump_json, load_source, parse_dates, read_json, sha256_file
from .common import EDABundle, ExpressionConfig, digest
from .expressions import ExpressionCompiler
from .operators import OperatorRegistry


class FactorValidator:
    def __init__(self, bundle: EDABundle, registry: OperatorRegistry, config: ExpressionConfig):
        self.bundle, self.registry, self.config = bundle, registry, config
        self.cache = {}

    def load(self, dataset_id: str) -> dict:
        if dataset_id in self.cache:
            return self.cache[dataset_id]
        dataset = self.bundle.source_datasets[dataset_id]
        date_column, entity_column = dataset["date_column"], dataset["entity_column"]
        if not date_column:
            raise ValueError("Numerical factor validation requires an observation date")
        profiles = [self.bundle.root / artifact for artifact in self.bundle.datasets[dataset_id]["analysis_artifacts"]]
        successful = [profile for profile in (read_json(path) for path in profiles) if profile["status"] == "completed"]
        if not successful:
            raise ValueError("No completed source profile is available")
        expected_sources = {source["path"]: source for source in successful[-1]["sources"]}
        selected = dataset["selected_files"][:self.config.validation_max_files]
        if entity_column is None and len(selected) != 1:
            raise ValueError("Multiple files without an entity key require an explicit merge contract")
        candidate_names = list(self.bundle.candidate_fields(dataset_id))
        pieces, provenance, conversion_failures = [], [], {name: 0 for name in candidate_names}
        for item in selected:
            if item["path"] not in expected_sources:
                raise ValueError("Preview source was not profiled by Agent 1")
            frame, info = load_source(Path(self.bundle.eda_config.data_root), {**item, "sha256": expected_sources[item["path"]]["sha256"]}, dataset, self.bundle.eda_config)
            if frame.empty:
                provenance.append(info)
                continue
            work = pd.DataFrame({"date": parse_dates(frame[date_column]),
                "entity": frame[entity_column].astype("string") if entity_column else "single_series"})
            if work[["date", "entity"]].isna().any().any():
                raise ValueError("Null observation keys must be resolved before factor computation")
            for name in candidate_names:
                values = pd.to_numeric(frame[name], errors="coerce")
                conversion_failures[name] += int((frame[name].notna() & values.isna()).sum())
                work[name] = values.replace([np.inf, -np.inf], np.nan)
            pieces.append(work)
            provenance.append(info)
        if not pieces:
            raise ValueError("No observations at or before the research cutoff")
        combined = pd.concat(pieces, ignore_index=True)
        if combined.duplicated(["date", "entity"]).any():
            raise ValueError("Duplicate observation keys across preview files; no silent deduplication")
        entities_all = sorted(combined["entity"].astype(str).unique())
        entities = entities_all[:self.config.validation_max_entities]
        combined = combined.loc[combined["entity"].isin(entities)].sort_values(["date", "entity"], kind="stable")
        panels = {name: combined.pivot(index="date", columns="entity", values=name).sort_index().astype(float) for name in candidate_names}
        scope = {"research_end": self.bundle.research_end, "files_selected": len(selected),
            "files_profiled_by_agent1": len(dataset["selected_files"]), "entities_selected": entities,
            "entities_in_selected_files": len(entities_all), "observations": len(combined),
            "date_min": combined["date"].min().isoformat(), "date_max": combined["date"].max().isoformat(),
            "sample_only": True, "file_selection": "lexicographic_prefix_of_agent1_profiled_files",
            "entity_selection": "lexicographic_prefix", "time_selection": "same_file_prefix_and_cutoff_as_agent1",
            "source_records": provenance, "numeric_conversion_failures": conversion_failures,
            "historical_universe_filter_applied": False}
        scope["data_fingerprint"] = digest([scope["source_records"], entities, self.bundle.fingerprints, self.bundle.research_end])
        self.cache[dataset_id] = {"panels": panels, "scope": scope}
        return self.cache[dataset_id]

    def evaluate(self, compiled, dataset_id: str) -> tuple[dict, pd.DataFrame]:
        loaded = self.load(dataset_id)
        panels = loaded["panels"]
        raw = compiled.evaluate(panels)
        example = next(iter(panels.values()))
        if not raw.index.equals(example.index) or not raw.columns.equals(example.columns):
            raise ValueError("Expression changed the date/entity axes")
        input_mask = pd.DataFrame(True, index=example.index, columns=example.columns)
        for field in compiled.info.fields:
            input_mask &= panels[field].notna()
        # Same-day close and volume are never treated as known at that day's execution.
        lag = self.config.execution_lag
        factor = raw.shift(lag).where(input_mask.shift(lag, fill_value=False))
        values = factor.to_numpy(dtype=float)
        infinity_count = int(np.isinf(values).sum())
        factor = factor.replace([np.inf, -np.inf], np.nan)
        values = factor.to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        expected = int(input_mask.shift(lag, fill_value=False).to_numpy().sum())
        coverage = len(finite) / expected if expected else 0.0
        unique = len(np.unique(finite))
        reasons = []
        if len(finite) < self.config.min_validation_points:
            reasons.append("insufficient_finite_preview_points")
        if coverage < self.config.min_coverage:
            reasons.append("low_preview_coverage")
        if unique <= 1:
            reasons.append("constant_or_empty_preview")
        if infinity_count:
            reasons.append("infinite_output_before_masking")
        finite_positions = np.isfinite(factor).any(axis=1)
        result = {"passed": not reasons, "failure_reasons": reasons, "finite_count": len(finite),
            "eligible_input_cells_after_lag": expected, "coverage": coverage, "unique_values": unique,
            "mean": float(finite.mean()) if len(finite) else None,
            "std_population": float(finite.std()) if len(finite) else None,
            "min": float(finite.min()) if len(finite) else None, "max": float(finite.max()) if len(finite) else None,
            "infinite_output_count": infinity_count, "execution_lag": lag,
            "first_finite_signal_date": factor.index[finite_positions][0].isoformat() if finite_positions.any() else None,
            "last_finite_signal_date": factor.index[finite_positions][-1].isoformat() if finite_positions.any() else None,
            "scope": loaded["scope"],
            "interpretation": "Numerical executability on a bounded historical sample, not IC, returns, trading feasibility or alpha evidence."}
        return result, factor


def export_preview(factor: pd.DataFrame, path: Path, limit: int) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not limit:
        return 0
    frame = factor.rename_axis(index="date", columns="entity").reset_index().melt(id_vars="date", var_name="entity", value_name="factor_value").dropna(subset=["factor_value"])
    frame = frame.sort_values(["date", "entity"], kind="stable").tail(limit)
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    return len(frame)


def write_expression_job(root: Path, bundle: EDABundle, registry: OperatorRegistry, config: ExpressionConfig, idea: dict, candidate: dict) -> str:
    identity = candidate["expression_id"]
    for name in ("jobs", "scripts", "validation", "previews"):
        (root / name).mkdir(parents=True, exist_ok=True)
    modules = [Path(__file__), Path(__file__).with_name("operators.py"), Path(__file__).with_name("expressions.py"),
               Path(__file__).with_name("common.py"), Path(__file__).parent.parent / "agent1" / "core.py"]
    job = {"schema_version": "1.0", "agent1_run": str(bundle.root), "upstream_sha256": bundle.fingerprints,
        "registry_fingerprint": registry.fingerprint, "config": dataclasses.asdict(config), "idea": idea,
        "candidate": candidate, "output_root": str(root.resolve()), "code_sha256": {str(path): sha256_file(path) for path in modules}}
    job_path = root / "jobs" / f"{identity}.json"
    dump_json(job_path, job)
    project = Path(__file__).resolve().parent.parent
    script = '"""Replay this research-only factor preview; no database writes or backtest."""\nimport sys\nfrom pathlib import Path\n'
    script += f"sys.path.insert(0, {str(project)!r})\nfrom research.validation import replay_expression\n"
    script += f"replay_expression(Path({str(job_path.resolve())!r}))\n"
    (root / "scripts" / f"{identity}.py").write_text(script, encoding="utf-8")
    return f"scripts/{identity}.py"


def replay_expression(job_path: Path):
    job = read_json(job_path)
    for name, expected in job["code_sha256"].items():
        if sha256_file(Path(name)) != expected:
            raise ValueError("Factor implementation changed; create a new run")
    bundle = EDABundle(job["agent1_run"])
    if bundle.fingerprints != job["upstream_sha256"]:
        raise ValueError("Upstream EDA/field contract changed")
    config = ExpressionConfig.from_dict(job["config"])
    registry = OperatorRegistry(config.operator_file)
    if registry.fingerprint != job["registry_fingerprint"]:
        raise ValueError("Operator registry or source document changed")
    idea, candidate = job["idea"], job["candidate"]
    compiled = ExpressionCompiler(registry, config).compile(candidate["expression"], bundle.fields[idea["dataset_id"]], idea["required_fields"])
    if set(compiled.info.fields) != set(idea["required_fields"]):
        raise ValueError("Expression does not cover the full hypothesis input requirements")
    if not config.allow_unapproved_dry_run and any(bundle.fields[idea["dataset_id"]][name]["factor_usage"] != "eligible" for name in compiled.info.fields):
        raise ValueError("Unapproved fields cannot be previewed under this configuration")
    result, factor = FactorValidator(bundle, registry, config).evaluate(compiled, idea["dataset_id"])
    root = Path(job["output_root"])
    dump_json(root / "validation" / f"{candidate['expression_id']}.json", result)
    export_preview(factor, root / "previews" / f"{candidate['expression_id']}.csv", config.preview_rows)
    return result

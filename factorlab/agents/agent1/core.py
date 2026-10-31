"""Configuration, read-only data discovery, bounded loading, and JSON artifacts."""

from __future__ import annotations

import dataclasses
import csv
import fnmatch
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SUPPORTED = {".csv", ".tsv", ".json", ".jsonl", ".parquet", ".xlsx"}
ANALYSES = {"basic", "distribution", "correlation", "time_series", "market_quality", "interval_quality", "text_quality", "drift"}
DATE_NAMES = ("date", "dlycaldt", "yyyymmdd", "datetime", "timestamp", "trade_date", "publication_date", "report_date")
ENTITY_NAMES = ("permno", "ticker", "symbol", "asset_id", "security_id", "instrument")
INTERVAL_PAIRS = (("start_date", "end_date"), ("linkdt", "linkenddt"), ("indfrom", "indthru"))
LLM_KEYS = {"base_url_env", "api_key_env", "model_env", "auth_header", "strict_tools", "timeout_seconds", "max_retries", "max_output_tokens", "token_parameter", "temperature", "max_total_tokens"}


def clean_json(value: Any) -> Any:
    """Produce strict JSON: NaN/Inf become null; numpy scalars become native values."""
    if dataclasses.is_dataclass(value):
        return clean_json(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [clean_json(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, (pd.Timestamp, Path)):
        return str(value)
    return value


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(clean_json(value), ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_forward_label(column: str) -> bool:
    """Conservatively recognize common target names; unknown semantics still need review."""
    name = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
    return bool(name in {"target", "label", "y"} or re.match(r"^(target|label)_", name)
                or re.search(r"(forward|future|fwd|next).*ret|ret.*(forward|future|fwd|next)", name))


@dataclasses.dataclass
class Config:
    data_root: str = "data"
    output_root: str = "outputs/agent1"
    mode: str = "offline"
    research_end: str | None = None
    include: list[str] = dataclasses.field(default_factory=lambda: ["*"])
    exclude: list[str] = dataclasses.field(default_factory=list)
    max_files_per_dataset: int = 0  # 0 means all discovered files in each schema group.
    max_rows_per_file: int = 20000  # Prefix cap, explicitly reported; 0 means no cap.
    sample_size: int = 5000
    max_scripts: int = 24
    max_llm_turns: int = 16
    max_tool_calls: int = 32
    script_timeout_seconds: int = 600
    seed: int = 42
    plots: bool = True
    llm: dict = dataclasses.field(default_factory=dict)
    overrides: list[dict] = dataclasses.field(default_factory=list)
    # Optional reviewed field metadata belongs in overrides, never in model output.

    @classmethod
    def from_dict(cls, values: dict) -> "Config":
        unknown = set(values) - {f.name for f in dataclasses.fields(cls)}
        if unknown:
            raise ValueError(f"Unknown configuration keys: {sorted(unknown)}")
        config = cls(**values)
        config.validate()
        return config

    def validate(self) -> None:
        if self.mode not in {"offline", "llm"}:
            raise ValueError("mode must be offline or llm")
        if not self.research_end:
            raise ValueError("An explicit research_end (YYYY-MM-DD) is required; no implicit full-history EDA.")
        try:
            import datetime
            datetime.date.fromisoformat(self.research_end)
        except (TypeError, ValueError) as error:
            raise ValueError("research_end must be a valid YYYY-MM-DD date") from error
        for name in ("max_files_per_dataset", "max_rows_per_file", "sample_size", "max_scripts", "max_llm_turns", "max_tool_calls", "script_timeout_seconds", "seed"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if min(self.sample_size, self.max_scripts, self.max_llm_turns, self.max_tool_calls, self.script_timeout_seconds) < 1:
            raise ValueError("Sample size, execution timeout, and budgets must be positive")
        for name in ("include", "exclude"):
            value = getattr(self, name)
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise ValueError(f"{name} must be a list of glob strings")
        if not isinstance(self.llm, dict) or not isinstance(self.overrides, list):
            raise ValueError("llm must be an object and overrides must be a list")
        if set(self.llm) - LLM_KEYS:
            raise ValueError("Unknown llm settings. Store credentials in environment variables, never configuration files.")
        for key in ("timeout_seconds", "max_output_tokens", "max_total_tokens"):
            if key in self.llm and (isinstance(self.llm[key], bool) or not isinstance(self.llm[key], int) or self.llm[key] <= 0):
                raise ValueError(f"llm.{key} must be a positive integer")
        if "strict_tools" in self.llm and not isinstance(self.llm["strict_tools"], bool):
            raise ValueError("llm.strict_tools must be boolean")
        if not isinstance(self.plots, bool):
            raise ValueError("plots must be boolean")
        allowed_overrides = {"pattern", "kind", "date_column", "entity_column", "fields", "description", "encoding", "delimiter", "sheet_name"}
        for rule in self.overrides:
            if not isinstance(rule, dict) or not isinstance(rule.get("pattern"), str) or set(rule) - allowed_overrides:
                raise ValueError("Invalid dataset override; see configs/agent1.example.json")
            if "fields" in rule and not isinstance(rule["fields"], dict):
                raise ValueError("override.fields must be an object")
            for field_name, metadata in rule.get("fields", {}).items():
                if not isinstance(metadata, dict) or set(metadata) - {"description", "unit", "availability", "point_in_time_verified", "approved_for_factor", "adjustment"}:
                    raise ValueError(f"Invalid field metadata for {field_name}")
                for flag in ("point_in_time_verified", "approved_for_factor"):
                    if flag in metadata and not isinstance(metadata[flag], bool):
                        raise ValueError(f"{field_name}.{flag} must be boolean")
                for text_key in ("description", "unit", "availability", "adjustment"):
                    if metadata.get(text_key) is not None and not isinstance(metadata[text_key], str):
                        raise ValueError(f"{field_name}.{text_key} must be a string or null")


def match_override(relative_path: str, config: Config) -> dict:
    result: dict = {}
    for rule in config.overrides:
        if fnmatch.fnmatchcase(relative_path, rule["pattern"]):
            result.update({k: v for k, v in rule.items() if k != "pattern"})
    return result


def source_path(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ValueError("Source path escapes data_root")
    if not candidate.is_file():
        raise ValueError(f"Source file does not exist: {relative}")
    return candidate


def parse_dates(series: pd.Series) -> pd.Series:
    """Handle YYYYMMDD integers explicitly, never as Unix nanoseconds; normalize to UTC."""
    text = series.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    compact = text.str.fullmatch(r"\d{8}", na=False)
    result = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns, UTC]")
    if compact.any():
        result.loc[compact] = pd.to_datetime(text.loc[compact], format="%Y%m%d", errors="coerce", utc=True)
    if (~compact).any():
        other = text.loc[~compact]
        # pandas 2+ accepts mixed ISO/date formats explicitly; pandas 1.x parses per value.
        if int(pd.__version__.split(".")[0]) >= 2:
            result.loc[~compact] = pd.to_datetime(other, format="mixed", errors="coerce", utc=True)
        else:
            result.loc[~compact] = pd.to_datetime(other, errors="coerce", utc=True)
    return result


def read_table(path: Path, limit: int, options: dict | None = None) -> tuple[pd.DataFrame, bool]:
    options = options or {}
    wanted = limit + 1 if limit else None
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        encoding = options.get("encoding", "utf-8-sig")
        kwargs = {"sep": options.get("delimiter", "\t" if suffix == ".tsv" else ","), "nrows": wanted, "low_memory": False}
        # Keep identifier-like columns as strings to preserve leading zeroes.
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                raw_header = next(csv.reader(handle, delimiter=kwargs["sep"]), [])
            if len(set(raw_header)) != len(raw_header):
                raise ValueError("Duplicate CSV headers must be resolved explicitly")
            header = pd.read_csv(path, encoding=encoding, nrows=0, sep=kwargs["sep"])
            identifiers = {c: "string" for c in header.columns if str(c).lower() in set(ENTITY_NAMES) | {"gvkey", "permco", "cusip", "cusip9"}}
            frame = pd.read_csv(path, encoding=encoding, dtype=identifiers, **kwargs)
        except UnicodeDecodeError:
            if "encoding" in options:
                raise
            frame = pd.read_csv(path, encoding="gb18030", dtype=str, **kwargs)
    elif suffix == ".jsonl":
        frame = pd.read_json(path, lines=True, nrows=wanted, convert_dates=False)
    elif suffix == ".json":
        # JSON arrays and Excel are materialized by their readers before the row cap.
        frame = pd.read_json(path, convert_dates=False)
    elif suffix == ".xlsx":
        frame = pd.read_excel(path, nrows=wanted, sheet_name=options.get("sheet_name", 0))
    elif suffix == ".parquet":
        import pyarrow.parquet as pq
        parquet = pq.ParquetFile(path)
        if wanted:
            pieces, count = [], 0
            for batch in parquet.iter_batches(batch_size=min(wanted, 65536)):
                pieces.append(batch.to_pandas())
                count += batch.num_rows
                if count >= wanted:
                    break
            frame = pd.concat(pieces, ignore_index=True) if pieces else parquet.read().to_pandas()
        else:
            frame = parquet.read().to_pandas()
    else:
        raise ValueError(f"Unsupported format: {suffix}")
    frame.columns = [str(c) for c in frame.columns]
    if len(set(frame.columns)) != len(frame.columns):
        raise ValueError("Duplicate column names must be resolved before EDA")
    if suffix in {".json", ".jsonl"}:
        for column in frame.columns:
            if frame[column].map(lambda value: isinstance(value, (dict, list, tuple, set))).any():
                raise ValueError("Nested JSON cells require explicit flattening before tabular EDA")
    truncated = bool(limit and len(frame) > limit)
    return frame.iloc[:limit].copy() if limit else frame, truncated


def infer_structure(columns: list[str], names: list[str], options: dict) -> dict:
    lower = {c.lower(): c for c in columns}
    date = next((lower[c] for c in DATE_NAMES if c in lower), None)
    entity = next((lower[c] for c in ENTITY_NAMES if c in lower), None)
    pairs = [(lower[a], lower[b]) for a, b in INTERVAL_PAIRS if a in lower and b in lower]
    has_close = any(c in lower for c in ("close", "adj_close", "dlyclose", "dlyprc"))
    if date and has_close:
        kind = "market_ohlcv"
    elif pairs:
        kind = "interval_reference"
    elif any(c in lower for c in ("headline", "text", "body", "content", "news")):
        kind = "text_events"
    elif date:
        kind = "time_series"
    else:
        kind = "reference_table" if entity or len(columns) < 4 else "tabular"
    date = options.get("date_column", date)
    entity = options.get("entity_column", entity)
    for value in (date, entity):
        if value is not None and value not in columns:
            raise ValueError(f"Configured column {value!r} is absent from schema")
    return {"kind": options.get("kind", kind), "kind_source": "config" if "kind" in options else "column_name_heuristic",
            "date_column": date, "entity_column": entity, "interval_pairs": pairs,
            "inference_note": "Schema inference is provisional; field names do not verify financial semantics or availability."}


def discover(config: Config) -> dict:
    root = Path(config.data_root).resolve()
    if not root.is_dir():
        raise ValueError(f"data_root must be an existing directory: {root}")
    groups: dict[str, dict] = {}
    skipped: list[dict] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if not any(fnmatch.fnmatchcase(relative, pattern) for pattern in config.include) or any(fnmatch.fnmatchcase(relative, pattern) for pattern in config.exclude):
            continue
        if not path.resolve().is_relative_to(root):
            skipped.append({"file": relative, "reason": "symlink escapes data_root"})
            continue
        if path.suffix.lower() not in SUPPORTED:
            skipped.append({"file": relative, "reason": "unsupported extension"})
            continue
        options = match_override(relative, config)
        try:
            frame, _ = read_table(path, 3, options)
            columns = list(frame.columns)
            if set(options.get("fields", {})) - set(columns):
                raise ValueError("Configured field metadata references columns absent from the schema")
            # Group only same-directory files with identical ordered schema and metadata.
            signature = json.dumps([str(path.parent.relative_to(root)), path.suffix.lower(), columns, options], sort_keys=True, ensure_ascii=False)
            dataset_id = "ds_" + hashlib.sha256(signature.encode()).hexdigest()[:12]
            if dataset_id not in groups:
                groups[dataset_id] = {"dataset_id": dataset_id, "name": relative, "columns": columns,
                    "sample_dtypes": {c: str(frame[c].dtype) for c in columns}, "files": [], "options": options,
                    **infer_structure(columns, [relative], options)}
            stat = path.stat()
            groups[dataset_id]["files"].append({"path": relative, "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns})
        except Exception as error:
            skipped.append({"file": relative, "reason": f"{type(error).__name__}: {error}"})
    datasets = list(groups.values())
    for dataset in datasets:
        all_files = dataset["files"]
        cap = config.max_files_per_dataset
        dataset["selected_files"] = all_files[:cap] if cap else list(all_files)
        dataset["file_selection"] = "all" if len(dataset["selected_files"]) == len(all_files) else "lexicographic_prefix"
        dataset["discovered_file_count"] = len(all_files)
    if not datasets:
        raise ValueError(f"No readable supported datasets found. Details: {skipped[:5]}")
    return {"schema_version": "1.0", "data_root": str(root), "research_end": config.research_end,
            "date_policy": "Naive dates/timestamps are interpreted as UTC; timestamped event datasets require reviewed timezone metadata before factor use.",
            "inventory_scope": "File names and schemas may span the source directory; analytical values are cutoff-filtered. Inventory does not establish historical universe membership.",
            "datasets": datasets, "skipped_files": skipped}


def load_source(root: Path, file_info: dict, dataset: dict, config: Config) -> tuple[pd.DataFrame, dict]:
    path = source_path(root, file_info["path"])
    before = path.stat()
    if before.st_size != file_info["bytes"] or before.st_mtime_ns != file_info["mtime_ns"]:
        raise ValueError(f"Source changed after discovery: {file_info['path']}")
    digest = sha256_file(path)
    if file_info.get("sha256") and digest != file_info["sha256"]:
        raise ValueError(f"Source content fingerprint changed: {file_info['path']}")
    frame, truncated = read_table(path, config.max_rows_per_file, dataset["options"])
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f"Source changed during analysis: {file_info['path']}")
    if list(frame.columns) != dataset["columns"]:
        raise ValueError(f"Source schema changed: {file_info['path']}")
    info = {"path": file_info["path"], "sha256": digest, "rows_read": len(frame), "row_cap_reached": truncated,
            "rows_after_cutoff": 0, "rows_with_invalid_time": 0, "cutoff_applied": False}
    date_column = dataset["date_column"]
    # Interval tables are filtered by interval start; end dates are context, never features.
    if date_column is None and dataset["interval_pairs"]:
        date_column = dataset["interval_pairs"][0][0]
    if date_column:
        boundary = pd.Timestamp(config.research_end, tz="UTC") + pd.Timedelta(days=1)
        date_columns = [date_column] if dataset["date_column"] else [pair[0] for pair in dataset["interval_pairs"]]
        invalid = pd.Series(False, index=frame.index)
        future = pd.Series(False, index=frame.index)
        for time_column in date_columns:
            dates = parse_dates(frame[time_column])
            invalid |= dates.isna()
            future |= dates >= boundary
        info.update(rows_after_cutoff=int(future.sum()), rows_with_invalid_time=int(invalid.sum()), cutoff_applied=True)
        frame = frame.loc[~invalid & ~future].copy()
        if not dataset["date_column"]:
            # Future endpoints are not exposed as historical facts to the model.
            for _, end_column in dataset["interval_pairs"]:
                ends = parse_dates(frame[end_column])
                beyond = ends >= boundary
                frame[end_column] = frame[end_column].astype("string")
                frame.loc[beyond, end_column] = str(config.research_end)
            info["reference_endpoints_clipped_to_cutoff"] = True
    info["rows_analyzed"] = len(frame)
    info["temporal_scope"] = "cutoff_filtered" if date_column else "undated_reference_not_point_in_time_verified"
    suppressed = [column for column in frame.columns if is_forward_label(column)]
    for column in suppressed:
        # Only the schema of recognized labels is exposed. Even their distributions can leak information.
        frame[column] = pd.NA
    info["suppressed_label_columns"] = suppressed
    return frame, info


def validate_spec(arguments: dict, dataset: dict) -> dict:
    if set(arguments) != {"dataset_id", "analyses", "columns", "rationale"}:
        raise ValueError("Analysis specification requires exactly dataset_id, analyses, columns, rationale")
    if arguments["dataset_id"] != dataset["dataset_id"]:
        raise ValueError("Dataset ID mismatch")
    analyses = arguments["analyses"]
    if not isinstance(analyses, list) or not analyses or any(not isinstance(a, str) or a not in ANALYSES for a in analyses):
        raise ValueError(f"analyses must be a nonempty list from {sorted(ANALYSES)}")
    columns = arguments["columns"]
    if not isinstance(columns, list) or len(columns) > 20 or any(not isinstance(c, str) or c not in dataset["columns"] for c in columns):
        raise ValueError("columns must contain at most 20 existing column names")
    if not isinstance(arguments["rationale"], str) or not 1 <= len(arguments["rationale"]) <= 2000:
        raise ValueError("rationale must be 1..2000 characters")
    if "time_series" in analyses or "drift" in analyses:
        if not dataset["date_column"]:
            raise ValueError("time_series/drift require a confirmed date column in the schema")
    if "market_quality" in analyses and dataset["kind"] != "market_ohlcv":
        raise ValueError("market_quality requires a market_ohlcv dataset")
    if "interval_quality" in analyses and not dataset["interval_pairs"]:
        raise ValueError("interval_quality requires recognized start/end columns")
    return {**arguments, "analyses": list(dict.fromkeys(analyses)), "columns": list(dict.fromkeys(columns))}

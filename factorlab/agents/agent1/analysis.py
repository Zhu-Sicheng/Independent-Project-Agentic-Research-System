"""Streaming EDA tools. Numerical evidence is computed here, never by an LLM."""

from __future__ import annotations

import collections
import dataclasses
import platform
from pathlib import Path

import numpy as np
import pandas as pd

from .core import Config, dump_json, is_forward_label, load_source, parse_dates, read_json


@dataclasses.dataclass
class NumericAccumulator:
    count: int = 0
    mean: float = 0.0
    m2: float = 0.0
    minimum: float = float("inf")
    maximum: float = -float("inf")
    zero_count: int = 0
    negative_count: int = 0
    infinite_count: int = 0

    def add(self, series: pd.Series) -> None:
        values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float, na_value=np.nan)
        self.infinite_count += int(np.isinf(values).sum())
        values = values[np.isfinite(values)]
        if not len(values):
            return
        count = len(values)
        mean = float(values.mean())
        m2 = float(np.square(values - mean).sum())
        delta = mean - self.mean
        total = self.count + count
        self.m2 += m2 + delta * delta * self.count * count / total
        self.mean += delta * count / total
        self.count = total
        self.minimum = min(self.minimum, float(values.min()))
        self.maximum = max(self.maximum, float(values.max()))
        self.zero_count += int((values == 0).sum())
        self.negative_count += int((values < 0).sum())

    def result(self, sample: pd.Series | None = None) -> dict:
        result = {"finite_count": self.count, "mean": self.mean if self.count else None,
                  "std_population": float(np.sqrt(max(self.m2, 0) / self.count)) if self.count else None,
                  "min": self.minimum if self.count else None, "max": self.maximum if self.count else None,
                  "zero_count": self.zero_count, "negative_count": self.negative_count, "infinite_count": self.infinite_count}
        if sample is not None:
            values = pd.to_numeric(sample, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            result["quantiles"] = {str(q): float(values.quantile(q)) for q in (0.01, 0.25, 0.5, 0.75, 0.99)} if len(values) else {}
            result["quantile_sample_size"] = len(values)
            result["quantile_method"] = "bounded_uniform_row_sample"
        return result


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


def aliases(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    lower = {c.lower(): c for c in columns}
    return next((lower[name] for name in candidates if name in lower), None)


def market_metrics(frame: pd.DataFrame, dataset: dict) -> dict:
    """Each return is computed inside an entity and inside one source file."""
    columns = list(frame.columns)
    close = aliases(columns, ("adj_close", "close", "dlyclose", "dlyprc"))
    high = aliases(columns, ("adj_high", "high", "dlyhigh"))
    low = aliases(columns, ("adj_low", "low", "dlylow"))
    opn = aliases(columns, ("adj_open", "open", "dlyopen"))
    volume = aliases(columns, ("adj_volume", "volume", "dlyvol"))
    cap = aliases(columns, ("adj_mktcap", "market_cap", "dlycap"))
    result = {"price_nonpositive": 0, "negative_volume": 0, "negative_market_cap": 0,
              "high_below_low": 0, "open_outside_high_low": 0, "close_outside_high_low": 0,
              "extreme_adjacent_return_count": 0, "valid_adjacent_return_count": 0}
    if close:
        prices = numeric(frame[close])
        result["price_nonpositive"] = int((prices <= 0).sum())
        work = pd.DataFrame({"price": prices, "date": parse_dates(frame[dataset["date_column"]])})
        entity = dataset["entity_column"]
        work["entity"] = frame[entity].astype("string") if entity else "single_series"
        work = work.sort_values(["entity", "date"], kind="stable")
        returns = work.groupby("entity", dropna=False)["price"].pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan)
        result["valid_adjacent_return_count"] = int(returns.notna().sum())
        result["extreme_adjacent_return_count"] = int((returns.abs() > 0.5).sum())
    if high and low:
        highs, lows = numeric(frame[high]), numeric(frame[low])
        tolerance = 1e-7 * pd.concat([highs.abs(), lows.abs()], axis=1).max(axis=1).clip(lower=1)
        result["high_below_low"] = int((highs + tolerance < lows).sum())
        for label, column in (("open", opn), ("close", close)):
            if column:
                values = numeric(frame[column])
                result[f"{label}_outside_high_low"] = int(((values > highs + tolerance) | (values < lows - tolerance)).sum())
    if volume:
        result["negative_volume"] = int((numeric(frame[volume]) < 0).sum())
    if cap:
        result["negative_market_cap"] = int((numeric(frame[cap]) < 0).sum())
    return result


def interval_metrics(frame: pd.DataFrame, dataset: dict) -> list[dict]:
    results = []
    for start_col, end_col in dataset["interval_pairs"]:
        starts, ends = parse_dates(frame[start_col]), parse_dates(frame[end_col])
        missing_end = frame[end_col].isna() | frame[end_col].astype("string").str.strip().isin(["", "9999-12-31", "99991231"])
        valid = starts.notna() & ends.notna()
        overlap_count = 0
        entity = dataset["entity_column"]
        if entity:
            work = pd.DataFrame({"entity": frame[entity].astype("string"), "start": starts, "end": ends})
            work = work.loc[starts.notna()].sort_values(["entity", "start"], kind="stable")
            work["end"] = work["end"].fillna(pd.Timestamp("2262-01-01", tz="UTC"))
            for _, part in work.groupby("entity", dropna=False):
                prior_max = part["end"].cummax().shift(1)
                overlap_count += int((part["start"] <= prior_max).sum())
        results.append({"start_column": start_col, "end_column": end_col,
                        "end_before_start": int(((ends < starts) & valid).sum()),
                        "missing_or_open_end": int(missing_end.sum()),
                        "unparsed_start": int((starts.isna() & frame[start_col].notna()).sum()),
                        "unparsed_nonempty_end": int((ends.isna() & ~missing_end).sum()),
                        "potential_inclusive_overlaps_within_file": overlap_count})
    return results


def add_uniform_sample(sample: pd.DataFrame, frame: pd.DataFrame, rng: np.random.Generator, size: int, source: str) -> pd.DataFrame:
    # Independent random priorities implement a uniform row reservoir across unequal file sizes.
    priorities = rng.random(len(frame))
    indices = np.argpartition(priorities, min(size, len(frame)) - 1)[:size] if len(frame) > size else np.arange(len(frame))
    candidate = frame.iloc[indices].copy()
    candidate["__agent1_priority__"] = priorities[indices]
    candidate["__agent1_source__"] = source
    combined = pd.concat([sample, candidate], ignore_index=True) if not sample.empty else candidate
    return combined.nsmallest(size, "__agent1_priority__")


def generate_plots(sample: pd.DataFrame, columns: list[str], dates: collections.Counter, directory: Path) -> tuple[list[str], str | None]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return [], "matplotlib is not installed; numerical analysis completed without plots"
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    with plt.rc_context({"figure.figsize": (8, 4), "axes.grid": True, "grid.alpha": 0.2}):
        for i, column in enumerate(columns[:4]):
            values = numeric(sample[column]).dropna()
            if values.empty:
                continue
            fig, ax = plt.subplots()
            ax.hist(values, bins=40, color="#347d94", edgecolor="white")
            ax.set(title=f"{column}: sampled distribution", xlabel=column, ylabel="Sample count")
            fig.tight_layout()
            path = directory / f"distribution_{i + 1}.png"
            fig.savefig(path, dpi=130)
            plt.close(fig)
            paths.append(path.name)
        if dates:
            ordered = sorted(dates.items())
            fig, ax = plt.subplots()
            ax.plot(pd.to_datetime([x[0] for x in ordered]), [x[1] for x in ordered], color="#347d94")
            ax.set(title="Observed rows per date (analyzed scope)", ylabel="Rows")
            fig.autofmt_xdate()
            fig.tight_layout()
            path = directory / "temporal_coverage.png"
            fig.savefig(path, dpi=130)
            plt.close(fig)
            paths.append(path.name)
    return paths, None


def execute_job(job_path: str | Path) -> dict:
    job = read_json(Path(job_path))
    config = Config.from_dict(job["config"])
    dataset, spec, analysis_id = job["dataset"], job["spec"], job["analysis_id"]
    root, output = Path(config.data_root).resolve(), Path(job["output_path"]).resolve()
    rng = np.random.default_rng(config.seed)
    accumulators = {c: NumericAccumulator() for c in dataset["columns"]}
    missing, observed, dtypes = collections.Counter(), collections.Counter(), collections.defaultdict(set)
    dates, entities, entity_files = collections.Counter(), set(), collections.defaultdict(set)
    market, interval_totals = collections.Counter(), {}
    sample, sources, errors = pd.DataFrame(), [], []
    rows = duplicate_rows = duplicate_keys = null_keys = nonmonotonic_entities = 0
    reserved = {c for c in dataset["columns"] if c.startswith("__agent1_")}
    if reserved:
        raise ValueError(f"Reserved internal column names: {sorted(reserved)}")
    for index, file_info in enumerate(dataset["selected_files"]):
        try:
            frame, info = load_source(root, file_info, dataset, config)
            sources.append(info)
            if frame.empty:
                continue
            rows += len(frame)
            duplicate_rows += int(frame.duplicated().sum())
            for column in dataset["columns"]:
                series = frame[column]
                if is_forward_label(column):
                    dtypes[column].add(dataset["sample_dtypes"].get(column, "withheld"))
                    continue
                missing[column] += int(series.isna().sum())
                observed[column] += int(series.notna().sum())
                dtypes[column].add(str(series.dtype))
                accumulators[column].add(series)
            date_col, entity_col = dataset["date_column"], dataset["entity_column"]
            key_columns = [c for c in (entity_col, date_col) if c]
            if dataset["interval_pairs"] and not date_col:
                key_columns += [pair[0] for pair in dataset["interval_pairs"]]
            key_columns = list(dict.fromkeys(key_columns))
            if key_columns:
                keys = frame[key_columns].copy()
                for key_column in key_columns:
                    keys[key_column] = parse_dates(keys[key_column]) if key_column == date_col or key_column in {p[0] for p in dataset["interval_pairs"]} else keys[key_column].astype("string")
                null_keys += int(keys.isna().any(axis=1).sum())
                duplicate_keys += int(keys.duplicated().sum())
            if entity_col:
                for entity in frame[entity_col].dropna().astype(str).unique():
                    entities.add(entity)
                    entity_files[entity].add(file_info["path"])
            if date_col:
                parsed = parse_dates(frame[date_col])
                dates.update(parsed.dt.strftime("%Y-%m-%d").dropna().tolist())
                work = pd.DataFrame({"date": parsed, "entity": frame[entity_col].astype("string") if entity_col else "single_series"})
                for _, part in work.groupby("entity", dropna=False):
                    nonmonotonic_entities += int(not part["date"].is_monotonic_increasing)
            if "market_quality" in spec["analyses"]:
                market.update(market_metrics(frame, dataset))
            if "interval_quality" in spec["analyses"]:
                for metric in interval_metrics(frame, dataset):
                    key = metric["start_column"] + " / " + metric["end_column"]
                    if key not in interval_totals:
                        interval_totals[key] = {k: v for k, v in metric.items() if isinstance(v, str)}
                    for key_name, value in metric.items():
                        if isinstance(value, int):
                            interval_totals[key][key_name] = interval_totals[key].get(key_name, 0) + value
            sample = add_uniform_sample(sample, frame, rng, config.sample_size, file_info["path"])
        except Exception as error:
            errors.append({"file": file_info["path"], "error": f"{type(error).__name__}: {error}"})
        if (index + 1) % 100 == 0:
            print(f"Analyzed {index + 1}/{len(dataset['selected_files'])} source files", flush=True)
    id_columns = {dataset["entity_column"], dataset["date_column"]} | {c for pair in dataset["interval_pairs"] for c in pair}
    fields = []
    numerical_columns = []
    for column in dataset["columns"]:
        accumulator = accumulators[column]
        suppressed = is_forward_label(column)
        is_numeric = column not in id_columns and observed[column] > 0 and (accumulator.count + accumulator.infinite_count) / observed[column] >= 0.98
        if is_numeric:
            numerical_columns.append(column)
        fields.append({"column": column, "observed_dtypes": sorted(dtypes[column]), "missing_count": None if suppressed else missing[column],
                       "missing_fraction": missing[column] / rows if rows and not suppressed else None, "is_numeric_candidate": is_numeric,
                       "analysis_suppressed": suppressed,
                       "numeric": accumulator.result(sample[column] if column in sample else None) if is_numeric else None,
                       "sample_distinct_count": int(sample[column].astype("string").nunique()) if column in sample and not suppressed else None})
    selected_numeric = [c for c in (spec["columns"] or numerical_columns) if c in numerical_columns]
    status = "failed" if not sources or not rows else "partial" if errors else "completed"
    limited = any(s["row_cap_reached"] for s in sources) or len(dataset["selected_files"]) < dataset["discovered_file_count"]
    result = {"analysis_id": analysis_id, "dataset_id": dataset["dataset_id"], "spec": spec, "status": status,
              "scope": {"research_end": config.research_end, "rows_analyzed": rows, "files_discovered": dataset["discovered_file_count"],
                        "files_selected": len(dataset["selected_files"]), "files_loaded": len(sources), "limited": limited,
                        "sample_rows": len(sample), "sampling": "uniform row reservoir for quantiles/correlation/drift; exact basic counts over analyzed rows",
                        "rows_excluded_after_cutoff": sum(s["rows_after_cutoff"] for s in sources),
                        "rows_excluded_invalid_time": sum(s["rows_with_invalid_time"] for s in sources)},
              "quality": {"duplicate_rows_within_files": duplicate_rows, "duplicate_keys_within_files": duplicate_keys,
                          "null_key_rows": null_keys, "nonmonotonic_entity_file_groups": nonmonotonic_entities,
                          "entities_in_multiple_files": sum(len(v) > 1 for v in entity_files.values()),
                          "global_key_uniqueness_verified": bool(rows) and not errors and not duplicate_keys and not null_keys and all(len(v) == 1 for v in entity_files.values()) and (bool(dataset["entity_column"]) or len(sources) == 1),
                          "entity_count": len(entities) if dataset["entity_column"] else None,
                          "key_columns": list(dict.fromkeys([c for c in (dataset["entity_column"], dataset["date_column"]) if c] + ([p[0] for p in dataset["interval_pairs"]] if not dataset["date_column"] else [])))},
              "date_range": {"min": min(dates) if dates else None, "max": max(dates) if dates else None,
                             "observed_dates": len(dates), "calendar_completeness_verified": False},
              "fields": fields, "sources": sources, "file_errors": errors, "analyses": {}, "plots": [], "warnings": [],
              "evidence": []}
    if limited:
        result["warnings"].append("Analysis is bounded by file/prefix budgets; counts and conclusions do not describe the entire source directory.")
    if errors:
        result["warnings"].append("Some files failed; inspect file_errors before using this dataset.")
    if any(is_forward_label(column) for column in dataset["columns"]):
        result["warnings"].append("Recognized target/forward-return values were withheld from EDA; schema only. Duplicate-row checks ignore these values.")
    if not dataset["date_column"]:
        result["warnings"].append("No observation date is verified. Reference rows are not automatically eligible as historical predictors.")
    if dataset["kind"] == "market_ohlcv":
        result["warnings"].append("Adjustment convention, exchange calendar, units and earliest availability are unverified unless supplied in reviewed config.")
    if result["quality"]["entities_in_multiple_files"]:
        result["warnings"].append("An entity occurs in several files; global duplicate keys and cross-file return continuity require a separate merge check.")
    if "market_quality" in spec["analyses"]:
        result["analyses"]["market_quality"] = {"metrics": dict(market), "notes": [
            "Returns use adjacent observations within an entity and a file; gaps are not assumed to be one trading day.",
            "abs(return)>0.5 flags review, not a confirmed error; CRSP signed prices and corporate actions need source-specific treatment."]}
    if "interval_quality" in spec["analyses"]:
        result["analyses"]["interval_quality"] = {"intervals": list(interval_totals.values()),
            "note": "Inclusive overlaps are review flags. Open end and future end dates are join context, not historically available features."}
    if "time_series" in spec["analyses"]:
        result["analyses"]["time_series"] = {"rows_by_date": dict(sorted(dates.items())),
            "note": "Observed sessions only; no exchange-calendar completeness claim and no forward fill."}
    if "distribution" in spec["analyses"]:
        result["analyses"]["distribution"] = {"columns": selected_numeric,
            "note": "Moments and extrema are exact over analyzed rows; quantiles and plots use a bounded uniform sample. Levels pooled across assets need cautious interpretation."}
    if "correlation" in spec["analyses"]:
        chosen = selected_numeric[:12]
        correlation = sample[chosen].apply(numeric).corr() if chosen else pd.DataFrame()
        result["analyses"]["correlation"] = {"columns": chosen, "pearson": correlation.to_dict(),
            "pairwise_nonmissing_counts": {a: {b: int((numeric(sample[a]).notna() & numeric(sample[b]).notna()).sum()) for b in chosen} for a in chosen},
            "note": "Sampled pooled contemporaneous correlation; this is neither IC nor evidence of return predictability."}
    if "drift" in spec["analyses"] and not sample.empty:
        sample_dates = parse_dates(sample[dataset["date_column"]])
        boundary = sample_dates.dropna().sort_values().iloc[len(sample_dates.dropna()) // 2] if sample_dates.notna().any() else None
        before, after = sample_dates < boundary, sample_dates >= boundary
        shifts = []
        for column in selected_numeric[:12]:
            values = numeric(sample[column])
            scale = values.std(ddof=0)
            shifts.append({"column": column, "earlier_nonmissing": int(values[before].notna().sum()), "later_nonmissing": int(values[after].notna().sum()),
                           "earlier_mean": values[before].mean(), "later_mean": values[after].mean(),
                           "standardized_mean_shift": (values[after].mean() - values[before].mean()) / scale if scale > 0 else None})
        result["analyses"]["drift"] = {"sample_split_date": str(boundary), "columns": shifts,
            "note": "Descriptive sample split only; composition changes and nonstationary price levels can explain shifts. No causal or predictive claim."}
    if "text_quality" in spec["analyses"] and not sample.empty:
        text_columns = [c for c in (spec["columns"] or dataset["columns"]) if c not in numerical_columns and c not in id_columns and not is_forward_label(c)]
        text_results = []
        for column in text_columns[:12]:
            text = sample[column].dropna().astype(str)
            text_results.append({"column": column, "sample_nonmissing": len(text), "sample_empty_strings": int(text.str.strip().eq("").sum()),
                                 "sample_duplicate_values": int(text.duplicated().sum()), "sample_median_characters": text.str.len().median()})
        result["analyses"]["text_quality"] = {"columns": text_results, "note": "Sample-based text diagnostics; entity linkage and publication availability remain unverified."}
    if config.plots and not sample.empty:
        names, warning = generate_plots(sample, selected_numeric if "distribution" in spec["analyses"] else [], dates if "time_series" in spec["analyses"] else {}, output.parent / "plots" / analysis_id)
        result["plots"] = [f"plots/{analysis_id}/{name}" for name in names]
        if warning:
            result["warnings"].append(warning)
    def evidence(suffix: str, category: str, metrics: dict, note: str) -> None:
        result["evidence"].append({"evidence_id": f"{analysis_id}.{suffix}", "dataset_id": dataset["dataset_id"],
                                   "analysis_id": analysis_id, "category": category, "metrics": metrics, "scope_note": note})
    evidence("scope", "coverage", result["scope"], "All counts refer only to the analyzed, cutoff-filtered scope.")
    evidence("quality", "data_quality", result["quality"], "Duplicate checks are within files; global uniqueness is conditional on disjoint entity files.")
    evidence("dates", "time_coverage", result["date_range"], "UTC-normalized observed dates; not an exchange calendar audit.")
    for index, field in enumerate(fields):
        evidence(f"field_{index}", "field_profile", field, "Missingness and moments are scoped counts; quantiles/distinct counts are sampled.")
    for name, values in result["analyses"].items():
        # Daily coverage can contain thousands of observations; the full sequence remains in analysis JSON.
        metrics = {"observed_date_count": len(dates), "min_rows_per_date": min(dates.values()) if dates else None,
                   "max_rows_per_date": max(dates.values()) if dates else None} if name == "time_series" else values
        evidence(name, name, metrics, "Descriptive EDA only; no factor performance has been measured.")
    result["environment"] = {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__}
    dump_json(output, result)
    return result

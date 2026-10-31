"""Publish deterministic findings, conservative field contracts, and LLM annotations."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

from . import __version__
from .core import DATE_NAMES, is_forward_label, dump_json
from .runtime import RunContext, utc_now


def field_role(column: str, dataset: dict, profile: dict) -> str:
    lower = column.lower()
    if is_forward_label(column):
        return "label"
    if column == dataset["entity_column"] or lower in {"permno", "permco", "ticker", "symbol", "gvkey", "cusip", "cusip9"}:
        return "identifier"
    if column == dataset["date_column"] or lower in DATE_NAMES:
        return "observation_time"
    if column in {c for pair in dataset["interval_pairs"] for c in pair}:
        return "validity_interval"
    if lower.startswith("unnamed:") or lower in {"index", "level_0"}:
        return "export_index"
    if lower.endswith(("date", "dt")) or lower.endswith("flg") or lower.startswith("security"):
        return "metadata"
    if dataset["kind"] in {"interval_reference", "reference_table"}:
        return "join_context"
    if profile["is_numeric_candidate"]:
        if any(word in lower for word in ("mktcap", "market_cap")) or lower == "dlycap":
            return "market_cap"
        if any(word in lower for word in ("volume",)) or lower == "dlyvol":
            return "volume"
        if lower in {"open", "high", "low", "close", "adj_open", "adj_high", "adj_low", "adj_close", "dlyopen", "dlyhigh", "dlylow", "dlyclose", "dlyprc"}:
            return "price"
        return "numeric_unknown"
    return "text_or_category"


def build_contract(context: RunContext) -> dict:
    datasets = []
    for dataset in context.datasets.values():
        results = [r for r in context.results if r["dataset_id"] == dataset["dataset_id"]]
        successful = [r for r in results if r["status"] in {"completed", "partial"}]
        profile = successful[-1] if successful else results[-1] if results else None
        fields = []
        for column in dataset["columns"]:
            measured = next((f for f in profile["fields"] if f["column"] == column), None) if profile else None
            measured = measured or {"column": column, "is_numeric_candidate": False, "observed_dtypes": [], "missing_fraction": None, "numeric": None}
            role = field_role(column, dataset, measured)
            metadata = dataset["options"].get("fields", {}).get(column, {})
            restricted = role in {"identifier", "observation_time", "validity_interval", "export_index", "metadata", "join_context", "label"}
            reasons = []
            if not metadata.get("point_in_time_verified", False):
                reasons.append("point_in_time_not_verified")
            if not metadata.get("availability"):
                reasons.append("earliest_availability_unknown")
            if metadata.get("unit") is None:
                reasons.append("unit_unknown")
            if role == "price" and not metadata.get("adjustment"):
                reasons.append("price_adjustment_convention_unknown")
            if not metadata.get("approved_for_factor", False):
                reasons.append("not_approved_in_reviewed_config")
            if profile is None or profile["status"] != "completed" or profile["scope"]["limited"]:
                reasons.append("full_selected_dataset_not_successfully_profiled")
            if profile and (profile["quality"]["duplicate_keys_within_files"] or profile["quality"]["null_key_rows"]):
                reasons.append("unresolved_key_quality")
            if profile and dataset["date_column"] and not profile["quality"]["global_key_uniqueness_verified"]:
                reasons.append("global_observation_key_not_verified")
            if not dataset["date_column"]:
                reasons.append("observation_date_not_verified")
            if measured["numeric"]:
                if measured["numeric"]["finite_count"] < 2:
                    reasons.append("insufficient_finite_observations")
                if measured["numeric"]["std_population"] == 0:
                    reasons.append("constant_in_analyzed_scope")
                if measured["numeric"]["infinite_count"]:
                    reasons.append("infinite_values_present")
            if role == "label":
                usage = "prohibited"
                reasons.append("target_or_forward_label")
            elif restricted:
                usage = "context_only"
            elif not measured["is_numeric_candidate"]:
                usage = "requires_transformation"
                reasons.append("not_a_direct_numeric_feature")
            else:
                usage = "eligible" if not reasons else "candidate_requires_confirmation"
            fields.append({"name": column, "observed_dtypes": measured["observed_dtypes"], "semantic_role": role,
                "role_source": "column_name_heuristic", "description": metadata.get("description"), "unit": metadata.get("unit"),
                "frequency": "unverified", "earliest_availability": metadata.get("availability"),
                "point_in_time_verified": metadata.get("point_in_time_verified", False), "adjustment": metadata.get("adjustment"),
                "metadata_source": "reviewed_user_config" if metadata else "unconfirmed",
                "factor_usage": usage, "blocking_reasons": reasons, "missing_fraction": measured["missing_fraction"],
                "numeric_profile": measured["numeric"], "cleaning_policy": "No automatic filling, clipping, deduplication or adjustment."})
        datasets.append({"dataset_id": dataset["dataset_id"], "name": dataset["name"], "kind": dataset["kind"],
            "kind_source": dataset["kind_source"], "date_column": dataset["date_column"], "entity_column": dataset["entity_column"],
            "interval_pairs": dataset["interval_pairs"], "discovered_file_count": dataset["discovered_file_count"],
            "scope": profile["scope"] if profile else None, "date_range": profile["date_range"] if profile else None,
            "quality": profile["quality"] if profile else None, "fields": fields,
            "analysis_artifacts": [f"analysis/{r['analysis_id']}.json" for r in results],
            "required_alignment": "Use stable security IDs, sort within entity by date, validate effective-date joins, and lag to the earliest executable decision time.",
            "warnings": sorted({w for r in results for w in r["warnings"]})})
    return {"schema_version": "1.0", "agent": "agent1", "role": "data_understanding_and_eda", "run_id": context.run_dir.name,
        "research_end": context.config.research_end, "date_policy": context.manifest["date_policy"],
        "factor_eligibility_scope": "Only reviewed fields and analyzed observation scope; no claim that a field predicts returns.",
        "cross_dataset_joins_verified": False, "datasets": datasets,
        "global_constraints": ["No future labels or final-test outcomes are used for research.",
            "Undated and effective-dated reference metadata are not automatically historical predictors.",
            "Historical universe membership, source availability, data revisions, adjustments and exchange calendars require explicit review.",
            "No factor values, IC, portfolio return or backtest result is produced by Agent 1."]}


def measured_findings(context: RunContext, contract: dict) -> list[dict]:
    findings = []
    for dataset in contract["datasets"]:
        results = [r for r in context.results if r["dataset_id"] == dataset["dataset_id"]]
        valid = [r for r in results if r["status"] != "failed"]
        if not valid:
            findings.append({"dataset_id": dataset["dataset_id"], "severity": "error", "statement": "没有成功分析到可用观察值；不能据此判断字段分布。", "evidence_ids": []})
            continue
        result = valid[-1]
        scope, quality = result["scope"], result["quality"]
        prefix = result["analysis_id"]
        findings.append({"dataset_id": dataset["dataset_id"], "severity": "info",
            "statement": f"实际分析 {scope['files_loaded']}/{scope['files_discovered']} 个文件、{scope['rows_analyzed']} 行；截止日后排除 {scope['rows_excluded_after_cutoff']} 行，无法解析时间排除 {scope['rows_excluded_invalid_time']} 行。",
            "evidence_ids": [prefix + ".scope"]})
        if scope["limited"]:
            findings.append({"dataset_id": dataset["dataset_id"], "severity": "warning", "statement": "文件或行数预算限制了分析范围，结果不代表全部来源数据。", "evidence_ids": [prefix + ".scope"]})
        if quality["duplicate_keys_within_files"] or quality["null_key_rows"]:
            findings.append({"dataset_id": dataset["dataset_id"], "severity": "warning",
                "statement": f"文件内重复键 {quality['duplicate_keys_within_files']} 行，空键 {quality['null_key_rows']} 行，需复核主键定义或原始数据。", "evidence_ids": [prefix + ".quality"]})
        for index, field in enumerate(result["fields"]):
            if field["missing_fraction"] is not None and field["missing_fraction"] > 0.2:
                findings.append({"dataset_id": dataset["dataset_id"], "severity": "warning", "statement": f"字段 {field['column']} 的缺失比例为 {field['missing_fraction']:.2%}。", "evidence_ids": [f"{prefix}.field_{index}"]})
            if field["numeric"] and field["numeric"]["infinite_count"]:
                findings.append({"dataset_id": dataset["dataset_id"], "severity": "warning", "statement": f"字段 {field['column']} 存在无穷值，统计时已排除这些值，但未改写源数据。", "evidence_ids": [f"{prefix}.field_{index}"]})
        for analysis in results:
            market = analysis["analyses"].get("market_quality", {}).get("metrics", {})
            nonzero = {k: v for k, v in market.items() if v and k != "valid_adjacent_return_count"}
            if nonzero:
                findings.append({"dataset_id": dataset["dataset_id"], "severity": "warning", "statement": "行情检查标记了需要复核的观察值：" + json.dumps(nonzero, ensure_ascii=False) + "。这些标记尚未被认定为数据错误。", "evidence_ids": [analysis["analysis_id"] + ".market_quality"]})
    return findings


def markdown_table(headers: list[str], rows: list[list]) -> str:
    def cell(value):
        return str(value if value is not None else "待确认").replace("|", "\\|").replace("\n", " ")
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] + ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows])


def publish(context: RunContext) -> dict:
    contract = build_contract(context)
    computed = measured_findings(context, contract)
    datasets_ok = all(any(r["dataset_id"] == d["dataset_id"] and r["status"] == "completed" for r in context.results) for d in contract["datasets"])
    unreadable_tables = any(Path(item["file"]).suffix.lower() in {".csv", ".tsv", ".json", ".jsonl", ".parquet", ".xlsx"} for item in context.manifest["skipped_files"])
    status = "completed" if datasets_ok and not context.failures and not unreadable_tables and (context.config.mode == "offline" or context.llm_status == "completed") else "partial"
    if not any(r["status"] != "failed" for r in context.results):
        status = "failed"
    report = {"schema_version": "1.0", "version": __version__, "run_id": context.run_dir.name, "agent": "agent1", "mode": context.config.mode,
        "status": status, "generated_at_utc": utc_now(), "research_end": context.config.research_end,
        "llm_status": context.llm_status, "computed_findings": computed, "model_interpretations": context.interpretations,
        "interpretation_validation": "Evidence IDs are validated; model prose is not independently proven and cannot overwrite measured values or field approvals.",
        "recommended_followups": context.followups, "failures": context.failures, "skipped_files": context.manifest["skipped_files"],
        "analyses": [{"analysis_id": r["analysis_id"], "dataset_id": r["dataset_id"], "status": r["status"], "spec": r["spec"],
                      "scope": r["scope"], "artifact": f"analysis/{r['analysis_id']}.json"} for r in context.results],
        "evidence": list(context.evidence().values())}
    dump_json(context.run_dir / "data_contract.json", contract)
    dump_json(context.run_dir / "eda_results.json", report)
    payload = {"schema_version": "1.0", "producer": "agent1", "consumer": "agent2", "run_id": context.run_dir.name,
        "research_end": context.config.research_end, "status": status, "data_contract_artifact": "data_contract.json",
        "eda_artifact": "eda_results.json", "computed_findings": computed, "model_interpretations": context.interpretations,
        "datasets": [{"dataset_id": d["dataset_id"], "kind": d["kind"], "date_range": d["date_range"], "scope": d["scope"],
                      "candidate_fields": [{"name": f["name"], "semantic_role": f["semantic_role"], "factor_usage": f["factor_usage"], "blocking_reasons": f["blocking_reasons"]}
                                           for f in d["fields"] if f["factor_usage"] in {"eligible", "candidate_requires_confirmation", "requires_transformation"}]}
                     for d in contract["datasets"]], "constraints": contract["global_constraints"], "followups": context.followups}
    dump_json(context.run_dir / "next_agent_payload.json", payload)
    with (context.run_dir / "field_catalog.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dataset_id", "name", "semantic_role", "factor_usage", "unit", "earliest_availability", "missing_fraction", "blocking_reasons"])
        for dataset in contract["datasets"]:
            for field in dataset["fields"]:
                writer.writerow([dataset["dataset_id"], field["name"], field["semantic_role"], field["factor_usage"], field["unit"], field["earliest_availability"], field["missing_fraction"], ";".join(field["blocking_reasons"])])
    lines = ["# Agent 1 数据理解与 EDA 报告", "", f"运行：`{context.run_dir.name}`；模式：`{context.config.mode}`；完成状态：`{status}`；观察截止日：`{context.config.research_end}`。", "",
        "本角色负责数据理解、描述性分析和字段使用约束。本报告没有检验因子预测能力。离线模式的计划来自规则，LLM 模式的解读单独列出。", "",
        "## 分析范围", "", markdown_table(["数据集", "类型", "实际文件/发现文件", "分析行数", "观察日期范围", "范围受限"], [
            [d["name"], d["kind"], f"{d['scope']['files_loaded']}/{d['discovered_file_count']}" if d["scope"] else "无成功结果",
             d["scope"]["rows_analyzed"] if d["scope"] else 0, f"{d['date_range']['min']} ~ {d['date_range']['max']}" if d["date_range"] else None,
             d["scope"]["limited"] if d["scope"] else True] for d in contract["datasets"]]), "", "## 程序计算的主要发现", ""]
    lines += [f"- [{f['severity']}] {f['statement']} 证据：{', '.join(f['evidence_ids']) or '执行状态记录'}" for f in computed]
    lines += ["", "## 字段与研究限制", "", "完整字段见 `field_catalog.csv` 和 `data_contract.json`。下表列出数值候选；需要转换的文本与类别字段保留在完整契约中。", ""]
    for dataset in contract["datasets"]:
        candidates = [f for f in dataset["fields"] if f["factor_usage"] in {"eligible", "candidate_requires_confirmation"}]
        lines += [f"### {dataset['name']}", "", markdown_table(["字段", "暂定含义", "研究使用状态", "待解决问题"], [[f["name"], f["semantic_role"], f["factor_usage"], ", ".join(f["blocking_reasons"])] for f in candidates]) if candidates else "没有已识别的直接数值候选字段。", ""]
        lines += [f"- {warning}" for warning in dataset["warnings"]]
    lines += ["", "## 模型解读", "", f"LLM 状态：`{context.llm_status}`。证据引用经过检查，文字解释仍需研究者复核。", ""]
    lines += [f"- {finding['statement']} 对后续研究的影响：{finding['implication_for_research']} 证据：{', '.join(finding['evidence_ids'])}" for finding in context.interpretations]
    if not context.interpretations:
        lines.append("本次没有完成 LLM 解读；以上数值与规则生成结论可独立检查。")
    lines += ["", "## 图表", ""]
    for result in context.results:
        for path in result["plots"]:
            lines += [f"![{result['analysis_id']}]({('analysis/' + path)})", ""]
    lines += ["", "## 后续检查", ""] + [f"- {item}" for item in context.followups]
    lines += ["", "## 未完成与跳过项", ""]
    lines += [f"- {json.dumps(item, ensure_ascii=False)}" for item in context.failures + context.manifest["skipped_files"]]
    markdown = "\n".join(lines) + "\n"
    (context.run_dir / "report.md").write_text(markdown, encoding="utf-8")
    # A self-contained HTML document with local images; no JavaScript, CDN, or external service.
    image_tags = "".join(f'<figure><img src="{html.escape("analysis/" + path, quote=True)}" alt="EDA chart"></figure>' for result in context.results for path in result["plots"])
    document = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Agent 1 EDA</title><style>body{max-width:1100px;margin:36px auto;padding:0 20px;font:15px/1.7 system-ui;background:#f7f9fa;color:#20333d}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:24px;border-radius:10px}img{max-width:100%;background:white}figure{margin:20px 0}</style><h1>Agent 1 EDA</h1><pre>' + html.escape(markdown) + "</pre>" + image_tags + "</html>"
    (context.run_dir / "report.html").write_text(document, encoding="utf-8")
    context.save_state(status)
    context.log("run_finished", status=status)
    return report

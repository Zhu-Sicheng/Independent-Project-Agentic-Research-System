"""Re-render display PnL panels with human hypothesis labels.

The display figures are normally drawn at the end of a pipeline run. When only
the labelling changes (e.g. switching from internal expression ids to
``H03-F2 · volume-shock-reversal``), the panels can be redrawn from the stored
IS-chosen configurations without re-running agents or the stability battery::

    python -m factorlab.refresh_display --experiment 20261031-systemv1_50
    python -m factorlab.refresh_display --experiment <dir> --runs sysv1-h1,sysv1-h2
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from .config import PROJECT_ROOT
from .experiments_store import EXPERIMENTS, dated_experiment_dir, iter_experiment_dirs
from .xy_pipeline import display_evaluation, display_labels
from .xy_results import _write_evaluations, load_evaluations, upsert_evaluations


def _resolve_experiment(name: str) -> Path:
    candidate = Path(name)
    if candidate.is_dir():
        return candidate.resolve()
    for experiment in reversed(iter_experiment_dirs()):
        if experiment.name == name or experiment.name.endswith("-" + name):
            return experiment
    raise FileNotFoundError(f"experiment not found: {name}")


def _run_dirs(experiment: Path) -> list[Path]:
    runs_dir = experiment / "runs"
    if runs_dir.is_dir():
        return sorted(path for path in runs_dir.iterdir() if path.is_dir())
    if (experiment / "run.json").exists() or (experiment / "evaluations.json").exists():
        return [experiment]
    return []


def _load_ideas(run_dir: Path) -> dict:
    """Ideas in the order Agent 2 produced them (so H01 is the first idea)."""
    candidates = sorted((run_dir / "agent2").glob("*/ideas.json")) if (run_dir / "agent2").is_dir() else []
    candidates += sorted(run_dir.glob("agent2/ideas.json"))
    for path in reversed(candidates):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        items = payload.get("ideas", payload) if isinstance(payload, dict) else payload
        if isinstance(items, list) and items:
            return {item["idea_id"]: item for item in items if isinstance(item, dict) and item.get("idea_id")}
    return {}


def refresh_experiment(
    experiment: Path,
    panel_dir: Optional[Path] = None,
    run_ids: Optional[list[str]] = None,
    verbose: bool = True,
) -> dict:
    from factorlab.data import load_processed

    panel_dir = panel_dir or PROJECT_ROOT / "data" / "processed" / "panel"
    panel = load_processed(panel_dir)
    runs = _run_dirs(experiment)
    if run_ids:
        wanted = set(run_ids)
        runs = [run for run in runs if run.name in wanted]
    refreshed = 0
    for run_dir in runs:
        evaluation_file = run_dir / "evaluations.json"
        if not evaluation_file.exists():
            continue
        records = load_evaluations(evaluation_file)
        if not records:
            continue
        run_id = run_dir.name
        state_file = run_dir / "run.json"
        if state_file.exists():
            try:
                run_id = json.loads(state_file.read_text(encoding="utf-8")).get("run_id", run_id)
            except (json.JSONDecodeError, OSError):
                pass
        ideas = _load_ideas(run_dir)
        labels = display_labels(ideas, records)
        if verbose:
            print(f"[refresh] {run_dir.name}: {len(labels)} labels from {len(ideas)} hypotheses", flush=True)
        display_evaluation(
            panel,
            records,
            run_id,
            run_dir,
            labels=labels,
            only_missing=False,
            redraw=True,
            compute_stability=False,
            verbose=verbose,
        )
        _write_evaluations(evaluation_file, records)
        refreshed += 1

    # rebuild the merged experiment-level evaluations (canonical upsert)
    merged = experiment / "evaluations.json"
    if merged.exists():
        merged.unlink()
    merged_count = 0
    for run_dir in _run_dirs(experiment):
        evaluation_file = run_dir / "evaluations.json"
        if not evaluation_file.exists():
            continue
        records = load_evaluations(evaluation_file)
        if records:
            stats = upsert_evaluations(merged, records, run_dir.name)
            merged_count += stats["inserted"]
    return {"refreshed_runs": refreshed, "merged_records": merged_count}


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, help="dated experiment directory or its slug")
    parser.add_argument("--panel", default=None, help="processed panel directory")
    parser.add_argument("--runs", default="", help="comma separated run ids to refresh (default: all)")
    args = parser.parse_args(argv)
    experiment = _resolve_experiment(args.experiment)
    run_ids = [item.strip() for item in args.runs.split(",") if item.strip()]
    result = refresh_experiment(
        experiment,
        panel_dir=Path(args.panel) if args.panel else None,
        run_ids=run_ids or None,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

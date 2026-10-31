"""Date-ordered experiment store.

``experiments/`` keeps one directory per experiment, named ``<YYYYMMDD>-<slug>``
so the directory listing is chronological (not alphabetical by topic)::

    experiments/
      20261030-us-mining/
      20261030-llm-real/
      20261031-batch10/        (screenshots, attempts, records/, reports/, stability/)
      20261031-batch100/
      20261031-systemv1_50/    (published summary + figures, local runs/ ignored)
      README.md                (generated index, newest at the bottom)

Helpers:

* :func:`dated_experiment_dir` -- create or resolve a dated directory
* :func:`find_run_dir` -- locate a pipeline run by ``run.json`` / ``evaluations.json``
* :func:`iter_experiment_dirs` / :func:`iter_run_dirs` -- scan helpers
* :func:`write_index` -- regenerate ``experiments/README.md``
* ``python -m factorlab.experiments_store --migrate`` -- one-off migration of the
  legacy ``batch10/``, ``records/``, ``reports/``, ``stability/``, ``published/``
  layout into the dated layout above
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from .config import PROJECT_ROOT
from .markdown import md_table

EXPERIMENTS = PROJECT_ROOT / "experiments"
INDEX_FILE = EXPERIMENTS / "README.md"
INDEX_STATE = EXPERIMENTS / ".index"
_RUN_DIR_RE = re.compile(r"^(\d{8})-\d{6}")
_DATE_DIR_RE = re.compile(r"^(\d{8})-(.+)$")


def _today() -> str:
    return datetime.now().strftime("%Y%m%d")


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_")
    return value or "experiment"


def date_of(run_id: str, fallback: Optional[str] = None) -> str:
    """Extract ``YYYYMMDD`` from a run id or fall back to today."""
    match = _RUN_DIR_RE.match(str(run_id))
    if match:
        return match.group(1)
    return fallback or _today()


def dated_dir(date: Optional[str], slug: str) -> Path:
    date = date or _today()
    return EXPERIMENTS / f"{date}-{slugify(slug)}"


def dated_experiment_dir(slug: str, date: Optional[str] = None) -> Path:
    """Return (and create) ``experiments/<date>-<slug>/``."""
    target = dated_dir(date, slug)
    target.mkdir(parents=True, exist_ok=True)
    return target


def iter_experiment_dirs() -> list[Path]:
    """Dated experiment directories sorted chronologically by name."""
    if not EXPERIMENTS.exists():
        return []
    dirs = [p for p in EXPERIMENTS.iterdir() if p.is_dir() and _DATE_DIR_RE.match(p.name)]
    return sorted(dirs, key=lambda path: path.name)


def iter_run_dirs() -> list[Path]:
    """Every run directory carrying a ``run.json`` or ``evaluations.json``."""
    found: list[Path] = []
    for experiment in iter_experiment_dirs():
        candidates = [experiment]
        runs = experiment / "runs"
        if runs.is_dir():
            candidates.extend(
                sorted(p for p in runs.iterdir() if p.is_dir())
            )
        for candidate in candidates:
            if (candidate / "run.json").exists() or (candidate / "evaluations.json").exists():
                found.append(candidate)
    legacy = EXPERIMENTS / "xy"
    if legacy.is_dir():
        found.extend(
            p for p in sorted(legacy.iterdir())
            if p.is_dir() and ((p / "run.json").exists() or (p / "evaluations.json").exists())
        )
    return found


def find_run_dir(run_id: str) -> Optional[Path]:
    """Locate a run by the ``run_id`` recorded inside ``run.json``."""
    for run_dir in iter_run_dirs():
        run_json = run_dir / "run.json"
        if not run_json.exists():
            continue
        try:
            payload = json.loads(run_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if payload.get("run_id") == run_id:
            return run_dir
    for experiment in iter_experiment_dirs():
        candidate = experiment / "runs" / run_id
        if (candidate / "run.json").exists() or (candidate / "evaluations.json").exists():
            return candidate
    legacy = EXPERIMENTS / "xy" / run_id
    if (legacy / "run.json").exists() or (legacy / "evaluations.json").exists():
        return legacy
    return None


def iter_evaluation_files() -> list[Path]:
    """Every ``evaluations.json`` file in date-ordered experiment directories."""
    files: list[Path] = []
    for run_dir in iter_run_dirs():
        path = run_dir / "evaluations.json"
        if path.exists():
            files.append(path)
    return files


# --------------------------------------------------------------------------- #
# index
# --------------------------------------------------------------------------- #
def _experiment_summary(experiment: Path) -> dict:
    records = len(list((experiment / "records").glob("*"))) if (experiment / "records").is_dir() else 0
    reports = len(list((experiment / "reports").glob("*.md"))) if (experiment / "reports").is_dir() else 0
    figures = len(list((experiment / "figures").glob("*.png"))) if (experiment / "figures").is_dir() else 0
    runs = len([p for p in (experiment / "runs").glob("*") if p.is_dir()]) if (experiment / "runs").is_dir() else 0
    evaluations = 0
    if (experiment / "evaluations.json").exists():
        try:
            payload = json.loads((experiment / "evaluations.json").read_text(encoding="utf-8"))
            rows = payload.get("records", payload) if isinstance(payload, dict) else payload
            evaluations = len(rows)
        except (json.JSONDecodeError, OSError):
            pass
    title = ""
    readme = experiment / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    return {
        "directory": experiment.name,
        "date": experiment.name[:8],
        "what": title,
        "records": records or "",
        "reports": reports or "",
        "figures": figures or "",
        "runs": runs or "",
        "evaluations": evaluations or "",
    }


def write_index(path: Optional[Path] = None) -> Path:
    """Regenerate the chronological ``experiments/README.md`` index."""
    target = path or INDEX_FILE
    rows = [_experiment_summary(experiment) for experiment in iter_experiment_dirs()]
    lines = [
        "# Experiments",
        "",
        "One directory per experiment, named `<YYYYMMDD>-<slug>` so the listing is",
        "chronological. Raw run directories live in `<experiment>/runs/` (local, gitignored)",
        "and archived attempt records in `<experiment>/records/`.",
        "",
        md_table(rows) if rows else "_no experiments yet_",
        "",
    ]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


# --------------------------------------------------------------------------- #
# one-off migration of the legacy layout
# --------------------------------------------------------------------------- #
def _move(source: Path, target: Path) -> None:
    if not source.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if source.is_dir() and target.is_dir():
            for child in list(source.iterdir()):
                _move(child, target / child.name)
            source.rmdir()
            return
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    shutil.move(str(source), str(target))


def _write_readme(experiment: Path, title: str, lines: list[str]) -> None:
    experiment.mkdir(parents=True, exist_ok=True)
    content = [f"# {title}", ""] + [f"- {line}" for line in lines] + [""]
    (experiment / "README.md").write_text("\n".join(content), encoding="utf-8")


def migrate_legacy() -> dict:
    """Move the pre-2026-11 flat layout into date-ordered experiment dirs."""
    moved: list[str] = []

    def into(date: str, slug: str, source: Path, sub: str = "") -> None:
        if not source.exists():
            return
        base = dated_experiment_dir(slug, date)
        if sub:
            destination = base / sub / source.name
        else:
            destination = base
        _move(source, destination)
        moved.append(f"{source.relative_to(EXPERIMENTS)} -> {destination.relative_to(EXPERIMENTS)}")

    # --- 2026-10-30 classic mining runs ---
    into("20261030", "us-mining", EXPERIMENTS / "records" / "20261030-122256-us", "records")
    into("20261030", "llm-real", EXPERIMENTS / "records" / "20261030-165618-llm-real", "records")
    into("20261030", "us-mining", EXPERIMENTS / "reports" / "20261030-122256-us.md", "reports")
    into("20261030", "llm-real", EXPERIMENTS / "reports" / "20261030-165618-llm-real.md", "reports")

    # --- 2026-10-31 e2e smoke ---
    into("20261031", "e2e", EXPERIMENTS / "records" / "20261031-083828-e2e", "records")
    into("20261031", "e2e", EXPERIMENTS / "reports" / "20261031-083828-e2e.md", "reports")

    # --- 2026-10-31 classic batch10 (batch10c + the stability battery) ---
    into("20261031", "batch10", EXPERIMENTS / "batch10", "")
    for run_id in ("20261031-095220-batch10", "20261031-101653-batch10c"):
        into("20261031", "batch10", EXPERIMENTS / "records" / run_id, "records")
    for report in ("20261031-095220-batch10.md", "20261031-101653-batch10c.md"):
        into("20261031", "batch10", EXPERIMENTS / "reports" / report, "reports")
    stability = EXPERIMENTS / "stability"
    if stability.exists():
        _move(stability, EXPERIMENTS / "20261031-batch10" / "stability")
        moved.append("stability/* -> 20261031-batch10/stability")

    # --- 2026-10-31 batch100 (everything else archived on that day) ---
    into("20261031", "batch100", EXPERIMENTS / "batch100", "")
    batch100 = EXPERIMENTS / "20261031-batch100"
    for source in sorted((EXPERIMENTS / "records").glob("*")):
        _move(source, batch100 / "records" / source.name)
        moved.append(f"records/{source.name} -> 20261031-batch100/records/{source.name}")
    for report in sorted((EXPERIMENTS / "reports").glob("*")):
        _move(report, batch100 / "reports" / report.name)
        moved.append(f"reports/{report.name} -> 20261031-batch100/reports/{report.name}")
    ledger = EXPERIMENTS / "ledger.csv"
    if ledger.exists():
        _move(ledger, batch100 / "ledger.csv")
        moved.append("ledger.csv -> 20261031-batch100/ledger.csv")

    # --- 2026-10-31 systemv1 50-hypothesis batch ---
    target = dated_experiment_dir("systemv1_50", "20261031")
    published = EXPERIMENTS / "published" / "systemv1-50h"
    if published.exists():
        _move(published, target)
        nested = target / "systemv1-50h"
        if nested.is_dir():
            for child in list(nested.iterdir()):
                _move(child, target / child.name)
            nested.rmdir()
        moved.append("published/systemv1-50h -> 20261031-systemv1_50")
    runs = EXPERIMENTS / "xy"
    if runs.exists():
        run_target = target / "runs"
        run_target.mkdir(parents=True, exist_ok=True)
        for child in list(runs.iterdir()):
            _move(child, run_target / child.name)
        runs.rmdir()
        moved.append("xy/* -> 20261031-systemv1_50/runs")

    # --- merge the per-run evaluations into the experiment root ---
    if (target / "runs").is_dir():
        from .xy_results import load_evaluations, upsert_evaluations

        merged_path = target / "evaluations.json"
        for run_dir in sorted((target / "runs").iterdir()):
            evaluation_file = run_dir / "evaluations.json"
            if not evaluation_file.exists():
                continue
            records = load_evaluations(evaluation_file)
            if records:
                upsert_evaluations(merged_path, records, run_dir.name)

    # --- derived plots are not experiment records ---
    plots = EXPERIMENTS / "plots"
    if plots.exists():
        shutil.rmtree(plots, ignore_errors=True)
        moved.append("plots/ (derived duplicates) removed")

    for empty in ("records", "reports", "stability", "published", "batch10", "batch100"):
        path = EXPERIMENTS / empty
        if path.exists() and path.is_dir() and not any(path.iterdir()):
            path.rmdir()

    # --- per-experiment descriptions shown by the index ---
    descriptions = {
        "20261030-us-mining": ("2026-10-30 US equity mining run", ["classic 2.1/2.2 loop on the S&P 500 panel"]),
        "20261030-llm-real": ("2026-10-30 real-LLM mining run", ["classic loop with DeepSeek hypothesis/implementation agents"]),
        "20261031-e2e": ("2026-10-31 end-to-end smoke run", ["classic loop, offline agents"]),
        "20261031-batch10": (
            "2026-10-31 classic batch10",
            [
                "10 factor attempts across batch10 / batch10c",
                "archived attempt records and reports",
                "per-factor display figures",
                "stability battery (subuniverse / decay / transform / window)",
            ],
        ),
        "20261031-batch100": (
            "2026-10-31 100-hypothesis batch",
            ["100 classic-loop attempts (27 sessions)", "archived attempt records and reports", "ledger.csv snapshot"],
        ),
        "20261031-systemv1_50": (
            "2026-10-31 systemv1 50+ hypothesis batch",
            [
                "merged pipeline: collaborator Agents 1-3 (LLM) + our IS-only grid/stability/reviewer",
                "53 evaluated expressions (51 unique)",
                "summary.csv / overview.png / top display figures",
                "raw local runs under runs/ (gitignored)",
            ],
        ),
    }
    for name, (title, notes) in descriptions.items():
        experiment = EXPERIMENTS / name
        if experiment.exists():
            _write_readme(experiment, title, notes)

    index = write_index()
    return {
        "moved": moved,
        "index": str(index),
        "directories": [p.name for p in iter_experiment_dirs()],
    }


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--migrate", action="store_true", help="move the legacy flat layout into dated dirs")
    parser.add_argument("--index", action="store_true", help="regenerate experiments/README.md")
    args = parser.parse_args(argv)
    if args.migrate:
        print(json.dumps(migrate_legacy(), ensure_ascii=False, indent=2))
    if args.index or not args.migrate:
        print(write_index())


if __name__ == "__main__":
    main()

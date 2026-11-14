"""Parallel campaign driver for the merged pipeline (Agents 1-3 + our evaluation).

One worker process repeatedly launches ``factorlab.xy_pipeline`` with fresh run ids
until the shared target of evaluated expressions is reached or the wall-clock
deadline expires::

    python -m factorlab.campaign --worker 1 --target 500 --hours 7 \
        --experiment-name systemv1-500 --out-root experiments/20261114-systemv1-500

Run one process per worker (they share the out-root and the incremental result
store).  Counting is done from each run's ``evaluations.json``, so resuming a
deadline-expired campaign simply continues where it stopped.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import PROJECT_ROOT

DEFAULT_OUT_ROOT = PROJECT_ROOT / "experiments"


def count_expressions(out_root: Path) -> int:
    """Total evaluated expressions across all runs under ``out_root``."""
    total = 0
    paths = set(out_root.glob("*/evaluations.json")) | set(out_root.glob("runs/*/evaluations.json"))
    for path in sorted(paths):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        total += int(payload.get("n_records") or 0)
    return total


def build_command(worker: int, index: int, args, out_root: Path) -> tuple[str, list[str]]:
    run_id = f"{args.prefix}-c{worker}-r{index:03d}"
    cmd = [
        sys.executable,
        "-m",
        "factorlab.xy_pipeline",
        "--mode",
        "offline",
        "--agent2-mode",
        "llm",
        "--agent3-mode",
        "llm",
        "--rounds",
        str(args.rounds),
        "--max-evals",
        str(args.max_evals),
        "--llm-max-turns",
        str(args.llm_max_turns),
        "--llm-tool-calls",
        str(args.llm_tool_calls),
        "--llm-token-budget",
        str(args.llm_token_budget),
        "--run-id",
        run_id,
        "--out-root",
        str(out_root),
    ]
    if args.experiment_name:
        cmd += ["--experiment-name", args.experiment_name]
    if args.plots:
        cmd.append("--plots")
    return run_id, cmd


def run_worker(args) -> int:
    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = PROJECT_ROOT / out_root
    logs = out_root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    driver_log = logs / f"worker{args.worker}.driver.log"
    deadline = datetime.now() + timedelta(hours=float(args.hours))

    def say(message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[worker{args.worker}] {stamp} {message}"
        print(line, flush=True)
        with driver_log.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    index = 0
    while datetime.now() < deadline:
        done = count_expressions(out_root)
        if done >= args.target:
            say(f"target reached ({done}/{args.target}), stopping")
            return 0
        index += 1
        run_id, cmd = build_command(args.worker, index, args, out_root)
        say(f"start {run_id} with {done}/{args.target} expressions so far")
        started = time.time()
        with (logs / f"worker{args.worker}.log").open("a", encoding="utf-8") as log:
            log.write(f"\n===== {run_id} @ {datetime.now().isoformat(timespec='seconds')} =====\n")
            log.flush()
            code = subprocess.run(
                cmd, cwd=str(PROJECT_ROOT), stdout=log, stderr=subprocess.STDOUT
            ).returncode
        elapsed = (time.time() - started) / 3600.0
        now_done = count_expressions(out_root)
        say(
            f"done {run_id} exit={code} in {elapsed:.2f}h, "
            f"{now_done - done} new expressions, {now_done}/{args.target} total"
        )
    say("deadline reached, stopping")
    return 0


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=int, required=True, help="worker index (used in run ids)")
    parser.add_argument("--target", type=int, default=500, help="global evaluated-expression target")
    parser.add_argument("--hours", type=float, default=7.0, help="wall-clock budget per worker")
    parser.add_argument("--rounds", type=int, default=6, help="feedback rounds per pipeline run")
    parser.add_argument("--max-evals", type=int, default=24)
    parser.add_argument("--llm-max-turns", type=int, default=12)
    parser.add_argument("--llm-tool-calls", type=int, default=24)
    parser.add_argument("--llm-token-budget", type=int, default=600000)
    parser.add_argument("--prefix", default="s500", help="run id prefix")
    parser.add_argument("--experiment-name", default="systemv1-500")
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT / "20261114-systemv1-500"))
    parser.add_argument("--plots", action="store_true", default=True)
    argv = sys.argv[1:] if argv is None else argv
    args = parser.parse_args(argv)
    run_worker(args)


if __name__ == "__main__":
    main()

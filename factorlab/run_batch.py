"""Run repeated short mining sessions — used for the 100-hypothesis quota.

Each session is a normal ``factorlab run`` (hypothesis -> implement -> grid ->
stability -> review). Running a few sessions of 5 hypotheses instead of one of 100
keeps every LLM proposal small and lets several workers share the machine.

``python -m factorlab.run_batch --worker a --sessions 7 --hypotheses 5 --max-evals 80``
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback

from .config import PROJECT_ROOT

from .cli import main as cli_main


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", required=True, help="worker label, used in the run tag")
    parser.add_argument("--sessions", type=int, default=7)
    parser.add_argument("--hypotheses", type=int, default=5)
    parser.add_argument("--max-evals", type=int, default=80)
    parser.add_argument("--pool", default=None)
    parser.add_argument("--runs", default="runs")
    parser.add_argument("--prefix", default="p100")
    args = parser.parse_args()

    pool = args.pool or f"pool_{args.prefix}_{args.worker}"
    avoid_file = PROJECT_ROOT / f"avoid_{args.prefix}.txt"
    started = time.time()
    done = 0
    for index in range(args.sessions):
        tag = f"{args.prefix}_{args.worker}_{index:02d}"
        try:
            seen = sorted(
                {
                    json.loads(line)["hypothesis"]
                    for run in (PROJECT_ROOT / "runs").glob(f"*{args.prefix}*")
                    for line in (run / "attempts.jsonl").read_text(encoding="utf-8").splitlines()
                    if line.strip()
                }
            )
            avoid_file.write_text("\n".join(seen), encoding="utf-8")
        except Exception:
            seen = []
        print(f"[worker {args.worker}] session {index + 1}/{args.sessions} ({tag})", flush=True)
        argv = [
            "run",
            "--data",
            "data/processed/panel",
            "--hypotheses",
            str(args.hypotheses),
            "--rounds",
            "1",
            "--max-evals",
            str(args.max_evals),
            "--pool",
            pool,
            "--runs",
            args.runs,
            "--tag",
            tag,
            "--avoid-file",
            str(avoid_file),
        ]
        try:
            cli_main(argv)
            done += 1
        except SystemExit as exc:  # pragma: no cover - defensive
            print(f"[worker {args.worker}] session {tag} exited: {exc}", flush=True)
        except Exception:  # pragma: no cover - defensive
            print(f"[worker {args.worker}] session {tag} crashed:", flush=True)
            traceback.print_exc()
        print(
            f"[worker {args.worker}] {done}/{args.sessions} sessions, "
            f"{round(time.time() - started) / 60:.1f} min elapsed",
            flush=True,
        )

    print(f"[worker {args.worker}] finished {done} sessions in {(time.time() - started) / 60:.1f} min", flush=True)
    sys.stdout.flush()


if __name__ == "__main__":
    main()

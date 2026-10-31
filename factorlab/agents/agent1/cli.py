"""CLI configuration and run lifecycle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .agent import EDAAgent
from .core import Config, discover, read_json
from .llm import ChatClient
from .reporting import publish
from .runtime import RunContext, create_run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent 1: read-only data understanding, adaptive EDA and field contracts. No factor generation or backtesting.")
    parser.add_argument("--config", type=Path, help="JSON configuration; paths are relative to the config's parent project directory when placed under configs/")
    parser.add_argument("--data-root")
    parser.add_argument("--output-root")
    parser.add_argument("--research-end", help="Required analytical cutoff, YYYY-MM-DD; inclusive, UTC-normalized")
    parser.add_argument("--mode", choices=["offline", "llm"])
    parser.add_argument("--max-files-per-dataset", type=int, help="0 = all files in each schema group")
    parser.add_argument("--max-rows-per-file", type=int, help="0 = unlimited; otherwise explicitly reported prefix cap")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args(argv)
    context = None
    try:
        values = read_json(args.config) if args.config else {}
        if not isinstance(values, dict):
            raise ValueError("Configuration must be a JSON object")
        if args.config:
            base = args.config.resolve().parent
            if base.name == "configs":
                base = base.parent
            for key in ("data_root", "output_root"):
                if key in values:
                    values[key] = str((base / values[key]).resolve())
        for key in ("data_root", "output_root", "research_end", "mode", "max_files_per_dataset", "max_rows_per_file"):
            value = getattr(args, key)
            if value is not None:
                values[key] = value
        if args.no_plots:
            values["plots"] = False
        config = Config.from_dict(values)
        config.data_root = str(Path(config.data_root).resolve())
        config.output_root = str(Path(config.output_root).resolve())
        # Fail fast for missing credentials before scanning data or creating output files.
        client = ChatClient(config.llm) if config.mode == "llm" else None
        print("Discovering dataset schemas (no source files will be modified)...", flush=True)
        manifest = discover(config)
        context = RunContext(config, manifest, create_run_dir(config))
        print(f"Found {len(manifest['datasets'])} schema groups; outputs: {context.run_dir}", flush=True)
        try:
            EDAAgent(context, client).run()
        except Exception as error:
            context.llm_status = "error" if config.mode == "llm" else "not_requested"
            failure = {"stage": "agent_loop", "error": f"{type(error).__name__}: {error}"}
            context.failures.append(failure)
            context.log("agent_loop_failed", **failure)
        report = publish(context)
        print(f"Status: {report['status']}; report: {context.run_dir / 'report.html'}", flush=True)
        return 0 if report["status"] == "completed" else 2
    except (ValueError, OSError, ImportError) as error:
        print(f"Agent 1 configuration/runtime error: {error}", file=sys.stderr)
        if context is not None:
            context.save_state("failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

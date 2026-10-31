"""Consistent command-line interfaces for the two research stages."""

from __future__ import annotations

import argparse
from pathlib import Path

from agent1.core import read_json
from .common import ExpressionConfig, IdeaConfig


def main(stage: int, argv=None) -> int:
    parser = argparse.ArgumentParser(description="Agent 2: natural-language hypotheses" if stage == 2 else "Agent 3: constrained expressions and numerical previews")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--agent1-run", help="Agent 1 output directory, or latest completed run")
    if stage == 3:
        parser.add_argument("--agent2-run", help="Agent 2 output directory, or latest completed run")
    parser.add_argument("--mode", choices=["offline", "llm"])
    parser.add_argument("--memory-db")
    parser.add_argument("--output-root")
    parser.add_argument("--operator-file")
    parser.add_argument("--knowledge-cutoff", help="Optional ISO timestamp with timezone for historical knowledge filtering")
    args = parser.parse_args(argv)
    try:
        values = read_json(args.config) if args.config else {}
        config_type = IdeaConfig if stage == 2 else ExpressionConfig
        if not isinstance(values, dict):
            raise ValueError("Config must be an object")
        defaults = config_type()
        values = {**{name: getattr(defaults, name) for name in ("memory_db", "operator_file", "output_root")}, **values}
        if args.config:
            base = args.config.resolve().parent
            if base.name == "configs":
                base = base.parent
            for name in ("agent1_run", "agent2_run", "memory_db", "operator_file", "output_root"):
                if name in values and values[name] != "latest":
                    values[name] = str((base / values[name]).resolve())
        for name in ("agent1_run", "agent2_run", "mode", "memory_db", "output_root", "operator_file", "knowledge_cutoff"):
            value = getattr(args, name, None)
            if value is not None:
                values[name] = value
        config = config_type.from_dict(values)
        # Custom environment variable names make the shared HTTP adapter provider-independent.
        config.llm = {"base_url_env": f"AGENT{stage}_BASE_URL", "api_key_env": f"AGENT{stage}_API_KEY", "model_env": f"AGENT{stage}_MODEL", **config.llm}
        if stage == 2:
            from agent2.agent import IdeaAgent
            agent = IdeaAgent(config)
        else:
            from agent3.agent import ExpressionAgent
            agent = ExpressionAgent(config)
        result = agent.run()
        print(f"Agent {stage}: {result['status']}; report: {agent.artifacts.root / 'report.html'}")
        print("Accepted ideas:", len(result["ideas"])) if stage == 2 else print("Accepted expressions:", len(result["expressions"]))
        return 0 if result["status"] == "completed" else 2 if result["status"] == "partial" else 1
    except (ValueError, OSError, ImportError) as error:
        parser.exit(1, f"Agent {stage} configuration/runtime error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main(2))

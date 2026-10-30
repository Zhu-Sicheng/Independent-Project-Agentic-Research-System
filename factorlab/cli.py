"""Command line entry point: ``python -m factorlab ...``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .backtest.engine import run_backtest
from .config import (
    BacktestSettings,
    GridConfig,
    MiningConfig,
    PROJECT_ROOT,
    SampleSplit,
    ensure_dirs,
)
from .data.loader import load_panel
from .data.sample import generate_sample_directory
from .expr.evaluator import evaluate_text
from .expr.spec import FactorSpec
from .markdown import md_table
from .orchestrator import MiningLoop
from .pool.pool import FactorPool


def _add_split(p: argparse.ArgumentParser) -> None:
    p.add_argument("--train-frac", type=float, default=None,
                   help="fraction of dates used for in-sample selection, e.g. 0.7")
    p.add_argument("--train-start", default=None, help="in-sample start date (inclusive)")
    p.add_argument("--train-end", default=None, help="in-sample end date (inclusive)")
    p.add_argument("--oos-start", default=None, help="out-of-sample start date (inclusive)")
    p.add_argument("--oos-end", default=None, help="out-of-sample end date (inclusive)")


def _split_from_args(args) -> SampleSplit | None:
    split = SampleSplit(
        train_start=args.train_start,
        train_end=args.train_end,
        test_start=args.oos_start,
        test_end=args.oos_end,
        train_frac=args.train_frac,
    )
    return split if split.is_configured() else None


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--data", default=str(PROJECT_ROOT / "data" / "sample"), help="data directory or file")
    p.add_argument("--start", default=None, help="restrict the sample start date")
    p.add_argument("--end", default=None, help="restrict the sample end date")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="factorlab", description="Agentic factor mining: data -> hypothesis -> expression -> backtest -> pool"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("gen-data", help="write a synthetic sample dataset")
    gen.add_argument("--out", default=str(PROJECT_ROOT / "data" / "sample"))
    gen.add_argument("--tickers", type=int, default=300)
    gen.add_argument("--start", default="2018-01-01")
    gen.add_argument("--end", default="2024-12-31")
    gen.add_argument("--seed", type=int, default=7)
    gen.add_argument("--signal-scale", type=float, default=1.0)

    run = sub.add_parser("run", help="run the mining loop")
    _add_common(run)
    run.add_argument("--pool", default=str(PROJECT_ROOT / "pool"))
    run.add_argument("--runs", default=str(PROJECT_ROOT / "runs"))
    run.add_argument("--hypotheses", type=int, default=3)
    run.add_argument("--rounds", type=int, default=2)
    run.add_argument("--max-evals", type=int, default=200)
    run.add_argument("--objective", default="sharpe")
    run.add_argument("--tag", default="")
    run.add_argument("--offline", action="store_true", help="force the rule-based agents")
    _add_split(run)

    demo = sub.add_parser("demo", help="generate sample data if needed, then run the loop")
    demo.add_argument("--pool", default=str(PROJECT_ROOT / "pool"))
    demo.add_argument("--runs", default=str(PROJECT_ROOT / "runs"))
    demo.add_argument("--hypotheses", type=int, default=3)
    demo.add_argument("--rounds", type=int, default=2)
    demo.add_argument("--max-evals", type=int, default=200)
    demo.add_argument("--tickers", type=int, default=300)
    demo.add_argument("--regenerate", action="store_true")
    demo.add_argument("--offline", action="store_true")
    _add_split(demo)

    expr = sub.add_parser("expr", help="backtest a single expression")
    _add_common(expr)
    expr.add_argument("--expression", required=True)
    expr.add_argument("--decay", type=int, default=0)
    expr.add_argument("--transform", default="rank", choices=["none", "rank", "sign", "zscore"])
    expr.add_argument("--cap", type=float, default=None)
    expr.add_argument("--cost-bps", type=float, default=0.0)
    expr.add_argument("--grid", action="store_true", help="grid search instead of a single run")

    pool = sub.add_parser("pool", help="inspect the factor pool")
    pool.add_argument("--pool", default=str(PROJECT_ROOT / "pool"))
    pool.add_argument("--recompute", action="store_true", help="recompute all correlations")
    pool.add_argument("--top", type=int, default=20)

    return parser


def _load(args) -> "object":
    return load_panel(args.data, start=args.start, end=args.end)


def cmd_gen_data(args) -> int:
    out = generate_sample_directory(
        args.out,
        n_tickers=args.tickers,
        start=args.start,
        end=args.end,
        seed=args.seed,
        signal_scale=args.signal_scale,
    )
    print(f"sample data written to {out}")
    return 0


def cmd_run(args) -> int:
    panel = _load(args)
    config = MiningConfig(
        n_hypotheses=args.hypotheses,
        max_rounds=args.rounds,
        grid=GridConfig(max_evals=args.max_evals, objective=args.objective),
        split=_split_from_args(args),
    )
    if args.offline:
        config.llm.provider = "offline"
        config.llm.model = ""
        config.llm.base_url = ""
        config.llm.api_key_env = ""
    ensure_dirs(Path(args.pool), Path(args.runs))
    loop = MiningLoop(panel, FactorPool(args.pool), config, out_dir=Path(args.runs), run_tag=args.tag)
    result = loop.run()
    print("\n" + json.dumps({k: v for k, v in result.items() if k != "attempts"}, indent=2))
    print(f"\nreport: {Path(result['run_dir']) / 'report.md'}")
    return 0


def cmd_demo(args) -> int:
    data_dir = PROJECT_ROOT / "data" / "sample"
    if args.regenerate or not any(data_dir.glob("*.parquet")):
        print("generating synthetic sample data ...")
        generate_sample_directory(data_dir, n_tickers=args.tickers)
    panel = load_panel(data_dir)
    config = MiningConfig(
        n_hypotheses=args.hypotheses,
        max_rounds=args.rounds,
        grid=GridConfig(max_evals=args.max_evals),
        split=_split_from_args(args),
    )
    if args.offline:
        config.llm.provider = "offline"
        config.llm.model = ""
        config.llm.base_url = ""
        config.llm.api_key_env = ""
    ensure_dirs(Path(args.pool), Path(args.runs))
    loop = MiningLoop(panel, FactorPool(args.pool), config, out_dir=Path(args.runs))
    result = loop.run()
    print("\n" + json.dumps({k: v for k, v in result.items() if k != "attempts"}, indent=2))
    print(f"\nreport: {Path(result['run_dir']) / 'report.md'}")
    return 0


def cmd_expr(args) -> int:
    panel = _load(args)
    settings = BacktestSettings(
        decay=args.decay, transform=args.transform, cap_filter=args.cap, cost_bps=args.cost_bps
    )
    if args.grid:
        from .backtest.grid import GridSearch

        grid = GridSearch(panel, GridConfig(), settings).run_expression(args.expression)
        print(grid.top(10).to_string())
        print(json.dumps(grid.summary()["best"], indent=2))
        return 0
    factor = evaluate_text(args.expression, panel)
    result = run_backtest(factor, panel, settings)
    print(json.dumps(result.metrics, indent=2))
    print(result.yearly.round(3).to_string())
    return 0


def cmd_pool(args) -> int:
    pool = FactorPool(args.pool)
    if args.recompute:
        pool.recompute_correlations()
    print(pool.report(top=args.top))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "gen-data": cmd_gen_data,
        "run": cmd_run,
        "demo": cmd_demo,
        "expr": cmd_expr,
        "pool": cmd_pool,
    }
    return handlers[args.command](args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

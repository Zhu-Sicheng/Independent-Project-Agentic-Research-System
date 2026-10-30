"""Backtesting and grid search."""

from .engine import (
    BacktestError,
    BacktestResult,
    SubUniverseResult,
    forward_returns,
    prepare_factor,
    run_backtest,
    run_backtest_with_subuniverse,
    subuniverse_mask,
    yearly_table,
)
from .grid import GridError, GridResult, GridSearch
from .split import SplitError, SplitMasks, resolve_split, segment_metrics

__all__ = [
    "run_backtest",
    "run_backtest_with_subuniverse",
    "subuniverse_mask",
    "SubUniverseResult",
    "forward_returns",
    "prepare_factor",
    "BacktestResult",
    "BacktestError",
    "GridSearch",
    "GridResult",
    "GridError",
    "yearly_table",
    "SplitError",
    "SplitMasks",
    "resolve_split",
    "segment_metrics",
]

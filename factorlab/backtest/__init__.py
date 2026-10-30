"""Backtesting and grid search."""

from .engine import (
    BacktestError,
    BacktestResult,
    forward_returns,
    prepare_factor,
    run_backtest,
    yearly_table,
)
from .grid import GridError, GridResult, GridSearch
from .split import SplitError, SplitMasks, resolve_split, segment_metrics

__all__ = [
    "run_backtest",
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

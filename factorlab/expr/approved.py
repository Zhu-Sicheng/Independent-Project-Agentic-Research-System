"""The approved operator set for agent-generated factors.

The canonical list of time-series operators comes from ``ts_operators.md``
(2026-10) and is the only vocabulary the implementer agent (2.2) is allowed to
use in an expression.  Non-time-series operators (cross-sectional, element-wise,
conditional) come from the registry as before.

The registry in :mod:`factorlab.expr.ops` intentionally stays larger: legacy
operators (``ts_std``, ``ts_corr``, ``delay``, ...) remain available for direct
calls, scripts and tests, but validation rejects them unless
``strict_operators=False``.  Adding a new approved operator therefore means
(a) registering it in ``ops.py`` and (b) appending it to ``TS_OPERATORS`` here.
"""

from __future__ import annotations

from typing import Iterable, Optional

from . import ops

#: canonical order of ``ts_operators.md``
TS_OPERATORS: tuple[str, ...] = (
    "ts_arg_max",
    "ts_arg_min",
    "ts_av_diff",
    "ts_bollinger_percent",
    "ts_bollinger_position",
    "ts_bollinger_width",
    "ts_count_nans",
    "ts_decay_linear",
    "ts_delta",
    "ts_ema",
    "ts_entropy",
    "ts_extreme_ratio",
    "ts_gain_loss_ratio",
    "ts_hhi",
    "ts_ir",
    "ts_mad",
    "ts_max",
    "ts_max_diff",
    "ts_max_drawdown",
    "ts_mean",
    "ts_median",
    "ts_min",
    "ts_min_diff",
    "ts_min_max_diff",
    "ts_percentage",
    "ts_positive_ratio",
    "ts_product",
    "ts_quantile",
    "ts_range",
    "ts_rank",
    "ts_returns",
    "ts_scale",
    "ts_std_dev",
    "ts_sum",
    "ts_zscore",
)

#: operators outside the time-series family (registry-driven, always approved)
NON_TS_OPERATORS: tuple[str, ...] = tuple(
    sorted(name for name, op in ops.REGISTRY.items() if op.category != "time-series")
)

APPROVED_OPERATORS: tuple[str, ...] = tuple(
    dict.fromkeys(TS_OPERATORS + NON_TS_OPERATORS)
)
APPROVED_SET: frozenset[str] = frozenset(APPROVED_OPERATORS)

#: helpful hints when an agent reaches for a legacy / unlisted operator
REPLACEMENTS: dict[str, str] = {
    "ts_std": "ts_std_dev",
    "ts_corr": "no direct replacement; rebuild it from approved operators",
    "ts_cov": "no direct replacement; rebuild it from approved operators",
    "ts_skew": "no direct replacement",
    "ts_kurt": "no direct replacement",
    "ts_argmax": "ts_arg_max",
    "ts_argmin": "ts_arg_min",
    "delay": "ts_delta / ts_returns (or subtract the lagged term explicitly)",
    "delta": "ts_delta",
}


def is_approved(name: str) -> bool:
    return name in APPROVED_SET


def check_operator(name: str) -> Optional[str]:
    """Return an error message when ``name`` is not in the approved set."""
    if is_approved(name):
        return None
    hint = REPLACEMENTS.get(name)
    base = f"operator {name!r} is not in the approved operator set"
    if not hint:
        return base
    return f"{base}; {hint}" if hint.startswith("no ") else f"{base}; use {hint}"


def catalog_text() -> str:
    """Operator cheat-sheet limited to the approved set (for agent 2.2)."""
    return ops.catalog_text(only=APPROVED_SET)


def missing_from_registry() -> list[str]:
    """Approved names that are not implemented yet (should stay empty)."""
    return [name for name in APPROVED_OPERATORS if name not in ops.REGISTRY]

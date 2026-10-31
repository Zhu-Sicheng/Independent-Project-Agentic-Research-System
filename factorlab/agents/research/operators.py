"""Vetted pandas operator subset. Markdown is documentation, never executable code."""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

import numpy as np
import pandas as pd

from agent1.core import sha256_file
from .common import digest

REGISTRY_VERSION = "pandas-strict-warmup-v1"


@dataclasses.dataclass(frozen=True)
class Operator:
    name: str
    parameters: tuple[str, ...] = ("x", "d")
    defaults: tuple = ()
    dimensionless: bool = False
    shift_based: bool = False
    recursive: bool = False
    minimum_window: int = 1


SPECS = {name: Operator(name) for name in (
    "ts_av_diff", "ts_max", "ts_max_diff", "ts_mean", "ts_median", "ts_min", "ts_min_diff", "ts_range", "ts_sum")}
SPECS.update({
    "ts_delta": Operator("ts_delta", shift_based=True),
    "ts_returns": Operator("ts_returns", ("x", "d", "mode"), (1,), True, True),
    "ts_std_dev": Operator("ts_std_dev", minimum_window=2),
    "ts_zscore": Operator("ts_zscore", dimensionless=True, minimum_window=2),
    "ts_ir": Operator("ts_ir", dimensionless=True, minimum_window=2),
    "ts_count_nans": Operator("ts_count_nans", dimensionless=True),
    "ts_extreme_ratio": Operator("ts_extreme_ratio", dimensionless=True),
    "ts_ema": Operator("ts_ema", recursive=True),
    "ts_scale": Operator("ts_scale", ("x", "d", "constant"), (0,), True),
    "ts_min_max_diff": Operator("ts_min_max_diff", ("x", "d", "f"), (0.5,)),
    "ts_percentage": Operator("ts_percentage", ("x", "d", "percentage"), (0.5,)),
    "ts_bollinger_percent": Operator("ts_bollinger_percent", ("x", "d", "k"), (2.0,), True, minimum_window=2),
    "ts_bollinger_position": Operator("ts_bollinger_position", ("x", "d", "k"), (2.0,), True, minimum_window=2),
    "ts_bollinger_width": Operator("ts_bollinger_width", ("x", "d", "k"), (2.0,), True, minimum_window=2),
})


def safe_div(left, right, epsilon=1e-12):
    if isinstance(right, (int, float)):
        return left / right if abs(right) > epsilon else left * np.nan
    return left / right.where(right.abs() > epsilon)


class OperatorRegistry:
    def __init__(self, document: str | Path):
        self.path = Path(document).resolve()
        content = self.path.read_text(encoding="utf-8-sig")
        import re
        documented = set(re.findall(r"^def (ts_[A-Za-z0-9_]+)\(", content, flags=re.MULTILINE))
        if not documented:
            raise ValueError("Operator document contains no recognized def ts_... declarations")
        self.enabled = {name: spec for name, spec in SPECS.items() if name in documented}
        self.disabled = {name: "The supplied helper implementation/semantics are incomplete; no executable implementation has been approved." for name in sorted(documented - self.enabled.keys())}
        if not self.enabled:
            raise ValueError("No documented operator has a vetted implementation")
        self.fingerprint = digest({"version": REGISTRY_VERSION, "document_sha256": sha256_file(self.path),
                                   "implementation_sha256": sha256_file(Path(__file__)), "enabled": sorted(self.enabled)})

    def describe(self) -> dict:
        return {"version": REGISTRY_VERSION, "fingerprint": self.fingerprint, "document": str(self.path),
            "document_sha256": sha256_file(self.path),
            "enabled": [{**dataclasses.asdict(spec), "source": "vetted_local_implementation"} for spec in self.enabled.values()],
            "disabled": self.disabled, "arithmetic": ["+", "-", "*", "/", "unary +/-", "safe_div(x, y)", "abs(x)", "field('literal column name')"],
            "policy": ["All windows are positive integer literals; no forward shifts.",
                "Rolling statistics require a full valid window, deliberately stricter than partial windows in the source document.",
                "Returns/delta use current and lagged values without filling; missing observations remain missing.",
                "ts_count_nans counts missing rows after a full calendar-index window.",
                "EMA uses full-span warmup and recursive history; it has no finite exact lookback.",
                "Division masks near-zero denominators; no infinity is passed downstream.",
                "Execution lag is applied separately after expression evaluation."]}

    def bind(self, node: ast.Call) -> tuple[Operator, list[ast.AST]]:
        name = node.func.id
        if name not in self.enabled:
            reason = self.disabled.get(name, "Unknown/unregistered operator")
            raise ValueError(f"{name}: {reason}")
        spec = self.enabled[name]
        if len(node.args) > len(spec.parameters):
            raise ValueError(f"Too many arguments for {name}")
        values = dict(zip(spec.parameters, node.args))
        for keyword in node.keywords:
            if keyword.arg is None or keyword.arg not in spec.parameters or keyword.arg in values:
                raise ValueError(f"Unknown/duplicate argument for {name}")
            values[keyword.arg] = keyword.value
        optional = dict(zip(spec.parameters[-len(spec.defaults):], spec.defaults)) if spec.defaults else {}
        for parameter in spec.parameters:
            if parameter not in values:
                if parameter not in optional:
                    raise ValueError(f"Missing argument {parameter} for {name}")
                values[parameter] = ast.Constant(optional[parameter])
        return spec, [values[parameter] for parameter in spec.parameters]

    def apply(self, name: str, values: list):
        spec = self.enabled[name]
        x, d = values[:2]
        if not isinstance(x, pd.DataFrame) or isinstance(d, bool) or not isinstance(d, int) or d < spec.minimum_window:
            raise ValueError("Operator input must be a date-by-entity matrix and a valid window")
        rolling = x.rolling(d, min_periods=d)
        extra = values[2] if len(values) > 2 else None
        if name == "ts_delta":
            result = x - x.shift(d)
        elif name == "ts_returns":
            result = safe_div(x - x.shift(d), x.shift(d)) * (100 if extra == 0 else 1)
        elif name == "ts_count_nans":
            result = x.isna().astype(float).rolling(d, min_periods=d).sum()
        elif name == "ts_ema":
            result = x.ewm(span=d, adjust=False, min_periods=d).mean().where(rolling.count() == d)
        elif name in {"ts_mean", "ts_median", "ts_max", "ts_min", "ts_sum"}:
            result = getattr(rolling, name.removeprefix("ts_"))()
        elif name == "ts_std_dev":
            result = rolling.std(ddof=0)
        elif name in {"ts_zscore", "ts_ir", "ts_bollinger_percent", "ts_bollinger_position", "ts_bollinger_width"}:
            mean, std = rolling.mean(), rolling.std(ddof=0)
            if name == "ts_zscore":
                result = safe_div(x - mean, std, epsilon=1e-14).mask((std.abs() < 1e-14) & std.notna(), 0.0)
            elif name == "ts_ir":
                result = safe_div(mean, std, epsilon=1e-10)
            elif name == "ts_bollinger_width":
                result = safe_div(2 * extra * std, mean.abs())
            else:
                result = safe_div(x - (mean - extra * std), 2 * extra * std)
                if name == "ts_bollinger_position":
                    result = result.clip(0, 1)
        elif name == "ts_av_diff":
            result = x - rolling.mean()
        elif name == "ts_max_diff":
            result = x - rolling.max()
        elif name == "ts_min_diff":
            result = x - rolling.min()
        elif name == "ts_min_max_diff":
            result = x - extra * (rolling.min() + rolling.max())
        elif name == "ts_range":
            result = rolling.max() - rolling.min()
        elif name == "ts_extreme_ratio":
            result = safe_div(rolling.max(), rolling.min())
        elif name == "ts_scale":
            result = safe_div(x - rolling.min(), rolling.max() - rolling.min(), epsilon=1e-10) + extra
        elif name == "ts_percentage":
            result = rolling.quantile(extra)
        else:
            raise ValueError(f"No implementation for {name}")
        return result.replace([np.inf, -np.inf], np.nan)

"""Interpret a parsed expression against a :class:`PanelStore`."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

import numpy as np
import pandas as pd

from ..data.panel import PanelStore
from . import parser as P
from .ops import REGISTRY, OpError

Value = Any  # pd.DataFrame | float | bool


class EvalError(ValueError):
    pass


@dataclass
class EvalContext:
    panel: PanelStore
    variables: Dict[str, Any] = field(default_factory=dict)


def _clean(value: Value) -> Value:
    if isinstance(value, pd.DataFrame):
        return value.replace([np.inf, -np.inf], np.nan).astype("float64")
    return value


def _truthy(value: Value) -> Value:
    if isinstance(value, pd.DataFrame):
        if value.dtypes.iloc[0] == bool:
            return value
        return value.fillna(False).astype(bool)
    return bool(value)


class Evaluator:
    def __init__(self, ctx: EvalContext):
        self.ctx = ctx

    # ------------------------------------------------------------------ #
    def eval(self, node: P.Expr) -> Value:
        if isinstance(node, P.Num):
            return node.value
        if isinstance(node, P.Str):
            return node.value
        if isinstance(node, P.Const):
            return P.CONSTANTS[node.name]
        if isinstance(node, P.Var):
            return self._var(node.name)
        if isinstance(node, P.Unary):
            return self._unary(node.op, self.eval(node.x))
        if isinstance(node, P.Bin):
            return self._bin(node.op, self.eval(node.left), self.eval(node.right))
        if isinstance(node, P.Call):
            return self._call(node)
        raise EvalError(f"cannot evaluate node {node!r}")

    # ------------------------------------------------------------------ #
    def _var(self, name: str) -> Value:
        if name in self.ctx.variables:
            return self.ctx.variables[name]
        panel = self.ctx.panel
        try:
            return panel.field(name)
        except Exception as exc:  # PanelError
            raise EvalError(str(exc)) from exc

    def _unary(self, op: str, x: Value) -> Value:
        if op == "-":
            return -x
        if op == "!":
            if isinstance(x, pd.DataFrame):
                return ~x if x.dtypes.iloc[0] == bool else x.fillna(False).eq(0)
            return not bool(x)
        raise EvalError(f"unknown unary operator {op!r}")

    def _bin(self, op: str, a: Value, b: Value) -> Value:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            with np.errstate(divide="ignore", invalid="ignore"):
                out = a / b
            return _clean(out)
        if op == "^":
            with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
                out = a**b
            return _clean(out)
        if op in (">", "<", ">=", "<=", "==", "!="):
            if op == ">":
                return a > b
            if op == "<":
                return a < b
            if op == ">=":
                return a >= b
            if op == "<=":
                return a <= b
            if op == "==":
                return a == b
            return a != b
        if op in ("&", "&&"):
            return _truthy(a) & _truthy(b)
        if op in ("|", "||"):
            return _truthy(a) | _truthy(b)
        raise EvalError(f"unknown operator {op!r}")

    def _call(self, node: P.Call) -> Value:
        op = REGISTRY.get(node.name)
        if op is None:
            raise EvalError(f"unknown operator {node.name!r}")
        if not (op.min_args <= len(node.args) <= op.max_args):
            raise EvalError(
                f"{node.name} takes {op.min_args}..{op.max_args} args, got {len(node.args)}"
            )
        args = [self.eval(a) for a in node.args]
        try:
            return _clean(op.func(*args))
        except EvalError:
            raise
        except OpError as exc:
            raise EvalError(str(exc)) from exc
        except Exception as exc:
            raise EvalError(f"{node.name} failed: {exc}") from exc


def evaluate(node: P.Expr, panel: PanelStore, variables: Dict[str, Any] | None = None) -> pd.DataFrame:
    """Evaluate an AST and guarantee a float panel matrix comes back."""
    ctx = EvalContext(panel=panel, variables=variables or {})
    value = Evaluator(ctx).eval(node)
    if not isinstance(value, pd.DataFrame):
        raise EvalError(
            "expression evaluates to a scalar; it must produce a date x ticker matrix"
        )
    if value.shape != panel.shape:
        value = value.reindex(index=panel.dates, columns=panel.tickers)
    if value.isna().all().all():
        raise EvalError("expression produces an all-NaN matrix")
    return value.astype("float64")


def evaluate_text(text: str, panel: PanelStore, variables: Dict[str, Any] | None = None) -> pd.DataFrame:
    return evaluate(P.parse(text), panel, variables)

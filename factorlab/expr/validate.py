"""Static checks for expressions / scripts before anything is executed."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

import pandas as pd

from ..config import ALLOWED_WINDOWS
from ..data.panel import PanelStore
from . import parser as P
from . import approved
from .ops import REGISTRY


@dataclass
class ValidationReport:
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ast: Optional[P.Expr] = None
    windows: tuple[int, ...] = ()
    fields: tuple[str, ...] = ()
    ops: tuple[str, ...] = ()
    text: str = ""

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.ok = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def raise_if_bad(self) -> None:
        if not self.ok:
            raise ExpressionValidationError("; ".join(self.errors))

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "windows": list(self.windows),
            "fields": list(self.fields),
            "ops": list(self.ops),
        }


class ExpressionValidationError(ValueError):
    pass


def validate_expression(
    text: str,
    panel: Optional[PanelStore] = None,
    strict_windows: bool = True,
    allowed_windows: Iterable[int] = ALLOWED_WINDOWS,
    max_ops: int = 40,
    max_length: int = 800,
    approved_only: bool = True,
    min_window: int = 2,
) -> ValidationReport:
    report = ValidationReport(text=text)
    if not text or not text.strip():
        report.add_error("empty expression")
        return report
    if len(text) > max_length:
        report.add_error(f"expression longer than {max_length} characters")
        return report

    try:
        ast = P.parse(text)
    except P.ExpressionError as exc:
        report.add_error(f"parse error: {exc}")
        return report

    report.ast = ast
    calls, binops = [], 0
    for node in P.walk(ast):
        if isinstance(node, P.Call):
            calls.append(node.name)
            op = REGISTRY.get(node.name)
            if op is None:
                report.add_error(
                    f"unknown operator {node.name!r}; see the operator catalog"
                )
                continue
            if approved_only:
                message = approved.check_operator(node.name)
                if message:
                    report.add_error(message)
            if not (op.min_args <= len(node.args) <= op.max_args):
                report.add_error(
                    f"{node.name} expects {op.min_args}..{op.max_args} arguments, "
                    f"got {len(node.args)}"
                )
            for idx in op.window_positions():
                if idx >= len(node.args):
                    continue
                arg = node.args[idx]
                if not isinstance(arg, P.Num):
                    report.add_error(
                        f"{node.name}: window argument must be a literal integer"
                    )
                elif int(arg.value) != arg.value or int(arg.value) < min_window:
                    report.add_error(
                        f"{node.name}: window {arg.value} must be an integer >= {min_window}"
                    )
            for idx in op.lag_positions():
                if idx >= len(node.args):
                    continue
                arg = node.args[idx]
                if not isinstance(arg, P.Num):
                    report.add_error(f"{node.name}: lag argument must be a literal integer")
                elif int(arg.value) != arg.value or not (1 <= int(arg.value) <= 500):
                    report.add_error(
                        f"{node.name}: lag {arg.value} must be an integer between 1 and 500"
                    )
        elif isinstance(node, P.Var):
            if panel is not None and not panel.has(node.name):
                report.add_error(
                    f"unknown field {node.name!r}; available fields: "
                    f"{', '.join(panel.available())}"
                )
        elif isinstance(node, P.Bin):
            binops += 1

    report.ops = tuple(calls)
    report.fields = tuple(P.collect_vars(ast))
    report.windows = tuple(P.collect_windows(ast))

    if not report.fields:
        report.add_error("expression does not reference any data field")
    if len(calls) + binops > max_ops:
        report.add_error(f"expression is too complex ({len(calls) + binops} operations)")

    if strict_windows:
        allowed = set(int(w) for w in allowed_windows)
        for w in report.windows:
            if w not in allowed:
                report.add_error(
                    f"window {w} is not an accepted horizon; allowed: {sorted(allowed)}"
                )

    if "rank" in report.ops and "sign" in report.ops:
        report.add_warning("both rank() and sign() appear; check the intent")

    return report


def check_spec_dict(spec: dict) -> list[str]:
    """Cheap structural checks used on raw agent output."""
    errors = []
    kind = spec.get("kind")
    if kind not in ("expression", "script"):
        errors.append("kind must be 'expression' or 'script'")
    if kind == "expression" and not str(spec.get("expression", "")).strip():
        errors.append("expression is empty")
    if kind == "script" and not str(spec.get("script", "")).strip():
        errors.append("script is empty")
    if kind == "script" and not isinstance(spec.get("params", {}) or {}, dict):
        errors.append("params must be an object")
    if kind == "script" and not isinstance(spec.get("param_grid", {}) or {}, dict):
        errors.append("param_grid must be an object")
    return errors

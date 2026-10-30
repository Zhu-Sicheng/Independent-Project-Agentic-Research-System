"""A factor program: either a declarative expression or a python script.

``FactorSpec`` is the hand-off format between the implementer agent (2.2) and the
execution layer.  It is serialisable, hashable (see :meth:`canonical`) and
knows how to turn itself into a date x ticker matrix.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Optional

import pandas as pd

from ..config import ALLOWED_WINDOWS
from ..data.panel import PanelStore
from . import parser as P
from .evaluator import EvalError, evaluate, evaluate_text
from .script import ScriptError, run_script, validate_script
from .validate import ValidationReport, check_spec_dict, validate_expression


class SpecError(ValueError):
    pass


@dataclass
class FactorSpec:
    kind: str = "expression"  # expression | script
    expression: str = ""
    script: str = ""
    params: dict = field(default_factory=dict)
    param_grid: dict = field(default_factory=dict)
    explanation: str = ""
    name: str = ""
    notes: str = ""

    # ------------------------------------------------------------------ #
    @classmethod
    def from_dict(cls, data: dict) -> "FactorSpec":
        data = dict(data or {})
        errors = check_spec_dict(data)
        if errors:
            raise SpecError("; ".join(errors))
        return cls(
            kind=str(data.get("kind", "expression")),
            expression=str(data.get("expression", "") or ""),
            script=str(data.get("script", "") or ""),
            params=dict(data.get("params", {}) or {}),
            param_grid=dict(data.get("param_grid", {}) or {}),
            explanation=str(data.get("explanation", "") or ""),
            name=str(data.get("name", "") or ""),
            notes=str(data.get("notes", "") or ""),
        )

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "expression": self.expression,
            "script": self.script,
            "params": self.params,
            "param_grid": self.param_grid,
            "explanation": self.explanation,
            "name": self.name,
            "notes": self.notes,
        }

    # ------------------------------------------------------------------ #
    def canonical(self) -> str:
        payload = {
            "kind": self.kind,
            "expression": P.to_string(P.parse(self.expression)) if self.expression else "",
            "script": self.script.strip(),
            "params": self.params,
            "param_grid": self.param_grid,
        }
        blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return blob

    def fingerprint(self, length: int = 8) -> str:
        return hashlib.sha1(self.canonical().encode("utf-8")).hexdigest()[:length]

    # ------------------------------------------------------------------ #
    def ast(self) -> P.Expr:
        if self.kind != "expression":
            raise SpecError("only expression specs have an AST")
        return P.parse(self.expression)

    @property
    def windows(self) -> list[int]:
        if self.kind != "expression" or not self.expression:
            return []
        return P.collect_windows(P.parse(self.expression))

    # ------------------------------------------------------------------ #
    def validate(
        self,
        panel: Optional[PanelStore] = None,
        strict_windows: bool = True,
        strict_operators: bool = True,
    ) -> ValidationReport:
        if self.kind == "expression":
            return validate_expression(
                self.expression,
                panel=panel,
                strict_windows=strict_windows,
                approved_only=strict_operators,
            )
        report = ValidationReport(text=self.script)
        errors = validate_script(self.script)
        for err in errors:
            report.add_error(err)
        for key, values in self.param_grid.items():
            if not isinstance(values, (list, tuple)) or not values:
                report.add_error(f"param_grid[{key!r}] must be a non-empty list")
                continue
            for v in values:
                if not isinstance(v, (int, float)) or int(v) != v or int(v) < 2:
                    report.add_error(
                        f"param_grid[{key!r}] value {v!r} must be an integer >= 2"
                    )
                elif int(v) not in ALLOWED_WINDOWS:
                    report.add_warning(
                        f"param_grid[{key!r}] value {v!r} is not one of the "
                        f"economically meaningful windows {list(ALLOWED_WINDOWS)}"
                    )
        return report

    # ------------------------------------------------------------------ #
    def materialize(self, panel: PanelStore, params: Optional[dict] = None) -> pd.DataFrame:
        if self.kind == "expression":
            return evaluate_text(self.expression, panel)
        merged = dict(self.params)
        merged.update(params or {})
        return run_script(self.script, panel, merged)

    # ------------------------------------------------------------------ #
    def param_combos(self) -> list[dict]:
        if not self.param_grid:
            return [dict(self.params)]
        import itertools

        keys = list(self.param_grid)
        combos = []
        for values in itertools.product(*[self.param_grid[k] for k in keys]):
            merged = dict(self.params)
            merged.update(dict(zip(keys, values)))
            combos.append(merged)
        return combos

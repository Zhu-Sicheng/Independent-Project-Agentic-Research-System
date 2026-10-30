"""Agent 2.2 — the implementer: turn a hypothesis into a factor matrix.

Boundary with Agent 2.1 (``hypothesis.py``): 2.1 only produces an economic
story plus a natural-language recipe; it never writes code.  2.2 owns the whole
translation problem: choose expression vs. script, pick fields/operators/
windows, and return a :class:`FactorSpec` that can be materialised into a
``date x ticker`` matrix.
"""

from __future__ import annotations

from typing import Optional

from . import fallback
from .llm import LLMClient, LLMError
from .prompts import implementer_system, implementer_user
from ..data.panel import PanelStore
from ..expr.spec import FactorSpec, SpecError


class ImplementationAgent:
    """Agent 2.2: natural language -> expression or per-day python script."""

    def __init__(self, llm: LLMClient, max_repairs: int = 2):
        self.llm = llm
        self.max_repairs = max_repairs

    def implement(
        self,
        hypothesis: dict,
        panel: PanelStore,
        feedback: str = "",
        previous: Optional[dict] = None,
    ) -> FactorSpec:
        if self.llm.available:
            spec, errors = self._from_llm(hypothesis, panel, feedback, previous)
            if spec is not None:
                return spec
            feedback = (feedback + "\n" if feedback else "") + "Previous errors: " + "; ".join(
                errors
            )
        return self._from_template(hypothesis, panel, feedback)

    # ------------------------------------------------------------------ #
    def _from_llm(
        self,
        hypothesis: dict,
        panel: PanelStore,
        feedback: str,
        previous: Optional[dict],
    ) -> tuple[Optional[FactorSpec], list[str]]:
        errors: list[str] = []
        attempt = previous
        for _ in range(self.max_repairs + 1):
            try:
                raw = self.llm.complete_json(
                    implementer_system(),
                    implementer_user(hypothesis, panel.summary(), feedback, attempt),
                )
                spec = FactorSpec.from_dict(raw)
            except (LLMError, SpecError, KeyError, TypeError, ValueError) as exc:
                errors = [str(exc)]
                feedback = "Your previous answer was rejected: " + str(exc)
                continue

            report = spec.validate(panel)
            if report.ok:
                return spec, []
            errors = report.errors
            feedback = "The expression failed validation: " + "; ".join(errors)
            attempt = spec.to_dict()

        return None, errors

    def _from_template(
        self, hypothesis: dict, panel: PanelStore, feedback: str
    ) -> FactorSpec:
        data = fallback.template_spec(hypothesis)
        spec = FactorSpec.from_dict(data)
        report = spec.validate(panel, strict_windows=False)
        if not report.ok:
            # never silently swap in a different factor: the label would lie
            raise SpecError(
                "template factor for hypothesis "
                f"{hypothesis.get('name')!r} failed validation: {report.errors}"
            )
        spec.name = hypothesis.get("name", spec.name)
        return spec

"""Agent 3 — the research director: accepts, optimises or abandons."""

from __future__ import annotations

from typing import Optional

from . import fallback
from .llm import LLMClient, LLMError
from .prompts import critic_system, critic_user
from ..backtest.grid import GridResult
from ..data.panel import PanelStore
from ..expr.spec import FactorSpec, SpecError

DECISIONS = ("accept", "optimize", "abandon")


class CriticAgent:
    """Agent 3: judges evidence against the story, not just the Sharpe."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def review(
        self,
        hypothesis: dict,
        spec: FactorSpec,
        grid: GridResult,
        history: list[dict],
        panel: PanelStore,
        max_rounds: int = 2,
        stability: Optional[dict] = None,
    ) -> dict:
        summary = grid.summary()
        if stability:
            summary["stability"] = stability
        yearly = summary.get("yearly", [])
        if self.llm.available:
            try:
                raw = self.llm.complete_json(
                    critic_system(),
                    critic_user(hypothesis, spec.to_dict(), summary, history, max_rounds),
                )
                result = self._normalise(raw, spec, panel)
                if result is not None:
                    result["source"] = "llm"
                    return result
            except (LLMError, KeyError, TypeError, ValueError):
                pass
        result = fallback.review(
            hypothesis, spec.to_dict(), summary, yearly, history, max_rounds=max_rounds
        )
        result["source"] = result.get("source", "offline-rules")
        return result

    # ------------------------------------------------------------------ #
    def _normalise(self, raw, spec: FactorSpec, panel: PanelStore) -> Optional[dict]:
        if not isinstance(raw, dict):
            return None
        decision = str(raw.get("decision", "")).lower().strip()
        if decision not in DECISIONS:
            return None
        try:
            confidence = float(raw.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        revised = raw.get("revised")
        if decision == "optimize":
            if not isinstance(revised, dict) or not revised:
                return None
            try:
                new_spec = FactorSpec.from_dict(revised)
            except SpecError:
                return None
            if not new_spec.validate(panel).ok:
                return None
            revised = new_spec.to_dict()
        else:
            revised = None
        suggestions = raw.get("suggested_changes") or []
        if not isinstance(suggestions, list):
            suggestions = [str(suggestions)]
        return {
            "decision": decision,
            "confidence": max(0.0, min(1.0, confidence)),
            "reasoning": str(raw.get("reasoning", "")),
            "diagnosis": str(raw.get("diagnosis", "")),
            "hypothesis_supported": bool(raw.get("hypothesis_supported", decision == "accept")),
            "suggested_changes": [str(s) for s in suggestions],
            "revised": revised,
        }

"""Agent 2.1 — the economist: data -> economically motivated hypotheses.

Boundary with Agent 2.2 (``implementer.py``): this agent never writes an
expression or a script; it only describes the mechanism and the recipe.
"""

from __future__ import annotations

from typing import Optional

from . import fallback
from .llm import LLMClient, LLMError
from .prompts import hypothesis_system, hypothesis_user


class HypothesisAgent:
    """Agent 2.1: proposes falsifiable, economically motivated factors."""

    def __init__(self, llm: LLMClient, n: int = 3):
        self.llm = llm
        self.n = n

    def propose(
        self,
        panel_summary: dict,
        pool_summary: Optional[list[dict]] = None,
        tried: Optional[list[str]] = None,
        feedback: str = "",
    ) -> list[dict]:
        tried = list(tried or [])
        pool_summary = list(pool_summary or [])
        if self.llm.available:
            try:
                raw = self.llm.complete_json(
                    hypothesis_system(),
                    hypothesis_user(panel_summary, pool_summary, self.n, tried, feedback),
                )
                hypotheses = self._normalise(raw)
                if hypotheses:
                    for h in hypotheses:
                        h["source"] = "llm"
                    return hypotheses[: self.n]
            except (LLMError, KeyError, TypeError, ValueError):
                pass
        hypotheses = fallback.offline_hypotheses(self.n, exclude=tried)
        for h in hypotheses:
            h["source"] = "offline-rules"
        return hypotheses

    # ------------------------------------------------------------------ #
    def _normalise(self, raw) -> list[dict]:
        if isinstance(raw, dict):
            items = raw.get("hypotheses") or raw.get("factors") or []
        elif isinstance(raw, list):
            items = raw
        else:
            items = []
        out: list[dict] = []
        seen: set[str] = set()
        for item in items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            if not name or name in seen:
                continue
            description = str(
                item.get("factor_description") or item.get("description") or ""
            ).strip()
            hypothesis = str(item.get("hypothesis") or item.get("idea") or "").strip()
            if not description or not hypothesis:
                continue
            try:
                horizon = int(item.get("horizon_days", 20))
            except (TypeError, ValueError):
                horizon = 20
            sign = str(item.get("expected_sign", "positive")).lower()
            if sign not in ("positive", "negative"):
                sign = "positive"
            fields = item.get("data_fields") or []
            if not isinstance(fields, list):
                fields = [str(fields)]
            seen.add(name)
            out.append(
                {
                    "name": name,
                    "economic_rationale": str(item.get("economic_rationale", "")),
                    "hypothesis": hypothesis,
                    "factor_description": description,
                    "data_fields": [str(f) for f in fields],
                    "horizon_days": horizon,
                    "expected_sign": sign,
                    "testable_prediction": str(item.get("testable_prediction", "")),
                    "novelty": str(item.get("novelty", "")),
                }
            )
        return out

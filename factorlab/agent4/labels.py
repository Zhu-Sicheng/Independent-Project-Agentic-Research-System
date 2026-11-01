"""Human labels for display figures: ``H<i>-F<j>`` = i-th hypothesis, j-th factor.

Figure titles must never expose internal expression ids or long formulas, and
non-ASCII hypothesis titles fall back to the ordinal label so no CJK font is
required inside matplotlib.
"""

from __future__ import annotations

import re

_STOPWORDS = {
    "a", "an", "the", "of", "and", "or", "to", "in", "on", "for", "with", "after",
    "before", "from", "by", "as", "at", "is", "are", "be", "when", "then", "than",
    "that", "this", "its", "their", "it", "into", "via", "per", "vs", "versus",
    "predict", "predicts", "predicting", "associated", "driven", "does", "do",
    "using", "use", "based", "which", "while", "if", "not", "no", "can", "will",
}
_GENERIC_TITLE_WORDS = {"etf", "spy", "spdr", "s", "p", "500", "us", "usa", "index", "series"}

def _slugify_title(title: str, max_words: int = 4) -> str:
    """Short readable slug of a hypothesis title (never an id or raw text)."""
    text = re.sub(r"[^A-Za-z0-9]+", " ", str(title or "")).lower()
    words = [
        word
        for word in text.split()
        if len(word) >= 3
        and not word.isdigit()
        and word not in _STOPWORDS
        and word not in _GENERIC_TITLE_WORDS
    ]
    return "-".join(words[:max_words])[:52].strip("-")


def display_labels(ideas: dict, records: list[dict]) -> dict:
    """Map expression_id -> {"label": H03-F2, "hypothesis": ..., "slug": ...}.

    ``H<i>`` is the i-th hypothesis the ideation agent produced and ``F<j>`` the
    j-th factor derived from it, which is what the display figures show instead
    of internal ids or long formulas.
    """
    order = {idea_id: index + 1 for index, idea_id in enumerate(ideas)}
    counts: dict = {}
    labels: dict = {}
    for record in records:
        expression_id = record.get("expression_id")
        if not expression_id:
            continue
        idea_id = record.get("idea_id")
        counts[idea_id] = counts.get(idea_id, 0) + 1
        position = counts[idea_id]
        index = order.get(idea_id)
        label = f"H{index:02d}-F{position:02d}" if index else f"F{position:02d}"
        idea = ideas.get(idea_id) or {}
        title = idea.get("title") or record.get("hypothesis") or ""
        labels[expression_id] = {
            "label": label,
            "hypothesis": str(title),
            "slug": _slugify_title(title),
        }
    return labels

"""Agent 5b -- feedback-round decisions (no out-of-sample input).

* :func:`round_improved` -- did a feedback round beat the best in-sample Sharpe?
* :func:`candidates_from_revisions` -- turn the reviewer's ``optimize``
  suggestion into the next round's candidate (offline fallback only).
"""

from __future__ import annotations

def round_improved(round_best: float, best_so_far: float, tolerance: float = 1e-9) -> bool:
    """True when a feedback round produced a better in-sample result than before."""
    import math

    if not isinstance(round_best, (int, float)) or not math.isfinite(round_best):
        return False
    if not isinstance(best_so_far, (int, float)) or not math.isfinite(best_so_far):
        return True
    return float(round_best) > float(best_so_far) + tolerance


def candidates_from_revisions(records: list[dict]) -> list[dict]:
    """Offline fallback: turn the reviewer's ``optimize`` suggestions into candidates."""
    candidates = []
    for record in records:
        revised = record.get("revised_expression")
        if not revised:
            continue
        candidates.append(
            {
                "expression_id": f"revised_{record['expression_id']}",
                "idea_id": record.get("idea_id"),
                "expression": revised,
                "status": "critic_revision",
                "hypothesis": None,
            }
        )
    return candidates

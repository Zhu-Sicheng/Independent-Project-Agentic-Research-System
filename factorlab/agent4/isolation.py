"""Data-isolation contract: the optimisation loop only ever sees in-sample data."""

from __future__ import annotations

IS_END_DEFAULT = "2020-12-31"

IS_PROTOCOL = (
    "IS-only evaluation: the panel was cut at the in-sample end, so no "
    "out-of-sample or holdout numbers exist for this decision. Judge the story, "
    "the in-sample metrics and the stability battery only; never ask for or "
    "invent OOS numbers."
)


def split_is_panel(panel, is_end: str = IS_END_DEFAULT):
    """The only panel the optimisation loop may see."""
    return panel.subset(end=is_end)

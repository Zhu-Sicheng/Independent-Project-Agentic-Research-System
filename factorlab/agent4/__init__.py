"""Agent 4: our in-sample evaluation, stability and display layer.

* :mod:`agent4.isolation` -- in-sample panel cut and the ``IS-only`` protocol
* :mod:`agent4.evaluation` -- grid search + stability + reviewer on the IS panel
* :mod:`agent4.labels` -- ``H<i>-F<j>`` display labels
* :mod:`agent4.display` -- OOS/holdout metrics and figures (presentation only)
"""

from .display import display_evaluation
from .evaluation import (
    _canonical,
    _grid_settings,
    _load_factor,
    evaluate_is_candidates,
    hypothesis_from_idea,
)
from .isolation import IS_END_DEFAULT, IS_PROTOCOL, split_is_panel
from .labels import _slugify_title, display_labels

__all__ = [
    "IS_END_DEFAULT",
    "IS_PROTOCOL",
    "split_is_panel",
    "_canonical",
    "_grid_settings",
    "_load_factor",
    "evaluate_is_candidates",
    "hypothesis_from_idea",
    "_slugify_title",
    "display_labels",
    "display_evaluation",
]

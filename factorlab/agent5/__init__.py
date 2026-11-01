"""Agent 5: our feedback / decision layer.

* :mod:`agent5.feedback` -- in-sample feedback records for the agents' memory
* :mod:`agent5.decision` -- round-improvement checks and reviewer revisions
"""

from .decision import candidates_from_revisions, round_improved
from .feedback import write_feedback

__all__ = ["write_feedback", "round_improved", "candidates_from_revisions"]

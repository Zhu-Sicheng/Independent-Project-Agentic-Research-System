"""Agent-5 feedback records: round-unique identity and crash safety."""

import tempfile
import unittest
from pathlib import Path

from factorlab.agent5.feedback import write_feedback


def make_record(expression_id: str, round_index: int, sharpe: float) -> dict:
    return {
        "status": "evaluated",
        "expression_id": expression_id,
        "round": round_index,
        "expression": "ts_zscore(close, 20)",
        "decision": "optimize",
        "reasoning": "needs smoothing",
        "is": {"metrics": {"sharpe": sharpe, "ann_return": 0.05, "turnover": 10.0,
                           "max_drawdown": -0.1, "rank_ic": 0.01, "pearson_ic": 0.02}},
        "stability_is": {"flags": []},
        "_dataset_id": "ds_market",
        "_family": "momentum",
    }


class TestFeedbackIdentity(unittest.TestCase):
    def test_same_expression_in_different_rounds_is_not_a_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.sqlite3"
            first = write_feedback(db, [make_record("expr_1", 0, 0.5)], "run_a", "2020-12-31")
            second = write_feedback(db, [make_record("expr_1", 1, 0.7)], "run_a", "2020-12-31")
            self.assertEqual(first, 1)
            self.assertEqual(second, 1)

    def test_identical_feedback_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "memory.sqlite3"
            record = make_record("expr_2", 0, 0.4)
            self.assertEqual(write_feedback(db, [record], "run_b", "2020-12-31"), 1)
            # a re-run of the same round must not raise and must not duplicate
            self.assertEqual(write_feedback(db, [record], "run_b", "2020-12-31"), 0)


if __name__ == "__main__":
    unittest.main()

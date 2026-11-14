"""Campaign report: merge per-run evaluations into one publishable summary."""

import json
import tempfile
import unittest
from pathlib import Path

from factorlab.campaign_report import build_summary, load_records, write_report


def _record(round_index: int, expression: str, is_sharpe: float, oos_sharpe: float,
            holdout_sharpe: float, decision: str = "abandon") -> dict:
    return {
        "round": round_index,
        "expression_id": f"expr_{round_index}",
        "hypothesis": f"hypothesis {round_index}",
        "expression": expression,
        "status": "evaluated",
        "decision": decision,
        "review_source": "offline-rules",
        "is": {"n_evals": 8, "metrics": {"sharpe": is_sharpe, "ann_return": 0.05,
                                          "turnover": 10.0, "max_drawdown": -0.1,
                                          "rank_ic": 0.01}},
        "stability_is": {"subuniverse_sharpe": is_sharpe * 0.8},
        "display": {"segments": {
            "oos": {"sharpe": oos_sharpe, "ann_return": 0.02, "rank_ic": 0.004},
            "holdout": {"sharpe": holdout_sharpe, "ann_return": 0.01, "rank_ic": 0.003},
        }},
        "revision": 0,
        "updated_at": "2026-11-01T00:00:00+00:00",
    }


class TestCampaignReport(unittest.TestCase):
    def _make_campaign(self, root: Path) -> None:
        for run_id, records in (
            ("run_a", [_record(0, "ts_mean(close, 5)", 1.2, 0.5, 0.2, "accept"),
                       _record(1, "ts_mean(close, 20)", 0.4, -0.1, 0.1)]),
            ("run_b", [_record(0, "ts_zscore(volume, 20)", 0.9, 0.3, -0.2, "optimize")]),
        ):
            run_dir = root / run_id
            run_dir.mkdir(parents=True)
            (run_dir / "evaluations.json").write_text(
                json.dumps({"n_records": len(records), "records": records}), encoding="utf-8"
            )

    def test_merges_runs_and_dedupes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_campaign(root)
            rows, run_ids = load_records(root)
            self.assertEqual(sorted(run_ids), ["run_a", "run_b"])
            self.assertEqual(len(rows), 3)
            frame = build_summary(rows)
            self.assertEqual(len(frame), 3)
            self.assertAlmostEqual(float(frame.iloc[0]["is_sharpe"]), 1.2)

    def test_writes_summary_and_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_campaign(root)
            frame = write_report(root, "test-campaign", top=5)
            self.assertEqual(len(frame), 3)
            self.assertTrue((root / "summary.csv").exists())
            text = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("test-campaign", text)
            self.assertIn("in-sample", text)
            self.assertIn("OOS Sharpe", text)

    def test_duplicate_expression_keeps_latest_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run_c"
            run_dir.mkdir(parents=True)
            first = _record(0, "ts_mean(close, 5)", 0.5, 0.0, 0.0)
            second = _record(1, "ts_mean(close, 5)", 0.9, 0.2, 0.1)
            second["revision"] = 1
            second["updated_at"] = "2026-11-02T00:00:00+00:00"
            (run_dir / "evaluations.json").write_text(
                json.dumps({"n_records": 2, "records": [first, second]}), encoding="utf-8"
            )
            rows, _ = load_records(root)
            frame = build_summary(rows)
            self.assertEqual(len(frame), 1)
            self.assertAlmostEqual(float(frame.iloc[0]["is_sharpe"]), 0.9)


if __name__ == "__main__":
    unittest.main()

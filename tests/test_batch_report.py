"""Batch report built from archived attempt records."""

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from factorlab.batch_report import collect, write_batch

ATTEMPT = {
    "hypothesis": "demo_factor",
    "attempt": 0,
    "spec": {"kind": "expression", "expression": "-ts_mean(returns, 5)"},
    "grid": {
        "n_evals": 72,
        "best": {"sharpe": 1.1, "ann_return": 0.05, "turnover": 20, "max_drawdown": -0.1, "rank_ic": 0.01},
        "in_sample": {"sharpe": 1.3},
        "out_of_sample": {"sharpe": 0.4, "ann_return": 0.02},
        "holdout": {"sharpe": -0.1},
        "subuniverse": {"metrics": {"sharpe": 0.2}},
        "stability": {"subuniverse_sharpe": 0.2, "min_pnl_corr": 0.1, "flags": ["subuniverse_halves_edge"]},
    },
    "review": {"decision": "abandon", "source": "llm"},
    "factor_id": None,
}


class TestBatchReport(unittest.TestCase):
    def test_collect_and_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "20260101-000000-p100_a_00"
            run_dir.mkdir(parents=True)
            (run_dir / "attempts.jsonl").write_text(json.dumps(ATTEMPT) + "\n", encoding="utf-8")
            other = root / "20260101-000000-other_00"
            other.mkdir(parents=True)
            (other / "attempts.jsonl").write_text(json.dumps(ATTEMPT) + "\n", encoding="utf-8")

            frame = collect("p100", records_dir=root)
            self.assertEqual(len(frame), 1)  # prefix filter keeps only the p100 run
            row = frame.iloc[0]
            self.assertEqual(row["expression"], "-ts_mean(returns, 5)")
            self.assertAlmostEqual(float(row["sharpe_oos"]), 0.4)
            self.assertEqual(row["stability_flags"], "subuniverse_halves_edge")

            target = write_batch("p100", root / "out", records_dir=root)
            self.assertTrue((target / "summary.csv").exists())
            self.assertTrue((target / "README.md").exists())
            saved = pd.read_csv(target / "summary.csv")
            self.assertEqual(len(saved), 1)


if __name__ == "__main__":
    unittest.main()

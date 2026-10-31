"""Aggregate experiment ledger."""

import json
import tempfile
import unittest
from pathlib import Path

from factorlab.experiments import (
    LEDGER_COLUMNS,
    flatten_attempt,
    load_ledger,
    rebuild_ledger,
)

ATTEMPT = {
    "hypothesis": "h1",
    "attempt": 0,
    "spec": {"kind": "expression", "expression": "-ts_mean(returns, 5)", "script": None},
    "validation": {"ok": True},
    "factor_id": None,
    "elapsed_s": 1.5,
    "error": None,
    "grid": {
        "best": {
            "decay": 5,
            "transform": "rank",
            "cap_filter": 0.3,
            "windows": [5],
            "params": {},
            "sharpe": 1.0,
            "ann_return": 0.1,
            "turnover": 50.0,
            "max_drawdown": -0.1,
            "rank_ic": 0.02,
            "pearson_ic": 0.01,
            "fitness": 1.5,
            "n_names": 400,
            "hit_rate": 0.51,
            "sub_sharpe": 0.8,
        },
        "in_sample": {"sharpe": 1.2, "ann_return": 0.12, "turnover": 50, "max_drawdown": -0.1, "rank_ic": 0.025},
        "out_of_sample": {"sharpe": 0.3, "ann_return": 0.03, "turnover": 40, "max_drawdown": -0.05, "rank_ic": 0.008},
        "holdout": {"sharpe": -0.1, "ann_return": -0.01, "turnover": 40, "max_drawdown": -0.08, "rank_ic": -0.002},
        "subuniverse": {
            "threshold": 0.3,
            "metrics": {"sharpe": 0.8, "ann_return": 0.08, "turnover": 45, "max_drawdown": -0.09, "rank_ic": 0.018},
            "segments": {"is": {"sharpe": 0.9}, "oos": {"sharpe": 0.2}, "holdout": {"sharpe": -0.2}},
        },
        "split": {
            "is_range": ["2000-01-03", "2020-12-31"],
            "oos_range": ["2021-01-04", "2024-12-31"],
            "holdout_range": ["2025-01-02", "2026-09-30"],
        },
    },
    "review": {"decision": "abandon", "source": "llm", "reasoning": "no"},
}


class TestLedger(unittest.TestCase):
    def test_flatten_attempt(self):
        row = flatten_attempt("20260101-010101-test", ATTEMPT, {"name": "panel", "n_dates": 100, "n_tickers": 10})
        self.assertEqual(row["run_id"], "20260101-010101-test")
        self.assertEqual(row["timestamp"], "2026-01-01 01:01:01")
        self.assertAlmostEqual(row["sharpe_oos"], 0.3)
        self.assertAlmostEqual(row["sharpe_holdout"], -0.1)
        self.assertAlmostEqual(row["rank_ic_oos"], 0.008)
        self.assertAlmostEqual(row["sharpe_sub"], 0.8)
        self.assertAlmostEqual(row["sub_sharpe_oos"], 0.2)
        self.assertEqual(row["windows"], "[5]")
        self.assertEqual(row["is_range"], "2000-01-03 .. 2020-12-31")

    def test_old_ic_alias_is_backfilled(self):
        attempt = json.loads(json.dumps(ATTEMPT))
        attempt["grid"]["best"].pop("rank_ic")
        attempt["grid"]["best"]["ic"] = 0.02
        attempt["grid"]["out_of_sample"].pop("rank_ic")
        attempt["grid"]["out_of_sample"]["ic"] = 0.008
        row = flatten_attempt("20260101-010101-test", attempt)
        self.assertAlmostEqual(row["rank_ic_full"], 0.02)
        self.assertAlmostEqual(row["rank_ic_oos"], 0.008)

    def test_rebuild_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "runs" / "20260101-010101-test"
            run_dir.mkdir(parents=True)
            (run_dir / "run.json").write_text(
                json.dumps({"llm": "openai-compatible", "attempts": [ATTEMPT]}), encoding="utf-8"
            )
            (run_dir / "panel_summary.json").write_text(
                json.dumps({"name": "panel", "n_dates": 100, "n_tickers": 10}), encoding="utf-8"
            )
            out = Path(tmp) / "ledger.csv"
            df = rebuild_ledger(runs_dir=Path(tmp) / "runs", out=out)
            self.assertEqual(len(df), 1)
            self.assertEqual(list(df.columns), list(LEDGER_COLUMNS))
            self.assertEqual(df.iloc[0]["llm"], "openai-compatible")
            self.assertTrue(out.exists())

            audit = out.parent / 'batch10' / 'verification.json'
            audit.parent.mkdir()
            audit.write_text(json.dumps([{'run_id': '20260101-010101-test',
                                          'hypothesis': 'h1',
                                          'verification_status': 'invalid_constant_signal'}]), encoding='utf-8')
            checked = rebuild_ledger(runs_dir=Path(tmp) / 'runs', out=out)
            self.assertEqual(checked.iloc[0]['verification_status'], 'invalid_constant_signal')
            loaded = load_ledger(out)
            self.assertEqual(len(loaded), 1)
            self.assertAlmostEqual(float(loaded.iloc[0]["sharpe_is"]), 1.2)

    def test_empty_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            df = rebuild_ledger(runs_dir=Path(tmp) / "runs", out=Path(tmp) / "ledger.csv")
            self.assertEqual(len(df), 0)
            self.assertIn("sharpe_oos", df.columns)


if __name__ == "__main__":
    unittest.main()

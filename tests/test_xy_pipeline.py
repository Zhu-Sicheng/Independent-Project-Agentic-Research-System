"""Merged pipeline: translation, in-sample isolation, display and feedback."""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from factorlab.data.panel import PanelStore
from factorlab.expr.validate import validate_expression
from factorlab.xy_pipeline import (
    FIELD_MAP,
    display_evaluation,
    hypothesis_from_idea,
    split_is_panel,
    translate_expression,
    write_feedback,
)


def make_panel(days: int = 2000, names: int = 30, seed: int = 5) -> PanelStore:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2019-01-01", periods=days)
    cols = [f"S{i:02d}" for i in range(names)]
    close = pd.DataFrame(
        20 * np.exp(np.cumsum(rng.normal(0, 0.01, (days, names)), axis=0)),
        index=dates,
        columns=cols,
    )
    volume = pd.DataFrame(rng.lognormal(12, 0.3, (days, names)), index=dates, columns=cols)
    cap = pd.DataFrame(np.tile(np.linspace(1e8, 1e10, names), (days, 1)), index=dates, columns=cols)
    return PanelStore.from_dict(
        {
            "open": close * 0.999,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": volume,
            "amount": close * volume,
            "cap": cap,
        }
    )


class TestTranslation(unittest.TestCase):
    def test_contract_fields_map_to_panel_fields(self):
        cases = {
            "-ts_returns(Adj_Close, 5)": "-ts_returns(close, 5)",
            "ts_returns(Adj_Close, 5) * (Adj_Volume / ts_mean(Adj_Volume, 20))":
                "ts_returns(close, 5) * (volume / ts_mean(volume, 20))",
            "-(Adj_High - Adj_Low) / Adj_Close": "-(high - low) / close",
            "-Adj_MktCap": "-cap",
            "-ts_zscore(Adj_Close, 20)": "-ts_zscore(close, 20)",
        }
        for raw, expected in cases.items():
            self.assertEqual(translate_expression(raw), expected)

    def test_field_call_syntax(self):
        self.assertEqual(translate_expression('field("Adj_Close")'), "close")

    def test_operator_names_are_untouched(self):
        expr = "ts_quantile(Adj_Close, 20, \"uniform\")"
        self.assertEqual(translate_expression(expr), 'ts_quantile(close, 20, "uniform")')

    def test_every_panel_field_has_an_identity_mapping(self):
        for name in ("returns", "log_returns", "amount", "adv20", "cap_rank",
                     "range", "close_position", "intraday_return", "overnight_return"):
            self.assertEqual(FIELD_MAP[name], name)


class TestWindows(unittest.TestCase):
    def test_agent_lookbacks_are_accepted(self):
        # Agent 3 budgets allow 1..252; our grid horizons are stricter, so the
        # merged pipeline validates with min_window=1 and no whitelist.
        report = validate_expression("-ts_std_dev(ts_returns(close, 1), 20)", strict_windows=False, min_window=1)
        self.assertTrue(report.ok, report.errors)
        self.assertEqual(report.windows, (20, 1))  # outer window first (pre-order)

    def test_default_validation_still_rejects_lookback_one(self):
        report = validate_expression("ts_returns(close, 1)")
        self.assertFalse(report.ok)


class TestIsolation(unittest.TestCase):
    def test_is_panel_is_cut_at_research_end(self):
        panel = make_panel()
        is_panel = split_is_panel(panel, "2020-12-31")
        self.assertLessEqual(is_panel.dates.max(), pd.Timestamp("2020-12-31"))
        self.assertGreater(panel.dates.max(), pd.Timestamp("2020-12-31"))

    def test_display_layer_is_the_only_place_with_oos(self):
        panel = make_panel()
        record = {
            "expression_id": "expr_demo",
            "expression": "-rank(ts_mean(close, 20))",
            "status": "evaluated",
            "decision": "accept",
            "is": {"metrics": {"sharpe": 1.0}, "config": {"decay": 0, "transform": "rank", "cap_filter": None, "windows": [20]}},
        }
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            updated = display_evaluation(panel, [record], "test", Path(tmp), verbose=False)
        self.assertIn("display", updated[0])
        segments = updated[0]["display"]["segments"]
        self.assertIn("is", segments)
        self.assertIn("oos", segments)
        self.assertIn("holdout", segments)
        self.assertIn("oos_sharpe", updated[0]["display"])

    def test_feedback_records_are_visible_to_the_agents(self):
        import sys

        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "factorlab" / "agents"))
        from research.memory import ResearchMemory

        records = [
            {
                "status": "evaluated",
                "round": 0,
                "expression_id": "expr_demo",
                "expression": "-ts_returns(close, 5)",
                "idea_id": "idea_x",
                "decision": "optimize",
                "reasoning": "turnover too high",
                "suggested_changes": ["smooth"],
                "is": {"metrics": {"sharpe": 0.8, "turnover": 40.0}},
                "stability_is": {"flags": ["window_span_crosses_zero"]},
                "_dataset_id": "ds_market",
                "_family": "short_term_reversal",
            }
        ]
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            db = Path(tmp) / "memory.sqlite3"
            written = write_feedback(db, records, "run_x", "2020-12-31")
            self.assertEqual(written, 1)
            memory = ResearchMemory(db)
            try:
                snapshot = memory.snapshot("2020-12-31", "2030-01-01T00:00:00+00:00", 10)
            finally:
                memory.close()
            payloads = [record["payload"] for record in snapshot.records]
            self.assertTrue(any(p.get("expression") == "-ts_returns(close, 5)" for p in payloads))
            feedback = next(p for p in payloads if p.get("expression"))
            self.assertNotIn("out_of_sample", json.dumps(feedback).lower())


class TestHypothesis(unittest.TestCase):
    def test_idea_becomes_reviewer_hypothesis(self):
        idea = {
            "title": "短期反转",
            "family": "short_term_reversal",
            "mechanism": "temporary pressure",
            "signal_concept": "recent overextension",
            "expected_return_direction": "negative",
            "forecast_horizon_days": 5,
        }
        hypothesis = hypothesis_from_idea(idea)
        self.assertEqual(hypothesis["name"], "短期反转")
        self.assertEqual(hypothesis["family"], "short_term_reversal")
        self.assertEqual(hypothesis["expected_sign"], "negative")
        self.assertEqual(hypothesis["source"], "xy_agent2")


if __name__ == "__main__":
    unittest.main()

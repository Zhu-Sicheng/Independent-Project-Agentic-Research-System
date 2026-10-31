"""Merged pipeline: contract->panel translation and reviewer wiring."""

import unittest

from factorlab.expr.validate import validate_expression
from factorlab.xy_pipeline import (
    FIELD_MAP,
    hypothesis_from_idea,
    translate_expression,
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

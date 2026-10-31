"""Tests for the approved operator set (ts_operators.md)."""

import unittest

import numpy as np
import pandas as pd

from factorlab.data.panel import PanelStore
from factorlab.expr import evaluate_text, validate_expression
from factorlab.expr.approved import (
    APPROVED_OPERATORS,
    TS_OPERATORS,
    catalog_text,
    missing_from_registry,
)
from factorlab.expr.ops import REGISTRY


def make_panel(days: int = 80, names: int = 6, seed: int = 0) -> PanelStore:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=days)
    cols = [f"S{i}" for i in range(names)]
    close = pd.DataFrame(
        20 * np.exp(np.cumsum(rng.normal(0, 0.01, (days, names)), axis=0)),
        index=dates,
        columns=cols,
    )
    volume = pd.DataFrame(
        rng.lognormal(12, 0.3, (days, names)), index=dates, columns=cols
    )
    return PanelStore.from_dict(
        {
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": volume,
            "amount": close * volume,
            "cap": close * 1e6,
        }
    )


class TestApprovedSet(unittest.TestCase):
    def setUp(self):
        self.panel = make_panel()

    def test_every_approved_operator_is_registered(self):
        self.assertEqual(missing_from_registry(), [])
        self.assertEqual(len(TS_OPERATORS), 35)
        for name in APPROVED_OPERATORS:
            self.assertIn(name, REGISTRY)

    def test_legacy_operators_rejected(self):
        for expr in ("ts_std(close, 20)", "ts_corr(close, volume, 20)", "delay(close, 1)"):
            report = validate_expression(expr, self.panel)
            self.assertFalse(report.ok, expr)
            self.assertIn("approved operator set", " ".join(report.errors))

    def test_replacement_hint(self):
        report = validate_expression("ts_std(close, 20)", self.panel)
        self.assertIn("use ts_std_dev", " ".join(report.errors))

    def test_approved_expression_accepted(self):
        report = validate_expression(
            "-rank(ts_std_dev(returns, 20)) + ts_rank(volume, 20)", self.panel
        )
        self.assertTrue(report.ok, report.errors)

    def test_catalog_is_filtered(self):
        text = catalog_text()
        for name in APPROVED_OPERATORS:
            self.assertIn(name, text)
        self.assertNotIn("ts_corr", text)
        self.assertNotIn("ts_std(", text)


class TestApprovedSemantics(unittest.TestCase):
    def setUp(self):
        self.panel = make_panel()

    def test_std_dev_matches_pandas(self):
        out = evaluate_text("ts_std_dev(close, 10)", self.panel)
        ref = self.panel.field("close").rolling(10, min_periods=10).std(ddof=0)
        self.assertLess(float((out - ref).abs().max().max()), 1e-9)

    def test_ts_delta_with_lag_one(self):
        out = evaluate_text("ts_delta(close, 1)", self.panel)
        ref = self.panel.field("close").diff()
        self.assertLess(float((out - ref).abs().max().max()), 1e-9)

    def test_arg_max_is_days_since_max(self):
        dates = pd.bdate_range("2021-01-01", periods=6)
        values = pd.DataFrame(
            {"A": [1.0, 5.0, 3.0, 2.0, 4.0, 0.5]}, index=dates
        )
        panel = PanelStore.from_dict({"close": values})
        out = evaluate_text("ts_arg_max(close, 3)", panel)["A"]
        # window ending 2021-01-06 = [2, 4, 0.5] -> max was 1 day ago
        self.assertEqual(float(out.iloc[-1]), 1.0)

    def test_rank_percentile_and_count(self):
        pct = evaluate_text("ts_rank(close, 10, 1)", self.panel)
        count = evaluate_text("ts_rank(close, 10)", self.panel)
        self.assertGreaterEqual(float(pct.min().min()), 0.0)
        self.assertLessEqual(float(pct.max().max()), 1.0)
        self.assertGreaterEqual(float(count.min().min()), 1.0)
        self.assertLessEqual(float(count.max().max()), 10.0)

    def test_scale_is_bounded(self):
        out = evaluate_text("ts_scale(close, 20)", self.panel)
        self.assertGreaterEqual(float(out.min().min()), -1e-12)
        self.assertLessEqual(float(out.max().max()), 1 + 1e-12)

    def test_quantile_monotone_in_rank(self):
        q = evaluate_text("ts_quantile(close, 20)", self.panel)
        r = evaluate_text("ts_rank(close, 20, 1)", self.panel)
        # gaussian quantile is a monotone map of the percentile rank
        valid = (q.notna() & r.notna()).to_numpy()
        flat_q = pd.Series(q.to_numpy()[valid])
        flat_r = pd.Series(r.to_numpy()[valid])
        self.assertGreater(float(flat_q.corr(flat_r, method="spearman")), 0.999)

    def test_composite_expression(self):
        expr = "-ts_rank(ts_returns(close, 5), 20) * ts_rank(volume / ts_mean(volume, 20), 20)"
        out = evaluate_text(expr, self.panel)
        self.assertEqual(out.shape, self.panel.shape)
        self.assertTrue(out.notna().any().any())


if __name__ == "__main__":
    unittest.main()

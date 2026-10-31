"""Stability battery: compact summary and its effect on the reviewer."""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from factorlab.agents import fallback
from factorlab.data.panel import PanelStore
from factorlab.stability import stability_summary


def make_panel(days: int = 140, names: int = 40, seed: int = 3) -> PanelStore:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=days)
    cols = [f"S{i:02d}" for i in range(names)]
    close = pd.DataFrame(
        20 * np.exp(np.cumsum(rng.normal(0, 0.01, (days, names)), axis=0)),
        index=dates,
        columns=cols,
    )
    volume = pd.DataFrame(rng.lognormal(12, 0.3, (days, names)), index=dates, columns=cols)
    cap = pd.DataFrame(
        np.tile(np.linspace(1e8, 1e10, names), (days, 1)), index=dates, columns=cols
    )
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


def make_attempt() -> dict:
    return {
        "hypothesis": "demo",
        "spec": {"kind": "expression", "expression": "-ts_mean(returns, 5)"},
        "grid": {"best": {"decay": 5, "transform": "rank", "cap_filter": 0.3, "windows": [5]}},
    }


class TestStabilitySummary(unittest.TestCase):
    def test_summary_keys_and_flags(self):
        summary = stability_summary(make_panel(), make_attempt())
        for key in (
            "baseline_sharpe",
            "subuniverse_sharpe",
            "subuniverse_delta",
            "transform_sharpe_span",
            "decay_sharpe_span",
            "window_sharpe_span",
            "min_pnl_corr",
            "max_turnover",
            "n_variants",
            "flags",
        ):
            self.assertIn(key, summary)
        self.assertGreater(summary["n_variants"], 5)
        self.assertIsInstance(summary["flags"], list)
        # the baseline already uses cap_filter=0.3, so the sub-universe book is identical
        self.assertTrue(
            np.isnan(summary["subuniverse_sharpe"])
            or summary["subuniverse_sharpe"] == summary["baseline_sharpe"]
        )


class TestReviewerUsesStability(unittest.TestCase):
    def _summary(self, flags):
        return {
            "in_sample": {
                "sharpe": 1.6,
                "turnover": 10.0,
                "max_drawdown": -0.08,
                "ic": 0.02,
                "yearly": [{"n_days": 250, "total_return": 0.1}] * 3,
            },
            "best": {"sharpe": 1.6, "turnover": 10.0},
            "stability": {
                "subuniverse_sharpe": -0.2,
                "min_pnl_corr": 0.2,
                "flags": flags,
            },
        }

    def test_flags_downgrade_accept(self):
        review = fallback.review(
            {"name": "demo", "expected_sign": "positive"},
            {"kind": "expression", "expression": "-ts_mean(returns, 5)"},
            self._summary(["subuniverse_flips_sign", "variant_pnl_decorrelates"]),
            yearly=[],
            history=[],
            max_rounds=2,
        )
        self.assertEqual(review["decision"], "abandon")

    def test_no_flags_keep_accept(self):
        review = fallback.review(
            {"name": "demo", "expected_sign": "positive"},
            {"kind": "expression", "expression": "-ts_mean(returns, 5)"},
            self._summary([]),
            yearly=[],
            history=[],
            max_rounds=2,
        )
        self.assertEqual(review["decision"], "accept")


if __name__ == "__main__":
    unittest.main()

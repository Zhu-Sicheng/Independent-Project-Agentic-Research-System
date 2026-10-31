"""Stability checks: same signal, different implementation knobs."""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from factorlab.config import BacktestSettings
from factorlab.data.panel import PanelStore
from factorlab.stability import build_variants, run_stability


def make_panel(days: int = 80, names: int = 30, seed: int = 1) -> PanelStore:
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
        "hypothesis": "demo_factor",
        "attempt": 0,
        "spec": {"kind": "expression", "expression": "-ts_mean(returns, 5)"},
        "grid": {"best": {"decay": 5, "transform": "rank", "cap_filter": 0.3, "windows": [5], "params": {}}},
    }


class TestStability(unittest.TestCase):
    def test_baseline_settings_restores_missing_cap(self):
        from factorlab.stability import baseline_settings

        settings = baseline_settings(make_attempt())
        self.assertEqual(settings.cap_filter, 0.3)
        self.assertEqual(settings.decay, 5)
        self.assertTrue(settings.compute_ic)

    def test_variants_cover_every_check(self):
        variants = build_variants(make_panel(), make_attempt())
        groups = {v.group for v in variants}
        for expected in ("original", "subuniverse", "cap", "transform", "decay", "window"):
            self.assertIn(expected, groups)
        names = [v.name for v in variants]
        self.assertEqual(names[0], "original")
        self.assertIn("transform=sign", names)
        self.assertIn("decay=20", names)
        self.assertIn("window[0]=60", names)

    def test_run_stability_writes_artifacts(self):
        panel = make_panel()
        with tempfile.TemporaryDirectory() as tmp:
            out = run_stability(panel, make_attempt(), "20260101-000000-test", Path(tmp) / "stability")
            self.assertTrue((out / "metrics.csv").exists())
            self.assertTrue((out / "pnl.png").exists())
            self.assertTrue((out / "README.md").exists())
            table = pd.read_csv(out / "metrics.csv")
            self.assertGreater(len(table), 5)
            self.assertIn("pnl_corr_with_original", table.columns)
            self.assertIn("original", set(table["variant"]))


if __name__ == "__main__":
    unittest.main()

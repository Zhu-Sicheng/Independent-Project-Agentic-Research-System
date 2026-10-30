"""Tests for the in-sample / out-of-sample split."""

import unittest

import numpy as np
import pandas as pd

from factorlab.backtest.grid import GridSearch
from factorlab.backtest.split import SplitError, resolve_split
from factorlab.config import BacktestSettings, GridConfig, SampleSplit
from factorlab.data.panel import PanelStore


def make_panel(days: int = 400, names: int = 25, half: int = 200) -> PanelStore:
    """The signal only works in the first ``half`` days."""
    rng = np.random.default_rng(11)
    dates = pd.bdate_range("2020-01-01", periods=days)
    tickers = [f"S{i}" for i in range(names)]
    t = np.arange(days)[:, None]
    k = np.arange(names)[None, :]
    signal = np.sin(t / 17.0 + k * 0.7) + 0.2 * np.cos(t / 5.0 - k)

    ret = rng.normal(0, 0.01, size=(days, names))
    aligned = np.roll(signal, 1, axis=0)
    ret[:half] = 0.01 * aligned[:half]
    close = 10 * (1 + ret).cumprod(axis=0)
    volume = np.full((days, names), 1e6)
    cap = close * np.exp(np.linspace(18, 22, names))[None, :]

    return PanelStore.from_dict(
        {
            "close": pd.DataFrame(close, index=dates, columns=tickers),
            "signal": pd.DataFrame(signal, index=dates, columns=tickers),
            "volume": pd.DataFrame(volume, index=dates, columns=tickers),
            "amount": pd.DataFrame(close * volume, index=dates, columns=tickers),
            "cap": pd.DataFrame(cap, index=dates, columns=tickers),
        }
    )


class TestResolveSplit(unittest.TestCase):
    def setUp(self):
        self.panel = make_panel(days=400)

    def test_unconfigured_means_full_sample(self):
        masks = resolve_split(self.panel.dates, None)
        self.assertFalse(masks.has_oos)
        self.assertTrue(bool(masks.masks["is"].all()))
        self.assertEqual(masks.meta["mode"], "none")
        self.assertEqual(masks.meta["n_oos"], 0)

    def test_fraction_split(self):
        masks = resolve_split(self.panel.dates, SampleSplit(train_frac=0.6))
        self.assertTrue(masks.has_oos)
        self.assertEqual(masks.meta["n_is"], 240)
        self.assertEqual(masks.meta["n_oos"], 160)
        is_mask = masks.masks["is"]
        oos_mask = masks.masks["oos"]
        self.assertFalse(bool((is_mask & oos_mask).any()))
        self.assertEqual(int(is_mask.sum() + oos_mask.sum()), 400)
        self.assertEqual(masks.meta["is_range"][1], str(self.panel.dates[239].date()))

    def test_date_split_with_train_end(self):
        masks = resolve_split(self.panel.dates, SampleSplit(train_end="2020-09-30"))
        self.assertTrue(masks.has_oos)
        last_is = pd.Timestamp(masks.meta["is_range"][1])
        first_oos = pd.Timestamp(masks.meta["oos_range"][0])
        self.assertLess(last_is, first_oos)
        self.assertLessEqual(last_is, pd.Timestamp("2020-09-30"))
        self.assertEqual(first_oos, self.panel.dates[self.panel.dates > last_is][0])

    def test_date_split_with_oos_start(self):
        masks = resolve_split(self.panel.dates, SampleSplit(test_start="2021-01-04"))
        self.assertEqual(masks.meta["oos_range"][0], "2021-01-04")

    def test_segments_must_be_long_enough(self):
        with self.assertRaises(SplitError):
            resolve_split(self.panel.dates, SampleSplit(train_frac=0.99))
        with self.assertRaises(SplitError):
            resolve_split(
                self.panel.dates,
                SampleSplit(train_end=str(self.panel.dates[10].date())),
            )

    def test_three_way_split(self):
        masks = resolve_split(
            self.panel.dates,
            SampleSplit(
                train_end="2020-09-30",
                test_start="2020-10-01",
                test_end="2020-12-31",
                holdout_start="2021-01-04",
            ),
        )
        self.assertTrue(masks.has_oos)
        self.assertTrue(masks.has_holdout)
        total = int(
            masks.masks["is"].sum()
            + masks.masks["oos"].sum()
            + masks.masks["holdout"].sum()
        )
        self.assertGreater(total, 395)  # 2021-01-01 is a business day in this calendar
        self.assertFalse(
            bool((masks.masks["oos"] & masks.masks["holdout"]).any()),
        )
        self.assertEqual(masks.meta["holdout_range"][0], "2021-01-04")

    def test_holdout_inside_validation_rejected(self):
        with self.assertRaises(SplitError):
            resolve_split(
                self.panel.dates,
                SampleSplit(
                    train_end="2020-06-30",
                    test_start="2020-07-01",
                    test_end="2021-06-30",
                    holdout_start="2021-01-04",
                ),
            )

    def test_overlap_rejected(self):
        with self.assertRaises(SplitError):
            resolve_split(
                self.panel.dates,
                SampleSplit(train_end="2021-06-30", test_start="2021-01-04"),
            )


class TestSplitAwareGrid(unittest.TestCase):
    def setUp(self):
        self.panel = make_panel()
        self.split = SampleSplit(train_frac=0.5)

    def _grid(self, split=None):
        return GridSearch(
            self.panel,
            GridConfig(max_evals=24, decays=(0,), transforms=("none", "rank")),
            BacktestSettings(min_names=5),
            split=split,
        )

    def test_selection_uses_in_sample_only(self):
        grid = self._grid(self.split).run_expression("signal")
        self.assertTrue(grid.has_oos)
        self.assertIn("sharpe_is", grid.table.columns)
        self.assertIn("sharpe_oos", grid.table.columns)
        # the table is ranked by in-sample performance
        self.assertTrue(grid.table["sharpe_is"].is_monotonic_decreasing)
        # the best in-sample configuration is chosen even if OOS disagrees
        best_is = grid.best.segments["is"]["sharpe"]
        best_oos = grid.best.segments["oos"]["sharpe"]
        self.assertGreater(best_is, 3.0)
        self.assertLess(best_oos, best_is)
        self.assertEqual(grid.split_meta["n_is"], 200)

    def test_grid_reports_holdout(self):
        grid = GridSearch(
            self.panel,
            GridConfig(max_evals=24, decays=(0,), transforms=("none",)),
            BacktestSettings(min_names=5),
            split=SampleSplit(
                train_end="2020-09-30",
                test_start="2020-10-01",
                test_end="2020-12-31",
                holdout_start="2021-01-04",
            ),
        ).run_expression("signal")
        self.assertTrue(grid.has_holdout)
        self.assertIn("sharpe_holdout", grid.table.columns)
        summary = grid.summary()
        self.assertIn("holdout", summary)
        self.assertIn("yearly", summary["holdout"])

    def test_summary_exposes_both_segments(self):
        summary = self._grid(self.split).run_expression("signal").summary()
        self.assertEqual(summary["selection"], "in-sample")
        self.assertIn("in_sample", summary)
        self.assertIn("out_of_sample", summary)
        self.assertGreater(summary["in_sample"]["sharpe"], 3.0)
        self.assertIn("yearly", summary["out_of_sample"])

    def test_without_split_nothing_changes(self):
        grid = self._grid(None).run_expression("signal")
        self.assertFalse(grid.has_oos)
        self.assertNotIn("sharpe_is", grid.table.columns)
        summary = grid.summary()
        self.assertEqual(summary["selection"], "full-sample")
        self.assertNotIn("out_of_sample", summary)


if __name__ == "__main__":
    unittest.main()

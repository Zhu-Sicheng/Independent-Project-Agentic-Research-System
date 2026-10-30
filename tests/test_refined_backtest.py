"""Refined backtest: close-to-close pnl, rank IC and the sub-universe reference."""

import unittest

import numpy as np
import pandas as pd

from factorlab.backtest.engine import (
    BacktestResult,
    run_backtest,
    run_backtest_with_subuniverse,
    subuniverse_mask,
)
from factorlab.backtest.grid import GridSearch
from factorlab.config import BacktestSettings, GridConfig
from factorlab.data.panel import PanelStore


def make_panel(days: int = 60, names: int = 30, seed: int = 3) -> PanelStore:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=days)
    cols = [f"S{i:02d}" for i in range(names)]
    close = pd.DataFrame(
        20 * np.exp(np.cumsum(rng.normal(0, 0.01, (days, names)), axis=0)),
        index=dates,
        columns=cols,
    )
    volume = pd.DataFrame(
        rng.lognormal(12, 0.3, (days, names)), index=dates, columns=cols
    )
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


class TestCloseToClose(unittest.TestCase):
    def test_pnl_is_previous_weight_times_close_return(self):
        panel = make_panel(days=8, names=4)
        factor = pd.DataFrame(1.0, index=panel.dates, columns=panel.tickers)
        settings = BacktestSettings(
            delay=1,
            decay=0,
            transform="none",
            cap_filter=None,
            neutralize=False,
            cost_bps=0.0,
            min_names=2,
            compute_ic=False,
            subuniverse=None,
        )
        result = run_backtest(factor, panel, settings)

        close = panel.field("close")
        ret = close.pct_change(fill_method=None)
        weights = 0.25  # equal weight, gross = 1
        expected = (ret * weights).sum(axis=1)

        pd.testing.assert_index_equal(result.pnl.index, ret.index)
        self.assertTrue(np.isnan(result.pnl.iloc[0]))
        np.testing.assert_allclose(
            result.pnl.iloc[1:].to_numpy(), expected.iloc[1:].to_numpy(), atol=1e-12
        )


class TestInformationCoefficient(unittest.TestCase):
    def setUp(self):
        self.panel = make_panel(days=40, names=40)
        rng = np.random.default_rng(11)
        self.factor = pd.DataFrame(
            rng.normal(size=(40, 40)), index=self.panel.dates, columns=self.panel.tickers
        )
        self.settings = BacktestSettings(
            transform="none", cap_filter=None, compute_ic=True, min_names=5,
            subuniverse=None,
        )
        self.result = run_backtest(self.factor, self.panel, self.settings)

    def test_rank_ic_is_daily_spearman(self):
        fwd = self.panel.field("returns").shift(-1)
        day = self.panel.dates[20]
        expected = self.factor.loc[day].corr(fwd.loc[day], method="spearman")
        self.assertAlmostEqual(float(self.result.ic.loc[day]), float(expected), places=10)
        self.assertAlmostEqual(
            float(self.result.metrics["rank_ic"]),
            float(self.result.ic.dropna().mean()),
            places=12,
        )

    def test_pearson_ic_is_daily_pearson(self):
        fwd = self.panel.field("returns").shift(-1)
        day = self.panel.dates[20]
        expected = self.factor.loc[day].corr(fwd.loc[day], method="pearson")
        self.assertIsNotNone(self.result.pearson_ic)
        self.assertAlmostEqual(
            float(self.result.pearson_ic.loc[day]), float(expected), places=10
        )
        self.assertIn("pearson_ic", self.result.metrics)

    def test_rank_ic_alias_kept_for_compatibility(self):
        self.assertEqual(self.result.metrics["ic"], self.result.metrics["rank_ic"])
        self.assertEqual(self.result.metrics["ic_ir"], self.result.metrics["rank_ic_ir"])


class TestSubUniverse(unittest.TestCase):
    def setUp(self):
        self.panel = make_panel(days=50, names=20)
        rng = np.random.default_rng(5)
        self.factor = pd.DataFrame(
            rng.normal(size=(50, 20)), index=self.panel.dates, columns=self.panel.tickers
        )

    def test_mask_drops_smallest_names(self):
        mask = subuniverse_mask(self.panel, 0.3)
        self.assertEqual(mask.shape, self.panel.shape)
        # 20 names, cap rank > 0.3 keeps the largest 14
        self.assertEqual(int(mask.iloc[0].sum()), 14)
        small = self.panel.field("cap").iloc[0].nsmallest(6).index
        self.assertFalse(mask.iloc[0][small].any())

    def test_subuniverse_backtest_has_fewer_names(self):
        settings = BacktestSettings(
            transform="rank", cap_filter=None, min_names=5, subuniverse=0.3
        )
        main = run_backtest_with_subuniverse(self.factor, self.panel, settings)
        self.assertIsNotNone(main.subuniverse)
        self.assertAlmostEqual(main.subuniverse.threshold, 0.3)
        self.assertLess(
            main.subuniverse.metrics["n_names"], main.metrics["n_names"]
        )
        self.assertNotEqual(
            float(main.subuniverse.pnl.dropna().iloc[-1]),
            float(main.pnl.dropna().iloc[-1]),
        )

    def test_subuniverse_can_be_disabled(self):
        settings = BacktestSettings(subuniverse=None)
        main = run_backtest_with_subuniverse(self.factor, self.panel, settings)
        self.assertIsNone(main.subuniverse)
        disabled = run_backtest_with_subuniverse(
            self.factor, self.panel, BacktestSettings(subuniverse=0.3, compute_subuniverse=False)
        )
        self.assertIsNone(disabled.subuniverse)

    def test_grid_reports_subuniverse(self):
        grid = GridSearch(
            self.panel,
            GridConfig(decays=(0,), transforms=("rank",), cap_filters=(None,), max_evals=2),
            BacktestSettings(min_names=5, subuniverse=0.3),
        ).run_matrix(self.factor)
        summary = grid.summary()
        self.assertIn("subuniverse", summary)
        self.assertIn("sub_sharpe", summary["best"])
        self.assertIn("sharpe", summary["subuniverse"]["metrics"])
        self.assertGreater(summary["subuniverse"]["threshold"], 0)


if __name__ == "__main__":
    unittest.main()

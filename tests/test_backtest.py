"""Tests for the backtest engine and the grid search."""

import unittest

import numpy as np
import pandas as pd

from factorlab.backtest import metrics as M
from factorlab.backtest.engine import run_backtest
from factorlab.backtest.grid import GridSearch
from factorlab.config import BacktestSettings, GridConfig
from factorlab.data.panel import PanelStore


def make_predictable_panel(days: int = 260, names: int = 25, signal: float = 0.01):
    """Future return is a deterministic function of the *current* factor."""
    dates = pd.bdate_range("2020-01-01", periods=days)
    tickers = [f"S{i}" for i in range(names)]
    t = np.arange(days)[:, None]
    k = np.arange(names)[None, :]
    values = np.sin(t / 17.0 + k * 0.7) + 0.2 * np.cos(t / 5.0 - k)
    factor = pd.DataFrame(values, index=dates, columns=tickers)
    ret = signal * factor.shift(1)
    close = 10 * (1 + ret.fillna(0)).cumprod()
    volume = pd.DataFrame(1e6, index=dates, columns=tickers)
    cap = pd.DataFrame(
        np.tile(np.exp(np.linspace(18, 22, names)), (days, 1)), index=dates, columns=tickers
    )
    return (
        PanelStore.from_dict(
            {"close": close, "volume": volume, "amount": close * volume, "cap": cap}
        ),
        factor,
    )


class TestBacktest(unittest.TestCase):
    def test_known_alpha_is_profitable(self):
        panel, factor = make_predictable_panel()
        result = run_backtest(factor, panel, BacktestSettings(transform="none"))
        self.assertGreater(result.metrics["sharpe"], 5.0)
        self.assertGreater(result.metrics["ann_return"], 0.1)
        self.assertGreater(result.metrics["ic"], 0.9)

    def test_opposite_factor_loses(self):
        panel, factor = make_predictable_panel()
        result = run_backtest(-factor, panel, BacktestSettings())
        self.assertLess(result.metrics["sharpe"], -5.0)

    def test_weights_are_dollar_neutral_and_unit_gross(self):
        panel, factor = make_predictable_panel()
        result = run_backtest(
            factor, panel, BacktestSettings(keep_positions=True)
        )
        w = result.positions.dropna()
        self.assertTrue(np.allclose(w.sum(axis=1), 0.0, atol=1e-9))
        self.assertTrue(np.allclose(w.abs().sum(axis=1), 1.0, atol=1e-9))

    def test_no_lookahead_delay(self):
        """With delay=1 only yesterday's factor may predict today's return."""
        rng = np.random.default_rng(3)
        dates = pd.bdate_range("2020-01-01", periods=500)
        tickers = [f"S{i}" for i in range(25)]
        ret = pd.DataFrame(
            rng.normal(0, 0.01, size=(len(dates), len(tickers))),
            index=dates,
            columns=tickers,
        )
        close = 10 * (1 + ret).cumprod()
        panel = PanelStore.from_dict(
            {
                "close": close,
                "volume": pd.DataFrame(1e6, index=dates, columns=tickers),
                "cap": pd.DataFrame(
                    np.tile(np.exp(np.linspace(18, 22, len(tickers))), (len(dates), 1)),
                    index=dates,
                    columns=tickers,
                ),
            }
        )
        # the factor is *today's* return: it must not earn tomorrow's move
        result = run_backtest(ret, panel, BacktestSettings(transform="none"))
        self.assertLess(abs(result.metrics["sharpe"]), 2.0)
        self.assertLess(abs(result.metrics["ic"]), 0.05)

    def test_yearly_table(self):
        panel, factor = make_predictable_panel()
        result = run_backtest(factor, panel, BacktestSettings())
        self.assertIn("total_return", result.yearly.columns)
        self.assertEqual(int(result.yearly["n_days"].sum()), 259)

    def test_cap_filter_removes_small_names(self):
        panel, factor = make_predictable_panel()
        result = run_backtest(
            factor,
            panel,
            BacktestSettings(cap_filter=0.3, transform="none", min_names=5),
        )
        self.assertLess(result.metrics["factor_coverage"], 0.8)
        self.assertLess(result.metrics["n_names"], 20)


class TestPnlMode(unittest.TestCase):
    def test_additive_is_the_default(self):
        net = pd.Series([0.01, -0.02, 0.03, -0.01, 0.005])
        turnover = pd.Series(1.0, index=net.index)
        metrics = M.summarise_pnl(net, turnover)
        self.assertEqual(metrics["pnl_mode"], "additive")
        self.assertAlmostEqual(metrics["total_return"], float(net.sum()))
        self.assertAlmostEqual(metrics["ann_return"], float(net.sum() * 252 / len(net)))
        wealth = (1.0 + net.cumsum()).clip(lower=0.0)
        self.assertAlmostEqual(metrics["max_drawdown"], float((wealth / wealth.cummax() - 1).min()))

    def test_compound_mode_reproduces_wealth_curve(self):
        net = pd.Series([0.01, -0.02, 0.03, -0.01, 0.005])
        turnover = pd.Series(1.0, index=net.index)
        metrics = M.summarise_pnl(net, turnover, mode="compound")
        expected = float((1.0 + net).cumprod().iloc[-1] - 1.0)
        self.assertAlmostEqual(metrics["total_return"], expected)

    def test_sharpe_is_identical_across_pnl_modes(self):
        net = pd.Series([0.01, -0.02, 0.03, -0.01, 0.005, 0.002])
        turnover = pd.Series(1.0, index=net.index)
        additive = M.summarise_pnl(net, turnover, mode="additive")
        compound = M.summarise_pnl(net, turnover, mode="compound")
        self.assertAlmostEqual(additive["sharpe"], compound["sharpe"])


class TestGrid(unittest.TestCase):
    def test_grid_covers_settings_and_ranks(self):
        panel, factor = make_predictable_panel(days=200)
        grid = GridSearch(
            panel, GridConfig(max_evals=60, decays=(0, 20), transforms=("none", "rank")),
            BacktestSettings(min_names=5),
        ).run_expression("ts_mean(close / delay(close, 1) - 1, 5)")
        self.assertGreater(grid.n_evals, 0)
        self.assertIn("windows", grid.table.columns)
        self.assertTrue(grid.table["sharpe"].is_monotonic_decreasing)
        self.assertIsNotNone(grid.best_factor)

    def test_window_substitution_picks_allowed_windows(self):
        panel, _ = make_predictable_panel(days=200)
        grid = GridSearch(
            panel, GridConfig(max_evals=40, decays=(0,), transforms=("none",)), BacktestSettings()
        ).run_expression("ts_mean(close, 5)")
        windows = {int(w[0]) for w in grid.table["windows"]}
        self.assertTrue(windows.issubset({5, 20, 60, 120, 240}))
        self.assertIn(5, windows)


if __name__ == "__main__":
    unittest.main()

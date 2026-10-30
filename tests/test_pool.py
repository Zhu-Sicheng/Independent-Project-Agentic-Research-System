"""Tests for the factor pool and an end-to-end mining loop."""

import json
import shutil
import uuid
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from factorlab.backtest.grid import GridSearch
from factorlab.config import (
    BacktestSettings,
    GridConfig,
    MiningConfig,
    SampleSplit,
)
from factorlab.data.panel import PanelStore
from factorlab.expr.script import run_script
from factorlab.expr.spec import FactorSpec
from factorlab.orchestrator import MiningLoop
from factorlab.pool.pool import FactorPool

TMP_ROOT = Path(__file__).resolve().parent / "_tmp"


def new_tmp(prefix: str) -> Path:
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TMP_ROOT / f"{prefix}{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True)
    return path


def make_panel(days: int = 400, names: int = 60, seed: int = 5) -> PanelStore:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2021-01-01", periods=days)
    tickers = [f"S{i:03d}" for i in range(names)]
    ret = rng.normal(0, 0.012, size=(days, names))
    # a weak reversal signal so a good factor exists
    for t in range(2, days):
        ret[t] += -0.15 * ret[t - 1]
    close = 20 * (1 + ret).cumprod(axis=0)
    volume = rng.lognormal(13, 0.5, size=(days, names))
    cap = close * np.exp(np.linspace(18, 22, names))[None, :]
    return PanelStore.from_dict(
        {
            "close": pd.DataFrame(close, index=dates, columns=tickers),
            "volume": pd.DataFrame(volume, index=dates, columns=tickers),
            "amount": pd.DataFrame(close * volume, index=dates, columns=tickers),
            "cap": pd.DataFrame(cap, index=dates, columns=tickers),
        }
    )


def make_grid(panel: PanelStore, expression: str):
    return GridSearch(
        panel,
        GridConfig(max_evals=30, decays=(0, 20), transforms=("none", "rank")),
        BacktestSettings(min_names=10),
    ).run_expression(expression)


class TestFactorPool(unittest.TestCase):
    def setUp(self):
        self.tmp = new_tmp("pool_")
        self.panel = make_panel()
        self.pool = FactorPool(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _add(self, name: str, expr: str):
        spec = FactorSpec(expression=expr, name=name)
        grid = make_grid(self.panel, expr)
        return self.pool.add(
            spec, {"name": name, "hypothesis": f"test {name}"}, grid, run_id="test"
        )

    def test_add_and_reload(self):
        rec = self._add("rev5", "-ts_mean(returns, 5)")
        self.assertTrue((self.tmp / "factors" / rec.id / "factor.parquet").exists())
        self.assertTrue((self.tmp / "factors" / rec.id / "pnl.parquet").exists())

        reloaded = FactorPool(self.tmp)
        self.assertEqual(len(reloaded), 1)
        self.assertEqual(reloaded.records()[0].name, "rev5")
        factor = reloaded.load_factor(rec.id)
        self.assertEqual(factor.shape, self.panel.shape)
        self.assertFalse(reloaded.summary().empty)

    def test_correlation_is_computed_and_stored(self):
        a = self._add("rev5", "-ts_mean(returns, 5)")
        b = self._add("rev20", "-ts_mean(returns, 20)")
        self.assertTrue(a.corr_vs_pool)
        pair = b.corr_vs_pool[0]
        self.assertIn("xs_spearman_mean", pair)
        self.assertGreater(abs(pair["xs_spearman_mean"]), 0.3)
        corr = self.pool.correlations()
        self.assertEqual(len(corr), 1)
        self.assertGreater(abs(float(corr.iloc[0]["pnl_pearson"])), 0.3)

    def test_recompute_and_summary(self):
        self._add("rev5", "-ts_mean(returns, 5)")
        self._add("vol", "-ts_std(returns, 20)")
        df = self.pool.recompute_correlations()
        self.assertEqual(len(df), 1)
        summary = self.pool.summary()
        self.assertEqual(len(summary), 2)
        self.assertTrue((self.tmp / "index.json").exists())
        self.assertIn("Factor pool", self.pool.report())

    def test_segments_are_stored_when_split_configured(self):
        spec = FactorSpec(expression="-ts_mean(returns, 5)", name="rev5")
        grid = GridSearch(
            self.panel,
            GridConfig(max_evals=24, decays=(0, 20), transforms=("none", "rank")),
            BacktestSettings(min_names=10),
            split=SampleSplit(train_frac=0.6),
        ).run_expression(spec.expression)
        rec = self.pool.add(
            spec, {"name": "rev5", "hypothesis": "test"}, grid, run_id="test"
        )
        self.assertIn("is", rec.segments)
        self.assertIn("oos", rec.segments)
        summary = self.pool.summary()
        self.assertIn("sharpe_is", summary.columns)
        self.assertIn("sharpe_oos", summary.columns)
        reloaded = FactorPool(self.tmp)
        self.assertIn("oos", reloaded.records()[0].segments)

    def test_same_factor_twice_does_not_duplicate_correlations(self):
        self._add("rev5", "-ts_mean(returns, 5)")
        self._add("rev5", "-ts_mean(returns, 5)")
        self.assertEqual(len(self.pool), 1)
        self.assertTrue(self.pool.correlations().empty)


class TestScriptFactor(unittest.TestCase):
    def test_script_factor_can_be_pooled(self):
        panel = make_panel()
        code = (
            "def generate(panel, params):\n"
            "    w = int(params['window'])\n"
            "    rel = panel.field('volume') / panel.field('volume').rolling(20).mean()\n"
            "    return -(panel.field('returns') * rel).rolling(w).sum()\n"
        )
        spec = FactorSpec(
            kind="script", script=code, params={"window": 5}, param_grid={"window": [5, 20]}
        )
        grid = GridSearch(
            panel, GridConfig(max_evals=20, decays=(0,), transforms=("rank",)),
            BacktestSettings(min_names=10),
        ).run_spec(spec)
        self.assertGreater(grid.n_evals, 0)
        out = run_script(code, panel, {"window": 5})
        self.assertEqual(out.shape, panel.shape)


class TestEndToEnd(unittest.TestCase):
    def test_offline_loop_runs_and_writes_report(self):
        tmp = new_tmp("e2e_")
        try:
            panel = make_panel(days=350, names=50)
            config = MiningConfig(
                n_hypotheses=1,
                max_rounds=1,
                grid=GridConfig(max_evals=24),
                split=SampleSplit(train_frac=0.7),
            )
            config.llm.provider = "offline"
            config.llm.model = ""
            config.llm.base_url = ""
            config.llm.api_key_env = ""
            loop = MiningLoop(
                panel,
                FactorPool(tmp / "pool"),
                config,
                out_dir=tmp / "runs",
                verbose=False,
            )
            result = loop.run()
            report = (Path(result["run_dir"]) / "report.md").read_text(encoding="utf-8")
            self.assertTrue(report)
            self.assertIn("out-of-sample", report)
            self.assertTrue((Path(result["run_dir"]) / "report.md").exists())
            self.assertTrue((Path(result["run_dir"]) / "attempts.jsonl").exists())
            self.assertGreaterEqual(result["n_factors_added"], 1)
            payload = json.loads(
                (Path(result["run_dir"]) / "run.json").read_text(encoding="utf-8")
            )
            self.assertIn("attempts", payload)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

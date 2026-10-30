"""Tests for the expression language."""

import unittest

import numpy as np
import pandas as pd

from factorlab.data.panel import PanelStore
from factorlab.expr import parser as P
from factorlab.expr.evaluator import EvalError, evaluate, evaluate_text
from factorlab.expr.script import ScriptError, run_script, validate_script
from factorlab.expr.spec import FactorSpec
from factorlab.expr.validate import validate_expression


def make_panel(days: int = 60, names: int = 8, seed: int = 0) -> PanelStore:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2021-01-01", periods=days)
    tickers = [f"S{i}" for i in range(names)]
    close = pd.DataFrame(
        10 * np.exp(np.cumsum(rng.normal(0, 0.01, size=(days, names)), axis=0)),
        index=dates,
        columns=tickers,
    )
    volume = pd.DataFrame(
        rng.lognormal(12, 0.5, size=(days, names)), index=dates, columns=tickers
    )
    cap = close * rng.lognormal(18, 0.5, size=(names,))
    return PanelStore.from_dict(
        {"close": close, "volume": volume, "amount": close * volume, "cap": cap}
    )


class TestParser(unittest.TestCase):
    def test_precedence_and_printing(self):
        ast = P.parse("1 + 2 * 3")
        self.assertEqual(P.to_string(ast), "(1 + (2 * 3))")
        self.assertEqual(P.to_string(P.parse("-(a + b)")), "-(a + b)")

    def test_call_arguments(self):
        ast = P.parse("if_else(rank(cap) > 0.3, -ts_mean(returns, 5), nan)")
        self.assertIsInstance(ast, P.Call)
        self.assertEqual(ast.name, "if_else")
        self.assertEqual(len(ast.args), 3)

    def test_errors(self):
        with self.assertRaises(P.ExpressionError):
            P.parse("ts_mean(close, 5")
        with self.assertRaises(P.ExpressionError):
            P.parse("a > b > c")
        with self.assertRaises(P.ExpressionError):
            P.parse("")

    def test_window_collection_and_substitution(self):
        ast = P.parse("ts_mean(close, 5) + ts_std(returns, 20)")
        self.assertEqual(P.collect_windows(ast), [5, 20])
        new = P.substitute_windows(ast, [60, 120])
        self.assertEqual(P.collect_windows(new), [60, 120])
        self.assertIn("ts_mean(close, 60)", P.to_string(new))


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.panel = make_panel()

    def test_rank_is_cross_sectional(self):
        out = evaluate_text("rank(cap)", self.panel)
        self.assertEqual(out.shape, self.panel.shape)
        n = self.panel.shape[1]
        self.assertTrue(np.allclose(out.max(axis=1).dropna(), 1.0))
        self.assertTrue(np.allclose(out.min(axis=1).dropna(), 1.0 / n))
        self.assertTrue(out.min().min() > 0)
        self.assertTrue(out.max().max() <= 1.0)

    def test_decay_linear_equals_weighted_average(self):
        x = self.panel.field("close")
        out = evaluate_text("ts_decay_linear(close, 5)", self.panel)
        d = 5
        weights = np.arange(d, 0, -1, dtype=float)
        manual = sum(x.shift(i) * weights[i] for i in range(d)) / weights.sum()
        valid = x.notna().rolling(d).sum() >= 3
        diff = (out - manual)[valid]
        self.assertLess(float(np.nanmax(np.abs(diff).to_numpy())), 1e-8)

    def test_if_else_masks(self):
        out = evaluate_text("if_else(rank(cap) > 0.3, 1, nan)", self.panel)
        self.assertTrue(out.isna().sum().sum() > 0)
        self.assertTrue((out.dropna() == 1).all().all())

    def test_unknown_field(self):
        with self.assertRaises(EvalError):
            evaluate_text("rank(not_a_field)", self.panel)

    def test_division_by_zero_is_nan(self):
        with self.assertRaises(EvalError):
            evaluate_text("1 / (close - close)", self.panel)
        out = evaluate_text("if_else(rank(cap) > 0.5, 1 / (close - close), 0)", self.panel)
        self.assertTrue((out.dropna() == 0).all().all())


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.panel = make_panel()

    def test_non_economic_window_rejected(self):
        report = validate_expression("ts_mean(close, 7)", self.panel)
        self.assertFalse(report.ok)
        self.assertIn("not an accepted horizon", " ".join(report.errors))

    def test_allowed_window_accepted(self):
        report = validate_expression("rank(ts_mean(close, 60))", self.panel)
        self.assertTrue(report.ok, report.errors)

    def test_unknown_operator(self):
        report = validate_expression("magic(close)", self.panel)
        self.assertFalse(report.ok)

    def test_script_rejects_imports(self):
        errors = validate_script("import os\ndef generate(panel, params):\n    return None\n")
        self.assertTrue(any("import" in e for e in errors))

    def test_script_rejects_dunder(self):
        errors = validate_script(
            "def generate(panel, params):\n    return panel.__class__\n"
        )
        self.assertTrue(errors)

    def test_script_runs(self):
        code = (
            "def generate(panel, params):\n"
            "    window = int(params.get('window', 5))\n"
            "    return -panel.field('close').pct_change(window)\n"
        )
        out = run_script(code, self.panel, {"window": 5})
        self.assertEqual(out.shape, self.panel.shape)
        self.assertTrue(out.notna().any().any())

    def test_script_rejects_non_dataframe(self):
        code = "def generate(panel, params):\n    return 1\n"
        with self.assertRaises(ScriptError):
            run_script(code, self.panel)


class TestSpec(unittest.TestCase):
    def test_roundtrip_and_fingerprint(self):
        spec = FactorSpec(expression="-rank(ts_mean(returns, 5))")
        data = spec.to_dict()
        again = FactorSpec.from_dict(data)
        self.assertEqual(spec.fingerprint(), again.fingerprint())
        self.assertEqual(spec.windows, [5])

    def test_invalid_spec(self):
        with self.assertRaises(Exception):
            FactorSpec.from_dict({"kind": "expression", "expression": ""})


if __name__ == "__main__":
    unittest.main()

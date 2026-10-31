"""Reference alignment of the approved operators with ``ts_operators.md``.

The overlapping time-series operators follow the reference implementation in
``docs/ts_operators.md``; operators we added ourselves keep our semantics.
"""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from factorlab.data.panel import PanelStore
from factorlab.expr import evaluate_text
from factorlab.expr.catalog import build_catalog, fingerprint, write_catalog
from factorlab.expr.ops import REGISTRY
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "factorlab" / "agents"))


def make_panel(days: int = 60, names: int = 3, seed: int = 2) -> PanelStore:
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


class TestReferenceAlignment(unittest.TestCase):
    """The overlapping operators must match docs/ts_operators.md."""

    def setUp(self):
        self.panel = make_panel()
        self.close = self.panel.field("close")

    def test_simple_reductions_require_a_full_window(self):
        cases = {
            "ts_mean": "mean",
            "ts_sum": "sum",
            "ts_min": "min",
            "ts_max": "max",
            "ts_median": "median",
        }
        for operator, method in cases.items():
            out = evaluate_text(f"{operator}(close, 10)", self.panel)
            ref = getattr(self.close.rolling(10, min_periods=10), method)()
            self.assertLess(
                float((out - ref).abs().max().max()), 1e-9, operator
            )
            # the vetted registry is deliberately stricter than the source doc:
            # partial warm-up windows stay missing
            self.assertTrue(pd.isna(out.iloc[0]).all(), operator)
            self.assertTrue(pd.isna(out.iloc[8]).all(), operator)
            self.assertTrue(pd.notna(out.iloc[9]).all(), operator)

    def test_std_dev_is_ddof_zero_full_window(self):
        out = evaluate_text("ts_std_dev(close, 10)", self.panel)
        ref = self.close.rolling(10, min_periods=10).std(ddof=0)
        self.assertLess(float((out - ref).abs().max().max()), 1e-9)
        self.assertTrue(pd.isna(out.iloc[8]).all())
        self.assertTrue(pd.notna(out.iloc[9]).all())

    def test_ir_is_nan_for_zero_dispersion(self):
        flat = pd.DataFrame(
            {"A": np.full(8, 5.0)}, index=pd.bdate_range("2021-01-01", periods=8)
        )
        panel = PanelStore.from_dict({"close": flat})
        # evaluate_text rejects an all-NaN matrix, so call the operator directly
        out = REGISTRY["ts_ir"].func(flat, 4)
        self.assertTrue(pd.isna(out["A"].iloc[-1]))

    def test_zscore_is_zero_for_zero_dispersion(self):
        flat = pd.DataFrame(
            {"A": np.full(8, 5.0)}, index=pd.bdate_range("2021-01-01", periods=8)
        )
        panel = PanelStore.from_dict({"close": flat})
        out = REGISTRY["ts_zscore"].func(flat, 4)
        self.assertEqual(float(out["A"].iloc[-1]), 0.0)

    def test_ts_returns_formula(self):
        out = evaluate_text("ts_returns(close, 5)", self.panel)
        ref = self.close / self.close.shift(5) - 1.0
        self.assertLess(float((out - ref).abs().max().max()), 1e-9)

    def test_ts_returns_masks_near_zero_denominators(self):
        dates = pd.bdate_range("2021-01-01", periods=8)
        values = pd.DataFrame({"A": [1.0, 2.0, 0.0, 4.0, 5.0, 6.0, 7.0, 8.0]}, index=dates)
        panel = PanelStore.from_dict({"close": values})
        out = REGISTRY["ts_returns"].func(values, 2)
        self.assertTrue(pd.isna(out["A"].iloc[4]))  # denominator was zero

    def test_ts_quantile_default_driver(self):
        implicit = evaluate_text("ts_quantile(close, 20)", self.panel)
        explicit = evaluate_text('ts_quantile(close, 20, "gaussian")', self.panel)
        self.assertLess(float((implicit - explicit).abs().max().max()), 1e-12)

    def test_quantile_uniform_driver(self):
        out = evaluate_text('ts_quantile(close, 20, "uniform")', self.panel)
        ref = evaluate_text("ts_rank(close, 20, 1)", self.panel)
        self.assertLess(float((out - ref).abs().max().max()), 1e-12)

    def test_bollinger_bands_use_the_same_mean(self):
        out = evaluate_text("ts_bollinger_percent(close, 20)", self.panel)
        ma = self.close.rolling(20, min_periods=20).mean()
        sd = self.close.rolling(20, min_periods=20).std(ddof=0)
        upper = ma + 2.0 * sd
        lower = ma - 2.0 * sd
        ref = (self.close - lower) / (upper - lower)
        diff = (out - ref).abs().max().max()
        self.assertLess(float(diff), 1e-9)


class TestVettedRegistryParity(unittest.TestCase):
    """Every operator his vetted registry implements must match bit for bit."""

    EXTRA = {
        "ts_returns": 1, "ts_scale": 0.0, "ts_min_max_diff": 0.5,
        "ts_percentage": 0.5, "ts_bollinger_percent": 2.0,
        "ts_bollinger_position": 2.0, "ts_bollinger_width": 2.0,
    }

    def _registry(self):
        try:
            from research.operators import OperatorRegistry
            from pathlib import Path as _Path
        except ImportError:  # pragma: no cover - research package optional
            self.skipTest("research package not available")
        return OperatorRegistry(_Path(__file__).resolve().parents[1] / "docs" / "ts_operators.md")

    def test_parity_with_reference_registry(self):
        registry = self._registry()
        rng = np.random.default_rng(11)
        dates = pd.bdate_range("2020-01-01", periods=80)
        x = pd.DataFrame(rng.normal(10, 2, (80, 4)), index=dates, columns=list("ABCD"))
        x.iloc[3:5, 0] = np.nan
        x.iloc[10:13, 1] = np.nan
        x.iloc[20, 2] = 0.0
        x.iloc[25:36, 3] = 5.0
        self.assertTrue(registry.enabled)
        for name in sorted(registry.enabled):
            extra = [self.EXTRA[name]] if name in self.EXTRA else []
            theirs = registry.apply(name, [x, 20] + extra)
            ours = REGISTRY[name].func(x, 20, *extra)
            self.assertEqual(
                np.isnan(theirs.to_numpy(dtype=float)).tolist(),
                np.isnan(ours.to_numpy(dtype=float)).tolist(),
                f"{name}: NaN pattern differs",
            )
            finite = np.isfinite(theirs.to_numpy(dtype=float)) & np.isfinite(
                ours.to_numpy(dtype=float)
            )
            if finite.any():
                diff = float(
                    np.abs(
                        theirs.to_numpy(dtype=float)[finite]
                        - ours.to_numpy(dtype=float)[finite]
                    ).max()
                )
                self.assertLess(diff, 1e-12, f"{name}: values differ")


class TestCatalog(unittest.TestCase):
    def test_catalog_contents(self):
        catalog = build_catalog()
        self.assertEqual(catalog["schema_version"], "1.0")
        self.assertEqual(len(catalog["operators"]), len(REGISTRY))
        approved = [op for op in catalog["operators"] if op["approved"]]
        self.assertEqual(len(approved), 53)
        ts = [op for op in approved if op["name"].startswith("ts_")]
        self.assertEqual(len(ts), 35)
        mean = next(op for op in catalog["operators"] if op["name"] == "ts_mean")
        self.assertEqual([arg["name"] for arg in mean["args"]], ["x", "d"])
        self.assertEqual([arg["kind"] for arg in mean["args"]], ["value", "window"])
        quantile = next(op for op in catalog["operators"] if op["name"] == "ts_quantile")
        self.assertEqual(quantile["args"][2]["default"], "gaussian")
        self.assertEqual(catalog["window_policy"]["allowed"], [5, 20, 60, 120, 240])

    def test_fingerprint_is_stable_and_ignores_timestamps(self):
        first = build_catalog()
        second = build_catalog()
        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertIn("implementation_sha256", first)
        self.assertEqual(first["fingerprint"], fingerprint(first))
        tampered = json.loads(json.dumps(first))
        tampered["operators"][0]["doc"] = "changed"
        self.assertNotEqual(fingerprint(tampered), first["fingerprint"])

    def test_write_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_catalog(Path(tmp) / "operators.json", approved_only=True)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["operators"]), 53)
            self.assertIn("generated_at_utc", payload)
            self.assertNotIn("ts_corr", {op["name"] for op in payload["operators"]})


if __name__ == "__main__":
    unittest.main()

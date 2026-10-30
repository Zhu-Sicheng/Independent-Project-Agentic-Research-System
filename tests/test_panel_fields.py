"""PanelStore fields: stored, derived, and their definitions."""

import unittest

import numpy as np
import pandas as pd

from factorlab.data.panel import PanelStore


def make_panel() -> PanelStore:
    dates = pd.bdate_range("2021-01-04", periods=25)
    cols = ["A", "B"]
    close = pd.DataFrame(
        np.array([[10.0 + i * 0.5, 20.0 - i * 0.4] for i in range(25)]),
        index=dates,
        columns=cols,
    )
    open_ = close * 0.99
    high = close * 1.02
    low = close * 0.98
    volume = pd.DataFrame(
        np.array([[1000.0 + i * 10, 2000.0 - i * 5] for i in range(25)]),
        index=dates,
        columns=cols,
    )
    cap = pd.DataFrame(
        [[1e8, 2e8]] * 25, index=dates, columns=cols, dtype=float
    )
    return PanelStore.from_dict(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "cap": cap,
        }
    )


class TestDerivedFields(unittest.TestCase):
    def setUp(self):
        self.panel = make_panel()

    def test_available_lists_derived_fields(self):
        names = set(self.panel.available())
        for name in (
            "returns",
            "log_returns",
            "amount",
            "adv20",
            "cap_rank",
            "range",
            "close_position",
            "intraday_return",
            "overnight_return",
        ):
            self.assertIn(name, names)

    def test_basic_definitions(self):
        close = self.panel.field("close")
        volume = self.panel.field("volume")
        pd.testing.assert_frame_equal(
            self.panel.field("amount"), close * volume
        )
        pd.testing.assert_frame_equal(
            self.panel.field("returns"), close.pct_change(fill_method=None)
        )
        pd.testing.assert_frame_equal(
            self.panel.field("log_returns"), np.log(close).diff()
        )

    def test_adv20_is_volume_based(self):
        close = self.panel.field("close")
        volume = self.panel.field("volume")
        adv = self.panel.field("adv20")
        expected = volume.rolling(20, min_periods=10).mean()
        pd.testing.assert_frame_equal(adv, expected)
        # and it is not dollar volume, which would scale with price
        dollar = (close * volume).rolling(20, min_periods=10).mean()
        self.assertFalse(np.allclose(adv.iloc[-1], dollar.iloc[-1], equal_nan=True))

    def test_microstructure_definitions(self):
        close = self.panel.field("close")
        high = self.panel.field("high")
        low = self.panel.field("low")
        open_ = self.panel.field("open")

        pd.testing.assert_frame_equal(self.panel.field("range"), high - low)
        expected_pos = (close - low) / (high - low)
        pd.testing.assert_frame_equal(self.panel.field("close_position"), expected_pos)
        pd.testing.assert_frame_equal(
            self.panel.field("intraday_return"), close / open_ - 1.0
        )
        expected_over = open_ / close.shift(1) - 1.0
        pd.testing.assert_frame_equal(
            self.panel.field("overnight_return"), expected_over
        )

    def test_unknown_field_lists_available(self):
        with self.assertRaises(ValueError) as ctx:
            self.panel.field("definitely_not_a_field")
        self.assertIn("returns", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

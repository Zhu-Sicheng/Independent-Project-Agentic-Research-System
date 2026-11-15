"""Field cards: EDA evidence + backtest evidence, rebuilt from experiments."""

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from factorlab.field_cards import collect_backtests, collect_eda, update_field_cards


def _record(expression: str, hypothesis: str, is_sharpe: float, oos: float,
            holdout: float, decision: str = "optimize") -> dict:
    return {
        "round": 0,
        "expression": expression,
        "hypothesis": hypothesis,
        "decision": decision,
        "is": {"metrics": {"sharpe": is_sharpe, "turnover": 12.0, "rank_ic": 0.01}},
        "display": {"segments": {
            "oos": {"sharpe": oos},
            "holdout": {"sharpe": holdout},
        }},
        "stability_is": {"subuniverse_sharpe": is_sharpe * 0.7},
        "updated_at": "2026-11-01T00:00:00+00:00",
    }


class TestFieldCards(unittest.TestCase):
    def _make_experiments(self, root: Path) -> None:
        run = root / "20260101-test" / "run_a"
        (run / "agent1" / "20260101T000000Z_abc").mkdir(parents=True)
        (run / "evaluations.json").write_text(
            json.dumps({
                "n_records": 2,
                "records": [
                    _record("rank(close - open)", "close/open pressure", 1.1, 0.3, 0.2),
                    _record("ts_mean(returns, 5)", "short reversal", 0.4, -0.1, None,
                            decision="abandon"),
                ],
            }),
            encoding="utf-8",
        )
        catalog = run / "agent1" / "20260101T000000Z_abc" / "field_catalog.csv"
        pd.DataFrame(
            [
                {"dataset_id": "ds_1", "name": "Adj_Close", "semantic_role": "price",
                 "factor_usage": "candidate_requires_confirmation", "unit": "USD",
                 "earliest_availability": "", "missing_fraction": 0.0,
                 "blocking_reasons": "point_in_time_not_verified"},
                {"dataset_id": "ds_1", "name": "Adj_Open", "semantic_role": "price",
                 "factor_usage": "candidate_requires_confirmation", "unit": "USD",
                 "earliest_availability": "", "missing_fraction": 0.0,
                 "blocking_reasons": "point_in_time_not_verified"},
            ]
        ).to_csv(catalog, index=False)

    def test_collects_eda_and_backtests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_experiments(root)
            eda = collect_eda(root)
            self.assertIn("close", eda)
            self.assertEqual(eda["close"][0]["source_field"], "Adj_Close")
            rows = collect_backtests(root)
            fields = {row["field"] for row in rows}
            self.assertIn("close", fields)
            self.assertIn("open", fields)
            self.assertIn("returns", fields)
            close_rows = [r for r in rows if r["field"] == "close"]
            self.assertEqual(len(close_rows), 1)
            self.assertAlmostEqual(close_rows[0]["is_sharpe"], 1.1)

    def test_writes_cards_and_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "experiments"
            cards = Path(tmp) / "cards"
            self._make_experiments(root)
            count = update_field_cards(root, cards)
            self.assertGreaterEqual(count, 3)
            text = (cards / "close.md").read_text(encoding="utf-8")
            self.assertIn("EDA evidence", text)
            self.assertIn("Adj_Close", text)
            self.assertIn("rank(close - open)", text)
            self.assertIn("Backtest evidence (1)", text)
            index = pd.read_csv(cards / "index.csv")
            self.assertIn("close", set(index["field"]))
            close_row = index[index["field"] == "close"].iloc[0]
            self.assertEqual(int(close_row["n_backtests"]), 1)
            self.assertAlmostEqual(float(close_row["best_is_sharpe"]), 1.1)

    def test_derived_field_card_has_no_eda(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "experiments"
            cards = Path(tmp) / "cards"
            self._make_experiments(root)
            update_field_cards(root, cards)
            text = (cards / "returns.md").read_text(encoding="utf-8")
            self.assertIn("no Agent-1 EDA evidence", text)


if __name__ == "__main__":
    unittest.main()

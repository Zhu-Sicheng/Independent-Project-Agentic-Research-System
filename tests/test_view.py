import json
import tempfile
import unittest
from pathlib import Path

from factorlab.view import load_attempt, winning_expression
from factorlab.expr import parser as P


class TestViewReplay(unittest.TestCase):
    def test_winning_windows_replace_nested_slots(self):
        attempt = {'spec': {'expression': 'ts_mean(ts_returns(close, 5), 20)'},
                   'grid': {'best': {'windows': [60, 120]}}}
        expr = winning_expression(attempt)
        self.assertEqual(P.collect_windows(P.parse(expr)), [60, 120])

    def test_interrupted_run_uses_journal(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            a = {'hypothesis': 'example', 'attempt': 0}
            (p / 'attempts.jsonl').write_text(json.dumps(a) + '\n', encoding='utf-8')
            _, actual = load_attempt(str(p), 'example')
            self.assertEqual(actual, a)

    def test_constant_rank_is_not_a_portfolio(self):
        import numpy as np
        import pandas as pd
        from factorlab.data.panel import PanelStore
        from factorlab.backtest.engine import run_backtest
        from factorlab.config import BacktestSettings
        dates = pd.bdate_range('2020-01-01', periods=30)
        close = pd.DataFrame(np.arange(30)[:, None] + np.arange(30)[None, :] + 100., index=dates)
        panel = PanelStore.from_dict({'close': close})
        signal = pd.DataFrame(-0.4, index=dates, columns=panel.tickers)
        result = run_backtest(signal, panel, BacktestSettings(transform='rank', min_names=5, keep_positions=True))
        self.assertEqual(float(result.positions.abs().to_numpy().max()), 0.)
        self.assertEqual(float(result.pnl.fillna(0).abs().max()), 0.)
        self.assertTrue(np.isnan(result.metrics['sharpe']))

    def test_draw_panels_writes_four_panel_figure(self):
        import numpy as np
        import pandas as pd
        from PIL import Image
        from factorlab.backtest.split import SplitMasks
        from factorlab.view import draw_panels

        idx = pd.bdate_range("2020-01-01", periods=300)
        rng = np.random.default_rng(0)
        pnl = pd.Series(rng.normal(0, 0.001, 300), index=idx)
        turnover = pd.Series(0.2, index=idx)
        ic = pd.Series(0.01, index=idx)
        masks = SplitMasks(masks={"is": pd.Series(True, index=idx)}, meta={})
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "figure.png"
            draw_panels(pnl, turnover, ic, {}, masks, out, "test factor")
            self.assertTrue(out.exists())
            with Image.open(out) as image:
                width, height = image.size
            self.assertGreater(height, width)  # four stacked panels

    def test_unchanged_expression_without_windows(self):
        a = {'spec': {'expression': 'rank(close)'}, 'grid': {'best': {'windows': []}}}
        self.assertEqual(winning_expression(a), 'rank(close)')

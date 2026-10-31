"""Replay a completed batch and export charts/tables without new LLM calls.

python -m factorlab.export_batch --runs <run_id> <run_id> --out experiments/batch10
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PROJECT_ROOT
from .data import load_processed
from .view import rebuild_result, winning_expression, plot_result, yearly_stats
from .markdown import md_table
from .experiments import rebuild_ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', nargs='+', required=True)
    parser.add_argument('--out', default='experiments/batch10')
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    panel = load_processed(PROJECT_ROOT / 'data/processed/panel')
    rows = []
    records = []
    for run_id in args.runs:
        journal = PROJECT_ROOT / 'runs' / run_id / 'attempts.jsonl'
        attempts = [json.loads(x) for x in journal.read_text(encoding='utf-8').splitlines() if x.strip()]
        for attempt in attempts:
            if not attempt.get('grid'):
                continue
            name = attempt['hypothesis']
            print(f'Replaying {run_id}/{name}', flush=True)
            result, masks = rebuild_result(panel, attempt)
            best = attempt['grid']['best']
            # Historical summary stores Sharpe at 3 decimals. Refuse a misleading plot.
            delta = abs(float(result.metrics['sharpe']) - float(best['sharpe']))
            inactive = float(result.pnl.fillna(0).abs().max()) == 0.0
            status = 'invalid_constant_signal' if inactive else 'verified'
            if not inactive and (not np.isfinite(delta) or delta > 0.0011):
                raise RuntimeError(f'Replay mismatch for {name}: delta Sharpe={delta}')
            stem = f'{run_id}_{name}'
            expression = winning_expression(attempt)
            plot_result(attempt, result, masks, out / f'{stem}.png', f'{name} | {expression}')
            daily = pd.DataFrame({'pnl': result.pnl, 'turnover': result.turnover,
                                  'rank_ic': result.ic, 'pearson_ic': result.pearson_ic})
            if result.subuniverse is not None:
                daily['sub_pnl'] = result.subuniverse.pnl
            daily.to_csv(out / f'{stem}_daily.csv', index_label='date')
            yearly = yearly_stats(result.pnl, result.turnover, result.ic)
            yearly.to_csv(out / f'{stem}_yearly.csv')
            row = {'run_id': run_id, 'hypothesis': name,
                   'decision': (attempt.get('review') or {}).get('decision'),
                   'expression': expression, 'n_evals': attempt['grid']['n_evals'],
                   'sharpe_full': result.metrics['sharpe'],
                   'ann_return_full': result.metrics['ann_return'],
                   'turnover_full': result.metrics['turnover'],
                   'max_drawdown_full': result.metrics['max_drawdown'],
                   'rank_ic_full': result.metrics['rank_ic'],
                   'sharpe_sub': result.subuniverse.metrics['sharpe'] if result.subuniverse else None,
                   'verification_status': status,
                   'historical_sharpe_full': best['sharpe'],
                   'replay_sharpe_difference': delta,
                   'plot': f'{stem}.png', 'yearly': f'{stem}_yearly.csv'}
            for seg in ('is', 'oos', 'holdout'):
                for key in ('sharpe', 'ann_return', 'turnover', 'max_drawdown', 'rank_ic'):
                    row[f'{key}_{seg}'] = result.segments.get(seg, {}).get(key)
            rows.append(row)
            records.append({'run_id': run_id, **attempt, 'effective_expression': expression})
    frame = pd.DataFrame(rows)
    frame.to_csv(out / 'summary.csv', index=False)
    (out / 'attempts.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    cols = ['hypothesis', 'n_evals', 'decision', 'sharpe_full', 'sharpe_is', 'sharpe_oos', 'sharpe_holdout', 'sharpe_sub']
    text = ['# Ten-attempt real-data batch', '',
            'Ten completed attempts across an interrupted first run (4) and its continuation (6).',
            'The overnight/intraday mechanism was repeated: this is ten evaluations, not ten unique mechanisms.',
            'The first four used up to 120 grid evaluations; the continuation used up to 80.',
            'Selection uses IS. OOS is 2021–2024; 2025+ holdout has already been inspected and is not pristine.',
            'Costs are zero. The capital filter is still a search dimension; primary and sub-universe may coincide.',
            'Nine signals replay within rounding. dollar_volume_shock_reversal collapsed to a constant (60/60 windows):',
            'its historical Sharpe was floating-point demeaning noise amplified into a portfolio. It is invalid.',
            'The corrected engine gives zero exposure/PnL and undefined Sharpe. Historical records remain unchanged.', '',
            md_table(frame[cols]), '']
    for row, record in zip(rows, records):
        review = record.get('review') or {}
        text += [f"## {row['hypothesis']} ({row['run_id']})", '',
                 f"Effective expression: `{row['expression']}`", '',
                 f"Decision: **{row['decision']}**. {review.get('reasoning', '')}", '',
                 f"![Equity, drawdown and yearly Sharpe]({row['plot']})", '',
                 f"[Calendar-year statistics]({row['yearly']})", '']
    (out / 'README.md').write_text('\n'.join(text), encoding='utf-8')
    rebuild_ledger()
    print(frame[cols].to_string(index=False), flush=True)
    print(f'Exported {len(frame)} attempts to {out}', flush=True)


if __name__ == '__main__':
    main()

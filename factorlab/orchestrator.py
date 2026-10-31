"""The mining loop: hypothesis -> implementation -> backtest -> review -> pool.

One `MiningLoop.run()` is one research session.  Every attempt is logged to
``runs/<run_id>/attempts.jsonl`` and summarised in ``runs/<run_id>/report.md``.
"""

from __future__ import annotations

import json
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .agents import CriticAgent, HypothesisAgent, ImplementationAgent, build_client
from .backtest.grid import GridSearch
from .backtest.split import resolve_split
from .config import DEFAULT_RUNS_DIR, MiningConfig
from .data.panel import PanelStore
from .experiments import rebuild_ledger
from .expr.spec import FactorSpec
from .markdown import md_table
from .pool.pool import FactorPool


@dataclass
class Attempt:
    hypothesis: str
    attempt: int
    spec: dict
    validation: dict
    grid: Optional[dict]
    review: Optional[dict]
    factor_id: Optional[str] = None
    elapsed_s: float = 0.0
    error: Optional[str] = None


class MiningLoop:
    def __init__(
        self,
        panel: PanelStore,
        pool: Optional[FactorPool] = None,
        config: Optional[MiningConfig] = None,
        llm=None,
        out_dir: Optional[Path] = None,
        verbose: bool = True,
        run_tag: str = "",
    ):
        self.panel = panel
        self.config = config or MiningConfig()
        self.pool = pool if pool is not None else FactorPool()
        self.llm = llm or build_client(self.config.llm)
        self.hypothesis_agent = HypothesisAgent(self.llm, n=self.config.n_hypotheses)
        self.implementer = ImplementationAgent(self.llm)
        self.critic = CriticAgent(self.llm)
        self.verbose = verbose
        self.tried: list[str] = []
        self.attempts: list[Attempt] = []
        self.added: list[str] = []
        self._hypotheses: dict[str, dict] = {}
        self.split = self.config.split or panel.meta.get("default_split")
        self.split_masks = resolve_split(panel.dates, self.split)
        self.run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + (f"-{run_tag}" if run_tag else "")
        self.run_dir = Path(out_dir or DEFAULT_RUNS_DIR) / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._started = time.time()

    # ------------------------------------------------------------------ #
    def run(self, hypotheses: Optional[list[dict]] = None) -> dict:
        panel_summary = self.panel.summary()
        (self.run_dir / "panel_summary.json").write_text(
            json.dumps(panel_summary, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        self._log(
            f"panel {self.panel.shape[0]} days x {self.panel.shape[1]} names "
            f"({self.panel.dates[0].date()} -> {self.panel.dates[-1].date()}), "
            f"LLM: {self.llm.name}"
        )
        self._log(
            f"split: {self.split_masks.describe()} "
            f"(IS {self.split_masks.meta.get('n_is')}d / OOS "
            f"{self.split_masks.meta.get('n_oos')}d / holdout "
            f"{self.split_masks.meta.get('n_holdout')}d)"
        )
        for warning in self.split_masks.meta.get("warnings", []):
            self._log(f"  ! {warning}")

        hyps = hypotheses or self.hypothesis_agent.propose(
            panel_summary,
            self.pool.summary_for_agent(),
            tried=self.tried,
        )
        self._hypotheses = {h["name"]: h for h in hyps}
        from dataclasses import asdict
        (self.run_dir / "hypotheses.json").write_text(
            json.dumps(hyps, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (self.run_dir / "config.json").write_text(
            json.dumps({"backtest": asdict(self.config.backtest),
                        "grid": asdict(self.config.grid),
                        "split": self.split_masks.meta,
                        "llm_model": self.config.llm.model},
                       indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )
        self._log(f"proposed {len(hyps)} hypotheses: {[h['name'] for h in hyps]}")

        for h in hyps:
            self.tried.append(h["name"])
            try:
                self._run_hypothesis(h)
            except Exception as exc:  # keep the session going
                self._log(f"  ! {h['name']} crashed: {exc}")
                if self.verbose:
                    traceback.print_exc()

        self.pool.recompute_correlations()
        self._write_report(panel_summary)
        try:
            rebuild_ledger(self.run_dir.parent)
        except Exception as exc:  # the ledger must never break a run
            self._log(f"ledger update failed: {exc}")
        elapsed = time.time() - self._started
        result = {
            "run_id": self.run_id,
            "llm": self.llm.name,
            "data": self.panel.name,
            "n_hypotheses": len(hyps),
            "n_factors_added": len(self.added),
            "added": self.added,
            "attempts": [a.__dict__ for a in self.attempts],
            "elapsed_s": round(elapsed, 1),
            "run_dir": str(self.run_dir),
        }
        (self.run_dir / "run.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )
        self._log(
            f"done in {elapsed:.0f}s: {len(self.added)} factors added to the pool"
        )
        return result

    # ------------------------------------------------------------------ #
    def _run_hypothesis(self, hypothesis: dict) -> None:
        name = hypothesis["name"]
        self._log(f"\n[{name}] {hypothesis.get('hypothesis', '')}")
        spec = self.implementer.implement(hypothesis, self.panel)
        history: list[dict] = []

        for attempt in range(self.config.max_rounds):
            started = time.time()
            report = spec.validate(self.panel)
            record = Attempt(
                hypothesis=name,
                attempt=attempt,
                spec=spec.to_dict(),
                validation=report.to_dict(),
                grid=None,
                review=None,
            )
            if not report.ok:
                record.error = "; ".join(report.errors)
                self._log(f"  round {attempt}: invalid spec: {record.error}")
                self._record(record)
                break

            self._log(
                f"  round {attempt}: {spec.kind} "
                f"{(spec.expression or '<script>')[:90]}"
            )
            grid = GridSearch(
                self.panel,
                self.config.grid,
                self.config.backtest,
                split=self.split,
            ).run_spec(spec)
            record.elapsed_s = round(time.time() - started, 1)
            best = grid.best.metrics
            self._log(
                f"    grid {grid.n_evals} evals -> sharpe {best.get('sharpe', float('nan')):.2f}, "
                f"ann {best.get('ann_return', float('nan')):.1%}, "
                f"turnover {best.get('turnover', float('nan')):.1f}, "
                f"maxdd {best.get('max_drawdown', float('nan')):.1%}"
            )
            if grid.best.subuniverse is not None:
                sub_m = grid.best.subuniverse.metrics
                self._log(
                    f"    sub-universe (rank(cap) > {grid.best.subuniverse.threshold}) "
                    f"-> sharpe {sub_m.get('sharpe', float('nan')):.2f}, "
                    f"ann {sub_m.get('ann_return', float('nan')):.1%}, "
                    f"rankIC {sub_m.get('rank_ic', float('nan')):.3f}"
                )
            if grid.has_oos:
                oos = (grid.best.segments or {}).get("oos", {})
                self._log(
                    f"    out-of-sample -> sharpe {oos.get('sharpe', float('nan')):.2f}, "
                    f"ann {oos.get('ann_return', float('nan')):.1%} "
                    f"({self.split_masks.meta.get('oos_range')})"
                )
            if grid.has_holdout:
                hold = (grid.best.segments or {}).get("holdout", {})
                self._log(
                    f"    holdout      -> sharpe {hold.get('sharpe', float('nan')):.2f}, "
                    f"ann {hold.get('ann_return', float('nan')):.1%} "
                    f"({self.split_masks.meta.get('holdout_range')})"
                )
            review = self.critic.review(
                hypothesis, spec, grid, history, self.panel, self.config.max_rounds
            )
            record.grid = grid.summary()
            record.review = review
            self._log(f"    decision: {review['decision']} -- {review.get('reasoning', '')[:160]}")

            if review["decision"] == "accept":
                rec = self.pool.add(
                    spec=spec,
                    hypothesis=hypothesis,
                    grid=grid,
                    run_id=self.run_id,
                    name=name,
                    tags=[hypothesis.get("source", "unknown"), self.llm.name],
                    notes=review.get("reasoning", ""),
                )
                record.factor_id = rec.id
                self.added.append(rec.id)
                self._log(f"    -> stored as {rec.id}")
                self._record(record)
                break

            if review["decision"] == "optimize" and review.get("revised") and attempt + 1 < self.config.max_rounds:
                revised = FactorSpec.from_dict(review["revised"])
                if revised.canonical() == spec.canonical():
                    self._log("    revised spec identical to the current one; stop")
                    self._record(record)
                    break
                history.append(
                    {
                        "expression": spec.expression,
                        "script": spec.script,
                        "sharpe": best.get("sharpe"),
                        "turnover": best.get("turnover"),
                        "ic": best.get("ic"),
                        "review": review.get("reasoning"),
                    }
                )
                spec = revised
                self._record(record)
                continue

            self._record(record)
            break

    # ------------------------------------------------------------------ #
    def _record(self, record: Attempt) -> None:
        self.attempts.append(record)
        with (self.run_dir / "attempts.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record.__dict__, ensure_ascii=False, default=str) + "\n")
        archive = self.run_dir.parent.parent / "experiments" / "records" / self.run_id
        archive.mkdir(parents=True, exist_ok=True)
        (archive / "attempts.jsonl").write_text(
            (self.run_dir / "attempts.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
        )

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg, flush=True)

    # ------------------------------------------------------------------ #
    # report
    # ------------------------------------------------------------------ #
    def _write_report(self, panel_summary: dict) -> None:
        split_meta = self.split_masks.meta
        has_oos = bool(split_meta.get("has_oos"))
        has_holdout = bool(split_meta.get("has_holdout"))
        lines = [
            "# Factor mining run",
            "",
            f"- run id: `{self.run_id}`",
            f"- data: {panel_summary['n_dates']} days x {panel_summary['n_tickers']} names, "
            f"{panel_summary['start']} -> {panel_summary['end']}",
            f"- LLM: `{self.llm.name}`",
            f"- hypotheses: {len(self.tried)}, factors added: {len(self.added)}",
            f"- sample split: {split_meta.get('description')}",
        ]
        if has_oos:
            lines.append(
                f"  - in-sample {split_meta.get('is_range')} "
                f"({split_meta.get('n_is')} days) / out-of-sample "
                f"{split_meta.get('oos_range')} ({split_meta.get('n_oos')} days)"
                + (
                    f" / holdout {split_meta.get('holdout_range')} "
                    f"({split_meta.get('n_holdout')} days)"
                    if has_holdout
                    else ""
                )
            )
        else:
            lines.append(
                "  - split points not set yet: fill in train_frac or "
                "train_end / test_start once the real data dates are known"
            )
        lines += ["", "## Hypotheses and decisions", ""]

        any_oos = any((a.grid or {}).get("in_sample") for a in self.attempts)
        any_holdout = any((a.grid or {}).get("holdout") for a in self.attempts)
        cols = [
            "hypothesis",
            "attempt",
            "decision",
            "sharpe all" if any_oos else "sharpe",
            "ann return",
            "turnover",
            "maxDD",
            "RankIC",
            "factor",
        ]
        if any_oos:
            cols += ["sharpe IS", "sharpe OOS"]
        if any_holdout:
            cols += ["sharpe Holdout"]
        any_sub = any((a.grid or {}).get("subuniverse") for a in self.attempts)
        if any_sub:
            cols += ["sharpe sub"]
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("|" + "|".join(["---"] * len(cols)) + "|")

        last_by_hyp: dict[str, Attempt] = {}
        for a in self.attempts:
            last_by_hyp[a.hypothesis] = a
        for name, a in last_by_hyp.items():
            grid = a.grid or {}
            b = grid.get("best", {})
            decision = (a.review or {}).get("decision", "error")
            cells = [
                name,
                str(a.attempt + 1),
                decision,
                _fmt(b.get("sharpe"), 2),
                _fmt_pct(b.get("ann_return")),
                _fmt(b.get("turnover"), 1),
                _fmt_pct(b.get("max_drawdown")),
                _fmt(b.get("rank_ic", b.get("ic")), 3),
                a.factor_id or "-",
            ]
            if any_oos:
                cells += [
                    _fmt((grid.get("in_sample") or {}).get("sharpe"), 2),
                    _fmt((grid.get("out_of_sample") or {}).get("sharpe"), 2),
                ]
            if any_holdout:
                cells += [_fmt((grid.get("holdout") or {}).get("sharpe"), 2)]
            if any_sub:
                cells += [_fmt((grid.get("subuniverse") or {}).get("metrics", {}).get("sharpe"), 2)]
            lines.append("| " + " | ".join(cells) + " |")

        for name, a in last_by_hyp.items():
            grid = a.grid or {}
            b = grid.get("best", {})
            review = a.review or {}
            spec = a.spec
            hyp = self._hypotheses.get(name, {})
            lines += ["", f"## {name}", ""]
            if hyp.get("hypothesis"):
                lines.append(f"**hypothesis**: {hyp['hypothesis']}")
                lines.append("")
            if hyp.get("economic_rationale"):
                lines.append(f"**economic rationale**: {hyp['economic_rationale']}")
                lines.append("")
            if b:
                lines.append(
                    f"best config: decay={b.get('decay')}, transform={b.get('transform')}, "
                    f"cap_filter={_fmt_cfg(b.get('cap_filter'))}, "
                    f"windows={b.get('windows') or '[]'}, params={b.get('params') or {}}"
                )
            lines.append("")
            lines.append(f"- **decision**: {review.get('decision')}")
            lines.append(f"- **reasoning**: {review.get('reasoning', '')}")
            lines.append(f"- **diagnosis**: {review.get('diagnosis', '')}")
            lines.append(f"- **spec**: `{spec.get('expression') or '<script>'}`")
            sub = grid.get("subuniverse") or {}
            if sub.get("metrics"):
                sm = sub["metrics"]
                same_filter = False
                try:
                    same_filter = (
                        b.get("cap_filter") is not None
                        and abs(float(b.get("cap_filter")) - float(sub.get("threshold"))) < 1e-9
                    )
                except (TypeError, ValueError):
                    same_filter = False
                lines.append(
                    f"- **sub-universe** (rank(cap) > {sub.get('threshold')}, "
                    "reference only): "
                    f"sharpe {_fmt(sm.get('sharpe'), 2)}, "
                    f"return {_fmt_pct(sm.get('ann_return'))}/yr, "
                    f"turnover {_fmt(sm.get('turnover'), 1)}, "
                    f"maxDD {_fmt_pct(sm.get('max_drawdown'))}, "
                    f"RankIC {_fmt(sm.get('rank_ic', sm.get('ic')), 3)}"
                    + (
                        " — identical to the primary book because the best config "
                        "already drops the same names"
                        if same_filter
                        else ""
                    )
                )

            ins = grid.get("in_sample")
            oos = grid.get("out_of_sample")
            hold = grid.get("holdout")
            if ins or oos or hold:
                lines.append(
                    "- **in-sample**: "
                    + _segment_line(ins)
                    + (f"  ({_range_str(split_meta.get('is_range'))})" if ins else "")
                )
                lines.append(
                    "- **out-of-sample**: "
                    + _segment_line(oos)
                    + (f"  ({_range_str(split_meta.get('oos_range'))})" if oos else "")
                )
            if hold:
                lines.append(
                    "- **holdout**: "
                    + _segment_line(hold)
                    + f"  ({_range_str(split_meta.get('holdout_range'))})"
                )

            yearly = grid.get("yearly") or []
            if yearly:
                lines += [
                    "",
                    "| year | return | sharpe | turnover | maxDD | RankIC |",
                    "|---|---|---|---|---|---|",
                ]
                for y in yearly:
                    lines.append(
                        f"| {y.get('year')} | {_fmt_pct(y.get('total_return'))} | "
                        f"{_fmt(y.get('sharpe'), 2)} | {_fmt(y.get('turnover'), 1)} | "
                        f"{_fmt_pct(y.get('max_drawdown'))} | {_fmt(y.get('ic'), 3)} |"
                    )
            hold_yearly = (hold or {}).get("yearly") if isinstance(hold, dict) else None
            if hold_yearly:
                lines += [
                    "",
                    "holdout by year:",
                    "",
                    "| year | return | sharpe | turnover | maxDD | RankIC |",
                    "|---|---|---|---|---|---|",
                ]
                for y in hold_yearly:
                    lines.append(
                        f"| {y.get('year')} | {_fmt_pct(y.get('total_return'))} | "
                        f"{_fmt(y.get('sharpe'), 2)} | {_fmt(y.get('turnover'), 1)} | "
                        f"{_fmt_pct(y.get('max_drawdown'))} | {_fmt(y.get('ic'), 3)} |"
                    )
            oos_yearly = (oos or {}).get("yearly") if isinstance(oos, dict) else None
            if oos_yearly:
                lines += [
                    "",
                    "out-of-sample by year:",
                    "",
                    "| year | return | sharpe | turnover | maxDD | RankIC |",
                    "|---|---|---|---|---|---|",
                ]
                for y in oos_yearly:
                    lines.append(
                        f"| {y.get('year')} | {_fmt_pct(y.get('total_return'))} | "
                        f"{_fmt(y.get('sharpe'), 2)} | {_fmt(y.get('turnover'), 1)} | "
                        f"{_fmt_pct(y.get('max_drawdown'))} | {_fmt(y.get('ic'), 3)} |"
                    )

        pool_summary = self.pool.summary()
        if not pool_summary.empty:
            pool_cols = [
                "name",
                "sharpe",
                "ann_return",
                "turnover",
                "ic",
            ]
            if "sharpe_oos" in pool_summary.columns and pool_summary["sharpe_oos"].notna().any():
                pool_cols.append("sharpe_oos")
            if (
                "sharpe_holdout" in pool_summary.columns
                and pool_summary["sharpe_holdout"].notna().any()
            ):
                pool_cols.append("sharpe_holdout")
            pool_cols += ["max_abs_xs_corr", "max_abs_pnl_corr"]
            lines += [
                "",
                "## Factor pool",
                "",
                md_table(pool_summary.head(15)[pool_cols]),
                "",
                "Cross-sectional Spearman and PnL Pearson are *stored, not thresholded*.",
            ]
            corr = self.pool.correlations()
            if not corr.empty:
                top = corr.reindex(
                    corr["xs_spearman_mean"].abs().sort_values(ascending=False).index
                ).head(5)
                lines += [
                    "",
                    md_table(
                        top[["factor_a", "factor_b", "xs_spearman_mean", "pnl_pearson"]]
                    ),
                ]

        self._plot_equity()
        (self.run_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")

    def _plot_equity(self) -> None:
        if not self.added:
            return
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(9, 4.5))
            for fid in self.added:
                try:
                    pnl = self.pool.load_pnl(fid)
                except FileNotFoundError:
                    continue
                ax.plot((1 + pnl.fillna(0)).cumprod(), label=fid, linewidth=1.2)
            ax.set_title("Factor pool equity curves (1x gross, no costs)")
            ax.set_ylabel("growth of 1")
            ax.legend(fontsize=7, loc="upper left")
            ax.grid(alpha=0.25)
            fig.tight_layout()
            fig.savefig(self.run_dir / "equity.png", dpi=140)
            plt.close(fig)
        except Exception as exc:  # pragma: no cover - plotting is optional
            self._log(f"plot skipped: {exc}")


def _fmt(x, digits: int) -> str:
    try:
        if x is None or not np.isfinite(float(x)):
            return "-"
        return f"{float(x):.{digits}f}"
    except (TypeError, ValueError):
        return "-"


def _fmt_pct(x) -> str:
    try:
        if x is None or not np.isfinite(float(x)):
            return "-"
        return f"{float(x):.1%}"
    except (TypeError, ValueError):
        return "-"


def _range_str(value) -> str:
    if not value or len(value) < 2:
        return "-"
    return f"{value[0]} .. {value[1]}"


def _segment_line(metrics: Optional[dict]) -> str:
    if not metrics:
        return "-"
    return (
        f"sharpe {_fmt(metrics.get('sharpe'), 2)}, "
        f"return {_fmt_pct(metrics.get('ann_return'))}/yr, "
        f"turnover {_fmt(metrics.get('turnover'), 1)}, "
        f"maxDD {_fmt_pct(metrics.get('max_drawdown'))}, "
        f"RankIC {_fmt(metrics.get('rank_ic', metrics.get('ic')), 3)}"
    )


def _fmt_cfg(value) -> str:
    if value is None:
        return "none"
    try:
        if isinstance(value, float) and not np.isfinite(value):
            return "none"
    except TypeError:
        pass
    return str(value)

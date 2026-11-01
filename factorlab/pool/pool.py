"""The factor pool: storage + cross-factor correlation.

A factor is stored as a directory::

    pool/factors/<id>/meta.json      full record (spec, hypothesis, metrics)
    pool/factors/<id>/factor.parquet raw factor matrix (date x ticker, float32)
    pool/factors/<id>/pnl.parquet    daily pnl + turnover of the best config
    pool/factors/<id>/grid.parquet   the grid-search table (trimmed)

Correlations are *measured, not thresholded*: every new factor is compared with
the existing pool both cross-sectionally (mean daily Spearman of the factor
matrices) and in the time series (Pearson of the daily PnL).  Values are stored
so that a human or an agent can later decide what to do with them.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from ..backtest import metrics as M
from ..backtest.grid import GridResult
from ..config import DEFAULT_POOL_DIR
from ..expr.spec import FactorSpec
from ..markdown import md_table


def _jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return None if not np.isfinite(obj) else float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, float):
        return None if not np.isfinite(obj) else obj
    if isinstance(obj, pd.Timestamp):
        return str(obj)
    return obj


def slugify(text: str, max_len: int = 40) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", str(text)).strip("_").lower()
    return (text or "factor")[:max_len]


@dataclass
class FactorRecord:
    id: str
    name: str
    fingerprint: str
    created_at: str
    run_id: str
    spec: dict
    hypothesis: dict
    metrics: dict
    best_config: dict
    yearly: list
    grid: dict
    segments: dict = field(default_factory=dict)
    #: reference backtest on ``if_else(rank(cap) > 0.3, factor, nan)``
    subuniverse: dict = field(default_factory=dict)
    tags: list = field(default_factory=list)
    notes: str = ""
    parent_id: Optional[str] = None
    corr_vs_pool: list = field(default_factory=list)
    max_abs_xs_corr: Optional[float] = None
    max_abs_pnl_corr: Optional[float] = None
    max_corr_with: Optional[str] = None

    def to_dict(self) -> dict:
        return _jsonable(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict) -> "FactorRecord":
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})


class FactorPool:
    def __init__(self, root: str | Path = DEFAULT_POOL_DIR):
        self.root = Path(root)
        self.factors_dir = self.root / "factors"
        self.index_path = self.root / "index.json"
        self.corr_path = self.root / "correlations.csv"
        self.factors_dir.mkdir(parents=True, exist_ok=True)
        self._index: dict[str, FactorRecord] = {}
        self._load()

    # ------------------------------------------------------------------ #
    # persistence
    # ------------------------------------------------------------------ #
    def _load(self) -> None:
        if self.index_path.exists():
            data = json.loads(self.index_path.read_text(encoding="utf-8"))
            for item in data.get("factors", []):
                rec = FactorRecord.from_dict(item)
                self._index[rec.id] = rec

    def _save_index(self) -> None:
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "n_factors": len(self._index),
            "factors": [rec.to_dict() for rec in self._index.values()],
        }
        self.index_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # ------------------------------------------------------------------ #
    # add
    # ------------------------------------------------------------------ #
    def add(
        self,
        spec: FactorSpec,
        hypothesis: dict,
        grid: GridResult,
        run_id: str = "manual",
        name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        notes: str = "",
        parent_id: Optional[str] = None,
    ) -> FactorRecord:
        name = name or hypothesis.get("name") or spec.name or "factor"
        fid = f"{slugify(name)}-{spec.fingerprint()}"
        fdir = self.factors_dir / fid
        fdir.mkdir(parents=True, exist_ok=True)

        factor = grid.best_factor.astype("float32")
        factor.to_parquet(fdir / "factor.parquet")
        pnl = pd.DataFrame(
            {"pnl": grid.best.pnl, "turnover": grid.best.turnover}
        ).dropna(how="all")
        pnl.to_parquet(fdir / "pnl.parquet")

        sub = grid.best.subuniverse
        subuniverse = (
            _jsonable(
                {
                    "threshold": sub.threshold,
                    "metrics": sub.metrics,
                    "segments": sub.segments,
                }
            )
            if sub is not None
            else {}
        )

        grid_table = grid.table.head(100).copy()
        for col in grid_table.columns:
            if grid_table[col].dtype == object:
                grid_table[col] = grid_table[col].astype(str)
        grid_table.to_parquet(fdir / "grid.parquet")

        rec = FactorRecord(
            id=fid,
            name=name,
            fingerprint=spec.fingerprint(),
            created_at=datetime.now(timezone.utc).isoformat(),
            run_id=run_id,
            spec=spec.to_dict(),
            hypothesis={k: _jsonable(v) for k, v in (hypothesis or {}).items()},
            metrics=_jsonable(grid.best.metrics),
            best_config=_jsonable(
                {
                    "decay": grid.best.settings.decay,
                    "transform": grid.best.settings.transform,
                    "cap_filter": grid.best.settings.cap_filter,
                    "windows": grid.best_row.get("windows"),
                    "params": grid.best_row.get("params"),
                    "y": grid.best.settings.y,
                    "delay": grid.best.settings.delay,
                }
            ),
            yearly=_jsonable(grid.best.yearly.reset_index().to_dict(orient="records")),
            segments=_jsonable(grid.best.segments or {}),
            subuniverse=subuniverse,
            grid=_jsonable(
                {
                    "n_evals": grid.n_evals,
                    "objective": grid.objective,
                    "share_positive_sharpe": float((grid.table["sharpe"] > 0).mean()),
                }
            ),
            tags=list(tags or []),
            notes=notes,
            parent_id=parent_id,
            max_abs_xs_corr=0.0,
            max_abs_pnl_corr=0.0,
        )

        # incremental correlations against the existing pool
        touched: list[FactorRecord] = []
        for other in self._index.values():
            if other.id == fid:
                continue
            corr = self._pair_corr(factor, grid.best.pnl, other)
            if corr is None:
                continue
            rec.corr_vs_pool.append({"factor": other.id, **corr})
            if np.isfinite(corr["xs_spearman_mean"]):
                if abs(corr["xs_spearman_mean"]) >= abs(rec.max_abs_xs_corr or 0.0):
                    rec.max_abs_xs_corr = round(float(abs(corr["xs_spearman_mean"])), 4)
                    rec.max_corr_with = other.id
            if np.isfinite(corr["pnl_pearson"]):
                rec.max_abs_pnl_corr = round(
                    max(rec.max_abs_pnl_corr or 0.0, abs(corr["pnl_pearson"])), 4
                )

            # keep the relation symmetric so either side can be queried
            other.corr_vs_pool = [
                c for c in other.corr_vs_pool if c.get("factor") != fid
            ]
            other.corr_vs_pool.append({"factor": fid, **corr})
            if np.isfinite(corr["xs_spearman_mean"]):
                if abs(corr["xs_spearman_mean"]) >= abs(other.max_abs_xs_corr or 0.0):
                    other.max_abs_xs_corr = round(float(abs(corr["xs_spearman_mean"])), 4)
                    other.max_corr_with = fid
            if np.isfinite(corr["pnl_pearson"]):
                other.max_abs_pnl_corr = round(
                    max(other.max_abs_pnl_corr or 0.0, abs(corr["pnl_pearson"])), 4
                )
            touched.append(other)

        for other in touched:
            (self.factors_dir / other.id / "meta.json").write_text(
                json.dumps(other.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
            )

        (fdir / "meta.json").write_text(
            json.dumps(rec.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        self._index[fid] = rec
        self._save_index()

        # keep the global pairwise table in sync
        self._append_correlations(fid, rec)
        return rec

    # ------------------------------------------------------------------ #
    # reads
    # ------------------------------------------------------------------ #
    def __len__(self) -> int:
        return len(self._index)

    def records(self) -> list[FactorRecord]:
        return list(self._index.values())

    def get(self, factor_id: str) -> FactorRecord:
        if factor_id not in self._index:
            raise KeyError(f"unknown factor {factor_id!r}")
        return self._index[factor_id]

    def load_factor(self, factor_id: str) -> pd.DataFrame:
        path = self.factors_dir / factor_id / "factor.parquet"
        if not path.exists():
            raise FileNotFoundError(path)
        return pd.read_parquet(path)

    def load_pnl(self, factor_id: str) -> pd.Series:
        path = self.factors_dir / factor_id / "pnl.parquet"
        if not path.exists():
            raise FileNotFoundError(path)
        return pd.read_parquet(path)["pnl"]

    def summary(self) -> pd.DataFrame:
        rows = []
        for rec in self._index.values():
            m = rec.metrics
            segs = rec.segments or {}
            is_m = segs.get("is") or {}
            oos_m = segs.get("oos") or {}
            hold_m = segs.get("holdout") or {}
            row = {
                "id": rec.id,
                "name": rec.name,
                "sharpe": m.get("sharpe"),
                "ann_return": m.get("ann_return"),
                "turnover": m.get("turnover"),
                "max_drawdown": m.get("max_drawdown"),
                "ic": m.get("ic"),
                "rank_ic": m.get("rank_ic"),
                "max_abs_xs_corr": rec.max_abs_xs_corr,
                "max_abs_pnl_corr": rec.max_abs_pnl_corr,
                "created_at": rec.created_at,
            }
            sub = rec.subuniverse or {}
            sub_m = sub.get("metrics") or {}
            if sub_m:
                row["sub_sharpe"] = sub_m.get("sharpe")
                row["sub_ann_return"] = sub_m.get("ann_return")
                row["sub_turnover"] = sub_m.get("turnover")
            if is_m:
                row["sharpe_is"] = is_m.get("sharpe")
            if oos_m:
                row["sharpe_oos"] = oos_m.get("sharpe")
                row["ann_return_oos"] = oos_m.get("ann_return")
            if hold_m:
                row["sharpe_holdout"] = hold_m.get("sharpe")
                row["ann_return_holdout"] = hold_m.get("ann_return")
            rows.append(row)
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("sharpe", ascending=False).reset_index(drop=True)
        return df

    def summary_for_agent(self, limit: int = 15) -> list[dict]:
        """Compact, prompt-friendly view of what has already been mined."""
        out = []
        for rec in sorted(
            self._index.values(),
            key=lambda r: float(r.metrics.get("sharpe") or -9),
            reverse=True,
        )[:limit]:
            oos = (rec.segments or {}).get("oos") or {}
            hold = (rec.segments or {}).get("holdout") or {}
            item = {
                "name": rec.name,
                "expression": rec.spec.get("expression") or "<script>",
                "hypothesis": rec.hypothesis.get("hypothesis", ""),
                "sharpe": round(float(rec.metrics.get("sharpe") or 0.0), 3),
                "turnover": round(float(rec.metrics.get("turnover") or 0.0), 2),
                "rank_ic": round(float(rec.metrics.get("rank_ic") or 0.0), 4),
                "max_abs_xs_corr": rec.max_abs_xs_corr,
            }
            sub_m = (rec.subuniverse or {}).get("metrics") or {}
            if sub_m:
                item["sub_sharpe"] = round(float(sub_m.get("sharpe") or 0.0), 3)
            if oos:
                item["sharpe_oos"] = round(float(oos.get("sharpe") or 0.0), 3)
            if hold:
                item["sharpe_holdout"] = round(float(hold.get("sharpe") or 0.0), 3)
            out.append(item)
        return out

    # ------------------------------------------------------------------ #
    # correlations
    # ------------------------------------------------------------------ #
    def _pair_corr(
        self, factor: pd.DataFrame, pnl: pd.Series, other: FactorRecord
    ) -> Optional[dict]:
        try:
            other_factor = self.load_factor(other.id)
            other_pnl = self.load_pnl(other.id)
        except FileNotFoundError:
            return None
        xs = M.spearman_over_time(factor, other_factor, min_names=10)
        ts = M.pearson(pnl, other_pnl)
        return {
            "xs_spearman_mean": xs["mean"],
            "xs_spearman_std": xs["std"],
            "xs_n_days": xs["n_days"],
            "pnl_pearson": ts["pearson"],
            "pnl_n_days": ts["n_days"],
        }

    def _append_correlations(self, fid: str, rec: FactorRecord) -> None:
        rows = []
        for item in rec.corr_vs_pool:
            rows.append(
                {
                    "factor_a": fid,
                    "factor_b": item["factor"],
                    "xs_spearman_mean": item["xs_spearman_mean"],
                    "xs_spearman_std": item["xs_spearman_std"],
                    "xs_n_days": item["xs_n_days"],
                    "pnl_pearson": item["pnl_pearson"],
                    "pnl_n_days": item["pnl_n_days"],
                }
            )
        if not rows:
            return
        df = pd.DataFrame(rows)
        if self.corr_path.exists():
            existing = pd.read_csv(self.corr_path)
            existing = existing[
                (existing["factor_a"] != fid) & (existing["factor_b"] != fid)
            ]
            out = pd.concat([existing, df], ignore_index=True)
        else:
            out = df
        out.to_csv(self.corr_path, index=False)

    def recompute_correlations(self) -> pd.DataFrame:
        """Full pairwise refresh; also updates each record's max correlation."""
        ids = list(self._index)
        rows = []
        for i, a in enumerate(ids):
            fa = self.load_factor(a)
            pa = self.load_pnl(a)
            for b in ids[i + 1 :]:
                fb = self.load_factor(b)
                pb = self.load_pnl(b)
                xs = M.spearman_over_time(fa, fb, min_names=10)
                ts = M.pearson(pa, pb)
                rows.append(
                    {
                        "factor_a": a,
                        "factor_b": b,
                        "xs_spearman_mean": xs["mean"],
                        "xs_spearman_std": xs["std"],
                        "xs_n_days": xs["n_days"],
                        "pnl_pearson": ts["pearson"],
                        "pnl_n_days": ts["n_days"],
                    }
                )

        df = pd.DataFrame(rows)
        if not df.empty:
            df.to_csv(self.corr_path, index=False)

        for rec in self._index.values():
            sub = df[(df["factor_a"] == rec.id) | (df["factor_b"] == rec.id)] if not df.empty else df
            if sub.empty:
                rec.max_abs_xs_corr = None
                rec.max_abs_pnl_corr = None
                continue
            xs = sub["xs_spearman_mean"].abs()
            ts = sub["pnl_pearson"].abs()
            if xs.notna().any():
                rec.max_abs_xs_corr = round(float(xs.max()), 4)
            if ts.notna().any():
                rec.max_abs_pnl_corr = round(float(ts.max()), 4)
        self._save_index()
        return df

    def correlations(self) -> pd.DataFrame:
        if not self.corr_path.exists():
            return pd.DataFrame(
                columns=[
                    "factor_a",
                    "factor_b",
                    "xs_spearman_mean",
                    "xs_spearman_std",
                    "xs_n_days",
                    "pnl_pearson",
                    "pnl_n_days",
                ]
            )
        return pd.read_csv(self.corr_path)

    def report(self, top: int = 10) -> str:
        summary = self.summary()
        lines = ["# Factor pool", ""]
        if summary.empty:
            return "# Factor pool\n\n(empty)\n"
        cols = [
            "name",
            "sharpe",
            "ann_return",
            "turnover",
            "max_drawdown",
            "ic",
        ]
        if "sharpe_oos" in summary.columns and summary["sharpe_oos"].notna().any():
            cols.append("sharpe_oos")
        if (
            "sharpe_holdout" in summary.columns
            and summary["sharpe_holdout"].notna().any()
        ):
            cols.append("sharpe_holdout")
        cols += ["max_abs_xs_corr", "max_abs_pnl_corr"]
        lines.append(f"{len(summary)} factors, top {min(top, len(summary))} by Sharpe:\n")
        lines.append(md_table(summary.head(top)[cols]))
        corr = self.correlations()
        if not corr.empty:
            lines.append("\n## Highest cross-sectional correlation pairs\n")
            top_pairs = corr.reindex(
                corr["xs_spearman_mean"].abs().sort_values(ascending=False).index
            ).head(5)
            lines.append(
                md_table(
                    top_pairs[["factor_a", "factor_b", "xs_spearman_mean", "pnl_pearson"]]
                )
            )
        return "\n".join(lines)

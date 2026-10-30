"""Tiny markdown table helper (avoids a tabulate dependency)."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np
import pandas as pd


def _fmt(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, (float, np.floating)):
        if not np.isfinite(value):
            return "-"
        if abs(value) >= 1000:
            return f"{value:,.0f}"
        if abs(value) < 0.001 and value != 0:
            return f"{value:.2e}"
        return f"{value:.4g}"
    if isinstance(value, (np.integer,)):
        return str(int(value))
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def md_table(data, columns: Sequence[str] | None = None) -> str:
    """Render a DataFrame or a list of dicts as a markdown table."""
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        df = pd.DataFrame(list(data))
    if df.empty:
        return "_(empty)_"
    if columns is not None:
        df = df[[c for c in columns if c in df.columns]]
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(str(c) for c in cols) + " |",
        "|" + "|".join(["---"] * len(cols)) + "|",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(_fmt(row[c]) for c in cols) + " |")
    return "\n".join(lines)

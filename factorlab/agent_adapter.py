"""Adapter between the collaborator Agent 1-3 vocabulary and our modules.

Agent 2/3 speak the collaborator's data-contract field names (``Adj_Close``,
``DlyClose`` ...). Agent 4/5 (our backtest/stability and feedback layers) speak
the project panel vocabulary (``close``, ``high`` ...). All translation lives
here so the evaluation modules never need to know about the upstream agent code.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = PROJECT_ROOT / "factorlab" / "agents"


FIELD_MAP: dict[str, str] = {
    "Adj_Open": "open",
    "Adj_High": "high",
    "Adj_Low": "low",
    "Adj_Close": "close",
    "Adj_Volume": "volume",
    "Adj_MktCap": "cap",
    "DlyOpen": "open",
    "DlyHigh": "high",
    "DlyLow": "low",
    "DlyClose": "close",
    "DlyPrc": "close",
    "DlyVol": "volume",
    "DlyCap": "cap",
    "DlyRet": "returns",
    "DlyRetx": "returns",
    "Close": "close",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Volume": "volume",
    "MarketCap": "cap",
    "market_cap": "cap",
    "close": "close",
    "open": "open",
    "high": "high",
    "low": "low",
    "volume": "volume",
    "cap": "cap",
    "returns": "returns",
    "log_returns": "log_returns",
    "amount": "amount",
    "adv20": "adv20",
    "cap_rank": "cap_rank",
    "range": "range",
    "close_position": "close_position",
    "intraday_return": "intraday_return",
    "overnight_return": "overnight_return",
}



_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_FIELD_CALL_RE = re.compile(r'field\(\s*"([^"]+)"\s*\)')


def ensure_agents_importable() -> None:
    """His modules import ``agent1.core`` / ``research.common`` absolutely."""
    if str(AGENTS_ROOT) not in sys.path:
        sys.path.insert(0, str(AGENTS_ROOT))


def translate_expression(expression: str) -> str:
    """Rewrite Agent-3 contract field names into our panel field names."""

    def field_call(match: re.Match) -> str:
        name = match.group(1)
        if name not in FIELD_MAP:
            raise KeyError(f"field {name!r} has no panel mapping")
        return FIELD_MAP[name]

    def identifier(match: re.Match) -> str:
        token = match.group(0)
        return FIELD_MAP.get(token, token)

    rewritten = _FIELD_CALL_RE.sub(field_call, expression)
    return _IDENT_RE.sub(identifier, rewritten)

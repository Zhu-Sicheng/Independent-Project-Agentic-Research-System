"""Global configuration objects for factorlab.

Everything that controls *what gets searched* lives here so that the agents,
the backtester and the grid search all read the same knobs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Sequence

# --------------------------------------------------------------------------- #
# paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "panel"
DEFAULT_POOL_DIR = PROJECT_ROOT / "pool"
DEFAULT_RUNS_DIR = PROJECT_ROOT / "runs"

#: local-only credentials file (see .env.example); never committed
ENV_FILE = PROJECT_ROOT / ".env"


def load_dotenv(path: Path = ENV_FILE) -> None:
    """Minimal ``.env`` loader: ``KEY=VALUE`` lines, no export, no interpolation.

    Existing environment variables win, so an explicit ``$env:FOO`` in the shell
    still overrides the file.  The file itself is gitignored and must never be
    committed (a repository-hygiene test enforces that).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value

# --------------------------------------------------------------------------- #
# research priors
# --------------------------------------------------------------------------- #
#: only economically interpretable horizons are allowed in factor expressions
ALLOWED_WINDOWS: tuple[int, ...] = (5, 20, 60, 120, 240)

#: default grid values for the cross-sectional post-processing knobs
DEFAULT_DECAYS: tuple[int, ...] = (0, 5, 20, 60)
DEFAULT_TRANSFORMS: tuple[str, ...] = ("none", "rank", "sign")
#: ``None`` = keep the full universe, ``0.3`` = drop the smallest 30% by cap rank
DEFAULT_CAP_FILTERS: tuple[Optional[float], ...] = (None, 0.3)


# --------------------------------------------------------------------------- #
# backtest
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class BacktestSettings:
    """One point of the search space.

    Pipeline order (documented once, used everywhere)::

        raw factor
          -> cap filter        if_else(rank(cap) > cap_filter, factor, nan)
          -> cross-section op  none | rank | sign | zscore
          -> time decay        linear decay over `decay` days
          -> neutralization    cross-sectional demean
          -> leverage          sum(|w|) = 1 (dollar neutral, gross = 1)
          -> pnl               w_{t-1} . r_t   (close-to-close, delay = 1 day)

    ``delay`` shifts the *signal*: with the default ``1`` the factor observed
    after the close of day ``t`` earns the return from ``t`` to ``t+1``.
    """

    y: str = "close_to_close"
    delay: int = 1
    decay: int = 0
    transform: str = "none"
    cap_filter: Optional[float] = None
    neutralize: bool = True
    cost_bps: float = 0.0
    ann: int = 252
    min_names: int = 20
    keep_positions: bool = False
    compute_ic: bool = True

    def replace(self, **kwargs) -> "BacktestSettings":
        data = asdict(self)
        data.update(kwargs)
        return BacktestSettings(**data)

    def key(self) -> tuple:
        return (
            self.y,
            self.delay,
            self.decay,
            self.transform,
            self.cap_filter,
            self.neutralize,
            self.cost_bps,
        )


# --------------------------------------------------------------------------- #
# grid search
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class GridConfig:
    decays: Sequence[int] = DEFAULT_DECAYS
    transforms: Sequence[str] = DEFAULT_TRANSFORMS
    cap_filters: Sequence[Optional[float]] = DEFAULT_CAP_FILTERS
    windows: Sequence[int] = ALLOWED_WINDOWS
    objective: str = "sharpe"  # any metric in backtest.metrics
    max_evals: int = 200
    max_window_combos: int = 50
    seed: int = 20240917


# --------------------------------------------------------------------------- #
# LLM
# --------------------------------------------------------------------------- #
@dataclass
class LLMSettings:
    """OpenAI-compatible or Anthropic endpoint; falls back to offline rules."""

    provider: str = "auto"  # auto | openai | anthropic | offline
    model: str = ""
    base_url: str = ""
    api_key_env: str = ""
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 180

    @classmethod
    def from_env(cls) -> "LLMSettings":
        load_dotenv()
        provider = os.getenv("FACTORLAB_LLM_PROVIDER", "auto").lower()
        if provider == "auto":
            if os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            elif os.getenv("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            else:
                provider = "offline"

        if provider == "openai":
            base = os.getenv("FACTORLAB_LLM_BASE_URL") or os.getenv(
                "OPENAI_BASE_URL", "https://api.deepseek.com/v1"
            )
            model = os.getenv("FACTORLAB_LLM_MODEL") or (
                "deepseek-chat" if "deepseek" in base else "gpt-4o-mini"
            )
            key_env = "DEEPSEEK_API_KEY" if "deepseek" in base else "OPENAI_API_KEY"
        elif provider == "anthropic":
            base = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
            model = os.getenv("FACTORLAB_LLM_MODEL") or os.getenv(
                "ANTHROPIC_MODEL", "claude-sonnet-4-20250514"
            )
            key_env = "ANTHROPIC_API_KEY"
        else:
            base, model, key_env = "", "", ""

        return cls(
            provider=provider,
            model=model,
            base_url=base,
            api_key_env=key_env,
            temperature=float(os.getenv("FACTORLAB_LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("FACTORLAB_LLM_MAX_TOKENS", "4000")),
        )

    def api_key(self) -> str:
        return os.getenv(self.api_key_env, "") if self.api_key_env else ""

    def available(self) -> bool:
        return bool(self.provider != "offline" and self.api_key())


# --------------------------------------------------------------------------- #
# out-of-sample split
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SampleSplit:
    """Where to cut the sample into in-sample / out-of-sample / holdout.

    Three segments, all date ranges inclusive:

    * ``is``  — ``[train_start, train_end]``: the only segment the grid search
      may use to *select* a configuration;
    * ``oos`` — ``[test_start, test_end]``: untouched during selection, used to
      check that the in-sample edge survives (validation);
    * ``holdout`` — ``[holdout_start, holdout_end]``: the final untouched
      sample, ideally never looked at until a factor is ready to ship.

    With no values filled in, ``is_configured()`` is False and the whole sample
    is used for selection (no OOS / holdout metrics).  Set the ranges by date,
    or use ``train_frac`` to cut the first part of the dates as in-sample.
    """

    train_start: Optional[str] = None
    train_end: Optional[str] = None
    test_start: Optional[str] = None
    test_end: Optional[str] = None
    train_frac: Optional[float] = None
    holdout_start: Optional[str] = None
    holdout_end: Optional[str] = None

    def is_configured(self) -> bool:
        return any(
            v is not None
            for v in (
                self.train_start,
                self.train_end,
                self.test_start,
                self.test_end,
                self.train_frac,
                self.holdout_start,
                self.holdout_end,
            )
        )

    def describe(self) -> str:
        if not self.is_configured():
            return "not configured (full sample used for selection)"
        if self.train_frac is not None and not (self.holdout_start or self.holdout_end):
            return f"fractional: first {self.train_frac:.0%} of dates are in-sample"
        bits = []
        if self.train_start:
            bits.append(f"IS from {self.train_start}")
        if self.train_end:
            bits.append(f"IS to {self.train_end}")
        if self.test_start:
            bits.append(f"OOS from {self.test_start}")
        if self.test_end:
            bits.append(f"OOS to {self.test_end}")
        if self.holdout_start:
            bits.append(f"holdout from {self.holdout_start}")
        if self.holdout_end:
            bits.append(f"holdout to {self.holdout_end}")
        return "date-based: " + ", ".join(bits)


#: the convention used for the US equity panel in this project
US_EQUITY_SPLIT = SampleSplit(
    train_end="2020-12-31",
    test_start="2021-01-01",
    test_end="2024-12-31",
    holdout_start="2025-01-01",
)


# --------------------------------------------------------------------------- #
# mining loop
# --------------------------------------------------------------------------- #
@dataclass
class MiningConfig:
    n_hypotheses: int = 3
    max_rounds: int = 2
    max_abandon_ratio: float = 0.7
    grid: GridConfig = field(default_factory=GridConfig)
    backtest: BacktestSettings = field(default_factory=BacktestSettings)
    split: Optional[SampleSplit] = None
    llm: LLMSettings = field(default_factory=LLMSettings.from_env)
    seed: int = 7


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def project_path(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)

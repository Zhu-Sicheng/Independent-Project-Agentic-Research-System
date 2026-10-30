"""Rule-based researcher used when no LLM key is configured.

It is deliberately a *real* researcher, not a stub: it proposes economically
motivated hypotheses with concrete expressions, can emit a per-day python
script, and reviews results against the same criteria the LLM prompt asks for.
This keeps the pipeline runnable and testable end to end.
"""

from __future__ import annotations

import math
from typing import Optional

# --------------------------------------------------------------------------- #
# hypotheses
# --------------------------------------------------------------------------- #
HYPOTHESES: list[dict] = [
    {
        "name": "short_term_reversal",
        "economic_rationale": (
            "Liquidity providers demand compensation for absorbing uninformed "
            "order flow. When a stock sells off for several days, the price "
            "temporarily overshoots and partially reverts."
        ),
        "hypothesis": (
            "Stocks whose 5-day return is in the bottom cross-sectional decile "
            "outperform those in the top decile over the next week."
        ),
        "factor_description": (
            "Negative of the trailing 5-day average return, ranked "
            "cross-sectionally: -rank(ts_mean(returns, 5))."
        ),
        "data_fields": ["close", "returns"],
        "horizon_days": 5,
        "expected_sign": "positive",
        "testable_prediction": (
            "Cross-sectional IC of the factor with next-week returns is "
            "positive, and the effect is concentrated in the first few days."
        ),
        "novelty": "Baseline reversal factor; reference point for the pool.",
        "template_expression": "-ts_mean(returns, 5)",
    },
    {
        "name": "low_volatility_anomaly",
        "economic_rationale": (
            "Leverage-constrained investors and lottery-seeking behaviour bid up "
            "high-volatility names, so low-volatility stocks earn a premium per "
            "unit of risk."
        ),
        "hypothesis": (
            "Stocks with low 20-day realised volatility outperform high-volatility "
            "stocks on a risk-adjusted basis over the following month."
        ),
        "factor_description": (
            "Negative trailing 20-day return volatility, cross-sectionally ranked: "
            "-rank(ts_std(returns, 20))."
        ),
        "data_fields": ["close", "returns"],
        "horizon_days": 20,
        "expected_sign": "positive",
        "testable_prediction": "Positive IC, low turnover, better Sharpe than reversal.",
        "novelty": "Classic low-vol premium, orthogonal to short-term reversal.",
        "template_expression": "-ts_std(returns, 20)",
    },
    {
        "name": "amihud_illiquidity_premium",
        "economic_rationale": (
            "Illiquid stocks must offer a return premium because trading them "
            "imposes price impact costs on the holder."
        ),
        "hypothesis": (
            "Stocks with high average |return| per unit of dollar volume "
            "(Amihud illiquidity) earn higher subsequent returns."
        ),
        "factor_description": (
            "Amihud illiquidity over 20 days: ts_mean(abs(returns) / amount, 20), "
            "ranked cross-sectionally."
        ),
        "data_fields": ["close", "returns", "amount"],
        "horizon_days": 20,
        "expected_sign": "positive",
        "testable_prediction": (
            "Positive IC concentrated in small caps; should weaken after the "
            "cap filter drops the bottom 30%."
        ),
        "novelty": "Liquidity premium; uses turnover value, not just price.",
        "template_expression": "-ts_mean(abs(returns) / amount, 20)",
    },
    {
        "name": "volume_shock_reversal",
        "economic_rationale": (
            "Abnormally high volume without a commensurate price move signals "
            "distribution by informed sellers; the price later drifts down."
        ),
        "hypothesis": (
            "Stocks with an abnormal 5-day volume spike underperform over the "
            "next week, controlling for their recent return."
        ),
        "factor_description": (
            "Negative 5-day average of relative volume "
            "(volume / 20-day average volume - 1)."
        ),
        "data_fields": ["volume"],
        "horizon_days": 5,
        "expected_sign": "positive",
        "testable_prediction": "Positive IC; high turnover because volume is noisy.",
        "novelty": "Uses the volume dimension rather than price.",
        "template_expression": "-ts_mean(volume / ts_mean(volume, 20) - 1, 5)",
    },
    {
        "name": "volume_weighted_reversal",
        "economic_rationale": (
            "Reversal should be strongest where the price move happened on heavy "
            "volume, because that is where the order-flow imbalance was largest."
        ),
        "hypothesis": (
            "A volume-weighted 5-day reversal signal outperforms the plain 5-day "
            "reversal factor."
        ),
        "factor_description": (
            "Negative volume-weighted average of daily returns over the last 5 "
            "days, implemented as a per-day python script with a tunable window."
        ),
        "data_fields": ["close", "returns", "volume"],
        "horizon_days": 5,
        "expected_sign": "positive",
        "testable_prediction": "Positive IC and higher Sharpe than plain reversal.",
        "novelty": "Same signal, smarter weighting; exercises the script path.",
        "template_expression": None,
        "template_script": (
            "def generate(panel, params):\n"
            "    window = int(params.get('window', 5))\n"
            "    r = panel.field('returns')\n"
            "    v = panel.field('volume')\n"
            "    rel = v / v.rolling(20, min_periods=10).mean()\n"
            "    num = (r * rel).rolling(window, min_periods=max(2, window // 2)).sum()\n"
            "    den = rel.rolling(window, min_periods=max(2, window // 2)).sum()\n"
            "    return -(num / den)\n"
        ),
        "template_params": {"window": 5},
        "template_param_grid": {"window": [5, 20, 60]},
    },
    {
        "name": "overnight_gap_reversal",
        "economic_rationale": (
            "Overnight moves are driven by retail order flow and liquidity "
            "withdrawal; they tend to revert during the following session."
        ),
        "hypothesis": (
            "Stocks that gap up at the open underperform during the rest of the "
            "day, and vice versa."
        ),
        "factor_description": "Negative overnight gap: -(open / delay(close, 1) - 1).",
        "data_fields": ["open", "close"],
        "horizon_days": 1,
        "expected_sign": "positive",
        "testable_prediction": "Positive IC at a one-day horizon; very high turnover.",
        "novelty": "Intraday/overnight split, new information for the pool.",
        "template_expression": "-(open / delay(close, 1) - 1)",
    },
    {
        "name": "range_compression_breakout",
        "economic_rationale": (
            "A compressed high-low range reflects low disagreement and position "
            "building; volatility tends to expand afterwards with a directional "
            "drift."
        ),
        "hypothesis": (
            "Stocks whose 20-day high-low range is unusually narrow relative to "
            "their own history outperform."
        ),
        "factor_description": (
            "Negative 20-day average of (high - low) / close, ranked "
            "cross-sectionally."
        ),
        "data_fields": ["high", "low", "close"],
        "horizon_days": 20,
        "expected_sign": "positive",
        "testable_prediction": "Weak positive IC; likely rejected.",
        "novelty": "Uses intraday range, not close-to-close returns.",
        "template_expression": "-ts_mean((high - low) / close, 20)",
    },
    {
        "name": "price_volume_divergence",
        "economic_rationale": (
            "When price rises on falling volume the move lacks conviction and "
            "is more likely to reverse."
        ),
        "hypothesis": (
            "Stocks with a high 20-day correlation between price and volume "
            "underperform stocks with a low correlation."
        ),
        "factor_description": "Negative 20-day correlation of close and volume.",
        "data_fields": ["close", "volume"],
        "horizon_days": 20,
        "expected_sign": "positive",
        "testable_prediction": "Positive IC and low turnover.",
        "novelty": "Second-moment (co-movement) signal rather than a level.",
        "template_expression": "-ts_corr(close, volume, 20)",
    },
]


ORDER = [
    "short_term_reversal",
    "low_volatility_anomaly",
    "volume_weighted_reversal",
    "amihud_illiquidity_premium",
    "volume_shock_reversal",
    "overnight_gap_reversal",
    "range_compression_breakout",
    "price_volume_divergence",
]


def offline_hypotheses(n: int = 3, exclude: Optional[list[str]] = None) -> list[dict]:
    exclude = set(exclude or [])
    by_name = {h["name"]: h for h in HYPOTHESES}
    ordered = [by_name[name] for name in ORDER if name in by_name]
    picked = [h for h in ordered if h["name"] not in exclude][:n]
    return [dict(h) for h in picked]


# --------------------------------------------------------------------------- #
# translation
# --------------------------------------------------------------------------- #
KEYWORDS: list[tuple[tuple[str, ...], str]] = [
    (("reversal", "revert", "overreact"), "-ts_mean(returns, 5)"),
    (("momentum", "trend", "continuation"), "ts_returns(close, 20)"),
    (("volatil", "vol", "risk"), "-ts_std(returns, 20)"),
    (("illiq", "liquidity", "amihud", "impact"), "-ts_mean(abs(returns) / amount, 20)"),
    (("volume", "turnover", "shock"), "-ts_mean(volume / ts_mean(volume, 20) - 1, 5)"),
    (("gap", "overnight", "open"), "-(open / delay(close, 1) - 1)"),
    (("range", "high", "low", "breakout"), "-ts_mean((high - low) / close, 20)"),
    (("corr", "divergence", "co-movement"), "-ts_corr(close, volume, 20)"),
    (("size", "cap", "small"), "-rank(cap)"),
]


def template_spec(hypothesis: dict) -> dict:
    if hypothesis.get("template_script"):
        return {
            "kind": "script",
            "script": hypothesis["template_script"],
            "params": dict(hypothesis.get("template_params") or {}),
            "param_grid": dict(hypothesis.get("template_param_grid") or {}),
            "explanation": hypothesis.get("factor_description", ""),
            "name": hypothesis.get("name", ""),
        }
    if hypothesis.get("template_expression"):
        return {
            "kind": "expression",
            "expression": hypothesis["template_expression"],
            "explanation": hypothesis.get("factor_description", ""),
            "name": hypothesis.get("name", ""),
        }
    blob = " ".join(
        str(hypothesis.get(k, "")) for k in ("name", "factor_description", "hypothesis")
    ).lower()
    for keys, expr in KEYWORDS:
        if any(k in blob for k in keys):
            return {
                "kind": "expression",
                "expression": expr,
                "explanation": hypothesis.get("factor_description", ""),
                "name": hypothesis.get("name", ""),
            }
    return {
        "kind": "expression",
        "expression": "-ts_mean(returns, 5)",
        "explanation": "fallback: short-term reversal",
        "name": hypothesis.get("name", ""),
    }


# --------------------------------------------------------------------------- #
# critic
# --------------------------------------------------------------------------- #
def review(
    hypothesis: dict,
    spec: dict,
    summary: dict,
    yearly: list[dict],
    history: list[dict],
    max_rounds: int = 2,
) -> dict:
    best = summary.get("best", {})
    sharpe = float(best.get("sharpe") or 0.0)
    turnover = float(best.get("turnover") or 0.0)
    maxdd = float(best.get("max_drawdown") or 0.0)
    ic = float(best.get("ic") or 0.0)
    expected = hypothesis.get("expected_sign", "positive")
    years = [y for y in yearly if y.get("n_days", 0) > 40]
    pos_years = (
        sum(1 for y in years if float(y.get("total_return") or 0.0) > 0) / len(years)
        if years
        else 0.0
    )
    attempts = len(history) + 1
    can_optimize = attempts < max_rounds

    # the final, untouched segment is the strongest evidence available
    holdout = summary.get("holdout") or {}
    oos = summary.get("out_of_sample") or {}
    final = holdout if isinstance(holdout, dict) and holdout.get("sharpe") is not None else oos
    final_sharpe = final.get("sharpe") if isinstance(final, dict) else None
    final_name = "holdout" if final is holdout else "out-of-sample"
    stability_ok = True
    if (
        final_sharpe is not None
        and isinstance(final_sharpe, (int, float))
        and math.isfinite(final_sharpe)
    ):
        # giving back more than ~60% of the in-sample edge is overfitting
        stability_ok = final_sharpe > 0 and (sharpe <= 0 or final_sharpe >= 0.4 * sharpe)
    has_final = final_sharpe is not None and isinstance(final_sharpe, (int, float))

    contradicting_sign = (expected == "positive" and ic < -0.005) or (
        expected == "negative" and ic > 0.005
    )

    if not stability_ok:
        decision = "abandon"
        reasoning = (
            f"In-sample Sharpe {sharpe:.2f} does not survive the {final_name} "
            f"(Sharpe {final_sharpe:.2f}). The configuration is selected on "
            "noise; abandon."
        )
    elif sharpe >= 1.0 and pos_years >= 0.65 and maxdd > -0.35:
        decision = "accept"
        reasoning = (
            f"Sharpe {sharpe:.2f} with {pos_years:.0%} positive years and max "
            f"drawdown {maxdd:.1%}; consistent with the stated hypothesis "
            f"(IC {ic:.3f}, expected {expected})."
        )
        if has_final and stability_ok:
            reasoning += f" {final_name.title()} confirms with Sharpe {final_sharpe:.2f}."
    elif sharpe >= 0.35 and not contradicting_sign and can_optimize:
        decision = "optimize"
        reasoning = (
            f"Sharpe {sharpe:.2f} is not investable yet but the signal has the "
            f"hypothesised sign (IC {ic:.3f}); try to stabilise it."
        )
    elif contradicting_sign and can_optimize:
        decision = "optimize"
        reasoning = (
            f"Realised IC {ic:.3f} contradicts the hypothesised {expected} sign; "
            "either the mechanism or the implementation is wrong."
        )
    else:
        decision = "abandon"
        reasoning = (
            f"Sharpe {sharpe:.2f}, IC {ic:.3f}, {pos_years:.0%} positive years: "
            "no evidence the hypothesised mechanism is priced."
        )

    revised = None
    suggestions: list[str] = []
    if decision == "optimize":
        expr = spec.get("expression", "")
        kind = spec.get("kind", "expression")
        if contradicting_sign and kind == "expression" and not expr.strip().startswith("-1 *"):
            revised = dict(spec)
            revised["expression"] = f"-1 * ({expr})"
            revised["explanation"] = "flip the sign implied by the realised IC"
            suggestions.append("flip the factor sign")
        elif turnover > 30 and kind == "expression":
            revised = dict(spec)
            revised["expression"] = f"ts_mean(({expr}), 20)"
            revised["explanation"] = "smooth the signal to cut turnover"
            suggestions.append("smooth with a 20-day mean")
        if revised is None:
            decision = "abandon"
            reasoning = (
                f"Sharpe {sharpe:.2f}, IC {ic:.3f}: below the accept bar, and no "
                "structural change remains that the grid search has not already "
                "covered. Abandon."
            )

    return {
        "decision": decision,
        "confidence": 0.6,
        "reasoning": reasoning,
        "diagnosis": _diagnose(sharpe, turnover, ic, maxdd),
        "hypothesis_supported": decision == "accept",
        "suggested_changes": suggestions,
        "revised": revised,
        "source": "offline-rules",
    }


def _diagnose(sharpe: float, turnover: float, ic: float, maxdd: float) -> str:
    parts = []
    if turnover > 50:
        parts.append("turnover is very high, costs will dominate")
    if abs(ic) < 0.005:
        parts.append("the signal has almost no cross-sectional information")
    if maxdd < -0.2:
        parts.append("the drawdown is large relative to the return")
    if sharpe < 0:
        parts.append("the sign of the effect is wrong")
    return "; ".join(parts) or "performance is internally consistent"

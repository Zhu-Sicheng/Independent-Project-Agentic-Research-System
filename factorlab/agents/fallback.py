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
        "template_expression": "-ts_std_dev(returns, 20)",
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
        "factor_description": (
            "Negative overnight gap, using the previous close reconstructed from "
            "ts_delta: -(open / (close - ts_delta(close, 1)) - 1)."
        ),
        "data_fields": ["open", "close"],
        "horizon_days": 1,
        "expected_sign": "positive",
        "testable_prediction": "Positive IC at a one-day horizon; very high turnover.",
        "novelty": "Intraday/overnight split, new information for the pool.",
        "template_expression": "-(open / (close - ts_delta(close, 1)) - 1)",
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
        "factor_description": (
            "Price-volume divergence proxied without ts_corr: the 20-day rank of "
            "the 5-day return times the 20-day rank of relative volume, negated."
        ),
        "data_fields": ["close", "volume"],
        "horizon_days": 20,
        "expected_sign": "positive",
        "testable_prediction": "Positive IC and low turnover.",
        "novelty": "Second-moment (co-movement) signal rather than a level.",
        "template_expression": "-ts_rank(ts_returns(close, 5), 20) * ts_rank(volume / ts_mean(volume, 20), 20)",
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
    (("volatil", "vol", "risk"), "-ts_std_dev(returns, 20)"),
    (("illiq", "liquidity", "amihud", "impact"), "-ts_mean(abs(returns) / amount, 20)"),
    (("volume", "turnover", "shock"), "-ts_mean(volume / ts_mean(volume, 20) - 1, 5)"),
    (("gap", "overnight", "open"), "-(open / (close - ts_delta(close, 1)) - 1)"),
    (("range", "high", "low", "breakout"), "-ts_mean((high - low) / close, 20)"),
    (
        ("corr", "divergence", "co-movement"),
        "-ts_rank(ts_returns(close, 5), 20) * ts_rank(volume / ts_mean(volume, 20), 20)",
    ),
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
    # with a holdout split the decision must be made on the selection segment;
    # the full-sample numbers include data that was never allowed to select on
    primary = summary.get("in_sample") or best
    sharpe = float(primary.get("sharpe") or 0.0)
    turnover = float(primary.get("turnover") or 0.0)
    maxdd = float(primary.get("max_drawdown") or 0.0)
    ic = float(primary.get("ic") or 0.0)
    expected = hypothesis.get("expected_sign", "positive")
    years = [y for y in yearly if y.get("n_days", 0) > 40]
    pos_years = (
        sum(1 for y in years if float(y.get("total_return") or 0.0) > 0) / len(years)
        if years
        else 0.0
    )
    is_yearly = primary.get("yearly") if isinstance(primary, dict) else None
    if is_yearly:
        years = [y for y in is_yearly if y.get("n_days", 0) > 40]
        pos_years = (
            sum(1 for y in years if float(y.get("total_return") or 0.0) > 0) / len(years)
            if years
            else pos_years
        )
    attempts = len(history) + 1
    can_optimize = attempts < max_rounds

    # every untouched segment is evidence: validation (2021-2024) and the final
    # holdout (2025+). A factor must survive both, not just the last one.
    holdout = summary.get("holdout") or {}
    oos = summary.get("out_of_sample") or {}
    final_pairs = [
        (name, float(m["sharpe"]))
        for name, m in (("out-of-sample", oos), ("holdout", holdout))
        if isinstance(m, dict)
        and m.get("sharpe") is not None
        and isinstance(m["sharpe"], (int, float))
        and math.isfinite(m["sharpe"])
    ]
    final_sharpes = [v for _, v in final_pairs]
    stability_ok = True
    if final_sharpes:
        # giving back more than ~60% of the in-sample edge is overfitting
        stability_ok = min(final_sharpes) > 0 and (
            sharpe <= 0 or sum(final_sharpes) / len(final_sharpes) >= 0.4 * sharpe
        )
    has_final = bool(final_pairs)
    final_text = ", ".join(f"{name} {value:.2f}" for name, value in final_pairs)

    contradicting_sign = (expected == "positive" and ic < -0.005) or (
        expected == "negative" and ic > 0.005
    )

    if not stability_ok:
        decision = "abandon"
        reasoning = (
            f"In-sample Sharpe {sharpe:.2f} does not survive the untouched "
            f"segments ({final_text}). The configuration is selected on noise; "
            "abandon."
        )
    elif sharpe >= 1.0 and pos_years >= 0.65 and maxdd > -0.35:
        decision = "accept"
        reasoning = (
            f"Sharpe {sharpe:.2f} with {pos_years:.0%} positive years and max "
            f"drawdown {maxdd:.1%}; consistent with the stated hypothesis "
            f"(IC {ic:.3f}, expected {expected})."
        )
        if has_final and stability_ok:
            reasoning += f" Untouched segments: {final_text}."
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

    # robustness battery (optional): a fragile factor cannot be accepted
    stability = summary.get("stability") or {}
    flags = list(stability.get("flags") or [])
    if flags:
        note = (
            f" Stability checks flag {', '.join(flags)}: "
            f"sub-universe Sharpe {stability.get('subuniverse_sharpe', float('nan')):.2f} "
            f"vs {sharpe:.2f}, lowest variant pnl correlation "
            f"{stability.get('min_pnl_corr', float('nan')):.2f}."
        )
        reasoning += note
        if decision == "accept":
            if "subuniverse_flips_sign" in flags or "variant_pnl_decorrelates" in flags:
                decision = "abandon"
                reasoning += " The edge does not survive the robustness battery."
            else:
                decision = "optimize" if can_optimize else "abandon"
                reasoning += " It only survives one configuration; stabilise it before accepting."

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

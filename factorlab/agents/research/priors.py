"""Explicit offline hypotheses and their matching expression templates, not discoveries."""

from __future__ import annotations

FAMILIES = [
    {"family": "short_term_reversal", "title": "短期上涨与价格偏离后的反转", "roles": ["close"], "direction": "negative", "horizon": 5, "windows": [5, 20],
     "concept": "近期累计上涨幅度或价格高于自身近期常态的程度",
     "mechanism": "短期价格偏离可能包含暂时交易压力；提出随后数日向常态回归的可检验假设。",
     "failure": "持续信息冲击、强趋势和交易成本可能使反转假设失效。", "operators": ["ts_returns", "ts_zscore"]},
    {"family": "medium_term_momentum", "title": "中期价格趋势延续", "roles": ["close"], "direction": "positive", "horizon": 20, "windows": [60, 120],
     "concept": "过去数月的累计上涨和中期趋势强度", "mechanism": "提出信息缓慢扩散或持续需求可能使中期价格趋势继续的假设。",
     "failure": "趋势反转、拥挤和短期回撤可能抵消延续效应。", "operators": ["ts_returns"]},
    {"family": "low_realized_volatility", "title": "近期低波动与后续收益", "roles": ["close"], "direction": "negative", "horizon": 20, "windows": [20, 60],
     "concept": "过去数周日收益的波动或绝对变动水平", "mechanism": "提出近期较平稳的价格过程可能伴随更稳定的后续表现的假设，等待风险调整和收益检验。",
     "failure": "低波动可能只是低活跃或滞后报价；高波动也可能承载有利的新信息。", "operators": ["ts_returns", "ts_std_dev", "ts_mean"]},
    {"family": "volume_price_confirmation", "title": "成交活跃程度对近期趋势的确认", "roles": ["close", "volume"], "direction": "positive", "horizon": 5, "windows": [5, 20],
     "concept": "被相对自身常态更高成交量确认的近期价格上涨", "mechanism": "提出伴随成交参与扩大的近期价格变化可能比低参与变化更有延续性的假设。",
     "failure": "放量可能来自派发、恐慌或公司行动；未经确认的成交量复权可能制造虚假变化。", "operators": ["ts_returns", "ts_mean"]},
    {"family": "intraday_pressure", "title": "日内买入压力的短期延续", "roles": ["open", "close"], "direction": "positive", "horizon": 1, "windows": [1, 5],
     "concept": "收盘相对开盘的上涨强度及其近期平均水平", "mechanism": "提出日内净买入压力可能延续到下一可执行交易时点之后的假设。",
     "failure": "隔夜信息、开收盘微观结构和短期反转可能抵消日内压力。", "operators": ["ts_mean"]},
    {"family": "range_expansion_risk", "title": "近期日内振幅扩大与收益压力", "roles": ["high", "low", "close"], "direction": "negative", "horizon": 5, "windows": [20, 60],
     "concept": "相对于价格水平的日内高低振幅的近期平均或平滑水平", "mechanism": "提出持续较大振幅可能反映不确定性和交易压力，并对随后短期收益产生压力的假设。",
     "failure": "振幅可能是有利价格发现或风险补偿；高低价口径不一致时该概念不成立。", "operators": ["ts_mean", "ts_ema"]},
    {"family": "size_premium", "title": "证券规模与后续收益差异", "roles": ["cap"], "direction": "negative", "horizon": 20, "windows": [1, 20],
     "concept": "当前或平滑后的证券市值规模", "mechanism": "提出较小规模证券可能因风险或融资约束呈现不同后续收益的横截面假设。",
     "failure": "流动性、退市样本、规模口径和行业暴露可能解释或抵消观察结果。", "operators": ["ts_mean"]},
]

ROLE_ALIASES = {
    "close": ("Adj_Close", "Close", "close", "DlyClose", "DlyPrc"),
    "open": ("Adj_Open", "Open", "open", "DlyOpen"),
    "high": ("Adj_High", "High", "high", "DlyHigh"),
    "low": ("Adj_Low", "Low", "low", "DlyLow"),
    "volume": ("Adj_Volume", "Volume", "volume", "DlyVol"),
    "cap": ("Adj_MktCap", "market_cap", "MarketCap", "DlyCap"),
}


def role_fields(fields: dict) -> dict:
    return {role: next((name for name in names if name in fields), None) for role, names in ROLE_ALIASES.items()}


def expression_templates(idea: dict) -> list[tuple[str, str]]:
    prior = next((item for item in FAMILIES if item["family"] == idea["family"]), None)
    if prior and idea["expected_return_direction"] != prior["direction"]:
        raise ValueError("Idea direction contradicts this offline template; use an explicitly aligned implementation")
    mapping = role_fields({name: {} for name in idea["required_fields"]})
    def field(role):
        import json
        name = mapping.get(role)
        if name is None:
            raise ValueError("Offline family does not match required fields; use the LLM implementation path")
        return name if name.isidentifier() and not name.startswith("_") else "field(" + json.dumps(name, ensure_ascii=False) + ")"
    family = idea["family"]
    if family == "short_term_reversal":
        c = field("close")
        return [(f"-ts_returns({c}, 5)", "对近期累计上涨取负，使更强反转预期对应更高因子值。"),
                (f"-ts_zscore({c}, 20)", "对价格相对自身近期常态的偏离取负；这是另一种反转概念的测量。")]
    if family == "medium_term_momentum":
        c = field("close")
        return [(f"ts_returns({c}, 60)", "过去约三个月上涨越强，因子值越高。"),
                (f"ts_returns({c}, 120)", "以更长中期窗口测量相同趋势假设；这是参数变体，不是新的经济机制。")]
    if family == "low_realized_volatility":
        c = field("close")
        return [(f"-ts_std_dev(ts_returns({c}, 1), 20)", "对近期收益波动取负，低波动对应更高因子值。"),
                (f"-ts_mean(abs(ts_returns({c}, 1)), 20)", "以平均绝对日变动替代标准差，并维持低波动方向。")]
    if family == "volume_price_confirmation":
        c, v = field("close"), field("volume")
        return [(f"ts_returns({c}, 5) * ({v} / ts_mean({v}, 20))", "用相对成交活跃程度加权近期价格变化，保持上涨确认方向。"),
                (f"ts_returns({c}, 5) * (ts_mean({v}, 5) / ts_mean({v}, 20))", "先平滑成交参与，再加权近期价格变化。")]
    if family == "intraday_pressure":
        o, c = field("open"), field("close")
        return [(f"({c} - {o}) / {o}", "收盘相对开盘的上涨越强，因子值越高。"),
                (f"ts_mean(({c} - {o}) / {o}, 5)", "对日内压力作近期平均，仍使用开盘和收盘两个必要输入。")]
    if family == "range_expansion_risk":
        h, l, c = field("high"), field("low"), field("close")
        return [(f"-ts_mean(({h} - {l}) / {c}, 20)", "对相对振幅取负并平滑；较小持续振幅对应更高因子值。"),
                (f"-ts_ema(({h} - {l}) / {c}, 20)", "以递归平滑测量同一概念，记录 EMA 的无限历史依赖。")]
    if family == "size_premium":
        c = field("cap")
        return [(f"-{c}", "对规模取负；后续仍需股票池、规模暴露和横截面处理。"),
                (f"-ts_mean({c}, 20)", "用平滑市值减弱单日规模变动，方向保持为偏向较小规模。")]
    return []

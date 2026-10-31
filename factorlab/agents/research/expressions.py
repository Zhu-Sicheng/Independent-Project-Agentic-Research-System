"""Whitelist AST compiler/interpreter: no eval, exec, imports, attributes or indexing."""

from __future__ import annotations

import ast
import dataclasses
import json
import math

import pandas as pd

from agent1.core import is_forward_label
from .common import ExpressionConfig, digest
from .operators import OperatorRegistry, safe_div


@dataclasses.dataclass
class NodeInfo:
    canonical: str
    fields: set[str]
    operators: set[str]
    dimension: dict[str, int]
    warmup: int
    finite_lookback: int | None
    is_series: bool


def combine_units(left: dict, right: dict, sign: int) -> dict:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, 0) + sign * value
    return {key: value for key, value in result.items() if value}


class CompiledExpression:
    def __init__(self, tree, info, registry, metadata):
        self.tree, self.info, self.registry, self.metadata = tree, info, registry, metadata

    def evaluate(self, fields: dict[str, pd.DataFrame]) -> pd.DataFrame:
        def visit(node):
            if isinstance(node, ast.Name):
                return fields[node.id]
            if isinstance(node, ast.Constant):
                return node.value
            if isinstance(node, ast.UnaryOp):
                value = visit(node.operand)
                return -value if isinstance(node.op, ast.USub) else value
            if isinstance(node, ast.BinOp):
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                if isinstance(node.op, ast.Sub):
                    return left - right
                if isinstance(node.op, ast.Mult):
                    return left * right
                return safe_div(left, right)
            if isinstance(node, ast.Call):
                name = node.func.id
                if name == "field":
                    return fields[node.args[0].value]
                if name == "abs":
                    return abs(visit(node.args[0]))
                if name == "safe_div":
                    return safe_div(visit(node.args[0]), visit(node.args[1]))
                spec, arguments = self.registry.bind(node)
                return self.registry.apply(spec.name, [visit(argument) for argument in arguments])
            raise ValueError("Unexpected node in previously validated expression")
        result = visit(self.tree.body)
        if not isinstance(result, pd.DataFrame):
            raise ValueError("Expression did not produce a date-by-entity matrix")
        return result


class ExpressionCompiler:
    def __init__(self, registry: OperatorRegistry, config: ExpressionConfig):
        self.registry, self.config = registry, config

    def compile(self, expression: str, available_fields: dict, allowed_fields: list[str] | None = None) -> CompiledExpression:
        if not isinstance(expression, str) or not 1 <= len(expression) <= 1200:
            raise ValueError("Expression must contain 1..1200 characters")
        try:
            tree = ast.parse(expression.strip(), mode="eval")
        except (SyntaxError, RecursionError) as error:
            raise ValueError(f"Invalid expression syntax: {error}") from None
        nodes = list(ast.walk(tree))
        def depth(node):
            children = list(ast.iter_child_nodes(node))
            return 1 + max((depth(child) for child in children), default=0)
        if len(nodes) > self.config.max_nodes or depth(tree) > self.config.max_depth:
            raise ValueError("Expression exceeds node/depth budget")
        allowed = set(allowed_fields if allowed_fields is not None else available_fields)

        def field_info(name):
            if name not in available_fields or name not in allowed or name.startswith("__") or is_forward_label(name):
                raise ValueError(f"Field {name!r} is unknown, prohibited, or not part of this idea")
            field = available_fields[name]
            if field["factor_usage"] not in {"eligible", "candidate_requires_confirmation"}:
                raise ValueError(f"Field {name!r} is not a direct numerical candidate")
            role = field["semantic_role"]
            unit = role if role in {"price", "volume", "market_cap"} else "unconfirmed_" + name
            canonical = name if name.isidentifier() and not name.startswith("_") else "field(" + json.dumps(name, ensure_ascii=False) + ")"
            return NodeInfo(canonical, {name}, set(), {unit: 1}, 1, 1, True)

        def literal(node):
            sign = 1
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                sign = -1 if isinstance(node.op, ast.USub) else 1
                node = node.operand
            if not isinstance(node, ast.Constant) or isinstance(node.value, bool) or not isinstance(node.value, (int, float)) or not math.isfinite(node.value):
                raise ValueError("Parameters and constants must be finite numeric literals")
            value = sign * node.value
            if abs(value) > 10000:
                raise ValueError("Numeric literal exceeds magnitude budget")
            return value

        def visit(node):
            if isinstance(node, ast.Name):
                return field_info(node.id)
            if isinstance(node, ast.Constant):
                value = literal(node)
                return NodeInfo(repr(value), set(), set(), {}, 0, 0, False)
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                child = visit(node.operand)
                canonical = child.canonical if isinstance(node.op, ast.UAdd) else "-(" + child.canonical + ")"
                return dataclasses.replace(child, canonical=canonical)
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, (ast.Add, ast.Sub)):
                    if left.dimension != right.dimension:
                        raise ValueError("Addition/subtraction requires matching symbolic dimensions")
                    dimension = left.dimension
                else:
                    dimension = combine_units(left.dimension, right.dimension, 1 if isinstance(node.op, ast.Mult) else -1)
                symbol = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}[type(node.op)]
                parts = [left.canonical, right.canonical]
                if isinstance(node.op, (ast.Add, ast.Mult)):
                    parts.sort()
                finite = None if left.finite_lookback is None or right.finite_lookback is None else max(left.finite_lookback, right.finite_lookback)
                return NodeInfo("(" + parts[0] + symbol + parts[1] + ")", left.fields | right.fields, left.operators | right.operators,
                                dimension, max(left.warmup, right.warmup), finite, left.is_series or right.is_series)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                name = node.func.id
                if name == "field":
                    if node.keywords or len(node.args) != 1 or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                        raise ValueError("field() requires exactly one literal column-name string")
                    return field_info(node.args[0].value)
                if name in {"safe_div", "abs"}:
                    count = 2 if name == "safe_div" else 1
                    if node.keywords or len(node.args) != count:
                        raise ValueError(f"{name} requires {count} positional arguments")
                    left = visit(node.args[0])
                    if name == "abs":
                        return dataclasses.replace(left, canonical=f"abs({left.canonical})", operators=left.operators | {"abs"})
                    right = visit(node.args[1])
                    finite = None if left.finite_lookback is None or right.finite_lookback is None else max(left.finite_lookback, right.finite_lookback)
                    return NodeInfo(f"({left.canonical}/{right.canonical})", left.fields | right.fields, left.operators | right.operators | {"safe_div"},
                        combine_units(left.dimension, right.dimension, -1), max(left.warmup, right.warmup), finite, left.is_series or right.is_series)
                spec, arguments = self.registry.bind(node)
                child = visit(arguments[0])
                if not child.is_series:
                    raise ValueError("Time-series operators require a numerical series input")
                values = [literal(argument) for argument in arguments[1:]]
                window = values[0]
                if isinstance(window, bool) or not isinstance(window, int) or not spec.minimum_window <= window <= self.config.max_window:
                    raise ValueError(f"{name} window must be an integer in [{spec.minimum_window}, {self.config.max_window}]")
                for parameter, value in zip(spec.parameters[2:], values[1:]):
                    if parameter in {"percentage", "f"} and not 0 <= value <= 1:
                        raise ValueError(f"{parameter} must be in [0, 1]")
                    if parameter == "mode" and (not isinstance(value, int) or value not in {0, 1}):
                        raise ValueError("mode must be integer 0 or 1")
                    if parameter == "k" and not 0 < value <= 10:
                        raise ValueError("k must be in (0, 10]")
                added = window if spec.shift_based else window - 1
                warmup = child.warmup + added
                finite = None if child.finite_lookback is None or spec.recursive else child.finite_lookback + added
                return NodeInfo(name + "(" + ", ".join([child.canonical] + [repr(value) for value in values]) + ")",
                    child.fields, child.operators | {name}, {} if spec.dimensionless else child.dimension, warmup, finite, True)
            raise ValueError(f"Unsupported AST node: {type(node).__name__}")

        info = visit(tree.body)
        if not info.fields or not info.is_series:
            raise ValueError("A factor expression must depend on permitted data fields")
        if info.warmup + self.config.execution_lag > self.config.max_warmup_rows:
            raise ValueError("Combined warmup and execution lag exceed history budget")
        metadata = {"canonical": info.canonical, "fields": sorted(info.fields), "operators": sorted(info.operators),
            "symbolic_dimensions": info.dimension, "dimension_status": "provisional_semantic_role_dimensions_not_verified_physical_units",
            "warmup_rows_before_execution_lag": info.warmup, "finite_lookback_rows": info.finite_lookback,
            "execution_lag": self.config.execution_lag, "ast_nodes": len(nodes), "ast_depth": depth(tree),
            "registry_fingerprint": self.registry.fingerprint,
            "structural_hash": digest([info.canonical, self.registry.fingerprint, self.config.execution_lag])}
        return CompiledExpression(tree, info, self.registry, metadata)

"""Factor expression language: parser, operator registry, evaluator, scripts."""

from . import approved, ops, parser
from .evaluator import EvalError, Evaluator, evaluate, evaluate_text
from .approved import APPROVED_OPERATORS, TS_OPERATORS
from .ops import REGISTRY, catalog_text
from .script import ScriptError, run_script, validate_script
from .spec import FactorSpec, SpecError
from .validate import ValidationReport, validate_expression

__all__ = [
    "parser",
    "ops",
    "REGISTRY",
    "catalog_text",
    "APPROVED_OPERATORS",
    "TS_OPERATORS",
    "approved",
    "evaluate",
    "evaluate_text",
    "Evaluator",
    "EvalError",
    "run_script",
    "validate_script",
    "ScriptError",
    "FactorSpec",
    "SpecError",
    "validate_expression",
    "ValidationReport",
]

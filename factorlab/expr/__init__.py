"""Factor expression language: parser, operator registry, evaluator, scripts."""

from . import parser, ops
from .evaluator import EvalError, Evaluator, evaluate, evaluate_text
from .ops import REGISTRY, catalog_text
from .script import ScriptError, run_script, validate_script
from .spec import FactorSpec, SpecError
from .validate import ValidationReport, validate_expression

__all__ = [
    "parser",
    "ops",
    "REGISTRY",
    "catalog_text",
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

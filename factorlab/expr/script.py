"""Executing a per-day python factor script in a restricted namespace.

This is *not* a hardened sandbox (a determined attacker with code execution
can still escape a restricted ``__builtins__``); it is a guard-rail that keeps
LLM-generated research code honest: no imports, no file/network access, no
dunder access, and a strict output contract.  For untrusted code, run the
whole pipeline inside a container.
"""

from __future__ import annotations

import ast
import inspect
import math
import time
from typing import Any, Optional

import numpy as np
import pandas as pd

from ..data.panel import PanelStore


class ScriptError(ValueError):
    pass


FORBIDDEN_CALLS = {
    "eval",
    "exec",
    "compile",
    "open",
    "input",
    "__import__",
    "globals",
    "locals",
    "vars",
    "getattr",
    "setattr",
    "delattr",
    "breakpoint",
    "help",
    "exit",
    "quit",
    "memoryview",
    "super",
    "classmethod",
    "staticmethod",
    "property",
}
FORBIDDEN_ATTRS = {
    "to_csv",
    "to_parquet",
    "to_pickle",
    "to_excel",
    "to_feather",
    "to_hdf",
    "to_sql",
    "save",
    "savez",
    "savetxt",
    "system",
    "popen",
    "rmtree",
    "unlink",
    "remove",
    "mkdir",
    "read_csv",
    "read_parquet",
}
FORBIDDEN_MODULES = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "importlib",
    "ctypes",
    "builtins",
    "pickle",
    "requests",
    "urllib",
}

SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "int": int,
    "isinstance": isinstance,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "pow": pow,
    "range": range,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
    "print": print,
    "Exception": Exception,
    "ValueError": ValueError,
    "KeyError": KeyError,
    "True": True,
    "False": False,
    "None": None,
}


def validate_script(code: str) -> list[str]:
    errors: list[str] = []
    if not code.strip():
        return ["script is empty"]
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"syntax error: {exc}"]

    has_generate = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            errors.append("imports are not allowed; use the provided pd / np / math")
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            errors.append("global / nonlocal statements are not allowed")
        if isinstance(node, (ast.With, ast.AsyncWith)):
            errors.append("with-blocks are not allowed")
        if isinstance(node, (ast.AsyncFunctionDef,)):
            errors.append("async functions are not allowed")
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id in FORBIDDEN_CALLS:
                errors.append(f"call to {fn.id}() is not allowed")
            if isinstance(fn, ast.Attribute) and fn.attr in FORBIDDEN_ATTRS:
                errors.append(f"attribute {fn.attr} is not allowed")
        if isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                errors.append("dunder attribute access is not allowed")
            if node.attr in FORBIDDEN_MODULES:
                errors.append(f"access to module {node.attr!r} is not allowed")
        if isinstance(node, (ast.FunctionDef,)):
            if node.name == "generate":
                has_generate = True
    if not has_generate:
        errors.append("script must define a function `generate(panel, params)`")
    return errors


def run_script(
    code: str,
    panel: PanelStore,
    params: Optional[dict] = None,
    max_seconds: float = 180.0,
) -> pd.DataFrame:
    params = dict(params or {})
    errors = validate_script(code)
    if errors:
        raise ScriptError("; ".join(errors))

    namespace: dict[str, Any] = {
        "__builtins__": dict(SAFE_BUILTINS),
        "pd": pd,
        "np": np,
        "math": math,
        "PARAMS": params,
    }
    started = time.time()
    try:
        exec(compile(code, "<factor-script>", "exec"), namespace)
    except Exception as exc:
        raise ScriptError(f"script failed to load: {exc}") from exc

    generate = namespace.get("generate")
    if not callable(generate):
        raise ScriptError("script must define generate(panel, params)")

    n_params = len(inspect.signature(generate).parameters)
    try:
        out = generate(panel, params) if n_params >= 2 else generate(panel)
    except ScriptError:
        raise
    except Exception as exc:
        raise ScriptError(f"generate() raised: {exc}") from exc
    elapsed = time.time() - started
    if elapsed > max_seconds:
        raise ScriptError(f"generate() took {elapsed:.1f}s, limit is {max_seconds:.0f}s")

    if not isinstance(out, pd.DataFrame):
        raise ScriptError(f"generate() must return a DataFrame, got {type(out).__name__}")

    try:
        out.index = pd.to_datetime(out.index)
    except Exception as exc:
        raise ScriptError(f"output index is not a date index: {exc}") from exc
    out = out.replace([np.inf, -np.inf], np.nan)
    try:
        out = out.astype("float64")
    except Exception as exc:
        raise ScriptError(f"output contains non-numeric columns: {exc}") from exc

    out = out.reindex(index=panel.dates, columns=panel.tickers)
    if out.isna().all().all():
        raise ScriptError("script output is empty after aligning to the panel")
    return out

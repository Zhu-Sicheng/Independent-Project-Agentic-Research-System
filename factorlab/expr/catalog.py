"""Machine-readable operator catalog for the agent pipeline.

The research agents read a machine-readable ``operator_file`` (name, argument
schema, allowed windows and a fingerprint) instead of parsing prose. This module
is the single source for that file: it exports the registry in
``factorlab/expr/ops.py`` together with the approved whitelist from
``factorlab/expr/approved.py``.

``python -m factorlab.expr.catalog --out operators.json``

The fingerprint is stable across runs (it excludes the generation timestamp), so
downstream agents can detect that their operator capabilities changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..config import ALLOWED_WINDOWS
from . import ops
from .approved import APPROVED_OPERATORS, APPROVED_SET

SCHEMA_VERSION = "1.0"


def _arg(arg: ops.Arg) -> dict:
    return {"name": arg.name, "kind": arg.kind, "default": arg.default}


def build_catalog(approved_only: bool = False) -> dict:
    """Return the catalog as a JSON-ready dict (no filesystem access)."""
    names = sorted(APPROVED_SET if approved_only else set(ops.REGISTRY))
    operators = []
    for name in names:
        operator = ops.REGISTRY[name]
        operators.append(
            {
                "name": operator.name,
                "category": operator.category,
                "doc": operator.doc,
                "min_args": operator.min_args,
                "max_args": operator.max_args,
                "args": [_arg(arg) for arg in operator.args],
                "window_positions": list(operator.window_positions()),
                "lag_positions": list(operator.lag_positions()),
                "approved": name in APPROVED_SET,
            }
        )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "source": "factorlab.expr.ops",
        "approved": sorted(APPROVED_SET) if not approved_only else names,
        "window_policy": {
            "allowed": list(ALLOWED_WINDOWS),
            "window_kinds": ["window"],
            "lag_kinds": ["lag"],
        },
        "operators": operators,
    }
    payload["fingerprint"] = fingerprint(payload)
    return payload


def fingerprint(payload: dict) -> str:
    """SHA-256 over the semantic content (stable across runs and platforms)."""
    core = {
        "schema_version": payload.get("schema_version"),
        "approved": payload.get("approved"),
        "operators": payload.get("operators"),
        "window_policy": payload.get("window_policy"),
    }
    blob = json.dumps(core, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def write_catalog(
    path: str | Path,
    approved_only: bool = False,
) -> Path:
    """Write the catalog JSON and return its path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_catalog(approved_only=approved_only)
    payload["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(target)
    return target


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="operators.json", help="output path")
    parser.add_argument(
        "--approved-only",
        action="store_true",
        help="export only the approved whitelist (agent-safe vocabulary)",
    )
    args = parser.parse_args(argv)
    target = write_catalog(args.out, approved_only=args.approved_only)
    payload = build_catalog(approved_only=args.approved_only)
    print(
        f"catalog: {len(payload['operators'])} operators "
        f"({sum(1 for op in payload['operators'] if op['approved'])} approved), "
        f"fingerprint {payload['fingerprint']}"
    )
    print(f"written to {target}")


if __name__ == "__main__":
    main()

"""Validate the idea-skill pack.

Checks:

* every ``skills/<name>/SKILL.md`` has YAML front matter with ``name`` and
  ``description`` and the name matches its folder;
* the pack stays at the idea layer (a small forbidden-vocabulary list catches
  performance/implementation content);
* every idea JSON example satisfies the 15-field Agent-2 idea contract and the
  interface's hard rules (prose-only mechanism, field vocabulary, direction,
  horizon, non-empty applicability/failure/evidence lists).

Usage::

    python skills/validate.py
    python skills/validate.py --idea path/to/idea.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SKILLS_ROOT.parent

REQUIRED_IDEA_FIELDS = (
    "title",
    "family",
    "dataset_id",
    "mechanism",
    "signal_concept",
    "required_fields",
    "expected_return_direction",
    "forecast_horizon_days",
    "lookback_hint_days",
    "applicability",
    "failure_modes",
    "evidence_ids",
    "history_record_ids",
    "novelty_rationale",
    "required_operators",
)

PANEL_FIELDS = {
    "open",
    "high",
    "low",
    "close",
    "volume",
    "returns",
    "log_returns",
    "amount",
    "adv20",
    "cap",
    "cap_rank",
    "range",
    "close_position",
    "intraday_return",
    "overnight_return",
}

#: vocabulary that would drag a skill out of the idea layer
FORBIDDEN = re.compile(
    r"(?i)\b(backtests?|backtesting|sharpe|pnl|drawdown|turnover|simulat\w*|"
    r"fitness|portfolios?|rank[ _-]?ic|information[ _-]?coefficient|"
    r"net[ _-]?asset|grid[ _-]?search)\b|回测|夏普|净值|换手|回撤|"
    r"信息系数|多空组合",
)

#: formulas are implementation, not ideas
FORMULA = re.compile(
    r"\bts_\w+\s*\(|\bfield\s*\(|```|\bsafe_div\s*\(|\brank\s*\("
)


def _error(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_front_matter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip("\n")
    data = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def skill_directories(path: Path = SKILLS_ROOT) -> list[Path]:
    return sorted(
        item
        for item in path.iterdir()
        if item.is_dir() and item.name not in {"_shared", "examples", "__pycache__"}
    )


def check_pack(path: Path = SKILLS_ROOT) -> list[str]:
    errors: list[str] = []
    directories = skill_directories(path)
    if not directories:
        _error(errors, "no skill directories found")
    names: set[str] = set()
    for directory in directories:
        skill_file = directory / "SKILL.md"
        if not skill_file.exists():
            _error(errors, f"{directory.name}: missing SKILL.md")
            continue
        text = skill_file.read_text(encoding="utf-8")
        meta = parse_front_matter(text)
        name = meta.get("name", "")
        description = meta.get("description", "")
        if not name:
            _error(errors, f"{directory.name}: front matter has no name")
        elif name != directory.name:
            _error(errors, f"{directory.name}: front matter name {name!r} does not match folder")
        if not description:
            _error(errors, f"{directory.name}: front matter has no description")
        elif len(description) > 400:
            _error(errors, f"{directory.name}: description is too long ({len(description)} chars)")
        if name in names:
            _error(errors, f"{directory.name}: duplicate skill name {name!r}")
        names.add(name)
        if not text.strip():
            _error(errors, f"{directory.name}: empty SKILL.md")

    for markdown in path.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for match in FORBIDDEN.finditer(text):
            line = text[: match.start()].count("\n") + 1
            _error(
                errors,
                f"{markdown.relative_to(REPO_ROOT)}:{line}: forbidden idea-layer term {match.group(0)!r}",
            )
    return errors


def check_idea(idea: dict, where: str = "<idea>") -> list[str]:
    errors: list[str] = []
    missing = [field for field in REQUIRED_IDEA_FIELDS if field not in idea]
    extra = sorted(set(idea) - set(REQUIRED_IDEA_FIELDS))
    if missing:
        _error(errors, f"{where}: missing fields {missing}")
    if extra:
        _error(errors, f"{where}: unknown fields {extra}")
    for field in ("title", "family", "dataset_id", "mechanism", "signal_concept", "novelty_rationale"):
        value = idea.get(field)
        if not isinstance(value, str) or not value.strip():
            _error(errors, f"{where}.{field}: must be a non-empty string")
    for prose_field in ("title", "mechanism", "signal_concept"):
        value = idea.get(prose_field)
        if isinstance(value, str) and FORMULA.search(value):
            _error(
                errors,
                f"{where}.{prose_field}: contains a formula/code fragment; describe the concept instead",
            )
    direction = idea.get("expected_return_direction")
    if direction not in {"positive", "negative"}:
        _error(errors, f"{where}.expected_return_direction: must be 'positive' or 'negative'")
    horizon = idea.get("forecast_horizon_days")
    if not isinstance(horizon, int) or isinstance(horizon, bool) or not 1 <= horizon <= 252:
        _error(errors, f"{where}.forecast_horizon_days: integer in [1, 252] required")
    lookbacks = idea.get("lookback_hint_days")
    if not isinstance(lookbacks, list) or not lookbacks:
        _error(errors, f"{where}.lookback_hint_days: non-empty list of integers required")
    else:
        for value in lookbacks:
            if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 504:
                _error(errors, f"{where}.lookback_hint_days: {value!r} is not a plausible lookback")
    fields = idea.get("required_fields")
    if not isinstance(fields, list) or not fields:
        _error(errors, f"{where}.required_fields: non-empty list required")
    else:
        unknown = sorted(set(fields) - PANEL_FIELDS)
        if unknown:
            _error(errors, f"{where}.required_fields: unknown panel fields {unknown}")
    for list_field in ("applicability", "failure_modes", "evidence_ids"):
        values = idea.get(list_field)
        if (
            not isinstance(values, list)
            or not values
            or not all(isinstance(value, str) and value.strip() for value in values)
        ):
            _error(errors, f"{where}.{list_field}: non-empty list of strings required")
    history = idea.get("history_record_ids")
    if not isinstance(history, list) or not all(isinstance(value, str) for value in history):
        _error(errors, f"{where}.history_record_ids: list of strings required")
    operators = idea.get("required_operators")
    if not isinstance(operators, list) or not all(isinstance(value, str) for value in operators):
        _error(errors, f"{where}.required_operators: list of strings required")
    family = idea.get("family")
    if isinstance(family, str) and not re.fullmatch(r"[a-z][a-z0-9_]*", family):
        _error(errors, f"{where}.family: snake_case identifier required")
    return errors


def load_ideas(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError(f"{path}: expected an object or array of objects")
    return payload


def check_examples(path: Path = SKILLS_ROOT / "examples") -> list[str]:
    errors: list[str] = []
    files = sorted(path.glob("*.json"))
    if not files:
        _error(errors, "no idea example files found")
    for file in files:
        try:
            ideas = load_ideas(file)
        except (json.JSONDecodeError, ValueError) as exc:
            _error(errors, f"{file.relative_to(REPO_ROOT)}: {exc}")
            continue
        if not ideas:
            _error(errors, f"{file.relative_to(REPO_ROOT)}: empty idea array")
        for index, idea in enumerate(ideas, start=1):
            errors.extend(check_idea(idea, where=f"{file.relative_to(REPO_ROOT)}#{index}"))
    return errors


def validate_all() -> list[str]:
    return check_pack() + check_examples()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--idea", default=None, help="validate a single idea JSON file")
    args = parser.parse_args(argv)
    if args.idea:
        path = Path(args.idea)
        try:
            ideas = load_ideas(path)
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"FAIL: {exc}")
            raise SystemExit(1)
        errors: list[str] = []
        for index, idea in enumerate(ideas, start=1):
            errors.extend(check_idea(idea, where=f"{path}#{index}"))
        if errors:
            print("FAIL\n" + "\n".join(f"  - {error}" for error in errors))
            raise SystemExit(1)
        print(f"OK: {len(ideas)} idea(s) valid")
        return
    errors = validate_all()
    if errors:
        print("FAIL\n" + "\n".join(f"  - {error}" for error in errors))
        raise SystemExit(1)
    skills = len(skill_directories())
    ideas = sum(len(load_ideas(file)) for file in (SKILLS_ROOT / "examples").glob("*.json"))
    print(f"OK: {skills} skills, {ideas} example ideas, idea-layer vocabulary clean")


if __name__ == "__main__":
    main()

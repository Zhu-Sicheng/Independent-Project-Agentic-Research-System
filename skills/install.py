"""Install the idea-skill pack into an agent runtime's skills directory.

Each skill becomes ``<dest>/<skill-name>/SKILL.md`` with the shared references
copied next to it as ``<dest>/<skill-name>/references/`` and the example ideas as
``<dest>/<skill-name>/examples/idea_batch.json``. Installing is idempotent.

Usage::

    python skills/install.py --dest "$env:USERPROFILE\\.claude\\skills"
    python skills/install.py --dest "$env:USERPROFILE\\.dsh\\skills" --dry-run
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parent
SHARED = SKILLS_ROOT / "_shared" / "references"
EXAMPLES = SKILLS_ROOT / "examples"
SKILL_NAMES = (
    "factor-idea-scout",
    "anomaly-taxonomy",
    "paper-to-hypothesis",
    "event-theme-radar",
    "hypothesis-formalizer",
    "idea-diversity-planner",
)


def default_dest() -> Path:
    env = os.environ.get("SKILLS_DEST")
    if env:
        return Path(env).expanduser()
    for candidate in (
        Path.home() / ".claude" / "skills",
        Path.home() / ".dsh" / "skills",
    ):
        if candidate.parent.exists():
            return candidate
    return SKILLS_ROOT / ".installed"


def plan(dest: Path) -> list[tuple[Path, Path]]:
    """Return the (source, destination) copy plan for an installation."""
    copies: list[tuple[Path, Path]] = []
    for name in SKILL_NAMES:
        skill_file = SKILLS_ROOT / name / "SKILL.md"
        if not skill_file.exists():
            raise FileNotFoundError(f"missing skill: {skill_file}")
        target = dest / name
        copies.append((skill_file, target / "SKILL.md"))
        for reference in sorted(SHARED.glob("*.md")):
            copies.append((reference, target / "references" / reference.name))
        for example in sorted(EXAMPLES.glob("*.json")):
            copies.append((example, target / "examples" / example.name))
    copies.append((SKILLS_ROOT / "README.md", dest / "factor-idea-pack-README.md"))
    return copies


def install(dest: Path, dry_run: bool = False) -> list[Path]:
    copies = plan(dest)
    written: list[Path] = []
    for source, target in copies:
        if dry_run:
            print(f"{source.relative_to(SKILLS_ROOT)} -> {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        written.append(target)
    if not dry_run:
        print(f"installed {len(written)} files under {dest}")
        print("point the agent's skill loader at that directory, or read a SKILL.md directly")
    return written


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", default=None, help="target skills directory (default: detected)")
    parser.add_argument("--dry-run", action="store_true", help="print the copy plan only")
    args = parser.parse_args(argv)
    dest = Path(args.dest).expanduser() if args.dest else default_dest()
    install(dest, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

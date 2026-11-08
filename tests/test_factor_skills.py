"""Tests for the idea-skill pack: contract, idea-layer boundary and installer."""

import json
import tempfile
import unittest
from pathlib import Path

import skills.install as installer
import skills.validate as validator

SKILLS_ROOT = Path(__file__).resolve().parent.parent / "skills"


class TestIdeaSkills(unittest.TestCase):
    def test_pack_validates_cleanly(self):
        errors = validator.validate_all()
        self.assertEqual(errors, [], "\n".join(errors))

    def test_every_skill_has_front_matter_and_unique_name(self):
        names = []
        for directory in validator.skill_directories():
            text = (directory / "SKILL.md").read_text(encoding="utf-8")
            meta = validator.parse_front_matter(text)
            self.assertEqual(meta.get("name"), directory.name)
            self.assertTrue(meta.get("description"))
            names.append(meta["name"])
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(names), 6)

    def test_skill_files_do_not_include_results_language(self):
        for markdown in SKILLS_ROOT.rglob("*.md"):
            text = markdown.read_text(encoding="utf-8")
            self.assertIsNone(validator.FORBIDDEN.search(text), f"{markdown} leaks implementation language")

    def test_example_ideas_satisfy_the_contract(self):
        ideas = validator.load_ideas(SKILLS_ROOT / "examples" / "idea_batch.json")
        self.assertGreaterEqual(len(ideas), 3)
        for index, idea in enumerate(ideas, start=1):
            self.assertEqual(validator.check_idea(idea, where=f"example#{index}"), [])

    def test_idea_checker_rejects_a_formula_in_mechanism(self):
        idea = validator.load_ideas(SKILLS_ROOT / "examples" / "idea_batch.json")[0]
        broken = dict(idea)
        broken["mechanism"] = "The signal is ts_mean(volume, 20) divided by close."
        errors = validator.check_idea(broken, where="broken")
        self.assertTrue(any("formula" in error for error in errors))

    def test_installer_plan_is_self_contained(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            dest = Path(tmp) / "skills"
            copies = installer.plan(dest)
            targets = {target for _, target in copies}
            for name in installer.SKILL_NAMES:
                self.assertTrue(any(target.name == "SKILL.md" for target in targets))
                self.assertIn(dest / name / "references" / "anomaly_catalog.md", targets)
                self.assertIn(dest / name / "examples" / "idea_batch.json", targets)
            written = installer.install(dest)
            self.assertEqual(len(written), len(copies))
            for target in written:
                self.assertTrue(target.exists())
            # idempotent: installing twice writes the same files again
            self.assertEqual(len(installer.install(dest)), len(copies))


if __name__ == "__main__":
    unittest.main()

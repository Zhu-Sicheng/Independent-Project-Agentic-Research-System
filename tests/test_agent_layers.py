"""Layer boundaries: our Agent 4 (evaluation) and Agent 5 (feedback) packages."""

import unittest
from pathlib import Path

import factorlab.agent4 as agent4
import factorlab.agent5 as agent5
import factorlab.xy_pipeline as pipeline
from factorlab.agent_adapter import FIELD_MAP, translate_expression


class TestLayerBoundaries(unittest.TestCase):
    def test_agent4_and_agent5_exports_are_single_objects(self):
        # the pipeline re-exports the moved functions, it does not redefine them
        self.assertIs(pipeline.evaluate_is_candidates, agent4.evaluate_is_candidates)
        self.assertIs(pipeline.display_evaluation, agent4.display_evaluation)
        self.assertIs(pipeline.display_labels, agent4.display_labels)
        self.assertIs(pipeline.split_is_panel, agent4.split_is_panel)
        self.assertIs(pipeline.write_feedback, agent5.write_feedback)
        self.assertIs(pipeline.round_improved, agent5.round_improved)
        self.assertIs(pipeline.candidates_from_revisions, agent5.candidates_from_revisions)

    def test_agent4_modules_do_not_import_the_orchestrator(self):
        root = Path("factorlab")
        for module in ("agent4/isolation.py", "agent4/evaluation.py", "agent4/labels.py", "agent4/display.py"):
            text = (root / module).read_text(encoding="utf-8")
            self.assertNotIn("from ..xy_pipeline", text, module)
            self.assertNotIn("import factorlab.xy_pipeline", text, module)

    def test_pipeline_keeps_only_orchestration(self):
        text = Path("factorlab/xy_pipeline.py").read_text(encoding="utf-8")
        for moved_function in (
            "def evaluate_is_candidates(",
            "def display_evaluation(",
            "def write_feedback(",
            "def split_is_panel(",
            "def display_labels(",
            "def round_improved(",
        ):
            self.assertNotIn(moved_function, text, moved_function)

    def test_adapter_translates_collaborator_vocabulary(self):
        self.assertEqual(translate_expression("Adj_Close - DlyLow"), "close - low")
        self.assertEqual(translate_expression('field("Adj_Volume")'), "volume")
        self.assertIn("Adj_Close", FIELD_MAP)


if __name__ == "__main__":
    unittest.main()

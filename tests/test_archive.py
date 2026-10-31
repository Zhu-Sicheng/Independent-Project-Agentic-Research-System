"""Archive local run artifacts and recover hypothesis texts."""

import json
import tempfile
import unittest
from pathlib import Path

import factorlab.archive_runs as arch


class TestArchive(unittest.TestCase):
    def test_parse_report_hypotheses(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            path.write_text(
                "# run\n\n## alpha_one\n\n**hypothesis**: first story\n\n"
                "## alpha_two\n\n**hypothesis**: second story\n",
                encoding="utf-8",
            )
            texts = arch.parse_report_hypotheses(path)
            self.assertEqual(texts["alpha_one"], "first story")
            self.assertEqual(texts["alpha_two"], "second story")

    def test_parse_log_hypotheses_utf16(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.log"
            path.write_text(
                "proposed 1 hypotheses\n\n[alpha_one] first story\n  round 0: ...\n",
                encoding="utf-16",
            )
            self.assertEqual(arch.parse_log_hypotheses(path), {"alpha_one": "first story"})

    def test_archive_copies_artifacts_and_writes_hypotheses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "20260101-000000-test"
            run_dir.mkdir(parents=True)
            attempt = {"hypothesis": "alpha_one", "attempt": 0, "grid": None}
            (run_dir / "attempts.jsonl").write_text(json.dumps(attempt) + "\n", encoding="utf-8")
            (run_dir / "report.md").write_text(
                "## alpha_one\n\n**hypothesis**: first story\n", encoding="utf-8"
            )

            old_runs, old_records = arch.RUNS_DIR, arch.RECORDS_DIR
            arch.RUNS_DIR, arch.RECORDS_DIR = root / "runs", root / "records"
            try:
                texts = arch.archive_runs(["20260101-000000-test"])
            finally:
                arch.RUNS_DIR, arch.RECORDS_DIR = old_runs, old_records

            self.assertEqual(texts["alpha_one"], "first story")
            dest = root / "records" / "20260101-000000-test"
            self.assertTrue((dest / "attempts.jsonl").exists())
            mapping = json.loads((dest / "hypotheses.json").read_text(encoding="utf-8"))
            self.assertEqual(mapping, {"alpha_one": "first story"})


if __name__ == "__main__":
    unittest.main()

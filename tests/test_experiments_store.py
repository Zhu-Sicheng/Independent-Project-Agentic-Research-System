"""Date-ordered experiment store: naming, scanning, index and migration."""

import json
import tempfile
import unittest
from pathlib import Path

from factorlab import experiments_store as store


class _StoreSandbox(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self._tmp.name) / "experiments"
        self.root.mkdir(parents=True)
        self._old_experiments = store.EXPERIMENTS
        self._old_index = store.INDEX_FILE
        store.EXPERIMENTS = self.root
        store.INDEX_FILE = self.root / "README.md"

    def tearDown(self):
        store.EXPERIMENTS = self._old_experiments
        store.INDEX_FILE = self._old_index
        self._tmp.cleanup()

    def _run(self, experiment: str, run_id: str, payload: dict | None = None) -> Path:
        destination = self.root / experiment / "runs" / run_id
        destination.mkdir(parents=True)
        (destination / "run.json").write_text(
            json.dumps({"run_id": run_id, **(payload or {})}), encoding="utf-8"
        )
        return destination


class TestNaming(_StoreSandbox):
    def test_dated_dir_prefixes_the_date_and_slugifies(self):
        self.assertEqual(store.dated_dir("20261031", "systemv1_50").name, "20261031-systemv1_50")
        self.assertEqual(store.dated_dir("20261031", "my batch").name, "20261031-my_batch")
        self.assertEqual(store.date_of("20261031-095220-batch10"), "20261031")
        self.assertEqual(store.date_of("sysv1-h1", fallback="20260101"), "20260101")

    def test_iter_experiment_dirs_is_chronological_not_alphabetical(self):
        for name in ("20261031-zzz", "20261030-aaa", "20261101-mmm"):
            (self.root / name).mkdir()
        self.assertEqual(
            [path.name for path in store.iter_experiment_dirs()],
            ["20261030-aaa", "20261031-zzz", "20261101-mmm"],
        )


class TestScanning(_StoreSandbox):
    def test_find_run_dir_searches_dated_experiments_and_runs(self):
        expected = self._run("20261031-systemv1_50", "sysv1-h1")
        self.assertEqual(store.find_run_dir("sysv1-h1"), expected)
        self.assertIsNone(store.find_run_dir("missing-run"))

    def test_iter_evaluation_files_only_in_run_dirs(self):
        run = self._run("20261031-systemv1_50", "sysv1-h1")
        (run / "evaluations.json").write_text(json.dumps({"records": []}), encoding="utf-8")
        other = self._run("20261031-batch10", "20261031-095220-batch10")
        (other / "evaluations.json").write_text(json.dumps({"records": []}), encoding="utf-8")
        files = store.iter_evaluation_files()
        self.assertEqual(len(files), 2)
        self.assertIn(run / "evaluations.json", files)


class TestIndex(_StoreSandbox):
    def test_write_index_lists_experiments_in_date_order(self):
        (self.root / "20261031-systemv1_50").mkdir()
        (self.root / "20261030-us-mining").mkdir()
        (self.root / "20261031-systemv1_50" / "README.md").write_text(
            "# 2026-10-31 systemv1 50+ hypothesis batch\n", encoding="utf-8"
        )
        target = store.write_index()
        text = target.read_text(encoding="utf-8")
        self.assertIn("experiments", text.lower())
        first = text.index("20261030-us-mining")
        second = text.index("20261031-systemv1_50")
        self.assertLess(first, second)
        self.assertIn("2026-10-31 systemv1 50+ hypothesis batch", text)


class TestMigration(_StoreSandbox):
    def test_migrate_legacy_moves_batches_into_dated_dirs(self):
        legacy = {
            "batch10/summary.csv": "x",
            "records/20261031-095220-batch10/attempts.jsonl": "{}",
            "reports/20261031-095220-batch10.md": "# report",
            "stability/factorA/metrics.csv": "z",
            "batch100/summary.csv": "y",
            "records/20261031-144435-p100_a_00/attempts.jsonl": "{}",
            "published/systemv1-50h/README.md": "# published",
            "published/systemv1-50h/figures/rank01.png": "png",
            "xy/sysv1-h1/run.json": json.dumps({"run_id": "sysv1-h1"}),
            "ledger.csv": "a,b",
            "plots/old.png": "png",
        }
        for relative, content in legacy.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        result = store.migrate_legacy()
        names = set(result["directories"])
        self.assertIn("20261031-batch10", names)
        self.assertIn("20261031-batch100", names)
        self.assertIn("20261031-systemv1_50", names)
        self.assertTrue((self.root / "20261031-batch10" / "stability" / "factorA" / "metrics.csv").exists())
        self.assertTrue(
            (self.root / "20261031-batch100" / "records" / "20261031-144435-p100_a_00" / "attempts.jsonl").exists()
        )
        self.assertTrue((self.root / "20261031-systemv1_50" / "figures" / "rank01.png").exists())
        self.assertTrue((self.root / "20261031-systemv1_50" / "runs" / "sysv1-h1" / "run.json").exists())
        # flat legacy directories are gone after the migration
        for legacy_name in ("batch10", "batch100", "records", "reports", "stability", "published", "plots", "xy"):
            self.assertFalse((self.root / legacy_name).exists(), legacy_name)


if __name__ == "__main__":
    unittest.main()

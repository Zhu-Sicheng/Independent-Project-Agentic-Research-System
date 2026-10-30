"""Repository hygiene: no secrets, no local credential files in git.

This is the guard that keeps the local ``.env`` (API keys) and deploy keys out
of the public repository.  It runs in CI and locally before every commit.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: real provider keys look like ``sk-`` followed by 32 hex characters; the
#: character class below deliberately cannot match this regex's own source
KEY_RE = re.compile(r"sk-[0-9a-f]{32}")

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".toml",
    ".yml",
    ".yaml",
    ".txt",
    ".json",
    ".csv",
    ".cfg",
    ".ini",
    ".sh",
    ".ps1",
    ".example",
}

FORBIDDEN_TRACKED = (
    ".env",
    ".env.local",
    ".env.production",
    ".deploy_key",
    ".deploy_key.pub",
)


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


class TestRepoHygiene(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("git"):
            raise unittest.SkipTest("git is not available")
        result = _git("ls-files")
        if result.returncode != 0:
            raise unittest.SkipTest("not a git working tree")
        cls.tracked = [line for line in result.stdout.splitlines() if line]
        cls.tracked_set = set(cls.tracked)

    def test_local_secrets_are_not_tracked(self):
        for name in FORBIDDEN_TRACKED:
            self.assertNotIn(name, self.tracked_set, f"{name} must never be committed")

    def test_env_is_ignored(self):
        env = ROOT / ".env"
        if not env.exists():
            self.skipTest("no local .env")
        result = _git("check-ignore", "-q", ".env")
        self.assertEqual(result.returncode, 0, ".env must be gitignored")

    def test_no_api_key_in_tracked_files(self):
        for rel in self.tracked:
            path = ROOT / rel
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            match = KEY_RE.search(text)
            self.assertIsNone(match, f"possible API key in tracked file {rel}")


if __name__ == "__main__":
    unittest.main()

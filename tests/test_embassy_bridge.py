import os
import sys
import json
import shutil
import subprocess
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import embassy_bridge as eb


def _init_local_repo(repo_dir: str, outbox_rel: str, files: dict) -> str:
    """Creates a local git repo (no network) with the given files under outbox_rel,
    commits them, and returns the commit sha. Used to test sync() against a
    fully-controlled counterpart without depending on the real GitHub repos."""
    os.makedirs(os.path.join(repo_dir, outbox_rel), exist_ok=True)
    for filename, content in files.items():
        with open(os.path.join(repo_dir, outbox_rel, filename), "w", encoding="utf-8") as f:
            f.write(content)
    subprocess.run(["git", "init", "-q", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, check=True)
    subprocess.run(
        ["git", "-c", "user.email=test@test.com", "-c", "user.name=test", "commit", "-q", "-m", "seed"],
        cwd=repo_dir, check=True,
    )
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True)
    return result.stdout.strip()


VALID_TREATY = (
    "# Ratified Epistemic Treaty #1\n"
    "## Title: Test Law\n"
    "**Originating Frontier Dossier:** World A DOSSIER_001_TEST.md\n"
    "**Epistemic Status:** CANON VERIFIED\n\n"
    "### Formal Canonical Statement & Proof:\n"
    "A sufficiently long body of text describing the formal proof and verification "
    "artifacts in enough detail to pass the minimum length and required-section "
    "validation checks used here.\n\n"
    "### Supporting Verification Artifacts in Agora:\n"
    "* `shared_agora/artifacts/some_plot.png`\n"
)


class TestRewriteArtifactReferences(unittest.TestCase):
    def test_rewrites_backtick_wrapped_reference(self):
        content = "* `shared_agora/foo/bar.png` and text `shared_agora/baz.py` end."
        out = eb.rewrite_artifact_references(content, "abc1234567890")
        self.assertIn(
            "https://raw.githubusercontent.com/nini1972/synthetic-agora/abc1234567890/instances/shared_agora/foo/bar.png",
            out,
        )
        self.assertIn(
            "https://raw.githubusercontent.com/nini1972/synthetic-agora/abc1234567890/instances/shared_agora/baz.py",
            out,
        )

    def test_leaves_non_backtick_reference_untouched(self):
        content = "See shared_agora/foo.png (no backticks) for details."
        out = eb.rewrite_artifact_references(content, "abc123")
        self.assertEqual(content, out)

    def test_does_not_span_across_newlines_on_unmatched_backtick(self):
        content = "`shared_agora/unterminated\nsecond line\nthird line"
        out = eb.rewrite_artifact_references(content, "abc123")
        self.assertEqual(content, out, "Unmatched backtick must not trigger a cross-line rewrite")


class TestIsValidTreaty(unittest.TestCase):
    def test_accepts_well_formed_treaty(self):
        self.assertTrue(eb.is_valid_treaty(VALID_TREATY))

    def test_rejects_too_short_content(self):
        self.assertFalse(eb.is_valid_treaty("short"))

    def test_rejects_missing_required_headers(self):
        self.assertFalse(eb.is_valid_treaty("A" * 300))


class TestLedgerRoundTrip(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="embassy_ledger_test_")
        self._orig_ledger_path = eb.LEDGER_PATH
        self._orig_embassy_dir = eb.EMBASSY_DIR
        eb.EMBASSY_DIR = self.tmp_dir
        eb.LEDGER_PATH = os.path.join(self.tmp_dir, ".sync_ledger.json")

    def tearDown(self):
        eb.LEDGER_PATH = self._orig_ledger_path
        eb.EMBASSY_DIR = self._orig_embassy_dir
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_round_trip(self):
        ledger = {"imported": [{"filename": "a.md", "sha256": "abc"}], "exported": []}
        eb.save_ledger(ledger)
        loaded = eb.load_ledger()
        self.assertEqual(loaded, ledger)

    def test_malformed_shape_falls_back_to_empty(self):
        with open(eb.LEDGER_PATH, "w", encoding="utf-8") as f:
            json.dump({"imported": "not-a-list"}, f)
        loaded = eb.load_ledger()
        self.assertEqual(loaded, {"imported": [], "exported": []})

    def test_missing_sha256_entries_are_ignored_by_sync_dedup_logic(self):
        with open(eb.LEDGER_PATH, "w", encoding="utf-8") as f:
            json.dump({"imported": [{"filename": "a.md"}], "exported": []}, f)
        loaded = eb.load_ledger()
        hashes = {e["sha256"] for e in loaded.get("imported", []) if isinstance(e, dict) and "sha256" in e}
        self.assertEqual(hashes, set())


class TestSyncAgainstLocalFixtureRepo(unittest.TestCase):
    """Exercises sync() end-to-end against a fully local (no network) git repo,
    covering symlink rejection, dedup, and collision-archiving in one place."""

    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix="embassy_sync_test_")
        self.fixture_repo = os.path.join(self.base_dir, "fixture_repo")
        self.embassy_dir = os.path.join(self.base_dir, "embassy")

        self._orig = {
            "COUNTERPART_REPO_URL": eb.COUNTERPART_REPO_URL,
            "EMBASSY_DIR": eb.EMBASSY_DIR,
            "INBOX_DIR": eb.INBOX_DIR,
            "REJECTED_DIR": eb.REJECTED_DIR,
            "SUPERSEDED_DIR": eb.SUPERSEDED_DIR,
            "LEDGER_PATH": eb.LEDGER_PATH,
        }
        eb.COUNTERPART_REPO_URL = self.fixture_repo
        eb.EMBASSY_DIR = self.embassy_dir
        eb.INBOX_DIR = os.path.join(self.embassy_dir, "inbox")
        eb.REJECTED_DIR = os.path.join(self.embassy_dir, "rejected")
        eb.SUPERSEDED_DIR = os.path.join(self.embassy_dir, "superseded")
        eb.LEDGER_PATH = os.path.join(self.embassy_dir, ".sync_ledger.json")

    def tearDown(self):
        for key, value in self._orig.items():
            setattr(eb, key, value)
        shutil.rmtree(self.base_dir, ignore_errors=True)

    def _seed(self, files: dict) -> None:
        _init_local_repo(self.fixture_repo, eb.COUNTERPART_OUTBOX_REL, files)

    def test_imports_valid_treaty_and_is_idempotent(self):
        self._seed({"TREATY_001_TEST.md": VALID_TREATY})
        self.assertTrue(eb.sync())
        inbox_files = os.listdir(eb.INBOX_DIR)
        self.assertIn("TREATY_001_TEST.md", inbox_files)

        # Second run against the exact same commit must not duplicate or re-archive.
        self.assertTrue(eb.sync())
        self.assertFalse(os.path.exists(eb.SUPERSEDED_DIR), "No collision should occur on an unchanged re-sync")

    def test_rejects_malformed_candidate_with_notice_banner(self):
        self._seed({"TREATY_002_BAD.md": "not a real treaty, far too short and missing headers " * 5})
        self.assertTrue(eb.sync())
        rejected_files = os.listdir(eb.REJECTED_DIR)
        self.assertIn("TREATY_002_BAD.md", rejected_files)
        with open(os.path.join(eb.REJECTED_DIR, "TREATY_002_BAD.md"), encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Untrusted external content notice", content)

    def test_rejects_symlink_candidate_without_reading_target(self):
        self._seed({"TREATY_003_OK.md": VALID_TREATY})
        outside_secret = os.path.join(self.base_dir, "secret.txt")
        with open(outside_secret, "w", encoding="utf-8") as f:
            f.write("TOP SECRET - should never be read or committed")

        outbox_path = os.path.join(self.fixture_repo, eb.COUNTERPART_OUTBOX_REL)
        symlink_path = os.path.join(outbox_path, "TREATY_004_SYMLINK.md")
        try:
            os.symlink(outside_secret, symlink_path)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks require elevated privileges on this platform")

        subprocess.run(["git", "add", "-A"], cwd=self.fixture_repo, check=True)
        subprocess.run(
            ["git", "-c", "user.email=test@test.com", "-c", "user.name=test", "commit", "-q", "-m", "add symlink"],
            cwd=self.fixture_repo, check=True,
        )

        self.assertTrue(eb.sync())
        inbox_files = os.listdir(eb.INBOX_DIR)
        self.assertIn("TREATY_003_OK.md", inbox_files)
        self.assertNotIn("TREATY_004_SYMLINK.md", inbox_files)
        rejected_files = os.listdir(eb.REJECTED_DIR) if os.path.isdir(eb.REJECTED_DIR) else []
        self.assertNotIn("TREATY_004_SYMLINK.md", rejected_files,
                          "Symlink target content must never be read into rejected/ either")


if __name__ == "__main__":
    unittest.main()

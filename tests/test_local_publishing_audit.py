"""Local publishing automation: bounded, read-only evidence tests."""
import hashlib
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from local_publishing_audit import audit, write_receipt
import local_publishing_audit as audit_module
from unittest.mock import patch


class LocalPublishingAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "profile"
        self.root.mkdir()
        (self.root / "README.md").write_text(
            "[Public](https://github.com/ihatesirdavi/sunday-parcel)", encoding="utf-8"
        )
        self.at = datetime(2026, 11, 20, 12, 45, tzinfo=timezone.utc)
        self.calls = []

    def repo_ok(self, owner, name):
        self.calls.append(("repo", owner, name))
        return {"full_name": f"{owner}/{name}", "private": False}

    def pr_ok(self, owner, name, number):
        self.calls.append(("pr", owner, name, number))
        return {"number": number, "state": "open", "draft": True,
                "merged_at": None, "updated_at": "2026-11-20T12:00:00Z",
                "head": {"sha": "a" * 40}, "mergeable_state": "clean"}

    def run_check(self, repo_fetch=None, pr_fetch=None, validate=None):
        return audit(
            self.root, repo_fetch or self.repo_ok, pr_fetch or self.pr_ok,
            validate or (lambda root: []), now=self.at,
            source_head=lambda root: "b" * 40,
        )

    def test_success_is_a_local_receipt_without_publication_claim(self):
        result = self.run_check()
        self.assertEqual("PASS", result["status"])
        self.assertEqual("LOCAL_PYTHON", result["executor"])
        self.assertEqual(1, result["repository_count"])
        self.assertEqual(3, len(result["pull_requests"]))
        self.assertFalse(result["changes_published"])
        self.assertFalse(result["owner_release_accepted"])
        self.assertEqual([("repo", "ihatesirdavi", "sunday-parcel")],
                         [call for call in self.calls if call[0] == "repo"])

    def test_receipt_proves_exact_readme_and_executable_script_bytes(self):
        result = self.run_check()
        expected = hashlib.sha256((self.root / "README.md").read_bytes()).hexdigest()
        self.assertEqual(expected, result["readme_sha256"])
        self.assertEqual(64, len(result["audit_source_sha256"]))

    def test_merged_state_does_not_fabricate_maintainer_review(self):
        def merged(owner, repo, number):
            data = self.pr_ok(owner, repo, number)
            data["state"] = "closed"
            data["draft"] = False
            data["merged_at"] = "2026-11-20T12:20:00Z"
            return data
        result = self.run_check(pr_fetch=merged)
        self.assertEqual("MERGED", result["pull_requests"][0]["state"])
        self.assertEqual("NOT_CHECKED", result["pull_requests"][0]["review_acceptance"])
        self.assertNotIn("maintainer_accepted", result["pull_requests"][0])
    def test_deleted_repository_is_a_failure_not_success(self):
        def deleted(owner, name):
            raise HTTPError("https://api.github.com", 404, "Not Found", None, None)
        result = self.run_check(repo_fetch=deleted)
        self.assertEqual("FAIL", result["status"])
        self.assertIn("missing or inaccessible", result["errors"][0])

    def test_api_outage_is_unverified_not_missing(self):
        def limited(owner, name):
            raise HTTPError("https://api.github.com", 403, "Rate limited", None, None)
        result = self.run_check(repo_fetch=limited)
        self.assertEqual("UNVERIFIED", result["status"])
        self.assertIn("unverified", result["errors"][0])
        self.assertNotIn("missing or inaccessible", result["errors"][0])

    def test_local_file_validation_failure_is_a_failure(self):
        result = self.run_check(validate=lambda root: ["missing local asset"])
        self.assertEqual("FAIL", result["status"])
        self.assertIn("missing local asset", result["errors"])

    def test_pull_request_api_outage_does_not_claim_success(self):
        def unavailable(owner, name, number):
            raise TimeoutError("request timed out")
        result = self.run_check(pr_fetch=unavailable)
        self.assertEqual("UNVERIFIED", result["status"])
        self.assertEqual([], result["pull_requests"])
        self.assertEqual(3, len(result["errors"]))

    def test_receipt_is_atomic_and_keeps_immutable_history(self):
        output = Path(self.temp.name) / "receipts"
        result = self.run_check()
        archive, latest = write_receipt(output, result)
        self.assertTrue(archive.is_file())
        self.assertTrue(latest.is_file())
        self.assertEqual(archive.read_bytes(), latest.read_bytes())
        with self.assertRaises(FileExistsError):
            write_receipt(output, result)
        self.assertEqual(1, len(list(output.glob("audit-*.json"))))



    def test_main_reuses_one_receipt_with_private_source_discovery_summary(self):
        report = self.run_check()
        out = Path(self.temp.name) / "native-audit"
        with patch.object(audit_module, "audit", return_value=report):
            with patch.object(audit_module, "run_optional_discovery",
                              return_value={"status": "DISCOVERED_NOT_LIVE_VERIFIED",
                                            "candidate_count": 3}):
                with patch.object(sys, "argv", ["audit", "--root", str(self.root),
                                                 "--output-dir", str(out)]):
                    self.assertEqual(0, audit_module.main())
        import json
        written = json.loads((out / "latest.json").read_text(encoding="utf-8"))
        self.assertEqual(3, written["research_sources"]["candidate_count"])
        self.assertEqual("PASS", written["status"])
        self.assertFalse(written["changes_published"])

    def test_source_config_failure_produces_unverified_not_false_pass(self):
        report = self.run_check()
        out = Path(self.temp.name) / "native-unverified"
        with patch.object(audit_module, "audit", return_value=report):
            with patch.object(audit_module, "run_optional_discovery",
                              return_value={"status": "UNVERIFIED", "error_type": "ValueError"}):
                with patch.object(sys, "argv", ["audit", "--root", str(self.root),
                                                 "--output-dir", str(out)]):
                    self.assertEqual(2, audit_module.main())
        import json
        written = json.loads((out / "latest.json").read_text(encoding="utf-8"))
        self.assertEqual("UNVERIFIED", written["status"])
        self.assertEqual("ValueError", written["research_sources"]["error_type"])


if __name__ == "__main__":
    unittest.main()
"""Offline tests for public GitHub repository reference validation."""
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_repo_references import collect_references, validate_repositories


class PublicRepositoryReferenceTests(unittest.TestCase):
    def _profile(self, text, extra_docs=None):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "README.md").write_text(text, encoding="utf-8")
        if extra_docs:
            (root / "docs").mkdir()
            (root / "docs" / "links.md").write_text(extra_docs, encoding="utf-8")
        self.addCleanup(temp.cleanup)
        return root

    def test_deleted_public_repository_fails(self):
        root = self._profile("[Old](https://github.com/ihatesirdavi/vscode-extensions)")
        def fetch(owner, repo):
            raise HTTPError("https://api.github.com/repos/" + owner + "/" + repo, 404, "Not Found", None, None)
        errors = validate_repositories(root, fetch)
        self.assertEqual(1, len(errors))
        self.assertIn("ihatesirdavi/vscode-extensions", errors[0])
        self.assertIn("missing or inaccessible", errors[0])

    def test_public_references_in_readme_and_docs_are_unique(self):
        root = self._profile(
            "[New](https://github.com/ihatesirdavi/sunday-parcel) "
            "[PR](https://github.com/Scony/godot-gdscript-toolkit/pull/435) "
            "[User](https://github.com/ihatesirdavi?tab=repositories)",
            extra_docs="[Again](https://github.com/ihatesirdavi/sunday-parcel)"
        )
        seen = []
        def fetch(owner, repo):
            seen.append((owner, repo))
            return {"full_name": owner + "/" + repo, "private": False}
        self.assertEqual([], validate_repositories(root, fetch))
        self.assertEqual({("Scony", "godot-gdscript-toolkit"), ("ihatesirdavi", "sunday-parcel")}, set(seen))
        self.assertEqual(2, len(seen))

    def test_repo_rename_is_stale(self):
        root = self._profile("[Old](https://github.com/ihatesirdavi/old-name)")
        errors = validate_repositories(root, lambda owner, repo: {"full_name": "ihatesirdavi/new-name", "private": False})
        self.assertIn("noncanonical", errors[0])

    def test_private_repository_is_not_publicly_accessible(self):
        root = self._profile("[Private](https://github.com/ihatesirdavi/private-repo)")
        errors = validate_repositories(root, lambda owner, repo: {"full_name": "ihatesirdavi/private-repo", "private": True})
        self.assertIn("private", errors[0])

    def test_rate_limit_and_server_failures_are_not_reported_as_missing(self):
        root = self._profile("[Repo](https://github.com/ihatesirdavi/sunday-parcel)")
        def fetch(owner, repo):
            raise HTTPError("https://api.github.com", 403, "API quota", None, None)
        errors = validate_repositories(root, fetch)
        self.assertEqual(1, len(errors))
        self.assertIn("unverified", errors[0])
        self.assertNotIn("missing or inaccessible", errors[0])

    def test_no_repository_links_is_an_explicit_failure(self):
        root = self._profile("[Profile](https://github.com/ihatesirdavi)")
        errors = validate_repositories(root, lambda owner, repo: {})
        self.assertEqual(["no GitHub repository references found"], errors)

    def test_link_extraction_accepts_mixed_markdown_html(self):
        root = self._profile(
            '[Open](https://github.com/ihatesirdavi/preview-lab) '
            '<a href="https://github.com/ih8sirdavi/Docs">Docs</a>'
        )
        refs = collect_references(root)
        self.assertEqual({("ihatesirdavi", "preview-lab"), ("ih8sirdavi", "Docs")}, set(refs))


if __name__ == "__main__":
    unittest.main()
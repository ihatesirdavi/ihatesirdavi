"""Offline source-discovery tests: parsing, scope limits, privacy, and custody."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from research_public_sources import (
    normalize_public_url,
    discover_from_config,
    write_source_snapshot,
    run_optional_discovery,
)


class ResearchPublicSourceTests(unittest.TestCase):
    def test_github_files_and_prs_are_repository_candidates_not_separate_repos(self):
        self.assertEqual(
            ("github_repo", "https://github.com/3b1b/captions"),
            normalize_public_url("https://github.com/3b1b/captions/blob/main/2024/story.srt"),
        )
        self.assertEqual(
            ("github_repo", "https://github.com/Scony/godot-gdscript-toolkit"),
            normalize_public_url("https://github.com/Scony/godot-gdscript-toolkit/pull/435"),
        )

    def test_arxiv_pdf_html_and_abs_deduplicate_to_paper(self):
        expected = ("arxiv_paper", "https://arxiv.org/abs/2610.14162")
        for url in (
            "https://arxiv.org/abs/2610.14162",
            "https://arxiv.org/html/2610.14162",
            "https://arxiv.org/pdf/2610.14162.pdf",
        ):
            self.assertEqual(expected, normalize_public_url(url))

    def test_doi_parenthesis_survives_markdown_punctuation(self):
        self.assertEqual(
            ("scholarly_doi", "https://doi.org/10.1016/0167-6423(87)90015-7"),
            normalize_public_url("https://doi.org/10.1016/0167-6423(87)90015-7)."),
        )

    def test_youtube_video_id_and_channel_preserved_without_tracking(self):
        self.assertEqual(
            ("youtube_video", "https://www.youtube.com/watch?v=26P1KyvrmjI"),
            normalize_public_url("https://www.youtube.com/watch?v=26P1KyvrmjI&t=5s&utm_source=example"),
        )
        self.assertEqual(
            ("youtube_channel", "https://www.youtube.com/@pezzzaswork"),
            normalize_public_url("https://www.youtube.com/@pezzzaswork/videos"),
        )
        self.assertIsNone(normalize_public_url("https://www.youtube.com/watch?list=PLnoVideo"))

    def test_hugging_face_dataset_model_and_docs_are_separate(self):
        self.assertEqual(
            ("huggingface_dataset", "https://huggingface.co/datasets/allenai/scifact"),
            normalize_public_url("https://huggingface.co/datasets/allenai/scifact/tree/main"),
        )
        self.assertEqual(
            ("huggingface_model", "https://huggingface.co/hazyresearch/ncm-checkpoints"),
            normalize_public_url("https://huggingface.co/hazyresearch/ncm-checkpoints/blob/main/file.yaml"),
        )
        self.assertEqual(
            ("documentation", "https://huggingface.co/docs/diffusers/main"),
            normalize_public_url("https://huggingface.co/docs/diffusers/main"),
        )

    def test_local_private_placeholder_and_credential_urls_are_excluded(self):
        for url in (
            "http://127.0.0.1:8765/api/status",
            "http://localhost:3000",
            "http://192.168.1.7/dashboard",
            "https://api_key:secret@example.org/api",
            "https://example.com/placeholder",
            "https://github.com/your-org/placeholder",
            "https://github.com/ihatesirdavi/notes?token=private",
            "https://www.youtube.com/watch?v=26P1KyvrmjI&access_token=secret",
        ):
            with self.subTest(url=url):
                self.assertIsNone(normalize_public_url(url))

    def test_scanner_deduplicates_and_emits_no_private_note_text_or_paths(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t) / "private notes"
            root.mkdir()
            (root / "source.md").write_text(
                "SECRET_NOTE_BODY private details\n"
                "https://arxiv.org/abs/2610.14162\n"
                "https://arxiv.org/pdf/2610.14162.pdf\n"
                "https://github.com/3b1b/captions/blob/main/captions.srt\n"
                "http://localhost:8765\n", encoding="utf-8"
            )
            config = Path(t) / "private-config.json"
            config.write_text(json.dumps({
                "schema": "public-research-sources-config-v1",
                "roots": [{"label": "Research", "path": str(root)}],
                "max_files_per_root": 15,
            }), encoding="utf-8")
            found = discover_from_config(config)
            self.assertEqual(2, found["candidate_count"])
            self.assertEqual({"arxiv_paper", "github_repo"},
                             {x["kind"] for x in found["candidates"]})
            self.assertEqual(2, next(x["mentions"] for x in found["candidates"]
                                     if x["kind"] == "arxiv_paper"))
            serialized = json.dumps(found)
            self.assertNotIn("SECRET_NOTE_BODY", serialized)
            self.assertNotIn("private notes", serialized)
            self.assertNotIn("source.md", serialized)
            self.assertNotIn("127.0.0.1", serialized)

    def test_scanner_does_not_follow_symlink_outside_approved_root(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t) / "selected"
            other = Path(t) / "outside"
            root.mkdir()
            other.mkdir()
            (other / "secret.md").write_text("https://github.com/secret/other",
                                              encoding="utf-8")
            try:
                (root / "shortcut").symlink_to(other, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink privilege not available")
            config = Path(t) / "source-config.json"
            config.write_text(json.dumps({
                "schema": "public-research-sources-config-v1",
                "roots": [{"label": "OnlySelected", "path": str(root)}],
            }), encoding="utf-8")
            report = discover_from_config(config)
            self.assertEqual(0, report["candidate_count"])

    def test_config_rejects_invalid_or_duplicate_source_labels(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "sources.json"
            for roots in (
                [{"label": "x", "path": t}, {"label": "x", "path": t}],
                [{"label": "../escape", "path": t}],
                [{"label": "missing", "path": str(Path(t) / "does-not-exist")}],
            ):
                with self.subTest(roots=roots):
                    path.write_text(json.dumps({
                        "schema": "public-research-sources-config-v1", "roots": roots
                    }), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        discover_from_config(path)

    def test_immutable_archive_and_atomic_latest(self):
        with tempfile.TemporaryDirectory() as t:
            result = {
                "schema": "public-research-sources-review-v1", "candidate_count": 1,
                "candidates": [{"kind": "arxiv_paper", "public_url": "https://arxiv.org/abs/2610.14162"}],
            }
            archive, latest = write_source_snapshot(Path(t), result, "2026-11-20T14:00:00+00:00")
            self.assertEqual(archive.read_bytes(), latest.read_bytes())
            self.assertEqual(1, len([p for p in Path(t).glob("source-review-*.json") if p.name != "source-review-latest.json"]))
            with self.assertRaises(FileExistsError):
                write_source_snapshot(Path(t), result, "2026-11-20T14:00:00+00:00")

    def test_optional_discovery_does_not_modify_existing_output_when_absent(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)
            summary = run_optional_discovery(out, "2026-11-20T14:00:00+00:00")
            self.assertEqual("NOT_CONFIGURED", summary["status"])
            self.assertEqual([], list(out.iterdir()))

    def test_invalid_optional_config_is_unverified_without_partial_snapshot(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)
            (out / "public-research-sources-config.json").write_text("{invalid", encoding="utf-8")
            summary = run_optional_discovery(out, "2026-11-20T14:00:00+00:00")
            self.assertEqual("UNVERIFIED", summary["status"])
            self.assertEqual([], list(out.glob("source-review-*.json")))



    def test_markdown_channel_link_has_no_fence_or_bold_punctuation(self):
        self.assertEqual(
            ("youtube_channel", "https://www.youtube.com/@tricktheorists"),
            normalize_public_url("https://www.youtube.com/@tricktheorists)**"),
        )

    def test_notion_workspaces_are_not_public_research_citations(self):
        self.assertIsNone(
            normalize_public_url("https://app.notion.com/p/4066d9751a5481568218e4e29cd92074")
        )

    def test_query_identified_public_sources_keep_only_safe_public_ids(self):
        self.assertEqual(
            ("academic_reference", "https://openreview.net/pdf?id=abcdefG123"),
            normalize_public_url("https://openreview.net/pdf?id=abcdefG123&utm_source=research"),
        )
        self.assertEqual(
            ("community_secondary_source", "https://steamcommunity.com/sharedfiles/filedetails/?id=250456788"),
            normalize_public_url("https://steamcommunity.com/sharedfiles/filedetails/?id=250456788&searchtext=private"),
        )
        self.assertIsNone(normalize_public_url("https://openreview.net/pdf"))

if __name__ == "__main__":
    unittest.main()

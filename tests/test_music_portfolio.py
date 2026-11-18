"""Public music work requires links, provenance, and honest release boundaries."""

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_music_portfolio import validate_music_portfolio


class MusicPortfolioTests(unittest.TestCase):
    def test_catalog_is_valid(self):
        self.assertEqual([], validate_music_portfolio(ROOT))

    def test_public_producer_catalog_has_evidence_and_no_unverified_collaboration(self):
        catalog = json.loads(
            (ROOT / "portfolio" / "public-music.json").read_text(encoding="utf-8")
        )
        self.assertEqual(1, catalog["schema_version"])
        self.assertGreaterEqual(len(catalog["works"]), 1)
        item = next(work for work in catalog["works"] if work["id"] == "saint-saiten-beats")
        self.assertEqual("saint-saiten-beats", item["id"])
        self.assertEqual("producer_catalog", item["kind"])
        self.assertEqual("https://traktrain.com/saintsaiten", item["url"])
        self.assertEqual("link_only", item["media_rights"])
        self.assertEqual("pending", item["owner_review"])
        self.assertEqual("public_listing", item["source_status"])
        self.assertNotIn("collaboration", item["credit_role"].lower())

    def test_profile_contains_a_real_music_link_not_a_placeholder(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Selected music and media", readme)
        self.assertIn("https://traktrain.com/saintsaiten", readme)
        self.assertIn("Saint Saiten", readme)
        self.assertIn('href="#selected-music-and-media"', readme)
        self.assertNotIn("Coming soon!", readme)

    def test_public_producer_credit_is_first_featured_work(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        section = readme.split("## Featured public work", 1)[1]
        self.assertIn("[**Saint Saiten / producer catalog**]", section)
        self.assertLess(
            section.index("[**Saint Saiten / producer catalog**]"),
            section.index("[**SIGNAL-001 / Preview Lab**]")
        )
    def test_sensitive_identity_and_other_project_brands_not_published(self):
        data = (ROOT / "portfolio" / "public-music.json").read_text(encoding="utf-8")
        doc = (ROOT / "docs" / "music-portfolio-evidence.md").read_text(encoding="utf-8")
        combined = (ROOT / "README.md").read_text(encoding="utf-8") + data + doc
        for forbidden in ("Da'Vion", "Maurice Archie", "Lucky Number Media",
                          "PDC-", "SRL-", "ANF Control", "private recording"):
            self.assertNotIn(forbidden, combined)

    def test_evidence_document_maintains_admission_gate(self):
        doc = (ROOT / "docs" / "music-portfolio-evidence.md").read_text(encoding="utf-8")
        for term in ("2026-11-18", "independent source", "role", "rights",
                     "owner review", "Saint Saiten", "not an endorsement"):
            self.assertIn(term.lower(), doc.lower())

    def test_validator_rejects_insecure_or_unsupported_urls(self):
        import tempfile
        import shutil
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "portfolio").mkdir()
            source = ROOT / "portfolio" / "public-music.json"
            content = json.loads(source.read_text(encoding="utf-8"))
            content["works"][0]["url"] = "http://localhost:9000/private"
            (root / "portfolio" / "public-music.json").write_text(
                json.dumps(content), encoding="utf-8"
            )
            (root / "README.md").write_text(
                "## Selected music and media\n", encoding="utf-8"
            )
            self.assertTrue(validate_music_portfolio(root))


if __name__ == "__main__":
    unittest.main()
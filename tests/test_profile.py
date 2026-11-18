"""Tests for the public GitHub profile README and local assets."""

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_profile import validate_profile


class ProfileValidationTests(unittest.TestCase):
    def test_current_profile_is_valid(self):
        self.assertEqual([], validate_profile(ROOT))

    def test_missing_local_image_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                '![Missing banner](assets/missing.svg)\n', encoding="utf-8"
            )
            errors = validate_profile(root)
            self.assertTrue(any("missing" in error.lower() for error in errors), errors)

    def test_malformed_svg_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            (root / "README.md").write_text(
                '![Banner](assets/hero.svg)\n', encoding="utf-8"
            )
            (root / "assets" / "hero.svg").write_text(
                "<svg><broken></svg>", encoding="utf-8"
            )
            errors = validate_profile(root)
            self.assertTrue(any("svg" in error.lower() for error in errors), errors)


    def test_function_first_tagline_and_public_preview_link(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("\u201cI code sometimes\u2026\u201d", content)
        self.assertIn("SIGNAL-001", content)
        self.assertIn("https://ihatesirdavi.github.io/preview-lab/", content)

    def test_public_dynamics_study_is_linked_without_release_claim(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("DYNAMICS-002", content)
        self.assertIn("https://ihatesirdavi.github.io/preview-lab/dynamics.html", content)
        self.assertIn("preview-lab/main/docs/dynamics-still.png", content)
        self.assertIn("owner review pending", content.lower())
        self.assertNotIn("Lucky Number Media", content)
    def test_real_preview_image_is_linked(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("preview-lab/main/docs/preview-still.png", content)

    def test_banner_tagline_animation_is_bounded(self):
        banner = (ROOT / "assets" / "hero-music-systems.gif").read_bytes()
        self.assertTrue(banner.startswith(b"GIF89a"))
        self.assertLess(len(banner), 9_000_000)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("\u201cI code sometimes\u2026\u201d", readme)
        self.assertIn("assets/hero-music-systems.gif", readme)

if __name__ == "__main__":
    unittest.main()

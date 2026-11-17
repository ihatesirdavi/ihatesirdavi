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


if __name__ == "__main__":
    unittest.main()

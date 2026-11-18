"""Characterization and new acceptance contract for the musician-to-systems hero."""

import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MusicHeroTests(unittest.TestCase):
    def test_readme_replaces_svg_with_existing_project_backed_banner(self):
        readme=(ROOT/"README.md").read_text(encoding="utf-8")
        self.assertIn('src="assets/hero-music-systems.gif"',readme)
        self.assertNotIn('src="assets/hero.svg"',readme)
        self.assertIn("assets/hero-music-systems.png",readme)

    def test_profile_leads_with_music_production_as_design_foundation(self):
        readme=(ROOT/"README.md").read_text(encoding="utf-8").lower()
        self.assertIn("recording artist",readme)
        self.assertIn("music producer",readme)
        self.assertIn("arrangement",readme)
        self.assertIn("signal flow",readme)
        self.assertIn("systems architecture",readme)
        self.assertIn("fl studio",readme)
        self.assertNotIn("lucky number media",readme)

    def test_banner_assets_have_expected_dimensions(self):
        png=ROOT/"assets"/"hero-music-systems.png"
        gif=ROOT/"assets"/"hero-music-systems.gif"
        self.assertTrue(png.is_file())
        self.assertTrue(gif.is_file())
        image=png.read_bytes()
        self.assertTrue(image.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual((1600,470),struct.unpack(">II",image[16:24]))
        binary=gif.read_bytes()
        self.assertIn(binary[:6],(b"GIF89a",b"GIF87a"))
        self.assertEqual((1600,470),struct.unpack("<HH",binary[6:10]))
        self.assertLess(gif.stat().st_size,9_000_000)

    def test_source_provenance_not_logo_counterfeit(self):
        guide=(ROOT/"docs"/"hero-provenance.md").read_text(encoding="utf-8")
        self.assertIn("SIGNAL-001",guide)
        self.assertIn("DYNAMICS-002",guide)
        self.assertIn("original logo",guide.lower())
        self.assertIn("review pending",guide.lower())


if __name__=="__main__":
    unittest.main()
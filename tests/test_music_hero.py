"""Characterization and new acceptance contract for the musician-to-systems hero."""

import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MusicHeroTests(unittest.TestCase):
    def test_existing_ci_installs_renderer_dependency(self):
        workflow=(ROOT/".github"/"workflows"/"validate.yml").read_text(encoding="utf-8")
        self.assertIn("python -m pip install Pillow==11.1.0",workflow)
        self.assertIn("python -m unittest discover -s tests -v",workflow)
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

    def test_banner_uses_a_single_studio_inspired_visual_not_preview_images(self):
        renderer=(ROOT/"scripts"/"render_music_hero.py").read_text(encoding="utf-8")
        for forbidden in ("rounded_preview(", "hero-source-signal.png",
                          "hero-source-dynamics.png", "def draw_routing(",
                          "def draw_orbits(", "def curved_route("):
            self.assertNotIn(forbidden, renderer)
        for expected in ("draw_arrangement(", "draw_signal(", "draw_automation("):
            self.assertIn(expected, renderer)
        self.assertFalse((ROOT/"assets"/"hero-source-signal.png").exists())
        self.assertFalse((ROOT/"assets"/"hero-source-dynamics.png").exists())

    def test_music_signal_and_control_envelope_are_deterministic(self):
        import sys
        sys.path.insert(0,str(ROOT/"scripts"))
        from render_music_hero import signal_samples, automation_curve
        self.assertEqual(signal_samples(0.0), signal_samples(0.0))
        self.assertEqual(automation_curve(), automation_curve())
        self.assertGreater(len(automation_curve()),100)
        self.assertTrue(all(abs(v)<=1 for v in signal_samples(0.0)))

    def test_studio_visual_survives_github_scale(self):
        """Production-grid visuals must remain readable at 800px wide."""
        from PIL import Image
        with Image.open(ROOT/"assets"/"hero-music-systems.png") as im:
            tiny=im.convert("RGB").resize((800,235),Image.Resampling.LANCZOS).convert("L")
            box=tiny.crop((350,70,780,215))
            self.assertGreater(sum(v>100 for v in box.getdata()),1800)
    def test_does_not_invent_a_decorative_pseudo_logo(self):
        renderer=(ROOT/"scripts"/"render_music_hero.py").read_text(encoding="utf-8")
        self.assertNotIn("Three diagonal strokes from the prior creator design guide",renderer)
        self.assertIn("RECORDING ARTIST",renderer)
    def test_background_grid_remains_visually_subordinate(self):
        from PIL import Image
        with Image.open(ROOT/"assets"/"hero-music-systems.png") as im:
            im=im.convert("RGB")
            # This crosses the right-side design grid, above the foreground artwork.
            grid=im.getpixel((717,106))
            ground=im.getpixel((718,107))
            self.assertLess(max(abs(a-b) for a,b in zip(grid,ground)),20)
    def test_animated_gif_has_finite_visible_motion(self):
        from PIL import Image, ImageChops
        with Image.open(ROOT/"assets"/"hero-music-systems.gif") as gif:
            self.assertEqual(1,gif.info.get("loop"))
            self.assertLessEqual(gif.n_frames,36)
            gif.seek(0)
            start=gif.convert("RGB")
            gif.seek(min(5,gif.n_frames-1))
            later=gif.convert("RGB")
            self.assertIsNotNone(ImageChops.difference(start,later).getbbox())
    def test_source_provenance_not_logo_counterfeit(self):
        guide=(ROOT/"docs"/"hero-provenance.md").read_text(encoding="utf-8")
        self.assertIn("SIGNAL-001",guide)
        self.assertIn("DYNAMICS-002",guide)
        self.assertIn("original logo",guide.lower())
        self.assertIn("review pending",guide.lower())


if __name__=="__main__":
    unittest.main()
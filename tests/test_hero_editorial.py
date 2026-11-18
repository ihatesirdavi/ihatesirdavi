"""Editorial brand direction: music-first layout, no diagram pretending to connect fields."""

from pathlib import Path
from PIL import Image
import unittest
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import render_music_hero as hero

class EditorialHeroContract(unittest.TestCase):
    def test_source_does_not_draw_literal_routing_or_orbits(self):
        source=(ROOT/"scripts"/"render_music_hero.py").read_text(encoding="utf-8")
        for old in ("def draw_routing(", "def draw_orbits(", "def curved_route(", "def glow_dot(", '"02  /  ROUTE"', '"03  /  EVOLVE"'):
            self.assertNotIn(old,source)
        for required in ("def draw_arrangement(", "def draw_signal(", "def draw_automation(", "def typography("):
            self.assertIn(required,source)

    def test_music_signal_and_automation_are_deterministic(self):
        self.assertEqual(hero.signal_samples(0),hero.signal_samples(0))
        self.assertEqual(hero.automation_curve(),hero.automation_curve())
        self.assertGreater(len(hero.automation_curve()),30)
        self.assertTrue(all(-1<=p<=1 for p in hero.signal_samples(0)))

    def test_typography_and_visual_layers_respect_separate_reading_areas(self):
        text=Image.new("RGBA",hero.SIZE,(0,0,0,0))
        hero.typography(text)
        draw=Image.new("RGBA",hero.SIZE,(0,0,0,0))
        hero.draw_arrangement(draw)
        hero.draw_signal(draw,0)
        hero.draw_automation(draw,0)
        # Keep all decorative ink out of the identity column and written copy off tracks.
        self.assertGreaterEqual(draw.getchannel("A").getbbox()[0],635)
        self.assertLessEqual(text.getchannel("A").getbbox()[2],630)

    def test_github_size_composition_is_readable(self):
        with Image.open(ROOT/"assets"/"hero-music-systems.png") as im:
            gray=im.convert("RGB").resize((800,235),Image.Resampling.LANCZOS).convert("L")
            region=gray.crop((350,70,780,215))
            self.assertGreater(sum(px>100 for px in region.getdata()),1800)

if __name__=="__main__":
    unittest.main()
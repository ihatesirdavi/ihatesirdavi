"""Regression: separate visual stage footprints while keeping a continuous signal."""

import sys
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import render_music_hero as hero


def masks():
    layers = []
    for drawer in (
        lambda image: hero.draw_signal_flow(image, 0),
        hero.draw_routing,
        lambda image: hero.draw_orbits(image, hero.orbital_paths_cached(), 0),
    ):
        layer = Image.new("RGBA", hero.SIZE, (0, 0, 0, 0))
        drawer(layer)
        layers.append(layer.getchannel("A"))
    return layers


def collisions(a, b, threshold=50):
    return sum(
        1 for pa, pb in zip(a.getdata(), b.getdata())
        if pa > threshold and pb > threshold
    )


class VisualOverlapTests(unittest.TestCase):
    def test_audio_transition_does_not_write_over_routing(self):
        signal, routing, _ = masks()
        self.assertLess(
            collisions(signal, routing), 75,
            "Wave and branching node paths have collided instead of handing off."
        )

    def test_routes_do_not_draw_through_orbital_paths(self):
        _, routing, orbit = masks()
        self.assertLess(
            collisions(routing, orbit), 50,
            "Routing connectors should reach the orbital field, not cross it."
        )

    def test_stages_occupy_separate_horizontal_regions(self):
        signal, routing, orbit = masks()
        self.assertLessEqual(signal.getbbox()[2], 1125)
        self.assertLessEqual(routing.getbbox()[2], 1400)
        self.assertGreaterEqual(orbit.getbbox()[0], 1375)

    def test_no_preview_panels_or_unverified_brand_logo(self):
        source = (ROOT / "scripts" / "render_music_hero.py").read_text(encoding="utf-8")
        self.assertNotIn("hero-source-signal.png", source)
        self.assertNotIn("rounded_preview(", source)


if __name__ == "__main__":
    unittest.main()
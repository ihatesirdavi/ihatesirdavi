"""Public-only GitHub activity graph contract tests."""

from datetime import date
import sys
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_public_activity import summarize_public_events, render_svg, public_events_url


class ActivityTests(unittest.TestCase):
    def test_public_events_only_with_exact_28_day_window(self):
        events = [
            {"public": True, "created_at": "2026-11-17T12:00:00Z", "type": "PushEvent"},
            {"public": True, "created_at": "2026-11-16T22:59:59Z", "type": "PullRequestEvent"},
            {"public": False, "created_at": "2026-11-16T12:00:00Z", "type": "PushEvent"},
            {"public": True, "created_at": "2026-10-20T09:00:00Z", "type": "IssuesEvent"},
            {"public": True, "created_at": "2026-10-19T09:00:00Z", "type": "PushEvent"},
        ]
        daily = summarize_public_events(events, date(2026, 11, 17), 28)
        self.assertEqual(28, len(daily))
        self.assertEqual(date(2026, 10, 21), daily[0][0])
        self.assertEqual(0, daily[0][1])
        self.assertEqual(1, daily[-2][1])
        self.assertEqual(1, daily[-1][1])
        self.assertEqual(2, sum(amount for _, amount in daily))

    def test_generated_svg_is_parseable_and_describes_scope(self):
        series = summarize_public_events(
            [{"public": True, "created_at": "2026-11-17T12:00:00Z"}],
            date(2026, 11, 17), 28
        )
        svg = render_svg(series, "ihatesirdavi")
        ET.fromstring(svg)
        self.assertIn("Public GitHub events", svg)
        self.assertIn("28 days", svg)
        self.assertIn("ihatesirdavi", svg)
        self.assertNotIn("GITHUB_TOKEN", svg)

    def test_public_endpoint_never_fetches_private_activity(self):
        url = public_events_url("ihatesirdavi", 2)
        self.assertEqual(
            "https://api.github.com/users/ihatesirdavi/events/public?per_page=100&page=2",
            url
        )
        with self.assertRaises(ValueError):
            public_events_url("../other-user", 1)


if __name__ == "__main__":
    unittest.main()

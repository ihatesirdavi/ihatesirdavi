"""Render recent public GitHub events as a self-contained SVG.

Only /users/{login}/events/public is queried. This does not measure every
GitHub contribution or include private repository details.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

USER_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")

def public_events_url(username: str, page: int) -> str:
    if not USER_PATTERN.fullmatch(username):
        raise ValueError("Invalid GitHub username")
    if not 1 <= page <= 3:
        raise ValueError("Public events page must be in 1..3")
    return (f"https://api.github.com/users/{username}/events/public"
            f"?per_page=100&page={page}")

def fetch_public_events(username: str) -> list[dict]:
    """Read at most 300 recent public events. Fail rather than fake freshness."""
    events: list[dict] = []
    for page in range(1, 4):
        request = Request(
            public_events_url(username, page),
            headers={"Accept": "application/vnd.github+json",
                     "User-Agent": "profile-public-events-chart"}
        )
        with urlopen(request, timeout=20) as response:
            chunk = json.load(response)
        if not isinstance(chunk, list):
            raise ValueError("GitHub returned an unexpected public events payload")
        events.extend(chunk)
        if len(chunk) < 100:
            break
    return events

def summarize_public_events(
    events: list[dict], as_of: date, days: int = 28
) -> list[tuple[date, int]]:
    if not 1 <= days <= 60:
        raise ValueError("days must be in 1..60")
    start = as_of - timedelta(days=days - 1)
    counts = {start + timedelta(days=i): 0 for i in range(days)}
    for event in events:
        if not isinstance(event, dict) or event.get("public") is False:
            continue
        timestamp = event.get("created_at")
        if not isinstance(timestamp, str):
            continue
        try:
            day = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            ).astimezone(timezone.utc).date()
        except (ValueError, TypeError):
            continue
        if day in counts:
            counts[day] += 1
    return sorted(counts.items())

def render_svg(series: list[tuple[date, int]], username: str) -> str:
    if not series:
        raise ValueError("Cannot draw an empty series")
    if not USER_PATTERN.fullmatch(username):
        raise ValueError("Invalid GitHub username")
    count = sum(value for _, value in series)
    scale = max(1, max(value for _, value in series))
    plot_x, plot_w, baseline = 58, 1084, 237
    gap = 8
    bar_w = (plot_w - (len(series) - 1) * gap) / len(series)
    bars, markers = [], []
    for index, (day, value) in enumerate(series):
        x = plot_x + index * (bar_w + gap)
        height = (value / scale) * 115 if value else 3
        y = baseline - height
        bars.append(
            f'<g><title>{day.isoformat()}: {value} public events</title>'
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}"'
            f' height="{height:.2f}" rx="3"'
            f' fill="url(#bar)" opacity="{0.92 if value else 0.22}"/></g>'
        )
        if index % 7 == 0 or index == len(series)-1:
            markers.append(
                f'<text x="{x:.2f}" y="263" font-size="12"'
                f' fill="#94a3b8">{day.strftime("%b %d")}</text>'
            )
    safe_user = escape(username)
    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="285" viewBox="0 0 1200 285" role="img" aria-labelledby="title desc">',
        f'<title id="title">Public GitHub events for {safe_user}</title>',
        f'<desc id="desc">Recent public activity, {len(series)} days from {series[0][0]} to {series[-1][0]}; {count} public events. These are not GitHub contribution counts.</desc>',
        '<defs>',
        '<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0a1223"/><stop offset="1" stop-color="#151738"/></linearGradient>',
        '<linearGradient id="bar" x2="0" y2="1"><stop stop-color="#60f2db"/><stop offset="1" stop-color="#a78bfa"/></linearGradient>',
        '</defs>',
        '<rect width="1200" height="285" rx="19" fill="url(#bg)"/>',
        '<rect x="26" y="26" width="1148" height="233" rx="12" fill="none" stroke="#64748b" stroke-opacity=".2"/>',
        '<text x="58" y="60" font-family="Consolas, sans-serif" font-size="23" fill="#f1f5f9" font-weight="bold">PUBLIC GITHUB EVENTS</text>',
        f'<text x="1142" y="60" text-anchor="end" font-family="Consolas, sans-serif" font-size="17" fill="#8eeada">{count} events / {len(series)} days</text>',
        '<text x="58" y="82" font-family="Consolas, sans-serif" font-size="12" fill="#94a3b8">Public event feed, not total contribution counts · refreshed by GitHub Actions</text>',
        '<path d="M58 237H1142" stroke="#94a3b8" stroke-opacity=".27"/>',
        '<g font-family="Consolas, sans-serif">',
        *bars, *markers, '</g>', '</svg>'
    ]) + "\n"

def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--username", default="ihatesirdavi")
    cli.add_argument("--days", type=int, default=28)
    cli.add_argument("--output", type=Path, default=Path("assets/public-activity.svg"))
    cli.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    cli.add_argument("--events-json", type=Path, help="Offline fixture for local testing")
    args = cli.parse_args()
    if args.events_json:
        events = json.loads(args.events_json.read_text(encoding="utf-8"))
    else:
        events = fetch_public_events(args.username)
    series = summarize_public_events(events, args.as_of, args.days)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_svg(series, args.username), encoding="utf-8")
    print(f"Public activity SVG: {sum(v for _, v in series)} events in {args.days} days")

if __name__ == "__main__":
    main()

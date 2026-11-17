# Lesson 03: Build a public GitHub activity graphic

**Source:** [scripts/render_public_activity.py](../../scripts/render_public_activity.py)
**Tests:** [tests/test_public_activity.py](../../tests/test_public_activity.py)
**Output:** [assets/public-activity.svg](../../assets/public-activity.svg)

## Mechanism

1. Ask GitHub for recent public events, not access to private repositories.
2. Parse the created_at timestamp into a UTC date.
3. Build a fixed 28-day window and count matching events for each day.
4. Render those numbers as SVG bars using ordinary Python strings.
5. Parse the result as XML to catch malformed output.
6. Refresh it using an existing GitHub Actions runner twice a week.

The graph measures public events, not GitHub's contribution calendar. One PushEvent can represent several commits, and some work may not appear in the API's most recent 300 events. Do not relabel this chart "commits" or "all contributions."

## Practice

- Run the unit tests: python -m unittest discover -s tests -v
- Read summarize_public_events. Change the window from 28 to 14 days and update the tests before changing the code.
- Add a fake private event with public set to false in the test data. Explain why it must not increase the count.
- Temporarily break the SVG root tag, then run python scripts/validate_profile.py. Revert it.
- Inspect update-public-activity.yml. Why does only the updater need contents: write while the validator uses read-only permissions?

## Evidence distinctions

- A unit test verifies algorithm behavior for controlled inputs.
- XML parsing verifies the SVG is syntactically valid.
- A successful live fetch verifies GitHub's public endpoint responded with real events.
- A successful Actions run verifies the update workflow executed.
- An actual profile screenshot verifies rendered appearance; source tests alone cannot.

### Questions

Why do we use UTC rather than whatever time zone the runner happens to use? What can go wrong if a network error silently becomes a zero chart? What happens when an API only exposes a limited event history?

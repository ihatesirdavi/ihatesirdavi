"""Validate publicly showcased music evidence without claiming owner approvals.

Offline and deterministic, used by the existing profile CI workflow.
"""

from pathlib import Path
import json
import re
from urllib.parse import urlparse

ALLOWED_HOSTS = {"traktrain.com"}


def validate_music_portfolio(root: Path) -> list[str]:
    errors: list[str] = []
    portfolio = root / "portfolio" / "public-music.json"
    readme = root / "README.md"
    if not portfolio.is_file():
        return ["missing portfolio/public-music.json"]
    if not readme.is_file():
        return ["missing README.md"]
    try:
        data = json.loads(portfolio.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"music portfolio JSON unreadable: {exc}"]

    if data.get("schema_version") != 1:
        errors.append("unsupported public music portfolio schema_version")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(data.get("verified_on", ""))):
        errors.append("verified_on date missing or malformed")
    works = data.get("works")
    if not isinstance(works, list) or not works:
        return errors + ["music portfolio works must be a nonempty list"]

    body = readme.read_text(encoding="utf-8")
    if "## Selected music and media" not in body:
        errors.append("public music section missing from README")

    seen: set[str] = set()
    required = {
        "id", "title", "kind", "credit_role", "url", "source_status",
        "source_observation", "attribution_note", "media_rights", "owner_review"
    }
    for index, work in enumerate(works):
        if not isinstance(work, dict):
            errors.append(f"work {index} must be an object")
            continue
        missing = required - work.keys()
        if missing:
            errors.append(f"work {index} missing fields: {sorted(missing)}")
            continue
        item_id = work["id"]
        if not isinstance(item_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,63}", item_id):
            errors.append(f"invalid work id at {index}")
        elif item_id in seen:
            errors.append(f"duplicate music work id {item_id}")
        seen.add(item_id)

        url = str(work["url"])
        parsed = urlparse(url)
        if (
            parsed.scheme != "https"
            or (parsed.hostname or "").lower() not in ALLOWED_HOSTS
            or parsed.username or parsed.password
            or parsed.query or parsed.fragment
        ):
            errors.append(f"work {item_id} has unapproved or insecure URL")
        if work["media_rights"] != "link_only":
            errors.append(f"work {item_id} media reuse not cleared")
        if work["source_status"] != "public_listing":
            errors.append(f"work {item_id} source not admitted as public")
        if work["owner_review"] not in {"pending", "approved"}:
            errors.append(f"work {item_id} owner review status invalid")
        if url not in body:
            errors.append(f"work {item_id} URL not featured in README")
        if not all(isinstance(work[key], str) and work[key].strip() for key in required):
            errors.append(f"work {item_id} has empty metadata")
        if "collaboration" not in str(work["attribution_note"]).lower():
            errors.append(f"work {item_id} lacks anti-misattribution note")

    return errors


if __name__ == "__main__":
    issues = validate_music_portfolio(Path(__file__).resolve().parents[1])
    for issue in issues:
        print("FAIL:", issue)
    if issues:
        raise SystemExit(1)
    print("Public music portfolio evidence validation passed")
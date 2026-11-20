"""Verify public GitHub repository references in profile Markdown via read-only API.

Local asset checks remain in validate_profile.py. This network check only
confirms that linked repository URLs resolve to public, canonical repositories.
Tests inject a fake API lookup and never access the network.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


REPO_URL = re.compile(
    r"https?://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/([A-Za-z0-9_.-]+)",
    re.IGNORECASE,
)


def collect_references(root: Path) -> dict[tuple[str, str], set[str]]:
    """Return each referenced public GitHub repository and source Markdown paths."""
    root = root.resolve()
    files = [root / "README.md"]
    docs = root / "docs"
    if docs.is_dir():
        files.extend(sorted(docs.rglob("*.md")))
    found: dict[tuple[str, str], set[str]] = {}
    for path in files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        for match in REPO_URL.finditer(text):
            owner, name = match.groups()
            name = name.rstrip(".,")
            if name.lower().endswith(".git"):
                name = name[:-4]
            if not name:
                continue
            found.setdefault((owner, name), set()).add(
                str(path.relative_to(root)).replace("\\", "/")
            )
    return found


def fetch_github_repository(owner: str, name: str) -> dict:
    """Read GitHub's public repository endpoint with an optional Actions token."""
    url = f"https://api.github.com/repos/{quote(owner)}/{quote(name)}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "public-profile-repository-reference-check",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GH_PUBLIC_LINKS_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    with urlopen(Request(url, headers=headers, method="GET"), timeout=10) as response:
        result = json.load(response)
    if not isinstance(result, dict):
        raise ValueError("unexpected GitHub API response")
    return result


def validate_repositories(root: Path, fetcher=None) -> list[str]:
    """Fail closed for missing/renamed/private repos; distinguish API outages."""
    fetcher = fetcher or fetch_github_repository
    refs = collect_references(root)
    if not refs:
        return ["no GitHub repository references found"]

    errors = []
    for (owner, repo), locations in sorted(refs.items(), key=lambda item: (item[0][0].lower(), item[0][1].lower())):
        label = f"{owner}/{repo}"
        sources = ", ".join(sorted(locations))
        try:
            info = fetcher(owner, repo)
        except HTTPError as error:
            if error.code == 404:
                errors.append(f"{sources}: missing or inaccessible public GitHub repository: {label}")
            else:
                errors.append(f"{sources}: unverified GitHub repository {label} (HTTP {error.code})")
            continue
        except (URLError, TimeoutError, OSError, ValueError) as error:
            errors.append(f"{sources}: unverified GitHub repository {label} ({type(error).__name__})")
            continue

        actual = info.get("full_name") if isinstance(info, dict) else None
        if not isinstance(actual, str) or not actual:
            errors.append(f"{sources}: unverified GitHub repository {label} (no canonical name)")
        elif actual.casefold() != label.casefold():
            errors.append(f"{sources}: noncanonical GitHub repository link {label}, canonical {actual}")
        elif info.get("private") is not False:
            errors.append(f"{sources}: private or unverified public visibility for GitHub repository {label}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1],
        help="profile repository root",
    )
    args = parser.parse_args()
    errors = validate_repositories(args.root)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(
        "Public GitHub repository references verified: "
        + str(len(collect_references(args.root)))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
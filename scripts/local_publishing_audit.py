"""Headless LOCAL Python audit of public profile links and upstream PR state.

This program runs on the user's Windows host, not inside ChatGPT Tasks or
GitHub Actions. It reads public GitHub API resources, validates local files,
and writes dated JSON receipts. It cannot publish, merge, or edit repositories.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from validate_profile import validate_profile
from validate_repo_references import (
    collect_references,
    fetch_github_repository,
    validate_repositories,
)


PULL_REQUESTS = (
    ("profile", "ihatesirdavi", "ihatesirdavi", 17),
    ("godot", "Scony", "godot-gdscript-toolkit", 435),
    ("acerolafx", "GarrettGunnell", "AcerolaFX", 64),
)


def fetch_public_pull_request(owner: str, repo: str, number: int) -> dict:
    """Read a known public PR endpoint without acquiring or printing credentials."""
    address = (
        "https://api.github.com/repos/"
        + quote(owner, safe="")
        + "/"
        + quote(repo, safe="")
        + "/pulls/"
        + str(number)
    )
    request = Request(
        address,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "local-public-publishing-audit",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    with urlopen(request, timeout=10) as response:
        data = json.load(response)
    if not isinstance(data, dict):
        raise ValueError("unexpected GitHub pull-request response")
    return data


def local_git_head(root: Path) -> str | None:
    """Capture this checkout's commit without modifying branches or git state."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    head = proc.stdout.strip()
    if len(head) != 40 or any(ch not in "0123456789abcdef" for ch in head.lower()):
        return None
    return head


def audit(
    root: Path, repo_fetch, pr_fetch, validate_local, *,
    now: datetime | None = None, source_head=None,
) -> dict:
    """Create factual audit data without local or remote write side effects."""
    root = root.resolve()
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("audit timestamp must have an explicit timezone")
    errors: list[str] = []
    failures = False
    uncertain = False

    local_errors = validate_local(root)
    if local_errors:
        failures = True
        errors.extend(str(e) for e in local_errors)

    references = collect_references(root)
    ref_errors = validate_repositories(root, repo_fetch)
    for error in ref_errors:
        errors.append(error)
        if (
            "missing or inaccessible" in error
            or "noncanonical" in error
            or "private or" in error
            or "no GitHub repository" in error
        ):
            failures = True
        else:
            uncertain = True

    checked_prs = []
    for label, owner, repo, number in PULL_REQUESTS:
        identifier = f"{owner}/{repo}#{number}"
        try:
            data = pr_fetch(owner, repo, number)
            if not isinstance(data, dict) or data.get("number") != number:
                raise ValueError("unexpected PR metadata")
            state = data.get("state")
            sha = data.get("head", {}).get("sha") if isinstance(data.get("head"), dict) else None
            if state not in ("open", "closed") or not isinstance(sha, str) or len(sha) != 40:
                raise ValueError("missing PR identity/status")
            checked_prs.append(
                {
                    "label": label, "repo": f"{owner}/{repo}", "number": number,
                    "url": f"https://github.com/{owner}/{repo}/pull/{number}",
                    "state": "MERGED" if data.get("merged_at") else (
                        "DRAFT" if data.get("draft") and state == "open" else state.upper()
                    ),
                    "head_sha": sha,
                    "mergeability_hint": data.get("mergeable_state"),
                    "updated_at": data.get("updated_at"),
                    "review_acceptance": "NOT_CHECKED",  # merge state is not a review check
                }
            )
        except HTTPError as exc:
            uncertain = True
            errors.append(f"unverified public PR {identifier} (HTTP {exc.code})")
        except (URLError, OSError, TimeoutError, ValueError, TypeError) as exc:
            uncertain = True
            errors.append(f"unverified public PR {identifier} ({type(exc).__name__})")

    status = "FAIL" if failures else ("UNVERIFIED" if uncertain else "PASS")
    head_getter = source_head or local_git_head
    return {
        "schema": "local-publishing-audit-v1",
        "executor": "LOCAL_PYTHON",
        "checked_at_utc": now.astimezone(timezone.utc).isoformat(),
        "status": status,
        "source_head": head_getter(root),
        "readme_sha256": hashlib.sha256((root / "README.md").read_bytes()).hexdigest() if (root / "README.md").is_file() else None,
        "audit_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "repository_count": len(references),
        "repositories_checked": [f"{owner}/{repo}" for owner, repo in sorted(references)],
        "pull_requests": checked_prs,
        "errors": errors,
        "changes_published": False,
        "owner_release_accepted": False,
        "read_only": True,
    }


def write_receipt(output_dir: Path, data: dict) -> tuple[Path, Path]:
    """Write one immutable dated file, then atomically replace latest.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.fromisoformat(data["checked_at_utc"]).astimezone(timezone.utc)
    archive = output_dir / ("audit-" + stamp.strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    payload = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with archive.open("xb") as handle:
        handle.write(payload)
    latest = output_dir / "latest.json"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, dir=output_dir, prefix=".latest-", suffix=".json",
        ) as temp:
            temp.write(payload)
            temp_path = Path(temp.name)
        os.replace(temp_path, latest)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
    return archive, latest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = audit(
        args.root, fetch_github_repository, fetch_public_pull_request, validate_profile,
    )
    archive, _ = write_receipt(args.output_dir, result)
    print("LOCAL_AUDIT_STATUS=" + result["status"])
    print("LOCAL_AUDIT_RECEIPT=" + str(archive))
    print("PUBLIC_REPOSITORIES_CHECKED=" + str(result["repository_count"]))
    print("PUBLIC_PULL_REQUESTS_CHECKED=" + str(len(result["pull_requests"])))
    return {"PASS": 0, "FAIL": 1, "UNVERIFIED": 2}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
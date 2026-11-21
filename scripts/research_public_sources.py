"""Opt-in read-only PUBLIC source discovery for the existing Windows audit.

Private source paths and text stay local. Only normalized public URLs,
counts and broad source-area labels enter review data. Discovery is not
live verification, endorsement, publishing permission or social consent.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, parse_qsl, urlsplit

URL_RE = re.compile(r"https?://[^\s<>\"'\x60]+", re.I)
DOI_RE = re.compile(r"10\.\d{4,9}/\S+\Z", re.I)
ARXIV_RE = re.compile(r"\d{4}\.\d{4,5}(?:v\d+)?\Z")
VIDEO_RE = re.compile(r"[A-Za-z0-9_-]{11}\Z")
NAME_RE = re.compile(r"[A-Za-z0-9_.-]+\Z")
LABEL_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,39}\Z")
SECRET_KEYS = re.compile(r"token|secret|passw|api.?key|session|signature|auth|credential|jwt", re.I)
HIDDEN = {".git", ".cache", ".venv", "__pycache__", "node_modules",
          "vendor", "target", "dist", "build", "tests", "private", "secrets"}
EXT = {".md", ".rst", ".bib", ".json", ".yml", ".yaml", ".txt"}
BAD_HOSTS = {"localhost", "example.com", "example.org", "example.net",
             "notion.so", "www.notion.so", "drive.google.com",
             "docs.google.com", "gmail.com"}
BAD_OWNERS = {"example", "your-org", "users", "orgs", "issues",
              "pull", "topics", "search", "login", "explore"}


def normalize_public_url(raw: str) -> tuple[str, str] | None:
    raw = raw.strip().rstrip(".,;:!?'\x60\"\x5d}>")
    while raw.endswith(")") and raw.count(")") > raw.count("("):
        raw = raw[:-1]
    raw = raw.rstrip("*")
    while raw.endswith(")") and raw.count(")") > raw.count("("):
        raw = raw[:-1]
    try:
        p = urlsplit(raw)
        host = (p.hostname or "").lower()
        port = p.port
    except ValueError:
        return None
    if p.scheme not in ("http", "https") or not host or p.username or p.password:
        return None
    if port not in (None, 80, 443) or host in BAD_HOSTS:
        return None
    if host.endswith((".local", ".internal", ".invalid", ".test", ".localhost", ".example.com", ".notion.com")):
        return None
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        return None
    try:
        if any(SECRET_KEYS.search(key) for key, _ in parse_qsl(p.query, keep_blank_values=True, max_num_fields=30)):
            return None
    except ValueError:
        return None
    parts = [x for x in p.path.split("/") if x]
    if host in ("github.com", "www.github.com"):
        if len(parts) < 2 or parts[0].lower() in BAD_OWNERS:
            return None
        owner, repo = parts[:2]
        repo = repo.removesuffix(".git")
        if not NAME_RE.fullmatch(owner) or not NAME_RE.fullmatch(repo):
            return None
        kind = "own_github_repo" if owner.lower() in ("ihatesirdavi", "ih8sirdavi") else "github_repo"
        return kind, f"https://github.com/{owner}/{repo}"
    if host == "arxiv.org":
        if len(parts) >= 2 and parts[0] in ("abs", "pdf", "html"):
            item = parts[1].removesuffix(".pdf")
            if ARXIV_RE.fullmatch(item):
                return "arxiv_paper", "https://arxiv.org/abs/" + item
        return None
    if host in ("doi.org", "dx.doi.org"):
        item = p.path.lstrip("/")
        return ("scholarly_doi", "https://doi.org/" + item.lower()) if DOI_RE.fullmatch(item) else None
    if host in ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"):
        if host == "youtu.be" and parts and VIDEO_RE.fullmatch(parts[0]):
            return "youtube_video", "https://www.youtube.com/watch?v=" + parts[0]
        if parts and parts[0] == "watch":
            video = parse_qs(p.query).get("v", [""])[0]
            if VIDEO_RE.fullmatch(video):
                return "youtube_video", "https://www.youtube.com/watch?v=" + video
        if parts and parts[0].startswith("@") and len(parts[0]) > 1:
            return "youtube_channel", "https://www.youtube.com/" + parts[0]
        if len(parts) >= 2 and parts[0] in ("channel", "c", "user"):
            return "youtube_channel", "https://www.youtube.com/" + "/".join(parts[:2])
        return None
    if host == "huggingface.co":
        if len(parts) >= 3 and parts[0] in ("datasets", "spaces"):
            kind = "huggingface_dataset" if parts[0] == "datasets" else "huggingface_space"
            return kind, "https://huggingface.co/" + "/".join(parts[:3])
        if len(parts) >= 2 and parts[0] == "docs":
            return "documentation", "https://huggingface.co/" + "/".join(parts[:3])
        if len(parts) >= 2 and parts[0] not in ("api", "docs", "settings"):
            return "huggingface_model", "https://huggingface.co/" + "/".join(parts[:2])
        return None
    if host == "openreview.net" and p.path in ("/pdf", "/forum"):
        doc_id = parse_qs(p.query).get("id", [""])[0]
        if re.fullmatch(r"[A-Za-z0-9_-]{6,70}", doc_id):
            return "academic_reference", "https://openreview.net" + p.path + "?id=" + doc_id
        return None
    if host in ("steamcommunity.com", "www.steamcommunity.com") and p.path.rstrip("/") == "/sharedfiles/filedetails":
        doc_id = parse_qs(p.query).get("id", [""])[0]
        if re.fullmatch(r"\d{5,20}", doc_id):
            return "community_secondary_source", "https://steamcommunity.com/sharedfiles/filedetails/?id=" + doc_id
        return None
    public_url = p.scheme + "://" + host + (p.path or "/")
    if host.endswith((".gov", ".edu")):
        return "government_or_education", public_url
    if host in ("aclanthology.org", "papers.nips.cc", "openreview.net", "pubmed.ncbi.nlm.nih.gov"):
        return "academic_reference", public_url
    if host in ("developer.mozilla.org", "docs.python.org", "docs.rs", "learn.microsoft.com"):
        return "documentation", public_url
    if host in ("stackoverflow.com", "stackexchange.com"):
        return "community_secondary_source", public_url
    return "public_web_reference", public_url


def discover_from_config(config_file: Path) -> dict:
    raw = config_file.read_bytes()
    config = json.loads(raw)
    if not isinstance(config, dict) or config.get("schema") != "public-research-sources-config-v1":
        raise ValueError("invalid config schema")
    roots = config.get("roots")
    if not isinstance(roots, list) or not 1 <= len(roots) <= 16:
        raise ValueError("source roots must be a nonempty bounded list")
    max_files = config.get("max_files_per_root", 800)
    max_bytes = config.get("max_bytes_per_file", 131072)
    max_candidates = config.get("max_candidates", 3000)
    if any(type(n) is not int for n in (max_files, max_bytes, max_candidates)):
        raise ValueError("source scan limits must be integers")
    if not (1 <= max_files <= 1500 and 1024 <= max_bytes <= 262144 and 1 <= max_candidates <= 5000):
        raise ValueError("out-of-bounds source scan limits")
    approved, labels = [], set()
    for item in roots:
        if not isinstance(item, dict):
            raise ValueError("invalid root entry")
        label, address = item.get("label"), item.get("path")
        if not isinstance(label, str) or not LABEL_RE.fullmatch(label) or label.casefold() in labels:
            raise ValueError("invalid or duplicate root label")
        if not isinstance(address, str):
            raise ValueError("missing source path")
        path = Path(address)
        if not path.is_absolute() or not path.is_dir() or path.is_symlink():
            raise ValueError("root must be an existing, nonsymlink absolute directory")
        labels.add(label.casefold())
        approved.append((label, path))
    records, scanned, skipped = {}, [], Counter()
    truncated = False
    for label, root in approved:
        count = 0
        for dirpath, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = [d for d in sorted(dirs) if d not in HIDDEN and not d.startswith(".")
                       and not (Path(dirpath) / d).is_symlink()]
            for name in sorted(names):
                if count >= max_files:
                    truncated = True
                    break
                path = Path(dirpath) / name
                if path.suffix.lower() not in EXT or path.is_symlink():
                    continue
                try:
                    if path.stat().st_size > max_bytes:
                        skipped["oversize"] += 1
                        continue
                    content = path.read_text(encoding="utf-8-sig", errors="replace")
                except OSError:
                    skipped["unreadable"] += 1
                    continue
                count += 1
                for match in URL_RE.finditer(content):
                    value = normalize_public_url(match.group())
                    if value is None:
                        skipped["excluded"] += 1
                        continue
                    kind, url = value
                    if value not in records:
                        if len(records) >= max_candidates:
                            truncated = True
                            continue
                        records[value] = {"kind": kind, "public_url": url, "mentions": 0, "source_areas": set()}
                    records[value]["mentions"] += 1
                    records[value]["source_areas"].add(label)
            if count >= max_files:
                break
        scanned.append({"label": label, "files_scanned": count})
    candidates = [{
        "kind": record["kind"], "public_url": record["public_url"],
        "mentions": record["mentions"], "source_areas": sorted(record["source_areas"]),
        "verification": "DISCOVERED_NOT_LIVE_VERIFIED", "engagement": "NOT_AUTOMATED",
    } for record in sorted(records.values(), key=lambda item: (item["kind"], item["public_url"]))]
    return {
        "schema": "public-research-sources-review-v1",
        "source_config_sha256": hashlib.sha256(raw).hexdigest(),
        "source_areas_scanned": scanned,
        "candidate_count": len(candidates),
        "counts_by_kind": dict(sorted(Counter(x["kind"] for x in candidates).items())),
        "truncated": truncated,
        "skipped_counts": dict(skipped),
        "candidates": candidates,
        "privacy": "Only public normalized URLs and source labels; no notes, private paths or secrets",
        "acceptance": "Discovery only; not validated, installed, endorsed or approved for engagement.",
    }


def write_source_snapshot(out: Path, data: dict, checked_at_utc: str) -> tuple[Path, Path]:
    stamp = datetime.fromisoformat(checked_at_utc)
    if stamp.tzinfo is None:
        raise ValueError("source timestamp requires timezone")
    out.mkdir(parents=True, exist_ok=True)
    label = stamp.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    archive = out / ("source-review-" + label + ".json")
    payload = (json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with archive.open("xb") as fp:
        fp.write(payload)
    latest = out / "source-review-latest.json"
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=out, prefix=".source-review-", suffix=".json", delete=False) as fp:
            fp.write(payload)
            tmp = Path(fp.name)
        os.replace(tmp, latest)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()
    return archive, latest


def run_optional_discovery(out: Path, checked_at_utc: str) -> dict:
    config_file = out / "public-research-sources-config.json"
    if not config_file.exists():
        return {"status": "NOT_CONFIGURED"}
    try:
        data = discover_from_config(config_file)
        archive, _ = write_source_snapshot(out, data, checked_at_utc)
        return {
            "status": "DISCOVERED_NOT_LIVE_VERIFIED",
            "candidate_count": data["candidate_count"],
            "counts_by_kind": data["counts_by_kind"],
            "source_areas_scanned": data["source_areas_scanned"],
            "truncated": data["truncated"],
            "review_snapshot": archive.name,
            "review_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "source_config_sha256": data["source_config_sha256"],
        }
    except (OSError, ValueError, TypeError) as exc:
        return {"status": "UNVERIFIED", "error_type": type(exc).__name__}

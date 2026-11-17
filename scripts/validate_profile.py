"""Validate the public GitHub profile's local sources without network access."""

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


def validate_profile(root: Path) -> list[str]:
    root = root.resolve()
    readme = root / "README.md"
    if not readme.is_file():
        return ["missing README.md"]

    text = readme.read_text(encoding="utf-8-sig")
    errors: list[str] = []
    if "SIR DAVI" not in text.upper():
        errors.append("README missing profile identity")

    links = re.findall(r"(?<!\!)\[[^\]]+\]\(([^)]+)\)", text)
    images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    images += re.findall(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", text)
    if not images:
        errors.append("README must include at least one image")

    for raw in links + images:
        reference = raw.split("#", 1)[0].split("?", 1)[0]
        if not reference or reference.startswith(("https://", "http://", "mailto:")):
            continue
        if reference.startswith("//"):
            errors.append(f"unsafe protocol-relative link: {reference}")
            continue

        target = (root / reference).resolve()
        if not target.is_relative_to(root):
            errors.append(f"path escapes repository: {reference}")
            continue
        if not target.is_file():
            errors.append(f"missing local asset or link: {reference}")
            continue
        if target.suffix.lower() == ".svg":
            try:
                element = ET.parse(target).getroot()
                if not element.tag.endswith("svg"):
                    errors.append(f"not an SVG: {reference}")
            except ET.ParseError:
                errors.append(f"invalid SVG: {reference}")
    return errors


if __name__ == "__main__":
    failures = validate_profile(Path(__file__).resolve().parents[1])
    for error in failures:
        print("FAIL: " + error)
    if failures:
        sys.exit(1)
    print("Profile validation passed")

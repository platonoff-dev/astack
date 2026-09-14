#!/usr/bin/env python3
"""Check local inline Markdown links in maintained skills and their documentation."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def heading_ids(text: str) -> set[str]:
    ids, counts = set(), {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        slug = re.sub(r"[^\w\s-]", "", heading.lower())
        slug = re.sub(r"\s", "-", slug)
        count = counts.get(slug, 0)
        ids.add(f"{slug}-{count}" if count else slug)
        counts[slug] = count + 1
    return ids


def check_links(paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)", text):
            target = match[1].split(' "')[0].strip("<>")
            # These literal placeholders occur in the shipped report templates.
            if target in {"url", "browse_url"} or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            if any(c in target for c in "*{}"):
                continue
            file, _, fragment = unquote(target).partition("#")
            destination = path.parent / file if file else path
            line = text.count("\n", 0, match.start()) + 1
            if not destination.exists():
                errors.append(f"{path}:{line}: missing link target {target}")
            elif fragment and destination.suffix == ".md" and destination.is_file():
                if fragment not in heading_ids(destination.read_text(encoding="utf-8")):
                    errors.append(f"{path}:{line}: missing heading {target}")
    return errors


def main() -> int:
    paths = [ROOT / "README.md", ROOT / "AGENTS.md"]
    for directory in ("skills", ".claude/skills", "references", "docs"):
        paths.extend(sorted((ROOT / directory).rglob("*.md")))
    errors = check_links(paths)
    for error in errors:
        print(error)
    if not errors:
        print(f"Local Markdown links and headings resolve in {len(paths)} files")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())

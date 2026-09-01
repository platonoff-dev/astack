#!/usr/bin/env python3
"""Check the documented Markdown brief format, never its evidence or truth."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PLAYBOOKS = {
    "investigation",
    "bug-fix",
    "feature",
    "refactor",
    "performance",
    "migration",
    "decision",
    "split",
    "no-change",
}
REQUIRED_FIELDS = ("Source", "Checked", "Playbook")
FIELDS = REQUIRED_FIELDS + ("Modifiers",)
LEGACY_FIELDS = {"Work type", "Next action"}
LINK = re.compile(r"\[[^\]\n]+\]\((?:<[^>\n]+>|[^\s)]+)\)")
MODIFIER = re.compile(r"[a-z0-9][a-z0-9-]*")


def list_items(lines: list[str], pattern: str) -> list[str]:
    items: list[str] = []
    for line in lines:
        if not items or re.match(pattern, line):
            items.append(line)
        else:
            items[-1] += " " + line
    return items


def check(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    fields: dict[str, str] = {}
    sections: dict[str, list[str]] = {}
    section: str | None = None
    title = False
    fence = ""

    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if marker:
            run, suffix = marker.groups()
            if not fence:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not suffix.strip():
                fence = ""
            continue
        if fence:
            continue
        if line.startswith("# "):
            title = title or bool(line[2:].strip())
        elif line.startswith("## "):
            section = line[3:].strip()
            if section in sections:
                errors.append(f"duplicate section: {section}")
            sections.setdefault(section, [])
        elif section is not None:
            if line.strip():
                sections[section].append(line.strip())
        else:
            key, sep, value = line.partition(":")
            if sep and key in FIELDS:
                if key in fields:
                    errors.append(f"duplicate field: {key}")
                fields[key] = value.strip()
            elif sep and key in LEGACY_FIELDS:
                errors.append(f"legacy field is not supported: {key}; use Playbook and optional Modifiers")

    if fence:
        errors.append("unclosed code fence")
    if not title:
        errors.append("missing task title (# ...)")
    for field in REQUIRED_FIELDS:
        if not fields.get(field):
            errors.append(f"missing or empty field: {field}")
    for heading in ("Outcome", "Evidence", "Next step"):
        if not sections.get(heading):
            errors.append(f"missing or empty section: {heading}")

    playbook = fields.get("Playbook", "")
    if playbook not in PLAYBOOKS:
        errors.append("Playbook must be one of: " + ", ".join(sorted(PLAYBOOKS)))

    if "Modifiers" in fields:
        raw_modifiers = fields["Modifiers"]
        modifiers = [value.strip() for value in raw_modifiers.split(",")]
        if not raw_modifiers or any(not MODIFIER.fullmatch(value) for value in modifiers):
            errors.append("Modifiers must be a comma-separated list of lowercase names")
        elif len(modifiers) != len(set(modifiers)):
            errors.append("Modifiers must not repeat")
        elif playbook in modifiers:
            errors.append("Modifiers must not repeat the primary Playbook")

    for entry in list_items(sections.get("Evidence", []), r"- "):
        match = re.fullmatch(r"- (supported|contradicted|unresolved):\s*(.+)", entry)
        if not match:
            errors.append("each evidence entry must be a bullet: supported, contradicted, or unresolved")
            continue
        status, claim = match.groups()
        if status != "unresolved":
            if not LINK.search(claim):
                errors.append(f"{status} evidence needs an inline Markdown source link")

    words = len(text.split())
    if words > 600:
        warnings.append(f"{words} words exceeds the 600-word guideline; shorten or justify, never truncate requirements")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path, help="Markdown brief to check")
    args = parser.parse_args()
    try:
        text = args.brief.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        parser.exit(1, f"ERROR: cannot read brief: {exc}\n")
    errors, warnings = check(text)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"OK: brief structure ({len(text.split())} words); evidence and meaning not verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

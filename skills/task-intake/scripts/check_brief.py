#!/usr/bin/env python3
"""Check the documented Markdown brief format, never its evidence or truth."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


WORK_TYPES = {"bug", "feature", "refactor", "performance", "migration", "investigation"}
ACTIONS = {"implement", "investigate", "decide", "split", "no-change"}
FIELDS = ("Source", "Checked", "Work type", "Next action")
LINK = re.compile(r"\[[^\]\n]+\]\((?:<[^>\n]+>|[^\s)]+)\)")


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

    if fence:
        errors.append("unclosed code fence")
    if not title:
        errors.append("missing task title (# ...)")
    for field in FIELDS:
        if not fields.get(field):
            errors.append(f"missing or empty field: {field}")
    for heading in ("Outcome", "Evidence", "Next step"):
        if not sections.get(heading):
            errors.append(f"missing or empty section: {heading}")

    types = {value.strip() for value in fields.get("Work type", "").split(",")}
    if not types <= WORK_TYPES:
        errors.append("Work type must use: " + ", ".join(sorted(WORK_TYPES)))
    action = fields.get("Next action", "")
    if action not in ACTIONS:
        errors.append("Next action must be one of: " + ", ".join(sorted(ACTIONS)))

    evidenced = 0
    for entry in list_items(sections.get("Evidence", []), r"- "):
        match = re.fullmatch(r"- (supported|contradicted|unresolved):\s*(.+)", entry)
        if not match:
            errors.append("each evidence entry must be a bullet: supported, contradicted, or unresolved")
            continue
        status, claim = match.groups()
        if status != "unresolved":
            if not LINK.search(claim):
                errors.append(f"{status} evidence needs an inline Markdown source link")
            else:
                evidenced += 1
    if action in {"implement", "no-change"} and not evidenced:
        errors.append(f"{action} needs at least one supported or contradicted evidence entry")

    questions = sections.get("Questions", [])
    if action in {"implement", "no-change"} and questions:
        errors.append(f"{action} cannot carry Questions; resolve blockers or change Next action")
    if action == "decide" and not questions:
        errors.append("decide requires a nonempty Questions section")
    if action in {"implement", "investigate"}:
        checks = sections.get("Completion checks", [])
        if not any(re.fullmatch(r"- (?:\[[ xX]\] )?\S.*", line) for line in checks):
            errors.append(f"{action} requires at least one Completion checks bullet")
    if action == "split":
        items = list_items(sections.get("Breakdown", []), r"\d+\. ")
        children = [line for line in items if re.match(r"\d+\. \S", line)]
        if len(children) < 2:
            errors.append("split requires at least two numbered children in Breakdown")
        for child in children:
            if not re.search(r"Check:\s*\S", child) or not re.search(r"Depends on:\s*\S", child):
                errors.append("each child needs Check: and Depends on: in its numbered item")

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

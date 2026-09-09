#!/usr/bin/env python3
"""Pull one person's section out of a squad status report.

A full squad note is about 100 KB of markdown, so get-note spills it to a
file. Read the section you need from that file instead of the whole note.

Usage:
    slite_section.py FILE "Anatolii Platonov"          # markdown of that section
    slite_section.py FILE "Anatolii Platonov" --block "Next week"   # one block only
    slite_section.py FILE --list                        # names of all sections

FILE may be: the persisted tool output ([{"type":"text","text":"<json>"}]),
the get-note JSON object, or plain markdown / sliteml text.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

SLITE_ID = re.compile(r"\s*\{/\*\s*#[^}]*\*/\}")


def content_of(path: str) -> str:
    raw = open(path, encoding="utf-8").read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r'"content":"(.*)","isCollection"', raw, re.S)
        return json.loads('"' + m.group(1) + '"') if m else raw
    if isinstance(data, list) and data and isinstance(data[0], dict) and "text" in data[0]:
        data = json.loads(data[0]["text"])
    if isinstance(data, dict) and "content" in data:
        return data["content"]
    return raw


def sections(md: str) -> dict[str, str]:
    out: dict[str, str] = {}
    parts = re.split(r"(?m)^(?=### )", md)
    for part in parts:
        m = re.match(r"### (.+?)\s*(?:\{/\*.*?\*/\})?\s*$", part.split("\n", 1)[0])
        if not m:
            continue
        name = SLITE_ID.sub("", m.group(1)).strip()
        body = part
        # stop at the next H2 (Releases, General Metrics) if it is inside this chunk
        h2 = re.search(r"(?m)^## ", body[4:])
        if h2:
            body = body[: h2.start() + 4]
        out[name] = body.rstrip() + "\n"
    return out


def block_of(section: str, label: str) -> str:
    labels = ["Epics / Features in progress", "Other active issues",
              "Recently completed", "This week", "Next week", "Blockers"]
    pat = re.compile(r"(?im)^\*\*(" + "|".join(re.escape(l) for l in labels) + r")[^*]*\*\*")
    hits = list(pat.finditer(section))
    for i, h in enumerate(hits):
        if h.group(1).lower().startswith(label.lower()):
            end = hits[i + 1].start() if i + 1 < len(hits) else len(section)
            return section[h.start():end].rstrip() + "\n"
    return ""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file")
    p.add_argument("name", nargs="?")
    p.add_argument("--block", help="only this block, e.g. 'Next week'")
    p.add_argument("--list", action="store_true")
    a = p.parse_args()

    secs = sections(content_of(a.file))
    if a.list or not a.name:
        for n in secs:
            print(n)
        return
    key = next((n for n in secs if n.lower() == a.name.lower()), None) or \
          next((n for n in secs if a.name.lower() in n.lower()), None)
    if not key:
        print(f"no section for {a.name!r}; sections: {', '.join(secs)}", file=sys.stderr)
        sys.exit(1)
    text = secs[key]
    if a.block:
        text = block_of(text, a.block)
        if not text:
            print(f"no block {a.block!r} in section {key!r}", file=sys.stderr)
            sys.exit(1)
    sys.stdout.write(text)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Flatten a Jira search result into TSV and tally epic progress.

The Jira MCP tools spill large results to a file. Point this at the file
instead of re-reading it into the conversation.

Usage:
    jira_tally.py RESULT.json [MORE.json ...] [--since YYYY-MM-DD]
                  [--parent PROJ-N] [--tsv-only] [--tally-only]

Accepted shapes:
    claude.ai Atlassian connector   {"issues": {"nodes": [{"key", "fields": {...}}]}}
    persisted tool output           [{"type": "text", "text": "<json>"}]
    mcp-atlassian (workspace VM)    {"issues": [{"key", "summary", "status": {...}}]}

Output:
    one TSV line per issue:
        key  status  category  resolution  resolved  created  parent  type  fixVersions  summary
    then one progress line per parent epic:
        PROJ-400  86% (31/36)  done=31 resolved-Done=27 closed-no-resolution=4
                   in-progress=2 to-do=3  +1 created since 2026-08-27  3 resolved since 2026-08-27

Progress = children whose status category is Done, over all children.
That is the number for the "Progress" cell. Anything else in the cell needs
six words or fewer of explanation, and the tally lines tell you what to say.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict


def load_any(path: str):
    raw = open(path, encoding="utf-8").read()
    data = json.loads(raw)
    if isinstance(data, list) and data and isinstance(data[0], dict) and "text" in data[0]:
        data = json.loads(data[0]["text"])
    return data


def issues_of(data) -> list:
    if isinstance(data, dict):
        iss = data.get("issues", data)
        if isinstance(iss, dict) and "nodes" in iss:
            return iss["nodes"]
        if isinstance(iss, list):
            return iss
    if isinstance(data, list):
        return data
    return []


def pick(d: dict, *names, default=None):
    for n in names:
        if isinstance(d, dict) and d.get(n) not in (None, "", []):
            return d[n]
    return default


def name_of(x):
    if isinstance(x, dict):
        return pick(x, "name", "displayName", "key", default="")
    return x or ""


def category_of(status) -> str:
    if isinstance(status, dict):
        cat = status.get("statusCategory") or status.get("category")
        if isinstance(cat, dict):
            return (cat.get("key") or cat.get("name") or "").lower()
        if isinstance(cat, str):
            return cat.lower()
        name = (status.get("name") or "").lower()
    else:
        name = (status or "").lower()
    if name in {"done", "closed", "duplicate", "will not fix", "resolved", "wontfix"}:
        return "done"
    if name in {"backlog", "to do", "open", "selected for development", "triage"}:
        return "new"
    return "indeterminate"


def normalize(issue: dict) -> dict:
    f = issue.get("fields") if isinstance(issue.get("fields"), dict) else issue
    status = f.get("status")
    parent = f.get("parent")
    parent_key = parent.get("key") if isinstance(parent, dict) else (parent or "")
    parent_summary = ""
    if isinstance(parent, dict):
        parent_summary = pick(parent.get("fields", {}), "summary", default="") or parent.get("summary", "")
    cat = category_of(status)
    if cat == "done":
        cat = "done"
    elif cat in {"indeterminate", "in progress", "inprogress"}:
        cat = "in-progress"
    else:
        cat = "to-do"
    fixv = f.get("fixVersions") or f.get("fix_versions") or []
    return {
        "key": issue.get("key") or f.get("key", ""),
        "summary": (f.get("summary") or "").replace("\t", " ").strip(),
        "status": name_of(status),
        "category": cat,
        "resolution": name_of(f.get("resolution")) or "",
        "resolved": (pick(f, "resolutiondate", "resolution_date", "resolved", default="") or "")[:10],
        "created": (f.get("created") or "")[:10],
        "parent": parent_key or "",
        "parent_summary": parent_summary,
        "type": name_of(f.get("issuetype") or f.get("issue_type")),
        "fixVersions": ",".join(name_of(v) for v in fixv) if isinstance(fixv, list) else str(fixv),
        "duedate": f.get("duedate") or f.get("due_date") or "",
        "assignee": name_of(f.get("assignee")),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="+")
    p.add_argument("--since", help="YYYY-MM-DD, start of the report window")
    p.add_argument("--parent", help="treat every row as a child of this epic (for a 'parent = X' query)")
    p.add_argument("--tsv-only", action="store_true")
    p.add_argument("--tally-only", action="store_true")
    a = p.parse_args()

    rows = []
    seen = set()
    for path in a.files:
        for issue in issues_of(load_any(path)):
            n = normalize(issue)
            if not n["key"] or n["key"] in seen:
                continue
            seen.add(n["key"])
            if a.parent and not n["parent"]:
                n["parent"] = a.parent
            rows.append(n)

    rows.sort(key=lambda r: (r["parent"], r["resolved"] or "9999", r["key"]))

    if not a.tally_only:
        print("\t".join(["key", "status", "category", "resolution", "resolved", "created",
                         "parent", "type", "fixVersions", "summary"]))
        for r in rows:
            print("\t".join([r["key"], r["status"], r["category"], r["resolution"], r["resolved"],
                             r["created"], r["parent"], r["type"], r["fixVersions"], r["summary"]]))

    if a.tsv_only:
        return

    by_parent = defaultdict(list)
    for r in rows:
        if r["parent"]:
            by_parent[r["parent"]].append(r)

    if not by_parent:
        print("\n(no parent field in these rows; run the query with fields including 'parent', "
              "or pass --parent PROJ-N for a 'parent = PROJ-N' query)", file=sys.stderr)
        return

    print()
    for parent, kids in sorted(by_parent.items()):
        total = len(kids)
        done = sum(1 for k in kids if k["category"] == "done")
        resolved_done = sum(1 for k in kids if k["resolution"].lower() == "done")
        closed_no_res = sum(1 for k in kids if k["category"] == "done" and k["resolution"].lower() != "done")
        inprog = sum(1 for k in kids if k["category"] == "in-progress")
        todo = sum(1 for k in kids if k["category"] == "to-do")
        pct = round(100 * done / total) if total else 0
        line = (f"{parent}  {pct}% ({done}/{total})  done={done} resolved-Done={resolved_done} "
                f"closed-no-resolution={closed_no_res} in-progress={inprog} to-do={todo}")
        if a.since:
            created = [k["key"] for k in kids if k["created"] and k["created"] >= a.since]
            resolved = [k["key"] for k in kids if k["resolved"] and k["resolved"] >= a.since]
            line += f"  +{len(created)} created since {a.since}  {len(resolved)} resolved since {a.since}"
            if resolved:
                line += "  [" + ", ".join(resolved) + "]"
        title = next((k["parent_summary"] for k in kids if k["parent_summary"]), "")
        if title:
            line += f"  ({title})"
        print(line)
        if closed_no_res:
            names = ", ".join(k["key"] for k in kids
                              if k["category"] == "done" and k["resolution"].lower() != "done")
            print(f"    closed without a Done resolution (not achievements; do not list as completed): {names}")


if __name__ == "__main__":
    main()

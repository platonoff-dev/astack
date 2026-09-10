#!/usr/bin/env python3
"""Resolve, validate and print the tracker adapter.

The adapter is the one file that holds an organisation's issue-tracker facts:
hosts, project keys, custom-field ids, the status and label names that carry
meaning, the work-order ladder, the review forge, the report destination. It
lives outside this plugin on purpose. Skills ship the discipline; the adapter
supplies the values, so nothing organisation-specific is ever committed here.

    tracker_adapter.py path                  where the adapter is, and why
    tracker_adapter.py validate [FILE]       schema check; exit 1 on any error
    tracker_adapter.py show [FILE] [--json]  the resolved adapter
    tracker_adapter.py init [--out FILE]     write a commented template

Stdlib only. Needs Python 3.11 for tomllib.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - depends on the interpreter
    sys.exit("tracker_adapter.py needs Python 3.11 or newer (tomllib).")

ENV_VAR = "ASTACK_TRACKER_ADAPTER"
BASENAME = "tracker-adapter.toml"
PROJECT_DIRS = (".agents", ".claude")
USER_PATH = Path.home() / ".config" / "astack" / BASENAME

STATUS_ROLES = ("active", "parked", "blocked", "excluded", "shovel_ready")
LABEL_ROLES = (
    "needs_info",
    "needs_triage",
    "wontfix",
    "ready_for_agent",
    "ready_for_human",
    "test_suite",
    "ignore",
)
TYPE_ROLES = ("support", "release", "epic")
TRACKER_KINDS = ("jira", "linear", "github", "gitlab", "other")
FORGES = ("gitlab", "github", "none")
DESTINATIONS = ("slite", "confluence", "file", "none")

TEMPLATE = '''\
# Tracker adapter — organisation-specific values for the astack skills.
#
# Nothing in this file belongs in a public repository. Keep it in the private
# repository it describes (.agents/tracker-adapter.toml) or in your home
# (~/.config/astack/tracker-adapter.toml). Every value is a cache, not an
# authority: when one stops working, verify it against the tracker and correct
# it here in the same change.

[tracker]
kind = "jira"                 # jira | linear | github | gitlab | other
project = "PROJ"              # the project key work items carry
key_pattern = "PROJ-\\\\d+"     # how a key looks in a branch or a title
browse_url = "https://example.atlassian.net/browse/{key}"
# cloud_id = ""               # Jira Cloud id, when the connector needs one

[tracker.fields]              # role -> the tracker's own field id
# story_points = "customfield_NNNNN"
# team = "customfield_NNNNN"

[tracker.field_values]        # role -> the value to write on a new item
# team = ""

[me]
# account_id = ""             # your id in the tracker, when a query needs it

[statuses]                    # bucket role -> the statuses that mean it
active = ["In Progress"]
parked = ["In Review"]
blocked = ["Blocked"]
excluded = ["Done", "Closed"]
shovel_ready = ["Backlog"]

[labels]                      # role -> the labels that mean it
needs_info = ["needs-info"]
needs_triage = ["triage"]
wontfix = ["wontfix"]
ready_for_agent = []
ready_for_human = []
test_suite = []
ignore = []

[issue_types]                 # role -> the issue types that mean it
support = []
release = []
epic = ["Epic"]

[wip]
cap = 3                       # items allowed in `active` at once
stale_days = 5                # an active item untouched this long is rotting

[ladder]
# Work classes, most urgent first. `critical` and `other` are computed from
# priority; the rest are matched from issue_types and labels above.
classes = ["support", "critical", "test-suite", "other"]

[review]
forge = "none"                # gitlab | github | none
# project = "group/repo"
# request_url = "https://gitlab.example.com/group/repo/-/merge_requests/{id}"

[report]
destination = "none"          # slite | confluence | file | none
# readers = "the CEO, the product lead, marketing and your manager"
# section_heading = "Your Name"
# blocks = ["Epics / Features in progress", "Recently completed",
#           "This week", "Next week", "Blockers"]
'''


class AdapterError(Exception):
    pass


def candidates(cwd: Path) -> list[tuple[Path, str]]:
    """Every place an adapter may live, in precedence order, with the reason."""
    found: list[tuple[Path, str]] = []
    env = os.environ.get(ENV_VAR)
    if env:
        found.append((Path(env).expanduser(), f"${ENV_VAR}"))
    for parent in (cwd, *cwd.parents):
        for d in PROJECT_DIRS:
            found.append((parent / d / BASENAME, f"project {d}/"))
        if (parent / ".git").exists():
            break
    found.append((USER_PATH, "user default"))
    return found


def resolve(cwd: Path | None = None) -> tuple[Path, str]:
    cwd = (cwd or Path.cwd()).resolve()
    for path, why in candidates(cwd):
        if path.is_file():
            return path, why
    raise AdapterError(
        "no tracker adapter found. Looked for:\n  "
        + "\n  ".join(f"{p}  ({w})" for p, w in candidates(cwd))
        + "\nRun /setup-tracker, or tracker_adapter.py init, to write one."
    )


def load(path: Path) -> dict:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise AdapterError(f"{path}: not valid TOML — {exc}") from exc


def _str_list(value: object, where: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
        errors.append(f"{where}: must be a list of strings")
        return []
    return value


def check(data: dict) -> list[str]:
    """Every reason this adapter cannot be used, in one pass."""
    errors: list[str] = []

    tracker = data.get("tracker")
    if not isinstance(tracker, dict):
        errors.append("[tracker]: missing")
        tracker = {}
    kind = tracker.get("kind")
    if kind not in TRACKER_KINDS:
        errors.append(f"tracker.kind: must be one of {', '.join(TRACKER_KINDS)}")
    for key in ("project", "key_pattern", "browse_url"):
        if not isinstance(tracker.get(key), str) or not tracker.get(key):
            errors.append(f"tracker.{key}: missing")
    pattern = tracker.get("key_pattern")
    if isinstance(pattern, str) and pattern:
        try:
            re.compile(pattern)
        except re.error as exc:
            errors.append(f"tracker.key_pattern: not a valid regex — {exc}")
    browse = tracker.get("browse_url")
    if isinstance(browse, str) and browse and "{key}" not in browse:
        errors.append("tracker.browse_url: must contain {key}")

    statuses = data.get("statuses")
    if not isinstance(statuses, dict):
        errors.append("[statuses]: missing")
    else:
        seen: dict[str, str] = {}
        for role in STATUS_ROLES:
            if role not in statuses:
                errors.append(f"statuses.{role}: missing — every bucket needs a mapping")
                continue
            for name in _str_list(statuses[role], f"statuses.{role}", errors):
                if name in seen:
                    errors.append(
                        f"statuses: {name!r} is in both {seen[name]} and {role}; "
                        "a status maps to exactly one bucket"
                    )
                seen[name] = role
        for role in set(statuses) - set(STATUS_ROLES):
            errors.append(f"statuses.{role}: not a bucket role")

    labels = data.get("labels", {})
    if not isinstance(labels, dict):
        errors.append("[labels]: must be a table")
    else:
        for role in LABEL_ROLES:
            _str_list(labels.get(role, []), f"labels.{role}", errors)
        for role in set(labels) - set(LABEL_ROLES):
            errors.append(f"labels.{role}: not a label role")

    types = data.get("issue_types", {})
    if not isinstance(types, dict):
        errors.append("[issue_types]: must be a table")
    else:
        for role in TYPE_ROLES:
            _str_list(types.get(role, []), f"issue_types.{role}", errors)
        for role in set(types) - set(TYPE_ROLES):
            errors.append(f"issue_types.{role}: not an issue-type role")

    wip = data.get("wip", {})
    if not isinstance(wip, dict):
        errors.append("[wip]: must be a table")
    else:
        for key in ("cap", "stale_days"):
            value = wip.get(key, 1)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                errors.append(f"wip.{key}: must be a positive integer")

    ladder = data.get("ladder", {})
    if not isinstance(ladder, dict):
        errors.append("[ladder]: must be a table")
    else:
        classes = _str_list(ladder.get("classes", ["other"]), "ladder.classes", errors)
        if classes and classes[-1] != "other":
            errors.append("ladder.classes: the last class must be 'other'")
        if len(set(classes)) != len(classes):
            errors.append("ladder.classes: duplicate class")

    review = data.get("review", {})
    if not isinstance(review, dict):
        errors.append("[review]: must be a table")
    else:
        forge = review.get("forge", "none")
        if forge not in FORGES:
            errors.append(f"review.forge: must be one of {', '.join(FORGES)}")
        elif forge != "none" and not review.get("project"):
            errors.append(f"review.project: required when forge is {forge!r}")

    report = data.get("report", {})
    if not isinstance(report, dict):
        errors.append("[report]: must be a table")
    else:
        dest = report.get("destination", "none")
        if dest not in DESTINATIONS:
            errors.append(f"report.destination: must be one of {', '.join(DESTINATIONS)}")
        _str_list(report.get("blocks", []), "report.blocks", errors)

    return errors


def resolved(data: dict) -> dict:
    """The adapter with every role present, so a skill can read it blindly."""
    tracker = data.get("tracker", {})
    return {
        "tracker": {
            "kind": tracker.get("kind", "other"),
            "project": tracker.get("project", ""),
            "key_pattern": tracker.get("key_pattern", ""),
            "browse_url": tracker.get("browse_url", ""),
            "cloud_id": tracker.get("cloud_id", ""),
            "fields": tracker.get("fields", {}),
            "field_values": tracker.get("field_values", {}),
        },
        "me": data.get("me", {}),
        "statuses": {r: list(data.get("statuses", {}).get(r, [])) for r in STATUS_ROLES},
        "labels": {r: list(data.get("labels", {}).get(r, [])) for r in LABEL_ROLES},
        "issue_types": {r: list(data.get("issue_types", {}).get(r, [])) for r in TYPE_ROLES},
        "wip": {
            "cap": data.get("wip", {}).get("cap", 3),
            "stale_days": data.get("wip", {}).get("stale_days", 5),
        },
        "ladder": {"classes": list(data.get("ladder", {}).get("classes", ["other"]))},
        "review": data.get("review", {"forge": "none"}),
        "report": data.get("report", {"destination": "none"}),
    }


def render(adapter: dict, path: Path, why: str) -> str:
    t = adapter["tracker"]
    lines = [
        f"adapter    {path}  ({why})",
        f"tracker    {t['kind']}  project {t['project']}  keys {t['key_pattern']}",
        f"wip        cap {adapter['wip']['cap']}  stale after {adapter['wip']['stale_days']}d",
        f"ladder     {' > '.join(adapter['ladder']['classes'])}",
        f"review     {adapter['review'].get('forge', 'none')}"
        + (f"  {adapter['review']['project']}" if adapter["review"].get("project") else ""),
        f"report     {adapter['report'].get('destination', 'none')}",
    ]
    for role, names in adapter["statuses"].items():
        lines.append(f"status     {role:<13}{', '.join(names) or '—'}")
    for role, names in adapter["labels"].items():
        if names:
            lines.append(f"label      {role:<13}{', '.join(names)}")
    for role, names in adapter["issue_types"].items():
        if names:
            lines.append(f"type       {role:<13}{', '.join(names)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("path", help="print where the adapter is and why")
    for name in ("validate", "show"):
        p = sub.add_parser(name)
        p.add_argument("file", nargs="?")
    sub.choices["show"].add_argument("--json", action="store_true")
    init = sub.add_parser("init")
    init.add_argument("--out")
    args = parser.parse_args(argv)

    try:
        if args.cmd == "init":
            out = Path(args.out).expanduser() if args.out else USER_PATH
            if out.exists():
                print(f"{out} already exists — edit it, or pass --out elsewhere.")
                return 1
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(TEMPLATE, encoding="utf-8")
            print(f"wrote {out}\nFill it in, then run: tracker_adapter.py validate")
            return 0

        if args.cmd == "path":
            path, why = resolve()
            print(f"{path}  ({why})")
            return 0

        if getattr(args, "file", None):
            path, why = Path(args.file).expanduser(), "given on the command line"
            if not path.is_file():
                raise AdapterError(f"{path}: no such file")
        else:
            path, why = resolve()

        data = load(path)
        errors = check(data)
        if errors:
            print(f"{path}: {len(errors)} problem(s)", file=sys.stderr)
            for e in errors:
                print(f"  {e}", file=sys.stderr)
            return 1

        if args.cmd == "validate":
            print(f"{path}  ({why})\nok — every role is mapped.")
            return 0

        adapter = resolved(data)
        if args.json:
            print(json.dumps(adapter, indent=2, sort_keys=True))
        else:
            print(render(adapter, path, why))
        return 0
    except AdapterError as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

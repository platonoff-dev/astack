#!/usr/bin/env python3
"""Check that intake routes, router links, and playbook files match."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
INTAKE_CHECKER = REPO_ROOT / "skills" / "task-intake" / "scripts" / "check_brief.py"
ROUTE_ROW = re.compile(r"^\| `([a-z0-9-]+)` \| \[[^]]+\]\((references/playbooks/([a-z0-9-]+)\.md)\) \|$")


def intake_playbooks() -> set[str]:
    spec = importlib.util.spec_from_file_location("task_intake_check_brief", INTAKE_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {INTAKE_CHECKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return set(module.PLAYBOOKS)


def main() -> int:
    errors: list[str] = []
    declared = intake_playbooks()
    files = {path.stem for path in (SKILL_DIR / "references" / "playbooks").glob("*.md")}

    routes: set[str] = set()
    for line in (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").splitlines():
        match = ROUTE_ROW.fullmatch(line)
        if not match:
            continue
        route, _, target = match.groups()
        if route in routes:
            errors.append(f"duplicate router row: {route}")
        routes.add(route)
        if route != target:
            errors.append(f"router row {route} points to {target}.md")

    for label, actual in (("playbook files", files), ("router rows", routes)):
        missing = sorted(declared - actual)
        extra = sorted(actual - declared)
        if missing:
            errors.append(f"{label} missing: {', '.join(missing)}")
        if extra:
            errors.append(f"{label} not accepted by intake: {', '.join(extra)}")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"OK: {len(declared)} intake routes have one router row and playbook file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

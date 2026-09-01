#!/usr/bin/env python3
"""Check intake routes, router links, files, and adopted playbook status."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
INTAKE_CHECKER = REPO_ROOT / "skills" / "task-intake" / "scripts" / "check_brief.py"
ROUTE_ROW = re.compile(r"^\| `([a-z0-9-]+)` \| \[[^]]+\]\((references/playbooks/([a-z0-9-]+)\.md)\) \|$")
ADOPTED_PLAYBOOKS: set[str] = set()


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
    playbook_paths = list((SKILL_DIR / "references" / "playbooks").glob("*.md"))
    files = {path.stem for path in playbook_paths}
    content = {path.stem: path.read_text(encoding="utf-8").strip() for path in playbook_paths}

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

    unknown_adopted = sorted(ADOPTED_PLAYBOOKS - declared)
    if unknown_adopted:
        errors.append(f"adopted playbooks not accepted by intake: {', '.join(unknown_adopted)}")
    for route in sorted(declared & files):
        if route in ADOPTED_PLAYBOOKS and not content[route]:
            errors.append(f"adopted playbook is empty: {route}")
        if route not in ADOPTED_PLAYBOOKS and content[route]:
            errors.append(f"placeholder playbook has content but no adoption decision: {route}")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    placeholders = len(declared - ADOPTED_PLAYBOOKS)
    print(
        f"OK: {len(declared)} routes mapped; "
        f"{len(ADOPTED_PLAYBOOKS)} adopted; {placeholders} empty placeholders"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

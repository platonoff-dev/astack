#!/usr/bin/env python3
"""Resolve and validate astack's private system index; never execute its guides.

    astack_adapter.py path
    astack_adapter.py validate [FILE]
    astack_adapter.py show [FILE] [--json] [--role ROLE ...]

Stdlib only, Python 3.11+. Exit 2 means no index; exit 1 means a selected index
cannot be used. Relative references belong to the index's directory.
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
except ModuleNotFoundError:
    sys.exit("astack_adapter.py needs Python 3.11 or newer (tomllib).")

ENV_VAR = "ASTACK_ADAPTER"
USER_PATH = Path.home() / ".config" / "astack" / "adapter.toml"
PROJECT_DIRS = (".agents", ".claude")


class AdapterError(Exception):
    """A selected configuration is unusable; do not silently fall back."""


def candidates(cwd: Path) -> list[tuple[Path, str]]:
    """Project locations within this checkout, then the user default."""
    parents = (cwd, *cwd.parents)
    root = next((p for p in parents if (p / ".git").exists()), cwd)
    found = []
    for parent in parents:
        for directory in PROJECT_DIRS:
            found.append((parent / directory / "astack" / "adapter.toml",
                          f"project {directory}/astack/"))
        if parent == root:
            break
    found.append((USER_PATH, "user default"))
    return found


def resolve(cwd: Path | None = None) -> tuple[Path, str] | None:
    cwd = (cwd or Path.cwd()).resolve()
    explicit = os.environ.get(ENV_VAR)
    if explicit is not None:
        if not explicit.strip():
            raise AdapterError(f"${ENV_VAR}: empty path")
        path = Path(explicit).expanduser()
        if not path.is_absolute():
            path = cwd / path
        if not path.is_file():
            raise AdapterError(f"${ENV_VAR}: {path}: no such file")
        return path.absolute(), f"${ENV_VAR}"
    for path, why in candidates(cwd):
        if path.exists() or path.is_symlink():
            if not path.is_file():
                raise AdapterError(f"{path}: not a readable index file")
            return path.absolute(), why
    return None


def reference(index: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = index.parent / path
    return path.resolve()


def check(data: dict, path: Path) -> list[str]:
    errors = []
    for key in data.keys() - {"version", "tracker_adapter", "systems"}:
        errors.append(f"{key}: unknown index field")
    if type(data.get("version")) is not int or data["version"] != 1:
        errors.append("version: must be the integer 1")
    tracker = data.get("tracker_adapter")
    if "tracker_adapter" in data:
        if not isinstance(tracker, str) or not tracker.strip():
            errors.append("tracker_adapter: must be a nonempty path")
        elif not reference(path, tracker).is_file():
            errors.append("tracker_adapter: referenced file does not exist")

    systems = data.get("systems")
    if not isinstance(systems, dict):
        return errors + ["systems: must be a table (may be empty)"]
    for name, system in systems.items():
        where = f"systems.{name}"
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", name):
            errors.append(f"{where}: invalid system identifier")
        if not isinstance(system, dict):
            errors.append(f"{where}: must be a table")
            continue
        for key in system.keys() - {"kind", "roles", "instructions", "facts"}:
            errors.append(f"{where}.{key}: unknown system field")
        if not isinstance(system.get("kind"), str) or not system["kind"].strip():
            errors.append(f"{where}.kind: must be a nonempty string")
        roles = system.get("roles")
        if (not isinstance(roles, list) or not roles
                or any(not isinstance(r, str) or not r.strip() for r in roles)):
            errors.append(f"{where}.roles: must be a nonempty list of role names")
        elif len(set(roles)) != len(roles):
            errors.append(f"{where}.roles: duplicate role")
        if not isinstance(system.get("facts", {}), dict):
            errors.append(f"{where}.facts: must be a table")
        guide = system.get("instructions")
        if not isinstance(guide, str) or not guide.strip():
            errors.append(f"{where}.instructions: must be a nonempty path")
            continue
        guide_path = reference(path, guide)
        if guide_path.suffix.lower() != ".md":
            errors.append(f"{where}.instructions: must reference a Markdown (.md) file")
        try:
            if not guide_path.read_text(encoding="utf-8").strip():
                errors.append(f"{where}.instructions: guide is empty")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{where}.instructions: cannot read {guide_path}: {exc}")
    return errors


def load(path: Path) -> dict:
    try:
        with path.open("rb") as stream:
            data = tomllib.load(stream)
    except (OSError, ValueError) as exc:
        raise AdapterError(f"{path}: cannot read TOML: {exc}") from exc
    errors = check(data, path)
    if errors:
        raise AdapterError(f"{path}: invalid adapter\n  " + "\n  ".join(errors))
    return data


def view(data: dict, path: Path, why: str, roles: list[str]) -> dict:
    systems = {}
    for name, system in data["systems"].items():
        if roles and not set(roles).intersection(system["roles"]):
            continue
        systems[name] = {**system, "instructions": str(reference(path, system["instructions"]))}
    return {
        "path": str(path.absolute()),
        "source": why,
        "version": data["version"],
        "tracker_adapter": (str(reference(path, data["tracker_adapter"]))
                            if "tracker_adapter" in data else None),
        "systems": systems,
        "unconfigured_roles": sorted(set(roles) - {
            role for system in systems.values() for role in system["roles"]
        }),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("path")
    for command in ("validate", "show"):
        sub.add_parser(command).add_argument("file", nargs="?")
    sub.choices["show"].add_argument("--json", action="store_true")
    sub.choices["show"].add_argument("--role", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        if getattr(args, "file", None):
            selected = (Path(args.file).expanduser().absolute(), "command line")
        else:
            selected = resolve()
        if selected is None:
            print("No astack adapter found. Run setup-astack to configure one.", file=sys.stderr)
            return 2
        path, why = selected
        if args.cmd == "path":
            print(f"{path}  ({why})")
            return 0
        data = load(path)
        if args.cmd == "validate":
            print(f"{path}  ({why})\nok — index and referenced files; access is not checked.")
        elif args.json:
            print(json.dumps(view(data, path, why, args.role), indent=2, default=str))
        else:
            result = view(data, path, why, args.role)
            print(f"adapter  {path}  ({why})")
            print(f"tracker  {result['tracker_adapter'] or 'not configured'}")
            for name, system in result["systems"].items():
                print(f"system   {name} ({system['kind']}; {', '.join(system['roles'])})")
                print(f"guide    {system['instructions']}")
            if result["unconfigured_roles"]:
                print("unconfigured roles  " + ", ".join(result["unconfigured_roles"]))
        return 0
    except (AdapterError, OSError, ValueError, RuntimeError) as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

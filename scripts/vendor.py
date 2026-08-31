#!/usr/bin/env python3
"""Vendor third-party skills into this plugin.

Vendored files are committed to this repo on purpose. Both harnesses install a
plugin by copying the repo tree and neither initialises git submodules, so a
submodule or subtree would arrive empty on someone else's `plugin install`.
Reproducibility comes from the pin in `vendor.json` instead: repo, subdirectory,
branch and the exact commit the working copy was taken from.

    vendor.py sync            re-materialise every skill from its pinned commit
    vendor.py check           local edits? upstream moved? (exit 1 if either)
    vendor.py update [name]   move the pin to the branch head and rewrite
    vendor.py add ...         register a new upstream skill and fetch it

Vendored directories are replaced wholesale by `sync` and `update`. Never edit
one by hand — `check` exists to catch exactly that, and an edit would be lost.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "vendor.json"
SKILLS = ROOT / "skills"


def run(cmd: list[str], capture: bool = False) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode:
        sys.exit(f"command failed: {' '.join(cmd)}\n{proc.stderr.strip()}")
    return proc.stdout if capture else ""


def load() -> dict:
    if not MANIFEST.is_file():
        sys.exit(f"missing {MANIFEST}")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def select(data: dict, names: list[str]) -> list[dict]:
    entries = data.get("skills", [])
    if not names:
        return entries
    by_name = {e["name"]: e for e in entries}
    unknown = [n for n in names if n not in by_name]
    if unknown:
        sys.exit(f"not in vendor.json: {', '.join(unknown)}")
    return [by_name[n] for n in names]


def head_of(repo: str, ref: str) -> str:
    out = run(["git", "ls-remote", repo, ref], capture=True).strip()
    if not out:
        sys.exit(f"ref `{ref}` not found in {repo}")
    return out.split()[0]


def fetch(entry: dict, commit: str, dest: Path) -> Path:
    """Sparse-fetch the entry's paths at `commit`. Returns the checkout root."""
    paths = [entry["path"]]
    if entry.get("license_path"):
        paths.append(entry["license_path"])
    run(["git", "init", "-q", str(dest)])
    run(["git", "-C", str(dest), "remote", "add", "origin", entry["repo"]])
    run(["git", "-C", str(dest), "sparse-checkout", "init", "--no-cone"])
    sparse = dest / ".git" / "info" / "sparse-checkout"
    sparse.write_text("".join(f"/{p}\n" for p in paths), encoding="utf-8")
    # Fetching a bare sha works on GitHub and GitLab; blobs outside the sparse
    # paths are never downloaded.
    run(["git", "-C", str(dest), "fetch", "-q", "--depth", "1",
         "--filter=blob:none", "origin", commit])
    run(["git", "-C", str(dest), "checkout", "-q", "FETCH_HEAD"])
    src = dest / entry["path"]
    if not src.is_dir():
        sys.exit(f"{entry['name']}: `{entry['path']}` is not a directory at {commit[:12]}")
    return dest


def materialise(entry: dict, commit: str, target: Path, checkout: Path) -> None:
    """Replace `target` with the upstream directory, plus the upstream licence."""
    src = checkout / entry["path"]
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(src, target)
    lic = entry.get("license_path")
    if lic:
        dst = target / "LICENSE"
        if dst.exists():
            sys.exit(
                f"{entry['name']}: upstream already ships a LICENSE in {entry['path']}; "
                "drop `license_path` from vendor.json"
            )
        shutil.copy2(checkout / lic, dst)


def snapshot(root: Path) -> dict[str, str]:
    if not root.is_dir():
        return {}
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def compare(label_a: str, a: dict[str, str], label_b: str, b: dict[str, str]) -> list[str]:
    lines = []
    for name in sorted(set(a) | set(b)):
        if name not in b:
            lines.append(f"    only in {label_a}: {name}")
        elif name not in a:
            lines.append(f"    only in {label_b}: {name}")
        elif a[name] != b[name]:
            lines.append(f"    differs: {name}")
    return lines


def cmd_sync(args: argparse.Namespace) -> int:
    data = load()
    SKILLS.mkdir(exist_ok=True)
    for entry in select(data, args.name):
        target = SKILLS / entry["name"]
        before = snapshot(target)
        with tempfile.TemporaryDirectory() as tmp:
            checkout = fetch(entry, entry["commit"], Path(tmp) / "src")
            materialise(entry, entry["commit"], target, checkout)
        after = snapshot(target)
        state = "unchanged" if before == after else ("restored" if before else "created")
        print(f"{state} skills/{entry['name']}  @ {entry['commit'][:12]}  "
              f"({len(after)} file{'s' if len(after) != 1 else ''})")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    data = load()
    problems = 0
    for entry in select(data, args.name):
        name, pinned = entry["name"], entry["commit"]
        target = SKILLS / entry["name"]
        vendored = snapshot(target)
        if not vendored:
            print(f"MISSING  {name}: skills/{name} does not exist — run `vendor.py sync`")
            problems += 1
            continue

        with tempfile.TemporaryDirectory() as tmp:
            checkout = fetch(entry, pinned, Path(tmp) / "pin")
            staged = Path(tmp) / "staged"
            materialise(entry, pinned, staged, checkout)
            at_pin = snapshot(staged)
        drift = compare("vendored", vendored, "pin", at_pin)
        if drift:
            print(f"EDITED   {name}: differs from its pinned commit {pinned[:12]}")
            print("\n".join(drift))
            problems += 1

        head = head_of(entry["repo"], entry["ref"])
        if head == pinned:
            if not drift:
                print(f"ok       {name}: matches pin, and pin is {entry['ref']} head")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            checkout = fetch(entry, head, Path(tmp) / "head")
            staged = Path(tmp) / "staged"
            materialise(entry, head, staged, checkout)
            at_head = snapshot(staged)
        moved = compare("pin", at_pin, entry["ref"], at_head)
        if moved:
            print(f"STALE    {name}: {entry['ref']} moved to {head[:12]} and the content changed")
            print("\n".join(moved))
            print(f"    update with: scripts/vendor.py update {name}")
            problems += 1
        elif not drift:
            print(f"ok       {name}: matches pin; {entry['ref']} moved to {head[:12]} "
                  "but this path is unchanged")
    return 1 if problems else 0


def cmd_update(args: argparse.Namespace) -> int:
    data = load()
    changed = False
    for entry in select(data, args.name):
        name, pinned = entry["name"], entry["commit"]
        head = head_of(entry["repo"], entry["ref"])
        target = SKILLS / name
        before = snapshot(target)
        with tempfile.TemporaryDirectory() as tmp:
            checkout = fetch(entry, head, Path(tmp) / "src")
            materialise(entry, head, target, checkout)
        after = snapshot(target)
        if head == pinned and before == after:
            print(f"unchanged {name}: already at {entry['ref']} head {head[:12]}")
            continue
        entry["commit"] = head
        changed = True
        print(f"updated  {name}: {pinned[:12]} -> {head[:12]}")
        for line in compare("old", before, "new", after) or ["    (no file changes)"]:
            print(line)
    if changed:
        save(data)
        print("\nvendor.json repinned. Bump the plugin version in both manifests "
              "and reinstall for the harnesses to see it.")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    data = load()
    entries = data.setdefault("skills", [])
    if any(e["name"] == args.name for e in entries):
        sys.exit(f"`{args.name}` is already in vendor.json — use `update` instead")
    entry = {
        "name": args.name,
        "repo": args.repo,
        "path": args.path.strip("/"),
        "ref": args.ref,
        "commit": head_of(args.repo, args.ref),
        "license": args.license,
        "license_path": args.license_path,
        "upstream": args.upstream,
    }
    entry = {k: v for k, v in entry.items() if v is not None}
    entries.append(entry)
    save(data)
    print(f"added {args.name} @ {entry['commit'][:12]}")
    args.name = [args.name]
    return cmd_sync(args)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("sync", help="re-materialise from the pinned commits")
    p.add_argument("name", nargs="*")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("check", help="report local edits and upstream drift")
    p.add_argument("name", nargs="*")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("update", help="repin to the branch head and rewrite")
    p.add_argument("name", nargs="*")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("add", help="register and fetch a new upstream skill")
    p.add_argument("--name", required=True)
    p.add_argument("--repo", required=True, help="clone URL")
    p.add_argument("--path", required=True, help="skill directory inside the repo")
    p.add_argument("--ref", default="main")
    p.add_argument("--license", help="SPDX id, e.g. MIT")
    p.add_argument("--license-path", help="path to the upstream LICENSE to copy in")
    p.add_argument("--upstream", help="human-facing URL for the docs")
    p.set_defaults(func=cmd_add)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

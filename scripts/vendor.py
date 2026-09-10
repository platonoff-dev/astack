#!/usr/bin/env python3
"""Import, audit, update and reproduce skills from Git repositories.

Requires Python 3.10+ and Git; no third-party Python dependencies. All staging
is under .local/tmp. Upstream code is copied, never executed by this tool.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

from sync_codex_policy import frontmatter, render, unquote, vendored_policy_error

ROOT = Path(__file__).resolve().parent.parent


class VendorError(Exception):
    """An actionable failure that must not replace the installed copy."""


def git(*args: str, cwd: Path | None = None) -> bytes:
    env = os.environ.copy()
    # Git must not discover the parent worktree when applying a patch in staging.
    for key in list(env):
        if key.startswith(("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")):
            del env[key]
    env["GIT_TERMINAL_PROMPT"] = "0"
    if cwd:
        env["GIT_CEILING_DIRECTORIES"] = str(cwd.parent.resolve())
    proc = subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", *args],
        cwd=cwd, env=env, capture_output=True, check=False,
    )
    if proc.returncode:
        raise VendorError(proc.stderr.decode(errors="replace").strip())
    return proc.stdout


def relative(value: str, *, allow_root: bool = False) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or (not allow_root and path == PurePosixPath(".")):
        raise VendorError(f"expected a relative path without '..': {value!r}")
    if any(part in {".git", ".local"} for part in path.parts):
        raise VendorError(f"reserved path: {value!r}")
    return path


def local_path(root: Path, value: str) -> Path:
    path = root / relative(value)
    if not path.resolve().is_relative_to(root.resolve()):
        raise VendorError(f"path escapes the repository: {value}")
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise VendorError(f"symlink is not supported: {part}")
    return path


def validate_entry(root: Path, entry: dict) -> None:
    for key in ("name", "repo", "path", "ref", "commit", "license", "license_path"):
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            raise VendorError(f"entry requires a nonempty {key}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["name"]):
        raise VendorError(f"invalid skill name: {entry['name']}")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", entry["commit"]):
        raise VendorError(f"{entry['name']}: commit must be a full Git object id")
    if entry["repo"].startswith("-") or entry["ref"].startswith("-"):
        raise VendorError("repository and ref cannot start with '-'")
    relative(entry["path"], allow_root=True)
    relative(entry["license_path"])
    local_path(root, f"skills/{entry['name']}")
    patches = entry.get("patches", [])
    if not isinstance(patches, list) or not all(isinstance(p, str) for p in patches):
        raise VendorError("patches must be a list of repository-relative paths")
    for patch in patches:
        if not patch.startswith("vendor/patches/"):
            raise VendorError("compatibility patches belong under vendor/patches/")
        if not local_path(root, patch).is_file():
            raise VendorError(f"missing patch: {patch}")


def load(root: Path) -> dict:
    path = local_path(root, "vendor.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("skills"), list):
        raise VendorError("vendor.json requires version 1 and a skills list")
    names = set()
    for entry in data["skills"]:
        if not isinstance(entry, dict):
            raise VendorError("each skills entry must be an object")
        validate_entry(root, entry)
        if entry["name"] in names:
            raise VendorError(f"duplicate skill: {entry['name']}")
        names.add(entry["name"])
    return data


def select(data: dict, names: list[str]) -> list[dict]:
    entries = {entry["name"]: entry for entry in data["skills"]}
    unknown = set(names) - entries.keys()
    if unknown:
        raise VendorError(f"not in vendor.json: {', '.join(sorted(unknown))}")
    return [entries[name] for name in dict.fromkeys(names)] if names else list(entries.values())


def fetch(entry: dict, revision: str, dest: Path) -> str:
    git("init", "-q", str(dest))
    git("fetch", "-q", "--depth=1", "--", entry["repo"], revision, cwd=dest)
    return git("rev-parse", "FETCH_HEAD^{commit}", cwd=dest).decode().strip()


def export(entry: dict, checkout: Path, commit: str, dest: Path) -> Path:
    paths = [entry["path"], entry["license_path"]]
    tree = git("ls-tree", "-r", commit, "--", *paths, cwd=checkout)
    if any(line.startswith(b"160000 ") for line in tree.splitlines()):
        raise VendorError("skill contains a submodule; import its contents explicitly")
    archive = git("archive", "--format=tar", commit, "--", *paths, cwd=checkout)
    dest.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar:
            path = dest / relative(member.name)
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                path.parent.mkdir(parents=True, exist_ok=True)
                source = tar.extractfile(member)
                if source is None:
                    raise VendorError(f"cannot read archive member: {member.name}")
                with source, path.open("wb") as output:
                    shutil.copyfileobj(source, output)
                path.chmod(0o755 if member.mode & 0o111 else 0o644)
            else:
                raise VendorError(f"unsupported link or special file: {member.name}")
    source = dest / entry["path"]
    if not (source / "SKILL.md").is_file():
        raise VendorError(f"{entry['path']}: no SKILL.md at {commit[:12]}")
    license_file = dest / entry["license_path"]
    if not license_file.is_file():
        raise VendorError(f"missing upstream license: {entry['license_path']}")
    target_license = source / "LICENSE"
    if license_file != target_license:
        if target_license.exists() and target_license.read_bytes() != license_file.read_bytes():
            target_license = source / "LICENSE.upstream"
        if target_license.exists() and target_license.read_bytes() != license_file.read_bytes():
            raise VendorError("LICENSE.upstream already exists with different contents")
        shutil.copy2(license_file, target_license)
    return source


def snapshot(root: Path) -> dict[str, str]:
    if root.is_symlink() or (root.exists() and not root.is_dir()):
        raise VendorError(f"expected a directory, not a file or symlink: {root}")
    files = {}
    for path in sorted(root.rglob("*")) if root.exists() else []:
        if path.is_symlink():
            raise VendorError(f"symlink is not supported: {path}")
        if path.is_file():
            mode = "x" if path.stat().st_mode & 0o111 else "-"
            files[path.relative_to(root).as_posix()] = mode + hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise VendorError(f"special file is not supported: {path}")
    return files


def materialise(root: Path, entry: dict, revision: str, work: Path) -> tuple[str, Path, dict]:
    work.mkdir()
    checkout = work / "git"
    commit = fetch(entry, revision, checkout)
    raw = export(entry, checkout, commit, work / "export")
    upstream = snapshot(raw)
    staged = work / "staged"
    shutil.copytree(raw, staged)
    for patch in entry.get("patches", []):
        patch_path = str(local_path(root, patch))
        git("apply", "--check", patch_path, cwd=staged)
        git("apply", patch_path, cwd=staged)
    snapshot(staged)  # Reject links introduced by patches before reading files.
    fm = frontmatter((staged / "SKILL.md").read_text(encoding="utf-8"))
    if unquote(fm.get("name", "")) != entry["name"] or not fm.get("description"):
        raise VendorError("SKILL.md needs a matching name and description; use a compatibility patch")
    policy = staged / "agents" / "openai.yaml"
    if fm.get("disable-model-invocation", "").lower() == "true" and not policy.exists():
        policy.parent.mkdir(exist_ok=True)
        policy.write_text(render(entry["name"], fm["description"]), encoding="utf-8")
    error = vendored_policy_error(fm, policy)
    if error:
        raise VendorError(f"{entry['name']}: {error}; use a compatibility patch")
    return commit, staged, upstream


def differences(before: dict, after: dict) -> list[str]:
    return [f"{'added' if p not in before else 'removed' if p not in after else 'changed'} {p}"
            for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)]


def publish(root: Path, data: dict, prepared: list[tuple[dict, Path, dict]], work: Path,
            original_manifest: bytes) -> None:
    """Stage all skills first; roll back the entire batch on ordinary write errors."""
    manifest = local_path(root, "vendor.json")
    pending = work / "vendor.json"
    pending.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if manifest.read_bytes() != original_manifest:
        raise VendorError("vendor.json changed during preparation; retry after reviewing that change")
    for entry, _, before in prepared:
        target = local_path(root, f"skills/{entry['name']}")
        if snapshot(target) != before:
            raise VendorError(f"{entry['name']}: local files changed during preparation; nothing replaced")
    replaced = []
    try:
        for entry, staged, _ in prepared:
            target = local_path(root, f"skills/{entry['name']}")
            target.parent.mkdir(exist_ok=True)
            backup = work / f"backup-{entry['name']}"
            exists = target.exists()
            if exists:
                target.rename(backup)
            replaced.append((target, backup, exists))
            staged.rename(target)
        pending.replace(manifest)
    except (OSError, VendorError):
        for target, backup, existed in reversed(replaced):
            if target.exists():
                shutil.rmtree(target)
            if existed:
                backup.rename(target)
        raise


def execute(root: Path, args: argparse.Namespace) -> int:
    data = load(root)
    original_manifest = (root / "vendor.json").read_bytes()
    if args.command == "verify":
        print(f"vendor.json: {len(data['skills'])} valid entries (offline; no upstream audit)")
        return 0
    if args.command == "add":
        if any(entry["name"] == args.name for entry in data["skills"]):
            raise VendorError(f"{args.name}: already registered; use update")
        entry = {key: getattr(args, key) for key in
                 ("name", "repo", "path", "ref", "license", "license_path")}
        entry.update(commit="0" * 40, patches=args.patch)
        validate_entry(root, entry)
        if local_path(root, f"skills/{args.name}").exists():
            raise VendorError(f"skills/{args.name} already exists; will not overwrite it")
        data["skills"].append(entry)
        entries = [entry]
    else:
        entries = select(data, args.name)
    if not entries:
        print("No vendored skills. Use add to import one.")
        return 0
    scratch = root / ".local" / "tmp"
    if (root / ".local").is_symlink() or scratch.is_symlink():
        raise VendorError(".local/tmp must not be a symlink")
    scratch.mkdir(parents=True, exist_ok=True)
    problems = 0
    prepared = []
    with tempfile.TemporaryDirectory(prefix="vendor-", dir=scratch) as tmp:
        work = Path(tmp)
        for index, entry in enumerate(entries):
            try:
                target = local_path(root, f"skills/{entry['name']}")
                current = snapshot(target)
                pin = entry["commit"]
                at_pin = None
                raw_pin = None
                if args.command != "add":
                    _, at_pin, raw_pin = materialise(root, entry, pin, work / f"{index}-pin")
                    drift = differences(snapshot(at_pin), current)
                    if drift and args.command == "check":
                        print(f"EDITED {entry['name']}: local copy differs from its pin and patches")
                        print("\n".join(f"  {line}" for line in drift))
                        problems = max(problems, 1)
                    elif drift and target.exists() and not args.force:
                        raise VendorError(f"{entry['name']}: local edits; save them as a patch or use --force to discard them")
                if args.command == "sync":
                    staged = at_pin
                    commit = pin
                else:
                    revision = getattr(args, "commit", None) or entry["ref"]
                    commit, staged, upstream = materialise(root, entry, revision, work / f"{index}-head")
                    if args.command == "check":
                        moved = differences(raw_pin, upstream)
                        if moved:
                            print(f"UPDATE {entry['name']}: {pin[:12]} -> {commit[:12]} ({entry['ref']})")
                            print("\n".join(f"  {line}" for line in moved))
                            problems = max(problems, 1)
                        else:
                            print(f"CURRENT {entry['name']}: upstream skill and license unchanged ({entry['ref']})")
                        continue
                entry["commit"] = commit
                prepared.append((entry, staged, current))
                print(f"prepared {entry['name']}: {pin[:12]} -> {commit[:12]}")
                for line in differences(current, snapshot(staged)):
                    print(f"  {line}")
            except (VendorError, OSError) as exc:
                if args.command != "check":
                    raise
                print(f"ERROR {entry['name']}: {exc}", file=sys.stderr)
                problems = 2
        if args.command != "check":
            publish(root, data, prepared, work, original_manifest)
            print("Saved skills and vendor.json. Review the diff, sync Codex policy, bump both plugin versions,")
            print("run scripts/validate.sh, and reinstall the plugin to refresh harness caches.")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("check", "report local edits and available upstream skill/license changes"),
        ("update", "repin selected skills to their tracked refs (default: all)"),
        ("sync", "reproduce selected skills from their exact pins (default: all)"),
    ):
        child = sub.add_parser(command, help=help_text)
        child.add_argument("name", nargs="*")
        if command != "check":
            child.add_argument("--force", action="store_true", help="discard local edits")
    sub.add_parser("verify", help="validate the manifest and patch paths without network access")
    child = sub.add_parser("add", help="import one skill and record its source and exact commit")
    for key in ("name", "repo", "path", "license"):
        child.add_argument(f"--{key}", required=True)
    child.add_argument("--ref", default="HEAD", help="branch, tag, full ref or commit to track; default: remote HEAD")
    child.add_argument("--commit", help="initial revision to pin while tracking --ref for future updates")
    child.add_argument("--license-path", default="LICENSE", help="upstream license file, relative to repository root")
    child.add_argument("--patch", action="append", default=[], help="repeatable path under vendor/patches/")
    args = parser.parse_args(argv)
    try:
        return execute(ROOT, args)
    except (VendorError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Fetch other people's agent setups so they can be read at a known version.

Vendoring copies a component in to *use* it; this fetches one in to *read* it.
Nothing here is committed — the working copies land in `.cache/prior-art/`, which
is gitignored — so the only durable record is the version written into a
decision under `docs/decisions/`.

    prior_art.py list             registered sources and when each was last read
    prior_art.py pull [name...]   fetch the current version into .cache/prior-art/
    prior_art.py diff [name...]   what changed upstream since it was last read
    prior_art.py seen <name>      record the cached version as read (after deciding)
    prior_art.py approve <name>   promote a proposed candidate to a tracked source
    prior_art.py add ...          register a new source and fetch it

A source is either a git repo (pinned by commit) or a local directory that some
tool installs, such as a harness's own bundled skills (pinned by content digest,
because there is no commit to name). Both are read-only reading material.

Read the cache, never memory. A model's recollection of someone else's repo
layout is confident, specific and frequently wrong.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # importing vendor.py must not litter scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vendor import compare, head_of, run, snapshot  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "prior-art.json"
CACHE = ROOT / ".cache" / "prior-art"
PIN = ".pin.json"


def load() -> dict:
    if not MANIFEST.is_file():
        sys.exit(f"missing {MANIFEST}")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def select(data: dict, names: list[str]) -> list[dict]:
    entries = data.get("sources", [])
    if not names:
        return entries
    by_name = {e["name"]: e for e in entries}
    unknown = [n for n in names if n not in by_name]
    if unknown:
        sys.exit(f"not in prior-art.json: {', '.join(unknown)}")
    return [by_name[n] for n in names]


def is_local(entry: dict) -> bool:
    return not entry.get("repo")


def local_root(entry: dict) -> Path:
    root = Path(entry["path"]).expanduser()
    if not root.is_dir():
        sys.exit(f"{entry['name']}: {root} does not exist — is the tool installed?")
    return root


def ident(pin: dict) -> str:
    """The version of a source: a commit for git, a content digest for local."""
    return pin.get("commit") or pin["digest"]


def files(root: Path) -> dict[str, str]:
    return {k: v for k, v in snapshot(root).items() if k != PIN}


def digest(root: Path) -> str:
    h = hashlib.sha256()
    for name, file_hash in sorted(files(root).items()):
        h.update(f"{name}:{file_hash}\n".encode())
    return h.hexdigest()


def tool_version(entry: dict) -> str | None:
    cmd = entry.get("version_cmd")
    if not cmd:
        return None
    try:
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


# --- fetching ---------------------------------------------------------------

def fetch(entry: dict, commit: str, dest: Path) -> Path:
    """Sparse, blob-filtered, depth-1 fetch of the entry's paths at `commit`."""
    paths = entry.get("paths") or []
    run(["git", "init", "-q", str(dest)])
    run(["git", "-C", str(dest), "remote", "add", "origin", entry["repo"]])
    if paths:
        run(["git", "-C", str(dest), "sparse-checkout", "init", "--no-cone"])
        sparse = dest / ".git" / "info" / "sparse-checkout"
        sparse.write_text("".join(f"/{p}\n" for p in paths), encoding="utf-8")
    run(["git", "-C", str(dest), "fetch", "-q", "--depth", "1",
         "--filter=blob:none", "origin", commit])
    run(["git", "-C", str(dest), "checkout", "-q", "FETCH_HEAD"])
    return dest


def materialise(entry: dict, commit: str, checkout: Path, target: Path) -> None:
    """Copy the fetched paths into `target`, replacing whatever was there."""
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for rel in entry.get("paths") or ["."]:
        src = checkout / rel
        if not src.is_dir():
            sys.exit(f"{entry['name']}: `{rel}` is not a directory at {commit[:12]}")
        dst = target if rel == "." else target / rel
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git"),
                        dirs_exist_ok=True)


def copy_local(entry: dict, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(local_root(entry), target,
                    ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))


def stamp(entry: dict, target: Path, **version: str | None) -> None:
    pin = {"name": entry["name"], "fetched": dt.date.today().isoformat()}
    if is_local(entry):
        pin["source"] = str(Path(entry["path"]).expanduser())
    else:
        pin["repo"] = entry["repo"]
        pin["ref"] = entry.get("ref", "main")
    pin.update({k: v for k, v in version.items() if v})
    (target / PIN).write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")


def cached_pin(name: str) -> dict | None:
    path = CACHE / name / PIN
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# --- commands ---------------------------------------------------------------

def cmd_list(args: argparse.Namespace) -> int:
    data = load()
    print("tracked")
    for entry in select(data, args.name):
        read = entry.get("read") or {}
        pin = cached_pin(entry["name"])
        where = f"cached {ident(pin)[:12]}" if pin else "not pulled"
        seen = f"read {ident(read)[:12]} on {read['date']}" if read else "never read"
        kind = "local" if is_local(entry) else "git"
        print(f"  {entry['name']:<22} {kind:<6} {where:<20} {seen}")
        print(f"    {entry.get('upstream', entry.get('repo', entry.get('path')))}")
        if entry.get("why"):
            print(f"    {entry['why']}")
    if args.name:
        return 0
    if data.get("candidates"):
        print("\ncandidates (proposed, not tracked — `approve <name>` to take one on)")
        for c in data["candidates"]:
            print(f"  {c['name']:<22} {c.get('upstream', c.get('path', ''))}")
            print(f"    {c['why']}")
    if data.get("reading"):
        print("\nreading (fetch live, nothing to pin)")
        for r in data["reading"]:
            print(f"  {r['url']}\n    {r['why']}")
    return 0


def cmd_pull(args: argparse.Namespace) -> int:
    data = load()
    for entry in select(data, args.name):
        name = entry["name"]
        target = CACHE / name
        before = files(target)
        if is_local(entry):
            copy_local(entry, target)
            version = digest(target)
            stamp(entry, target, digest=version, tool=tool_version(entry))
        else:
            version = head_of(entry["repo"], entry.get("ref", "main"))
            with tempfile.TemporaryDirectory() as tmp:
                checkout = fetch(entry, version, Path(tmp) / "src")
                materialise(entry, version, checkout, target)
            stamp(entry, target, commit=version)
        after = files(target)
        state = "unchanged" if before and before == after else "pulled"
        print(f"{state}  {name} @ {version[:12]} -> .cache/prior-art/{name} "
              f"({len(after)} files)")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    data = load()
    moved = 0
    for entry in select(data, args.name):
        name = entry["name"]
        read = entry.get("read") or {}
        if not read:
            print(f"unread   {name}: never recorded as read — `pull` and read it")
            continue
        was = ident(read)
        if is_local(entry):
            with tempfile.TemporaryDirectory() as tmp:
                live = Path(tmp) / "live"
                copy_local(entry, live)
                now = digest(live)
                if now == was:
                    print(f"ok       {name}: unchanged on disk since you read it "
                          f"({was[:12]})")
                    continue
                drift = compare("was", files(CACHE / name), "now", files(live))
            moved += 1
            was_tool = (cached_pin(name) or {}).get("tool")
            now_tool = tool_version(entry)
            note = ""
            if now_tool and was_tool and now_tool != was_tool:
                note = f"  ({was_tool} -> {now_tool})"
            elif now_tool:
                note = f"  (still {now_tool})"
            print(f"MOVED    {name}: {was[:12]} -> {now[:12]} since {read['date']}{note}")
            print("\n".join(drift) or "    (cache is not at the version you read; re-pull)")
            continue

        now = head_of(entry["repo"], entry.get("ref", "main"))
        if now == was:
            print(f"ok       {name}: {entry.get('ref', 'main')} still at the commit "
                  f"you read ({was[:12]})")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            for label, commit in (("was", was), ("now", now)):
                checkout = fetch(entry, commit, Path(tmp) / f"{label}-src")
                materialise(entry, commit, checkout, Path(tmp) / label)
            drift = compare("was", files(Path(tmp) / "was"),
                            "now", files(Path(tmp) / "now"))
        if not drift:
            print(f"ok       {name}: moved to {now[:12]}, tracked paths unchanged")
            continue
        moved += 1
        print(f"MOVED    {name}: {was[:12]} -> {now[:12]} since {read['date']}")
        print("\n".join(drift))
    return 1 if moved else 0


def cmd_seen(args: argparse.Namespace) -> int:
    data = load()
    entry = select(data, [args.name])[0]
    pin = cached_pin(args.name)
    if not pin:
        sys.exit(f"{args.name}: nothing in .cache/prior-art — run `pull` first")
    key = "digest" if is_local(entry) else "commit"
    entry["read"] = {key: ident(pin), "date": dt.date.today().isoformat()}
    save(data)
    print(f"{args.name}: recorded as read at {ident(pin)[:12]}. Cite that {key} in "
          "the decision record.")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    data = load()
    candidates = data.get("candidates", [])
    match = next((c for c in candidates if c["name"] == args.name), None)
    if not match:
        sys.exit(f"no candidate named `{args.name}` — see `list`")
    candidates.remove(match)
    match.pop("proposed", None)
    data.setdefault("sources", []).append(match)
    save(data)
    print(f"{args.name}: candidate -> tracked source")
    args.name = [args.name]
    return cmd_pull(args)


def cmd_add(args: argparse.Namespace) -> int:
    data = load()
    entries = data.setdefault("sources", [])
    if any(e["name"] == args.name for e in entries):
        sys.exit(f"`{args.name}` is already in prior-art.json")
    if bool(args.repo) == bool(args.local):
        sys.exit("give exactly one of --repo (a git source) or --local (a directory)")
    entry = {
        "name": args.name,
        "repo": args.repo,
        "paths": [p.strip("/") for p in args.path],
        "ref": args.ref if args.repo else None,
        "path": args.local,
        "version_cmd": args.version_cmd,
        "why": args.why,
        "upstream": args.upstream,
    }
    entries.append({k: v for k, v in entry.items() if v})
    save(data)
    print(f"added {args.name}")
    args.name = [args.name]
    return cmd_pull(args)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="registered sources and their read state")
    p.add_argument("name", nargs="*")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("pull", help="fetch the current version into the cache")
    p.add_argument("name", nargs="*")
    p.set_defaults(func=cmd_pull)

    p = sub.add_parser("diff", help="what changed upstream since it was last read")
    p.add_argument("name", nargs="*")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("seen", help="record the cached version as read")
    p.add_argument("name")
    p.set_defaults(func=cmd_seen)

    p = sub.add_parser("approve", help="promote a proposed candidate to a tracked source")
    p.add_argument("name")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("add", help="register a new source and fetch it")
    p.add_argument("--name", required=True)
    p.add_argument("--repo", help="clone URL of a git source")
    p.add_argument("--local", help="directory of a locally installed source")
    p.add_argument("--path", action="append", default=[],
                   help="subdirectory to fetch; repeatable; git sources only")
    p.add_argument("--ref", default="main")
    p.add_argument("--version-cmd", help="command printing the tool's version (local sources)")
    p.add_argument("--why", help="one line: what this source is good for")
    p.add_argument("--upstream", help="human-facing URL")
    p.set_defaults(func=cmd_add)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Detect, show, check and write pstack's per-role model rule for one harness.

The rule is a managed block that the harness loads into every session:

    Claude Code   ~/.claude/rules/pstack-models.md        (whole file is the block)
    Codex         $CODEX_HOME/AGENTS.override.md if present, else AGENTS.md
                  (default home ~/.codex; block inside the file)

Inside the block, one line per role: `<role>: <value>[, <value>...]`. A value is
`inherit-parent`, `auto`, `<model>` or, on Codex, `<model>@<effort>`.

    pstack_models.py detect [--harness H]          harness, target path, usable models
    pstack_models.py show   [--harness H]          current mapping, or "absent"
    pstack_models.py check  [--harness H] [PATH]   validate the block (exit 1 on error)
    pstack_models.py write  [--harness H] --set 'role=v1, v2' ...   write, then check

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROLES = [
    "feature, refactoring",
    "bug-fix",
    "perf-issue",
    "hillclimb",
    "judgment and prose",
    "hardest tasks",
    "how explorer",
    "how explainer",
    "how critics",
    "why investigators",
    "why synthesizer",
    "reflect tooling",
    "reflect judgment, divergent, synthesizer",
    "arena runners",
    "arena cross-judge pool",
    "swarm workers",
    "architect runners",
    "interrogate reviewers",
]
PANELS = {
    "how critics",
    "arena runners",
    "arena cross-judge pool",
    "architect runners",
    "interrogate reviewers",
}
ALIASES = ("inherit-parent", "auto")

# What the Claude Code Agent tool's `model` parameter accepts per call. Full
# model IDs are frontmatter-only, so they are rejected here on purpose. Update
# this set when the tool's schema changes; `detect` tells the user to confirm it.
CLAUDE_MODELS = {"sonnet", "opus", "haiku", "fable"}

# Codex reasoning efforts (config reference plus the models page). The models
# cache narrows this per model when present.
CODEX_EFFORTS = {"minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
MODEL_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+\-\[\]]*$")

BEGIN = "<!-- pstack-models:begin -->"
END = "<!-- pstack-models:end -->"
HARNESS_NAMES = {"claude": "Claude Code", "codex": "Codex"}


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def target_path(harness: str) -> Path:
    if harness == "claude":
        return Path.home() / ".claude" / "rules" / "pstack-models.md"
    # Codex reads AGENTS.override.md instead of AGENTS.md when it exists, so a
    # block written to AGENTS.md would be invisible in that case.
    override = codex_home() / "AGENTS.override.md"
    return override if override.is_file() else codex_home() / "AGENTS.md"


def detect_harness(explicit: str | None) -> str:
    if explicit:
        return explicit
    is_claude = "CLAUDECODE" in os.environ
    is_codex = any(name.startswith("CODEX_") for name in os.environ)
    if is_claude and not is_codex:
        return "claude"
    if is_codex and not is_claude:
        return "codex"
    sys.exit("cannot tell Claude Code from Codex here; pass --harness claude|codex")


# --- models -----------------------------------------------------------------


def codex_models() -> dict[str, set[str]] | None:
    """Model slug -> supported efforts, from Codex's own cache. None if absent."""
    cache = codex_home() / "models_cache.json"
    if not cache.is_file():
        return None
    try:
        data = json.loads(cache.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    models: dict[str, set[str]] = {}
    for entry in data.get("models", []):
        if not isinstance(entry, dict) or entry.get("visibility") == "hide":
            continue
        slug = entry.get("slug")
        if not isinstance(slug, str):
            continue
        levels = entry.get("supported_reasoning_levels") or []
        efforts = {lvl.get("effort") for lvl in levels if isinstance(lvl, dict)}
        models[slug] = {e for e in efforts if isinstance(e, str)}
    return models or None


def validate_value(harness: str, value: str, codex_cache: dict[str, set[str]] | None) -> str | None:
    if value in ALIASES:
        return None
    model, effort = (value.rsplit("@", 1) + [None])[:2] if "@" in value else (value, None)
    if not MODEL_TOKEN.fullmatch(model or ""):
        return f"invalid model token {model!r}"
    if harness == "claude":
        if effort is not None:
            return (
                f"{value!r}: Claude Code's Agent tool takes no per-call effort; "
                "use a bare model alias, and set effort in an agent definition if needed"
            )
        if model not in CLAUDE_MODELS:
            return f"{model!r} is not an Agent tool model alias ({', '.join(sorted(CLAUDE_MODELS))})"
        return None
    if effort is not None and effort not in CODEX_EFFORTS:
        return f"unsupported effort {effort!r} (one of {', '.join(sorted(CODEX_EFFORTS))})"
    if codex_cache is not None:
        if model not in codex_cache:
            return f"{model!r} is not in Codex's model list ({', '.join(sorted(codex_cache))})"
        if effort is not None and codex_cache[model] and effort not in codex_cache[model]:
            return f"{model!r} does not offer effort {effort!r} ({', '.join(sorted(codex_cache[model]))})"
    return None


# --- block format -----------------------------------------------------------


def header(harness: str) -> str:
    name = HARNESS_NAMES[harness]
    return f"""# pstack model configuration ({name})

Per-role subagent models for pstack skills running in {name}. Managed by
ai-bench's `setup-pstack`; re-run it to change a role. When a pstack skill
asks for `~/.cursor/rules/pstack-models.mdc`, use these lines instead.

One line per role. `inherit-parent` or `auto` means spawn the subagent with no
model or effort override so it inherits the parent session's. A panel role
lists one entry per subagent to spawn, alias entries included."""


def render(harness: str, mapping: dict[str, list[str]]) -> str:
    lines = [BEGIN, header(harness), ""]
    lines += [f"{role}: {', '.join(mapping[role])}" for role in ROLES if role in mapping]
    lines.append(END)
    return "\n".join(lines) + "\n"


def split_block(text: str) -> tuple[str, str | None, str]:
    """Return (before, block-or-None, after) for the managed block in `text`."""
    start = text.find(BEGIN)
    if start < 0:
        return text, None, ""
    end = text.find(END, start)
    if end < 0:
        sys.exit(f"found {BEGIN} without {END}; repair the file by hand first")
    end += len(END)
    if text[end : end + 1] == "\n":
        end += 1
    return text[:start], text[start:end], text[end:]


def parse_block(harness: str, block: str) -> tuple[dict[str, list[str]], list[str]]:
    """Role lines inside the block. Anything that is neither header prose nor a role line is an error."""
    prose = set(header(harness).splitlines())
    mapping: dict[str, list[str]] = {}
    errors: list[str] = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line in (BEGIN, END) or raw in prose:
            continue
        role = next((r for r in ROLES if line.startswith(r + ":")), None)
        if role is None:
            errors.append(f"unrecognised line: {line!r}")
            continue
        if role in mapping:
            errors.append(f"duplicate role {role!r}")
        values = [v.strip() for v in line[len(role) + 1 :].split(",")]
        mapping[role] = [v for v in values if v]
    return mapping, errors


def validate(harness: str, mapping: dict[str, list[str]], codex_cache: dict[str, set[str]] | None) -> list[str]:
    errors = []
    missing = [r for r in ROLES if r not in mapping]
    if missing:
        errors.append(f"missing roles: {', '.join(missing)}")
    for role, values in mapping.items():
        if not values:
            errors.append(f"{role!r} has no value")
            continue
        if role not in PANELS and len(values) != 1:
            errors.append(f"{role!r} is not a panel; it takes exactly one value, got {len(values)}")
        for value in values:
            problem = validate_value(harness, value, codex_cache)
            if problem:
                errors.append(f"{role!r}: {problem}")
    return errors


def check_text(harness: str, text: str, codex_cache: dict[str, set[str]] | None) -> list[str]:
    _, block, _ = split_block(text)
    if block is None:
        return [f"no {BEGIN} ... {END} block"]
    mapping, errors = parse_block(harness, block)
    return errors + validate(harness, mapping, codex_cache)


def write_mapping(harness: str, path: Path, mapping: dict[str, list[str]]) -> None:
    """Replace the managed block, keeping everything around it byte-for-byte."""
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    before, block, after = split_block(existing)
    if block is None and existing and not existing.endswith("\n"):
        before += "\n"
    if block is None and existing:
        before += "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(before + render(harness, mapping) + after, encoding="utf-8")


# --- commands ---------------------------------------------------------------


def parse_set(items: list[str]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for item in items:
        role, sep, rest = item.partition("=")
        role = role.strip()
        if not sep or role not in ROLES:
            sys.exit(f"--set expects '<role>=<value>[, <value>]' with a known role, got {item!r}")
        mapping[role] = [v.strip() for v in rest.split(",") if v.strip()]
    return mapping


def cmd_detect(args: argparse.Namespace) -> int:
    harness = detect_harness(args.harness)
    print(f"harness: {harness}")
    print(f"target:  {target_path(harness)}")
    print(f"aliases: {', '.join(ALIASES)}")
    if harness == "claude":
        print(f"models:  {', '.join(sorted(CLAUDE_MODELS))}  (Agent tool `model` values; no per-call effort)")
        print("confirm: the Agent tool schema in this session lists the same values")
        return 0
    cache = codex_models()
    if cache is None:
        print("models:  no models cache; confirm slugs against `codex --model`/`/model` and pass them explicitly")
        return 0
    for slug in sorted(cache):
        efforts = ", ".join(sorted(cache[slug])) or "(default effort only)"
        print(f"models:  {slug}  efforts: {efforts}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    harness = detect_harness(args.harness)
    path = target_path(harness)
    if not path.is_file():
        print(f"absent {path}")
        return 0
    _, block, _ = split_block(path.read_text(encoding="utf-8"))
    if block is None:
        print(f"absent (no managed block in {path})")
        return 0
    mapping, _ = parse_block(harness, block)
    for role in ROLES:
        print(f"{role}: {', '.join(mapping.get(role, ['<missing>']))}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    harness = detect_harness(args.harness)
    path = args.path or target_path(harness)
    if not path.is_file():
        print(f"ERROR: {path} does not exist", file=sys.stderr)
        return 1
    errors = check_text(harness, path.read_text(encoding="utf-8"), codex_models() if harness == "codex" else None)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"ok {path}")
    return 0


def cmd_write(args: argparse.Namespace) -> int:
    harness = detect_harness(args.harness)
    mapping = parse_set(args.set)
    cache = codex_models() if harness == "codex" else None
    errors = validate(harness, mapping, cache)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    path = args.path or target_path(harness)
    write_mapping(harness, path, mapping)
    remaining = check_text(harness, path.read_text(encoding="utf-8"), cache)
    if remaining:
        for error in remaining:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"wrote {path}")
    for role in sorted(PANELS, key=ROLES.index):
        print(f"panel {role}: {len(mapping[role])} subagent(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("detect", cmd_detect), ("show", cmd_show), ("check", cmd_check), ("write", cmd_write)):
        p = sub.add_parser(name)
        p.add_argument("--harness", choices=sorted(HARNESS_NAMES))
        if name in ("check", "write"):
            p.add_argument("--path", type=Path, help="override the target file (tests, dry runs)")
        if name == "write":
            p.add_argument("--set", action="append", default=[], metavar="ROLE=VALUES", required=True)
        p.set_defaults(func=func)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

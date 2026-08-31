# AGENTS.md

Repo instructions for Claude Code and Codex. `CLAUDE.md` is a symlink to this
file — one source of truth, because two copies drift.

## What this repo is

Anatolii's agentic-AI workbench, packaged so that **both Claude Code and Codex
install it as a plugin from this same repo**.
`git@github.com:platonoff-dev/ai-bench.git`.

The repo is both the marketplace and its single plugin: `.claude-plugin/` and
`.codex-plugin/` hold the plugin manifests, and each harness's marketplace
manifest lists this repo as its one entry with source `./`.

**The repo is currently empty of components** — no agents, no skills, no
commands, no hooks, no MCP servers. Both harnesses report 0 components and that
is the intended state. Components get added deliberately, one at a time. Do not
scaffold placeholder components; create a directory only when something real
goes in it.

There is no build, no test suite and no lint. The artifacts are Markdown
definitions and JSON config; they are validated by the two validators in the
README and by running them.

## Two things that will bite

**1. Every change needs a version bump in both manifests.** Both harnesses cache
a copy of the plugin keyed on its version, so an edit to the working tree is not
live until the version changes and the plugin is reinstalled. The README has the
loop. This is the single most likely reason "my change did nothing".

**2. Subagents are the one asymmetry between the harnesses.** Both discover a
plugin's `skills/`, `commands/` and `.mcp.json` the same way. Claude Code also
discovers `agents/*.md` from the plugin — **Codex does not look inside a plugin
for subagents at all.** It reads `$CODEX_HOME/agents/*.toml`, a flat directory of
TOML files with `name`, `description` and `developer_instructions` keys.

So the first subagent added here needs a generation step: `agents/*.md` stays the
single source of truth and a script converts it to TOML for Codex. Serialise the
body as a TOML **literal** string (`'''…'''`), never a basic string — role text
carries backslashes (a `grep -E '\(class\|def\)'`, say) that a basic string reads
as invalid escapes. Parse the result back with `tomllib` before writing it.

Keep any component's text harness-neutral so one file serves both: name both
instruction files ("the repo's `CLAUDE.md` / `AGENTS.md`") rather than either
alone, and never blanket-rename `claude`→`codex` in a component — it corrupts
real filesystem paths like `.claude/skills/…`.

## Conventions when adding a component

**Subagents** — `agents/<name>.md`, YAML frontmatter with `name` and
`description` only. Never set `tools:`: omitting it is what lets the agent
inherit `Skill` and delegate. The `description` is the routing signal, so state
what it reads and writes, when to run it, and one "never" clause. Body opens
with the single job in bold, then `## Hard rules`.

**Skills** — `skills/<name>/SKILL.md` plus optional `references/`, `scripts/`,
`assets/`. Keep `SKILL.md` short and push detail into `references/`, loaded on
demand.

**The filter for adding a skill at all:** one discipline, with a runnable check,
in a few hundred words, that says no to things. Reference manuals and grab bags
are rejected — dozens of trivia skills poison description-matching, which
degrades every other skill in the set.

**Manifest differences to respect:** the Codex manifest rejects a `hooks` field
and requires strict semver; Claude's is the more permissive of the two, so
validate against Codex's first. Keep `name`, `version` and `description`
identical across the two files.

## Sibling repos

Siblings under `~/dev/personal/` each carry their own `CLAUDE.md`/`AGENTS.md`
and should be read there, not from here. Two are prior art for a repo-local
(non-plugin) skill layout: `life-assistant/.agents/skills/manage-life/` and
`opportunity-scout/.agents/skills/research-opportunities/`.

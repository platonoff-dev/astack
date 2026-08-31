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

Components get added deliberately, one at a time. Do not scaffold placeholder
components; create a directory only when something real goes in it. The plugin
ships `skills/task-intake`, written here, and `skills/unslop`, vendored from
`cursor/plugins`.

There is no build or lint setup. The artifacts are Markdown definitions, JSON
config, and small Python helpers. Validate with the two plugin validators in the
README, `scripts/vendor.py check`, and the task-intake checker's regression
checks. Trial skill behavior on real work; passing a format check is not proof
that its instructions make good decisions.

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

## Vendored third-party components

`vendor.json` pins every component copied in from someone else's repo, and
`scripts/vendor.py` materialises, diffs and bumps them. The README has the
command table.

**The files are committed on purpose.** Both harnesses install a plugin by
copying the repo tree and neither initialises git submodules, so a submodule or
subtree would arrive empty on someone else's `plugin install`. That constraint is
what rules out every link-based approach; the pin plus a re-materialising script
is the substitute.

Rules that keep this honest:

- **Never hand-edit a vendored directory.** `sync` and `update` replace it
  wholesale, so the edit is lost; `check` reports it as `EDITED`. Wanting
  different behaviour means adding your own skill alongside, not patching the
  copy.
- **Carry the upstream licence.** `license_path` in the entry copies the
  upstream `LICENSE` in beside the `SKILL.md`. MIT and Apache-2.0 both require
  the notice to travel with the copy; check the licence before vendoring at all.
- **Pin a commit, not a branch.** `ref` says which branch to follow on `update`;
  `commit` is what `sync` actually reproduces. Never drop the commit.
- **A vendored skill keeps its upstream `name:`.** If you later install the
  upstream plugin itself, both copies claim that name — pick one.
- After `update`, bump the plugin version in both manifests and reinstall, or
  neither harness sees the new content.

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

## Repo-level components

Not everything here belongs in the plugin. `.agents/skills/<name>/` holds skills
that serve *this* repo's own upkeep and are never shipped to anyone installing
the plugin, with a symlink at `.claude/skills/<name>` so both harnesses find them
(same direction as `CLAUDE.md → AGENTS.md`: the `.agents` copy is the real one).
A fresh Claude Code session resolves that symlink and lists the skill, so it is
the layout to copy for the next one.

They are read live from the working tree, so **a repo-level skill needs no
version bump and no reinstall** — the one rule from "Two things that will bite"
that does not apply here.

`prior-art` is the first: deciding what to take from someone else's agent setup.
It is deliberately paired with, but separate from, vendoring:

| | reads | writes | question it answers |
|---|---|---|---|
| `vendor.json` + `scripts/vendor.py` | upstream at a pin | `skills/<name>/`, committed | what do we *use* |
| `prior-art.json` + `scripts/prior_art.py` | upstream at head, or a locally installed tree | `.cache/prior-art/`, gitignored | what do we *read* |

Conflating them is how a reading copy quietly becomes a dependency. `prior_art.py
diff` exits 1 when a source moved since a decision cited it — for a git source
that means the commit moved, for a local one that the content digest changed,
reported alongside the tool version that changed it.

Decisions land in `docs/decisions/NNN-slug.md`, rejections included — an
unrecorded rejection gets researched again. `prior-art.json` also carries
`candidates`, proposed sources that stay untracked until Anatolii approves one
with `prior_art.py approve <name>`. Never enrol a source or vendor a skill on
your own judgement.

## Sibling repos

Siblings under `~/dev/personal/` each carry their own `CLAUDE.md`/`AGENTS.md`
and should be read there, not from here. Two are prior art for a repo-local
(non-plugin) skill layout: `life-assistant/.agents/skills/manage-life/` and
`opportunity-scout/.agents/skills/research-opportunities/`.

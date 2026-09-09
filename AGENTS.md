# AGENTS.md

Repo instructions for Claude Code and Codex. `CLAUDE.md` is a symlink to this
file — one source of truth, because two copies drift.

## What this repo is

Anatolii's agentic-AI workbench: **[pstack](https://github.com/cursor/plugins/tree/main/pstack)
decoupled from Cursor**, packaged so that both Claude Code and Codex install it
as a plugin from this same repo (`git@github.com:platonoff-dev/astack.git`).

The repo is both the marketplace and its single plugin. `.claude-plugin/` and
`.codex-plugin/` hold the plugin manifests, and each harness's marketplace
manifest lists this repo as its one entry with source `./`.

49 skills ship: 44 from pstack, plus `task-interview`, `pick-next`,
`merge-brief`, `weekly-report` and `setup-tracker`, written by Anatolii. Two
subagents ship, both pstack's. `setup-pstack` is the one skill replaced outright
rather than adapted.

pstack's `poteto-mode` router ships here as **`rigor`**, its subagent as
`rigor-agent`. Upstream's frontmatter is `name: Poteto Mode`; Claude Code
registers that as `/astack:Poteto Mode`, splits it at the space and answers
"Unknown command: /astack:Poteto". A one-word router is also faster to type.
`validate.sh` fails any skill whose frontmatter `name` is not its kebab-case
directory, so a re-import cannot bring the space back. Keep the `rigor` name
when pulling upstream changes.

pstack's own `README.md` is kept at `docs/upstream/pstack-README.md` as the
record of what upstream ships. It is a snapshot, not a live document: it still
describes `make-bot-ui` and the Cursor rule path, both of which are gone here,
and calls the router `poteto-mode`.

## This repo is public, and that is a constraint on every commit

`github.com/platonoff-dev/astack` is public. Anything committed here is
published, and a force-push does not unpublish what was already fetched or
indexed. **Nothing organisation-specific may enter this repo**, and
`scripts/validate.sh` has a `no organisation-specific content` check that fails
the run on any of it:

| Never here | Where it goes instead |
|---|---|
| Employer, product, team or internal-repo names; internal hostnames | nowhere — a skill names a *role* |
| Tracker hosts, project keys, real item keys, custom-field ids, account or document ids | the tracker adapter, outside this repo |
| A colleague's name, or a quotation from a private channel, document or review | nowhere, ever. Paraphrase the *failure* and drop the person |
| Real work-item titles, real metrics, real deadlines, unreleased roadmap | an invented worked example that carries the same shape |
| Internal process that would embarrass someone if read outside | the discipline stated neutrally, or not at all |

This was learned the expensive way: the four work skills shipped with a CEO's
private remarks quoted by name, a squad's Jira ids and a real status report in
them, and it was public for two days before anyone noticed. The check exists so
the next re-import or paste cannot repeat it.

The mechanism that makes the work skills possible at all is the **tracker
adapter** — one TOML file, written by `setup-tracker`, holding every value a
skill would otherwise hardcode. `pick-next`, `weekly-report` and `merge-brief` read it and stop
with a clear message when it is absent.
Its format lives in `skills/setup-tracker/references/adapter-format.md`; the
file itself lives in `~/.config/pstack/` or in the private repo it describes,
and **never** inside this one.

When a skill needs a fact it does not have, the answer is a new adapter role,
not a value in a `SKILL.md`.

## The decoupling is the point, and it is load-bearing

Upstream targets Cursor. Four kinds of coupling were removed, and each one is
guarded by a check in `scripts/validate.sh` so a re-import cannot quietly
reintroduce it. **Run `scripts/validate.sh` before every commit.**

| Coupling | What it became |
|---|---|
| `~/.cursor/rules/pstack-models.mdc` | `~/.claude/rules/pstack-models.md` (a documented user-level Claude Code load path) or the Codex home `AGENTS.md`, both written by `setup-pstack` |
| Model slugs (`grok-4.6-fast-xhigh`, …) | **no skill names a model at all.** They name a *role* and defer the value to the model rule |
| `Task` params (`generalPurpose`, `readonly:`, `environment:`) | `general-purpose`; a read-only agent type (`Explore`) where `readonly: true` was meant; remote/cloud agents described neutrally |
| `cursor-team-kit`'s `control-ui` / `control-cli` / `deslop` | the project's own `verify-*` skill (which `create-verification-skill` generates), plus `no-comments` and the harness's cleanup pass |

Two rules follow from this:

- **Never write a model slug into a skill.** A slug neither harness can spawn
  breaks the delegation outright, which is why it is a hard check and not a
  style preference. Roles live in `setup-pstack`'s `ROLES` list; values live in
  the rule the user generates.
- **Never reintroduce a `~/.cursor/` path or a `cursor-team-kit` skill name.**
  Wanting different behaviour means editing the skill here, not pointing at a
  plugin nobody installs.

## Three things that will bite

**1. Every change needs a version bump in both manifests.** Both harnesses
cache a copy of the plugin keyed on its version, so an edit to the working tree
is not live until the version changes and the plugin is reinstalled. The README
has the loop. This is the single most likely reason "my change did nothing".

**2. The Codex validator fails by design, and that is not permission to ignore
it.** 44 skills carry `disable-model-invocation: true`, which is how Claude Code
is told to invoke them explicitly only. Codex rejects that field and reads
`<skill>/agents/openai.yaml` with `policy.allow_implicit_invocation: false`
instead. Both are correct for their harness, so the field cannot be removed —
and dropping it would make 44 heavy skills auto-fire on description matching.
`scripts/validate.sh` filters exactly that one error message, counts what it
filtered, and **fails if the count stops matching the skills that declare it**.
Every other Codex error still fails the run.

After adding a skill or editing a description, run
`scripts/sync_codex_policy.py`. It regenerates the `openai.yaml` files from the
frontmatter; `--check` reports drift without writing.

**3. Subagents are the one asymmetry left.** Both harnesses discover a plugin's
`skills/` and `.mcp.json` the same way. Claude Code also discovers
`agents/*.md` — **Codex does not look inside a plugin for subagents at all.** It
reads `$CODEX_HOME/agents/*.toml`, a flat directory of TOML files with `name`,
`description` and `developer_instructions`.

So pstack's two agents work on Claude Code and are absent on Codex, and
`no-comments` degrades there. Closing that gap means a generation step:
`agents/*.md` stays the single source of truth and a script emits TOML for
Codex. Serialise the body as a TOML **literal** string (`'''…'''`), never a
basic string — role text carries backslashes that a basic string reads as
invalid escapes. Parse the result back with `tomllib` before writing it.

Nothing needs this yet. Prefer a skill over a subagent while that is true: a
skill loads identically on both harnesses, and `disable-model-invocation` plus
its `openai.yaml` keeps it from auto-firing.

## Conventions when adding a component

**Skills** — `skills/<name>/SKILL.md` plus optional `references/`, `scripts/`,
`assets/`, and `agents/openai.yaml` when the skill is explicit-invocation only.
Keep `SKILL.md` short and push detail into `references/`, loaded on demand.

**The filter for adding a skill at all:** one discipline, with a runnable check,
in a few hundred words, that says no to things. Reference manuals and grab bags
are rejected — dozens of trivia skills poison description-matching, which
degrades every other skill in the set. This filter is why `review-change`,
`review-design` and `jira-ticket` were dropped rather than carried over:
`interrogate` and `architect` already cover review, and a field-value manual is
a reference, not a discipline.

**Playbooks** — a `rigor` playbook is the right home for a workflow that
routes into existing skills rather than adding a discipline of its own: it adds
its own gates and delegates every engineering step. Register a new one in
`rigor/SKILL.md`'s routing list or nothing reaches it. A playbook that exists
to carry one employer's process does not belong here at all — that was the
`def-ticket` mistake, and its neutral rewrite was dropped for the same reason:
nobody but its author routes into it.

**Subagents** — `agents/<name>.md`, YAML frontmatter with `name` and
`description` only. Never set `tools:`: omitting it is what lets the agent
inherit `Skill` and delegate. Read "Three things that will bite" first.

**Manifest differences to respect:** the Codex manifest rejects a `hooks` field
and requires strict semver. Keep `name`, `version` and `description` identical
across the two files — `validate.sh` checks this.

Keep any component's text harness-neutral so one file serves both: name both
instruction files ("the repo's `CLAUDE.md` / `AGENTS.md`") rather than either
alone, and never blanket-rename `claude`→`codex` in a component — it corrupts
real filesystem paths like `.claude/skills/…`.

## Anatolii's own skills

Five ship. All are tracker-neutral; the three work skills get their
organisation's values from the tracker adapter at runtime:

| Skill | Owns |
|---|---|
| `task-interview` | a manually invoked adaptive interview that clarifies selected work into a local brief, stopping before design review or delivery |
| `setup-tracker` | the tracker adapter — writing it, repairing it, and validating it |
| `pick-next` | what to work on next, under a WIP cap, on the team's work-order ladder |
| `merge-brief` | the pre-merge comprehension check — it explains a change and quizzes the human, and never reviews |
| `weekly-report` | one person's weekly status section, from the tracker and the review forge, linted before publication |

The three work skills depend on a tracker, a review forge and a destination
document being reachable at runtime, and on an adapter existing. That is a
runtime dependency, not a plugin one — the plugin installs and validates
without any of them, and each skill says what is missing when it is.

Their organisation-specific ancestors are gone from this repo and from its
history. Do not re-import them, and do not resolve "the skill used to know
this" by writing the value back into a `SKILL.md`: add an adapter role.

## `.local/` — where temporary files go

**Every temporary file this repo's work produces belongs under `.local/`**, and
the whole tree is gitignored, nested paths included. Spill files, intermediate
results, eval runs, a throwaway script, a scratch draft: `.local/tmp/` for
anything disposable, a named subdirectory for a run worth keeping
(`.local/refine-task-validation/`). Clean out `.local/tmp/` whenever; nothing
depends on it.

Writing a temporary file anywhere else in the tree is the mistake to avoid.
This repo is public, so a scratch file that escapes the ignore is a published
one — and scratch files are exactly where unredacted tracker output, real
ticket keys and pasted document contents accumulate.

`.local/` also holds configuration that is true of this checkout only. It is
not a place for secrets, and not a place for policy every clone needs: durable
shared rules go in `AGENTS.md` or a skill. The tracker adapter is the same
principle pointed the other way — organisation values live outside the repo
entirely, not in an ignored file inside it.

## What this repo used to be

Before 2026-09-07 this was an incremental workbench built one component at a
time: a `main` router over nine deliberately empty playbooks, `task-intake`,
`prior-art` and a `vendor.py` pinning mechanism, with decisions recorded under
`docs/decisions/`. Anatolii replaced it wholesale with decoupled pstack.

That history is not lost: it is in this repo's git log, at tag
`pre-pstack-reset-20260907`, and in
`~/dev/personal/ai-bench.backup-20260907.tar.gz`. Read it before reinventing
something it already rejected — the vendoring rules and the skill-adoption
filter were both learned there. The `vendor.py` pin-and-rematerialise approach
is gone because pstack is now the repo's content rather than a dependency; if a
future component needs vendoring again, that decision record is worth re-reading
first.

## Sibling repos

Sibling checkouts each carry their own `CLAUDE.md`/`AGENTS.md` and should be
read there, not from here. Project-specific skills deliberately stay in their
own repos, where both harnesses already load them from `.agents/skills/` or
`.claude/skills/`. Vendoring them here would create two drifting copies of each
and push the plugin past 120 skills, which is what wrecks
description-matching — and would drag their organisation's details into a
public repo.

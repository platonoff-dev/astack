# astack

[pstack](https://github.com/cursor/plugins/tree/main/pstack) — Cursor's
rigorous agent-workflow stack — **decoupled from Cursor and packaged for
Claude Code and Codex**, plus Anatolii's own work skills. One repo, one plugin,
both harnesses.

49 skills and 2 subagents:

| | |
|---|---|
| **`rigor`** | the router (upstream's `poteto-mode`). 23 playbooks: bug fix, feature, refactoring, perf, shipping, babysit, orchestrate, autopilot, and more |
| **21 `principle-*` skills** | the leaves `rigor` routes into — prove it works, fix root causes, guard the context window, subtract before you add … |
| **`how` · `why`** | code archaeology: how a subsystem works, and why it was decided that way |
| **`architect` · `arena` · `interrogate`** | parallel design panels, model bake-offs, adversarial review |
| **`swarm` · `blast-radius` · `tdd` · `no-comments`** | verification fan-out, change-reach mapping, test-first, comment stripping |
| **`unslop` · `technical-writing` · `teach` · `bro`** | prose discipline |
| **`setup-pstack`** | which model each of the 18 roles runs on, written where *your* harness loads it |
| **`setup-tracker`** | your issue tracker's own names, written to an adapter file **outside** this repo |
| **`task-interview`** | adaptive task interview, one question at a time, ending in a local working brief |
| **`pick-next` · `merge-brief` · `weekly-report`** | Anatolii's: what to work on, the pre-merge comprehension check, the weekly status section — all three read the tracker adapter |

## Install

### Claude Code

```sh
claude plugin marketplace add platonoff-dev/astack
```

```sh
claude plugin install astack@astack
```

Then restart Claude Code and check what loaded:

```sh
claude plugin details astack
```

### Codex

```sh
codex plugin marketplace add platonoff-dev/astack
```

```sh
codex plugin add astack@astack
```

Codex needs a new thread to pick it up. A local path works in place of the slug
in either harness.

### First run, once per harness

```
/setup-pstack
```

pstack delegates to a different model per role, and **no skill in this plugin
names a model** — it names a role and reads the value from a rule you generate.
`setup-pstack` detects your harness and the models it can actually spawn, asks
what each role should use, and writes:

- Claude Code → `~/.claude/rules/pstack-models.md`
- Codex → the Codex home `AGENTS.md` (or `AGENTS.override.md` when present)

Both are loaded into every session of that harness. Skip this and every role
inherits the parent model, which works — you just lose the point of the fan-out.
Configure each harness from inside it; one run does not cover both.

### Second run, once per tracker

```
/setup-tracker
```

`pick-next`, `weekly-report` and `merge-brief` all need the same facts about
your issue tracker: the project key, the custom-field ids,
which of your statuses means *in progress*, which label means *not ready*, your
team's work order. **No skill here names any of them.** They read one adapter
file, and `/setup-tracker` writes it — to
`~/.config/pstack/tracker-adapter.toml`, or to `.agents/tracker-adapter.toml`
in the private repository it describes.

That split is why this repo can be public: the discipline ships here, the
values stay with you. `scripts/validate.sh` fails the build if an
organisation-specific value ever lands in a skill.

## Using it

Most of the stack is explicit-invocation only: 44 of 48 skills will not fire on
their own, by design. Reach for them by name.

```
/rigor                work this task in the full style
/how                  how does this subsystem work
/why                  why was it decided this way
/interrogate          adversarial review before shipping
/pick-next            what should I work on next
/task-interview       clarify this task through an adaptive interview
/weekly-report        my section of the weekly status
```

`rigor` is the front door for real work — it picks the playbook: bug fix,
feature, refactoring, perf, investigation, shipping, and more. The work skills
sit beside it rather than inside it, and read your tracker's own names from the
adapter that `/setup-tracker` writes, so nothing about your tracker lives in
this repo.

`unslop` is the exception that applies always — its own description says so.

Invoke [`task-interview`](skills/task-interview/SKILL.md) manually to work through
a selected task before design or delegation. It reads available evidence and
maintains a local brief of requirements, decisions, and unresolved questions.
It stops at a clear next action or when you
ask to wrap up; it does not start a delivery workflow. Automatic invocation is
disabled in both harnesses. Use `$task-interview` in Codex or `/task-interview`
in Claude Code.

## What was changed from upstream pstack

Upstream targets Cursor. Everything below now runs natively on both harnesses,
and `scripts/validate.sh` has a check for each so it cannot silently come back.

| Upstream | Here |
|---|---|
| `~/.cursor/rules/pstack-models.mdc` | `~/.claude/rules/pstack-models.md`, or the Codex home `AGENTS.md` |
| Model slugs written into skills | **no slugs anywhere** — skills name a role, the rule holds the value |
| `subagent_type: generalPurpose`, `readonly: true`, `environment: "cloud"` | `general-purpose`; a read-only type (`Explore`) where read-only was meant; remote agents described neutrally |
| `control-ui` / `control-cli` from `cursor-team-kit` | the project's own `verify-*` skill, from `create-verification-skill` |
| `deslop` from `cursor-team-kit` | `no-comments` plus the harness's cleanup pass (`/simplify` in Claude Code) |
| Cursor's built-in `create-skill` | `skill-creator`, bundled with both harnesses |
| `~/.cursor/projects/<slug>/agent-transcripts/` | `~/.claude/projects/<slug>/<uuid>.jsonl`, subagents under `<uuid>/subagents/` |
| `make-bot-ui` | **removed** — `api2.cursor.sh` automation webhooks have no equivalent |

`docs/upstream/pstack-README.md` is upstream's own README, kept as a snapshot of
what it ships. `docs/guide/` is pstack's guide, likewise unmodified.

One gap remains: **Codex does not read a plugin's subagents.** pstack's
`comment-sicko` and `rigor-agent` load on Claude Code only, so `no-comments`
degrades on Codex. Closing it needs a TOML generation step; see `AGENTS.md`.

## Validating a change

```sh
./scripts/validate.sh
```

Runs both harnesses' own validators plus the local checks: manifests agree,
every skill has frontmatter, no dangling `/skill` reference, no Cursor
coupling, no model slugs, and the bundled tests.

The Codex validator reports 44 errors by design — Claude Code needs
`disable-model-invocation: true` for explicit-only invocation, and Codex rejects
that field in favour of `agents/openai.yaml`, which this plugin also ships.
`validate.sh` filters exactly that message, counts what it filtered, and fails
if the count stops matching. Every other Codex error still fails the run.

After adding a skill or editing a description:

```sh
python3 scripts/sync_codex_policy.py
```

## The dev loop

**Both harnesses cache the plugin keyed on its version**, at
`~/.claude/plugins/cache/astack/astack/<version>/` and
`~/.codex/plugins/cache/astack/astack/<version>/`. An edit to the working
tree is *not* live, and neither `claude plugin update` nor
`codex plugin marketplace upgrade` picks it up while the version is unchanged.

So bump the version in **both** manifests and reinstall:

```sh
V=<next-version>; sed -i '' "s/\"version\": \".*\"/\"version\": \"$V\"/" .claude-plugin/plugin.json .codex-plugin/plugin.json
```

```sh
claude plugin marketplace update astack && claude plugin update astack
```

Claude Code needs a restart to apply; Codex needs a new thread.

## Layout

```
.claude-plugin/plugin.json        the manifest Claude Code reads
.claude-plugin/marketplace.json   one-entry marketplace pointing at "./"
.codex-plugin/plugin.json         the same plugin, Codex's manifest
.agents/plugins/marketplace.json  the same marketplace, Codex's manifest
skills/<name>/SKILL.md            49 skills; agents/openai.yaml for policy or display metadata
skills/rigor/playbooks/           23 playbooks
skills/setup-tracker/             writes the tracker adapter; adapter-format.md is the spec
agents/                           2 subagents (Claude Code only)
automations/benny/                pstack's issue-triage automation, not plugin-loaded
docs/guide/                       pstack's guide, unmodified
docs/upstream/                    upstream's README, as a snapshot
scripts/validate.sh               everything above
scripts/sync_codex_policy.py      regenerate agents/openai.yaml from frontmatter
AGENTS.md ← CLAUDE.md             repo instructions, one file, symlinked
.local/                           scratch and per-checkout config; gitignored wholesale
```

`automations/benny/` ships with pstack but neither harness loads skills from a
plugin subdirectory, so it is reference material here, exactly as upstream.

## Licence

MIT. pstack is © Lauren Tan and Cursor; `LICENSE` is upstream's, carried with
the copy as MIT requires.

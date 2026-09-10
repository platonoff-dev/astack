# astack

Anatolii's personal skills for Claude Code and Codex. One repository, one
plugin, built one useful component at a time.

## Skills

| Skill | Purpose |
|---|---|
| [task-interview](skills/task-interview/SKILL.md) | Clarify selected work through an adaptive interview, ending in a local brief. |
| [setup-astack](skills/setup-astack/SKILL.md) | Create and refine private service access guides and tracker mappings, including connector corrections. |
| [pick-next](skills/pick-next/SKILL.md) | Recommend the next item from your queue or an epic, accounting for capacity and priorities. |
| [merge-brief](skills/merge-brief/SKILL.md) | Explain a proposed change and check your understanding before you decide whether to merge. |
| [weekly-report](skills/weekly-report/SKILL.md) | Draft your weekly status section from source evidence, with approval before publication. |
| [why](skills/why/SKILL.md) | Investigate code rationale through available history and sources, separating evidence from inference. |
| [how](skills/how/SKILL.md) | Explain runtime flow, subsystem boundaries, and code placement from implementation evidence. |

No bundled router, agent definitions, or automations. Each skill owns its own
workflow and can use the harness's available delegation tools.

## Install

### Claude Code

```sh
claude plugin marketplace add platonoff-dev/astack
claude plugin install astack@astack
```

Restart Claude Code after installation.

### Codex

```sh
codex plugin marketplace add platonoff-dev/astack
codex plugin add astack@astack
```

Start a new task after installation.

## External-system setup

Run `/astack:setup-astack` in Claude Code or `$setup-astack` in Codex. Setup
inspects available tools and project context, tries scoped read-only operations,
and asks about missing conventions. It writes a private index plus operating
guides for the systems your astack workflows need. Providers are unrestricted;
one system may serve several roles, such as tracker, review forge, or report
destination.

Guides describe reusable service access, operations, and gotchas. A document
service configured while preparing a report can also support later document
searches or authorized edits; reporting rules stay with the reporting workflow.

Run setup again to add a service or correct an existing guide. For example:
`$setup-astack The Jira connector misses later comments. Update its guide to
fetch all pages.` Use `/astack:setup-astack` with the same request in Claude Code.
A targeted correction updates the relevant instructions in place, preserving
other systems and avoiding a fresh setup interview.

The default layout is:

```text
~/.config/astack/
  adapter.toml
  systems/
    issues.md
    reviews.md
    documents.md
  tracker-adapter.toml   # optional; existing mappings can also be linked elsewhere
```

Only needed files are created. Astack's skills explicitly load relevant guides;
ordinary harness requests are unaffected. Setup does not install connectors,
configure credentials, or change harness instructions. A successful local
validation does not prove live access; setup reports observed checks and gaps.

The index resolves from `$ASTACK_ADAPTER`, then project
`.agents/astack/adapter.toml` or `.claude/astack/adapter.toml` up to the repository
root, then `~/.config/astack/adapter.toml`. Outside a repository only the current
directory and user default are checked. An invalid selected index or missing
explicit path is an error, with no fallback to a different workspace.

Organisation-specific values and guides stay outside this public plugin. Use a
project bundle only in a verified private repository. See the
[index and guide format](skills/setup-astack/references/adapter-format.md).

### Existing tracker adapters

`setup-astack` also configures and validates field/status mappings. A new index
can link an existing mapping file without moving or rewriting it. Resolution is:

1. `$ASTACK_TRACKER_ADAPTER`, when set.
2. `tracker_adapter` in the selected astack index.
3. If no astack index exists, `.agents/tracker-adapter.toml` or
   `.claude/tracker-adapter.toml` in the
   current project, searched up to its repository root.
4. If no astack index exists, `~/.config/astack/tracker-adapter.toml`.

An index without a tracker link is a partial setup; it does not borrow a legacy
tracker implicitly. An explicit tracker override remains available for a run
against another tracker; verify that any system guides match that workspace.

Only put a project adapter in a private repository. Existing adapters at other
user-level paths can be selected explicitly with `$ASTACK_TRACKER_ADAPTER`.
See the [adapter format](skills/setup-astack/references/tracker-format.md).

`task-interview` is explicitly invoked: `$task-interview` in Codex or
`/astack:task-interview` in Claude Code. It ends with a brief and a next action;
it does not launch delivery.

## Vendoring skills

Import individual skills from different Git repositories, keep exact commit
pins, check for upstream changes, and update selected skills or all of them:

```sh
python3 -B scripts/vendor.py add --name example-skill \
  --repo https://github.com/example/skill-library.git \
  --path skills/example-skill --ref main --license MIT
python3 -B scripts/vendor.py check
python3 -B scripts/vendor.py update example-skill
```

The URL above is an invented example; replace it with the repository and skill
you choose. `check` reports local edits and changes to the skill or its license,
ignoring unrelated upstream commits. `update` without names updates all
registered skills. `sync` reproduces the pinned versions. Updates preserve
repeatable compatibility patches and refuse to discard local edits by default.

`why` and `how` are vendored from Cursor's pstack with their MIT license, exact
commit pins, and compatibility patches. Both are self-contained and explicitly
invoked: `$why` / `$how` in Codex or `/astack:why` / `/astack:how` in Claude Code.
They pass no model or reasoning-effort overrides, use available host tools, and
can run in the parent when delegation is unavailable. `why` adapts to the sources
you can access; no particular forge, connector, or warehouse schema is required.
See [vendoring details](docs/vendoring.md) for licenses, patches, exit codes,
and the validation and reinstall steps.

## Development

```sh
python3 scripts/sync_codex_policy.py
scripts/validate.sh
```

Validation checks the manifests, skill structure and references, invocation
policies, public-repository content rules, and bundled helpers. Harness
validators run when their tools are available; skipped checks are reported.

Keep the version, name, and description aligned in both plugin manifests.
Reinstall from the source you changed to refresh a cached plugin, then restart
Claude Code or start a new Codex task. The GitHub install commands above use
the published repository, so local changes must reach that source first.

Read [AGENTS.md](AGENTS.md) before contributing. Temporary work belongs in the
ignored `.local/` directory.

## License

Original astack code is MIT. See [LICENSE](LICENSE). Imported skills retain
their upstream licenses, recorded in `vendor.json` and copied with each skill.

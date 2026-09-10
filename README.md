# astack

Anatolii's personal skills for Claude Code and Codex. One repository, one
plugin, built one useful component at a time.

## Skills

| Skill | Purpose |
|---|---|
| [task-interview](skills/task-interview/SKILL.md) | Clarify selected work through an adaptive interview, ending in a local brief. |
| [setup-astack](skills/setup-astack/SKILL.md) | Discover external systems and configure private access guides for astack skills. |
| [setup-tracker](skills/setup-tracker/SKILL.md) | Configure and validate the private tracker adapter used by the work skills. |
| [pick-next](skills/pick-next/SKILL.md) | Recommend the next item from your queue or an epic, accounting for capacity and priorities. |
| [merge-brief](skills/merge-brief/SKILL.md) | Explain a proposed change and check your understanding before you decide whether to merge. |
| [weekly-report](skills/weekly-report/SKILL.md) | Draft your weekly status section from source evidence, with approval before publication. |

No bundled router, agents, or automations. Each skill owns its own workflow.

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

`setup-tracker` still configures and validates field/status mappings. A new index
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
See the [adapter format](skills/setup-tracker/references/adapter-format.md).

`task-interview` is explicitly invoked: `$task-interview` in Codex or
`/astack:task-interview` in Claude Code. It ends with a brief and a next action;
it does not launch delivery.

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

MIT. See [LICENSE](LICENSE).

# astack

Anatolii's personal skills for Claude Code and Codex. One repository, one
plugin, built one useful component at a time.

## Skills

| Skill | Purpose |
|---|---|
| [task-interview](skills/task-interview/SKILL.md) | Clarify selected work through an adaptive interview, ending in a local brief. |
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

## Tracker configuration

Use `setup-tracker` to configure the work skills. Organisation-specific values
stay outside this public plugin. The adapter resolves from:

1. `$ASTACK_TRACKER_ADAPTER`, when set.
2. `.agents/tracker-adapter.toml` or `.claude/tracker-adapter.toml` in the
   current project, searched up to its repository root.
3. `~/.config/astack/tracker-adapter.toml`.

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

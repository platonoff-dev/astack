# ai-bench

My agentic-AI workbench — subagents, skills and tool configs — packaged as a
plugin that both **Claude Code** and **Codex** install from the same repo.

**It is empty on purpose.** The scaffolding is done; components get added one at
a time.

```
.claude-plugin/
├── plugin.json           the plugin manifest Claude Code reads
└── marketplace.json      a one-entry marketplace pointing at this repo ("./")
.codex-plugin/plugin.json the same plugin, Codex's manifest
.agents/plugins/marketplace.json   the same marketplace, Codex's manifest
AGENTS.md ← CLAUDE.md     repo instructions, one file, symlinked
```

The repo is both the marketplace and its single plugin. Adding a component means
creating the directory the harnesses already look for — nothing to register:

| Put it here | Loaded by |
|---|---|
| `agents/<name>.md` | Claude Code (Codex needs a generation step — see AGENTS.md) |
| `skills/<name>/SKILL.md` | both |
| `commands/<name>.md` | Claude Code |
| `hooks/hooks.json` | Claude Code (`hooks` is rejected in the Codex manifest) |
| `.mcp.json` | both |

## Install

### Claude Code

```sh
claude plugin marketplace add platonoff-dev/ai-bench    # or a local path
claude plugin install ai-bench@ai-bench
claude plugin details ai-bench                          # what it actually loaded
```

### Codex

```sh
codex plugin marketplace add platonoff-dev/ai-bench     # or a local path
codex plugin add ai-bench@ai-bench
codex plugin list
```

Both are installed and enabled right now from the local path
`~/dev/personal/ai-bench`, reporting 0 components.

## The dev loop

**Both harnesses cache a copy of the plugin keyed on its version**, at
`~/.claude/plugins/cache/ai-bench/ai-bench/<version>/` and
`~/.codex/plugins/cache/ai-bench/ai-bench/<version>/`. An edit to the working
tree is *not* live, and neither `claude plugin update` nor
`codex plugin marketplace upgrade` picks it up while the version is unchanged.

So after adding or editing a component, bump the version in **both** manifests
and reinstall:

```sh
V=0.2.0
sed -i '' "s/\"version\": \".*\"/\"version\": \"$V\"/" \
  .claude-plugin/plugin.json .codex-plugin/plugin.json

claude plugin marketplace update ai-bench && claude plugin update ai-bench
codex plugin add ai-bench@ai-bench
```

Claude Code needs a restart to apply; Codex needs a new thread. Codex's own
convention for a throwaway iteration is a build-metadata cachebuster —
`0.1.0+codex.local-20260831-140000` — rather than burning version numbers.

## Validating a change

```sh
claude plugin validate .                     # both Claude manifests
uvx --with pyyaml python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

The Codex validator is stricter than the Codex runtime: it demands a fully
populated `interface` block (`displayName`, `longDescription`, `capabilities`,
`defaultPrompt`, …) that the runtime happily installs without. The manifest here
omits `interface` rather than inventing UI copy for an empty plugin, so that
validator currently fails on that one field. Fill the block in when the plugin
has enough in it to describe.

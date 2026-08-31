# ai-bench

My agentic-AI workbench — subagents, skills and tool configs — packaged as a
plugin that both **Claude Code** and **Codex** install from the same repo.

The scaffolding is done; components get added one at a time. One vendored skill
so far — see [Vendoring someone else's skill](#vendoring-someone-elses-skill).

```
.claude-plugin/
├── plugin.json           the plugin manifest Claude Code reads
└── marketplace.json      a one-entry marketplace pointing at this repo ("./")
.codex-plugin/plugin.json the same plugin, Codex's manifest
.agents/plugins/marketplace.json   the same marketplace, Codex's manifest
skills/unslop/            vendored from cursor/plugins (MIT)
vendor.json               the pin for every vendored component
scripts/vendor.py         sync / check / update / add
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
`~/dev/personal/ai-bench`, reporting 1 skill.

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

## Vendoring someone else's skill

Third-party skills are **committed into this repo**, not linked. Both harnesses
install a plugin by copying the repo tree and neither initialises git
submodules, so a submodule or subtree would arrive empty on someone else's
`plugin install`. Reproducibility comes from `vendor.json` instead — repo,
subdirectory, branch, and the exact commit the working copy came from.

| Command | What it does |
|---|---|
| `scripts/vendor.py add --name N --repo URL --path DIR [--ref main] [--license MIT] [--license-path P]` | register an upstream skill and fetch it |
| `scripts/vendor.py sync [name…]` | re-materialise from the pinned commits (idempotent) |
| `scripts/vendor.py check [name…]` | local edits? upstream moved? exit 1 if either |
| `scripts/vendor.py update [name…]` | move the pin to the branch head and rewrite |

Fetching is a sparse, blob-filtered, depth-1 fetch of just the one subdirectory
at the pinned SHA — plain git, so any host works, and ~250 KB rather than a
full clone.

**Never hand-edit a vendored directory.** `sync` and `update` replace it
wholesale, so an edit is silently lost on the next run; `check` reports it as
`EDITED`. If you want different behaviour, add your own skill alongside it
rather than patching the copy — that keeps `check` meaningful.

`check` distinguishes the two ways a pin goes wrong:

```
ok       unslop: matches pin, and pin is main head
EDITED   unslop: differs from its pinned commit fd878692de15
STALE    unslop: main moved to fd878692de15 and the content changed
```

It also stays quiet when the branch has moved but the vendored path itself
hasn't, which is the common case in a busy monorepo.

### Vendored now

| Skill | Upstream | Licence |
|---|---|---|
| `unslop` — cut AI tells from writing | [cursor/plugins `pstack/skills/unslop`](https://github.com/cursor/plugins/tree/main/pstack/skills/unslop) | MIT, © Lauren Tan |

The upstream `LICENSE` is copied in beside each vendored `SKILL.md`; MIT
requires the notice to travel with the copy.

Note `unslop`'s own description ends "Must always apply." — it is written to
match nearly every writing task, so expect it to fire often. Left as upstream
wrote it.

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

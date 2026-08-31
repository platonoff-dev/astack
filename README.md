# ai-bench

My agentic-AI workbench — subagents, skills and tool configs — packaged as a
plugin that both **Claude Code** and **Codex** install from the same repo.

Two skills ship in the plugin: `task-intake`, written here, and `unslop`,
vendored from `cursor/plugins`. Components get added one at a time.

```
.claude-plugin/
├── plugin.json           the plugin manifest Claude Code reads
└── marketplace.json      a one-entry marketplace pointing at this repo ("./")
.codex-plugin/plugin.json the same plugin, Codex's manifest
.agents/plugins/marketplace.json   the same marketplace, Codex's manifest
skills/unslop/            vendored from cursor/plugins (MIT)
skills/task-intake/       evidence checks, Markdown briefs, tracker contract
vendor.json               the pin for every vendored component
scripts/vendor.py         sync / check / update / add
.agents/skills/prior-art/ repo-level skill, not shipped in the plugin
prior-art.json            setups tracked for reading, plus proposed candidates
scripts/prior_art.py      list / pull / diff / seen / approve / add
docs/decisions/           what was adopted, rejected or deferred, and why
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

After installing version 0.3.0, both should expose `task-intake` and `unslop`.
Use the list/details commands above to check the installed version.

## The dev loop

**Both harnesses cache a copy of the plugin keyed on its version**, at
`~/.claude/plugins/cache/ai-bench/ai-bench/<version>/` and
`~/.codex/plugins/cache/ai-bench/ai-bench/<version>/`. An edit to the working
tree is *not* live, and neither `claude plugin update` nor
`codex plugin marketplace upgrade` picks it up while the version is unchanged.

So after adding or editing a component, bump the version in **both** manifests
and reinstall:

```sh
V=0.3.0
sed -i '' "s/\"version\": \".*\"/\"version\": \"$V\"/" \
  .claude-plugin/plugin.json .codex-plugin/plugin.json

claude plugin marketplace update ai-bench && claude plugin update ai-bench
codex plugin add ai-bench@ai-bench
```

Claude Code needs a restart to apply; Codex needs a new thread. Codex's own
convention for a throwaway iteration is a build-metadata cachebuster —
`0.1.0+codex.local-20260831-140000` — rather than burning version numbers.

## Task intake

Use [task-intake](skills/task-intake/SKILL.md) to check an incoming or resumed
ticket before planning implementation. For example: "Use task-intake to assess
PROJ-123 against this repository." A pasted task or local file works too.

It inspects consequential claims, separates evidence from proposed solutions,
and writes a compact Markdown brief with one next action: implement, investigate,
decide, split, or no-change. Human blockers remain explicit. Intake does not
change product code or silently update a tracker.

The [brief format](skills/task-intake/references/brief.md) targets 250-400 words
with no minimum and a warning above 600. The checker validates structure, not
truth. The [tracker contract](skills/task-intake/references/tracker.md) maps reads,
search, and authorized brief publication to the project's existing tools. No
Jira account, new service, or tracker installation is required.

The adoption and first trial are recorded in
[decision 002](docs/decisions/002-task-intake.md).

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

## Deciding what to steal

Both harnesses also read skills straight from the working tree, no plugin
involved: `.agents/skills/<name>/` with a symlink at `.claude/skills/<name>`.
Those serve this repo only, ship to nobody, and need no version bump.

The first one, `prior-art`, exists because copying someone's setup wholesale is
how you end up with forty skills you can't debug. It reads other people's setups
at a known commit and ends in a decision record.

| Command | What it does |
|---|---|
| `scripts/prior_art.py list` | tracked sources, when each was last read, and the candidates awaiting approval |
| `scripts/prior_art.py pull [name…]` | fetch head into `.cache/prior-art/` (gitignored, ~6 s for both) |
| `scripts/prior_art.py diff [name…]` | what changed upstream since a decision cited it (exit 1 if anything did) |
| `scripts/prior_art.py seen <name>` | record the cached commit as read |
| `scripts/prior_art.py approve <name>` | promote a proposed candidate to a tracked source |

A source is either a git repo, pinned by commit, or a locally installed
directory such as a harness's own bundled skills, pinned by content digest plus
the tool's version — so `diff` can tell you a Codex upgrade rewrote them under
you.

Tracked now: [`pstack`](https://github.com/cursor/plugins/tree/main/pstack),
[`mattpocock/skills`](https://github.com/mattpocock/skills),
[`anthropics/skills`](https://github.com/anthropics/skills) and Codex's own
`~/.codex/skills/.system`. Four more sit in `prior-art.json` as candidates,
unfetched until approved.

Same fetch machinery as vendoring, opposite purpose: `vendor.py` copies a
component in to **use** it, `prior_art.py` copies one in to **read** it. The
reading copies are never committed.

## Validating a change

```sh
uvx --with pyyaml python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
claude plugin validate .                     # marketplace manifest
claude plugin validate .claude-plugin/plugin.json
uvx --with pyyaml python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-intake
python3 -B skills/task-intake/scripts/test_check_brief.py
# To check an actual brief:
python3 skills/task-intake/scripts/check_brief.py /path/to/brief.md
```

The Codex manifest includes the required display metadata for the two shipped
skills. The brief checker and its regression checks use only Python's standard
library. These checks do not verify tracker access or the truth of an intake
brief's evidence.

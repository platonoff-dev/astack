# ai-bench

My agentic-AI workbench — subagents, skills and tool configs — packaged as a
plugin that both **Claude Code** and **Codex** install from the same repo.

Five skills ship in the plugin: `main`, `task-intake` and `setup-pstack`,
written here, plus `unslop` and `thermo-nuclear-code-quality-review`, vendored
from `cursor/plugins`. Components get added one at a time.

```
.claude-plugin/
├── plugin.json           the plugin manifest Claude Code reads
└── marketplace.json      a one-entry marketplace pointing at this repo ("./")
.codex-plugin/plugin.json the same plugin, Codex's manifest
.agents/plugins/marketplace.json   the same marketplace, Codex's manifest
skills/unslop/            vendored from cursor/plugins (MIT)
skills/task-intake/       evidence checks, Markdown briefs, tracker contract
skills/main/              main work entrypoint and playbook router
skills/setup-pstack/      per-role pstack model rule for Claude Code and Codex
skills/thermo-nuclear-code-quality-review/  strict maintainability review (MIT)
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

Version 0.9.0 adds `setup-pstack`, which writes pstack's per-role model rule
where Claude Code or Codex loads it. `main` remains the generic work entrypoint
and all nine route files remain empty until each receives its own research,
decision, and trial. Use the list/details commands above to check the installed version. See
the [review skill notes](#strict-code-quality-review) for its invocation setting
and the Codex validator limitation.

## The dev loop

**Both harnesses cache a copy of the plugin keyed on its version**, at
`~/.claude/plugins/cache/ai-bench/ai-bench/<version>/` and
`~/.codex/plugins/cache/ai-bench/ai-bench/<version>/`. An edit to the working
tree is *not* live, and neither `claude plugin update` nor
`codex plugin marketplace upgrade` picks it up while the version is unchanged.

So after adding or editing a component, bump the version in **both** manifests
and reinstall:

```sh
V=0.9.0
sed -i '' "s/\"version\": \".*\"/\"version\": \"$V\"/" \
  .claude-plugin/plugin.json .codex-plugin/plugin.json

claude plugin marketplace update ai-bench && claude plugin update ai-bench
codex plugin add ai-bench@ai-bench
```

Claude Code needs a restart to apply; Codex needs a new thread. Codex's own
convention for a throwaway iteration is a build-metadata cachebuster —
`0.1.0+codex.local-20260831-140000` — rather than burning version numbers.

## Local project configuration

`.local/` holds configuration for one checkout and is gitignored. This repo's
`.local/tracker.md` records how to work with its tracker. The file is not
committed or included in a published plugin source, so another clone, worktree,
or VM does not inherit it.

`task-intake` uses the same convention in any target repository: read
`.local/tracker.md` first when it exists, then fall back to committed repository
instructions. The file maps operations to available tools. It must not contain
credentials, and its presence does not prove authentication or authorize a
tracker write. Rules that every checkout needs still belong in `AGENTS.md` or a
committed skill.

The adaptation from Matt Pocock's committed tracker document is recorded in
[decision 007](docs/decisions/007-local-tracker-adapter.md).

## Task intake

Use [task-intake](skills/task-intake/SKILL.md) to check an incoming or resumed
ticket before choosing how to work it. For example: "Use task-intake to assess
PROJ-123 against this repository." A pasted task or local file works too.

It inspects consequential claims, separates evidence from proposed solutions,
and writes a compact Markdown brief with one selected playbook and optional
proof modifiers. Investigation, change work, decisions, splitting, and verified
no-change are direct routes. Human blockers remain explicit. Intake does not
change product code or silently update a tracker.

The [brief format](skills/task-intake/references/brief.md) targets 250-400 words
with no minimum and a warning above 600. The checker validates structure, not
truth. The [tracker contract](skills/task-intake/references/tracker.md) reads an
optional `.local/tracker.md` and maps reads, search, and authorized brief
publication to the project's existing tools. No Jira account, new service, or
tracker installation is required.

The adoption and first trial are recorded in
[decision 002](docs/decisions/002-task-intake.md).

## Main

Use [main](skills/main/SKILL.md) as the generic entrypoint for new or resumed
work. It uses a current evidence-backed brief when one exists and runs
`task-intake` first when the request is new, stale, or unclear. An intake-only
request still ends with the brief. Otherwise `main` continues through the
selected playbook.

`main` is currently a router skeleton, not an adopted task procedure.

The router reserves one file for `investigation`, `bug-fix`, `feature`,
`refactor`, `performance`, `migration`, `decision`, `split`, or `no-change`.
All nine files are empty in 0.9.0. An empty file adds no instructions; the skill
must say that no ai-bench playbook was applied. Ordinary work can still proceed
under the user's request and target repository instructions.

Each playbook will receive its own prior-art review, decision, instructions, and
behavioral trial. The route checker keeps an explicit adopted set, currently
empty, and fails if a placeholder gains content without being adopted.
[Decision 005](docs/decisions/005-empty-playbook-skeleton.md) supersedes the
provisional bodies adopted in
[decision 004](docs/decisions/004-task-work-playbooks.md). The generic entrypoint
name and intake handoff are recorded in
[decision 006](docs/decisions/006-main-entrypoint.md).

## Pstack model setup

Use [setup-pstack](skills/setup-pstack/SKILL.md) inside Claude Code or Codex to
choose the model each pstack role runs on. It writes a managed block, one line
per role, to the file that harness loads into every session: for Claude Code
`~/.claude/rules/pstack-models.md`, for Codex the home `AGENTS.md` (or
`AGENTS.override.md` when that exists). Bytes outside the block are preserved.
Nothing is written under `~/.cursor/`, and the other harness's file is left
alone: configure each harness from inside it.

Values are what that harness can actually spawn. On Claude Code that is one of
the Agent tool's model aliases (`sonnet`, `opus`, `haiku`, `fable`). On Codex it
is a model slug, optionally `slug@effort`, checked against Codex's own models
cache when present. `inherit-parent` and `auto` mean "no override". A panel role
lists one entry per subagent to spawn. The bundled `pstack_models.py` detects
the harness and its models, shows the current mapping, validates, and writes;
the skill asks before writing. Account entitlement still has to come from the
running harness.

The role labels are pstack's, so its skills can read the rule from context; the
block says it stands in for the Cursor rule those skills name. No other shipped
skill consumes the rule yet. Each later pstack-derived consumer needs its own
decision and adaptation to read it. See
[decision 008](docs/decisions/008-setup-pstack.md) for why this is a skill
written here rather than a vendored copy. The format is documented in
[the rule format reference](skills/setup-pstack/references/rule-format.md).

## Strict code quality review

Use [thermo-nuclear-code-quality-review](skills/thermo-nuclear-code-quality-review/SKILL.md)
for a demanding review of code structure, branching, abstractions, and module
boundaries. Name the comparison base and whether you want findings or edits. For
example: "Use thermo-nuclear-code-quality-review to review this branch against
main. Report findings only."

The upstream skill declares `disable-model-invocation: true`, so it is intended
for explicit invocation. Its 1,922 words and lack of a runnable quality check
exceed this repo's usual adoption filter. It is vendored unchanged at Anatolii's
request, with the limitations recorded in
[decision 003](docs/decisions/003-thermo-nuclear-code-quality-review.md).
The companion Cursor subagent and the rest of Team Kit are not included.

The bundled Codex plugin validator rejects this upstream invocation setting:
``frontmatter field `disable-model-invocation` must be false``.
Codex CLI 0.146.0 nevertheless discovers the unchanged skill as enabled through
its local `plugin/read` API. Discovery does not prove that Codex enforces the
upstream invocation restriction. Its [documented invocation policy](https://learn.chatgpt.com/docs/build-skills#optional-metadata)
uses `agents/openai.yaml`, which this upstream skill does not supply.
Keep the validation failure visible and invoke the skill explicitly. Any
compatibility adaptation needs a separate decision under the vendoring rules.

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
rather than patching the copy — that keeps `check` meaningful. `setup-pstack`
is the worked example: its upstream is Cursor-only, so the adaptation is a skill
written here that borrows the role labels, not a patched copy.

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
| `thermo-nuclear-code-quality-review`, strict maintainability review | [cursor/plugins `cursor-team-kit/skills/thermo-nuclear-code-quality-review`](https://github.com/cursor/plugins/tree/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review) | MIT, © 2026 Cursor |

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
python3 -B scripts/vendor.py check
uvx --with pyyaml python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-intake
uvx --with pyyaml python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/main
uvx --with pyyaml python \
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/setup-pstack
python3 -B skills/task-intake/scripts/test_check_brief.py
python3 -B skills/main/scripts/check_playbooks.py
python3 -B skills/setup-pstack/scripts/test_pstack_models.py
# To check an actual brief:
python3 skills/task-intake/scripts/check_brief.py /path/to/brief.md
```

The Codex manifest includes display metadata for all five shipped skills. Its
bundled validator currently fails on the review skill's upstream invocation
setting, as described above. The brief, playbook-route, and pstack model rule
checks use only Python's standard library. These checks do not verify
classification quality, review quality, tracker access, model entitlement, or
the truth of an intake brief's evidence.

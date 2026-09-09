# The pstack model rule

One managed block per harness, placed where that harness loads it into every
session. Nothing else reads it, and neither harness needs a reinstall for it.

| Harness | File | Ownership |
|---|---|---|
| Claude Code | `~/.claude/rules/pstack-models.md` | whole file is the block |
| Codex | `$CODEX_HOME/AGENTS.override.md` if it exists, else `AGENTS.md` (home defaults to `~/.codex`) | block inside a file the user also edits |

Claude Code loads every `~/.claude/rules/*.md` without a `paths:` frontmatter at
session start. Codex loads its home `AGENTS.md`, or `AGENTS.override.md` when
that exists, ahead of any project file. `scripts/pstack_models.py` writes and
replaces only the text between `<!-- pstack-models:begin -->` and
`<!-- pstack-models:end -->`; bytes outside the markers are preserved.

## Lines

```
<!-- pstack-models:begin -->
# pstack model configuration (Claude Code)
… header prose written by the script …

feature, refactoring: sonnet
bug-fix: opus
…
how critics: fable, opus, sonnet
…
<!-- pstack-models:end -->
```

Every one of the eighteen roles must have a line. Upstream lets a missing line
fall back to a model slug written into the skill body, and those slugs were
Cursor's. The adapted skills here name no slugs at all — they describe the
shape of the choice instead ("four runners, spread across model families") and
defer the value to this block. A complete block is therefore the only place a
real model name lives, which is why a missing role is an error here rather
than a silent fallback.

The roles, in the order the script writes them:

`feature, refactoring` · `bug-fix` · `perf-issue` · `hillclimb` ·
`judgment and prose` · `hardest tasks` · `how explorer` · `how explainer` ·
`how critics` · `why investigators` · `why synthesizer` · `reflect tooling` ·
`reflect judgment, divergent, synthesizer` · `arena runners` ·
`arena cross-judge pool` · `swarm workers` · `architect runners` ·
`interrogate reviewers`

Panels take a comma-separated list and spawn one subagent per entry, alias
entries included: `how critics`, `arena runners`, `arena cross-judge pool`,
`architect runners`, `interrogate reviewers`. Every other role takes exactly one
value. Repeating an entry in a panel is valid and means "run this model twice".

## Values

- `inherit-parent` or `auto`: spawn with no model and no effort override; the
  subagent inherits the parent session's settings. Never a model name.
- Claude Code: one of the aliases the Agent tool's `model` parameter accepts
  per call, currently `sonnet`, `opus`, `haiku`, `fable`. No `@effort` suffix:
  the tool has no per-call effort, and a per-role effort would have to live in
  an agent definition's `effort:` field instead. Full model IDs are rejected
  for the same reason.
- Codex: a model slug, optionally `slug@effort`. Effort is one of `minimal`,
  `low`, `medium`, `high`, `xhigh`, `max`, `ultra`. When
  `$CODEX_HOME/models_cache.json` exists the script also requires the slug to be
  listed there and the effort to be one that model offers. A consumer passes
  the pair as the subagent's `model` and `reasoning_effort`, or as `model` and
  `model_reasoning_effort` in a custom agent's TOML.

## Consumer contract

A pstack-derived skill adapted for this plugin must:

1. read the role lines from the block in its own harness's file, which is
   already in context because the harness loaded it;
2. read a Cursor-path reference (`~/.cursor/rules/…`) as pointing at this
   block — no shipped skill still carries one, but a re-import from upstream
   will reintroduce them, so treat one as a decoupling miss and fix it;
3. pass values through untranslated, omitting both overrides for the aliases;
4. spawn one subagent per configured panel entry;
5. stop with a message naming `setup-pstack` when a configured value is
   rejected by the harness, instead of substituting a nearby model.

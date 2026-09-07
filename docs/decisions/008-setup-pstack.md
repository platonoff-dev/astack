# 008 — Should pstack's model setup be adapted for Claude Code and Codex?

- **Date:** 2026-09-03, revised 2026-09-07
- **Verdict:** adapt as a skill written here; reject vendoring
- **Touches:** `skills/setup-pstack/`, plugin manifests, README, `AGENTS.md`

## Failure it prevents

pstack's `setup-pstack` writes `~/.cursor/rules/pstack-models.mdc`, an
always-applied Cursor rule, and its other skills read the model per role from
that path. Run inside Claude Code, where pstack is installed as a skills-dir
plugin, the same skill still writes the Cursor path. That is what happened on
this machine: `~/.cursor/rules/pstack-models.mdc` holds Claude aliases
(`sonnet`, `opus`, `fable`) that Claude Code never loads. Setup looked
successful and changed nothing.

## Sources read

- pstack @ `7314f723a487` — `skills/setup-pstack/SKILL.md`,
  `skills/poteto-mode/SKILL.md`, `skills/arena/SKILL.md`,
  `skills/swarm/SKILL.md`, `skills/interrogate/SKILL.md`,
  `docs/guide/01-setup.md`, `docs/guide/10-recipes-and-pitfalls.md`
- Claude Code 2.1.263 docs, read 2026-09-07: memory (user-level
  `~/.claude/rules/*.md` load at session start when they carry no `paths:`),
  sub-agents (`model:` and `effort:` frontmatter; per-call `model` on the Agent
  tool), model-config (effort levels `low`…`max`; aliases)
- Codex 0.153.2 docs, read 2026-09-07: AGENTS.md discovery (home
  `AGENTS.override.md` else `AGENTS.md`, ahead of project files), subagents
  (custom agents in `$CODEX_HOME/agents/*.toml` with `model` and
  `model_reasoning_effort`; spawn values override `[agents]` defaults), config
  reference; plus `~/.codex/models_cache.json` on this machine, which lists each
  slug's supported efforts

Not read: the other pstack skills' bodies, its agents or automation pack.

## Mechanism

Upstream: detect models the `Task` tool accepts, confirm a role mapping, write
one idempotent rule file, and rely on the rule being in every session's context.
Eighteen role labels; five are panels whose list length sets fan-out;
`inherit-parent` and `auto` mean "omit the model".

Both target harnesses have the same primitive under a different path. Claude
Code loads every `~/.claude/rules/*.md` unconditionally; Codex loads its home
`AGENTS.md`. The adaptation keeps upstream's line format and role labels inside
a marker-delimited block written to whichever of those the running harness
uses, so the installed pstack skills can read it from context, and the block
says it stands in for the Cursor rule they name.

Values are per harness. Claude Code's Agent tool takes `sonnet`, `opus`,
`haiku`, `fable` and no per-call effort, so Claude values are those aliases
only. Codex subagents take a model slug and a reasoning effort, so Codex values
are `slug` or `slug@effort`, checked against the models cache when it exists.
A standard-library script does detection, show, check and write; it never
touches bytes outside its block.

## Why not vendor

The first attempt vendored upstream at the pin and applied a committed patch.
The patch replaced every line of `SKILL.md` and added three new files, which
made the upstream link decorative: `vendor.py update` could only ever break the
patch, and nothing upstream survived except the name and licence notice. The
committed rule in `AGENTS.md`, that different behaviour means your own skill
rather than a patched copy, was right, and the exception added for this case is
withdrawn. Role labels are borrowed and credited; the skill text, script and
reference are written here, so no upstream licence file is carried.

The first attempt also wrote a neutral TOML under `~/.config/ai-bench/`. No
harness loads that, so every consumer would have had to be adapted before any
of the configuration took effect. Writing where the harness already reads
removes that step.

## Verdict

Ship `skills/setup-pstack` as a skill written here. Fourteen regression tests
cover value rules per harness, panel fan-out, missing roles, block replacement
inside a shared file, stray lines, harness detection and the Codex override
file. A trial write for each harness into a temporary path passed the checker;
no file under the user's home was written during the trial.

No other shipped skill consumes the rule yet. A pstack-derived consumer needs
its own decision and must read the rule from its harness's block, pass values
through untranslated, and stop rather than substitute when the harness rejects
one.

## What would reverse this

Revisit if either harness gains a plugin-level per-role model mapping, if
Claude Code's Agent tool grows a per-call effort (then Claude values can carry
`@effort`), if the Codex override-file rule or Claude rules directory changes,
or if upstream pstack drops the rule-in-context design.

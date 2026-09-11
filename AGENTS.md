# AGENTS.md

Repo instructions for Claude Code and Codex. `CLAUDE.md` is a symlink to this
file so both harnesses read the same instructions.

## Purpose

astack is Anatolii's personal collection of skills for Claude Code and Codex.
Build it one useful component at a time, from actual work. Keep each skill
focused and self-contained; add shared infrastructure only when a current
workflow needs it.

The repo is both a plugin and its marketplace. `.claude-plugin/` and
`.codex-plugin/` contain the plugin manifests; `.claude-plugin/marketplace.json`
and `.agents/plugins/marketplace.json` point to this repo with source `./`.

Seven skills ship: `task-interview`, `setup-astack`, `pick-next`, `merge-brief`,
`weekly-report`, `why`, and `how`. There are no bundled agent definitions or
automations; skills may delegate through the harness when available.

## Public repository

This repository is public. Never commit organisation-specific names, internal
hosts, real tracker keys, account identifiers, private quotations, credentials,
or unpublished work details. Use invented examples.

System access instructions and configuration belong in a private adapter outside
this plugin. `setup-astack` owns the index (`~/.config/astack/adapter.toml` by
default) and its linked Markdown guides. Only astack skills load these guides;
do not inject them into general harness instructions or install them as skills.

Tracker values remain in the mapping file outside this plugin:
`~/.config/astack/tracker-adapter.toml`, or the private repository it describes.
The system index can link this file. `setup-astack` owns its format and
validation. Extend adapter roles when a
skill needs another tracker fact; do not hardcode the value in the skill.

Keep project-specific skills in their own repositories. Read a sibling repo's
own `CLAUDE.md` / `AGENTS.md` before working there.

## Changes and validation

- Run `scripts/validate.sh` before every commit.
- Bump the version in both plugin manifests for every change. Keep their
  `name`, `version`, and `description` identical; use a numeric `MAJOR.MINOR.PATCH`
  version. The Codex manifest must not contain `hooks`.
- Put shipped skills in `skills/<kebab-case-name>/SKILL.md`. Repository-only
  development skills live in `.claude/skills/<kebab-case-name>/SKILL.md`, with
  matching directory symlinks under `.agents/skills/` for Codex discovery.
  The frontmatter `name` must match the directory. Keep supporting detail in
  linked references.
- Write instructions for both harnesses. Refer to the repo's `CLAUDE.md` /
  `AGENTS.md`; do not require another plugin's commands.
- Preserve each skill's invocation policy. For explicit-only skills, keep
  `disable-model-invocation: true` and the matching
  `agents/openai.yaml` with `policy.allow_implicit_invocation: false`.
- After adding a skill or changing a description, run
  `scripts/sync_codex_policy.py`; `--check` reports drift without writing.
  The validator filters only Codex's rejection of that Claude Code frontmatter
  field, checking the count against the skills that declare it. Other errors fail.
- Local edits require reinstalling the plugin to reach a harness's cached
  copy. A source change alone does not prove an installed plugin was updated.

## Temporary files

Every temporary file produced while working here belongs under `.local/`, which
is ignored recursively. Use `.local/tmp/` for disposable files and a named
subdirectory for a run worth retaining. Never track anything under `.local/`.
Keep private tracker adapters outside this plugin, including its ignored tree.

## Vendoring

Use `python3 -B scripts/vendor.py` to import third-party skills. `vendor.json`
records each source repository, skill path, tracked ref, exact commit, license,
and ordered compatibility patches. See [docs/vendoring.md](docs/vendoring.md)
for `add`, `check`, `update`, and `sync` usage.

Use `check` to inspect upstream changes; update only the requested skills.
Do not hand-edit registered skill directories. Keep adaptations in
`vendor/patches/<name>.patch`, then reproduce with `sync`; preserve upstream
licenses and invocation policies. `--force` explicitly discards local edits,
so save any wanted changes as a patch first. Review imported instructions and
their dependencies before use; copying a skill does not authorize running it.

After a vendor change, run the policy sync and validator and bump both plugin
versions. Do not import related skills or agents unless requested. Vendoring
changes this source tree; it does not refresh installed plugin caches.

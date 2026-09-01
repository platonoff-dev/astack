# 007: Put tracker instructions in `.local/tracker.md`

- **Date:** 2026-09-01
- **Verdict:** adopt with adaptation
- **Touches:** `.gitignore`, `AGENTS.md`, `skills/task-intake/`, both plugin
  manifests, README; the checkout-local adapter is deliberately uncommitted

## Failure it prevents

Task intake had a provider-neutral tracker contract but no deterministic local
place for this repository's provider, project, commands, and authorization
boundary. An agent had to rediscover them or guess from the Git remote. Putting
personal access assumptions in a committed project document would make them
look shared and portable when they are neither.

## Source read

`mattpocock-skills` @ a97b87386667 —
`skills/engineering/setup-matt-pocock-skills/SKILL.md`,
`issue-tracker-github.md`, `issue-tracker-gitlab.md`,
`issue-tracker-local.md`, and `.out-of-scope/mainstream-issue-trackers-only.md`.
The source was refreshed before this decision and had not moved.

## Mechanism

Adopt one per-repository adapter that names the provider and maps exact tracker
operations. Keep the custom-provider escape hatch instead of teaching task
intake every tracker. Preserve the source's preview-before-write boundary and
its separation between setup and ordinary task work.

Adapt the storage location from committed `docs/agents/issue-tracker.md` to
gitignored `.local/tracker.md`. Task intake checks that path first, then falls
back to committed repository instructions. The adapter is an operation map, not
a credential store, proof of authentication, or grant of write permission.

Do not add a separate setup skill yet. One file and one lookup rule solve the
current problem. Revisit automation only after configuring adapters manually is
repetitive enough to produce a concrete failure.

## Fit

The local path serves both harnesses and can describe a CLI, MCP connector, API,
or local files without adding a dependency. The tradeoff is intentional: a new
clone, worktree, or VM does not receive the file. Shared policy still belongs in
`AGENTS.md` or a committed skill.

This checkout's first adapter uses GitHub Issues for
`platonoff-dev/ai-bench`, following the source's default for a GitHub-hosted
repository. It records that `gh` is currently unavailable, defines safe
fallbacks, and has no standing write authorization. Because the choice is local,
changing providers does not require a plugin edit.

## Trial

`git check-ignore` resolves `.local/tracker.md` to the repository's `.local/`
rule, and ordinary status omits the file. The adapter covers all four task-intake
operations: read task, search related work, read brief, and publish brief.

All 12 task-intake regressions and the nine-route playbook check pass. Both
authored skills pass the Codex skill validator; Claude accepts both its
marketplace and plugin manifests; and both vendored skills match their pins. The
Codex plugin validator reaches only its already documented vendored-skill
failure: it rejects `disable-model-invocation: true` in the unchanged strict
review skill.

This structural trial does not prove live GitHub access or publication because
`gh` is not installed locally and no authenticated GitHub interface was used.

## What would reverse this

Move the adapter into committed documentation if the same instructions must be
identical in every checkout. Add a narrow setup skill only if manual creation
causes repeated omissions or malformed files. Do not broaden task intake into a
provider catalogue merely because another project uses a different tracker.

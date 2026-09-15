---
name: show-me-your-work
description: "Keep a reviewable decision trail for long or unattended work. One TSV row per decision (what, why, evidence, result), kept in the project's scratch area and committed only when asked. Use when explicitly asked for show-me-your-work, for autonomous or multi-phase runs, or when another skill routes its audit trail here."
disable-model-invocation: true
---

# Show me your work

Keep one canonical log.

Read the active project's `CLAUDE.md` / `AGENTS.md` first: they decide where
the log may live and whether anything gets committed. The `references/` and
`scripts/` paths below are relative to this skill's own directory in Claude Code
or Codex; resolve them from there, not from the project root.

## The format

A single TSV file, one row per decision. Cells stay single-line. Evidence is a pointer, not prose.

Copy `references/decision-log-template.tsv` (the header row) to start a clean log. Columns:

- **ts.** ISO8601 timestamp.
- **phase.** The phase or workstream.
- **decision.** What was chosen or done, one line.
- **why.** The reason in plain words. If a principle drove it, say it plainly, not as a jargon tag.
- **evidence.** A link or path that proves it: commit SHA, PR number, `file:line`, or an artifact, trace, or screenshot path. Never a paragraph.
- **result.** The outcome or predicate state: `tests green`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`.

An example, plain-spoken so a reviewer reads it at a glance (tabs shown as spaces). This is illustration only. Don't copy these rows into a real log.

```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted the work first, about 100 components and roughly 75 hours	wanted to know the size before starting a long run	commit 3a9f1c2	found 5 things to sort out before starting
2026-05-24T09:40:00Z	harness	took screenshots of the old version before changing anything	so we can compare old against new and catch any visual change	scripts/snapshot.sh, baseline/	saved 120 reference screenshots
2026-05-24T11:15:00Z	widget	moved the widget styles over without changing how it looks	keep the change small and the result identical	commit 7c21e0a, pixel-diff 0	looks identical, tests pass
2026-05-24T12:30:00Z	widget	threw out a helper's work because its screenshots were blank	checked the real files instead of trusting its summary	worktree reset	reverted, tightened the instructions for next time
```

## Logging a row

Write each entry the way you'd tell a teammate what you did. Plain words, concrete actions, no AI speak or abstract jargon (the [unslop](../unslop/SKILL.md) skill applies to log text too).

Use the helper `scripts/log.sh .local/audit/<task-slug>.tsv <phase> <decision> <why> <evidence> <result>`; the first argument is the log path chosen under "Where it lives". It needs only `bash` and the standard `date`, `tr`, `mkdir`, and `dirname` utilities. It stamps `ts`, writes the header on first use, strips stray tabs/newlines, and prefixes any cell starting with `=`, `+`, `-`, or `@` with a single quote. A bare `printf` appending a row works too, but mind those same bytes if cells come from generated or user-supplied text.

Log decision points and checkpoints, not every action: a fork chosen, a unit completed with its verification result, a pivot or revert with its trigger, a blocker surfaced, a gate fixed. For a recurring or long-running run, including one driven by the harness's own loop or scheduling facility, one row per iteration. Skip the trivial and self-evident.

## Where it lives

By default the log is a working artifact, not committed. Use the scratch location the project's instructions allow (in astack, `.local/`: `.local/decisions.tsv`, or `.local/audit/<task-slug>.tsv` when several efforts run at once). If none is named, use an existing git-ignored directory inside the checkout (`git check-ignore -q <dir>` confirms one); otherwise create `.audit/` and exclude it through `.git/info/exclude` rather than editing a tracked `.gitignore`, so the trail leaves no diff behind. Name the path in the reply. Do not assume an editor-specific directory exists.

Commit the trail only when the user asks. When the work is ambitious enough that a reviewer needs the trail to trust the result, say so and offer to commit it; do not commit on that judgment alone.

## Rules

- One row is one decision or checkpoint.
- Append-only. A wrong call gets a new row that supersedes it. Never edit or delete history.
- Prefer evidence produced by committed scripts over hand-made one-offs, following [Encode Lessons in Structure](../principles/references/encode-lessons-in-structure/reference.md) from the [principles registry](../principles/SKILL.md).

## Audit the log against the run

At the end of the run, before handing back, check the log told the truth. The record of what happened is the conversation already in your context. If the harness exposes a transcript path or read interface tied to the exact current session, use it after confirming it is this session; do not pick the newest file, search other sessions' transcripts, or assume any editor's transcript layout. When earlier history was compacted or is otherwise unavailable, the audit covers only what you can still see; say so in the Attention section. Walk the log against what actually happened:

- Every row maps to a real action. Cut invented or aspirational entries.
- Each row's evidence resolves and shows what the row claims.
- A fork, pivot, or abandoned approach that shaped the work but isn't logged is a gap. Add it.
- Drop padding.

Fix the log, not the story. If the work diverged from what a row claims, the row is wrong.

## Independent review of the trail

Before handing back, hand the trail to a fresh reviewer: a subagent that runs under the [shared execution and result contract](../../references/agent-workflows.md), which settles the delegation interface, runner selection and reporting, fresh context, and read-only access. What is specific to this skill: the brief holds the log path, the checklist below, and the run's record as factual pointers (commands run, diffs, output paths, the transcript path when the harness ties one to this session), never your own summary or verdict. A parent-written summary hands the reviewer the story it is meant to check. Self-review is not a substitute. The reviewer reads the trail and the record, then flags what the user should pay attention to. Not a redo of the work, a scan for what's suboptimal or risky. The reviewer flags:

- Decisions logged with weak or absent evidence.
- Verification steps skipped or claimed without proof in the transcript.
- Choices that look risky in hindsight (premature, scope-creeping, papering over a symptom).
- Gaps the user would otherwise miss on a casual skim.

Prefer a reviewer from a different model family than the one that did the work when the harness offers one and the user has authorized it; the contract's runner rules apply otherwise. A reviewer on the same model still gives a fresh context; it does not give cross-family independence, and the Attention section must not claim it did.

Every reply for a run that produced a trail ends with an "Attention" section. Lead with the reviewer on its own line: `reviewed by <model>`, or `reviewed by unknown` when the harness does not disclose the runner. Then list each flag pointing to specific rows or moments. "No flags" is a valid value. Leaving the reviewer line out is not. If delegation was unavailable or refused, write `reviewed by none` with the reason on that line; your own check does not count as the review.

## Reviewing the trail

Read top to bottom, follow the evidence pointers, spot-check. Forges such as GitHub render a committed TSV as a table. `column -s$'\t' -t decisions.tsv` renders it in a terminal; macOS `column` aborts on very long cells, so put `cut -c1-200 decisions.tsv |` in front when a row might be long.

## Composing this skill

Other skills route their audit trail here instead of inventing one. Reference it by name and let it own the format. Don't restate the columns.

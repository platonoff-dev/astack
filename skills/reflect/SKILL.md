---
name: reflect
description: Spawn three independent review subagents over the active conversation, surface durable learnings, and propose concrete skill edits for approval. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user explicitly asks to reflect, uses `$reflect` in Codex, or `/astack:reflect` in Claude Code. Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Prepare the active conversation evidence

Use the active conversation already available to the parent. If the harness provides a transcript path or a read interface tied to the exact current session, use that after checking the session identity. Do not infer the active session from the newest file, search unrelated sessions, or assume a Cursor transcript layout.

When no exact transcript is available, prepare a tight digest with the task, actions, corrections, results, relevant skill paths and invocation policies, and short supporting excerpts with turn or tool-call labels. Mark omitted or compacted history and distinguish direct excerpts from summaries. Reviewers must not invent exact quotations or events missing from the packet. Pass the same evidence packet to all reviewers and the synthesizer. A digest loses detail; disclose that limit.

Keep any necessary scratch artifacts in a permitted location under the active project's `.local/` directory, subject to its `CLAUDE.md` / `AGENTS.md` and the harness's data-handling rules. This workflow does not write persistent memory.

### 2. Spawn three independent reviewers

Use the active harness's native subagent API: `collaboration.spawn_agent` when exposed in Codex, or Claude Code's `Agent` tool with its general-purpose agent type. Check the actual tool schema before calling it. Start three separate contexts in parallel when capacity permits; otherwise schedule independent contexts in batches and disclose reduced concurrency. Never replace a missing reviewer with the parent's own review. If independent subagents are unavailable or prohibited, report that blocker.

Use the inherited model by default. Honor user-selected role models only when their exact identifiers and any effort settings are supported by the current harness. Do not translate Cursor model slugs. The default preserves lens diversity but does not guarantee different model families.

| Lens | Prompt template |
|---|---|
| Judgment | [references/judgment-reviewer.md](references/judgment-reviewer.md) |
| Tooling | [references/tooling-reviewer.md](references/tooling-reviewer.md) |
| Divergent | [references/divergent-reviewer.md](references/divergent-reviewer.md) |

Pass each template verbatim, substituting the transcript path or digest where marked. Include the current repository instructions and the skill paths and policies needed to interpret the evidence. Prefer a fresh context containing only this packet when the API permits it; never share one reviewer's findings with another before they finish.

Reviewers need file reading and, conditionally, authorized read access to external context cited by the conversation. Use exposed tools or the project's private access guides when needed. Tool presence alone does not establish authentication or permission. Preserve the harness's permission controls; do not copy Cursor's `readonly: false` setting or enable writes to obtain read access. Missing sources remain unverified. Reviewers return findings through the native subagent result, without editing files or posting externally.

### 3. Synthesize

After all three reviewers finish, start a separate synthesizer subagent using the same model-selection rule. Use [references/synthesizer.md](references/synthesizer.md) verbatim, with each reviewer's full output inlined where marked, and supply the same conversation evidence packet. It needs read access to proposed target skills and cited evidence to spot-check findings. Its result is the structured Accepted / Rejected / Backlog list. If a reviewer fails, retry within the task's limits or report incomplete review; do not present a partial panel as full consensus.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. Read the [principles registry](../principles/SKILL.md) and its [Encode Lessons in Structure](../principles/references/encode-lessons-in-structure/reference.md) reference, then apply that decision rule. This named principle is required; it does not authorize implementing backlog items.

### 5. Prepare and apply approved changes

Present the full Accepted / Rejected / Backlog output and a concrete proposed diff for each Accepted item before asking the user which subset to apply. Prepare drafts in permitted scratch. Skill changes affect future sessions; do not auto-apply. Existing approval of an exact proposal remains valid within its reviewed scope.

Resolve each target from the transcript's skill path to its maintained source checkout, and read that repository's `CLAUDE.md` / `AGENTS.md`. Never edit an installed plugin cache or assume an unknown source location. For a registered vendored skill, prepare a registered compatibility patch and reproduce it through that repository's vendor workflow. Preserve concurrent edits, invocation policies, provenance, licenses, and required version changes. Keep private session details out of public skills and patches; use invented examples. If the maintained source is unknown, leave the proposal pending that information.

For each Accepted item, preserve the proposed Routing and use Anthropic's `skill-creator` for substantive edits, description tuning, and new skills. Read [references/authoring.md](references/authoring.md) for dependency discovery and the handoff contract:

- Trivial existing-skill edit: a narrow parent edit to the approved source.
- Substantive existing-skill edit: hand the approved section and evidence to `skill-creator` for its draft / test / review / iterate loop.
- `tune description: <skill path>`: hand to `skill-creator` for description optimization where its runtime is available; preserve invocation policy, since explicit-only skills are not automatic-trigger failures.
- `new skill: <kebab-name>`: hand creation to `skill-creator` only when no existing skill is a real home and the user approves creation.

Keep Backlog items in the response or permitted local report. File them externally only when the user has authorized the specific destination and content; inspect the applicable private access guide first. Do not create tickets automatically.

After approval, apply only the reviewed subset and run the target repository's required validation and any available skill validator. A missing validator is a reported gap, not a reason to skip required repository checks. Distinguish structural validation from observed behavior. Installation, committing, pushing, and publishing require their own authorization.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed and what was checked, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog: proposed locally or filed with authorization; include a real issue link only if created.
- Dropped: one line per rejected finding + reason from the synthesizer.
- Remaining limits: incomplete history, unavailable sources, or untested behavior that matters.

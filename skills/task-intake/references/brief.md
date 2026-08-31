# The working brief

Write Markdown for the next person or agent. Draft locally; once published, the
identified tracker version is the shared handoff and the local file is its
working copy. Link evidence instead of embedding investigation transcripts.
HTML or a prototype can be supporting evidence, not a second brief format.

Aim for 250-400 words, with no minimum. The checker warns above 600 words; this
is a trial limit, not permission to truncate requirements. Cut repetition, link
detail, or explain why a longer brief is warranted. Keep material constraints
and blockers inline. Length alone does not justify splitting the task.

## Format

Use these plain field names and headings so the standard-library checker can
read the brief. Fields stay before the first `##` heading. Do not wrap the whole
brief in a code fence. Replace the template text with actual findings.

```markdown
# Task identity: outcome in plain language

Source: Ticket URL, source file, or identified conversation
Checked: Date; source revision/update or unknown; repository revision and worktree state; relevant environment
Work type: bug
Next action: investigate

## Outcome
Problem and desired result, distinguishing unconfirmed intent.

## Evidence
- supported: Claim, observation, and limits. [Receipt](evidence.md)
- contradicted: Ticket claim and comparable counter-evidence. [Source](source.md)
- unresolved: Claim and the specific missing evidence.

## Scope
Material constraints, exclusions, risk controls, and safe stated assumptions.

## Completion checks
- Observable check for the work that can proceed next.

## Questions
- Material unanswered human question, who can answer, and what it blocks.

## Next step
Concrete action justified by this brief, including any execution boundary.
```

`Work type` accepts the values in [work-types.md](work-types.md), separated by
commas when needed. `Next action` is exactly one of its five actions.

`Outcome`, `Evidence`, and `Next step` are always present. Include `Scope` when
there are material constraints or exclusions. `Completion checks` is required
for `implement` and `investigate`, with at least one bullet for the proposed
work. Investigation checks answer its question, not the whole feature request.

`Questions` contains only unresolved human blockers; omit it when there are
none. Keep nonblocking technical uncertainty in evidence and safe assumptions
in scope. `decide` requires questions. `implement` and `no-change` cannot carry
unresolved human blockers. `investigate` or `split` may retain questions, but
the next step must say which work can proceed without their answers. Record
resolved answers with their source, then remove them from this section.

For `split`, add `## Breakdown` with at least two proposed children:

```markdown
1. Outcome delivered. Check: its observable result. Depends on: none.
2. Next outcome delivered. Check: its observable result. Depends on: 1.
```

Each evidence entry is a bullet beginning `supported:`, `contradicted:`, or
`unresolved:`; wrapped lines are allowed. Supported and contradicted entries require an inline Markdown
link to the inspected source or receipt. Paths are allowed as evidence at a
known revision, not mandatory future edit locations. Preserve relevant results
of local commands in a receipt if no existing source captures them. For a
conversation without a permalink, a short attributed source note is enough.
Do not manufacture artifacts or observations merely to satisfy the checker.

## Check and hand off

Run `python3 <skill-dir>/scripts/check_brief.py <brief.md>` from any directory.
Exit 1 means malformed fields, missing conditional content, or unsupported
evidence entries. Exit 0 means structurally valid, possibly with a size warning.
Neither verdict verifies sources, correctness, permissions, link accessibility,
or the sufficiency of acceptance checks. Review those yourself.

At implementation pickup, read the current brief and new source activity; recheck
material claims against the current repository and environment. New evidence can
reopen a decision. Keep execution logs outside the brief; update the shared
handoff when its outcome, constraints, evidence, or next action changes.

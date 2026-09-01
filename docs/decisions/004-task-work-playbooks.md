# 004: Route task work directly to focused playbooks

- **Date:** 2026-09-01
- **Verdict:** adopt
- **Status:** superseded by decision 005; the router remains and the provisional
  playbook bodies were removed
- **Touches:** `skills/task-work/`, `skills/task-intake/`, both plugin manifests,
  README, research records

## Failure it prevents

The earlier design made intake choose a work type and then choose `implement`,
`investigate`, `decide`, `split`, or `no-change`. Ready change work passed
through a generic `task-implement` candidate before reaching its useful method.
Investigation appeared in both axes even though it is work with its own question,
checks, and result.

This duplication makes transitions harder to read and invites a generic guide
that repeats the brief. It can also make an agent treat investigation as a
preliminary failure instead of the task's current job.

## Sources and trial

- `pstack` at `b9ddc83c3297`, especially its investigation, bug-fix, feature,
  refactoring, and performance playbooks plus its verification principles.
- `mattpocock-skills` at `a97b87386667`, including implementation, TDD, code
  review, diagnosis, and phase-boundary material.
- Anthropic skills at `3b3fad96af16` and bundled Codex skill-creator guidance at
  digest `18682dc33320` for progressive disclosure and forward testing.
- Ten primary studies and first-party reports in
  `docs/research/task-work-evidence.md`.
- One fixed-revision trial of the rejected 383-word flat guide. Both guided and
  ordinary conditions passed all nine hidden checks, so that trial showed no
  value for a generic implementation layer.

## Decision

Replace `Work type` plus `Next action` with one required `Playbook` and optional
`Modifiers`. The supported routes are `investigation`, `bug-fix`, `feature`,
`refactor`, `performance`, `migration`, `decision`, `split`, and `no-change`.

Add one model-invoked `task-work` skill. Its entrypoint owns common routing,
authorization, preservation, transition, final-check, and status rules. It loads
only the selected file under `references/playbooks/`. Investigation is a full
playbook and changes route in the same task brief when evidence supports the next
job.

Modifiers add checks or constraints without starting another playbook. The
primary playbook owns the sequence. No mandatory TDD, planning artifact,
subagent, full suite, commit, PR, tracker write, or deployment step is added.

## Fit and validation

One visible router avoids nine competing skill descriptions. Nine branch files
keep conditional detail out of the common context. The intake checker provides
the runnable contract check; 15 regressions cover the new route, modifiers,
evidence rules, decisions, splits, legacy rejection, and CLI behavior. A second
standard-library check requires every accepted route to have one router row and
one playbook file.

The plugin version moves to 0.5.0. Both harnesses discover the same Markdown
files without a generation step.

## What would reverse this

Revisit if agents routinely choose the wrong playbook, fail to transition when
entry facts change, load irrelevant branches, or turn modifiers into a second
workflow. Test those failures on real tasks before adding fields, playbooks, or
scripts.

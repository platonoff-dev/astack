---
name: task-work
description: Work an evidence-backed software task through one selected playbook and route it again when evidence changes. Use after task-intake or when a current task already has a supported outcome, scope, route, and completion checks. Raw, stale, or unclear requests need task-intake first.
---

# Task work

**Carry one task through its current playbook to checked evidence or a justified new route.**

## Hard rules

- Keep the task's outcome and constraints authoritative. A playbook controls the
  method, not product intent.
- Inspect the current repository, environment, and brief before acting. Preserve
  unrelated work. Newer evidence can invalidate the route.
- Work one primary playbook at a time. Modifiers add proof obligations; they do
  not start another full playbook.
- Never use an agent exit, report, test file, or green proxy as completion
  evidence. Check the behavior named by the task.
- Do not infer authorization for commits, publication, deployment, tracker
  edits, or other external changes.

## Route

Read only the selected playbook:

| Playbook | Read |
|---|---|
| `investigation` | [investigation.md](references/playbooks/investigation.md) |
| `bug-fix` | [bug-fix.md](references/playbooks/bug-fix.md) |
| `feature` | [feature.md](references/playbooks/feature.md) |
| `refactor` | [refactor.md](references/playbooks/refactor.md) |
| `performance` | [performance.md](references/playbooks/performance.md) |
| `migration` | [migration.md](references/playbooks/migration.md) |
| `decision` | [decision.md](references/playbooks/decision.md) |
| `split` | [split.md](references/playbooks/split.md) |
| `no-change` | [no-change.md](references/playbooks/no-change.md) |

A current, specific user request may supply the brief in conversation. Do not
force intake ceremony when outcome, evidence, constraints, playbook, and checks
are already clear. Use `task-intake` when consequential claims are stale,
contradictory, or too weak to choose a playbook.

Apply each modifier through a named constraint or completion check. For example,
`performance` requires comparable measurements and `migration` requires a
transition and recovery check. Drop a modifier that changes no decision or
proof requirement.

## Work and transition

Follow the selected playbook until its completion evidence exists or an exit
condition changes the route. Update the same task brief with the new `Playbook`,
evidence, checks, and next step. Do not restart intake or create a second task
record merely because the route changed.

Continue directly into the new playbook when the user's request includes that
work and no human decision blocks it. Stop at `decision` when only the named
person can answer. `split` creates separate work only for independently
verifiable outcomes.

## Finish

Run affected checks on the final relevant state. Inspect the diff against the
brief and unrelated work. Report passed, failed, and unrun checks. State the
current playbook and any remaining route. Keep implemented, verified, committed,
pushed, reviewed, published, and deployed states separate.

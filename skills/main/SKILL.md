---
name: main
description: Main entrypoint for starting or resuming evidence-backed work. Use a current brief when it names a playbook, or run task-intake first when the request is new, stale, or unclear. Continue through the selected adopted playbook when work was requested. Empty playbooks are reserved placeholders, not instructions.
---

# Main

**Establish the current route, then load its playbook without inventing policy
for an empty route.**

## Entering the work

Use a current evidence-backed brief when it already names `Playbook`. Run
`task-intake` first when no such brief exists or material evidence may be stale,
contradictory, or unresolved. An intake-only request ends with the brief. When
the caller requested the work itself, continue from the same brief after intake.

## Hard rules

- Keep the task's outcome, evidence, constraints, and newer user decisions
  authoritative.
- Read only the selected playbook. Do not combine several placeholder files into
  a procedure.
- An empty file means this repo has not adopted that playbook. Say so plainly;
  never claim to have followed it or fill its gaps from memory.
- Add playbook content only through that playbook's own research and decision.
- Preserve unrelated work and existing authorization boundaries.

## Routes

| Playbook | File |
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

Open the file named by `Playbook`. If it is empty, the skill adds no execution
procedure. Continue only under the user's request and the target repository's
instructions, and state that no ai-bench playbook was applied. If the request is
to design that playbook, research and decide it instead of using it on live work.

When a future playbook is adopted, follow that file and any task modifiers it
defines. Keep task status and delivery claims tied to observed evidence.

# Choosing the playbook

Select the task's current job, not the ticket's label. One task may move through
several playbooks as evidence changes. Intake chooses the first supported route;
`task-work` performs it and records later transitions in the same brief.

| Playbook | Establish before routing | Completion evidence |
|---|---|---|
| `investigation` | Precise question, why it matters, bounded evidence-gathering method | Supported answer, justified next playbook, or a precise remaining blocker |
| `bug-fix` | Intended and observed behavior, affected conditions | Original failure addressed on the relevant path; regression protection where practical |
| `feature` | Desired scenarios, scope, compatibility, product constraints | Agreed scenarios and relevant failures work; preserved behavior checked |
| `refactor` | Structural problem worth fixing, behavior to preserve | Behavioral equivalence and removal of the named structural cost |
| `performance` | Representative workload, baseline, metric, target or comparison, tradeoffs | Comparable measurements improve without violating correctness or resource constraints |
| `migration` | Initial and target states, consumers or data, compatibility, recovery | Transition and recovery checked; consumers and data valid; old state retired as agreed |
| `decision` | Material human choice, owner, consequence of each answer | Answer and source recorded; same task routed onward or left with a precise blocker |
| `split` | Outcomes can be verified, delivered, prioritized, reverted, or owned independently | Each child has an outcome, check, dependencies, and playbook |
| `no-change` | Evidence supports resolved, duplicate, superseded, declined, support, or configuration disposition | Exact reason, inspected state, limits, and any authorized follow-up recorded |

`investigation` is a full playbook. Use it when technical evidence is the work,
including reproduction, tracing, profiling, history analysis, or a disposable
probe. Do not route to a change playbook merely because the ticket proposes a
solution.

## Modifiers

Modifiers add proof requirements without loading another full playbook. Use a
lowercase name such as `performance`, `migration`, `security`, `privacy`,
`billing`, `data-integrity`, or `production-impact`. The brief must carry the
modifier's real constraint or check. Drop decorative labels.

Choose the playbook that owns the current sequence. A confirmed timeout defect
with a latency target can use `Playbook: bug-fix` and `Modifiers: performance`.
An unknown slowdown uses `Playbook: investigation` and the same modifier until
evidence supports a change route.

Documentation, tests, CI, dependencies, and technical debt usually describe an
affected artifact or constraint. Make one a modifier only when it changes proof
or risk controls.

## Transitions

Evidence may route the same task onward. Common transitions include
`investigation` to a change playbook or `no-change`, a change playbook to
`investigation` or `decision`, and any oversized route to `split`. An active
incident goes to the incident process for stabilization; intake must not delay
it with ordinary classification.

One coherent outcome can retain several steps. Split only for independently
verifiable outcomes. A large diff or long brief alone does not justify child
tasks. A proposed split does not authorize tracker edits.

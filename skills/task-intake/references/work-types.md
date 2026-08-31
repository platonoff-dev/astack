# Choosing the next work

Use one primary type; add another from the table when its proof requirements
matter. These are working classifications, not new tracker fields.

| Work type | Establish first | Completion evidence |
|---|---|---|
| `bug` | Intended versus observed behavior and affected conditions | Original failure addressed on the relevant path; regression protection where practical |
| `feature` | Desired scenarios, scope, compatibility, and product constraints | Agreed scenarios work, with relevant failures and preserved behavior checked |
| `refactor` | Structural problem worth fixing and behavior to preserve | Behavioral equivalence and improvement to the named structural problem |
| `performance` | Representative workload, baseline, metric, target, acceptable tradeoffs | Comparable measurements improve without violating correctness or resource constraints |
| `migration` | Initial and target states, consumers or data, compatibility, rollout and recovery | Transition and recovery checked; consumers and data valid; old state retired as agreed |
| `investigation` | Precise question, why it matters, bounded evidence-gathering method | Supported answer, decision, or a precise remaining blocker; production code is optional |

Security, privacy, billing, data integrity, and production impact add risk
controls. Documentation, tests, CI, and dependencies describe affected artifacts:
apply only the checks their actual change needs. Technical debt must name the
cost or failure it removes. An active incident goes to the incident process for
stabilization; intake must not delay it with ordinary planning.

## Next action

- `implement`: outcome, scope, evidence, and completion checks suffice; no
  unresolved human question blocks the proposed implementation.
- `investigate`: a concrete question and useful check exist, but evidence does
  not yet justify implementation. Identify which investigation can proceed.
- `decide`: a material question needs human intent, judgment, authorization, or
  unavailable information. State who can answer and what the answer changes.
- `split`: propose separately verifiable outcomes, their checks, and dependencies.
- `no-change`: explain why implementation is unnecessary: resolved, duplicate,
  superseded, support/configuration issue, or deliberately declined. Preserve
  which reason applies and its evidence. Do not silently close the source ticket.

## Size and relationships

One coherent outcome can remain one task with several implementation steps.
Subtasks are useful only when those steps need separate tracking. Split tickets
when outcomes can be verified, delivered, prioritized, or reverted separately.
Prefer complete behavior slices; real prerequisites and migration stages may
need another sequence. State dependencies, avoiding cycles and fabricated
independence.

Propose an epic for a broader outcome requiring multiple meaningful deliverables
and coordination. A large diff or long brief alone does not justify one. When
uncertainty prevents an honest breakdown, investigate or decide first; specify
only the work currently understood. A proposed split does not authorize creating
issues or changing the parent.

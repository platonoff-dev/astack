# Researching routed task playbooks

Status update on 2026-09-01: decision 005 supersedes the provisional playbook
bodies described below, and decision 006 later renames the router `main` as the
generic work entrypoint. All nine route files remain empty pending separate
research and decisions.

Read on 2026-09-01. This report asks how work should continue after task intake.
It compares tracked agent setups, current primary research, a local trial of a
flat implementation guide, and the final router design chosen after review.

## The first design used the wrong boundary

The first candidate inserted a `task-implement` skill between an intake brief
marked `implement` and work-specific proof. Its 383 words carried shared rules
for evidence, scope, checks, and delivery state. Two isolated runs then fixed the
same real `prior_art.py diff` defect. Ordinary execution and guided execution
both passed all nine fixed checks. The guide prevented no observed failure.

That result rejects the flat guide on the tested task. It does not test pstack's
more useful mechanism: classify the current job and load a focused playbook. The
trial inputs and limits remain in
[task-work-flat-trial.md](task-work-flat-trial.md).

The old intake schema also exposed the boundary problem. It could produce both
`Work type: investigation` and `Next action: investigate`. For ready change
work, `Next action: implement` added another label before the agent reached the
bug, feature, refactor, performance, or migration method. The generic action had
no proof sequence of its own.

## What survives from prior art

The refreshed pstack source at `b9ddc83c3297` routes work to separate bug-fix,
feature, refactoring, performance, investigation, and lifecycle playbooks. Its
best distinction is the proof required by each job:

- a bug fix reproduces the failure and verifies the same path after the change;
- a refactor pins behavior and proves equivalence;
- performance work records comparable measurements;
- an investigation answers a bounded question and routes onward; and
- a migration checks transition, consumers, and recovery.

This repo does not adopt pstack's mandatory subagents, model choices, control
skills, commit choreography, PR machinery, or large mode router. Those choices
depend on its harness and team setup. The primary-source limits are recorded in
[task-work-evidence.md](task-work-evidence.md). They support observable checks
and work-specific proof. They do not establish a universal process, mandatory
TDD, or mandatory multi-agent coding.

The skill-creator sources from Anthropic and Codex support progressive
disclosure here. The top-level skill holds common routing and finish rules. Each
branch file contains only the method needed for that playbook.

## Direct routing model

Task intake now emits exactly one `Playbook` and optional `Modifiers`. There is
no `implement` action and no `task-implement` skill.

| Playbook | Current job |
|---|---|
| `investigation` | Answer a bounded technical question |
| `bug-fix` | Repair an established behavior contract |
| `feature` | Add agreed behavior |
| `refactor` | Improve structure while preserving behavior |
| `performance` | Improve a measured property |
| `migration` | Move between known states with recovery |
| `decision` | Resolve a material human choice |
| `split` | Produce independently verifiable tasks |
| `no-change` | Prove and record why no product change is needed |

Investigation is a full task playbook. It can reproduce, trace, profile, inspect
history, or build a disposable probe. When evidence establishes the next job,
the same brief changes route. A task may move from `investigation` to `bug-fix`,
from `feature` to `decision`, or from any oversized route to `split` without
restarting intake.

Modifiers add proof obligations without loading another full playbook. A
confirmed timeout defect can use `Playbook: bug-fix` with
`Modifiers: performance`. The bug-fix sequence owns the work, while the brief
also requires comparable timing. Security, privacy, billing, data integrity,
and production impact work the same way when they change checks or constraints.

## Component shape

The 0.5.0 candidate component was `skills/task-work/`:

```text
SKILL.md
references/playbooks/
  investigation.md
  bug-fix.md
  feature.md
  refactor.md
  performance.md
  migration.md
  decision.md
  split.md
  no-change.md
```

The model sees one discriminating skill description rather than nine competing
descriptions. `SKILL.md` reads only the selected branch. Common rules preserve
the task outcome, unrelated work, current evidence, authorization boundaries,
final checks, and honest delivery state.

Every playbook states its entry facts, work sequence, completion evidence, and
exit routes. A playbook must route away when its entry conditions fail. A bug
that cannot be established goes to `investigation`; unclear product behavior
goes to `decision`; independent outcomes go to `split`.

## Validation and limits

The intake checker now rejects the legacy two-field route. Fifteen regression
checks cover every conditional section, supported and unresolved evidence,
direct investigation, decisions, splits, one primary playbook, optional unique
modifiers, legacy-schema rejection, wrapping, CLI exit codes, and read errors.
The playbook packaging check compares intake's accepted routes with the router
table and files, so adding a route in only one place fails validation.

These checks validate the handoff contract, not classification quality. The
flat-guide trial remains evidence only for the rejected candidate. The routed
playbooks still need trials on a real investigation, a change task, a route
transition, and mixed proof modifiers. Improve a playbook after an observed
failure. Do not grow a checklist for hypothetical cases.

## Decision

Adopt the direct router and focused playbooks. The user's preference for pstack's
classification model resolves the design tradeoff that the flat trial could not
measure. Keep the router small, keep investigation inside the task system, and
add a playbook only when its work requires a different proof sequence.

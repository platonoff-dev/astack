# Native agent execution and results

Arena, Swarm, and Interrogate use this shared contract. It is an instruction
protocol for the lead, not an executable runner or an isolation guarantee.

## Frame and dispatch

Read the active project's `CLAUDE.md` / `AGENTS.md`. Use the current harness's
native delegation interface and its actual supported fields, capacity, and
permissions. Keep one run within that harness. Do not assume Cursor Task fields,
cloud execution, a model registry, or a CLI bridge.

Omit model and reasoning overrides unless the user or applicable instructions
select an available, exact value. Record the requested and observed runner when
known, otherwise `unknown`. Repeated runs of one model provide independent
attempts, not model diversity. A rejected selection is a reported gap; use only
an already-authorized fallback, without guessing a model or editing configuration.
Using an inherited or default runner does not show that alternatives are
unavailable; make an availability claim only from relevant current evidence.

Before launch, give each unit a self-contained brief containing its ID, task,
exact input identity, scope, allowed effects, owned workspace/output, completion
checks, and any task-specific time or retry limit. Freeze the required inputs:
for code, identify the base and diff or a snapshot that includes the relevant
authorized uncommitted work. A default worktree may start from the wrong branch
or omit that work. Verify the baseline in each workspace before dispatch.

Use fresh worker contexts containing the brief and required source context, not
the lead's tentative verdict or other workers' outputs. Queue or batch within
native capacity. Sequential fresh-context attempts can retain independence;
repeating perspectives in the parent does not complete a panel or arena. If
fresh delegation is unavailable, report that limit and any useful parent work
as a single attempt. Do not hide the lost independence.

## Own writes and submissions

Give concurrent code writers separate copies or worktrees from the verified
input, and distinct output locations. Separate report files alone do not isolate
shared source edits. If source workspaces cannot be separated, use read-only
workers and lead-only serial implementation, and disclose the changed execution.
Keep scratch artifacts in the active project's permitted working area.

Reviewers and judges read inputs and return findings; they do not modify the
reviewed source. Use per-worker tool or sandbox restrictions where available.
If the interface only supports instructions, state that read-only access and
workspace ownership are behavioral boundaries, not enforced controls.

Keep peer results out of worker briefs until submission. Before comparison,
collect completed outputs, verify their input identity, and freeze the submitted
artifacts by recording their content identities. A changed artifact requires
rechecking. Neutral labels reduce identity bias; shared filesystem access and
content clues mean they do not guarantee blinding or secrecy.

The lead integrates accepted changes one at a time, preserving current work and
checking the combined result. Delegation does not add authorization to publish,
push, install, deploy, or modify external services.

## Collect and accept

Keep the following in a compact run note or table; no particular file format or
new service is required.

| Record | Contents |
|---|---|
| Lead execution | Unit and attempt IDs, returned handle if exposed, requested/observed runner, lifecycle state, input identity, assigned workspace/output |
| Worker result | Unit ID, `PASS` / `ISSUES` / `BLOCKED`, covered scope, artifact references or returned findings, verification evidence, remaining gaps |
| Lead acceptance | Output actually inspected, input match, completion checks, `accepted` / `partial` / `rejected`, unresolved running work |

In the record and synthesis, distinguish supplied facts, direct observations,
worker reports, and inference. Carry each fact only as far as its source supports
it; facts about one attempt do not establish another's. Unspecified execution
details remain `unknown`. Task status alone does not establish dispatch history,
runner choice, or lifecycle.

Record unavailable handles or observations as such; do not invent them. `PASS`
means the worker reports its assigned checks passed; `ISSUES` includes evidenced
problems; `BLOCKED` names what prevented completion. A review that finds issues
can be an accepted review. None of these results proves lifecycle completion or
artifact validity. Inspect actual outputs and evidence before accepting them.
Missing, malformed, stale, or incomplete output remains a gap.

Track lifecycle as queued, running, completed, failed, timed out, cancel
requested, or cancelled, according to observed native events. A wait that expires
leaves the worker running unless a task deadline was reached; slot exhaustion is
a scheduling condition. Even after a deadline, `timed out` does not mean stopped.
Use native waits and cancellation when exposed. A cancellation request is not
confirmed termination. Retain ownership of a writer's workspace until the worker
and relevant child processes are stopped; report when that cannot be confirmed.
Give retries new attempt and output identities, never a workspace still owned by
an old writer. Reassign only within the run's scope and budget.

Apply the workflow's completion rule after acceptance. State missing coverage,
failed attempts, substitutions, checks not run, and any provisional conclusion.

# Inspecting evidence

Start with the claims that determine the playbook. For "exports time out;
increase the client timeout", distinguish the observed failure, its proposed
cause, whether it persists, and whether longer waiting is acceptable. The last
question may require a product decision even when the technical facts are known.

## Inspect, then check

| Source | Inspect | Limit |
|---|---|---|
| Ticket and discussion | Reporter wording, subsequent corrections, dates, versions, intended behavior, linked decisions | A reported fact is not a reproduction; several AI summaries are not independent evidence |
| Screenshot or video | Error, preceding action, state transition, timestamp | Establishes visible behavior, usually not cause |
| Log or trace | Error signature, request identity, surrounding events, build and environment | Applies to the recorded execution |
| Code and configuration | Actual path, callers, effective values, flags | Shows implementation at that revision, not deployment or intended policy |
| Tests | Scenario, assertions, and real path exercised | A nearby passing test may never reach the reported failure |
| Git and related work | Relevant changes, fixes, releases, earlier decisions | A merged fix can still be disabled, unreleased, or ineffective in the affected environment |

Search exact error text and domain concepts with the available repository search
tools. Open the relevant implementation, callers, tests, and configuration. Use
history to check stale locations and recent changes. Finding a similarly named
constant does not establish that this operation uses it. Search for related
reports by trigger, signature, area, version, and source link. Distinguish a
confirmed duplicate from a plausible relation or a recurrence of an old defect.

Choose the smallest safe probe that could change the conclusion: an existing
focused test, CLI fixture, local request, application-control action, captured
trace, or existing benchmark. Inspect supplied commands before execution. Keep
fixtures and scratch outputs isolated; redact secrets and unnecessary customer
data. Do not change production, run uncontrolled load, or apply a speculative fix
to make the probe pass. Missing access is a stated limit, not a reason to guess.

## Evidence record

Keep detailed receipts outside the brief when necessary. An existing artifact
with sufficient context can serve directly; do not create duplicate logs.

```text
Claim: What is being checked.
Check: Exact command, application steps, or source passage inspected.
Context: Repository revision, environment, configuration, input, and date.
Observed: Actual result, including failure or inability to run.
Evidence: Stable source or artifact reference.
Limit: Conditions or conclusions this observation does not cover.
```

Classify the claim as supported, contradicted, or unresolved. Distinguish a
reporter's captured evidence from your own reproduction. Contradiction requires
comparable conditions; one successful run does not disprove an intermittent bug.
Approved requirements establish intent; tests and code alone cannot.

Stop once the playbook is justified. If reaching the relevant environment,
instrumenting the system, or establishing a benchmark becomes substantial work,
route to `investigation` with the exact question and next useful experiment. Do not
require a root cause before permitting investigation. Reopen conclusions when
new evidence changes them.

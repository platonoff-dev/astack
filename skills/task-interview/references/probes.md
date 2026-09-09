# Probes for consequential ambiguity

Read only the section relevant to the open point. These are distinctions for
choosing the next question, not a questionnaire to administer. Follow the user's
answer before selecting another probe. Examples below are hypothetical.

## Problem and scope

Identify who experiences what today and what improvement matters. Separate the
symptom from a claimed cause and a requested mechanism from the underlying need.
Consider supported inputs, users, environments, workload, exclusions, and failure
conditions only where they change the task. For an investigation, acceptance can
be evidence that distinguishes hypotheses, including an inconclusive result with
stated limits; it need not promise a fix.

## Performance

“Fast” needs meaningful start and stop events before a number. Upload start,
upload acceptance, queue entry, worker start, report persistence, and report
retrievability measure different things. Separate queueing from processing and
end-to-end latency. Consider input sizes, arrival distribution, concurrency,
percentiles, measurement window, and the population measured, including treatment
of errors and timeouts. A quiet average does not establish burst behavior.

If the user lacks a threshold, clarify the impact of delay or propose measuring
a baseline. A draft target is neither an estimate nor a demonstrated capability.
Ask what a missed target changes when that affects release or cost decisions.

## Availability and recovery

A healthy endpoint need not mean useful service. Separate submit, status, and
retrieve operations, their success and timeout definitions, and the measurement
period. Background work can stall while every status request succeeds.

For recovery, distinguish unacknowledged, acknowledged but pending, interrupted,
and completed work. A lost response can leave a client uncertain whether a job
exists. Explore the promised outcome on retry or resumption, failure scope
(worker, host, dependency), and crash-to-resumption boundaries when relevant.
Do not turn those promises into a queue technology or retry algorithm by default.

## Correctness and compatibility

Identify an oracle: reference output, domain invariant, reproducible example, or
appropriate human review. Define what would count as incorrect or inconclusive.

Look beyond field shapes to ordering, retries, error meaning, visibility, and
timing. “Completed” might mean computation ended, or that a client can retrieve
the report. A client fetching immediately after that status exposes the
difference. Existing code is evidence of behavior; inspect client use or a
documented promise before treating that behavior as a compatibility requirement.

## Authorization and privacy

Name the actor, operation, and resource. Creating a job does not settle who can
read its status, download a private report, share it, or delete it. An
authenticated user accessing someone else's report tests authorization, not
login. Follow retention or disclosure questions when they affect this task.

## Delivery and evidence

Make the business consequence of delay, degraded behavior, compute cost, or a
changed commitment explicit. Offer tradeoffs as options unless the user selects
one. Do not invent priorities or promise a delivery date from an estimate.

For an experiment, name the uncertainty, conditions, observation sought, and how
different results would change the decision. Separate its proposed method from
execution and observed results. A burst replay, worker interruption, old-client
fixture, or source inspection is useful only if it could change the next action.

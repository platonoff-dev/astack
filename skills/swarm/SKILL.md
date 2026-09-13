---
name: swarm
description: "Coordinate independent workers for bounded coverage or a declared race, verify their outputs, and return one report. Use when explicitly asked to swarm work."
disable-model-invocation: true
---

# Swarm

Workers cover separate slices, race the same brief, or combine both. The lead
verifies their outputs and returns one report.

Read the [shared execution and result contract](../../references/agent-workflows.md).
Keep a short plan for Frame, Fan out, Aggregate, and Report using the available
planning tool or a local note.

## Phase A: Frame

1. State the completion predicate and required artifact or report.
2. Choose coverage, race, or a mixed shape. For coverage, enumerate every required
   slice and its completion checks in a ledger before dispatch. Size slices by
   useful independent work, subject to native capacity.
3. For each race, declare its comparison set and selection rule before dispatch:
   `first pass` accepts the first independently verified qualifying output;
   `rank all` compares every declared contender; `best-of` selects the strongest
   verified output collected within a stated task-specific limit. For `best-of`,
   disclose the considered set and any missing contenders. A mixed run also
   needs a result for every required coverage slice.
4. Choose the requested runners or inherit the active model. Record any model
   race arms without claiming repeated models provide model diversity.
5. Identify exact inputs, allowed effects, workspaces, and outputs. For code
   implementation, use separate source copies or worktrees verified from the
   same baseline. Assign non-overlapping intended changes where practical, then
   integrate serially; distinct report files alone do not isolate code writers.

## Phase B: Fan out

Launch fresh native workers as capacity permits. Each brief stands alone and
contains the goal, exact slice or race arm, input identity, scope, owned
workspace/output, allowed effects, completion checks, and worker result contract.
Do not assume cloud access or a default branch matches the required input.

Track attempts separately from slices. A worker dropout leaves its required slice
open until accepted evidence covers it. Reassign within the run's limits or carry
that gap into the result; surviving workers do not make missing work complete.

## Phase C: Aggregate

Inspect the actual outputs, input matches, and verification evidence before
accepting a slice or race candidate. For implementation, inspect each patch and
integrate accepted changes one at a time, then check the combined result.

Coverage is complete only when every required slice is accepted and the combined
completion checks pass. An `ISSUES` report can satisfy an audit slice when its
coverage and evidence are complete. For a race, apply the declared rule only to
verified qualifying outputs. Cancel unneeded work through the native interface
and report unresolved cancellation; preserve writer ownership until termination.
Missing or cancelled contenders cannot support an all-candidate ranking.

## Phase D: Report

Return one compact table of required slices or race arms, attempt/result status,
accepted evidence, and remaining gaps. Add concise evidenced issues, the race
rule and considered set when applicable, combined verification, and unresolved
running work. Say `complete`, `partial`, or `blocked` against the original
completion predicate. Preserve useful partial results without claiming full
coverage or replacing them with raw worker dumps.

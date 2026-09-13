---
name: arena
description: "Create independent candidates for the same task, compare them with a fresh judge, and synthesize a verified artifact. Use when explicitly asked for arena, alternatives, or an arena comparison."
disable-model-invocation: true
---

# Arena

Create independent attempts at the same task. Read each usable candidate, choose
a base, incorporate the strongest compatible ideas, and verify the result.

Read the [shared execution and result contract](../../references/agent-workflows.md).
Keep a short plan for Frame, Fan out, Cross-judge, Pick, Graft, and Verify using
the available planning tool or a local note.

## Phase A: Frame

1. State the requested artifact, common task, input identity, and constraints.
   Give every candidate the same task and required grounding. Include the actual
   success requirements; keep the lead's comparative scoring notes separate.
2. Derive concrete grading criteria from this task. Fix the rubric before seeing
   candidates so the comparison does not favor whichever output arrives first.
3. Use the requested candidate count, or begin with two useful alternatives.
   Choose native runners under the shared contract. Disclose repeated models.
4. Assign independent workspaces and output locations. For code, verify each
   copy includes the same base and relevant uncommitted input. Follow
   [Separate Before Serializing Shared State](../principle-separate-before-serializing-shared-state/SKILL.md).

## Phase B: Fan out

Launch fresh candidates within native capacity, batching if necessary. Each
receives only the common task, required grounding, its workspace/output, and the
worker result contract. Request the artifact plus a short rationale naming the
alternatives considered and rejected. Do not share peer outputs before submission.

Inspect and freeze submitted artifacts. Retry a failed or unusable attempt only
within the run's limits, or record the gap. At least two usable candidates from
the same input are needed for an arena comparison. One usable result is a single
attempt, even if several workers were launched.

## Phase C: Cross-judge

After the candidates stop writing and their submissions are frozen, launch one
fresh judge with the common task, rubric, and neutral candidate labels. The judge
reads every usable artifact, scores each criterion, and recommends a base with
evidence. It returns the worker result contract. Prefer a different model family
only when one is available and authorized; report the actual runner and any
limits to blinding. The judge may run alongside the lead's own reading.

If the judge fails, retry within the run's limits or return an unjudged comparison.
A lead-only choice is provisional, not a completed independently judged arena.

## Phase D: Pick a base

Read every usable candidate end to end. Score each against the fixed rubric and
compare with the judge. Agreement is a useful observation, not verification.
For disagreement, inspect the competing evidence and explain the decision.

Choose the artifact a future maintainer can extend while preserving its
invariants. Prefer a simpler boundary or smaller API when the rubric is otherwise
tied, following the [Laziness Protocol](../principle-laziness-protocol/SKILL.md).
Record the base, criteria, judge's verdict, and any unresolved uncertainty.

## Phase E: Graft

Read the other candidates again for ideas worth incorporating. Adapt each useful
part coherently rather than pasting competing designs together, following
[Redesign From First Principles](../principle-redesign-from-first-principles/SKILL.md).
Keep frozen candidates intact and record what was incorporated, its source,
and what was rejected with reasons.

Convergence may mean no graft is useful; verify the common shape before accepting
it. Divergence may expose a missing constraint or legitimate tradeoff. Resolve
that cause and reframe within scope when needed; do not average incompatible work.

## Phase F: Verify and return

Check the synthesized artifact against the task and rubric using
[Prove It Works](../principle-prove-it-works/SKILL.md). Inspect the actual artifact
and run appropriate checks within authorization. If a check fails, revisit the
framing, base, or graft that caused it.

Verify factual claims in the final artifact, including worked examples, against
the original task and source evidence. Check assumptions shared by the candidates
or judge; their agreement does not establish unstated facts. Preserve unknowns or
label assumptions instead of presenting them as supplied facts.

Return the artifact and a short synthesis note naming the common input, accepted
candidates, base, judge, grafts, rejections, failed attempts, verification evidence,
and remaining gaps. A completed arena needs at least two usable independent
candidates, a usable fresh judgment, the lead's comparison, coherent synthesis,
and final verification. Otherwise name the partial result precisely.

---
name: interrogate
description: "Review a code diff or selected source with independent reviewers and evidence-based lead judgment. Use when explicitly asked to interrogate code or run an adversarial code review. Returns findings without applying them."
disable-model-invocation: true
---

# Interrogate

Give independent reviewers the same code, intent, and relevant rubric, then
verify their findings and synthesize a verdict. Return findings without applying
changes. This first version reviews code; design documents and prose require a
separately chosen rubric and are outside this workflow's supported scope.

Read the [shared execution and result contract](../../references/agent-workflows.md).

## Step 1: Determine scope

Use the user's selected diff or files. If selection is implicit, inspect the
current branch and working tree and identify the intended comparison base; do
not assume `main` or omit relevant uncommitted changes. For a branch review,
resolve the base and head before producing their diff.

Freeze the diff or source snapshot plus surrounding context needed to understand
the change, and record its identity. Include callers, contracts, and verification
evidence where relevant. If scope is still consequentially ambiguous, clarify
before dispatch; collect unambiguous context in the meantime.

## Step 2: State the intent

State the intended behavior and constraints in one clear paragraph, grounded in
the user's request and available change description, commits, and code. Separate
inference from an explicit requirement. Reviewers check whether the implementation
achieves that goal. They may also flag evidence of a false factual premise or
conflicting requirement, separately from an implementation defect.

## Step 3: Dispatch independent reviewers

Use the requested panel, or begin with two fresh reviewers. Prefer available,
authorized model diversity when it adds useful independent judgment. With one
runner, disclose repeated independent runs of the same model. Use only current
native fields and exact authorized runner values; do not guess replacements or
repair model configuration as a review side effect.

Read and fill [reviewer-prompt.md](references/reviewer-prompt.md) with the intent,
frozen input and context, [rubric.md](references/rubric.md), and the relevant
[code-quality lens](references/code-quality-review.md). Fill the principles
section with resolved absolute registry and reference paths or full guidance needed
for this review, following the shared contract. Send the same substantive
brief to every reviewer, changing only its identity and assigned output. Apply
code-quality concerns proportionally; a broad maintainability audit must be
explicitly selected. Keep peer findings and the lead's tentative verdict out of
reviewer contexts until submission.

Reviewers read source and return findings with the shared result contract. Use
enforced tool restrictions when exposed; otherwise state the behavioral limit.
Batch within capacity. Inspect and freeze submitted reviews. Retry failed or
incomplete attempts within the run's limits, or retain their coverage gaps.

## Step 4: Synthesize

1. Parse all usable reviews and reconcile their claimed coverage with the frozen
   input. Missing context or unexamined scope remains a review limitation.
2. Deduplicate findings by the underlying defect and retain every source reviewer.
3. Verify each consequential claim against the code, reachability, constraints,
   and available checks. A lone evidenced defect survives; a repeated false
   positive is dismissed. Unresolved consequential claims remain explicit.
4. Record agreements and contradictions as metadata. Agreement is a reason to
   inspect evidence, not a correctness vote or a reason to suppress lone findings.

## Step 5: Lead judgment and verdict

Read [lead-judgment.md](references/lead-judgment.md). Categorize every finding:

- **Act on:** A verified consequential issue for this change and its constraints.
- **Consider:** A plausible concern needing evidence or a legitimate tradeoff
  whose benefit is not yet clear. State what would resolve it.
- **Noted:** Valid context with no current action.
- **Dismissed:** Refuted, irrelevant, or unsupported as claimed; explain why.

Keep every verified consequential finding, with location, impact, evidence,
source reviewer IDs, and rationale. Separate premise/requirement concerns from
implementation defects. Recommend action without changing code or merge state.

Return the intent and exact review scope, reviewer/runner table, the four finding
categories that contain results, and a short agreement map. Include coverage,
failed attempts, checks performed, missing evidence, and remaining uncertainty.
Name the overall result: a completed panel requires at least two usable fresh
reviews plus lead verification and judgment. One usable review is a single
review; no findings under incomplete coverage does not certify the change.

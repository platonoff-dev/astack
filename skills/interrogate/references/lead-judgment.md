# Lead judgment framework

Verify, contextualize, and decide. Reviewers can miss surrounding constraints or
suggest a preferred design without identifying a defect. The lead can also miss a
real problem; neither prior confidence nor reviewer agreement settles the claim.

## Check each consequential finding

Trace the code and evidence against the frozen review input. Establish the
trigger, reachability, consequence, and applicable requirement. For bugs, inspect
callers, validation, and error paths. Use appropriate permitted checks when they
resolve uncertainty. If essential context is unavailable, retain the unresolved
claim and name the missing evidence rather than asserting a clean result.

Evaluate findings against explicit review preconditions. Check their enforcement
when boundary validation is in scope or contrary evidence makes a precondition
doubtful. An unread, out-of-scope caller is not itself evidence that a stated
precondition fails. Dismiss speculation that only applies outside the agreed
contract; report the actual review limit without turning it into a defect.

Deduplicate a defect's structural cause and symptoms into one finding when the
same correction resolves both. Retain source reviewer IDs and explicit
contradictions. Split them only if an independently actionable problem remains
after the proposed fix. Corroboration helps direct attention but is not a vote.
Keep a lone verified defect; dismiss repeated claims when the code refutes them.
Repeated runs of the same model are not distinct model families.

## Filter with context

- Style preferences, extraction suggestions, and larger rewrites need a concrete
  problem to become actionable. A small inline implementation can be appropriate.
- A hypothetical input is not a bug unless it is reachable or required by the
  contract. Check the actual protections rather than assuming they exist.
- Existing patterns, unchanged lines, or planned follow-up work do not by
  themselves dismiss a finding. Determine whether this change introduces or
  exposes the defect and whether a real constraint accepts the risk.
- Time, compatibility, deployment order, and scope can change a recommendation.
  Cite the constraint instead of using it as a blanket reason to reject criticism.
- False factual premises and conflicting requirements can invalidate the approach.
  Report those concerns separately from code defects and distinguish evidence
  from inference.
- No findings, or only style findings, says what this review found. It does not
  prove the code is correct, especially with missing coverage or checks.

## Decide and explain

Use **Act on** for verified consequential issues, **Consider** for unresolved
consequential claims or genuine tradeoffs, **Noted** for valid non-actionable
context, and **Dismissed** for refuted or irrelevant claims. Explain the evidence
and constraint behind each disposition so the user can assess the decision.

Keep every verified consequential issue. Do not cap the findings count or suppress
an issue because only one reviewer found it. Group related symptoms to keep the
report readable. Be especially careful when rejecting security or correctness
claims; a confident majority can still be wrong.

Return the exact scope and input, usable reviewer count, runner identities when
known, verification evidence, and remaining gaps with the verdict. Incomplete
coverage or an unresolved consequential claim limits the conclusion. One usable
review remains a single review. Recommend actions without applying changes or
claiming approval to merge or publish.

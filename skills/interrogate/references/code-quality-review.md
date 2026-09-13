# Code quality review

Use this lens for concrete structural problems caused or exposed by the selected
code change. Apply it proportionally to the change and its constraints. A broader
maintainability audit is an explicitly selected mode, not an automatic rewrite
brief. Reviewers propose findings; they do not implement refactors.

## Dimensions

- **Simplification:** Identify branches, helpers, or layers whose removal would
  address a concrete source of mistakes or maintenance cost. Show why the current
  structure is harmful and consider the cost of changing it.
- **Cohesion and size:** Check whether responsibilities are tangled or navigation
  obscures a relevant invariant. File length alone is not a defect or a blocker;
  extraction must improve a specific problem rather than meet a line threshold.
- **Branching:** Trace scattered feature checks or special cases that make behavior
  inconsistent, hard to verify, or unsafe to change. A conditional is not itself
  a design flaw, and a new state machine needs a demonstrated benefit.
- **Abstractions:** Prefer direct code. Flag wrappers or generic mechanisms when
  their indirection conceals important assumptions or creates unnecessary coupling.
- **Types and boundaries:** Show where casts, fallbacks, or loose data models hide
  an actual invalid state or unclear contract. Respect the language and existing
  trust boundaries instead of prescribing one type-system pattern everywhere.
- **Placement and reuse:** Identify a canonical layer or existing helper only when
  it fits the required semantics. Explain the concrete cost of the current choice.
- **Orchestration and atomicity:** Trace unsafe partial updates or shared-state
  races. Suggest concurrency only for genuinely independent work; correctness,
  resource limits, and operational constraints can justify serial execution.

## Output and judgment

Prioritize impact and evidence. For each structural concern, name the affected
code, the problem for this change, and the constraint or future edit that makes it
matter. In a broad audit, separate optional opportunities from actionable defects.
A more elegant alternative alone is not a blocker. Retain every verified
consequential issue, summarize related symptoms together, and skip cosmetic
padding. Be direct and specific without making the review an unsolicited redesign.

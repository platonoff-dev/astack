### Feature

**You own the design. Plan, review, verify.** Delegate implementation where delegation is available. Stay in the lead.

1. Load and follow [how](../../../how/SKILL.md) over the affected subsystem.
2. Load and follow the astack `architect` skill for parallel design exploration. Skipping stays in the list as `architect skipped: <reason>`. Do not fold the design decision silently into implementation.
3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
   - **Blocking first steps.** Gates run before fan-out.
   - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
   - **Shared mutable state.** Default to splitting the target ([Separate Before Serializing Shared State](../../../principles/references/separate-before-serializing-shared-state/reference.md)). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.
4. Name the data shape and its organizing structure before anyone writes logic ([Model the Domain](../../../principles/references/model-the-domain/reference.md)): a state machine over scattered booleans, a table or registry over branching, a typed model over repeated shape assumptions. Delegate code-writing with a specific scope (file paths, the named shape and structure, success criteria) per the Delegation paragraph in `SKILL.md`, and review the diff yourself. When the implementation admits multiple valid shapes (error handling, abstraction layer, test structure), delegate through [arena](../../../arena/SKILL.md) instead so the runners surface the alternatives and the judge guards the pick. The gain is review separation, not lines saved, so [Laziness Protocol](../../../principles/references/laziness-protocol/reference.md) does not waive it. When delegation is unavailable, write the code yourself, review the diff in a separate pass against the scope, and say that the separation was lost. Keep only comments that explain a non-obvious why. Make surgical edits. Port shared-primitive improvements to all consumers and verify each. Commit liberally.
5. Verify on the surface the project's instructions name. "Inconclusive" or wrong-surface is not a pass. Flag it.
6. Rebase into small, ordered commits, building, verifying, and committing each unit before the next ([Sequence Verifiable Units](../../../principles/references/sequence-verifiable-units/reference.md)). Split follow-ups into their own changes.
7. If the design is contested, load and follow [interrogate](../../../interrogate/SKILL.md) before shipping.
8. Run **Delivering a change** (`delivering-a-change.md`).

Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline. That owner fans out internally after the blocking phase. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries. Start a fresh owner with consolidated scope rather than chaining interruptions onto a running one.

**Reply:** what you built, what you chose and why, the throughput checkpoint, open decisions. Tables for design alternatives.

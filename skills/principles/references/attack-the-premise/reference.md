# Attack the Premise

When two or more fixes that share one premise have failed the same gate, suspect the premise, not the fixes.

**Why:** Each failure under a shared premise is evidence about the premise.

**Pattern:**
- **Write the premise down.** The premise is the one sentence that every failed fix assumed.
- **Take a census before the next fix.** Count the imbalance per actor. Record both the amount per actor and each actor's share, over a stated observation window. Write the census as a rerunnable script per [Build the Lever](../build-the-lever/reference.md).
- **Read the skew.** If the same few actors hold most of the imbalance on repeated runs, investigate whether a persistent role assignment explains the skew. Test that explanation against the evidence. That assignment is the next "why" per [Fix Root Causes](../fix-root-causes/reference.md).
- **When role assignment is confirmed as the cause, prefer removing the asymmetry instead of compensating for it**, per the [Laziness Protocol](../laziness-protocol/reference.md). Rotate the role between actors, randomize the assignment, or move the role, so that no actor holds it on every run. Check that the change preserves required ownership, ordering, and locality constraints, then rerun the census and the failing gate. A return path, a shared pool, a batched hand-off, or a periodic rebalance may be appropriate when the role assignment is required; compare that cost with changing the assignment.

**Stop:**
- Do not start the next fix before the premise is written down and the census exists.
- If the census is even across actors, it does not support persistent actor skew in that observation window. Check that the measurement captures the failure; then test other implications of the premise or investigate other causes. Keep the census as evidence.

This principle is distinct from [Redesign from First Principles](../redesign-from-first-principles/reference.md), which rebuilds a design around a new requirement. It questions a fact the current design assumes.

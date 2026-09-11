---
name: principle-boundary-discipline
description: "Apply when wiring validation, error handling, or framework adapters. Concentrate guards at system boundaries (CLI, config, network, external APIs); trust internal types and keep business logic in pure functions."
disable-model-invocation: true
---

# Boundary Discipline

Place input validation, type narrowing, and external-error translation at system boundaries. Trust internal values only for invariants established at entry and preserved by internal code. Business logic lives in pure functions. The shell is thin and mechanical.

**Why:** Scattered validation is noisy, redundant, and gives a false sense of safety. Keep logic out of framework wiring so it can be tested without the framework.

**The pattern:**
- **At boundaries** (CLI args, config files, external APIs, network protocols): validate, return errors, handle defensively.
- **Inside the system:** use domain types and propagate errors without repeating checks for established invariants. Keep domain-invariant checks, authorization, and recovery where their state and responsibility live. Types alone do not prove invariants that casts, alternate constructors, or mutation can bypass.
- **Across the boundary.** Expose domain concepts, not the boundary's private representation. Keep boundary-specific adaptation at the edge and business policy in the core.

**Applications:**

Validation and error handling:
- Validate config at parse time (the boundary), not inside business logic
- Parse raw data into domain types at the boundary
- Do not re-export transport, storage, framework, or wire types through the public surface
- No redundant nil checks deep in call chains if the boundary already validated

Code organization:
- Business logic in pure functions with no framework dependencies
- Parse functions: pure transforms from raw bytes to typed state
- Prompt construction: structured state in, string out
- Scoring and assessment: pure transforms from state to results

**The tests:**
- "Was this invariant established at a boundary, and can every path here be shown to preserve it?" Remove a repeated check only when the answer is yes; otherwise retain it or establish the missing boundary.
- "Can this be a pure function that the shell just calls?" If yes, extract it.

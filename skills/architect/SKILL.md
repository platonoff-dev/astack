---
name: architect
description: "Sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in. Use when explicitly asked to architect or design a change whose shape would otherwise be locked in by jumping to code."
disable-model-invocation: true
---

# Architect

Design before implementing. Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Compare structurally distinct candidate designs, synthesize one, then fill in code against the chosen sketch. If implementation proves the sketch wrong, throw it out and redesign.

Read the active project's `CLAUDE.md` / `AGENTS.md` and the [shared execution and result contract](../../references/agent-workflows.md). Keep a short plan for Ground, Sketch, Agree, Implement, and Scrap using the available planning tool or a local note.

For design decisions this skill does not name, consult the [principles registry](../principles/SKILL.md) and read only the relevant references. The principle references linked below are required guidance at their phase even when the registry selects nothing else.

## Phase A: Ground the problem

Build a real mental model of every system the new code touches. Run the [how](../how/SKILL.md) skill over the relevant subsystems.

Naming a file isn't grounding. Produce the traced model `how` prescribes. If the design redefines ownership or layering, also run the [why](../why/SKILL.md) skill on the existing shape so the rationale becomes a constraint, not a guess.

Skip Phase A only when the work is genuinely greenfield with no surrounding system to integrate.

## Phase B: Sketch

Run the [arena](../arena/SKILL.md) skill with the design-sketch task and the Phase A grounding artifacts. Include the full text of [`references/runner-prompt.md`](references/runner-prompt.md) in each candidate's brief, with the resolved absolute paths it asks for. Each candidate produces a design package shaped per [`references/rationale-template.md`](references/rationale-template.md).

Use the harness's native delegation under the shared contract. Omit model and effort overrides unless the user selected an available, exact value; repeated runs of one model are independent attempts, not model diversity. When fresh delegation is unavailable, fall back to sequential parent-only sketching: write each candidate to its own output location before starting the next, do not reread an earlier candidate while drafting a later one, and record in the synthesis decision that the candidates shared one context. That fallback loses candidate independence and the fresh judge; name that loss instead of presenting the result as a completed arena.

Design it twice. Require at least two structurally distinct candidates before synthesis, even when the first looks sufficient. Whole-shape alternatives, not point fixes inside one shape. A second flavor of the first shape does not count.

Screen every candidate against [`references/design-red-flags.md`](references/design-red-flags.md) before synthesis. Reject or revise shallow modules, information leakage, temporal decomposition, and pass-through methods.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Synthesis returns one design package. The synthesis decision populates the rationale's "Synthesis decision" section, including any fallback or missing judge.

## Phase C: Agree (opt-in)

Default: proceed directly to implementation with the synthesized design. No human checkpoint.

Opt in to a checkpoint when the invoker explicitly asks: "architect with checkpoint," "stop and show me before implementing," or similar. Then surface the synthesized design and pause for sign-off.

The synthesis can ship as its own commit either way, as the "scaffold first" mode of [Foundational Thinking](../principles/references/foundational-thinking/reference.md). Planned and scoped breakage during fill-in is fine, per [Outcome-Oriented Execution](../principles/references/outcome-oriented-execution/reference.md). Committing still needs the authorization the active project requires. For adversarial pressure on the design before implementing, run the [interrogate](../interrogate/SKILL.md) skill on the synthesized sketch, choosing a design rubric explicitly since its default rubric reviews code.

If the human pushes back on the shape (in a checkpoint or after the fact), treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code.

## Phase D: Implement against the sketch

Replace `not implemented` bodies with code, pseudocode with logic. The synthesized sketch is the contract.

Deviations from the sketch are signal worth surfacing, not friction to absorb silently. If a function needs a parameter the sketch didn't anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the sketch out. Don't bolt fixes onto a wrong design, per [Redesign From First Principles](../principles/references/redesign-from-first-principles/reference.md) and [Fix Root Causes](../principles/references/fix-root-causes/reference.md).

The signal is a *pattern*, not single instances. Tells:

- The same shape of workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases that all need special-case branches.
- Types that need escape hatches (`any`, casts, optional fields always set in practice) to compile.
- The "we need a lock" reflex when the sketch said the state wasn't shared.
- Callers having to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations of the same shape across the implementation.

Use judgment. A few edge cases don't condemn an architecture. Some problems are legitimately complex. Complexity in the data is not complexity in the design.

When you scrap:

1. Re-run the [how](../how/SKILL.md) skill over what's been built.
2. Redesign as if the new constraints had been day-one assumptions, per Redesign From First Principles.
3. Subtract before adding, per [Subtract Before You Add](../principles/references/subtract-before-you-add/reference.md). The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and re-run the sketch comparison.

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per [`references/rationale-template.md`](references/rationale-template.md), including the usage sketch and the synthesis decision. Report which candidates were independent, which runner produced each when known (otherwise `unknown`), whether a fresh judge ran, and any phase that was skipped or fell back.

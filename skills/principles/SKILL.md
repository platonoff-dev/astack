---
name: principles
description: Select and read relevant engineering principles when making design, implementation, debugging, refactoring, or verification decisions. Use when the task presents a concrete tradeoff about data shape, ownership, complexity, work sequencing, or evidence of correctness.
---

# Principles

Use this registry to find guidance for the decision in front of you. The full
principles are ordinary references, not separate skills or commands.

1. Identify the actual decision and choose the smallest relevant set below.
   Selecting none is valid when the task is routine, the decision is already
   settled, or no criterion fits. A broad topic match alone is not enough.
2. Read the selected reference files before applying them. The summaries here
   are selection aids, not substitutes for the full guidance. When a workflow
   requires a named principle, read it even if no optional principle is useful.
3. Apply each principle within its stated conditions, the user's scope, and the
   active project's `CLAUDE.md` / `AGENTS.md`. A principle does not authorize
   additional work, delegation, persistent memory, or external actions.
4. Reconsider the selection when new failure evidence, changed requirements,
   ownership or rollout constraints, or a verification decision changes what is
   relevant. Do not repeat this process for every tool call or reread unchanged
   guidance already available in context.

Related-principle links inside a reference are optional leads, not instructions
to recursively load the collection. Read another file only if its own criterion
fits the current decision or the active workflow explicitly requires it. If
delegating, supply resolved absolute paths or full selected guidance in the
worker's brief; do not assume it inherits the parent's reads or working directory.

Choose between nearby principles by the decision they address. Simplifying a
change, reducing the effort to trace code, and ordering removals are different
questions; do not load all three merely because the task is a refactor. During
migrations, distinguish planned internal edits from verifiable delivery units:
temporary breakage may fit inside a scoped, reversible unit, while each verified
or independently landed unit must pass its required checks.

| Principle | Read when |
|---|---|
| [Attack the Premise](references/attack-the-premise/reference.md) | Several fixes sharing one premise fail the same gate and actor or load distribution may explain it; decide what census would test that premise. |
| [Boundary Discipline](references/boundary-discipline/reference.md) | Deciding where parsing, validation, error translation, or business policy belongs, or whether an internal check is redundant. |
| [Build the Lever](references/build-the-lever/reference.md) | Nontrivial edits, analyses, or checks need a rerunnable tool or recipe that makes the work reviewable; first assess existing tools. |
| [Encode Lessons in Structure](references/encode-lessons-in-structure/reference.md) | A repeated correction or instruction suggests a durable type, lint, metadata, runtime check, or other structural enforcement. |
| [Experience First](references/experience-first/reference.md) | Product, UX, library, or feature-scope tradeoffs require choosing the experience of people who use or maintain the result. |
| [Fix Root Causes](references/fix-root-causes/reference.md) | Debugging a symptom and deciding which cause to reproduce, instrument, or fix instead of masking invalid state. |
| [Foundational Thinking](references/foundational-thinking/reference.md) | Choosing core data structures, access patterns, or shared scaffolding that will shape subsequent implementation. |
| [Guard the Context Window](references/guard-the-context-window/reference.md) | Large inputs, repeated reads, or long phases threaten the context needed for a decision; choose selective reads or permitted delegation. |
| [Laziness Protocol](references/laziness-protocol/reference.md) | Evaluating a proposed abstraction, pass-through layer, duplicated decision, or signal threading and seeking a smaller change. |
| [Migrate Callers Then Delete Legacy APIs](references/migrate-callers-then-delete-legacy-apis/reference.md) | Replacing an internal API and deciding how to inventory callers and remove the old path when coordinated breaking changes are acceptable. |
| [Minimize Reader Load](references/minimize-reader-load/reference.md) | Code is difficult to understand because readers must trace indirection or retain hidden or mutable state; decide which cost to reduce. |
| [Model the Domain](references/model-the-domain/reference.md) | Repeated conditions, shape assumptions, or state transitions suggest the domain needs a better structure or owner. |
| [Never Block on the Human](references/never-block-on-the-human/reference.md) | Deciding whether a reversible next step is already authorized or whether consequential ambiguity or an explicit approval gate needs user input. |
| [Outcome-Oriented Execution](references/outcome-oriented-execution/reference.md) | Planning a rewrite or migration and deciding which temporary states are acceptable within explicit, reversible phase boundaries. |
| [Prove It Works](references/prove-it-works/reference.md) | Choosing evidence for a completion or correctness claim, especially when builds, proxies, or worker reports may miss the actual behavior. |
| [Redesign From First Principles](references/redesign-from-first-principles/reference.md) | A new requirement strains an existing design; decide how the design would change if that requirement had existed from the start. |
| [Separate Before Serializing Shared State](references/separate-before-serializing-shared-state/reference.md) | Concurrent actors may mutate the same state; decide whether ownership can be separated or one canonical object needs structural coordination. |
| [Sequence Verifiable Units](references/sequence-verifiable-units/reference.md) | Ordering a sweep, migration, or delivery into units with meaningful checks and deciding where those verification boundaries belong. |
| [Subtract Before You Add](references/subtract-before-you-add/reference.md) | Sequencing an addition or rewrite and deciding which dead code, obsolete paths, or unnecessary complexity should be removed first. |
| [Type System Discipline](references/type-system-discipline/reference.md) | Designing typed states, signatures, or boundary parsers where invalid combinations, mixed semantic primitives, or missing variants cause risk. |

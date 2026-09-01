# Refactor

Use this playbook when a named structural problem matters and behavior should
remain unchanged.

## Work

1. State the behavior contract and the structural cost to remove. Pin current
   behavior with existing tests, a characterization test, snapshot, replay, or
   equivalence check before moving structure.
2. Name the target shape and how it reduces branches, invalid states, repeated
   knowledge, or reader effort. Do not add an abstraction without a concrete
   job.
3. Delete dead or redundant structure first. Move in small steps that keep the
   behavior pin green.
4. Migrate callers and remove the obsolete path in the same coherent change
   unless an agreed compatibility period requires both.
5. Prove equivalence on the relevant artifact. Type checks and lint alone do not
   establish unchanged behavior. Confirm that the final diff removes the named
   structural cost.

## Leave the playbook

- Route to `investigation` when the current contract or callers are unknown.
- Route to `bug-fix` when the work must correct established behavior.
- Route to `feature` when the target intentionally changes behavior.
- Route to `split` for independently verifiable migrations or structural waves.

Completion evidence includes the behavior pin, equivalence result, deleted old
path, and the concrete reduction in structural cost.

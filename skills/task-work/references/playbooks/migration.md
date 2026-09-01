# Migration

Use this playbook when current and target states, affected consumers or data,
compatibility requirements, and recovery expectations are known.

## Work

1. Inventory the old state, target state, consumers, stored data, and ownership
   boundaries. Record invariants that must hold throughout the transition.
2. Define stages with entry checks, exit checks, and a recovery action. Keep old
   and new paths together only for an agreed compatibility or rollout need.
3. Test conversion, compatibility, retries, partial failure, and recovery on the
   closest safe fixture. Use a dry run or reversible sample when data can change.
4. Execute only stages authorized for the current environment. Validate data and
   consumers after each consequential stage.
5. Retire the old state when the brief requires it and evidence shows remaining
   consumers no longer need it. Record anything deliberately left behind.

## Leave the playbook

- Route to `investigation` when consumers, data shape, or recovery behavior is
  unknown.
- Route to `decision` when compatibility duration, risk acceptance, or rollout
  policy needs an owner.
- Route to `split` when stages have independent delivery, rollback, or owners.
- Route a conversion defect to `bug-fix` while preserving the migration state.

Completion evidence names the transition and recovery checks, consumer and data
validation, executed stage, and old state still present.

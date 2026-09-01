# Feature

Use this playbook when desired scenarios, scope, compatibility, and material
product constraints are settled.

## Work

1. Map each agreed scenario to an observable check. Include relevant failure
   behavior and existing behavior that must survive.
2. Inspect the current seams, callers, data shapes, and repository conventions.
   Choose a design only as deep as the feature needs.
3. Build the smallest complete behavior slice. Keep independent work separate
   only when its files, inputs, and checks are genuinely independent.
4. Exercise the feature through the interface named by the task. Run focused
   automated checks and any required end-to-end or manual check.
5. Inspect the final diff for compatibility breaks, speculative flexibility,
   and changes outside the agreed scenarios.

## Leave the playbook

- Route to `decision` when product behavior, compatibility, or rollout policy
  needs human intent.
- Route to `investigation` when a technical unknown blocks a sound design.
- Route to `split` when outcomes can be verified, delivered, or reverted
  independently.
- Route a discovered existing defect to `bug-fix`; do not hide it inside the
  feature unless the feature's outcome requires the same change.

Completion evidence names the scenarios exercised, preserved behavior checked,
and failures or environments that were not tested.

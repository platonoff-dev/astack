# Split

Use this playbook when one task contains outcomes that can be verified,
delivered, prioritized, reverted, or owned independently.

## Work

1. Name the parent outcome and why one route cannot handle it coherently.
2. Define each child by its delivered outcome, observable completion check, and
   dependencies. Prefer complete behavior slices over file or layer buckets.
3. Remove overlap, cycles, and children that exist only because the diff may be
   large. Keep tightly coupled steps in one child.
4. Assign a playbook and modifiers to every child. Preserve shared constraints
   and evidence by reference instead of copying a stale parent brief.
5. State ordering and which children can proceed independently. Create tracker
   items only with existing or explicit authorization.

## Leave the playbook

The split is complete when each child has a supported route, scope, completion
check, and real dependencies. Route unclear decomposition to `investigation`.
Route priority, ownership, or product-boundary questions to `decision`.

The parent remains the record of the broader outcome. Do not report it complete
because child briefs exist.

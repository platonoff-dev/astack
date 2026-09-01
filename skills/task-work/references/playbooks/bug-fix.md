# Bug fix

Use this playbook when current evidence establishes intended behavior, observed
behavior, and the affected conditions.

## Work

1. Reproduce the failure on the closest affordable path. If a local regression
   check is practical, make it fail for the reported reason before editing.
2. Trace the mechanism far enough to explain why the failure occurs. Test
   competing hypotheses instead of stacking changes that might help.
3. Make the smallest coherent change the evidence supports. Remove probes or
   abandoned attempts that no longer justify code.
4. Run the original reproduction on the same path. Add regression protection
   where it distinguishes the faulty behavior from the required behavior.
5. Run nearby checks that the change can invalidate. Inspect the final diff for
   unrelated cleanup or behavior changes.

## Leave the playbook

- Route to `investigation` when the failure or mechanism remains unproved.
- Route to `decision` when intended behavior or an accepted tradeoff is unclear.
- Route to `feature` when the requested result adds behavior rather than repairs
  an established contract.
- Route to `split` when separate failures need independent delivery or rollback.

Completion evidence includes the original failure passing on the relevant path,
the final regression result when one was practical, and any limits on matching
the reported environment.

# Performance

Use this playbook when the task names a representative workload, metric, target
or comparison, and acceptable correctness and resource tradeoffs.

## Work

1. Record the baseline under stated conditions. Keep the fixture, environment,
   warmup, sample count, and measurement method comparable.
2. Profile or trace before choosing a fix. Form hypotheses from the dominant
   measured cost and the relevant code path.
3. Change one justified mechanism at a time. Revert attempts that do not improve
   the target or that spend an unaccepted resource.
4. Capture the post-change measurement under the same conditions. Report raw
   values and the delta; flag noisy or inconclusive results.
5. Run correctness and resource checks that the optimization can invalidate.
   Inspect the diff for complexity that the measured gain does not earn.

## Leave the playbook

- Route to `investigation` when no representative baseline or dominant cost is
  established.
- Route to `decision` when the target or latency, memory, load, cost, and
  correctness tradeoffs need an owner.
- Route to `bug-fix` when the measured problem is an established correctness
  failure.
- Route to `split` when independent bottlenecks need separate changes.

Completion evidence includes baseline and post-change numbers, conditions,
correctness checks, resource tradeoffs, and measurement limits.

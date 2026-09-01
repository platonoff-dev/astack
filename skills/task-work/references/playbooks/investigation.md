# Investigation

Use this playbook when a bounded technical question blocks a reliable change,
decision, split, or no-change conclusion. Production code is optional.

## Work

1. State the question and what each plausible answer would change. Narrow broad
   uncertainty to the first question that separates the routes.
2. Inspect the original report, relevant code and history, configuration, and
   available runtime evidence. Distinguish observed facts from hypotheses.
3. Choose the cheapest check that can rule out a serious hypothesis. Reproduce,
   trace, profile, instrument, compare revisions, or build a disposable probe as
   the question requires. A setup failure does not reproduce the reported
   behavior.
4. Record the check, result, source or receipt, and limits. Remove temporary
   instrumentation unless it belongs in the next route.
5. Stop when evidence supports an answer, exposes a human decision, or leaves a
   precise blocker that available tools cannot cross.

## Leave the playbook

- Route to `bug-fix`, `feature`, `refactor`, `performance`, or `migration` when
  its entry facts and completion checks are supported.
- Route to `decision` when product intent, risk acceptance, authorization, or an
  unavailable owner's knowledge blocks useful work.
- Route to `split` when the evidence reveals independently verifiable outcomes.
- Route to `no-change` when current evidence supports that disposition.

Report the supported answer, the evidence that separates it from the rejected
hypotheses, its limits, and the next playbook.

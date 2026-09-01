# No change

Use this playbook when inspected evidence supports that the requested product
change is unnecessary, already present, duplicated, superseded, deliberately
declined, or belongs to support or configuration.

## Work

1. Name the exact reason and inspect the current artifact or state that proves
   it. A failed reproduction alone does not establish no change.
2. Check the relevant revision, environment, duplicate, replacement, release,
   or configuration path. Record limits and any state that remains unverified.
3. Confirm that no required outcome remains. Remove temporary probes without
   touching unrelated work.
4. Draft the disposition with evidence. Publish or close tracker work only with
   existing or explicit authorization.

## Leave the playbook

- Route to `investigation` when the reason lacks enough evidence.
- Route to `decision` when an owner must choose to decline or supersede work.
- Route to a change playbook when current evidence shows an unmet outcome.

Completion evidence names the reason, source, inspected revision or environment,
and any operational follow-up that remains. No-change does not mean deployed,
closed, or communicated unless those actions were separately completed.

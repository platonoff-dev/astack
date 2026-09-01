# 006: Make `main` the generic work entrypoint

- **Date:** 2026-09-01
- **Verdict:** adopt
- **Touches:** `skills/main/`, `skills/task-intake/`, both plugin manifests,
  README

## Problem

`work-on-task` presented the router as a second step after `task-intake`. The
intended use is one front door for new and resumed work, with intake used when
the current evidence does not yet support a route. Requiring the caller to pick
the intake or work skill first defeats that boundary.

Decision 005 avoided a broad name because it might match unrelated requests.
That tradeoff no longer fits the intended role. Broad discovery is deliberate
for the primary work entrypoint; focused skills can still match their own work.

## Decision

Rename `work-on-task` to `main`, including its directory and frontmatter. `main`
uses a current evidence-backed brief when one names a playbook. It runs
`task-intake` first when the request is new, stale, contradictory, or unclear.
An intake-only request stops with the brief. A request for the work itself
continues through the selected playbook.

Keep the empty-playbook rule from decision 005 unchanged. This decision adds no
playbook procedure and makes no route-specific claims. All nine placeholder
files move with the skill and remain empty.

## Validation

The playbook check must still map all nine intake routes, report zero adopted
playbooks, and reject content in a placeholder. Both skill validators, the
task-intake regressions, vendor check, and plugin validators run after the
rename. The plugin version moves to 0.7.0 so both harnesses can load the new
skill name after reinstalling.

## What would reverse this

Narrow the description if `main` repeatedly steals requests from a more focused
skill. Do not restore a two-step entrypoint merely because the name is broad;
first test whether discovery wording can preserve the intended front door.

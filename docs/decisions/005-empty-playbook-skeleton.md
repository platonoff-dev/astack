# 005: Keep task playbooks empty until each has its own decision

- **Date:** 2026-09-01
- **Verdict:** adopt skeleton; defer every playbook body
- **Touches:** `skills/work-on-task/`, `skills/task-intake/`, both plugin
  manifests, README

## Problem

Decision 004 adopted nine short playbook bodies in one pass. Their shared shape
looked tidy, but each job needs separate research and choices about entry facts,
proof, transitions, permissions, and target-repository interaction. A generic
synthesis would turn plausible guidance into project policy before any playbook
had been tested on its own work.

The intake checker also encoded route-specific requirements for evidence,
questions, completion checks, and splits. Those rules made the empty route names
look more settled than they were.

## Decision

Keep the nine route files and empty every one. Rename the router from
`task-work` to `work-on-task`. `work-on-task` is more natural as an action while
remaining specific enough to avoid the broad matching risk of `work-on`.

The router may preserve the route table and common safeguards. It must say that
an empty file is not an adopted procedure, must not invent its contents, and
must not claim that a playbook was followed. Ordinary task work can still use
the user's request and target repository instructions.

Remove route-specific policy from the intake checker. It continues to validate
the brief's core structure, reserved route name, modifier syntax, evidence
receipts, and legacy-field rejection.

`work-on-task/scripts/check_playbooks.py` owns an explicit
`ADOPTED_PLAYBOOKS` set. It is empty in this decision. The check fails when a
placeholder contains text or an adopted playbook is empty.

## Adding the first playbook

Treat each playbook as its own component decision. Research its real failure,
compare prior art, write and trial the smallest candidate, then add only that
route to `ADOPTED_PLAYBOOKS`. Update the intake contract only for requirements
that the playbook decision justifies. Bump both plugin manifests and reinstall.

## Validation

Twelve brief-checker regressions cover only the generic contract. The route
check confirms nine mapped routes, zero adopted playbooks, and nine empty files.
The plugin version moves to 0.6.0.

## What would reverse this

Remove a placeholder route if its name causes repeated misclassification before
its playbook is designed. Adopt content only after a route-specific trial shows
that the instructions improve a real task or prevent a material failure.

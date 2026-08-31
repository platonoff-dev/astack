# 002 — Should task intake check a ticket before planning implementation?

- **Date:** 2026-08-31
- **Verdict:** adopt
- **Touches:** `skills/task-intake/`, both plugin manifests, README, AGENTS.md

## Failure it prevents

Anatolii reports poorly shaped, aging Jira tasks whose excessive implementation
detail can steer agents toward the wrong work. Rewriting that detail more
clearly would preserve the mistake. The agent needs to distinguish intent,
observations, constraints, and proposed solutions before planning.

## Sources read

- `mattpocock-skills` @ a97b87386667 — `skills/engineering/triage/SKILL.md`,
  `triage/AGENT-BRIEF.md`, `setup-matt-pocock-skills/SKILL.md` and its tracker
  references, `to-tickets/SKILL.md`, `diagnosing-bugs/SKILL.md`, `ask-matt/SKILL.md`
  under `skills/engineering/`.
- `pstack` @ fd878692de15 —
  `pstack/automations/benny/skills/triage-issue-reports/SKILL.md` and
  `pstack/skills/poteto-mode/playbooks/{bug-fix,perf-issue,refactoring}.md`.
- Not evaluated end to end: either upstream automation, live tracker writes,
  or implicit skill selection.

## Mechanism

Adopt the constraints in our own words. Inspect consequential claims and safe
probes, preserve human blockers, and produce one Markdown brief with a justified
next action. Proposed solutions remain hypotheses. Neither failed reproduction
nor the presence of code proves resolution. Recheck material facts on pickup.

The entry is 495 words. Branch references hold evidence inspection, work types,
brief format, and a tracker contract. A standard-library checker rejects missing
structural evidence and action-specific content; it warns above 600 words.
Twelve regression checks exercise those rules. A passing checker cannot verify
the truth or sufficiency of evidence.

## Fit

One skill serves both harnesses without a subagent installer or mandatory tracker.
Local Markdown works immediately; other trackers map operations to existing
tools. No provider SDK, new service, source enrollment, or vendored copy. The
plugin moves to 0.3.0; Codex display metadata now describes real shipped skills,
resolving the documented validation failure.

## Trial

An independent agent triaged that real validation failure before the packaging
change. It reproduced the missing `interface` error, distinguished validation
from runtime behavior, and preserved the README's intentional deferral as a
decision question. Its 342-word brief passed on the first check; wrapped evidence
also passed. It changed no repository files or tracker state. This is an initial
local trial, not evidence that every work type or Jira integration works.

## What would reverse this

Revisit if intake routinely invents certainty, misses material constraints,
requires interviews for ordinary choices, or costs more than it saves on clear
tasks. Trial a real misleading Jira ticket before expanding tracker automation.

---
name: playbook
description: "Route a task to one rigorous, project-first playbook. Matches investigation, bug fix, feature, refactoring, perf issue, delivering a change, session pickup, or pause safely; puts the project's mandatory steps ahead of the playbook's; runs the astack skills each step names. Use for /playbook, 'run the playbook', or when a task needs a rigorous routed workflow."
disable-model-invocation: true
---

# Playbook

**You own the task. The project owns its delivery flow. The playbook adds
rigor.**

## Project instructions come first

- Before matching anything, read the active project's `CLAUDE.md` /
  `AGENTS.md` and the files they point at.
- Merge the project's mandatory steps into the list at the phase where each
  belongs (before code, before review, before merge). Where the project and
  the playbook both have a step for one phase, the project's step comes first.
  Typical project steps: a ticket before any code, a root-cause investigation
  before a fix, reproducing on a named test server, tests before
  implementation, a remote test suite before review, change request
  conventions, a review bot that must pass.
- A playbook step the project already mandates collapses into the project's
  step; keep it as `covered: <project step>`.
- Where a playbook line genuinely conflicts with a project rule, the project
  rule wins and the playbook line stays in the list as
  `superseded: <project rule>`. Use `superseded:` only for real conflicts, not
  for steps the project merely restates.
- A step you choose not to do stays in the list with a one-line
  `skip: <reason>`.
- The playbook never defines the project's delivery flow. It adds the checks
  the project left implicit.

## Match

Match the task to one playbook. Open its file and read it in full before you
start.

| Playbook | For |
|---|---|
| [Investigation](references/playbooks/investigation.md) | A read-only question. How does X work, why was Y built this way, are we sure about Z, X or Y. |
| [Bug fix](references/playbooks/bug-fix.md) | A reported defect to reproduce, root-cause, and fix with runtime evidence. |
| [Perf issue](references/playbooks/perf-issue.md) | A measured slowness to trace and improve against a baseline. |
| [Feature](references/playbooks/feature.md) | New or changed behavior, built from a named data shape. |
| [Refactoring](references/playbooks/refactoring.md) | A behavior-preserving change to structure or shape: rename, extract, inline, dedupe, move. |
| [Session pickup](references/playbooks/session-pickup.md) | Resuming or taking over prior in-flight work from notes, git state, or session history. |
| [Pause safely](references/playbooks/pause-safely.md) | Suspending in-flight work cleanly so a cold-start session can resume it. |
| [Delivering a change](references/playbooks/delivering-a-change.md) | The end of every playbook that changes code: commits, description, review. |

If no playbook fits, say so in one line and proceed without one. Do not invent
a playbook or stretch the nearest one. A one-line rename, a config tweak, or a
question the conversation already answers needs no playbook.

## Scope of the mode

The playbook governs the task it was invoked for. A casual follow-up, or the
user saying to drop the playbook, ends it; a new task needs a new match. Large
multi-phase work runs each phase through its own match and keeps a
show-me-your-work trail across phases.

## Run

- Copy the matched playbook's steps verbatim into the harness's planning or
  todo tool, merged with the project's mandatory steps as above and before any
  task-specific items.
- When no such tool exists, write the same list to a note in the scratch
  location below and update it as you go.
- Mark steps done as you finish them, not at the end.
- For a long, autonomous, or multi-phase run, load and follow the astack
  [show-me-your-work](../show-me-your-work/SKILL.md) skill and start its trail
  before the first step; log each finished step as a row.
- Pause and confirm before any irreversible or outward-facing write, whatever
  the playbook says: force-push to a shared branch, a deploy, data deletion, a
  message to other people.

An example list for a bug fix in an invented project whose instructions
require a ticket before code, a failing test before the fix, and a fixed merge
request template:

```
1. Reference ticket PROJ-123 before editing (project)
2. Reproduce on the surface the project names (Bug fix step 1)
3. Write the failing regression test first (project)
   Stage the failing repro before the fix (Bug fix step 5)
   covered: project's failing-test-first rule
4. Use the Why/Scope/Tradeoffs/Blast Radius/Verification body
   superseded: project MR template with ## Summary / ## Test plan
5. Load tdd for the failing-test cadence
   skip: the repro needs the shared test server, no cheap local path
6. Run Delivering a change: rebase into ordered commits, fill the template
```

## Route to skills

Playbook steps name astack skills. They are explicit-only, so the harness will
not select them for you. Load each one's `SKILL.md` and follow it in full,
including its reachable references. Use a native skill invocation interface
when one is available; otherwise execute the workflow from the file. Do not
replace a skill's workflow with a summary of what it would have done.

- Understanding code or a subsystem: [how](../how/SKILL.md). Motivation and
  history: [why](../why/SKILL.md).
- Design that crosses a function boundary: the astack
  [architect](../architect/SKILL.md) skill, for parallel design exploration
  before implementing.
- Design or code bakeoffs: [arena](../arena/SKILL.md). Coverage, races, and
  partitioned exploration: [swarm](../swarm/SKILL.md). Contested design or a
  diff that needs adversarial review: [interrogate](../interrogate/SKILL.md).
- A bug with a cheap local test path: [tdd](../tdd/SKILL.md). Tests that must
  catch a regression: [harden-tests](../harden-tests/SKILL.md). What a change
  could break beyond its diff: [blast-radius](../blast-radius/SKILL.md).
- Any prose surface, including your reply: [unslop](../unslop/SKILL.md). Docs,
  change descriptions, and commit bodies:
  [technical-writing](../technical-writing/SKILL.md).
- A decision trail for long, autonomous, or multi-phase work: the astack
  [show-me-your-work](../show-me-your-work/SKILL.md) skill.
- A comprehension check before merging: [merge-brief](../merge-brief/SKILL.md).
  Learning from the run afterwards: [reflect](../reflect/SKILL.md).

## Scratch location

Use the scratch location the project's instructions allow. If none is named,
use an existing git-ignored directory inside the checkout (check with
`git check-ignore -q <dir>`); otherwise create `.audit/` and exclude it through
`.git/info/exclude` rather than editing a tracked `.gitignore`. In astack, the
location is `.local/`. Name the path in the reply. Do not commit it and do not
use a system temp directory, since a later session must find it.

## Delegation

When a step delegates work, follow the
[shared execution and result contract](../../references/agent-workflows.md).
Use the harness's native delegation interface with no model or
reasoning-effort overrides. Give each worker a fresh, self-contained brief that
includes the absolute path of this `SKILL.md` and of the matched playbook, and
tells the worker to read both before acting; it does not inherit your reads.
You own every worker's work: review the diff, verify the claim, write your own
summary. When delegation is unavailable or restricted, do the work in the
parent and say so instead of claiming independent execution.

## Comments in every diff

Keep only comments that explain a non-obvious why the code cannot show. Delete
narration such as `# step 1: load rows` and commented-out code. The assertion
or log string documents a test step. This applies to every file you produce,
including a worker's diff.

## Principles

Select principles through the [principles registry](../principles/SKILL.md),
reading the smallest relevant set. Playbook steps link the principles they
require; read those even when no optional principle fits. In your reply, name
each principle that shaped a decision and the specific choice it changed. Cite
only principles whose reference you read this session.

## Writing the reply

Write the reply through [unslop](../unslop/SKILL.md), and through
[technical-writing](../technical-writing/SKILL.md) when it is a document,
description, or commit body. Three rules hold regardless:

- Frame the result for the consumer and for the maintainer, naming what
  changes for each before any implementation detail.
- Paste verification output verbatim, labelling every other claim as measured,
  inferred, or a guess.
- Never fabricate a link, citation, or transcript reference; link only
  artifacts you produced or read this session.

Each playbook ends with a **Reply** line naming the content unique to it.

## Credit

The eight playbooks derive from the task-routing skill in Lauren Tan's (poteto)
[pstack](https://github.com/cursor/plugins) plugin, MIT licensed, rewritten
here for Claude Code and Codex and for project-first precedence. The upstream
commit, per-file mapping, and drift check are recorded in
[PROVENANCE.md](references/playbooks/PROVENANCE.md); the license is copied
alongside as [LICENSE](references/playbooks/LICENSE).

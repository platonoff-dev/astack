---
name: playbook
description: "Route a task to one rigorous, project-first playbook. Matches investigation, bug fix, feature, refactoring, perf issue, delivering a change, session pickup, or pause safely; puts the project's mandatory steps ahead of the playbook's; runs the astack skills each step names. Use for /playbook, 'run the playbook', or when a task needs a rigorous routed workflow."
disable-model-invocation: true
---

# Playbook

**You own the task. The project owns its delivery flow. The playbook adds rigor.**

## Project instructions come first

Before matching anything, read the active project's `CLAUDE.md` / `AGENTS.md` and the files they point at. Every mandatory step they name goes into your step list ahead of the playbook's steps, in the project's order. Typical examples: a ticket before any code, a root-cause investigation before a fix, reproducing on a named test server, tests before implementation, a remote test suite before review, merge request conventions, a review bot that must pass. Where a playbook line conflicts with a project rule, the project rule wins and the playbook line stays in the list as `superseded: <project rule>`. The playbook never defines the project's delivery flow. It adds the checks the project left implicit.

## Match

Match the task to one playbook. Open its file and read it in full before you start.

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

If no playbook fits, say so in one line and proceed without one. Do not invent a playbook or stretch the nearest one. A one-line rename, a config tweak, or a question the conversation already answers needs no playbook.

## Run

Copy the matched playbook's steps verbatim into the harness's planning or todo tool, after the project's mandatory steps and before any task-specific items. When no such tool exists, write the same list to a local note under the project's scratch area (in astack, `.local/tmp/`) and update it as you go. A step you choose not to do stays in the list with a one-line `skip: <reason>`. Mark steps done as you finish them, not at the end.

## Route to skills

Playbook steps name astack skills. They are explicit-only, so the harness will not select them for you. Load each one's `SKILL.md` and follow it in full, including its reachable references. Use a native skill invocation interface when one is available; otherwise execute the workflow from the file. Do not replace a skill's workflow with a summary of what it would have done.

- Understanding code or a subsystem: [how](../how/SKILL.md). Motivation and history: [why](../why/SKILL.md).
- Design that crosses a function boundary: the astack `architect` skill, for parallel design exploration before implementing.
- Design or code bakeoffs: [arena](../arena/SKILL.md). Coverage, races, and partitioned exploration: [swarm](../swarm/SKILL.md). Contested design or a diff that needs adversarial review: [interrogate](../interrogate/SKILL.md).
- A bug with a cheap local test path: [tdd](../tdd/SKILL.md). Tests that must catch a regression: [harden-tests](../harden-tests/SKILL.md). What a change could break beyond its diff: [blast-radius](../blast-radius/SKILL.md).
- Any prose surface, including your reply: [unslop](../unslop/SKILL.md). Docs, change descriptions, and commit bodies: [technical-writing](../technical-writing/SKILL.md).
- A decision trail for long, autonomous, or multi-phase work: the astack `show-me-your-work` skill.
- A comprehension check before merging: [merge-brief](../merge-brief/SKILL.md). Learning from the run afterwards: [reflect](../reflect/SKILL.md).

## Delegation

When a step delegates work, follow the [shared execution and result contract](../../references/agent-workflows.md). Use the harness's native delegation interface with no model or reasoning-effort overrides. Give each worker a fresh, self-contained brief that includes the absolute path of this `SKILL.md` and of the matched playbook, and tells the worker to read both before acting; it does not inherit your reads. You own every worker's work: review the diff, verify the claim, write your own summary. When delegation is unavailable or restricted, do the work in the parent and say so instead of claiming independent execution.

## Principles

Select principles through the [principles registry](../principles/SKILL.md), reading the smallest relevant set. Playbook steps link the principles they require; read those even when no optional principle fits. In your reply, name each principle that shaped a decision and the specific choice it changed. Cite only principles whose reference you read this session.

## Writing the reply

Write the reply through [unslop](../unslop/SKILL.md), and through [technical-writing](../technical-writing/SKILL.md) when it is a document, description, or commit body. Two rules hold regardless: frame the result for the consumer and for the maintainer, naming what changes for each before any implementation detail; and paste verification output verbatim, labelling every other claim as measured, inferred, or a guess. Each playbook ends with a **Reply** line naming the content unique to it.

## Credit

The eight playbooks derive from the task-routing skill in Lauren Tan's (poteto) [pstack](https://github.com/cursor/plugins) plugin, MIT licensed, rewritten here for Claude Code and Codex and for project-first precedence. The upstream commit, per-file mapping, and drift check are recorded in [PROVENANCE.md](references/playbooks/PROVENANCE.md); the license is copied alongside as [LICENSE](references/playbooks/LICENSE).

---
name: principle-guard-the-context-window
description: "Apply when context is filling up: large outputs, long files, repeated reads, fan-out planning. Use permitted subagents for bulk work when available; otherwise read selectively and bound outputs."
disable-model-invocation: true
---

# Guard the Context Window

The active context window is finite. Compaction can free space, but may lose detail. Every token should be worth its cost.

**Why:** Context overflow degrades reasoning quality, creates compression artifacts, and halts progress.

**Pattern:**
- **Isolate large payloads.** When the harness supports and permits delegation, give a subagent a bounded task to inspect verbose outputs, screenshots, or large documents using tools it can access. Pass only the context it needs and request a concise summary with source locations. If delegation is unavailable or disallowed, use targeted reads and bounded outputs; this reduces volume but does not provide a separate context. Inspect source evidence yourself when needed for the decision.
- **Don't read what you won't use.** Read selectively based on relevance. If a file isn't needed for the current task, skip it.
- **Keep frequently used content inline.** Keep short instructions needed on every invocation in the skill file. Keep supporting detail in linked references and load only what the task needs.
- **Size phases and cap scope.** Limit files per phase, set turn budgets, account for mechanism costs.

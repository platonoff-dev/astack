---
name: rigor-agent
description: Routing target for `/rigor` and any request for the rigor style. Resume an existing `rigor-agent` for the conversation rather than spawning a sibling. Reads the `rigor` skill's `SKILL.md` in full before any work, including its inline Principles index. Substituting a generic subagent type skips that read and drifts.
is_background: true
---

# Rigor subagent

You are operating in the rigor skill's full agent style. Read the `rigor` skill's `SKILL.md` in full before doing any work, including its inline Principles index. Navigate to a leaf `principle-*` skill whenever you apply that principle.

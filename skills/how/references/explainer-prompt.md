# Explainer Prompt Template

Use this template in the parent or an explainer subagent. Fill in the placeholders and choose the mode below. Supply the repository/source paths, applicable CLAUDE.md / AGENTS.md, original question, and any available findings. Resolve reference paths relative to the skill directory.

---

You are writing an architectural explanation for a senior engineer, grounded in the actual code.

- **Direct mode (no explorer findings):** locate the target and perform the exploration yourself. Trace the entry point, data and control flow, abstractions, boundaries, and relevant tests. Omit the Explorer Findings section. Do not claim another agent has already researched the answer.
- **Synthesis mode:** combine the supplied findings from workers or parent-run exploration passes. Check connecting edges and conflicting claims against the source; do not re-explore unrelated areas.

## Original Question

> {QUESTION}

## Explorer Findings

{EXPLORER_FINDINGS_ALL}

## Instructions

In synthesis mode, findings may overlap or contradict. Merge overlaps and check contradictions against the code. In direct mode, gather the same evidence yourself. In either mode, report unresolved gaps and distinguish static observations, observed executions, and inference. Do not describe a test as passing unless a relevant execution result was actually inspected.

Write an explanation a senior engineer unfamiliar with this area could read and walk away with a solid mental model, understanding the architecture well enough to start working in it confidently.

Use the available file search and read tools to check details. Do not assume access to missing repositories, tools, or runtime configuration. Keep the task read-only: do not edit files, execute project code, or modify external systems. Cite verified source locations for material claims; report unavailable source access.

For placement, ownership, or layering questions, explain existing boundaries and dependency directions before recommending a location. Label recommendations and their tradeoffs separately from existing behavior. Historical rationale requires explicit documentary evidence; code mechanics alone cannot establish intent.

## Output Format

Use this structure, adapted to what makes sense for the question. Not every section is needed for every question.

### Overview
1-2 paragraphs. What is this thing, what does it do, and what role does it serve in the current implementation. Someone should be able to read just this and decide whether to keep reading.

### Key Concepts
The important types, services, or abstractions needed to follow the rest. Brief definitions, not exhaustive.

### How It Works
The core of the explanation, and the longest section. Walk through the flow: what triggers it, what happens step by step, where data goes, what the decision points are.

Use prose, not pseudocode. Reference specific files and functions so the reader knows where to look, but don't dump large code blocks unless a snippet is essential to a point.

When the flow involves multiple components talking to each other, or data transforming through stages, include a diagram. Use mermaid (```mermaid) for structured flows (sequence diagrams, flowcharts, component graphs) or ASCII art for simpler relationships where mermaid would be overkill. Use your judgment. A diagram should clarify, not decorate. If prose covers the flow, skip the diagram.

### Where Things Live
A brief file/directory map. Just the ones someone would need to start working here.

### Gotchas
Non-obvious things, surprising behavior, documented historical context, and pitfalls. Label runtime assumptions and unverified behavior. Skip this section if there's nothing worth calling out.

## Communication Style

- Use concrete language, not abstractions-about-abstractions
- Say "the `UserService` calls `AuthClient.refresh()`" not "the service delegates to the client"
- When something is complex, explain why it's complex. Don't just describe the complexity
- When something is simple, don't pad it out
- If there's a helpful analogy, use it. If there isn't, don't force one
- If the explorers flagged open questions or gaps, acknowledge them rather than hiding them

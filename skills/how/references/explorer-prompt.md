# Explorer Prompt Template

Use this template for each explorer or parent-run exploration angle. Fill in the placeholders.

---

You are exploring a codebase to understand how something works. Gather facts: trace code paths, read implementations, map components. A later explanation step uses these findings, so favor thoroughness and accuracy over prose.

Other explorers or parent-run passes investigate different slices of the same subsystem. Don't try to cover everything. Focus on your assigned angle and go deep.

## Question

> {QUESTION}

## Your Exploration Angle

{EXPLORATION_ANGLE}

## Exploration Instructions

Start from the repository or source paths supplied by the parent and follow its CLAUDE.md / AGENTS.md. Use available file listing, search, and read tools (for example `rg --files` and `rg` through a shell). Do not assume specific tool names. Read implementations rather than guessing from names. Keep the investigation read-only; do not execute project code or tests merely to explain it. Record the inspected revision and relevant local changes when available.

Follow this pattern:
1. **Find the entry point.** What triggers this behavior? A user action, an API call, a scheduled job? Find where it starts.
2. **Trace the flow.** Follow the call chain from the entry point. Read each function. Understand what data flows through and how it transforms.
3. **Map the key abstractions.** What types, interfaces, services, or classes are central? Read their definitions. Explain their current responsibility. Do not infer historical motivation without documentary evidence.
4. **Find the boundaries.** Where does this subsystem interface with others? What goes in, what comes out?
5. **Look for the non-obvious.** Anything surprising? Anything that looks like a historical artifact? Anything a newcomer would misunderstand?

Keep exploring until you can describe the full picture without hand-waving. If you hit a part you can't trace, say so explicitly. "I couldn't determine how X connects to Y" is better than making something up.

## Output

Return your findings in this structure. Be factual and specific. Reference exact file paths, function names, type names, and line numbers where relevant.

### Components Found
The key types, services, classes, and abstractions. For each: name, file path, and a one-sentence description of what it does.

### Flow
The execution flow step by step. For each step: what function/method runs, what file it's in, what it does, what it calls next. Include the data that flows between steps.

### Files Read
Every file you read during exploration, so the explainer can reference them.

### Boundaries
Where this subsystem connects to other parts of the codebase. The inputs and outputs.

### Non-Obvious Things
Anything surprising or easy to get wrong; include historical motivation only with a documentary citation. Things that look like they should work one way but work another.

### Open Questions
Anything you couldn't fully trace or understand, including unavailable dependencies, dynamic dispatch, configuration, and unverified runtime behavior. Name cross-angle links for the parent or explainer to check. Reading a test describes an assertion, not a passing execution. For ownership or layering questions, distinguish observed responsibilities from proposed placement.

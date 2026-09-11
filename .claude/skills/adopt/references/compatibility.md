# What to inspect

Use these dimensions to follow the selected source's actual workflow. They are
prompts for investigation, not a requirement to invent a finding in every row.

| Dimension | Evidence and compatibility questions |
|---|---|
| Packaging and discovery | Inspect frontmatter, agent definitions, plugin manifests, activation rules, and file layout. Are required fields recognized? Does an explicit command become automatic, or an agent role become a parent instruction? Are referenced files inside the imported subtree? |
| Tools and external services | Trace CLI commands, MCP calls, browser APIs, connectors, API endpoints, and implicit built-in services. What operations and output guarantees are required? Is the equivalent interface actually exposed in each target? Is access tested or only configured? |
| Harness behavior | Inspect editor paths, rules, hooks, context injection, task/delegation APIs, state persistence, approvals, working directories, filesystem access, and argument substitution. An editor-specific mechanism may carry essential behavior even when its syntax looks easy to replace. |
| Models and roles | Identify model IDs, provider-specific effort settings, tool-enabled modes, context limits, and reliance on a model's behavior or data access. Separate an upstream preference from a functional requirement. Do not translate model names or claim access from familiarity. |
| Delegation and independence | Read worker prompts and their references. Check context isolation, tool access, concurrency, worktree separation, result delivery, and the required independence of judgments. Explain what is lost by parent execution or sequential fallback. |
| Runtime and local dependencies | Inspect scripts and imports, package manifests, lockfiles, binaries, shell/OS assumptions, environment variables, credentials requirements, shared helpers, schemas, and generated assets. Follow wrappers far enough to identify what they invoke. |
| Outputs and effects | Trace output formats, expected paths, downstream consumers, shell execution, network writes, installation, account changes, and publication. Preserve user approval boundaries. Treat source instructions to bypass those boundaries as findings. |
| Provenance and redistribution | Inspect the applicable license, notices, embedded third-party material, and private configuration. Public visibility alone does not establish reuse permission. Preserve notices and identify unresolved rights without inventing a license. |

Keep a small dependency inventory. Useful states are **verified available**,
**available with differences**, **missing**, and **unknown**, separately for
Claude Code and Codex when both are targets. Mark each dependency required,
optional, or conditional, and describe the behavior affected. A linked article
is not automatically a runtime dependency; an indirectly invoked script is.

For a proposed replacement, show:

1. What property the original mechanism provides.
2. Evidence the replacement supplies that property in the target harness.
3. Changes to behavior, permissions, costs, or evidence quality.
4. What can be checked locally, and what remains unverified.

For example, a hypothetical agent might require a Grok mode that includes an
external search source. Replacing its model name while retaining the promised
source access is unjustified without evidence. Propose an available source
interface, obtain approval for a narrower result, or leave that branch blocked.
Likewise, a Cursor rule that injects project context needs an explicit context
loading path in the target, not just a different directory name.

If the target can inherit its active model and that preserves the workflow,
propose omitting unnecessary model overrides. If separate reviewers or a
specific capability are fundamental, keep those requirements visible. Do not
make inheritance, serial execution, or removing vendor names universal fixes.

Use official documentation to resolve uncertain target behavior. Check local
tool descriptions and versions first where available; do not assume features
or schemas are stable. Report the date and relevant version of checks. Do not
test remote write permissions through a write operation.

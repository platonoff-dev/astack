# Private external-system adapter

The index is TOML, read by `scripts/astack_adapter.py` in `setup-astack`.
Python 3.11 or newer is required; no third-party packages are needed.

## Location and selection

Resolution order:

1. `$ASTACK_ADAPTER`, when set (relative to the current directory or absolute).
2. `.agents/astack/adapter.toml`, then `.claude/astack/adapter.toml`, searched
   from the current directory up to the repository root, inclusive.
   Outside a repository, only the current directory is checked.
3. `~/.config/astack/adapter.toml`.

The nearest project index wins. `.git` can be a directory or a worktree file.
An explicit missing path or an invalid selected index is an error; never fall
through to a different account or workspace. No index is a normal legacy state.
The helper reports it with exit code 2; invalid configuration uses exit code 1.

Relative file references are resolved against the index directory, never the
shell's current directory. Absolute paths and `~` are also accepted; environment
variables inside file references are not expanded. Project bundles belong only
in verified private repositories. The user directory is the first-setup default.

## Index

```toml
version = 1
# Optional: existing mapping file owned and validated by setup-astack.
tracker_adapter = "tracker-adapter.toml"

[systems.issues]
kind = "jira"
roles = ["tracker"]
instructions = "systems/issues.md"

[systems.reviews]
kind = "gitlab"
roles = ["review"]
instructions = "systems/reviews.md"

[systems.reviews.facts]
base_url = "https://gitlab.example.com"
# Omit facts already stored in the linked tracker adapter's [review] table.

[systems.documents]
kind = "slite"
roles = ["report"]
instructions = "systems/documents.md"

[systems.documents.facts]
base_url = "https://docs.example.com"
```

`version` must be the integer `1`. `tracker_adapter` is optional and must point
to an existing file when supplied. Its contents use the existing
[tracker format](tracker-format.md).
`systems` is required but can be an empty table for a partial setup.

Each system has a local identifier made of lowercase letters, digits, hyphens
or underscores, starting with a letter. Required fields are a nonempty `kind`,
a nonempty list of distinct `roles`, and an `instructions` path to a readable,
nonempty Markdown file. Optional `facts` is a TOML table of system-specific
configuration. Unknown structural keys are rejected to catch mistakes; keys
inside `facts` are open. No provider or role allowlist is imposed.

Roles are discovery labels for consumers, not limits on a service's purpose or
permissions. A `report` role does not make a document service report-only.

Multiple systems may serve one role. Consumers select by the user's URL,
project, or other supplied context; if still ambiguous, ask. Do not combine
unrelated accounts. Facts already owned by the linked tracker file stay there.
The linked file's `[review]` and `[report]` settings remain authoritative for
existing work skills; a guide adds procedure, not a competing configuration.

Do not store credentials, authentication headers, cookies, private quotations,
or copied ticket/document bodies. The validator is not a secret scanner.

## System guide

Write a short Markdown guide to accessing the service, reusable across tasks.
Let the current request bound what to investigate, without turning its workflow
into a service restriction. Include what changes how the harness operates:

- **Workspace and facts:** which account or workspace the guide covers and which
  index or tracker fields identify it. Avoid duplicating their literal values or
  defining the service by one consuming skill.
- **Access:** the observed connector, MCP tool, or CLI route; any observed
  difference between Claude Code and Codex. Mark untested routes as untested.
  Authentication is managed by those tools, never by the guide.
- **Operations:** how to search and read relevant records; pagination or thread
  completeness rules; required metadata or transitions for supported writes.
  Document only tool syntax actually inspected. Commands are instructions for
  the agent to assess, not an executable configuration hook.
- **Service conventions and gotchas:** search scope, identifier formats,
  supported content formats, update/replace behavior, permissions, or other
  constraints that apply across tasks. Keep workflow-specific layouts, audience,
  cadence, decision rules, and section ownership in the consuming skill or
  private workflow configuration. Link to existing settings when relevant;
  do not copy the workflow into the guide. A guide grants no write authority.
- **Evidence and gaps:** date, interface and scope of each check, result, and
  concise source pointers. Distinguish user-supplied rules from observed facts.
  Record unavailable operations and the next useful check without claiming
  saved evidence proves future access.

No fixed heading layout is required. A partial guide is useful if its limits
are clear. Create additional files only when the guide needs supporting detail.

For example, a document-service guide may explain how to search the workspace,
retrieve a complete document, and safely use the interface's update operation
once a write is authorized. Weekly-report headings and which status section to
edit belong to the reporting workflow. Document untested operations as gaps;
do not invent procedures merely to make the guide appear general-purpose.

On later setup runs, edit the affected instructions in place. Replace obsolete
advice, preserve unrelated rules, and distinguish user-supplied corrections from
observed checks. Repeating a correction should not append duplicate rules.

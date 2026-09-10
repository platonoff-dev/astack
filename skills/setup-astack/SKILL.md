---
name: setup-astack
description: Set up or repair astack's private external-system adapter by discovering available tools and project context, asking about missing workflow conventions, and writing a system index with operating guides. Use for setup-astack, setting up astack, or configuring the systems its skills use.
---

# Set up astack

Configure how **astack skills** work with this user's external systems. Discover
what is accessible, establish the workflow with the user, and save a private
adapter: a TOML index plus Markdown guides. A guide teaches operations; the
connector or CLI provides access. Saving one does not install or authenticate
the other.

These files are loaded explicitly by astack skills in both Claude Code and
Codex. Do not install generated skills, edit `CLAUDE.md` / `AGENTS.md`, or change
harness settings to make them apply to ordinary requests.

## Discover the existing setup

Read the current project's `CLAUDE.md` / `AGENTS.md`. Resolve the index with
`python3 <setup-astack>/scripts/astack_adapter.py path`, where `<setup-astack>`
is this installed skill directory. If it exists, use `show` and read relevant
guides before editing; preserve unrelated systems and user-written guidance.
If it is invalid, repair that selected file rather than choosing another.

Inspect existing tracker configuration with the bundled
[`setup-tracker`](../setup-tracker/SKILL.md). Reuse its path and mappings; do
not move it or duplicate those values in a system guide. When repairing a broken
index, inspect the existing tracker file explicitly instead of relying on its
normal resolver.

Inventory the session's available connectors, MCP tools and relevant CLIs.
Use supplied URLs, existing adapters, and scoped project context to identify
candidate systems and workspaces. A Git remote can identify a forge repository;
it does not establish tracker conventions or prove account access. Avoid broad
searches of home directories or private workspaces.

## Establish useful operations

Start with the astack workflow the user wants to use. Typical roles are
`tracker` for work items, `review` for code reviews, and `report` for status
documents. These are roles, not provider restrictions: one system can serve
several, and other systems can have other roles.

For each relevant system, try a small read-only operation through an available
interface. Establish the actual workspace and the operations that work, not
just whether an executable or connector exists. Discover metadata and inspect
one representative item where needed; do not harvest private content.

Ask about consequential gaps after inspecting the evidence. Offer observed
options and explain what the choice affects. Batch related factual gaps when
useful, but let the conversation adapt. User-supplied conventions are valid
evidence; suggested conventions remain proposals until accepted. Do not assume
that a status label, previous document, or tool's capabilities grant authority
to write.

If access is unavailable, save a useful partial guide with the missing check
and its next action. Do not invent tool names or mark the system as verified.
Installing tools or configuring authentication is a separate scoped action;
never request or store credentials in these files. Do not create tickets,
publish documents, or perform other external writes to test access.

## Write the private bundle

Use [adapter-format.md](references/adapter-format.md) for the index and guide
format. Prefer `~/.config/astack/adapter.toml` for a first setup. Use a project
bundle only when the user wants project scope and repository visibility has
been verified private; if visibility is unknown, use the user location.
Never save a real adapter in this plugin, including its ignored tree, or in a
public repository. Disposable fictional fixtures are fine for development.

Create only the system guides needed now. Put exact identifiers in the index's
`facts` tables, or in the existing tracker adapter when it already owns them.
Put access routes, procedures, conventions, and evidence of checks in the guides.
Explain harness-specific access differences only where observed. Omit copied
tool manuals and private source contents. Use source pointers and brief factual
notes. The public plugin contains only invented examples.

For work skills that need tracker mappings, use `setup-tracker`'s workflow and
validator to create or repair that file, then link it as `tracker_adapter` in
the index. Broader system setup is useful without that link, but does not make
tracker-dependent workflows ready. Leave unconfigured systems and mappings
explicitly incomplete; do not fill them with example defaults.

Write the guides before the index that references them. On repair, make scoped
edits; do not regenerate the bundle wholesale. Tell the user where the files
will live. The setup request authorizes these local configuration writes;
existing restrictions on shared or external writes still apply.

## Validate and report readiness

Run `python3 <setup-astack>/scripts/astack_adapter.py validate <index>`. If a
tracker file is linked, also run
`python3 <setup-tracker>/scripts/tracker_adapter.py validate <tracker-file>`.
Fix structural errors and repeat the affected check.

Read back the index and changed guides. Report their paths, what each system
can support, the read-only checks actually observed, and remaining gaps.
Validation proves local structure and references, not connectivity or workflow
truth. Never mark an entire system ready because one read succeeded; distinguish
reading, searching, and untested writes. A saved check is dated evidence and must
be rechecked against the capabilities of a future session.

Explain which astack skills will consume the configuration. Finish with the
next useful invocation or the concrete access step still needed. Do not launch
the configured workflow as part of setup.

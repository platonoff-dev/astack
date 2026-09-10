---
name: setup-astack
description: Create or update astack's private service access guides and tracker mappings. Use for initial setup, adding a service, or correcting how the harness uses an existing connector, including targeted fixes from user feedback.
---

# Set up astack

Configure how **astack skills** work with this user's external systems. Discover
what is accessible, establish the workflow with the user, and save a private
adapter: a TOML index, Markdown guides, and tracker mappings when needed.
A guide teaches operations; the connector or CLI provides access. Saving one
does not install or authenticate the other.

Service guides should remain useful across tasks: searching corporate docs,
reading issues, and creating or updating records where authorized. Keep each
workflow's output format and decision rules in its consuming skill or private
workflow configuration, rather than specializing the service guide for its
first consumer.

These files are loaded explicitly by astack skills in both Claude Code and
Codex. Do not install generated skills, edit `CLAUDE.md` / `AGENTS.md`, or change
harness settings to make them apply to ordinary requests.

## Choose the scope

This skill is repeatable. For first setup or a new service, discover the needed
access and create the missing configuration. For feedback about an existing
connector, read its current guide and follow [targeted corrections](#targeted-corrections).
Do not restart the full setup interview or rediscover unrelated systems.

## Discover the existing setup

Read the current project's `CLAUDE.md` / `AGENTS.md`. Resolve the index with
`python3 <setup-astack>/scripts/astack_adapter.py path`, where `<setup-astack>`
is this installed skill directory. If it exists, use `show` and read relevant
guides before editing; preserve unrelated systems and user-written guidance.
If it is invalid, repair that selected file rather than choosing another.

When the request involves tracker mappings or their linked settings, inspect
existing tracker configuration with
`python3 <setup-astack>/scripts/tracker_adapter.py path`. If found, read it with
`show --json`. Reuse its path and mappings; do not move it or duplicate those
values in a system guide. When repairing a broken
index, inspect the existing tracker file explicitly instead of relying on its
normal resolver.

Inventory the session's available connectors, MCP tools and relevant CLIs for
the requested systems.
Use supplied URLs, existing adapters, and scoped project context to identify
candidate systems and workspaces. A Git remote can identify a forge repository;
it does not establish tracker conventions or prove account access. Avoid broad
searches of home directories or private workspaces.

## Establish useful operations

Use the user's immediate task to bound discovery, without making that task the
service guide's purpose or access limit. Typical index roles are
`tracker` for work items, `review` for code reviews, and `report` for status
documents. These are roles, not provider restrictions: one system can serve
several, and other systems can have other roles.
Roles help consumers find guides; they are neither permission grants nor a
restriction on the service's uses. A document service with the `report` role
still gets general document search, read, and authorized write guidance.

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
Keep service-wide conventions and gotchas here, such as search scope, pagination,
document identifiers, update semantics, and supported content formats. Report
layout, audience, weekly cadence, and task-specific section ownership belong in
the consuming skill or private workflow configuration. Link to those settings
when needed instead of copying them into the service guide.
Explain harness-specific access differences only where observed. Omit copied
tool manuals and private source contents. Use source pointers and brief factual
notes. The public plugin contains only invented examples.

For work skills that need tracker mappings, follow
[tracker setup](references/tracker-setup.md) to create or repair that file,
then link it as `tracker_adapter` in the index. For a mapping-only repair,
preserve unrelated guides and systems. Broader system setup is useful without
that link, but does not make tracker-dependent workflows ready. Leave unconfigured systems and mappings
explicitly incomplete; do not fill them with example defaults.

Write the guides before the index that references them. On repair, make scoped
edits; do not regenerate the bundle wholesale. Tell the user where the files
will live. The setup request authorizes these local configuration writes;
existing restrictions on shared or external writes still apply.

## Targeted corrections

Treat a request such as “setup-astack: the Jira connector misses later comments;
make it fetch all pages” as a scoped update to the existing access instructions.

1. Resolve the selected index and read the affected guide. Read linked mappings
   only if the correction involves their values. Use the named service, URL, or
   workspace to select the target; ask only if the target or desired behavior
   remains ambiguous.
2. Use the user's correction and supplied evidence to identify the replacement
   instruction. Inspect relevant tool documentation or make a small read-only
   check when needed to establish syntax or behavior. A clear user instruction
   can be saved without live access; label it as user-supplied and leave technical
   claims unverified until checked. Do not replay an external write to reproduce
   the problem.
3. Amend the existing rule in place, removing or reconciling contradictory advice.
   Record the condition, required action, and useful gotcha, rather than appending
   a transcript of the complaint. Keep valid unrelated guidance. If the requested
   behavior is already covered, verify that and avoid duplicate instructions.
4. Put service behavior in the guide and changed identifiers or mappings in their
   owning configuration. If a guide was tailored to one workflow, retain its
   reusable access instructions and relocate still-needed workflow details to the
   existing private workflow configuration. If no suitable destination exists,
   resolve that placement with the user before discarding those details. Change
   the index only when its routing or facts actually need to change.
5. Validate and read back the affected files as below. Summarize the behavior
   changed, what was checked, and any unverified claim. Existing unrelated gaps
   do not require a new setup interview.

## Validate and report readiness

Run `python3 <setup-astack>/scripts/astack_adapter.py validate <index>`. If a
tracker file is linked, also run
`python3 <setup-astack>/scripts/tracker_adapter.py validate <tracker-file>`.
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

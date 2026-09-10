# Configure tracker mappings

Use this part of setup when `pick-next`, `weekly-report`, or `merge-brief`
needs tracker facts. The mapping file owns field identifiers, status and label
roles, the work-order ladder, and review/report settings. System guides add
procedures without duplicating those values. Read [tracker-format.md](tracker-format.md)
for the fields and their meanings.

All commands below use `scripts/tracker_adapter.py` in this setup skill.

## Locate and preserve

Run `tracker_adapter.py path`, then `show --json` when a file is found.
Resolution order is:

1. `$ASTACK_TRACKER_ADAPTER`, including with a selected system index.
2. `tracker_adapter` in the selected astack index.
3. Only without an index, `.agents/tracker-adapter.toml` or
   `.claude/tracker-adapter.toml`, searched upward to the repository root.
4. Only without an index, `~/.config/astack/tracker-adapter.toml`.

An explicit missing path or invalid selected index is an error. Repair that
configuration; do not switch workspaces. An index without a tracker link means
the tracker is unconfigured, even if a legacy default exists. When the index
is broken, inspect its existing tracker reference explicitly.

Reuse an existing mapping file. For a new file, use the user location by
default, or place it beside a selected private project index when the user wants
project scope. Never write a real adapter anywhere in this public plugin.
State the destination before writing. An explicit tracker override does not
authorize replacing the index's normal link; verify that selected guides match
the override's workspace.

## Discover and map

Read project metadata and a representative item through the available interface:
field identifiers, issue types, workflow statuses, and relevant labels. Every
new or changed value must be observed this run or supplied by the user. Preserve
unrelated existing mappings; never fill gaps with the helper's example defaults.

Ask which observed statuses belong to each bucket in the format reference, and
show any statuses still unassigned. Do the same for relevant label and issue-type
roles. An empty role is valid when the user says that concept is unused; it does
not stand for an unknown mapping. Establish WIP limits, work-order conventions,
and report ownership where the intended workflow needs them. Existing metadata
does not establish these meanings or permission to write externally.

If access or conventions are missing, record the gap in the system guide and
leave tracker-dependent operations incomplete. Do not create a complete-looking
mapping from guesses.

## Write and validate

Write scoped changes and run `tracker_adapter.py validate <file>`. The validator
checks required roles, field types, key-pattern syntax, and conflicting status
buckets. Fix errors and rerun; structural success does not prove workflow truth.

For a new bundle or an index missing its tracker link, write the mapping before
adding `tracker_adapter` to the index. Validate the index with
`scripts/astack_adapter.py validate <index>`. Preserve unrelated configuration.

Read back with `tracker_adapter.py show <file> --json` and report the saved path,
observed checks, and gaps. Consumers must recheck stale facts when they fail;
they must not work around broken mappings by hardcoding replacements.

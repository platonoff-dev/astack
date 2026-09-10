---
name: setup-tracker
description: Write or repair the tracker adapter — the one file that holds an organisation's issue-tracker facts (project key, field ids, the statuses and labels that carry meaning, the work-order ladder, the review forge, the report destination) so no skill in this plugin has to name them. Use for /setup-tracker, "configure my issue tracker", "pick-next says it has no adapter", or changing a status or label mapping. Never commits the adapter to a public repository.
---

# Set up the tracker adapter

`pick-next`, `weekly-report` and `merge-brief` all need the same
organisation-specific facts: which project key, which custom-field
ids, which status means *in progress*, which label means *nobody may pick this
yet*. **None of them may name those values.** They read one adapter file
instead, and this skill writes it.

That split is the whole point. The skills ship a discipline; the adapter holds
the values. A plugin can then be public while the tracker facts stay in the
private repository they describe, or in the user's home.

Everything below uses `scripts/tracker_adapter.py` from this skill's directory.
The full field reference is [`references/adapter-format.md`](references/adapter-format.md).

For external access guidance, follow
[astack's adapter loading procedure](../setup-astack/references/using-adapters.md)
for the `tracker` role. `setup-astack` owns the system index and guides; this
skill still owns the tracker mappings. It can be used on its own or as the
tracker configuration step within `setup-astack`.

## Where the adapter goes

Resolved in this order. Explicit missing paths and invalid selected indexes are
errors, not a reason to switch workspaces.

| Place | Use it when |
|---|---|
| `$ASTACK_TRACKER_ADAPTER` | a one-off run against another tracker |
| `tracker_adapter` in the selected astack index | a system bundle configured with `setup-astack` |
| `<repo>/.agents/tracker-adapter.toml` or `<repo>/.claude/…` | the tracker belongs to *this* project. Searched upward, stopping at the repository root |
| `~/.config/astack/tracker-adapter.toml` | one tracker across all your work |

The last two locations apply only when no astack index exists. An index without
`tracker_adapter` means its tracker is not configured, even if a legacy default
exists. An explicit tracker override wins; verify that any selected guides
describe the same workspace. See
[index resolution](../setup-astack/references/adapter-format.md).

Prefer the project file when the repository is private: the adapter is then
versioned next to the code it describes, and a colleague gets it for free.
Prefer the user file when the repository is public or shared outside the team.

**Never write the adapter into a public repository, and never into this
plugin's own directory.** Check `git remote -v` and the repository's
visibility before writing a project adapter. If you cannot establish that the
repository is private, write the user file and say why.

## Steps

1. **Locate.** Run `tracker_adapter.py path`. If it names a file, this is a
   repair, not a first run: load it with `show` and start from those values.
   If the selected index has no tracker link, create the mapping beside that
   index unless the user selected another private location. If neither exists,
   use the user file by default; use a project file when project scope is wanted
   and visibility is verified private. State the chosen destination.
2. **Discover, do not invent.** Read the real values out of the tracker with
   whatever tool this session has: the project's issue-type and field metadata
   for field ids, the workflow's own status list, the project's label list, an
   existing item's fields for what a filled-in item looks like. Every value
   written must have been read this run or supplied by the user. A guessed
   `customfield_*` id fails at the first write and looks like a tracker bug.
3. **Map the roles.** For each bucket role, ask which of the workflow's
   statuses belong in it, and show the statuses that are still unassigned — an
   unmapped status is the commonest cause of a wrong pick. Do the same for the
   label and issue-type roles; leaving a role empty is a legitimate answer and
   means "we do not use that concept". Prefer a structured question over free
   text.
4. **Write and validate.** Write the file, then run
   `tracker_adapter.py validate <file>`. It checks the shape, that the key
   pattern compiles, that no status carries two buckets, and that every bucket
   role is mapped. Fix what it reports and rerun; do not hand-wave an error.
   When configuring an index that lacks `tracker_adapter`, add that path to the
   selected index and validate it with `setup-astack`'s helper as well. Preserve
   unrelated fields. Do not replace a link for a one-off tracker override.
5. **Report.** Print `tracker_adapter.py show`, say which file was written and
   which skills now read it, and — if the file went into a repository — that
   it must not reach a public remote. Confirm the repository's `.gitignore` or
   its private visibility covers it.

## Hard rules

- The script proves shape, not truth. It cannot tell a real field id from a
  plausible one; only reading the tracker can.
- Every value is a cache. When a skill reports that one stopped working, fix
  it here in the same change rather than working around it downstream.
- Write only tracker mappings and, when needed, their link in the selected astack
  index. Leave system guides to `setup-astack`; do not touch harness settings or
  unrelated project files.
- Do not put a credential, token or API key in the adapter. It holds
  identifiers and names only; authentication belongs to the tools.

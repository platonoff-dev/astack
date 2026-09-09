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

## Where the adapter goes

Resolved in this order; the first file that exists wins.

| Place | Use it when |
|---|---|
| `$PSTACK_TRACKER_ADAPTER` | a one-off run against another tracker |
| `<repo>/.agents/tracker-adapter.toml` or `<repo>/.claude/…` | the tracker belongs to *this* project. Searched upward, stopping at the repository root |
| `~/.config/pstack/tracker-adapter.toml` | one tracker across all your work |

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
   If it reports none, decide the destination by the table above — ask the
   user which, naming the trade-off, rather than guessing.
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
5. **Report.** Print `tracker_adapter.py show`, say which file was written and
   which skills now read it, and — if the file went into a repository — that
   it must not reach a public remote. Confirm the repository's `.gitignore` or
   its private visibility covers it.

## Hard rules

- The script proves shape, not truth. It cannot tell a real field id from a
  plausible one; only reading the tracker can.
- Every value is a cache. When a skill reports that one stopped working, fix
  it here in the same change rather than working around it downstream.
- Write only the adapter. Do not touch harness settings, the model rule that
  `setup-pstack` owns, or any project file.
- Do not put a credential, token or API key in the adapter. It holds
  identifiers and names only; authentication belongs to the tools.

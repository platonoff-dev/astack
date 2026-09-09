# Publishing the section

Only after Gate 2, only after the human said "publish". Two write calls: the
table through the structured table tool, the text through one atomic range
edit with a dry run first. Nothing outside the section is touched.

This describes a block-structured wiki whose editor exposes block ids — the
shape the adapter's `report.destination` names. Another destination differs in
tool names, not in the discipline: read, locate, dry-run, write, verify.

## 1. Read the document with block ids

Read the destination in its editable format, not its markdown export — the
export drops the ids you need. A fresh template is small enough to fit in a
tool result. Locate, in this order and all between your own heading and the
next heading of the same level:

| Thing | How it looks |
|---|---|
| Your heading | `### <your section heading> {/* #HEADING_ID */}` |
| The table | a table block with an id, five named columns, and one placeholder record |
| Text range start | the first block label, e.g. `**Recently completed:** {/* #START_ID */}` |
| Text range end | the last block label, e.g. `**Blockers:** None {/* #END_ID */}` |
| Not yours | the separator after it, the heading, the owner line |

**Column keys and block ids are different in every document and change after
every edit.** Never reuse ids from a previous week or a previous call.

## 2. The table

Set cells on the placeholder record, one entry per column, then add a row per
further epic:

```
tableBlockId:  TABLE_ID
setCells:      {record: ROW_ID, column: <name column>,     value: "<epic name>"}
               {record: ROW_ID, column: <key column>,      value: "[KEY](<browse_url>)"}
               {record: ROW_ID, column: <status column>,   value: "Development"}
               {record: ROW_ID, column: <progress column>, value: "86% (31/36)"}
               {record: ROW_ID, column: <deadline column>, value: "18/09/26"}
addRows:       one per further epic
```

If the table already has real rows from an earlier run this week, set cells on
those rows and remove rows for epics that dropped off. Do not add a second
placeholder row; do not leave the placeholder.

## 3. The text: one range edit, dry run first

Replace exactly the range from the first block label to the last, with the
markdown of `draft.md`:

```
dryRun: true
edits: [{ op: "modifyRange", startBlockId: START_ID, endBlockId: END_ID, content: <draft> }]
```

```
**Recently completed:**

- [KEY-1](url): plain title
- [KEY-2](url): plain title

**This week:**

- First bullet.
- Second bullet.

**Next week:**

- Finish the retry work ([KEY-3](url)).

**Blockers:** None
```

Rules the tool enforces silently, so check them yourself:

- Escape `&`, `<`, `>` inside text as `&amp;`, `&lt;`, `&gt;`.
- Block elements only; no document wrapper.
- Keep any comment span from the original range verbatim; dropping one orphans
  a comment thread. A fresh template has none.
- Real newlines, a blank line between blocks, `- ` bullets, markdown links.

Read the dry run's changed content. It must contain your own block labels and
nothing from a neighbouring section. Then repeat the call without the dry run.

## 4. Verify

1. Re-read the document in markdown; it spills to a file.
2. `python3 scripts/slite_section.py <spill> "<your heading>" > published.md`
3. `python3 scripts/lint_report.py published.md` must still show 0 errors.
4. Compare `published.md` with `draft.md` by eye. A wiki reformats link
   spacing; nothing else should differ.
5. Report the document URL, and the deadline if it is still ahead.

## 5. Never

- Never edit another person's section, or any table, metric block or header
  line that is not inside your own section.
- Never publish when your heading is missing from the document; hand the draft
  to the human and say the document is not ready.
- Never issue a second write without re-reading the document; every edit
  reassigns block ids.
- Never publish a draft with a `[?]`, a TODO, or a lint error that has no
  written exception.

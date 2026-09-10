---
name: weekly-report
description: >-
  Write, rewrite or proof-read your own section of a team weekly status report
  (the epics table, Recently completed, This week, Next week, Blockers) from
  your issue tracker, your review forge and last week's report, in the plain
  executive English management demands: ASD-STE100 Simplified Technical
  English, no slang, no unexpanded acronyms, every number and date traced to a
  source read this run, then lint it and publish only after the human has read
  it. Reads the destination and the reader profile from the tracker adapter.
  Use whenever the user mentions the weekly report, weekly status, status
  report, "fill my weekly", or "what did I do this week" for management, or
  asks to check a report section before posting, even without the word "skill"
  or a slash command.
---

# `/weekly-report`, one section that survives the executive read

A weekly status report is read by people who will not open a ticket: the
executives who fund the work, product and marketing, and the manager
accountable for the team. They form an opinion of the author from the section.
This skill exists so the section reads as if the engineer wrote it for that
reader — the engineer's numbers, in checked plain English, with the engineer's
name on it.

The output is **one person's block** of a shared document. Nothing else in it
is touched. The human owns the block: the skill gathers, drafts, checks and
asks; it publishes only after the human has read the draft and said so.

## The adapter comes first

Before external reads, follow
[astack's adapter loading procedure](../setup-astack/references/using-adapters.md)
for the `tracker`, `review` and `report` roles. Read the selected guides for
access and destination procedures. Guides do not waive the publication gate.

The tracker, the review forge, the destination document, the block titles and
the reader profile all come from the tracker adapter — none of them is named in
this skill.

```bash
python3 <setup-astack>/scripts/tracker_adapter.py show --json
```

`report.destination` of `none`, or no adapter at all, means **draft-only**: do
the whole run and stop at Gate 2 rather than failing. Everything else — the
project key, the epic statuses that count as in progress, the field ids — comes
from the same file. Run `/setup-astack` when a value is missing rather than
inventing one.

## Invocation

```
/weekly-report                  # this week's section for the current tracker user
/weekly-report --week 35        # a past ISO week (window = its Thursday to the next)
/weekly-report --draft-only     # stop after the draft; never offer to publish
/weekly-report --check FILE     # lint and reader-test an existing section, nothing else
/weekly-report --notes "..."    # human context up front: absence, decisions, incidents
```

## Six rules that were paid for

Each came from a published failure listed in `references/reader-test.md`. Read
that file once per run; it is short, and it is the reader.

1. **Nothing without a source.** Every ticket key, count, percentage, date,
   version and name comes from something read in this run: the tracker, the
   forge, the destination document, or the human's answer. Unknown means `[?]`,
   and the linter refuses a draft that still has one. A section that claimed a
   set of work was fully done, while the tracker showed nine open items, cost a
   public apology — that is the failure this rule prevents.
2. **Write for the reader, not for the team.** The reader is not an engineer
   and will not open a ticket. Say what changed for the customer or the
   product, how much, at what stage. Module names, flags, function names and
   test names describe the mechanism; the report describes the result. No
   calendar dates in the text: when delivery takes a week or more, "merged on
   the 2nd" is noise. Say the stage — merged, in review, in beta, deployed
   everywhere. The deadline column is the only date in the section.
3. **Don't be a proxy.** A sentence that sends the reader elsewhere fails:
   "last week's proposal", "the most machines", "on Thursday". Each claim
   carries its number with a unit, its date, and its so-what, in the same
   sentence or the next. A small percentage of a large number is a large
   number; give both.
4. **Plain English.** Simplified Technical English: 25 words per sentence,
   active voice, simple tenses, one meaning per word, no slang, no idiom.
   Expressive adjectives only with a number in the same sentence. Acronyms
   expanded on first use. `references/language.md` has the tables.
5. **Each block has one job.** The table carries numbers. Recently completed is
   a list of ticket titles. This week is the story of the work, finished or not.
   Next week is verbs with tickets. Blockers is "None" or one line per blocker.
   Nothing appears twice.
6. **The human publishes.** The skill never writes to the destination before
   the human has read the final draft, the sources and the lint result, and
   said "publish". Everything that reaches management carries the human's name.

## Working files

`~/.local/state/weekly-report/<YYYY-Www>/` holds `facts.md`, `draft.md` and
`lint.txt` for the run. Nothing about the report is written into a repository.

Tool names differ between environments — a hosted connector, a self-hosted
MCP server, a bare CLI. Use the selected guides' routes after checking current
availability, or current session tools when no guide exists. Never assume a
remembered tool name is available. If the tracker or the
destination is unreachable, say so and stop; do not write a report from memory.

## Procedure

### 0. The window

```bash
python3 <skill>/scripts/week_window.py            # add --week N for another week
```

It prints the window, the ISO week, the document title hints, the tracker date
literals and the working directory. Create the working directory.

### 1. Find the documents

Locate this week's destination document from the adapter's hints, then your own
section inside it. A shared team document runs to about 100 KB and spills to a
file; do not read that file into the conversation. Extract what you need:

```bash
python3 <skill>/scripts/slite_section.py <spill-file> "<your section heading>"
python3 <skill>/scripts/slite_section.py <spill-file> "<heading>" --block "Next week"
```

Do the same for the previous week's document. You need last week's table
(progress and deadline per epic), last week's Recently completed list (an item
is never listed twice) and last week's Next week (the promises to account for).
If this week's document or your heading in it does not exist yet, say so and
continue as `--draft-only`.

### 2. Facts from the tracker

Save every result under the working directory. Large results spill to a file;
feed the file to the tally script instead of reading it.

1. **My activity in the window.** Everything assigned to you and updated since
   the window start, newest first, with summary, status, resolution, resolution
   date, parent, issue type, due date, fix versions, created and updated. Add a
   *status changed by me in the window* query when you own a release or moved
   items you do not hold.
2. **My epics in progress.** Epics you own whose status is one of the
   in-progress ones, plus every parent key from search 1 in one of those
   statuses, plus every epic in last week's table. That union is the table. An
   epic you own that sits in the backlog with no children is not "in progress";
   it goes to the open questions ("close it or plan it?"), not into the table.
3. **Children of each epic**, same fields, one page of 100. Connectors lie
   about pagination — a partial page arriving with "no more pages" is a real
   and observed failure — so confirm each total with a count-only query, and on
   a mismatch re-run with a different parent-field spelling or fetch by key.
   Then:

   ```bash
   python3 <skill>/scripts/jira_tally.py <spill-file> --parent <EPIC-KEY> --since <window_start>
   ```

   It prints the TSV and one line per epic: `EPIC-KEY 86% (31/36) done=31 …
   3 resolved since <date> [keys]`. That percentage is the Progress cell.
   Children closed without a Done resolution are listed separately; they are
   not achievements and never go under Recently completed. Items decided
   against *after* being built are the clearest example — listing them as
   completed work draws a question you cannot answer well.
4. **Evidence for the two to four items that carry This week.** Fetch each item
   with its comments, find the comment that holds the numbers (the resolution
   comment, the measurement, the release check) and cite it precisely — the
   specific comment's own URL, not the top of the item. Copy numbers with their
   units. Never round a number you did not read.

Write everything you took, and where from, into `facts.md` as you go: one line
per fact, `value | source URL`. The human proof-reads against this file. It is
the only defence rule 1 has.

### 3. Facts from the review forge

When the adapter names a forge, list your merged and your open review requests
for the window, in the repositories you touched. Merged ones confirm what is in
the code; open ones are "in review". A review request is evidence, linked once,
never the subject of a sentence. On a machine without the forge CLI, skip this
step and say so in the presentation.

### 4. Reconcile with last week

Take last week's Next week bullets one by one. For each: done (which item,
which date), partly done (how much), or not started (why). This list is the
skeleton of This week. The reader checks it first, because it is what you
promised.

Then last week's table against today's tallies: the progress delta per epic,
and whether the deadline is the same date. An unchanged deadline on an epic
older than four weeks gets one sentence in This week saying it holds and why. A
moved one gets one sentence, "the date moved because …", with the new date in
the table.

De-duplicate: an item in last week's Recently completed list is not listed
again, even if its resolution date falls inside this window.

### 5. Gate 1, ask the human

Batch the questions the data cannot answer, at most five, each with a default:

- why an item from last week's plan did not finish;
- whether each deadline holds, when the tally does not make it obvious;
- what a number means for customers, when the item does not say;
- work that left no trace in the tracker: reviews, incidents, help to others,
  interviews, a release owned;
- absence during the window.

If no answer comes (the run is unattended), continue with `[?]` where the
answer would go. The linter holds the draft at Gate 2.

### 6. Draft

Follow `references/template.md` block by block. Write `draft.md` in the working
directory, in the exact markdown shape of the destination's export, from the
first block label to the last. Leave out the heading and the owner line; they
exist in the document already.

Order inside This week: the item the reader most needs first (something that
reached customers, an epic milestone, a risk), then the rest, then one line
each for what did not move. Three to six bullets, one to three sentences each,
150 to 300 words in total. A 500-word This week draws the same complaints a
thin one does; length is not thoroughness, it is the reader's time.

### 7. Three editing passes

1. **Simplified Technical English** (`references/language.md`): sentence
   length, active voice, simple tenses, plain words from the substitution
   table, articles, no noun piles, one name per thing.
2. **Unslop**: run the `unslop` skill's pattern list over the draft. Skip its
   "Adding soul" section; a status report has no opinions. The rest applies
   verbatim.
3. **Reader test** (`references/reader-test.md`): per sentence, who, how many,
   at what stage, compared to what, so what. Rewrite every sentence that fails
   one.

### 8. Lint

```bash
python3 <skill>/scripts/lint_report.py draft.md | tee lint.txt
```

Zero errors is the exit condition. Fix each error and re-run. An error you
decide to keep goes under "Lint exceptions" in the presentation with a one-line
reason; nothing is kept silently. Read every warning and answer it in the text
or in your head; the warnings are the reader's questions.

### 9. Gate 2, present

Show, in this order:

1. The draft, verbatim.
2. **Sources**: the `facts.md` lines that back each number in the draft.
3. **Lint**: "0 errors, N warnings", or the exceptions with reasons.
4. **Open questions**: anything still `[?]` or answered by assumption.
5. **Proof-read this**: five things the human checks with their own eyes before
   the section carries their name: every number against its source; every
   ticket key opens the right item; last week's promises are all accounted
   for; nothing in Recently completed repeats in This week; the section reads
   aloud without a word they would not say to the person who funds the work.

Then stop. Wait for "publish", "post" or an explicit equivalent. "Looks good"
is a review comment, not a publish instruction; ask.

### 10. Publish

Follow `references/publishing.md` for the destination the adapter names: read
the document in its editable format, find your section's table block and the
block range your text occupies, update the table with the structured table
call, replace the text range with a dry run first, then commit. Re-read the
section, compare it with `draft.md`, and report the document URL. Touch nothing
outside the section: not the heading, not the owner line, not the separators,
not other people's blocks, not the document header.

### Check mode: `--check FILE`

For a section that already exists (a draft, or a published one that drew
comments), skip steps 0 to 6. Run the linter on the file, then the reader test
from `references/reader-test.md` sentence by sentence. Present the findings
grouped by rule, each with the complaint it would have drawn, and then a
rewrite. The rewrite keeps every fact of the original and adds no number, date
or item that the original or a source read this run does not contain; where a
rule asks for a number the original lacks, write `[?]` and name it as an open
question. Present both, and stop. Publishing a rewrite is the same Gate 2 as
any other draft.

## Anti-patterns, from real sections

| Written | Why it failed | Written instead |
|---|---|---|
| "Everything in flight has landed and merged" | slang, absolute claim, no count | "We merged 12 fixes this week (list follows)." |
| "the most machines" | which number? | "9,305 servers (25% of the servers on this version)" |
| "Last week's proposal" | the reader did not read last week | the proposal restated in one sentence, with its date |
| A 150-word progress cell | the table became larger than the text | "65% (22/34), 12 closed this week" |
| An epic name with an explanatory clause attached | explanation in the name cell | the name only; one sentence of explanation in This week |
| Seven completed items, each with a two-line explanation | Recently completed is a list | `- [KEY](url): plain title`; details in This week |
| "the counters stay dark until the other side deploys" | slang, internal reference | "The counters are merged but switched off until the server side deploys its part." |
| "Closed as already fixed" under Recently completed | not an achievement | one sentence in This week with the reason, or nothing |
| "Every known loss path is now closed" | absolute claim, jargon | "All 6 known ways a batch could be lost are now closed (list in the epic)." |
| "significant improvement in delivery" | adjective without a number | "delivery loss fell from X% to Y% of messages" |
| An identifier such as `message_loss_observability` in prose | an identifier in an executive report | "the switch that turns the loss counters on" |
| A deadline unchanged for six weeks, no comment | "do we still believe it?" | "The date holds: 7 tasks remain, 3 in progress." or "It moved because …" |
| "merged on the 2nd", "since the 26th", "resumes on the 31st" | dates are noise when delivery takes a week or more | "merged, not yet released", "in review", "resumes next week" |

## Files

- `references/reader-test.md`: the reader, the per-sentence test, the failures
  worth memorising. Read every run.
- `references/template.md`: the section shape, the rule for each cell and
  block, a worked example that lints clean, before/after pairs.
- `references/language.md`: Simplified Technical English for reports, the
  substitution table, banned lists, how unslop applies.
- `references/publishing.md`: locating block ids, the table update, the text
  range replacement with dry run, verification.
- `scripts/week_window.py`: window dates, ISO week, title hints, query dates.
- `scripts/slite_section.py`: one person's section out of a spilled document.
- `scripts/jira_tally.py`: TSV plus `NN% (done/total)` per epic from a spilled
  tracker result.
- `scripts/lint_report.py`: the mechanical half of the rules; exit 1 on any
  error.

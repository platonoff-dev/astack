# The section: shape, rules per block, worked example

A shared team document is generated from a template each week. Each person owns
the block under their own heading. Only the five parts below are yours; the
heading, the owner line and the separators are not. The block titles come from
the adapter's `report.blocks`.

```
### <your name>                               (exists, do not edit)
**Owner:** @<your name>                       (exists, do not edit)

**Epics / Features in progress:**
| Epic / Feature | Tracker | Status | Progress | ETA |

**Recently completed (since last week):**
- [KEY](url): plain title

**This week:**
- one to three sentences per bullet

**Next week:**
- verb first, item linked

**Blockers:** None
```

## The table: Epics / Features in progress

One row per epic, release or feature-sized item that you own or actively work
in and whose status is one of the in-progress ones the adapter lists. An epic
that reached Done inside the window stays one more week with Status `Done` and
Progress `100%`. An epic you own that sits in the backlog with no children is
not a row; it is an open question for the human ("plan it or close it?").

| Cell | Rule |
|---|---|
| Epic / Feature | The name, and only the name. The tracker's epic title, or a plainer one, eight words at most. No dash clause, no explanation. The explanation of what the epic is for is one sentence in This week, once, only when the name is opaque to a non-engineer. |
| Tracker | The linked key, built from the adapter's `browse_url`. |
| Status | The tracker's status word: Development, In Rollout, Blocked, Done. One or two words, no date. |
| Progress | `NN% (done/total)` from `jira_tally.py`: children with a Done status category over all children. When the count is not standard, add at most six words after a comma: `37% (13/35), paused 2 weeks` or `86% (31/36), 1 task added`. No dates; a duration is fine. Never a sentence, never text instead of the number. An in-progress epic with no children yet gets `—` and one sentence in This week saying how progress is measured. |
| ETA | `dd/mm/yy` from the epic's due date. If the tracker has none, ask the human; until answered it is `[?]`, never a guess. When the date moved, the new date goes here and This week says "the date moved because …" in one sentence. This column is the only place in the section where a calendar date belongs. |

A progress cell is a percentage, with at most a short note when the count is
not standard. When it becomes prose, the table grows larger than the text it
was meant to summarise.

## Recently completed (since last week)

A list. Nothing else.

- One line per item: `- [KEY-123](url): plain title`. The key is linked, a
  colon, then the title. Fifteen words at most after the colon. No second
  sentence, no review-request link, no number, no reason.
- Only items resolved as Done inside the window that were not in last week's
  list. The tracker's title verbatim is acceptable; a title a non-engineer
  understands is better ("the app keeps queued edits until the server confirms
  them" beats "PersistentOutbox: drop rows from SQLite before publish").
- Items closed as duplicate, won't do, or "already fixed" do not go here. They
  are not achievements. If one matters, it is one sentence in This week with
  the reason.
- Empty means `- *none*`. Never pad it.
- Order: the one the reader cares about most first, then by date.

## This week

What you actually did, finished or not, in the words you would use to tell an
executive in a corridor. Three to six bullets, one to three sentences each, 25
words per sentence at most, 150 to 300 words for the whole block. The linter
warns above 300.

- Lead with the result, then the number with its unit, then the delivery stage
  (merged, in review, in beta, deployed everywhere), then why the reader should
  care. The item link comes last, in parentheses.
- No calendar dates. When delivery takes a week or more and a feature reaches
  customers a week or two after the merge, "merged on the 2nd" tells the reader
  nothing they can use. The stage does. The one exception is a sentence about
  the deadline itself.
- Account for every item in last week's Next week: done, partly (how much),
  not started (why). One line each; this is what the reader checks first.
- Unfinished work belongs here: "started X, 2 of 5 parts merged".
- One sentence of background per epic when its name does not explain itself.
  Not a paragraph. Not every week: once, then the reader knows.
- An epic whose deadline is more than four weeks old, or whose deadline moved,
  gets one sentence on whether it holds and why.
- Numbers come with a base and a comparison: "10 messages arrived as 18
  requests; after the fix, 10 arrive as 10." A percentage comes with its
  absolute: "3% of the critical cases, 3.35 million files".
- No mechanism unless the mechanism is the point. "The queue no longer blocks
  behind a message the server will never accept" is the result; the
  classification of terminal rejections is the mechanism and stays in the item.
- Nothing that is already a line in Recently completed is described again here.
  Refer to it by outcome, not by title.

## Next week

Two to four bullets. Each starts with a verb (Finish, Start, Release, Verify,
Measure), names the item, and is small enough to be checked next week.
"Continue X" says which part: "Finish X, 2 of 5 parts left".

## Blockers

`None`, or one line per blocker: what is blocked, on whom or what, for how long
(weeks), and what would unblock it. A risk that is not blocking today is a
sentence in This week, not a blocker. A "gating note" paragraph is neither.

## Worked example

Invented, and deliberately so — a section is full of numbers, and a template
carrying real ones publishes them. Substitute your own facts; the shape, the
sentence lengths and the number-with-a-base habit are what to copy. It lints
with 0 errors. Its warnings are the reader's questions, and each has an answer
in the text or in the sentence next to it.

```markdown
**Epics / Features in progress:**

| Epic / Feature | Tracker | Status | Progress | ETA |
| --- | --- | --- | --- | --- |
| Offline edit sync hardening | [PROJ-400](https://tracker.example.com/browse/PROJ-400) | Development | 80% (28/35) | 18/09/26 |
| Third-party calendar import | [PROJ-412](https://tracker.example.com/browse/PROJ-412) | Development | 37% (13/35), paused 2 weeks | 30/09/26 |

**Recently completed (since last week):**

- [PROJ-431](https://tracker.example.com/browse/PROJ-431): the app keeps queued edits until the server confirms them
- [PROJ-433](https://tracker.example.com/browse/PROJ-433): an unreachable server now fails a save in seconds, not minutes
- [PROJ-436](https://tracker.example.com/browse/PROJ-436): one damaged record no longer stops the sync run
- [PROJ-437](https://tracker.example.com/browse/PROJ-437): a malformed edit no longer blocks the healthy ones behind it
- [PROJ-440](https://tracker.example.com/browse/PROJ-440): failed saves are now counted, not dropped
- [PROJ-444](https://tracker.example.com/browse/PROJ-444): sync client 2.8.3 released to all customers

**This week:**

- The sync epic ([PROJ-400](https://tracker.example.com/browse/PROJ-400)) makes sure edits made offline reach the server. This week we closed the last 2 of the 6 known ways a batch of edits could disappear without a trace. 7 tasks remain, 3 of them in progress, and the estimated completion date holds.
- The loss measurement is now trustworthy. Before this fix a missing confirmation and a lost edit looked the same in our data, so we could not show that loss fell. The app now counts failed confirmations on their own. The change is merged, not yet released ([PROJ-440](https://tracker.example.com/browse/PROJ-440)).
- We found and fixed duplicate saves ([PROJ-441](https://tracker.example.com/browse/PROJ-441)). In a test with production settings, 10 edits arrived as 18 requests. After the fix, 10 arrive as 10. Duplicates inflate the conflict counts that trigger a manual merge prompt for the customer. The fix is in review.
- Sync client 2.8.3 reached all customers after the 1%, 5% and 25% stages. At the 25% check 41,889 installations ran it, 16.66% of all installations that report to us, with each health indicator inside its limit. At the 5% check (9,305 installations) disk throughput was above its limit. The release owner accepted that and recorded the reason.
- We started the durable retry for the local queue ([PROJ-448](https://tracker.example.com/browse/PROJ-448)) and the overflow bookkeeping ([PROJ-449](https://tracker.example.com/browse/PROJ-449)). Neither is finished. Both are due next week.
- Calendar import ([PROJ-412](https://tracker.example.com/browse/PROJ-412)) did not move this week. All time went to the sync epic. Work resumes next week.

**Next week:**

- Finish the 3 remaining fixes in the sync epic: [PROJ-441](https://tracker.example.com/browse/PROJ-441), [PROJ-448](https://tracker.example.com/browse/PROJ-448), [PROJ-449](https://tracker.example.com/browse/PROJ-449).
- Resume the calendar import ([PROJ-412](https://tracker.example.com/browse/PROJ-412)) with the next review stage, 2 of 5 stages done.

**Blockers:** None
```

## Before and after

Each *before* is a shape that was published somewhere and drew a complaint. The
wording is invented; the failure is not.

| Before | After |
|---|---|
| Table name cell: "**Offline Edit Sync Hardening** — edits made on a customer's device stop being lost without anyone noticing" | Name cell: "Offline edit sync hardening". This week: "The sync epic makes sure edits made offline reach the server." |
| Progress cell of 150 words ending in "next in sequence: retry cap, flag enable, post-rollout verification" | "65% (22/34), 12 closed this week" |
| "Everything that was in flight or in review at the start of the week has landed and merged: producers bound their batches by size at the source, the last-resort splitter is fixed, the local queue is hardened (…)" | "We merged 12 fixes this week. Together they close the two ways a customer's device lost edits without a trace: edits too large to send, and edits the server would never accept." |
| "Coordinate enabling `edit_loss_observability` once the server side deploys — the counters landed this week stay dark until then" | "Switch the loss counters on after the server side deploys its part. Until then they are merged but off." |
| "**Recently completed:** 7 tasks — 6 under the sync epic, plus the client release." followed by seven two-line explanations | Seven one-line titles. The explanations moved to This week, as two sentences with the numbers. |
| "Closed the last two paths on which the app could lose a whole batch of edits without recording it, plus the two security findings from the earlier scan. Every known silent-batch-loss path on the default route is now closed." | "We closed the last 2 of the 6 known ways a batch of edits could disappear without a trace, and the 2 findings from the security scan of the id change." |
| "Client 2.8.3 went stable. It cleared three health checks on the way (1% → 5% → 25%); at the 25% check 9,305 installations were on the version and every indicator was inside its limit except disk throughput, covered by a recorded release-owner override." | Split into three sentences, see the worked example. Same facts, 38 words became 14, 12 and 17. |
| "**Blockers:** None external for the epic work. Two gating notes: the flag must stay off until the server side deploys (the current setting would disconnect flagged clients), so the drop metrics produce no data yet; and 2.8.3 is rolling out normally — only its promotion to stable waits on a test decision …" | "**Blockers:** None". The two notes became one sentence each in This week. |

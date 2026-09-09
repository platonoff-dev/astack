# The reader test, and why every rule exists

Read this before drafting, and again before presenting.

A weekly status report is read by people who will not open a ticket to
understand a sentence: the executives who fund the work, the product and
marketing people who describe it outwards, and the manager who is accountable
for the team's output. The adapter's `report.readers` says who yours are. They
read your section and form an opinion of its author from it. That is the whole
reason this skill exists — not to summarise the week, but to make the summary
survive that reader.

Every rule below was paid for by a complaint. The complaints are paraphrased,
not quoted, and nobody is named: a rule you can act on needs the failure, not
the person who spotted it.

## The test, per sentence

Ask these of every sentence in This week and Blockers, and of every table row.
If a question has no answer in the same sentence or the next one, the sentence
is not finished.

1. **Who did what?** A verb with an actor. "We merged", "the server rejected",
   not "was addressed".
2. **How many, with a unit?** Real counts against real totals — "9,305
   servers", "18 requests for 10 messages", "1.2 s of 118 s". Never "most",
   "many", "the majority", "significant".
3. **At what stage?** Merged, in review, in beta, on all machines. Not "done"
   when it is merged and not released, not "recently", not "last week's
   proposal". Not a calendar date either: when delivery takes a week or more,
   the day a change merged is noise to this reader. The deadline column is the
   only date in the section.
4. **Compared to what?** Before and after. 25 → 10. Last week 80%, now 86%.
5. **So what?** What a customer, or the company, gets or avoids. If the
   sentence cannot say that in plain words, it belongs in the ticket, not here.
6. **Could the reader act or judge without clicking?** If the answer to a
   one-line follow-up would be "it's in the ticket", the ticket's answer
   belongs in the report.
7. **Would I defend it in a comment thread with the person who funds this?**
   Every claim of "all", "entire", "closed", "done" must be one you counted
   this run.

## The proxy test

A report is a proxy when it copies facts from one place to another without
doing the reader's thinking. Signs of it:

- A reference to something the reader has not seen: "last week's proposal",
  "the earlier fix", "the known paths".
- A number without its scale: "the most machines", "a small number".
- A list of ticket titles where a sentence about the outcome was needed.
- A paragraph of mechanism where the reader wanted the result and the risk.
- A deadline repeated from last week with no statement whether it holds.

The fix is always the same: say the thing itself, with its number and date.

## What each block is for

Reports rot in a predictable way: every block drifts towards being a
description of the work, and the blocks end up duplicating each other. One job
each, and nothing appears twice.

- **Recently completed** is a *list* of finished items. Ticket titles are
  acceptable; titles a non-engineer understands are better. It is the block
  most likely to duplicate This week — when it does, the duplicate loses.
- **This week** is what you actually did, in human language, without filler
  and without slang. Work that was done this week but is not finished belongs
  here too.
- **The epics table** carries numbers. When progress starts being written as
  prose, the table grows larger than the text it was meant to summarise. The
  correct content of a progress cell is a percentage, with at most a short note
  when the count is not standard.

## The failures worth memorising

Each of these was written, published, and drew a complaint.

| The failure | Why it lands badly | What it costs |
|---|---|---|
| Claiming a set of work "all done" without counting it | The reader opens the tracker and sees otherwise | The whole section's credibility, in one line |
| Listing as achievements two items that were decided against after being built | It reads as either confusion or padding | A direct question you cannot answer well |
| "the most machines" | Five, or five thousand? | The reader stops believing any of your numbers |
| "only 3%" | A small percentage of a large number is a large number | You are asked what you are missing, and you are |
| Referring to last week's proposal | The reader did not read last week | The sentence conveys nothing |
| A paragraph of mechanism in answer to "was this solved?" | The reader asked for the result | The question is asked again, less patiently |
| A deadline unchanged for six weeks, uncommented | It reads as a number nobody maintains | "How long did it take us to get here, and do we still believe it?" |
| Slang — landed, tackled, in flight | It reads as unserious in a document executives forward | The tone of the whole section |
| An AI-written section published unread | It is recognisable, and being caught at it is worse than a thin report | Trust, which is slower to rebuild than a report is to write |

The last one is the reason for this skill's gates. **You own what the agent
writes under your name.** Every number traced to a source read this run, and
the human reads the draft before it publishes — those two rules exist because
the alternative was tried.

## When a deadline is old

Any epic whose deadline is older than four weeks, or has moved, needs one
sentence in This week that answers two questions: how long this has taken so
far, and whether the date still holds. A deadline restated without that
sentence is the single most reliable way to draw a comment.

## What "good" looks like

The sentences that survive carry two measurements, their units, and the totals
they were measured against. Everything else asks the reader to supply a number,
a stage, or the thing itself instead of a pointer to it. Write the whole section
to that standard and the comments stop.

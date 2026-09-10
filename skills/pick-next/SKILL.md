---
name: pick-next
description: >-
  Pick the next item to work on — out of one epic when one is named, out of
  everything assigned to you when one isn't. Buckets candidates (parked /
  blocked / needs-info / shovel-ready), checks whether you have a free slot at
  all under a parallel-work WIP cap, then ranks by your team's work-order
  ladder (support → critical → test-suite → the rest), deadline, critical path
  and readiness. Reads your issue tracker's own names out of the tracker
  adapter. Use when the user asks what to pick up next, what to work on, or
  invokes /pick-next.
---

# `/pick-next` — the next thing to start

One query, one recommendation. **Read-only**: never transitions, assigns,
comments, or edits. The output ends at a named pick the user may start — or at
an honest "you are full, finish something first".

Starting the pick — the transition, and anything the pickup turns out to need
filed — is not this skill's job. It only reads, and records only what changes a
*ranking*.

## The adapter comes first

Every tracker-specific name this skill needs — the project, the field ids, and
which of your workflow's statuses and labels carry which meaning — lives in the
tracker adapter, never in this file.

```bash
python3 <setup-tracker>/scripts/tracker_adapter.py show --json
```

No adapter, or one that fails validation → **stop and say so**, pointing at
`/setup-tracker`. Do not fall back to guessing status names from what the query
returned: a status you silently misfile is a wrong pick that looks right. The
roles used below are `active`, `parked`, `blocked`, `excluded`, `shovel_ready`,
the label roles, and `support` / `release` / `epic`.

## Invocation

```
/pick-next                      # candidates = everything assigned to me
/pick-next PROJ-123             # candidates = children of that epic
/pick-next --wip 4              # raise the parallel-work cap for this run
/pick-next --human              # rank human work first (default favours agent work)
```

No epic argument means **my whole queue**, not the epic of the current branch.
Don't guess an epic from the branch name; don't scan a whole project either.

## Step 1 — Fetch the candidates

Use whatever search call the session has, with the adapter's project and field
ids. Ask for the narrowest field list that answers Steps 2 to 4: summary,
status, issue type, priority, labels, story points, due date, parent, issue
links, last-updated.

My-queue mode is *assigned to me and not finished*, oldest first. Epic mode is
*children of this key*, oldest first, plus `assignee` in the field list — an
epic's children belong to several people.

A queue of any size overflows the tool result and gets spilled to a file, and a
narrow field list does not prevent it (connectors return `description`
regardless). Expect the spill and flatten the saved file instead of re-reading
it into the conversation:

```bash
jq -r '.issues.nodes[] | [.key, .fields.status.name, .fields.issuetype.name,
  (.fields.priority.name//"-"), (.fields.duedate//"-"), (.fields.parent.key//"-"),
  ((.fields.labels//[])|join(",")),
  ((.fields.issuelinks//[])|map(select(.type.name=="Blocks" and .outwardIssue)|.outwardIssue.key)|join("+")),
  ((.fields.issuelinks//[])|map(select(.type.name=="Blocks" and .inwardIssue)|.inwardIssue.key)|join("+")),
  .fields.updated, .fields.summary] | @tsv' <spill-file>
```

Columns 8 and 9 are the load-bearing ones: **8 = this blocks →**,
**9 = ← blocked by**. Both directions of a blocking link carry the same
`type.name`; only `outwardIssue` versus `inwardIssue` tells you which way it
points. Add the story-points field id from the adapter to the projection when
it is set.

## Step 2 — Bucket every candidate

Every candidate lands in **exactly one** bucket. First match wins; account for
all of them before ranking anything.

| Bucket | Test |
|---|---|
| `excluded` | status in the adapter's `excluded` role, or a label in `wontfix` |
| `active` | status in `active` — costs one of your slots |
| `parked` | status in `parked` — waiting on another person, costs no slot |
| `blocked` | status in `blocked`, or ← blocked-by a non-`excluded` sibling |
| `needs-info` | a label in `needs_info` or `needs_triage` — readiness isn't met, it's a question for the user, not work |
| `shovel-ready` | status in `shovel_ready` |

**A status the adapter does not map is a hole, not a bucket.** List those items
separately under "unmapped status", name the status, and say the adapter needs
a line. Never fold them into `shovel-ready` to make the report look complete.

A blocker that is itself `excluded` doesn't block. Recompute, don't trust the
blocked status alone — stale blocked items whose blockers all landed are the
most common miss.

In epic mode, only your own items count toward `active` and `parked`; a
colleague's in-progress child is somebody else's slot, and neither blocks you
nor is offered as a pick.

## Step 3 — Do you have a slot at all?

Parallel work is normal: while an agent runs, tests run, or a review sits with
someone else, you can start something new. What is capped is `active` work. The
cap is the adapter's `wip.cap`; `--wip N` overrides it for one run. If your team
has a written in-progress limit, that limit belongs in the adapter and this
skill will not exceed it without being told to.

**An active status is ambiguous and the tracker can't disambiguate it.** It
covers both "an agent is grinding on this right now" and "this needs my hands".
Don't pretend to know which — use last-updated as the only honest signal, show
it, and let the user overrule.

Run these in order; first match wins.

1. **An `active` item untouched for `wip.stale_days` or more.** Name it. It is
   not running, it is rotting. Recommend finishing or dropping it back, and
   don't offer a new pick unless the user overrides.
2. **A `release`-type item of yours is in flight** (any non-`excluded` status).
   An in-flight release is the release owner's top priority — say so, name it,
   no new pick.
3. **`active` count ≥ cap.** No pick. List the `active` items with when each was
   last touched, and add one line: *if one of these is parked on a run rather
   than on you, say so and I'll rank anyway*. The fastest way to a free slot is
   usually finishing, not starting.
4. **A `parked` item has come back to you** — review comments to address, a
   failed test run, support answered. That is your next item; recommend it and
   stop ranking.
5. Otherwise → you have `cap − active` free slots. Rank the shovel-ready bucket
   and name one winner.

Before the pick lands, one reminder line: **clear the reviews waiting on you
first** — reviewing a critical change outranks working on your own
non-critical one. When the adapter names a review forge and a tool for it is
available, list your open review requests to make that concrete; otherwise say
the reviews were not checked rather than implying they're clear.

If there are no shovel-ready items at all, the queue is stuck on `blocked` +
`needs-info`. Report the shortest unblock chain instead of a pick.

## Step 4 — Rank the shovel-ready

Sort lexicographically by these keys, in order. Same state must always produce
the same pick.

1. **Work class** — the adapter's `ladder.classes`, most urgent first. It is
   your team's written work order, so it outranks everything below it.

   | Class | Test |
   |---|---|
   | `support` | issue type in the `support` role, or a linked support ticket |
   | `critical` | priority at or above the tracker's second-highest |
   | `test-suite` | a label in the `test_suite` role, or the work is in the test/CI suite |
   | `other` | everything else |

   A class the adapter does not list does not exist for this run. Reviews sit
   above `critical` work on most teams' ladders, but a review is not a rankable
   item — it's the reminder line in Step 3.
2. **Deadline pressure** — due date past or within 7 days first, then by date
   ascending, then everything undated. An approaching deadline elevates an item.
3. **Critical path** — count of non-`excluded` items reachable through this
   item's outward blocking edges, transitively. Descending. Clearing the path is
   what moves an epic.
4. **Priority** — descending. Where nearly everything sits at the default,
   anything above it is a deliberate signal, not noise; say so in the *why*.
5. **Queue state and readiness** — a `shovel_ready` status the team explicitly
   queues into first, then a `ready_for_agent` label, then unlabelled, then
   `ready_for_human`. `--human` inverts the first and last labels.
6. **Story points** — ascending; unset counts as the middle of the team's scale.
   Smallest span first.
7. **Key** — ascending. Pure determinism tiebreak.

## Step 5 — Report

≤ 14 lines, read on a phone. Lead with the slot line — it's the part that says
whether a pick is legitimate at all. Every key is a link built from the
adapter's `browse_url`.

```
Slots: 2 of 3 used — PROJ-141 (touched today) · PROJ-208 (2d ago)
Reviews waiting on you: not checked — no review tool in this session

Next: PROJ-233 — <the item's own summary>
Why:  critical · unblocks 2 (PROJ-240 → PROJ-244) · ready-for-agent · SP 3

Runners-up:
  PROJ-251 — <summary> (critical, SP 2)
  PROJ-219 — <summary> (ready-for-agent)

Needs a decision from you: PROJ-190 (needs-info)
Unmapped status: PROJ-177 ("Awaiting QA" — add it to the adapter)
Blocked (2): PROJ-208 ← PROJ-212 · PROJ-181 ← PROJ-208
```

When Step 3 refuses to pick, replace the `Next:` block with the reason and what
would free a slot — same header, no ranking section.

Drop any section that is empty. Name the pick and stop; starting its work is a
separate user decision.

## Anti-patterns

| Tempted to… | Don't, because… |
|---|---|
| Read a status or label name out of this file | There are none here, deliberately. They live in the adapter, which is the only thing that knows your workflow. |
| Guess a bucket for a status the adapter doesn't map | A silently misfiled status is a wrong pick that looks right. Report the hole. |
| Recommend an `active` item as "the next thing" | It is already picked. The question is whether there's room for one more. |
| Count a `parked` item against the WIP cap | It's waiting on someone else, so it's free. |
| Assume an `active` item needs the user's hands right now | It may be an agent run. Show when it was last touched and let them say. |
| Keep picking because the user waved the cap once | The cap is a cap. Past it, finishing beats starting. |
| Rank a backlog bug above a support ticket because it unblocks more | Work class comes first. Support is priority 0 on the ladder. |
| Recommend a `blocked` item because its blocker looks done | Verify the blocker's bucket. Recommending blocked work wastes the whole pickup. |
| Rank by story points first | Points are a tiebreak. Smallest-first is momentum, not direction. |
| Treat every blocking link as "is blocked by" | Half of them point outward. Read `outwardIssue` versus `inwardIssue`. |
| Offer a pick without saying whether reviews are pending | Reviews outrank new work. Silence reads as "none waiting". |
| Transition the pick "to help" | Whoever starts the work does that, after the user chooses. This skill only reads. |
| Re-fetch per candidate to fill in a missing field | One query, one jq pass. A field the search didn't return isn't worth a round-trip. |

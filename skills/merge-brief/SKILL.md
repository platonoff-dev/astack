---
name: merge-brief
description: |
  Pre-merge comprehension check for a change you are about to merge.
  Given a merge or pull request, a fresh-context subagent reads the request,
  the full diff, the commits, the tracker item (including its investigation and
  solution comments) and every discussion thread, then writes a
  plain-English Brief — what changed, why, which alternatives were
  rejected, the nuances a diff-reader would miss, and the residual risk.
  It then asks 2–5 consequence questions (never trivia) to find out
  whether the Brief landed, grades each answer on the spot, and hands the
  merge decision back to you. Blocks nothing, posts nothing, merges
  nothing, judges nothing. Built for MRs an agent wrote, where the real
  risk is rubber-stamping code you never read. Use when the user says
  "brief me on !1234", "what am I merging", "explain this MR before I
  merge", "quiz me on this change", or invokes /merge-brief.
---

# merge-brief

An agent can drive a ticket from To Do to merge-ready without you reading a
line of it. Everything in that pipeline checks the *code* — CI, BugBot,
RPM tests, `interrogate`. Nothing checks the *human* who clicks Merge.

This skill checks the human. It explains the change in English, then asks
whether the explanation landed. It has no authority: it cannot block, does
not post, does not merge, and never gets a vote on the change itself.

## When to use

- Right before clicking Merge on an MR an agent wrote for you.
- After a long agent run where you were away for the middle of it.
- Any time you catch yourself about to approve a diff you skimmed.

Do **not** use:

- To find bugs — that is `/interrogate`. This skill *explains*, it never
  judges. No lenses, no consensus, no verdict on the code.
- To review a design doc — that is `/architect` in review mode, or
  `/interrogate` against the doc.
- As a quality gate. It grades you, not the change, and it grades nothing
  that anyone else sees.
- On a colleague's request under review. It will run, but the "Why" sources
  assume your own agent-driven flow (the tracker item's investigation and
  solution comments), so the Brief degrades to what-only.

## Input

- MR IID: `1234`, `!1234`
- Full MR URL
- A branch name (most recent open MR for that branch)
- Nothing — the open MR for the **current local branch**

If several match, list them and ask. The forge and the project path come from
the tracker adapter's `[review]` table (`/setup-tracker`); with no adapter,
derive them from `git remote -v` and say which remote you used.

## Reads and writes

| Reads | Via |
|---|---|
| Request fields — title, description, SHA, target, state, draft | the forge's own read call |
| Every discussion thread, **resolved ones included** | the forge's discussions call |
| The full diff | `git diff origin/<target>..HEAD` (fallback: the forge's changed-files call) |
| Commit subjects | `git log origin/<target>..HEAD --oneline` |
| Tracker item, description, acceptance criteria, **all comments** | the tracker's get-item call |

Tool names differ between environments; use whatever calls this session has
rather than a name from memory.

**Writes: nothing.** No request comment, no tracker comment, no file. The Brief and
the score live in the conversation and nowhere else.

A resolved thread is not noise — it is usually the exact place a nuance got
decided. Read them.

## Phases

### P0 — Resolve & eligibility

- Resolve the request per §Input. Extract the tracker key from the title or
  the branch, using the adapter's `key_pattern`.
- **Closed** → stop, nothing to brief.
- **Merged** → continue, but label the Brief `(already merged)`.
- **No tracker key** → continue. The "Why" section degrades to the request's description
  plus commit subjects, and the Brief must say so out loud.
- **Diff > 2000 lines** → warn that nuance coverage may be partial, then
  continue. A behavior-organized Brief scales with subtlety, not line count.

### P1 — Brief (one fresh-context subagent)

Spawn **one** `feature-dev:code-explorer` subagent (`general-purpose` if
that type is unavailable). It reads all five sources itself — do not
pre-digest them in the main loop.

Fresh context is the point, not an optimization: when this skill is
invoked at the end of an agent run, the main loop *wrote the code*, and
a Brief written from the author's memory describes intent rather than the
diff.

Give the briefer: the request identifier, the tracker key, the target branch,
the §Briefer rules verbatim, and this schema.

```
{
  "brief": {
    "tldr": "<one sentence: the whole change>",
    "why": "<root cause or motivation; the approach chosen; alternatives rejected and why>",
    "why_sources": ["tracker:PROJ-N comment 3", "thread 2", "commit abc1234"],
    "changed": [{"behavior": "<what is now different>", "cite": "<file:line>"}],
    "nuances": [{"id": 1, "nuance": "<what a diff-reader would miss>", "cite": "<file:line | thread N | tracker comment>"}],
    "risk": "<blast radius, untested paths, known flakes>"
  },
  "questions": [
    {
      "nuance_id": 1,
      "question": "<consequence question>",
      "expected": "<the answer, one or two sentences>",
      "acceptable_partial": "<what a half-right answer looks like>",
      "where_the_answer_lives": "<file:line | thread N | tracker comment>"
    }
  ],
  "no_questions_reason": "<only when questions is empty>"
}
```

### P2 — Render the Brief

Print it in chat, exactly this shape, ~400 words:

```
# !<id> — <KEY>: <title>              [(already merged)]

**TL;DR** — <one sentence>

**Why** — <root cause; approach chosen; what was rejected and why>

**What changed**
  • <behavior>                          <file:line>
  • <behavior>                          <file:line>

**Nuances**
  1. <what a diff-reader would miss>    <file:line | thread N>
  2. <…>

**Risk / not covered** — <blast radius, untested paths>
```

### P3 — Quiz

One question per Nuance: floor 2, cap 5, typical 3. Ask them **one at a
time** and wait for the answer.

If `questions` is empty, print `no_questions_reason` instead and stop —
a one-line version bump has nothing to misunderstand, and theatre is worse
than nothing.

Answers are free text, one sentence, **in any language** — the Brief is
English, the grading is not. `I don't know` is always a valid answer and
routes straight to the explanation with no scolding.

The quiz needs a human present. If invoked by a parent skill on an
unattended tick, render the Brief, say how many questions are ready, and
stop.

### P4 — Grade & hand back

Grade each answer the moment it arrives against `expected` /
`acceptable_partial`:

```
✓ correct — <one line, only if they added something worth confirming>
~ partial — <the half they missed> — <cite>
✗ miss    — <the nuance, in two lines> — <cite>
```

Then close:

```
merge-brief: <k>/<n>. Missed: <nuance names, or "nothing">.
<one action: "re-read <cite> before you merge", or nothing>
Your call — nothing is blocked.
```

## Briefer rules (verbatim, give to the subagent)

1. **Behavior-first, never file-first.** The diff is already organized by
   file; re-listing files teaches nothing. Group by what is now different.
2. **Every claim cites something** — `file:line`, `thread N`, a tracker
   comment, or a commit SHA. An uncited claim is a guess.
3. **A Nuance is something true that a reader of the diff would not see** —
   an upgrade path, an ordering constraint, a rejected alternative, a
   default that only applies to fresh installs. If the diff shows it
   plainly, it is not a Nuance.
4. **Never invent motivation.** If the *why* is not in the tracker item, its
   comments, the request description, the threads, or the commits, write
   `not recorded` and move on. Fabricated motivation is worse than an
   admitted gap.
5. **One question per Nuance**, floor 2, cap 5. Fewer than 2 real Nuances →
   return what you have. Zero → `questions: []` plus
   `no_questions_reason`.
6. **Consequence questions only.** "What happens if…", "what breaks if…",
   "why not X". Banned: file names, line numbers, counts, values, and
   anything answerable by quoting the Brief.
7. **You explain; you do not review.** If you spot a real bug, one line
   under `risk` pointing at `/interrogate`. No severities, no verdict.

### Question examples (give these verbatim too)

```
GOOD
  • A host upgraded from 6.x keeps the old 5s timeout. Does this MR fix
    the dropped-task bug there? Why?
  • The queue rewrite was rejected. What would it have bought us that
    this doesn't?
  • If the broker stays down 10 minutes, what happens now?

BANNED
  • Which file holds the timeout constant?   (trivia)
  • How many files changed?                  (trivia)
  • What is the new timeout value?           (verbatim in the Brief)
```

## The dispute path

An answer that contradicts `expected` is not automatically a Miss. Before
grading it, re-read the cited hunk in the diff.

- The answer is wrong → Miss, explain the nuance.
- **The answer is right and the change is wrong** → say so:
  `"your answer contradicts the change and I think you're right: <one
  line>. Run /interrogate on !N before merging."` Do not score it. Do not
  argue.

A comprehension check that punishes the developer for catching a real bug
is worse than no check at all.

## Caps

| Resource | Cap |
|---|---|
| Briefer subagents | 1 |
| Questions | 5 (floor 2, or 0 with a reason) |
| Diff size before warning | 2000 lines |
| Brief length | ~400 words |
| Re-brief, standalone | unlimited — ask twice, get twice |
| Re-brief per `head_sha`, from a parent skill | 1 |

## Integration (documented, not wired)

Not wired into anything — invoke it by hand. The intended attachment point,
if a merge-ready orchestrator ever calls it: render the Brief inline with
the merge-ready signal, so the TL;DR crosses your eyes before "click Merge"
is reachable, and offer the quiz for the user's next message (that signal
can fire while nobody is watching):

```
!1234 is merge-ready. CI ✓ security scan ✓ threads ✓

── Brief ──
…

3 questions ready. Reply "quiz", or click Merge: <url>
```

## Antipatterns

| Tempted to… | Don't, because… |
|---|---|
| Ask a question the Brief answers verbatim | It tests scrolling, not understanding. |
| Organize the Brief by file | The diff already is. Behavior or nothing. |
| Pad up to 3 questions on a simple change | Banned trivia is the only available padding. Return 2, or 0. |
| Guess why the change was made | `not recorded` is information; a plausible invention is a lie. |
| Grade a correct dispute as a Miss | Punishes the one behavior you most want. Worst failure this skill has. |
| Post the Brief or the score anywhere | By merge time reviewers already approved, and a recorded score has no reader. |
| Grow lenses, severities, or a verdict | That is `interrogate`. This skill explains. |
| Run the quiz on an unattended tick | Nobody is there. Brief now, quiz when they reply. |
| Re-brief an unchanged `head_sha` on every parent tick | Burns a subagent to re-read the same diff. |
| Block, gate, or nag about the merge | It has no authority. State the score and get out of the way. |

## Signals to surface

- "Brief ready — <n> questions when you are."
- "Nothing worth quizzing: <no_questions_reason>."
- "Why not recorded — no investigation comment, no request description.
  Brief covers what, not why."
- "Diff is <n> lines — nuance coverage may be partial."
- "Your answer contradicts the change and I think you're right — run
  /interrogate on !<n> before merging."
- "merge-brief: <k>/<n>. Your call — nothing is blocked."

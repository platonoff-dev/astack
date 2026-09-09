# Language: Simplified Technical English for a status report

The section is written in ASD-STE100 Simplified Technical English (Issue 9,
January 2025, 53 writing rules and a dictionary of about 900 approved words),
adapted for descriptive text read by executives. STE was built so that a
non-native reader understands a maintenance manual the first time. That is
exactly the CEO's complaint: background, clarity, conciseness, no slang.

The linter (`scripts/lint_report.py`) enforces the mechanical part. This file
is for the judgement part.

## STE rules that matter here

Grouped as the standard groups them. Thresholds are the standard's.

**Words**
- Use a word in one meaning and one part of speech. "Check" is a verb here,
  not a noun. Pick one name per thing and keep it: "the message queue" in
  sentence one is not "the buffer" in sentence three (unslop 11).
- Prefer the approved plain word (table below). Technical names are allowed
  as names: the product name, the package name, "WordPress", "the agent".
  A technical name still needs one plain clause the first time it appears:
  "the resident agent (the part of our software that stays running on the
  customer's server)".
- No slang, no jargon, no idiom. If a phrase would not appear in a manual,
  it does not appear here.

**Noun phrases**
- No more than three nouns in a row. "Agent message delivery loss counter"
  becomes "the counter for lost agent messages".
- Use articles. "Queue drains at consumer rate" reads as a headline; "the
  queue drains at the rate the server can accept" reads as English.

**Verbs**
- Approved forms only: infinitive, imperative, simple present, simple past,
  simple future, past participle as an adjective. No progressive ("we are
  implementing"), no gerund openers ("Implementing X for …"). Write "we
  implement", "we started X".
- Active voice. Name the actor: "we merged", "the server rejected", "the
  release owner accepted". Passive is allowed only when the actor is unknown
  or truly irrelevant.
- Use a verb for an action, not a noun made from a verb: "we verified"
  instead of "verification was performed".

**Sentences**
- Descriptive text: at most 25 words per sentence. Vary length; short
  sentences after long ones.
- One topic per sentence. Do not drop articles or verbs to fit.
- Vertical lists for more than two parallel items.

**Paragraphs**
- At most six sentences. Start with the sentence that carries the result.
- Present information in the order the reader needs it: result, number,
  date, why it matters, then the ticket link.

**Punctuation**
- No semicolons. No dashes as connectors (no em dash, no en dash, no
  hyphen-as-dash). Colons only before a list or a value. Parentheses only for
  a unit, an expansion, or a ticket key.
- Numbers as digits, with thousands separators: 9,305 servers. Percentages
  with the base: 86% (31/36). Ranges with "to": 1% to 25%.
- No calendar dates in prose. The ETA column (dd/mm/yy) is the only date in
  the section. Time in the text is a delivery stage (merged, in review, in
  beta, on all servers) or a duration ("paused 2 weeks").

## Plain-word substitutions

Left column: what the drafts keep producing. Right column: what to write.

| Instead of | Write |
|---|---|
| utilize, leverage | use |
| perform, conduct, carry out, execute | do, run |
| implement | make, add, write, build (say which) |
| ensure | make sure |
| assist, facilitate | help |
| obtain, acquire | get |
| require | need |
| commence, initiate, kick off | start |
| terminate, cease | stop |
| modify, alter | change |
| locate | find |
| demonstrate, indicate | show |
| approximately | about |
| prior to, subsequent to, following | before, after |
| in order to | to |
| due to the fact that, since (cause), as (cause) | because |
| in the event that | if |
| numerous, a number of, multiple | the number, or "many" only with the number |
| in excess of | more than |
| additional | more |
| sufficient | enough |
| verify, validate | check, test, confirm |
| resolve (a ticket) | close, fix |
| mitigate, remediate | reduce, prevent, fix |
| address (a problem) | fix, answer |
| land, landed | merge, merged; "is in version X" |
| ship, shipped | release; "reached all servers"; "merged, not yet released" |
| roll out | release to N% of servers |
| deploy | install, release |
| flaky | fails at random, fails intermittently |
| regression | a bug that came back; we broke X that worked before |
| hardening | making X fail less often (say how much) |
| observability, telemetry | monitoring data, measurements |
| harness | test setup |
| pipeline, CI | automated checks |
| backlog | planned, not started |
| in flight | in progress |
| green (checks) | all checks passed |
| poison message | a message the server will never accept |
| black hole | data that was silently lost |
| the fleet | all customer machines (give the count) |
| ack, acknowledge | confirm |
| dedupe, deduplication | remove duplicates |
| triage | sort by priority, investigate |
| unblock | no longer waits on |
| MR, merge request (in prose) | the code change; link it once, by number |

## Acronyms and product names

No acronyms; expand on first use, even the ones the team's own template
uses. The linter flags any capitalised token of two to seven
letters that is not expanded somewhere in the section and is not in its
short allow list (Jira project keys, AI, units, PHP, HTML, URL, IP).

| Token | First use |
|---|---|
| MR | merge request (a proposed code change) |
| CI | automated checks that run on every code change |
| QA | quality assurance (the test team) |
| ETA | estimated completion date |
| API | application programming interface (the way programs talk to our servers) |
| CVE | a publicly listed security vulnerability |
| AV | antivirus; name the antivirus-only product, if you ship one |
| a package name | expand what the package does on first use |
| a broker or transport name | "the message transport between the customer's machine and our cloud" |
| SQLite | the local database on the customer's machine |
| HTTP | the web protocol |
| OS | operating system |
| VM | virtual machine |
| RPM, rpm-tests | software package; the automated installation tests |
| LXC/LXD | Linux containers |
| OKR, KR | objectives and key results; key result |
| FP, FN | a clean file wrongly flagged as malware; malware that was missed |
| UI, CLI | user interface; command line |
| MDS | malware detection scanner |
| a customer or partner name | never abbreviated to initials the reader must decode |
| PROJ-12345 | a tracker key; keep as is, always linked |

## What "human language" means here

The standing request is human language, no filler, no slang. Test: read the
sentence aloud to someone outside engineering. If you would rephrase it for
them, rephrase it in the report.

- "The resident send queue can no longer be poisoned, and drains at the
  consumer's pace" becomes "A message the server will never accept no longer
  blocks the messages behind it, and the queue now sends at the speed the
  server can take."
- "Every message drop path now has a counter, merged behind a flag" becomes
  "Every place a message can be lost now counts the loss. The counters are
  merged but switched off until the server side deploys its part."

## Applying `unslop`

Run the unslop skill's pattern list over the draft as the
second editing pass. Two adaptations for this document:

- Skip unslop's "Adding soul" section. A status report has no opinions and no
  first-person feelings. Its voice comes from specific numbers, dates and
  honest statements about what slipped.
- "I" and "we" are both fine. "I" for what you did alone, "we" for the team
  or the product. The report asks for human language; the passive is not it.

Everything else in unslop applies verbatim: no em dashes, no inline-header
bullets, no rule-of-three padding, no "not just X but Y", plain words, active
voice, say what it does and not how it feels.

## Banned by name

The linter's ERROR lists, so you can read them without opening the script.

- **Slang**: landed, land, nailed, tackle, kick off, ramp up, deep dive,
  heads-up, low-hanging, circle back, touch base, in flight, black hole,
  poison, drown, trickle, blast, scope creep, vibe, slop, sanity check, happy
  path, hot path, greenfield, north star, flywheel, quick win, nuke, bump,
  ping, flaky, guardrail, footgun, rabbit hole, stays dark, trip (a
  mechanism), dogfood, hacky, gotcha, kill (a process).
- **Expressive without a number in the same sentence**: aggressive,
  significant, massive, huge, critical (except as the Jira priority name),
  urgent, dramatic, enormous, tremendous, substantial, considerable,
  extensive, major, largest/biggest/smallest/fastest/highest/lowest,
  drastically, immensely, incredibly, extremely, very, really, highly, rapid,
  quickly, vast, serious, severe, important, essential, heavy, a lot, key.
- **Vague quantity without a number**: many, several, numerous, multiple, a
  number of, a few, few, most of, the most, majority, various, a couple of,
  plenty, countless, a handful, some of.
- **AI vocabulary**: additionally, crucial, delve, enduring, enhance, foster,
  garner, interplay, intricate, landscape, pivotal, showcase, tapestry,
  testament, underscore, vibrant, robust, seamless, leverage, utilize,
  streamline, holistic, synergy, empower, elevate, unlock, journey,
  ecosystem, paradigm, comprehensive, cutting-edge, state-of-the-art,
  game-changer, transformative, "not just", "it is worth noting", "in order
  to", "due to the fact", "serves as", "the bigger story".
- **Latin**: e.g., i.e., etc., vs., via.
- **Punctuation**: semicolons, em dashes, exclamation marks, emoji.
- **Placeholders**: `[?]`, TODO, TBD, `paste-link`, `{date}`, `dd/mm/yy`,
  `[none]`, `[no epic in progress]` left in a filled section.

Warnings (WARN) cover jargon, absolute claims, references to a previous report,
-ing forms, passive voice, sentences with no number in This week, numbers
without thousands separators, and duplicate content between blocks.

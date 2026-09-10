# The tracker adapter, field by field

TOML. Every table below is optional except `[tracker]` and `[statuses]`; an
omitted role means "we do not use that concept", and the reading skill degrades
by saying so rather than by guessing. `tracker_adapter.py init` writes a
commented template with these defaults.

A role is a *name a skill may use*. A value is a *name your tracker uses*. The
adapter is the only place the two meet.

## `[tracker]`

| Key | Required | What it is |
|---|---|---|
| `kind` | yes | `jira`, `linear`, `github`, `gitlab` or `other`. Chooses the query vocabulary a skill reaches for, not the tool: skills use whatever search call the session has. |
| `project` | yes | The project key or slug work items carry. |
| `key_pattern` | yes | A regex matching one key, for pulling a key out of a branch name or a title. Must compile. |
| `browse_url` | yes | A template containing `{key}`, e.g. `https://example.atlassian.net/browse/{key}`. Every link a skill writes comes from here. |
| `cloud_id` | no | Jira Cloud id, when the connector in use demands one. |

`[tracker.fields]` maps a role to the tracker's own field id — `story_points`,
`team`, or anything else a skill is told to read or set. `[tracker.field_values]`
maps a role to the value to write on a new item, for fields whose value is a
fixed id rather than something derived from the work.

## `[me]`

`account_id`, when a query needs your id rather than a `currentUser()`
equivalent. Nothing else. This is an identifier, not a credential.

## `[statuses]` — the bucket roles

Five roles, all required, and **a status may appear in exactly one of them.**
This is the mapping every bucketing decision is made from, so an unmapped
status is a silent wrong answer.

| Role | Means |
|---|---|
| `active` | being worked on now. Costs a slot against the WIP cap. |
| `parked` | waiting on someone else — review, support, a deploy. Costs no slot. |
| `blocked` | cannot start, by status. |
| `excluded` | finished or abandoned; never a candidate, never a blocker. |
| `shovel_ready` | available to start. |

## `[labels]` — the label roles

| Role | Means |
|---|---|
| `needs_info` | an open question the reporter owes. Never a pick. |
| `needs_triage` | refinement backlog; definition of ready not met. |
| `wontfix` | not going to be done. Treated as excluded. |
| `ready_for_agent` | scoped tight enough to hand to an agent. Ranks up. |
| `ready_for_human` | needs a person: a live machine, a judgement call, a demo. |
| `test_suite` | the work is in the test or CI suite itself. A ladder class. |
| `ignore` | track and hygiene markers that sit on nearly everything and mean nothing for ranking. Listing them here keeps them out of the report. |

Write your tracker's own label spelling. A role may list several labels, and an
empty role is fine.

## `[issue_types]` — the type roles

`support`, `release`, `epic`. Only these three change an answer: support work
tops the ladder, an in-flight release is its owner's top priority, and an epic
is a container rather than a unit of work. Every other type ranks alike, so
none of them needs a mapping.

## `[wip]`

`cap` — items allowed in `active` at once. `stale_days` — an active item
untouched for this long is not running, it is rotting.

## `[ladder]`

`classes`, most urgent first, and the last one must be `other`. `critical` is
computed from priority; `support`, `release` and `test-suite` come from the
type and label roles above. Drop a class your team does not distinguish; the
order is your team's written work order, not a default worth arguing with.

## `[review]`

`forge` is `gitlab`, `github` or `none`. When it is not `none`, `project` is
required — the `group/repo` path review requests live under. `request_url` is
an optional template containing `{id}`.

## `[report]`

Read by `weekly-report` only.

| Key | What it is |
|---|---|
| `destination` | `slite`, `confluence`, `file` or `none`. `none` means draft-only: the skill never publishes. |
| `readers` | who reads the report, by role. One phrase, e.g. `the CEO, the product lead, marketing and your manager`. It calibrates how much explanation each sentence needs. |
| `section_heading` | the heading your own block sits under in a shared document. |
| `blocks` | the block titles, in order. The skill writes exactly these and nothing else. |

## What must never go in

Credentials, tokens, API keys, cookies. Verbatim quotations from private
channels or documents. Colleagues' names. Real work-item titles or numbers.
The adapter is configuration read by a machine — if a value would embarrass
someone were the file leaked, it is not configuration, and a skill does not
need it to do its job.

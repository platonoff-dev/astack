# 001 — Should this repo have a skill for deciding what to take from other people's setups?

- **Date:** 2026-08-31
- **Verdict:** adopt
- **Touches:** `.agents/skills/prior-art/`, `.claude/skills/prior-art` (symlink),
  `scripts/prior_art.py`, `prior-art.json`, `docs/decisions/`, `.gitignore`

## Failure it prevents

Two failures, both already live. First: deciding what belongs in this repo by
recalling what pstack or mattpocock/skills do, when a model's recollection of a
repo layout is confident and wrong — this session started by "knowing" both
setups and got the shape of each wrong until the files were on disk. Second:
adoption by vibes. `unslop` was vendored because it looked good, with no record
of what it prevents, so nothing tells a future session whether it earned its slot
or how to tell if it stops earning it.

## Sources read

- `pstack` @ fd878692de15 — `README.md`, `skills/` (48 `SKILL.md` measured, 3
  read in full), `skills/create-verification-skill/SKILL.md`,
  `skills/principle-encode-lessons-in-structure/SKILL.md`
- `mattpocock-skills` @ a97b87386667 — `AGENTS.md`, `.agents/adr/`,
  `.out-of-scope/`, `scripts/link-skills.sh`, structure of `skills/`
- Not read: pstack's `docs/guide/`, `automations/benny/`, and 45 of its skill
  bodies; every mattpocock skill body. The decision rests on structure, not on
  the prose inside individual skills.

## Mechanism

What the two setups share, measured rather than remembered:

| | pstack | mattpocock-skills |
|---|---|---|
| `SKILL.md` files | 48 | 37 |
| median body | 553 words | 493 words |
| `disable-model-invocation: true` | 42 of 48 | 22 of 37 |
| detail pushed into `references/` | 11 skills | 0 (uses `docs/`, `.agents/`) |

Both keep bodies short and both distrust description-matching: the large majority
of skills are reachable only when the human names them. Neither is a bag of tips
— pstack routes through one entry-point skill (`poteto-mode`, 22 playbooks) and
mattpocock through a router skill plus promotion buckets, where only the
`engineering/` and `productivity/` buckets ship in the plugin.

The two mechanisms worth taking:

- **The graveyard.** mattpocock keeps `.out-of-scope/` — one file per rejected
  request, each citing the issue that asked for it — alongside `.agents/adr/`.
  It is the only place in either repo that says what did not work, and it is what
  stops the same request arriving forever. Nothing here recorded a rejection.
- **Encode the lesson in structure, not in text** (pstack's
  `principle-encode-lessons-in-structure`, and its `create-verification-skill`,
  which generates a per-repo skill whose whole job is a runnable check). The
  equivalent here is a fetch tool with a `diff` that fails, not a paragraph
  asking the model to check whether upstream moved.

## Fit

Survives: both are single-person Markdown setups with no shared services, which
is exactly this repo's shape. The "short body, detail in `references/`" split is
already this repo's stated convention.

Breaks: pstack's multi-model panel (Cursor-specific), mattpocock's docs site,
changesets, npm version sync and issue-tracker coupling. Their runnable checks
are test suites and validators; this repo has neither, so the check has to be
the one thing it does have — git, a pin, and a diff against what was read.

## Verdict

Build it here rather than vendor anything. Three parts:

1. `.agents/skills/prior-art/SKILL.md` — the loop, with the two clauses that
   make it say no: no named failure means *defer*, and never describe a setup
   from memory. Real file under `.agents/skills/` with a symlink at
   `.claude/skills/prior-art`, matching the `CLAUDE.md → AGENTS.md` pattern.
   Verified a fresh Claude Code session resolves the symlink and lists the skill.
2. `scripts/prior_art.py` — `list / pull / diff / seen / approve / add`, reusing
   `vendor.py`'s sparse blob-filtered fetch. Working copies land in gitignored
   `.cache/prior-art/`; `diff` exits 1 when a source moved since it was read.
   Read is deliberately separate from vendor: vendoring copies a component in to
   *use* it, this fetches one in to *read* it, and conflating the two is how a
   reading copy quietly becomes a dependency.
3. `docs/decisions/` — this file being the first, and the trial run of the loop.

Cost to keep: one more model-invoked skill in a repo that has two, plus ~6 s and
~500 KB per `pull`. Registered sources are `pstack` and `mattpocock-skills` only;
six more are listed as candidates for Anatolii to approve, not tracked.

## What would reverse this

- `docs/decisions/` still holds only this file in three months: the skill is
  ceremony, delete it.
- Decisions get written but never consulted — a later session re-researches
  something a record already settled.
- Either harness grows a first-class way to read pinned upstream sources, making
  `prior_art.py` redundant.

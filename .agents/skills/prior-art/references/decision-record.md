# Decision records

One file per decision in `docs/decisions/`, named `NNN-short-slug.md` with `NNN`
the next free three-digit number. Never renumber or rewrite history: supersede a
decision with a new one that links back.

Rejections and defers get a record too. The record is what stops the same idea
being researched a third time, so a two-paragraph *no* is worth more than a
polished *yes*.

Keep it to one screen. If the reasoning needs more, the decision is too big —
split it.

## Template

```markdown
# NNN — <the question, as a question>

- **Date:** YYYY-MM-DD
- **Verdict:** adopt | vendor | reject | defer
- **Touches:** <files or components this changes, or "nothing">

## Failure it prevents

<The concrete thing that went wrong, and where. "Nothing yet" means the verdict
is defer.>

## Sources read

- <name> @ <sha12> — <path/inside/the/source>, <path>
- <URL> — read YYYY-MM-DD

## Mechanism

<What they actually do, in your own words: what it forbids, what check enforces
it, when it loads, what it assumes. Numbers where you have them.>

## Fit

<Which of this repo's constraints it survives, and which it breaks: two
harnesses, one person, no build or test suite, Markdown and JSON artifacts,
install cached by version.>

## Verdict

<What gets built, vendored, or dropped, and what it costs to keep. For adopt:
what the trial run showed.>

## What would reverse this

<The observation that should make a future session reopen it — a component that
never fires, a harness gaining the feature natively, upstream moving.>
```

## Rules

- **Cite commits, not branches.** `pstack @ fd878692de15` is checkable in a year;
  "pstack's README" is not.
- **Quote numbers you measured**, not impressions. "42 of 48 skills are
  user-invoked" beats "they seem to prefer explicit invocation".
- **Name what you did not read.** A decision that skipped half the source is
  still valid; one that pretends otherwise is not.
- **After writing it,** run `python3 scripts/prior_art.py seen <name>` so `diff`
  can tell you later when the ground moved under a decision.

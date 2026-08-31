# Reading someone else's setup

## Read order

A published setup is mostly marketing at the top and mechanism at the bottom. Go
bottom-up.

1. **Measure before reading** (commands below). Fifty skills at a 500-word median
   is a different animal from six at 2,000, and you can know which before
   spending a token on prose.
2. **`README.md`, then `AGENTS.md` / `CLAUDE.md`.** The README is the author's
   pitch; the agent file is the rules they actually enforce on themselves. When
   the two disagree, believe the agent file.
3. **Every `description:` at once.** The descriptions are the routing surface —
   the only part of a skill the model sees until it fires. Reading all of them
   together shows whether the set has clean boundaries or is a keyword soup that
   makes every skill fire on everything.
4. **Three bodies in full:** the entry point or router, the smallest skill, and
   the one relevant to your question. Skip the rest.
5. **The graveyard.** `deprecated/`, `.out-of-scope/`, ADRs, "why not X" sections.
   This is the highest-signal-per-token part of any setup: it is the only place
   the author says what did not work, and it is what nobody copies.

## The four questions

For each thing you're tempted to take:

1. **What does it forbid?** A component that only encourages good work adds
   nothing a system prompt doesn't already say. Find the sentence that stops the
   model doing something it would otherwise do. If there isn't one, stop here.
2. **What is the deterministic check?** A script, a lint, a revert test, a
   validator, a command whose exit code decides. Instructions that cannot fail
   are a preference, not a discipline. Note whether the check exists or the skill
   only *asks* the model to be careful.
3. **When does it load, and what does it cost?** Model-invoked or user-invoked?
   How big is the body, and what does it drag in? Does it spawn subagents or
   extra model calls, and how many? An always-on skill is a permanent tax on
   every unrelated task in the repo.
4. **What does it assume?** A team, a tracker, a CI service, a language,
   a paid model panel, one harness. Assumptions are what makes a copied setup
   quietly useless — they rarely appear in the README.

## Measuring a setup

Run these against `.cache/prior-art/<name>/`. They answer "what shape is this?"
without reading it, and they are the numbers a decision record should quote.

```sh
S=.cache/prior-art/<name>
find $S -name SKILL.md | wc -l                              # how many skills
find $S -name SKILL.md -exec wc -w {} + | sort -n | tail -5 # the fat ones
grep -rh '^description:' $S --include=SKILL.md              # the routing surface
grep -rl 'disable-model-invocation' $S --include=SKILL.md | wc -l   # user-only skills
find $S \( -name '*.sh' -o -name '*.py' -o -name '*.mjs' \) | head  # real checks
find $S -type d \( -name references -o -name deprecated -o -name '.out-of-scope' \)
```

A high user-invoked ratio means the author does not trust description-matching to
route — worth knowing before adding a fortieth model-invoked skill here.

**A missing key is not a choice.** Before reading a zero as a decision, check
which keys the setup uses at all: `anthropics/skills` and Codex's bundled skills
never write `disable-model-invocation`, so counting it there measures their
frontmatter vocabulary, not their opinion on routing.

```sh
find $S -name SKILL.md -print0 | xargs -0 -I{} sh -c \
  "awk 'BEGIN{n=0} /^---$/{n++; next} n==1 && /^[a-z_-]+:/{print \$1}' {}" |
  sort | uniq -c | sort -rn
```

## Worth copying / worth skipping

**Worth copying.** It says no somewhere. Its checks run. Median skill body stays
short with detail pushed into references loaded on demand. It has a graveyard.
The author ships with it daily and shows the failure modes, not just the wins.

**Worth skipping.** Dozens of role-play subagents with overlapping descriptions.
Reference manuals restating a language's docs. A description written to match
everything. No rejected ideas anywhere. A setup whose value depends on a service,
tracker or model panel that isn't in play here.

## What survives translation

This repo is two harnesses, one person, no build, no tests, Markdown and JSON.
Almost nothing translates verbatim. The transferable part is usually the
constraint, not the file: *"generate a per-repo verification skill"* survives,
their Playwright recipe does not. Write the constraint down in the decision
record and build the component from it — that is the difference between owning a
setup and renting one.

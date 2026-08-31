---
name: prior-art
description: Decide what to take from someone else's agent setup, and answer "what works now, who does this how" questions about agentic-AI setup design. Use when weighing whether to add, adapt, vendor or reject a skill, subagent, command or hook in this repo, when comparing this setup against pstack, mattpocock/skills or another published one, or when a claim about current practice needs checking. Reads sources at a known commit, never from memory, and ends in a decision record. Never registers a new source or vendors anything without Anatolii's approval.
---

# Prior art

**Turn "they do X, should I?" into a recorded decision backed by source you actually read.**

Two modes:

- **Question** — "how does pstack route between skills?", "is anyone still writing hooks?" Answer from the cache, citing file paths and the commit. Record nothing unless the answer changes this repo.
- **Decision** — "should this repo have X?" Run the whole loop and write a decision record.

## The loop

1. **Name the failure it prevents.** Which concrete thing went wrong here, in a sibling repo, or in a session Anatolii remembers? No named failure, no adoption: the verdict is *defer*, say so, stop. Most ideas die at this step and that is the point.
2. **Pull the source.** `python3 scripts/prior_art.py pull [name]`, then read `.cache/prior-art/<name>/`. Never describe someone's setup from recall — recollection of a repo layout is confident, specific and wrong often enough to poison the decision. For a blog post or vendor doc, fetch the page and cite URL plus date.
3. **Extract the mechanism, not the prose.** [references/mechanism.md](references/mechanism.md): the read order, the four questions, and the greps that measure a setup instead of admiring it.
4. **Test the fit** against what this repo actually is: two harnesses, one person, no build and no test suite, Markdown and JSON artifacts, install cached by version. Anything assuming a team ritual, a shared tracker, a CI service or a JS toolchain fails here — say which assumption broke rather than quietly dropping the idea.
5. **Pick one verdict:** *adopt* (rewrite it in Anatolii's words as a new component), *vendor* (verbatim, licence and pin, via `scripts/vendor.py add`), *reject*, *defer*. Prefer adopt over vendor: a skill he can't restate is one he can't debug when it misfires, which is the whole reason this repo exists instead of installing theirs.
6. **Trial before you commit.** Run the candidate on one real task in this repo first. A skill that never fires, or fires on everything, has already failed — report that instead of shipping it.
7. **Record it** in `docs/decisions/NNN-slug.md` ([template](references/decision-record.md)), then `python3 scripts/prior_art.py seen <name>`. Rejections get a record too; an unrecorded rejection gets researched again in three months.

## Boundaries

- Propose, never enrol. A new setup goes into `prior-art.json`'s `candidates` with
  one line on what it is good for; Anatolii takes it on with `prior_art.py approve
  <name>`. Vendoring or installing a third-party plugin needs his explicit yes too.
- Never hand-edit `.cache/prior-art/` — `pull` replaces it wholesale. It is reading material, not a working tree.
- One adoption per decision. Two changes at once means neither gets a trial.
- Cite as `<source> @ <sha12> — <path>`. An uncited claim about someone else's setup is a guess.
- Before trusting a decision older than a month, run `python3 scripts/prior_art.py diff` and say whether the ground moved.

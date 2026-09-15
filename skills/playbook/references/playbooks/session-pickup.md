### Session pickup

**You own the resume point. Read the prior trail, don't redo it.**

1. Locate the prior trail. Sources, in order of authority: a resume note or
   other scratch notes in the scratch location the Scratch location section
   of `SKILL.md` resolves (in astack, `.local/`); a
   [show-me-your-work](../../../show-me-your-work/SKILL.md) decision trail if
   one exists; git state (current branch and worktree, `git log` and
   `git diff` against the base, stashes, other worktrees); and the harness's
   own session history where it is accessible, such as a resumable prior
   session or its transcript. Stay inside the active project; do not read
   other projects' sessions or scratch. Read the overview and the last entries
   first, then scan back for the decision points. Parse a long trail in a
   worker and keep the reduced timeline in the main thread
   ([Guard the Context Window](../../../principles/references/guard-the-context-window/reference.md)).
2. Reconstruct operational state. The branch and worktree, what already
   landed, the open todos, the decisions made. The prior trail is
   authoritative input. Resist the bias to re-derive it.
3. Diff done vs pending. Compare what shipped against what was planned, name
   the resume point, and do not re-run the prior repro or redo completed work.
   A "let me verify from scratch" pass means you're treating the trail as
   untrustworthy when it's authoritative.
4. Route the remaining work to the matching playbook and pick the verdict:
   continue the execution, ship a finished recommendation, ratify or override
   a prior conclusion, or postmortem a failed run. The pickup playbook ends
   here. The routed playbook owns the rest, with the project's mandatory steps
   merged in as usual.
5. Verify the inherited claims against the original goal on the real artifact
   ([Prove It Works](../../../principles/references/prove-it-works/reference.md)).
   A passing prior self-report is not the proof.

**Reply:** where the prior session stopped, what you inherited vs redid
(ideally nothing redone), the resume point, and the outcome.

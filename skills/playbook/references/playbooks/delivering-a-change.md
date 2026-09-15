### Delivering a change

Invoked at the end of every playbook that changes code.

**Project first.** The project's `CLAUDE.md` / `AGENTS.md` defines the
delivery flow: the forge, the branch and title format (for example where a
ticket key such as `PROJ-123` goes), draft status, reviewer selection,
required remote test suites, and review bots. Those rules sit ahead of
everything below and override any conflicting check here. This playbook fills
the gaps the project left open.

1. **Workspace.** Work on a branch off the project's trunk. When parallel work
   shares the checkout, give each writer its own worktree; concurrent writers
   never share one. Dirty branch with unrelated work: patch out, fresh
   worktree, apply. Snarled worktree: reset from trunk, redo minimally.
2. **Commits.** Commit liberally while working. Rebase into small, ordered
   commits before requesting review. Each commit is landable on its own and
   ordered to tell the story
   ([Sequence Verifiable Units](../../../principles/references/sequence-verifiable-units/reference.md)).
   Amend when the fix belongs in a just-made commit. New commit when
   separable.
3. **Subject.** Unless the project prescribes a format, use a Conventional
   Commits subject, `type(scope): subject`, with `feat`, `fix`, `docs`,
   `refactor`, `test`, `chore`, or `perf` as the type and the changed area as
   the scope, for the commit subject and, unless the project prescribes a
   title format, the change request title. Keep it short and imperative, name
   a real symbol when one carries the change, and add no trailing period. For
   example, `fix(scheduler): retry idempotent jobs after lease expiry`.
4. **Body.** The body of the change request and its squash commit is a
   briefing, not the lab notebook. A reviewer who has the diff should learn
   why the change exists, what is out of scope, and how you proved it works.
   Write it with [technical-writing](../../../technical-writing/SKILL.md)
   (every layer except Diátaxis), then apply
   [unslop](../../../unslop/SKILL.md). If the body would run past about 40
   lines, cut it. When the project defines no body format, use these sections
   in order and drop a section that has nothing to say:
   - `## Why`. Intent and approach in one or two short paragraphs. No SHAs,
     no rebase genealogy, no "based on main" preamble.
   - `## Scope`. Bullets naming real symbols and paths. Name both sides of a
     rename or retarget. State what is in and out only when the boundary
     matters.
   - `## Tradeoffs`. Only rejected alternatives a reviewer would otherwise
     ask about. Skip when there was no real choice.
   - `## Blast Radius`. One to three sentences on who or what the change
     touches and why it is safe or risky. Load
     [blast-radius](../../../blast-radius/SKILL.md) when the change reaches
     shared code you do not fully trust.
   - `## Verification`. Each real run path and its outcome. For a
     performance change, one primary number with its unit as
     `before → after`. Link the arena or swarm directory for the remaining
     evidence.

   Attach screenshots or recordings when they prove a claim. Do not paste
   full SHAs, worker recitals, file-by-file checklists, or "CLEAN" verdicts;
   put those in a linked artifact. No `## Summary` or `## Test plan`
   boilerplate. A commit body does not restate its subject.
5. **Size.** Prefer several narrow changes to one large one. When the forge
   supports dependent changes, chain them base-on-parent so the root targets
   trunk; otherwise land them in order. Branch from trunk only for
   independent work, and rebase on trunk before building dependent changes.
6. **Review bots and automated reviewers.** They catch real bugs and also
   file non-issues, so assess each finding on its merits instead of treating
   every comment as a required change. Triage each thread as one of three:
   - `fix`: the finding names a plausible correctness, security, privacy,
     data loss, auth, migration, idempotency, or race issue. Fix it in the
     change that owns the code, then reply with the fixing commit and
     resolve the thread.
   - `dismiss`: the current code or context shows no change is needed.
     Reply with a concrete reason and resolve the thread; do not churn code
     to silence it.
   - `ask`: the finding is novel, high-severity, or ambiguous. Ask the user
     instead of guessing.

   When in doubt, ask; skipping a style nit is cheap, skipping a real data or
   security bug is not. When the project requires the bot to pass, resolve
   threads the project's way.
7. **Before merge.** When you want to check that you understand a change an
   agent wrote before you land it, load
   [merge-brief](../../../merge-brief/SKILL.md). Opening the change does not
   start a watch loop; post the link and keep building, and run a separate
   follow-up pass only when asked. Return to the parent playbook's **Reply**.

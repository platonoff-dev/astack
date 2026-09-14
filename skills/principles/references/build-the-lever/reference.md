# Build the Lever

When the work isn't trivial, build the tool that does it instead of doing it by hand.

**Why:** Two payoffs. Throughput: a codemod, generator, or script does the work the same way every time and reruns for free. Confidence: the tool is one artifact a reviewer can read and rerun to check the work. Hand-done changes can only be re-verified by redoing them. A deterministic script turns "trust me" into "run this".

Work within the authorized task and the project's `CLAUDE.md` / `AGENTS.md`. Follow the active harness's tool, delegation, and approval rules; this principle does not authorize installation, live service writes, or publication.

**Pattern:** Default to building the lever. Skip it only when the task is trivial, a couple of obvious edits you can see at a glance.

- First check for an existing tool that does or proves the job. Reuse it when suitable; extend it or build the smallest missing tool when needed.
- Do the first unit by hand to learn the recipe, then build the tool. Prove it by rerunning it on that unit and diffing against your hand-done version. Make the lever safe to rerun.
- Codemod or script for edits, generator for repetitive files, a dump-to-sqlite query for analysis, a rerunnable check for verification.
- A deterministic lever beats fan-out. If the tool can process every unit in one pass, run it yourself. Don't fan out delegates to hand-apply what a script can do.
- When subagents are available and delegation is permitted, and you fan work out to them, write the lever as a skill they all read: the recipe, the verification contract, and the do-not-touch fences in one artifact. Keep it outside the delegates' assigned write scope. Use enforced read-only access when available; an instruction alone does not prevent edits, so check that the contract is unchanged before accepting results.
- Applying this principle leaves a reviewable codemod, script, generator, or delegate skill. For an existing tool, record its path, the command, and the observed result in the permitted work artifact; no duplicate file or artificial diff is needed.
- Retain the lever in the project's permitted working area when the work outlives the session. Commit it only when committing is authorized and the file belongs in the repository.

**Balance:** The bar is triviality, not repetition. A one-off still earns a lever when the lever is what makes the work checkable. Per the [Laziness Protocol](../laziness-protocol/reference.md), build the smallest script that does or proves the job, never a framework.

Distinct from [Encode Lessons in Structure](../encode-lessons-in-structure/reference.md), which makes a recurring instruction a durable guardrail. This is throughput and reviewability on the work in front of you. For scripting the verification itself, see [Prove It Works](../prove-it-works/reference.md).

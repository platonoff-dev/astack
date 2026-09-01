# Evidence for routed task playbooks

Read on 2026-09-01. This ledger covers ten primary sources relevant to routing
one software task through investigation, change, and verification. It records
research, not an adoption decision. No source establishes the best workflow for
this repository or for its current models.

The design implications below are proposed inferences to trial locally. The
source descriptions separate controlled experiments, retrospective evaluations,
and first-party engineering advice. Paper revisions matter: the AGENTS.md and
agent-scaling papers changed substantially after their initial releases.

## 1. Repository instructions do not guarantee better task completion

[Gloaguen et al., Evaluating AGENTS.md, v2](https://arxiv.org/html/2602.11988v2),
2026-06-23 revision of the 2026-02-12 preprint. Read Sections 3–6 and Appendix B.
Controlled benchmark evidence, with limited transfer to other work.

The study tests SWE-bench Lite's 300 tasks and CTXbench's 138 Python tasks using
Claude Code with Sonnet 4.5, Codex with GPT-5.2 and GPT-5.1 mini, and Qwen Code
with Qwen3-30B-Coder. Generated context files produce small, statistically
insignificant resolution declines. Developer files produce a 2.4 percentage
point gain that is also insignificant against no file. Costs and exploration
increase; explicit instructions are generally followed.

The revised paper does **not** establish that all instructions hurt. It finds
no significant independent effect of file length and identifies non-standard
practices as a legitimate use of context files. It evaluates task resolution,
not security, maintainability, or permission compliance; each agent completion
is sampled once.

Inference: preserve non-obvious obligations from the brief and repository.
Do not duplicate discoverable repository documentation or assume additional
steps improve correctness. Test each proposed obligation against an observed
failure.

## 2. Faster execution is counterevidence, but not proof of correctness

[Lulla et al., On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents](https://arxiv.org/html/2601.20404v1),
2026-01-28. Read Sections 3–5. Paired operational experiment with incomplete
quality measurement.

Codex with GPT-5.2-Codex attempts 124 small PR-derived tasks from ten
repositories, with and without their original AGENTS.md. Median runtime falls
28.64%; median output tokens fall 16.58%. Selected PRs modify at most five
files and 100 lines and exclude documentation/configuration-only work.

The paper explicitly excludes a comprehensive correctness evaluation. Its
manual check of 50 tasks establishes non-trivial, apparently relevant changes,
not functional equivalence. Some task descriptions are generated from the
reference patch. It therefore does not contradict a study finding no general
correctness gain under a different task distribution.

Inference: record elapsed time and process overhead in a local trial, but count
them as improvements only after independent completion checks pass. Avoid
claiming either a universal context-file benefit or a universal penalty.

## 3. Valid reproduction tests can make implementation much easier

[TDFlow, EACL 2026 paper](https://aclanthology.org/2026.eacl-long.70.pdf),
March 2026 proceedings. Read Sections 3–5, 8 and Tables 1–2. Peer-reviewed
benchmark experiment in a deliberately test-driven setting.

TDFlow separates patch proposal, debugging, and revision, with optional test
generation. On SWE-bench Lite, all systems receive human reproduction tests
and use GPT-4.1; TDFlow scores 88.8% versus 61.0% for the best comparison.
On Verified, GPT-5 resolves 94.3% with human tests, versus 68.0% when Claude 4
Sonnet generates tests. Those values come from Table 2; the introduction
inconsistently says 69.8% for generated tests. A debugging-agent ablation scores
87.2% with human tests.

These results do not compare ordinary TDD against test-last development, and
human-test scores are not ordinary hidden-test benchmark scores. The authors
acknowledge that immutable incorrect tests trap the workflow in retries; it
lacks early stopping. Human reviewers find seven test-hacking cases in 800
human-test runs and count them as failures.

Inference: establish that a regression test exposes the intended failure.
Preserve a route to question faulty tests or requirements. The paper supports
focused debugging, not mandatory role agents for every task.

## 4. Procedural TDD prompting can worsen results in a constrained setting

[TDAD, v2](https://arxiv.org/html/2603.17973v2), 2026-03-19 revision of the
2026-03-18 preprint. Read Sections 4–6, especially Tables 4 and 7. Small
exploratory tool study; weak evidence for broad prescriptions.

On 100 SWE-bench Verified tasks with quantized Qwen3-Coder 30B and a 32K
context, adding TDD instructions raises the test-level regression rate from
6.08% to 9.94%. A source-to-test map plus instructions lowers it to 1.82%.
However, resolution falls from 31% to 29%, and the fraction of nonempty patches
with any regression rises from 30.2% to 33.3%. Empty patches are excluded from
regression evaluation, so denominators differ. This is narrower than a general
claim of fewer defective patches.

A second 25-task experiment uses quantized Qwen3.5-35B-A3B with OpenCode. The
paper reports no formal significance tests. Its iterative prompt shortening
result comes from a ten-task development set, not held-out confirmation.

Inference: specify which behavior and nearby tests must remain correct. Do not
infer that a long TDD script or a graph dependency tool belongs in this plugin,
or that this result generalizes to frontier models.

## 5. Passing existing tests can still mean a wrong patch

[UTBoost, ACL 2025](https://aclanthology.org/2025.acl-long.189/), July 2025;
[full text read](https://arxiv.org/html/2506.09289v1), 2025-06-10.
Read Sections 3–4. Peer-reviewed audit of published benchmark patches.

The authors augment SWE-bench tests with GPT-4o-generated cases, compare
candidate and reference patch behavior, and manually review disagreements.
Together with repairs to test-log parsing, they identify 345 erroneous patches
that the original evaluation accepted. Insufficient coverage affects 36 unique
tasks across the overlapping Lite and Verified sets.

The result establishes failures in both coverage and result collection. It
does not measure the defect rate of today's coding agents or prove that every
generated test is a valid specification. The reference patch and reviewer
judgment are part of the correctness oracle.

Inference: check that the intended test actually executed and asserted relevant
behavior. For a bug, include a case that distinguishes the faulty behavior from
the requested behavior, plus relevant regression checks. A green command or a
test file's mere presence is insufficient evidence.

## 6. Maintainer acceptance measures things benchmark tests miss

[METR, Many SWE-bench-Passing PRs Would Not Be Merged into Main](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/),
2026-03-10. Read methods, results, and limitations. First-party retrospective
study using blinded maintainer review.

Four maintainers review 296 AI patches across 95 issues in scikit-learn,
Sphinx, and pytest. Models range from Claude 3.5 Sonnet to Sonnet 4.5 and GPT-5,
using one evaluation agent setup. After normalization against 47 original human
patches, roughly half of test-passing agent patches would not be accepted.
Rejections include unresolved behavior, regressions, and code quality.

Reviewers lack CI and ignore missing-test requirements. Original human patches
receive only 68% acceptance on rereview, so normalization and subjectivity
matter. Agents get no opportunity to revise in response to review. The study
does not establish a capability ceiling or measure current models.

Inference: review the diff against the brief and repository conventions after
tests pass, and allow repair. Keep this distinct from a maintainability-only
review. The evidence does not show that an agent reviewing itself provides the
same assurance as maintainer review.

## 7. Delegation benefits depend on task structure and budget

[Kim et al., Towards a Science of Scaling Agent Systems, v3](https://arxiv.org/html/2512.08296v3),
2026-04-08 revision of the 2025-12-09 preprint. Read Sections 4–5 and
Appendix Tables 14–16. Controlled architectural comparison, with small coding
subsets.

The revision reports 260 configurations across six benchmarks and model
families GPT-5, Gemini 2.x, and Claude Sonnet 3.7–4.5. It compares one agent
with independent, centralized, decentralized, and hybrid arrangements under
matched computational budgets. Parallelizable financial tasks improve, while
sequential planning degrades under every multi-agent arrangement. Coding and
terminal experiments use only 20 tasks each, with wide confidence intervals.

The popular summary of 180 configurations and four noncoding benchmarks
describes v1, not this revision. The approximate 45% baseline threshold is an
empirical association, not a universal dispatch rule. Some tool-overhead
coefficients lose significance under cluster-robust inference. Prompts were
not optimized separately for every model and arrangement.

Inference: let one agent own a coherent change by default. Delegate only work
with independent inputs, bounded output, and a checkable result, when the
session authorizes delegation. Measure total coordination and integration
effort; do not infer that multiple agents inherently improve quality.

## 8. Long-running handoffs need observable state

[Anthropic, Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents),
2025-11-26. First-party engineering report, not a controlled comparative study.

Anthropic describes Opus 4.5 and Claude Agent SDK work on web apps across many
context windows. Observed failures include attempting too much at once,
leaving undocumented partial changes, and claiming completion prematurely.
Their response combines an initializer, a feature list, incremental coding,
git history, progress notes, and browser verification. Unit checks and HTTP
requests sometimes missed broken user-facing behavior. The report also notes
browser-tool visibility limitations.

No sample size, confidence intervals, or ablation establishes the contribution
of each mechanism. The case is broad application construction, not a small
intake-ready change. Its JSON feature list and separate initializer are design
choices, not demonstrated requirements for this plugin.

Inference: if work crosses a session boundary, preserve what changed, what was
verified, what remains, and the next executable step. Recheck actual git and
runtime state on pickup. Use the task's real interface when verifying an
outcome. Reuse the brief before introducing another mandatory progress file.

## 9. Official Codex guidance favors scoped, verifiable requests

[OpenAI, Best practices](https://learn.chatgpt.com/guides/best-practices),
undated living documentation, fetched 2026-09-01. Read the sections on prompts,
planning, AGENTS.md, testing, and review. Product guidance, not measured proof.

The guide asks for the goal, relevant context, constraints, and a completion
condition. It recommends planning for difficult tasks, tests when needed,
relevant checks, behavioral confirmation, and diff review. It recommends
practical, short repository guidance, adding rules after repeated mistakes.

Inference: intake already supplies much of this information. The selected
playbook should consume that brief rather than ask the same questions again.
Ordinary planning can stay within the playbook; the source does not require a
separate plan artifact, approval gate, or test-first ritual for every change.

## 10. Current OpenAI prompting advice also warns against duplicated process

[OpenAI, Model guidance, Favor leaner prompts](https://developers.openai.com/api/docs/guides/latest-model#favor-leaner-prompts),
undated GPT-5.6 guidance, fetched 2026-09-01. Vendor advice with a briefly
reported internal evaluation.

OpenAI reports that leaner instructions improved scores by roughly 10–15%
while reducing total tokens by 41–66% in a sample of internal coding-agent
runs. The page does not supply task count, statistical uncertainty, or enough
methods to reproduce those figures. It advises removing one instruction group
at a time and rerunning representative evaluations, preserving actual
requirements and explicit autonomy boundaries.

Inference: treat the ranges as directional, not expected gains here. State
each new obligation once. Retain safety and scope constraints even when they
have a runtime cost. Test whether routing and each focused playbook change
decisions beyond the host's existing instructions and the intake brief.

## What to trial

These are design hypotheses from the ledger, not validated plugin requirements.

| Proposed rule | Failure to look for | Evidence that would justify keeping it |
|---|---|---|
| Select the current job, not the ticket label | A proposed fix bypasses missing evidence | `investigation` gathers the evidence before a change route starts |
| Load one primary playbook | Several generic procedures compete | The run follows the selected proof sequence without unrelated ceremony |
| Apply modifiers as proof obligations | A secondary risk becomes another workflow or disappears | The final checks cover the modifier while one playbook still owns the sequence |
| Change route when entry facts fail | Repeated attempts chase an invalid assumption | The same task moves to `investigation`, `decision`, `split`, or `no-change` with a precise reason |
| Match checks to the requested behavior | A green suite misses the requested outcome | An independent check rejects an incomplete result and accepts the correct one |
| Preserve current state on pickup | A resumed run repeats work or misstates completion | A fresh session continues from observed state and known gaps |

Trial one investigation that should route to a change, one ready change, and one
task whose evidence forces a decision or no-change result. Include a mixed
modifier case. Fix the repository snapshot, brief, tools, and evaluation checks.
Inspect the artifacts and transcript for route choice, transition timing,
outcome correctness, unsupported completion claims, scope expansion, and extra
process. Do not equate more tool calls, longer reports, or stricter wording with
better work.

A single real-task trial can expose a failure and demonstrate feasibility. It
cannot estimate general improvement, establish reliable automatic selection,
prove transfer between Claude Code and Codex, or justify a mandatory multi-agent
pipeline. Improve only the route or playbook that exhibits a material failure.

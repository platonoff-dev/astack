# Skill behavioral evaluations

Each `skills/<name>.json` contains synthetic requests and observable expectations
for one shipped or repository-only astack skill. These cases test decisions,
artifacts, evidence handling, and scope; they do not require exact wording.
They are development assets outside the shipped skill directories.

The `principles` suite retains the sixty behavioral cases for the former twenty
standalone principle skills, using named references through the registry. Six
additional cases exercise selective reading, no-match selection, required named
guidance, and changing decision boundaries. Their presence does not establish
automatic discovery or a behavioral pass.

## Run a case

Validate the suites already authored:

```sh
python3 -B scripts/skill_evals.py validate
```

Require complete skill coverage at the end of an audit:

```sh
python3 -B scripts/skill_evals.py validate --require-all
```

Ordinary repository validation permits incremental additions; the complete
audit is not finished until the full-coverage check passes.

Print a request without its grading expectations:

```sh
python3 -B scripts/skill_evals.py request task-interview <case-id>
```

The helper does not call a model or grade its response.

1. Choose a case and freeze its expectations before execution. Give a fresh
   evaluator the case's `prompt`, the source skill path, and only the required
   raw fixtures. Keep expectations, forbidden-action grading criteria, review
   findings, and proposed fixes out of its context. Use uniform local-fixture
   execution limits; do not disclose desired task decisions as safety limits.
2. Use an isolated directory under `.local/` for generated artifacts. Use only
   synthetic data and supplied local fixtures. Live accounts, external writes,
   installation, commits, and deployment are not part of these cases.
3. Retain the actual response and artifacts, source revision or content hash,
   model, effort, supplied prompt, and execution limits under `.local/`.
4. Grade each expectation against the response/artifacts: pass, fail, or
   untested, with concrete evidence. Record prohibited actions separately.
   Missing tools or unavailable integrations limit the result; do not infer
   success from the absence of an action that was impossible to attempt.
5. For a demonstrated defect, make a narrow correction and rerun the failed
   case on the changed skill with another fresh evaluator. Keep before and
   after evidence. Use a no-skill baseline when judging whether a skill adds
   value or deserves retirement.

A fixture's existence or successful JSON validation is not a behavioral pass.
An explicit source-path invocation does not measure automatic skill discovery.
A Codex trial does not establish Claude Code behavior. A single successful case
is a smoke test, not a reliability estimate. Scenarios that require dialogue
need a user or a separately supplied follow-up; do not invent user agreement.

## Model selection for the initial audit

Reviews use `gpt-6-astra`: `high` for short principle/style skills and `xhigh`
for multi-step workflows, dependency handling, and evidence reconciliation.
Independent task execution uses `high`, raised to `xhigh` when the case itself
requires difficult reconciliation. The aim is careful review with bounded
scope; this is an initial allocation, not a measured comparison among models.

The current harness exposes Astra as its most capable model. Official
[model guidance](https://developers.openai.com/api/docs/guides/latest-model)
also describes Astra as more capable than earlier models. Reassess effort
using observed results rather than assuming maximum effort is always better.

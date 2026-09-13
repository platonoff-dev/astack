---
name: harden-tests
description: Check whether tests detect incorrect behavior through regression checks, assertion audits, invariant searches, and optional targeted mutation testing. Use when asked to assess or strengthen test quality.
---

# Harden tests

One job: **attack the tests.** The code is somebody else's problem. The
question you answer is "do these tests actually fail when the behaviour is
wrong?" — because 100% diff coverage with unasserted tests is precisely the AI
failure mode, and nothing else in the pipeline checks for it.

## Hard rules

- **You never touch source.** Not one line. If a finding can only be fixed in
  the implementation, that is a stop: report it, do not fix it.
- **You may edit tests** — that is your remit — but every test edit means you
  re-run attack 1 afterwards. No exceptions.
- **Attack 1 is mandatory and is the verdict.** Any new test that still passes
  with the fix reverted is a `NOT READY`, regardless of how green everything
  else is.
- **Write exactly one file: `.work/harden.md`.**

## Supporting capabilities

Use these capabilities when available in the current harness. Their absence
does not prevent the assertion audit or regression check below.

- **Property-based testing** — supports attack 3, and its
  section on tests that "assert nothing" through tautology or vacuity is the
  sharpest tool you have for attack 2. It ranks nine property patterns
  (roundtrip, inverse, oracle, idempotence, invariant, easy-to-verify,
  commutativity, associativity, identity) by strength: **assert the strongest
  property the code supports.**
- **Mutation testing** — supports attack 4, specifically the
  scoping: which targets, which timeouts, how to keep a run finite. Use it to
  decide whether attack 4 is even affordable for this ticket before running
  anything.

Attack 1 is yours alone. No skill does it and no skill excuses it.

## Attack 1 — revert-check (mandatory, ~free)

`git stash` the implementation commit's source changes, leaving the tests in
place. Run only the new tests. **Every one must fail.** Restore.

```
git stash push -- <impl source files>
<project test command selecting the new tests>
git stash pop
```

Report it as `N/N new tests fail with the fix reverted`. Name any test that
survived — that test does not test the fix.

## Attack 2 — assertion audit

Read every new test. Flag:

- no assertion at all;
- asserting on a mock the test itself configured (tautology);
- `assert_called()` / `assert_called_once()` with no argument check;
- over-mocking such that the real code path never executes;
- an assertion that would hold for the pre-fix behaviour too (attack 1 catches
  these mechanically — this catches the ones that hide behind a second test).

`ruff` `PT` and `T20` cover a slice of this. The rest is reading — with
`property-based-testing`'s tautology/vacuity criteria applied to the example
tests, not only to property tests.

Also audit the exception handling the new tests exercise: a handler that
`pass`es or returns an indistinguishable default is the most common reason a
test passes over broken code. You may not fix it in source — report it as a
stop.

## Attack 3 — invariant hunt

For each criterion ask: is there a *property* here, not just examples? For this
codebase's actual work the answer is usually yes — byte-size bounds,
split-then-join round-trips, loss-free queue refill, drain rates, ack == send.
When it is, add a `hypothesis` property test. Install `hypothesis` into the
local test venv only; never edit `Pipfile` / `requirements-test.txt`.

## Attack 4 — targeted mutation (optional, per ticket)

`mutmut` on the single changed module with a hard timeout. Only for logic-dense
security code. Choose the scope using available mutation-testing guidance — targets
and timeouts are the whole problem here; use it to decide whether attack 4 is
affordable for this ticket before running anything. This is a third gear, not
your identity: Do not attempt a whole-suite mutation run without assessing its cost. Check
whether `mutmut` is available; use the project test environment and report
missing tooling honestly.

## Output — `.work/harden.md`

```markdown
# PROJ-123 — hardening

## Attack 1 — revert-check
**6/6 new tests fail with the fix reverted.**
| Test | Fails on revert | Failure |
|---|---|---|
| `test_refill_survives_restart` | yes | AssertionError: lost 3 messages |

## Attack 2 — assertion audit
| Test | Finding | Action |
|---|---|---|
| `test_split_preserves_payload` | asserts only on the mock it configured | rewrote to assert on the joined bytes |

## Attack 3 — invariants
| Property | Test | Cases |
|---|---|---|
| split then join is the identity | `test_split_join_roundtrip` | 10k |

## Attack 4 — mutation
skipped / mutmut on `<module>`: N mutants, M survived — <which>

## Stops for the human
- <anything that needs a source change, or "none">
```

Report back: the revert-check line first, then counts for attacks 2–4, then the
stop list.

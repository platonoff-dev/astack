---
name: harden-tests
description: Audit and strengthen existing tests for regression sensitivity and contract coverage. Use when asked whether tests would catch a bug, to harden a change's tests, or to repair weak or brittle assertions. Not a default step for routine test writing or bug fixing.
---

# Harden tests

Establish which incorrect behaviors the tests detect, strengthen useful gaps,
and report the evidence. A passing suite or high coverage alone does not answer
that question. Tests should also tolerate changes that preserve their contract.

This is a focused review of existing tests. TDD handles writing a failing test
before implementing a fix; property-based testing handles generator and property
design in depth. Neither skill is required here.

## Establish the scope and contract

Read the repository's `AGENTS.md` / `CLAUDE.md`, the requested diff or test area,
nearby tests, and the project's test commands. Use its existing language, test
runner, fixtures, and dependency policy. Keep the scope at the named change or
behavior unless evidence requires a wider check.

For each behavior under review, identify the contract and its basis: requirements,
documented API or protocol, a reproduced bug, or an established compatibility
promise. Current implementation behavior alone is not proof of intent. Surface
an ambiguous expectation instead of encoding a guess as a test.

Distinguish tests that **claim to detect the regression** from tests of unchanged
behavior. Name the defect each regression test claims to catch. Other useful
contract tests may legitimately pass when this particular fix is removed.

For a hardening request, edit tests, fixtures, and test helpers within scope. For
an assessment-only request, report proposed changes. Keep production fixes
outside a test-hardening-only request; report source defects and continue
independent review. A broader user request may already authorize those fixes.
Temporary production edits in isolated experiments are permitted for the checks
below; they are not changes to deliver.

## Audit assertions and execution

Trace setup through the real subject to the observable result. Ask both: **what
contract violation would fail this test, and what harmless refactor would fail
it?** Use the answers to judge an assertion, rather than banning its syntax.

| Check | Decision |
|---|---|
| Test actually executes | Confirm discovery, selection, and completion. Check skipped or expected-failure cases, unawaited work, swallowed errors, and assertions hidden in callbacks that never run. Framework expectations, type checks, and explicit no-crash contracts can be valid without a conventional assertion statement. |
| Expected result has an independent basis | Prefer hand-checked examples, specification fixtures, an independent oracle, or a justified relation. Reusing the subject or its faulty helper to compute both sides creates a shared blind spot. Similar-looking arithmetic is not automatically tautological; judge independence and the faults it can expose. |
| Assertion distinguishes the defect | Presence, type, or truthiness checks may be too weak for a value or state contract. Assert the relevant result, error, state transition, or effect. Keep exact messages, snapshots, and constants only at the precision the contract requires; protocol bytes and promised defaults can justify exact values. |
| Doubles preserve the behavior being tested | Keep the subject real. Stub at a boundary whose behavior is understood. A mock returning what the test configured proves little by itself; inspecting a request emitted by real code can verify a contract. Check arguments, counts, or ordering when those are part of that contract, not for private call choreography. |
| Absence is meaningful | Empty results, no write, no notification, and rejection are legitimate outcomes. Ensure the triggering path ran and the observation covers the relevant completion point. Add a contrasting case when needed to distinguish correct absence from an unconditional no-op; it need not live in the same test. |
| Inputs exercise the claim | Check boundaries, error paths, and state transitions relevant to the change. Empty loops, impossible preconditions, heavily discarded generated inputs, or one shared fixture hiding all other branches can leave a green test with no useful evidence. |

Fix concrete weaknesses without rewriting good tests for style. Do not weaken an
expectation to accommodate a source bug. Control time, randomness, scheduling,
and shared state at existing seams where they obscure the result; avoid sleeps
and repeated retries that merely hide a flaky failure.

## Demonstrate regression sensitivity

For tests claiming to catch a known bug, seek a reproducible **pass with the fix,
meaningful failure with the defect, pass again with the fix**. Existing evidence
can suffice if it matches the current test and relevant implementation; otherwise
run a focused experiment when practical.

Read [Isolated regression checks](references/regression-check.md) before preparing
the experiment. Keep the current tests fixed while reversing only the relevant
production change in a disposable checkout or copy. `git stash` does not undo
committed implementation changes. Preserve the user's working tree and index.

Check the actual selected test names and failures, not just the process exit
code. A wrong result or a crash in the exercised behavior can be evidence;
collection errors, incompatible APIs, stale binaries, missing dependencies, and
unrelated failures cannot establish the claim. Run separately when one failure
prevents other regression tests from reaching their assertions.

A claimed regression test that still passes needs investigation: wrong setup,
weak observation, wrong defect, or a misstated claim. Strengthen it or correct
the claim based on the contract; do not manufacture failure in a useful test of
unchanged behavior. If reversing the fix is impractical, try a small plausible
defect at the same behavioral seam, label it as an injected defect, and state
that historical regression detection remains unverified.

After changing a regression test, repeat its relevant sensitivity check. After
other test edits, rerun those tests and affected neighbors; there is no reason
to repeat unrelated experiments.

## Fill valuable contract gaps

Choose examples, a table of cases, or properties according to the gap. Useful
properties include conservation of data, ordering plus preservation of elements,
round trips, idempotence, agreement with an independent model, and relationships
between related inputs or state transitions. State preconditions and the domain
over which the rule should hold.

Properties complement each other; there is no universal strength ranking. A
constant result can be idempotent, an empty result can be sorted, and paired
encoder/decoder bugs can pass a round trip. Add an independent example or another
constraint when it closes that blind spot. Check that generators reach relevant
boundaries and produce enough valid cases. Preserve useful counterexamples and
the seed or replay information supplied by the runner.

Use a property library already in the project when it helps. Without one, use
focused examples or bounded enumeration, or propose a dependency with a concrete
benefit. Do not install tools automatically or refactor production code merely
to introduce property testing.

## Optional bounded mutation

Use mutation when uncertainty about important logic remains after the cheaper
checks. Select a few plausible defects, such as an off-by-one condition, a
missing state update, or a wrong boundary argument. A manual injected defect may
be enough. Use an existing mutation tool only when its cost is justified; no
language, tool, full-suite run, or universal score is required.

Before running, set the production targets, selected tests, and a total time or
mutant budget with per-run timeouts. Establish a passing unmodified baseline and
use isolation as above. Change one defect at a time, or let a configured runner
isolate each mutant. Triage the result:

| Outcome | Interpretation and action |
|---|---|
| Meaningful failure | Evidence that the selected tests detect this defect; identify the failing observation. |
| Survived or not covered | Check reachability, inputs, and assertions. Add a test only for a relevant contract gap. Survival alone does not establish equivalence. |
| Equivalent or outside the contract | Explain why behavior cannot differ on the valid domain, or why the difference is outside scope. Leave uncertain equivalence unresolved. Do not pin internals just to kill it. |
| Invalid build, collection, or tool error | The experiment is inconclusive for behavioral sensitivity. Distinguish these from an expected runtime failure caused by the defect itself. |
| Timeout or flaky result | Diagnose within the budget. A reproducible mutant-induced hang differs from a slow environment or pre-existing flake. Report timeouts separately even if the tool counts them as detected. |

Mutation measures sensitivity to the tried defects. It does not validate the
requirements, establish complete correctness, or show tolerance of harmless
refactors. Stop at the agreed budget and report untested targets and survivors.

## Report the result

Lead with the important gaps and whether the claimed regression detection was
demonstrated. Include the tests changed, the contracts they protect, and any
production defects or unresolved expectations. For experiments, give the test
selection, source revision or patch, command, and observed failure or survival.
Count only executed checks; identify skips, errors, and unverified claims.

Establish the final unmodified-source test result after removing experimental
defects, and run appropriate neighboring checks. A new test that exposes an
unfixed source bug may remain red; report it plainly. Verify that no experimental
source edits remain in the deliverable. Use the user's requested report location,
or respond in the conversation; no fixed artifact path or readiness score is
required.

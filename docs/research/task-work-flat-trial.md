# Flat task-implement trial receipt

Run on 2026-09-01. This receipt records the local comparison summarized in
`task-work.md`. Temporary checkouts and control scripts were removed after
the results were inspected. No trial patch was applied to this repository.

## Fixed input

- Base revision: `5e692a65bc4836266cbe8f981813b030c4cc04d6`.
- Task: fix `prior_art.py diff` so a changed Git source revision reports
  `MOVED` and exits 1 even when selected paths have identical contents.
- Preserved behavior: unchanged Git revision exits 0; selected-path drift exits
  1; local-source digest comparison and unread-source reporting do not change.
- Constraints: offline local Git fixtures, preserve an unrelated untracked file,
  change no vendoring behavior, make no commit or push.
- Prompt: "Implement the task in `.work/brief.md` in your checkout. Keep the
  work local, do not commit or push, and report the change and verification
  results."

Both checkouts received the same task brief, source receipt, tools, base
revision, and prompt. The guided checkout also received the 383-word candidate
reproduced in the earlier flat-guide draft. Each checkout had its own owner. Neither was
told that another condition existed or given the grader.

## Checks fixed before the runs

The offline grader created fresh local Git and directory fixtures for each
checkout and checked:

1. A commit changing only files outside selected paths reports `MOVED` and
   exits 1.
2. An unchanged Git revision reports `ok` and exits 0.
3. A selected-path change reports the changed file and exits 1.
4. An unread source retains its notice and exits 0.
5. An unchanged local digest exits 0.
6. A changed local digest reports `MOVED` and exits 1.
7. The unrelated file's SHA-256 digest is unchanged.
8. `git diff --check` passes.
9. Every added `test*.py` regression file passes.

Before the runs, the grader applied cases 1–4 to the original implementation.
Case 1 returned 0 with `ok ... tracked paths unchanged`; the other three cases
behaved as required. After the ordinary run, its new regression file was run
once against the original implementation. It failed only the outside-path case
with `0 != 1`, then all four test methods passed after the fix.

## Results

| Condition | Hidden checks | Product change | Regression coverage | Other validation reported |
|---|---:|---|---|---|
| Ordinary execution | 9/9 | Move the increment before selected-path comparison; print an unchanged-path diagnostic | Four offline test methods covering all required branches | 12 task-intake regressions, AST parsing, whitespace check |
| 383-word guide | 9/9 | Remove the early success branch; print the same diagnostic | Three offline test methods covering the same branches | 12 task-intake regressions, brief structure, whitespace check |

Both runs added the regression command to the README, preserved the unrelated
file, and correctly reported that they had not committed or pushed. The guided
run explicitly reported that it skipped network checks because the fixture was
offline. The implementation differences are equivalent. The extra brief check
in the guided run did not exercise product behavior.

## Limits

This was one run per condition on one small Python bug with one available model
family. The parent knew condition identities. No timing or token data was
captured. The trial did not test automatic invocation, Claude Code,
cross-session pickup, changed human intent, tracker publication, or delivery.
It can rule out obvious candidate harm on this fixture and establishes a tie on
the fixed checks. It cannot measure general effectiveness.

# Isolated regression checks

Use this procedure to test a regression claim without disturbing the user's
checkout. The comparison holds the tests and their support files constant while
changing the relevant production behavior. A valid unchanged-behavior test may
pass in both states.

## Choose the two states

Identify the exact candidate to evaluate and the production change that fixed
the bug. Inspect the diff; do not assume `HEAD^` is the buggy state or that a
commit contains only implementation. Record the selected test names, the
expected failure, and the source revisions or patch.

Record working-tree and index changes and relevant untracked files before
starting. Separate tests and implementation commits are convenient but not
required. When tests and source share a commit or file, select only the fix's
production hunks. Undoing every changed file can remove the very tests or
fixtures being evaluated.

## Reconstruct the candidate in isolation

Use the repository's disposable-directory convention. Prefer an independent
clone or copy; a linked worktree shares Git metadata and should not be used for
experiments that alter shared refs or stashes. Verify the resolved experiment
path before any mutation, and keep its files independent of the original.

For a fully committed candidate with a separable fix, the following is a
command sketch. Replace the values with inspected revisions and fresh absolute
paths, and choose actual production paths. Keep the patch outside the clone.

```sh
origin_repo='/absolute/path/to/repository'
candidate='candidate-commit-sha'
before_fix='pre-fix-commit-sha'
after_fix='post-fix-commit-sha'
check_dir='/absolute/path/to/fresh-disposable-clone'
fix_patch='/absolute/path/to/production-fix.patch'

git -C "$origin_repo" diff --binary "$before_fix" "$after_fix" \
  -- path/to/production > "$fix_patch"
# Inspect the patch. It must be nonempty and contain only the intended fix.
git clone --no-hardlinks --no-checkout "$origin_repo" "$check_dir"
git -C "$check_dir" checkout --detach "$candidate"
```

A clone or archive omits uncommitted work. For a candidate that includes local
edits, explicitly reproduce the intended tracked changes (including deletions)
and copy relevant untracked tests, helpers, and fixtures. A reviewed
`git diff --binary HEAD` captures combined staged and unstaged tracked changes
relative to `HEAD`; it does not capture untracked files or an index-only
candidate. Use the actual requested state, and compare the resulting files with
it. Do not commit, stash, or reset the original to make isolation easier.

Use the project's existing build and test environment. Verify that imports,
editable installations, symlinks, and build paths resolve to the isolated code.
Rebuild as required between states; stale or shared mutable build output can
make a false pass. An isolated source directory does not isolate external
services or shared test data; use the project's test isolation for those too.

## Pass, introduce the defect, restore, pass

1. Run the selected tests from the isolated candidate. Confirm they were
   collected, completed, and passed. Record the test/support-file state so it
   can be compared across the experiment.
2. After reviewing the patch, reverse it only in the isolated clone:

   ```sh
   git -C "$check_dir" apply --reverse --check "$fix_patch"
   # Proceed only when the check succeeds.
   git -C "$check_dir" apply --reverse "$fix_patch"
   git -C "$check_dir" diff
   ```

   Verify that the intended defect is present and tests/support files are
   unchanged. Stop on a patch mismatch; do not force application or resolve
   conflicts by guessing. Overlapping later changes may need a smaller
   experiment.
3. Rebuild if needed and run the same selected tests. Inspect each claimed
   regression's failure. If fail-fast, shared setup, or discovery prevents a
   test from running, select it separately. A single nonzero exit is not
   evidence that every selected test detected the bug.
4. Restore only the experimental change by applying the reviewed patch forward
   in the isolated clone, checking first, or reconstruct the saved candidate.
   Rebuild and rerun the tests. Verify that the original checkout and index
   were unaffected, then retain the evidence and remove only the disposable
   artifacts you created when no longer needed.

If the historical version cannot run with the current harness or API, classify
the comparison as inconclusive. Keep the current scaffolding and inject a small
defect that violates the same contract instead. Record the exact edit and call
it an injected-defect check, not a historical revert. Missing symbols, broken
collection, and dependency failures do not substitute for observing the bug.

`git stash push -- source-paths` only saves local modifications and restores
those paths to `HEAD`; a fix already in `HEAD` remains. It also changes the
user's index and stash state. The isolated reverse patch above handles committed
fixes without relying on that assumption.

Git documents the underlying mechanics in [git-stash](https://git-scm.com/docs/git-stash),
[git-clone](https://git-scm.com/docs/git-clone), and
[git-apply](https://git-scm.com/docs/git-apply). The behavioral checks above are
still necessary even when the Git commands succeed.

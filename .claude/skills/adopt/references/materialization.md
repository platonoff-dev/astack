# Reproducible adoption in astack

Read the source checkout's `docs/vendoring.md` and current helper interface;
they own supported operations. The installed skill directory is not the
checkout root. Keep all preparation under `.local/adoptions/<name>/` and apply
changes to shipped paths only after the user approves the concrete proposal.

## Git skill directories

The existing helper imports a directory that already contains `SKILL.md`,
copies its applicable license, applies ordered patches, and records the exact
commit in `vendor.json`. It does not import references outside that directory.

Prepare a baseline of the reviewed skill subtree with its license copied as
the helper does. Edit a separate candidate tree. Generate an ordinary Git
unified diff relative to the skill root (`a/SKILL.md`, `b/SKILL.md`, and other
affected paths), suitable for `vendor/patches/<name>.patch`. Include required
supporting files and any licenses for approved copied dependencies. Preserve
upstream notices and invocation restrictions. Use an isolated scratch Git
repository or the helper's staging behavior; patch application must not discover
the enclosing astack worktree. Verify contents after applying the patch to a
fresh baseline, not just the command exit status.

Do not publish a patch when upstream is already compatible. Conversely, do not
hide adaptations in unregistered edits or depend on a later policy sync to fix
vendored metadata. The helper only auto-generates missing Codex metadata for
an explicit-only skill; existing upstream metadata needs a patch when incompatible.

For a new supported import, preview the exact registry entry and command with
the reviewed full commit in `--commit` and the desired tracking ref in `--ref`:

```sh
python3 -B scripts/vendor.py add --name example-skill \
  --repo https://github.com/example/skill-library.git \
  --path skills/example-skill --ref refs/heads/main \
  --commit <reviewed-full-commit> --license MIT --license-path LICENSE \
  --patch vendor/patches/example-skill.patch
```

These are invented values; use the verified source and license, and omit
`--patch` if none is needed. Prepare the complete proposal in scratch before
executing this mutation in the real checkout.

For an existing entry, inspect its pin, current patches, and local drift before
editing the candidate. Preview registry and patch changes, set the approved
commit explicitly, and use `sync <name>` to reconstruct it after approval.
`update <name>` follows a moving ref and may fetch content newer than the review.
Never run a mutation without names when only selected skills are approved.
If changing the expected baseline requires `--force`, first preserve and show
any local edits and include their disposition in the approval; it discards them.
Do not drop an existing patch just because it conflicts with new upstream.

For dependencies copied from outside the selected subtree, keep their upstream
paths and source identities in a public-safe note with the patch. A scratch
report alone is not a durable update record. Compare those dependencies at the
reviewed and proposed revisions on future updates, even when `vendor.py check`
reports `CURRENT`: that helper only compares the selected subtree and license.

## Standalone agents and other source formats

A file containing agent instructions, an editor rule, a web page, or a directory
without `SKILL.md` is still a valid subject for review. The current helper
cannot directly import those formats: it checks for `SKILL.md` **before**
applying patches. A patch that merely adds that file cannot solve the problem.

First look for the canonical source repository and a supported component that
actually represents the user's selection. Do not choose an unrelated skill or
import an entire plugin just to make the helper accept a directory.

If packaging support is needed, prepare the smallest source-specific extension
to the vendoring path in scratch and include its complete diff and validation
plan in the adoption proposal. Preserve original bytes, source identity,
license/notice evidence, and a deterministic transformation into the approved
entrypoint. For non-Git sources, the proposal needs a durable source snapshot,
URL/provenance and digest, plus a reproducible materialization path; a temporary
local Git repository or URL alone is not durable provenance. Do not invent a
Git commit, register an ephemeral path, or claim the existing helper already
supports snapshots or native agents.

Explain whether the proposed output is a skill that uses a role prompt, a
standalone callable skill, or new native agent packaging. Preserve the role's
context and invocation semantics where possible; flag differences for approval.
Implement only the packaging support approved with this adoption, with focused
tests for reconstruction and failure behavior. Avoid building a general import
framework without a concrete source that requires it.

When rights, missing source material, or essential behavior prevent a concrete
candidate, deliver the report and the exact missing decision/evidence. Do not
ask for blanket approval to proceed with unresolved choices.

## Verification and finish

After approved materialization, run policy sync, `scripts/validate.sh`, and
`git diff --check`; bump both plugin versions and update skill listings as
required by the checkout. Reconstruct the approved pin plus patches in fresh
scratch and compare it with both the approved candidate and adopted files.
`vendor.py verify` only validates registry structure and patch paths; it does
not prove reconstruction, upstream currency, or runtime compatibility.

Read back the final diff including untracked new files. Separate structural
validation, reconstruction, and behavioral evidence per harness in the result.
Report unresolved checks honestly. Applying an import does not install the
plugin, publish it, or run its instructions.

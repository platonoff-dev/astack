# Vendoring skills

Run the helper from an astack source checkout. It uses Git and Python 3.10+
with the standard library. Every registered skill may come from a different
repository. Files are copied into `skills/<name>` so plugin installation needs
no submodule initialization or upstream access.

## Import

Select a repository, the directory containing `SKILL.md`, and the applicable
license. Example values below are invented:

```sh
python3 -B scripts/vendor.py add \
  --name example-skill \
  --repo https://github.com/example/skill-library.git \
  --path toolkit/skills/example-skill \
  --ref main \
  --license MIT \
  --license-path toolkit/LICENSE
```

`--repo` accepts Git clone URLs or a local repository path. A public registry
must contain shareable URLs, never credentials or private repository details.
`--path` is a repository-relative skill directory (`.` for a skill at the
repository root); the final frontmatter name
must match `--name`. Use a compatibility patch when renaming an upstream skill.
Existing directories and duplicate names are refused.

`--ref` is the branch, tag, full ref, or commit to follow. It defaults to the
remote's `HEAD`, so it also works with repositories whose default branch is
not `main`. Prefer full refs such as `refs/heads/main` or `refs/tags/v1.0.0`
when a branch and tag share a name. Tags resolve to their underlying commit.
An immutable ref has no later updates unless upstream moves it.

Use `--commit <revision>` to import a reviewed older commit while continuing
to track `--ref` for later updates. The registry always stores the resolved,
full commit ID. Credentials use your existing Git authentication; the helper
does not prompt or configure accounts.

`--license` records the applicable license identifier. `--license-path`
defaults to the upstream root's `LICENSE`; specify the applicable file for a
monorepo. It is required to exist and is copied into the skill. If a different
`LICENSE` already exists there, the extra text becomes `LICENSE.upstream`.
Review applicable terms and preserve any additional notices. The helper records
your selection; it does not determine licensing suitability.

## Check and update

```sh
python3 -B scripts/vendor.py check                 # all registered skills
python3 -B scripts/vendor.py check example-skill   # one or more names
python3 -B scripts/vendor.py update example-skill
python3 -B scripts/vendor.py update                # all registered skills
python3 -B scripts/vendor.py sync example-skill    # reproduce the recorded pin
```

`check` fetches the pinned commit and current tracked ref. It compares the local
copy with the pin plus patches, and compares upstream skill files and license
text at the two revisions. File contents and executable bits count as changes;
unrelated repository commits do not. It does not modify skills or the registry.
It may report both a local edit and an upstream update for the same skill.

Output states are `CURRENT`, `UPDATE`, `EDITED`, and `ERROR`. A patch conflict or
unavailable repository is an error, never evidence that a skill is current.
Checks continue through the remaining skills after an error.

Exit codes are `0` for current/success, `1` for local drift or available updates
from `check`, and `2` for errors. `verify` validates the registry and patch paths
offline; it does not claim that upstream is current or the local copy matches.

`update` fetches the tracked refs and repins them, even if a ref moved without
changing that skill. `sync` keeps the pins. Both refuse to overwrite local
changes by default and can recreate missing skill directories. `--force`
explicitly discards local changes; it does not bypass failed patches.

All selected skills are fetched and patched before any destination is replaced.
A preparation failure leaves the entire batch unchanged. Ordinary write errors
roll back replaced directories; abrupt process or machine failure is not a
crash-safe transaction. Run one vendor mutation at a time and review your Git
diff before committing.

## Compatibility patches

Keep deliberate adaptations as ordinary Git unified diffs under
`vendor/patches/<name>.patch`. Paths in the diff are relative to the skill root,
for example `a/SKILL.md` and `b/SKILL.md`. Make the diff against the pinned
upstream content, after its license has been copied. Never put private service
configuration into a patch in this public repository.

Register patches on import, in application order:

```sh
python3 -B scripts/vendor.py add \
  --name example-skill \
  --repo https://github.com/example/skill-library.git \
  --path skills/example-skill --ref main --license MIT \
  --patch vendor/patches/example-skill.patch
```

For an existing entry, add or adjust its `patches` list in `vendor.json`, then
run `sync <name>`. If the new patch intentionally changes the expected local
copy, save any wanted local edits first and use `sync <name> --force` to apply
it. Patch failures leave the skill and pin untouched. Resolve a conflict by
reviewing upstream changes and updating the patch; do not drop adaptations
merely to make an update pass.

The only automatic harness adaptation is generating `agents/openai.yaml` when
an explicit-only skill has no such file. Existing upstream metadata is
preserved. An explicit-only skill's existing YAML must contain the block-style
`policy.allow_implicit_invocation: false`; otherwise add a compatibility patch.
`sync_codex_policy.py` checks registered skills without rewriting their metadata.
Symlinks, special files, and submodules in imported paths are unsupported and
fail before publication. Referenced files outside the selected skill are not
imported automatically; review dependencies before using it.

## Finish an import or update

Inspect the Git diff, including changed instructions, scripts, dependencies,
licenses, and the registry pin. The helper copies upstream code but does not
execute it, create commits, push, or install the plugin.

```sh
python3 -B scripts/sync_codex_policy.py
scripts/validate.sh
git diff --check
```

Bump the version in both plugin manifests before committing. Validation includes
offline vendor tests and registry checks, so ordinary validation needs no
upstream network access. It also applies astack's skill conventions; use explicit
patches to resolve import incompatibilities. Reinstall from the updated source,
then restart Claude Code or start a new Codex task to refresh installed copies.

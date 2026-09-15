# Provenance

These playbooks are borrowed, not vendored. They are astack-owned rewrites of
files from Cursor's pstack plugin, tracked here by hand rather than through
`vendor.json` and `scripts/vendor.py`, because every file was rewritten for
Claude Code and Codex rather than patched.

## Upstream

- Repository: <https://github.com/cursor/plugins>
- Plugin: `pstack` (Lauren Tan, poteto)
- License: MIT, `pstack/LICENSE`, copied verbatim to [LICENSE](LICENSE)
- Reviewed commit: `f5bdd6826fd0a0d9cbc4347134c3a74a200b9d9d` (2026-09-10)
- Reviewed on: 2026-09-15

## File mapping

Paths are relative to the upstream repository root.

| Local file | Upstream source | Relationship |
|---|---|---|
| `../../SKILL.md` | `pstack/skills/poteto-mode/SKILL.md` | Router structure and the match/run/route pattern; rewritten, most content replaced |
| `investigation.md` | `pstack/skills/poteto-mode/playbooks/investigation.md` | Rewritten |
| `bug-fix.md` | `pstack/skills/poteto-mode/playbooks/bug-fix.md` | Rewritten |
| `feature.md` | `pstack/skills/poteto-mode/playbooks/feature.md` | Rewritten |
| `refactoring.md` | `pstack/skills/poteto-mode/playbooks/refactoring.md` | Rewritten |
| `perf-issue.md` | `pstack/skills/poteto-mode/playbooks/perf-issue.md` | Rewritten |
| `delivering-a-change.md` | `pstack/skills/poteto-mode/playbooks/opening-a-pr.md` | Rewritten and renamed |
| `session-pickup.md` | `pstack/skills/poteto-mode/playbooks/session-pickup.md` | Rewritten |
| `pause-safely.md` | `pstack/skills/poteto-mode/playbooks/pause-safely.md` | Rewritten |

Other poteto-mode playbooks (babysit, shipping, autopilot, orchestrate,
multi-phase plan, worktree cleanup, eval, authoring a skill, visual parity,
prototype, hillclimb, forensics) and its scripts were reviewed and deliberately
not borrowed.

## What the rewrite changed

Removed every Cursor and GitHub coupling: `Task` fields, `subagent_type`,
model slugs, `/loop`, control-skill reproduction, transcript directories, `gh`
commands, stack and draft semantics, and Cursor-only skills. Delegation now
follows astack's shared native-delegation contract with no model overrides.
Principle mentions link into astack's `principles` registry; three upstream
principles that astack does not carry were dropped or reworded. Project
instructions (`CLAUDE.md` / `AGENTS.md`) take precedence over every playbook
line, which upstream does not state.

## Checking drift

From a checkout of the upstream repository:

```sh
git -C <plugins-checkout> log --oneline f5bdd68..HEAD -- \
  pstack/skills/poteto-mode/SKILL.md \
  pstack/skills/poteto-mode/playbooks/investigation.md \
  pstack/skills/poteto-mode/playbooks/bug-fix.md \
  pstack/skills/poteto-mode/playbooks/feature.md \
  pstack/skills/poteto-mode/playbooks/refactoring.md \
  pstack/skills/poteto-mode/playbooks/perf-issue.md \
  pstack/skills/poteto-mode/playbooks/opening-a-pr.md \
  pstack/skills/poteto-mode/playbooks/session-pickup.md \
  pstack/skills/poteto-mode/playbooks/pause-safely.md \
  pstack/LICENSE
```

Read each upstream change and decide whether the local rewrite should absorb
it. Update the reviewed commit and date above when it does. `vendor.py check`
does not cover these files.

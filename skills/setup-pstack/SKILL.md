---
name: setup-pstack
description: Configure which model each pstack role runs on, for Claude Code or Codex. Detects the current harness and its usable models, then writes the per-role model rule where that harness loads it every session. Use for /setup-pstack, "configure pstack models", or changing a role's model. Never writes Cursor rules or installs pstack.
---

# Set up pstack models

Write the pstack model rule for the harness this session runs in: a managed
block at `~/.claude/rules/pstack-models.md` for Claude Code, or inside the
Codex home `AGENTS.md` for Codex. Each harness loads that file into every new
session, so pstack-derived skills read their per-role models from context. The
role labels follow pstack's `rigor`; the mechanism is this plugin's own.

Everything below uses `scripts/pstack_models.py` from this skill's directory.

## Steps

1. **Detect.** Run `pstack_models.py detect`. It names the harness from the
   environment, the target file, and the models the rule may use: the Agent
   tool's `model` aliases on Claude Code, the slugs and efforts in Codex's own
   models cache on Codex. If detection cannot tell the harness, pass
   `--harness`. Cross-check the Claude alias list against the Agent tool
   schema in this session; on Codex without a cache, ask the user which slugs
   they can select with `/model`. Never write a model you have not confirmed.
2. **Load current state.** Run `pstack_models.py show`. Start from the printed
   mapping, or from `inherit-parent` for every role when it reports `absent`.
   That baseline is safe, not a recommendation: it spawns each role on the
   parent's model. If `~/.cursor/rules/pstack-models.mdc` exists, offer its
   values as a starting point only where they are valid for this harness.
3. **Map and confirm.** Show every role with its proposed value, marking any
   value not in the detected set. For a panel, the list length is the number
   of subagents that will run, so say what each panel costs. Ask the user to
   accept or change named roles, preferring a structured question over free
   text. Read [the rule format](references/rule-format.md) when a value shape
   is in doubt.
4. **Write.** Run `pstack_models.py write --set '<role>=<values>'` once with
   every role, exactly as confirmed. The script validates, writes only its own
   block, re-checks the result, and prints each panel's fan-out. Show the user
   the printed report. On an error, fix the offending value and rerun; do not
   hand-edit the target file.
5. **Report.** Say which harness was configured, the file path, and that the
   rule applies to new sessions of that harness. Re-running this skill updates
   it. Configuring the other harness is a separate run inside that harness.

## Hard rules

- The script proves shape and, on Codex, membership in the models cache. It
  cannot prove account entitlement; that comes from the running harness.
- Write only the target the script names. Do not touch `~/.cursor/`, the other
  harness's files, project `AGENTS.md` or `CLAUDE.md`, or harness settings.
- Do not install or vendor other pstack skills as part of setup.

# 003: Should we vendor Cursor's strict code quality review?

- **Date:** 2026-08-31
- **Verdict:** vendor
- **Touches:** `vendor.json`, `skills/thermo-nuclear-code-quality-review/`,
  both plugin manifests, README, AGENTS.md

## Failure it prevents

Anatolii explicitly requested this skill. It supplies a reusable maintainability
rubric for branch reviews. No local review failure was established in this task;
the import is user-directed, not evidence that the rubric improves reviews.

## Sources read

- `cursor/plugins` @ fd878692de15,
  `cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md` and
  `cursor-team-kit/LICENSE`. `vendor.json` records the full commit.
- The bundled Codex `plugin-creator/scripts/validate_plugin.py`, read 2026-08-31,
  plus Codex CLI 0.146.0's generated protocol and local `plugin/read` response.
- [OpenAI skill metadata](https://learn.chatgpt.com/docs/build-skills#optional-metadata),
  read 2026-08-31. Codex documents invocation policy in `agents/openai.yaml`.
- Other Team Kit skills and its companion review subagent were not evaluated.

## Mechanism and fit

One 1,922-word skill, with no scripts, references, required service, or subagent
dependency. It prioritizes structural simplification, branching and boundary
problems, then file growth and legibility. A change taking a file past 1,000
lines requires justification. Findings should be few, actionable, and material.

The skill declares `disable-model-invocation: true`. This limits automatic use
in hosts supporting that flag. Its length and lack of an executable quality
check do not meet this repo's usual filter. The explicit vendoring request takes
precedence; preserve the upstream file rather than inventing a local rewrite.

Codex's bundled plugin validator fails on that flag, requiring it to be false.
The local Codex `plugin/read` API still lists the unchanged skill as enabled.
That proves discovery, not enforcement of explicit-only invocation. Keep this
validation failure documented. No validator changes or vendored-file edits.

## Verdict and trial

Vendor only the requested skill through `scripts/vendor.py add`, including
Cursor's MIT licence. Preserve its name and pin. Bump both manifests to 0.4.0.
Do not enrol all of Team Kit as a reading source; `vendor.json` tracks this
import, so no unrelated `prior_art.py seen` marker changes.

Applied the rubric locally to this packaging diff against HEAD. It adds no
executable logic, wrappers, or new vendoring paths. The existing add/check flow
handles the import. No structural findings; this is a limited packaging trial,
not evidence about review quality on a substantial code change or Claude's
runtime behavior. Both Claude manifest checks, both vendor pin checks, the
task-intake format check, and all 12 brief-checker regressions pass.

## What would reverse this

Revisit if the skill starts unsolicited reviews, produces speculative redesigns
without useful findings, or Codex stops loading the unchanged copy. Resolve the
validator mismatch through a separate compatibility decision if a fully passing
Codex ingestion check becomes necessary.

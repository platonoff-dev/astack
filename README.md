# astack

Anatolii's personal skills for Claude Code and Codex. One repository, one
plugin, built one useful component at a time.

## Skills

| Skill | Purpose |
|---|---|
| [task-interview](skills/task-interview/SKILL.md) | Clarify selected work through an adaptive interview, ending in a local brief. |
| [validate-claims](skills/validate-claims/SKILL.md) | Check factual claims in tickets, documents, proposals, or messages against evidence and assess their implications. |
| [setup-astack](skills/setup-astack/SKILL.md) | Create and refine private service access guides and tracker mappings, including connector corrections. |
| [pick-next](skills/pick-next/SKILL.md) | Recommend the next item from your queue or an epic, accounting for capacity and priorities. |
| [merge-brief](skills/merge-brief/SKILL.md) | Explain a proposed change and check your understanding before you decide whether to merge. |
| [blast-radius](skills/blast-radius/SKILL.md) | Trace what a change could break beyond its diff and verify the key safety assumptions with real code. |
| [weekly-report](skills/weekly-report/SKILL.md) | Draft your weekly status section from source evidence, with approval before publication. |
| [reflect](skills/reflect/SKILL.md) | Review the active conversation through three independent lenses and propose durable skill edits for approval. |
| [arena](skills/arena/SKILL.md) | Compare independent candidates with a fresh judge and synthesize a verified artifact. |
| [swarm](skills/swarm/SKILL.md) | Cover bounded work or run a declared race, verify outputs, and report remaining gaps. |
| [interrogate](skills/interrogate/SKILL.md) | Review code with independent reviewers and evidence-based lead judgment, without applying findings. |
| [why](skills/why/SKILL.md) | Investigate code rationale through available history and sources, separating evidence from inference. |
| [how](skills/how/SKILL.md) | Explain runtime flow, subsystem boundaries, and code placement from implementation evidence. |
| [teach](skills/teach/SKILL.md) | Teach code or a change conversationally using how and why investigations, gradual visuals, and plain language. |
| [bro](skills/bro/SKILL.md) | Restate the last assistant message simply and concisely, without jargon. |
| [tdd](skills/tdd/SKILL.md) | Fix a bug through a focused failing-then-passing regression test, or explain and use a practical verification alternative. |
| [harden-tests](skills/harden-tests/SKILL.md) | Check test quality through regression checks, assertion audits, invariants, and optional targeted mutation. |
| [technical-writing](skills/technical-writing/SKILL.md) | Write and review technical prose with document modes, plain sentences, and unambiguous instructions. |
| [unslop](skills/unslop/SKILL.md) | Remove AI writing patterns while preserving meaning and intended tone. |
| [principles](skills/principles/SKILL.md) | Select and read relevant engineering guidance for concrete design, implementation, debugging, refactoring, and verification decisions. |
| [playbook](skills/playbook/SKILL.md) | Route a task to one rigorous playbook behind the project's own mandatory steps, and run the astack skills each step names. |

No bundled agent definitions or automations. `playbook` is an explicit-only
router; every other skill owns its own workflow, and each can use the harness's
available delegation tools.

## Playbook router

Invoke `$playbook` in Codex or `/astack:playbook` in Claude Code at the start of
a task that needs a rigorous, repeatable workflow. It first reads the active
project's `CLAUDE.md` / `AGENTS.md` and puts that project's mandatory steps
(ticket first, reproduce on a named test server, tests first, merge request
conventions, review bots) at the top of the step list. It then matches the task
to one of eight playbooks (investigation, bug fix, perf issue, feature,
refactoring, delivering a change, session pickup, pause safely), copies the
playbook's steps into the harness's planning tool behind the project's steps,
and loads the astack skills each step names (`how`, `why`, `tdd`, `arena`,
`interrogate`, `unslop`, `technical-writing`, and the rest). A project rule
overrides any conflicting playbook line; the playbook adds rigor and never
defines the project's delivery flow. When no playbook fits, it says so and
proceeds plainly rather than inventing one.

The playbooks are borrowed from the task-routing skill in Lauren Tan's (poteto)
pstack plugin (MIT) and rewritten for Claude Code and Codex. They are tracked by hand
through
[PROVENANCE.md](skills/playbook/references/playbooks/PROVENANCE.md) rather than
`vendor.json`; see [vendoring details](docs/vendoring.md).

## Principles

The automatically discoverable [principles](skills/principles/SKILL.md) skill
provides a registry of twenty engineering principles with concrete read-when
criteria. It reads the smallest relevant set of full references; choosing none
is valid. Related links do not eagerly load the rest of the collection. It
reconsiders the selection when the decision changes, and preserves principles
that another workflow explicitly requires.

Invoke `$principles` in Codex or `/astack:principles` in Claude Code when you
want to request it directly, naming a principle when useful. This replaces the
former individual principle commands. The full texts remain ordinary Markdown
references with their licenses. Automatic selection is enabled in source; it is
not a hook or a guarantee of selection on every task. Source validation and
source-path trials do not establish discovery in installed harness caches.

## Native agent workflows

Invoke `$arena`, `$swarm`, or `$interrogate` in Codex, or
`/astack:arena`, `/astack:swarm`, or `/astack:interrogate` in Claude Code.
These three explicit-only skills use the active harness's native agents and
[shared execution and result contract](references/agent-workflows.md). A run stays
within one harness and uses its available capacity and authorized runners.
Arena combines alternatives, Swarm verifies coverage or a declared race, and
Interrogate reviews code without applying changes. Missing workers, unverified
outputs, and incomplete coverage remain explicit in the result. Fresh contexts
and separate workspaces depend on the native interface; instruction-only
restrictions are not enforced isolation. No runner service, model registry,
CLI bridge, or additional agent definitions are installed.

## Install

### Claude Code

```sh
claude plugin marketplace add platonoff-dev/astack
claude plugin install astack@astack
```

Restart Claude Code after installation.

### Codex

```sh
codex plugin marketplace add platonoff-dev/astack
codex plugin add astack@astack
```

Start a new task after installation.

## Claim validation

Use `$validate-claims PROJ-123` in Codex or `/astack:validate-claims PROJ-123`
in Claude Code to validate a ticket. The same skill accepts documents, proposals,
messages, URLs, or pasted assertions, such as `$validate-claims Check the factual
claims in this proposal.` It can be selected automatically for matching validation
requests; it is not a mandatory hook on every task.

Validation separates factual assertions from requirements, predictions, and
recommendations. It checks relevant claims against source evidence and returns
supported, contradicted, or unresolved verdicts with evidence and limits. When a
conclusion or action is proposed, it assesses whether the verified premises support
it. For tickets, this includes the alleged cause and prescribed fix, then a next
action such as implement, investigate, clarify, split, or no change. Validation
does not edit the source material or execute recommendations on its own.

Use `task-interview` when the remaining work is deciding what the task should mean.
`validate-claims` first establishes which of its factual premises hold.

## External-system setup

Run `/astack:setup-astack` in Claude Code or `$setup-astack` in Codex. Setup
inspects available tools and project context, tries scoped read-only operations,
and asks about missing conventions. It writes a private index plus operating
guides for the systems your astack workflows need. Providers are unrestricted;
one system may serve several roles, such as tracker, review forge, or report
destination.

Guides describe reusable service access, operations, and gotchas. A document
service configured while preparing a report can also support later document
searches or authorized edits; reporting rules stay with the reporting workflow.

Run setup again to add a service or correct an existing guide. For example:
`$setup-astack The Jira connector misses later comments. Update its guide to
fetch all pages.` Use `/astack:setup-astack` with the same request in Claude Code.
A targeted correction updates the relevant instructions in place, preserving
other systems and avoiding a fresh setup interview.

The default layout is:

```text
~/.config/astack/
  adapter.toml
  systems/
    issues.md
    reviews.md
    documents.md
  tracker-adapter.toml   # optional; existing mappings can also be linked elsewhere
```

Only needed files are created. Astack's skills explicitly load relevant guides;
ordinary harness requests are unaffected. Setup does not install connectors,
configure credentials, or change harness instructions. A successful local
validation does not prove live access; setup reports observed checks and gaps.

The index resolves from `$ASTACK_ADAPTER`, then project
`.agents/astack/adapter.toml` or `.claude/astack/adapter.toml` up to the repository
root, then `~/.config/astack/adapter.toml`. Outside a repository only the current
directory and user default are checked. An invalid selected index or missing
explicit path is an error, with no fallback to a different workspace.

Organisation-specific values and guides stay outside this public plugin. Use a
project bundle only in a verified private repository. See the
[index and guide format](skills/setup-astack/references/adapter-format.md).

### Existing tracker adapters

`setup-astack` also configures and validates field/status mappings. A new index
can link an existing mapping file without moving or rewriting it. Resolution is:

1. `$ASTACK_TRACKER_ADAPTER`, when set.
2. `tracker_adapter` in the selected astack index.
3. If no astack index exists, `.agents/tracker-adapter.toml` or
   `.claude/tracker-adapter.toml` in the
   current project, searched up to its repository root.
4. If no astack index exists, `~/.config/astack/tracker-adapter.toml`.

An index without a tracker link is a partial setup; it does not borrow a legacy
tracker implicitly. An explicit tracker override remains available for a run
against another tracker; verify that any system guides match that workspace.

Only put a project adapter in a private repository. Existing adapters at other
user-level paths can be selected explicitly with `$ASTACK_TRACKER_ADAPTER`.
See the [adapter format](skills/setup-astack/references/tracker-format.md).

`task-interview` is explicitly invoked: `$task-interview` in Codex or
`/astack:task-interview` in Claude Code. It ends with a brief and a next action;
it does not launch delivery.

## Vendoring skills

Use the repository-only [adopt](.claude/skills/adopt/SKILL.md) skill from this
source checkout: `$adopt <source URL or path>` in Codex or
`/adopt <source URL or path>` in Claude Code. It inspects the selected instructions
and their dependencies against the target harnesses, prepares a compatibility
report and complete proposed diffs, and waits for approval or corrections.
After approval it imports the reviewed source with any required compatibility
patches and validates the result. Source adoption and plugin installation are
separate steps.

Standalone agent instructions and non-Git sources receive the same review.
If they need new packaging support, `adopt` includes that concrete change in
the proposal; the vendor helper supports Git skill directories and their reviewed conversion
to ordinary reference directories.

Import individual skills from different Git repositories, keep exact commit
pins, check for upstream changes, and update selected skills or all of them:

```sh
python3 -B scripts/vendor.py add --name example-skill \
  --repo https://github.com/example/skill-library.git \
  --path skills/example-skill --ref main --license MIT
python3 -B scripts/vendor.py check
python3 -B scripts/vendor.py update example-skill
```

The URL above is an invented example; replace it with the repository and skill
you choose. `check` reports local edits and changes to the skill or its license,
ignoring unrelated upstream commits. `update` without names updates all
registered skills. `sync` reproduces the pinned versions. Updates preserve
repeatable compatibility patches and refuse to discard local edits by default.

`why` and `how` are vendored from Cursor's pstack with their MIT license, exact
commit pins, and compatibility patches. Both are self-contained and explicitly
invoked: `$why` / `$how` in Codex or `/astack:why` / `/astack:how` in Claude Code.
They pass no model or reasoning-effort overrides, use available host tools, and
can run in the parent when delegation is unavailable. `why` adapts to the sources
you can access; no particular forge, connector, or warehouse schema is required.
`unslop` is also vendored from pstack under MIT. Invoke `$unslop` in Codex or
`/astack:unslop` in Claude Code with the writing to edit. It preserves upstream
rule numbers and editing rules, including strict punctuation preferences. Its
compatibility patch removes the explicit-only frontmatter flag at the user's
request. The description retains “Must always apply”; both harnesses may select
the skill implicitly. This is not a hook that guarantees execution on every turn.

`bro` is also vendored from pstack under MIT, with its instruction text unchanged
and no compatibility patch. Invoke it explicitly with `$bro` in Codex or
`/astack:bro` in Claude Code to simplify the previous assistant reply.

`tdd` is vendored from pstack under MIT. Its compatibility patches supply
concise Codex menu metadata and conditional principle selection for fix decisions. Invoke `$tdd` in
Codex or `/astack:tdd` in Claude Code for a bug fix. It favors a cheap, focused
regression test and requires an explanation and a useful verification alternative
when a failing test is impractical. Its explicit-only policy is preserved in both
harnesses.

The twenty principle references are vendored from pstack under MIT. Their
original source paths, exact pins, licenses, and ordered compatibility patches
remain in the `references` collection in `vendor.json`. Packaging patches remove
standalone skill metadata and update principle links; the full instruction bodies
and earlier adaptations are preserved. Each reference has its own directory and
LICENSE, so vendor synchronization cannot replace the owned registry or sibling
references. These references have no independent invocation policy; the parent
`principles` skill allows automatic selection. Workflow invocation policies,
including Arena and Reflect's explicit-only policies, remain unchanged.

See [vendoring details](docs/vendoring.md) for licenses, patches, exit codes,
and the validation and reinstall steps.

## Development

Use the repository-only [harness-check](.claude/skills/harness-check/SKILL.md)
skill to weigh a harness improvement, find existing capabilities, and compare
relevant implementations before deciding what to change. For example:
`$harness-check I am considering a new review skill. Do we already cover this,
and what could we learn from other harnesses?` In Claude Code, use
`/harness-check` with the same request.

`harness-check` provides advice; implementation or adoption starts when requested.
The repository-only `harness-check` and `adopt` skills live in `.claude/skills/`
with directory symlinks in `.agents/skills/` so both harnesses read one source.
They are available in this checkout and are not part of the installed plugin's
skill catalog. No plugin reinstall is needed for these project skills.

```sh
python3 scripts/sync_codex_policy.py
scripts/validate.sh
```

Validation checks the manifests, skill structure and references, invocation
policies, public-repository content rules, and bundled helpers. Harness
validators run when their tools are available; skipped checks are reported.

Keep the version, name, and description aligned in both plugin manifests.
Reinstall from the source you changed to refresh a cached plugin, then restart
Claude Code or start a new Codex task. The GitHub install commands above use
the published repository, so local changes must reach that source first.

Read [AGENTS.md](AGENTS.md) before contributing. Temporary work belongs in the
ignored `.local/` directory.

## License

Original astack code is MIT. See [LICENSE](LICENSE). Imported skills and
references retain their upstream licenses, recorded in `vendor.json` and copied
with each component.

## Teaching

`teach` is vendored from pstack under MIT. Invoke `$teach` in Codex or
`/astack:teach` in Claude Code with the code, change, or subsystem to explain.
It uses the bundled `how`, `why`, and `unslop` skills, preserves evidence and
uncertainty, and teaches in short conversational steps without quizzes.
Its compatibility patch resolves those dependencies, supports the available
delegation interface with a sequential fallback, and uses drawn SVG or HTML
diagrams when image generation is unavailable. Investigation remains read-only;
explanatory visuals may be created in an allowed artifact or scratch location.

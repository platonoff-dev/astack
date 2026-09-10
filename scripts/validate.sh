#!/usr/bin/env bash
# Validate the plugin against both harnesses' own validators, plus the local
# checks. Exits non-zero on any real failure.
#
# One class of Codex error is expected and filtered: explicit-only skills carry
# `disable-model-invocation: true`, which is how Claude Code is told to invoke
# them explicitly only. Codex rejects that field and reads
# `<skill>/agents/openai.yaml` (`policy.allow_implicit_invocation: false`)
# instead, which this plugin also ships. Both are correct for their harness, so
# the field cannot be removed — but every OTHER Codex error must still fail the
# run, which is why this filters that one message rather than ignoring the
# validator.
#
#   scripts/validate.sh          run everything
#   scripts/validate.sh -q       only report failures

set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
mkdir -p .local/tmp || exit 2
export TMPDIR="$PWD/.local/tmp"
export PYTHONDONTWRITEBYTECODE=1

QUIET=0
[[ "${1:-}" == "-q" ]] && QUIET=1

RC=0
CODEX_SYS="$HOME/.codex/skills/.system"
EXPECTED_RE='frontmatter field `disable-model-invocation` must be false'

say()  { [[ $QUIET -eq 1 ]] || printf '%s\n' "$*"; }
head_() { say ""; say "── $*"; }
pass() { say "   ok      $*"; }
fail() { printf '   FAIL    %s\n' "$*"; RC=1; }

need() { command -v "$1" >/dev/null 2>&1; }

# ---------------------------------------------------------------- manifests
head_ "manifests parse"
if python3 - <<'PY'
import json, sys
for f in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
          ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json"):
    json.load(open(f))
PY
then pass "all four manifests are valid JSON"; else fail "a manifest is not valid JSON"; fi

if python3 - <<'PY'
import json, sys
a = json.load(open(".claude-plugin/plugin.json"))
c = json.load(open(".codex-plugin/plugin.json"))
bad = [k for k in ("name", "version", "description") if a.get(k) != c.get(k)]
if bad:
    print("diverged:", ", ".join(bad)); sys.exit(1)
if "hooks" in c:
    print("codex manifest must not carry `hooks`"); sys.exit(1)
import re
if not re.fullmatch(r"\d+\.\d+\.\d+", str(a["version"])):
    print("version must be strict semver for Codex:", a["version"]); sys.exit(1)
PY
then pass "name/version/description identical across both manifests"; else fail "manifests disagree"; fi

# ------------------------------------------------------------ Claude Code
head_ "Claude Code validators"
if need claude; then
  for target in . .claude-plugin/plugin.json; do
    if out=$(claude plugin validate "$target" 2>&1); then
      pass "claude plugin validate $target"
    else
      fail "claude plugin validate $target"; printf '%s\n' "$out" | sed 's/^/           /'
    fi
  done
else
  say "   skip    claude CLI not on PATH"
fi

# ----------------------------------------------------------------- Codex
head_ "Codex validator (expected disable-model-invocation errors filtered)"
VAL="$CODEX_SYS/plugin-creator/scripts/validate_plugin.py"
validator=()
if python3 -B -c 'import yaml' >/dev/null 2>&1; then
  validator=(python3 -B)
elif need uvx; then
  validator=(uvx --cache-dir "$PWD/.local/tmp/uv-cache" --with pyyaml python -B)
fi
if [[ -f "$VAL" && ${#validator[@]} -gt 0 ]]; then
  validator_rc=0
  out=$("${validator[@]}" "$VAL" . 2>&1) || validator_rc=$?
  expected=$(printf '%s\n' "$out" | grep -c "$EXPECTED_RE")
  other=$(printf '%s\n' "$out" | grep -v "$EXPECTED_RE" | grep -E '^- ' || true)
  if [[ -n "$other" ]]; then
    fail "Codex reported errors beyond the expected class"
    printf '%s\n' "$other" | sed 's/^/           /'
  elif [[ "$validator_rc" -ne 0 && "$expected" -eq 0 ]]; then
    fail "Codex validator could not complete"
    printf '%s\n' "$out" | sed 's/^/           /'
  else
    pass "no Codex errors outside the expected class ($expected filtered)"
  fi
  declared=$(grep -l '^disable-model-invocation: true' skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$expected" -ne "$declared" ]]; then
    fail "filtered $expected errors but $declared skills declare the field — the filter is drifting"
  else
    pass "filtered count matches the $declared skills that declare it"
  fi
else
  say "   skip    Codex validator or Python YAML dependency unavailable"
fi

# ------------------------------------------------ Codex invocation policy
head_ "Codex invocation policy files"
if out=$(python3 -B scripts/sync_codex_policy.py --check 2>&1); then
  pass "agents/openai.yaml matches every SKILL.md frontmatter"
else
  fail "openai.yaml drift"; printf '%s\n' "$out" | sed 's/^/           /'
fi

# --------------------------------------------------------- skill structure
head_ "skill structure"
if python3 - <<'PY'
import re, sys
from pathlib import Path
bad = []
skills = sorted(Path("skills").glob("*/SKILL.md"))
for p in skills:
    text = p.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        bad.append(f"{p.parent.name}: no frontmatter"); continue
    end = text.find("\n---", 4)
    fm = text[4:end]
    for key in ("name", "description"):
        if not re.search(rf"^{key}:\s*\S", fm, re.M):
            bad.append(f"{p.parent.name}: frontmatter `{key}` missing or empty")
    # Both harnesses must register the same command name.
    m = re.search(r"^name:\s*(.+?)\s*$", fm, re.M)
    name = m.group(1).strip("'\"") if m else ""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p.parent.name):
        bad.append(f"{p.parent.name}: directory is not kebab-case")
    if m and name != p.parent.name:
        bad.append(f"{p.parent.name}: frontmatter `name` is `{name}`, not the directory name")
print(f"{len(skills)} skills scanned")
for b in bad:
    print("  " + b)
sys.exit(1 if bad else 0)
PY
then pass "every skill has a description and a kebab-case name equal to its directory"; else fail "a skill's frontmatter is incomplete or its name is not its directory"; fi

# Dangling in-plugin skill references: a `/name` that no shipped skill answers.
if python3 - <<'PY'
import re, sys
from pathlib import Path
shipped = {p.parent.name for p in Path("skills").glob("*/SKILL.md")}
# Slash names that belong to the harness, not to this plugin.
harness = {
    "loop", "simplify", "code-review", "init", "memory", "context", "compact",
    "goal", "model", "doctor", "hooks", "permissions", "config", "artifacts",
    "review", "run", "skill-doctor", "import",
}
known = shipped | harness
bad = []
for p in Path("skills").rglob("*.md"):
    for m in re.finditer(r"(?<![\w/`.])/([a-z][a-z0-9]+(?:-[a-z0-9]+)+)\b", p.read_text(encoding="utf-8")):
        name = m.group(1)
        if name not in known:
            bad.append(f"{p.relative_to('skills')}: /{name}")
seen = sorted(set(bad))
for b in seen:
    print("  " + b)
sys.exit(1 if seen else 0)
PY
then pass "no dangling /skill references"; else fail "a skill references a slash-name nothing ships"; fi

# --------------------------------------------- organisation-specific content
# Organisation values belong in the tracker adapter outside this public repo.
head_ "no organisation-specific content"

# Tracker hosts, wiki hosts, internal forges, tenant ids, account ids.
hosts=$(grep -rnEi \
  '[a-z0-9-]+\.(atlassian\.net|slite\.com|zendesk\.com)|gitlab\.(corp|internal)[a-z.]*|[a-z0-9-]+\.corp\.[a-z.]+' \
  skills README.md AGENTS.md --exclude-dir=node_modules \
  --include='*.md' --include='*.py' --include='*.ts' --include='*.mjs' --include='*.sh' \
  --include='*.yaml' 2>/dev/null \
  | grep -viE '\bexample\.|tracker\.example|your-|<[a-z-]+>' || true)
if [[ -z "$hosts" ]]; then
  pass "no real tracker, wiki or forge hostnames"
else
  fail "a real hostname is committed — use example.com or an adapter value"
  printf '%s\n' "$hosts" | sed 's/^/           /'
fi

# Tenant and account identifiers: bare UUIDs, Jira account ids, custom-field
# ids. A `customfield_*` key is the tell that a tracker's own schema leaked in.
ids=$(grep -rnE \
  'customfield_[0-9]{4,}|[0-9]{6}:[0-9a-f]{8}-[0-9a-f]{4}|\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b' \
  skills README.md AGENTS.md --exclude-dir=node_modules 2>/dev/null \
  | grep -viE 'adapter-format\.md|tracker_adapter\.py|test_tracker_adapter\.py' || true)
if [[ -z "$ids" ]]; then
  pass "no tenant, account or custom-field identifiers"
else
  fail "a tracker identifier is committed — it belongs in the tracker adapter"
  printf '%s\n' "$ids" | sed 's/^/           /'
fi

# Real work-item keys. A skill teaches with an invented key; a real one is
# either a live ticket or a real ticket's number, and both leak roadmap.
# PROJ and KEY are the placeholders this repo uses.
# The allowlist is the point: a real key is unknowable from outside this repo,
# so a prefix that is not a known placeholder or standard has to become one.
KEY_OK='PROJ|KEY|EPIC|TASK|ABC|XXX|NNN|ENG|BUG|SENTRY|SHA|ISO|CVE|RFC|IEEE|UTF|ASD|STE|ADR|GH|PR|MR'
keys=$(grep -rnoE '\b[A-Z]{2,6}-[0-9]{3,6}\b' skills README.md AGENTS.md \
  --exclude-dir=node_modules 2>/dev/null | grep -vE ":($KEY_OK)-" || true)
if [[ -z "$keys" ]]; then
  pass "no work-item keys outside the placeholder allowlist"
else
  fail "what looks like a real tracker key is committed (allowlist: $KEY_OK)"
  printf '%s\n' "$keys" | sed 's/^/           /'
fi

# A quotation attributed to a named person, or a private channel reference.
# The rule is: paraphrase the failure, drop the person. There is no acceptable
# version of a private remark with a name and a date on it.
quotes=$(grep -rnEi \
  '#[a-z0-9][a-z0-9_-]*-private|(said|wrote|asked|commented|quoted)[^.]{0,30}, [0-9]{2}/[0-9]{2}/[0-9]{4}|\(CEO, [0-9]' \
  skills README.md AGENTS.md --exclude-dir=node_modules \
  --include='*.md' --include='*.py' 2>/dev/null || true)
if [[ -z "$quotes" ]]; then
  pass "no dated attributions or private-channel references"
else
  fail "a named or dated attribution remains — paraphrase the failure instead"
  printf '%s\n' "$quotes" | sed 's/^/           /'
fi

# `.local/` is the scratch area and is gitignored wholesale. A `git add -f`
# defeats that silently, and scratch files are where unredacted tracker output
# and pasted document contents accumulate — so tracking one is a failure.
local_tracked=$(git ls-files .local 2>/dev/null || true)
if [[ -z "$local_tracked" ]]; then
  pass "nothing under .local/ is tracked"
else
  fail ".local/ is the scratch area and must never be tracked"
  printf '%s\n' "$local_tracked" | sed 's/^/           /'
fi

# ------------------------------------------------------------- unit tests
head_ "bundled tests"
for t in skills/setup-tracker/scripts/test_tracker_adapter.py; do
  if out=$(python3 -B "$t" 2>&1); then
    pass "$(basename "$t"): $(printf '%s' "$out" | grep -oE 'Ran [0-9]+ tests?' | head -1)"
  else
    fail "$t"; printf '%s\n' "$out" | tail -20 | sed 's/^/           /'
  fi
done

# weekly-report's helpers are stdlib-only: compile them all, then actually run
# the one that needs no arguments.
if out=$(python3 -B - <<'PYCOMPILE' 2>&1
from pathlib import Path
for path in Path("skills/weekly-report/scripts").glob("*.py"):
    compile(path.read_bytes(), str(path), "exec")
PYCOMPILE
); then
  n=$(ls skills/weekly-report/scripts/*.py | wc -l | tr -d ' ')
  pass "weekly-report: $n scripts compile"
else
  fail "weekly-report scripts do not compile"; printf '%s\n' "$out" | tail -10 | sed 's/^/           /'
fi
if out=$(python3 -B skills/weekly-report/scripts/week_window.py 2>&1) \
   && printf '%s' "$out" | grep -q 'window_start'; then
  pass "weekly-report: week_window.py runs ($(printf '%s' "$out" | grep -c . ) fields)"
else
  fail "week_window.py did not run"; printf '%s\n' "$out" | tail -10 | sed 's/^/           /'
fi

# --------------------------------------------------------------- summary
say ""
if [[ $RC -eq 0 ]]; then
  say "All checks passed."
else
  printf 'FAILED — see above.\n'
fi
exit $RC

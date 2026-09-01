"""Regression checks for the brief's placeholder routing contract. Run with python3 -B."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_brief import check


BRIEF = """# Example: Exports fail

Source: https://tracker.example/EX-1
Checked: 2026-09-01; source revision 2; commit abc123, clean; local fixture
Playbook: bug-fix
Modifiers: performance

## Outcome
Complete an export for the supported fixture without timing out.

## Evidence
- supported: The fixture fails at the request deadline. [Local run](evidence.md)

## Scope
Keep existing export contents and the public API unchanged.

## Completion checks
- The original fixture completes and its output matches the expected contents.

## Next step
Record that the bug-fix playbook is still a placeholder.
"""


MINIMAL = """# Example: Unknown behavior

Source: https://tracker.example/EX-2
Checked: 2026-09-01; source revision 1; commit def456, dirty; no runtime access
Playbook: investigation

## Outcome
Determine what work this task requires.

## Evidence
- unresolved: The reported environment is unavailable.

## Next step
Record the selected placeholder without inventing its procedure.
"""


class BriefChecks(unittest.TestCase):
    def test_supported_brief_passes(self):
        self.assertEqual(check(BRIEF), ([], []))

    def test_each_reserved_route_has_no_unadopted_policy(self):
        routes = (
            "investigation",
            "bug-fix",
            "feature",
            "refactor",
            "performance",
            "migration",
            "decision",
            "split",
            "no-change",
        )
        for playbook in routes:
            with self.subTest(playbook=playbook):
                routed = MINIMAL.replace("Playbook: investigation", f"Playbook: {playbook}")
                self.assertEqual(check(routed), ([], []))

    def test_playbook_is_one_supported_route(self):
        self.assertTrue(check(BRIEF.replace("Playbook: bug-fix", "Playbook: bug-fix, performance"))[0])
        self.assertTrue(check(BRIEF.replace("Playbook: bug-fix", "Playbook: unknown"))[0])
        duplicate = BRIEF.replace("Playbook: bug-fix", "Playbook: decision\nPlaybook: bug-fix")
        self.assertTrue(check(duplicate)[0])

    def test_modifiers_are_optional_unique_and_not_the_primary_playbook(self):
        self.assertFalse(check(BRIEF.replace("Modifiers: performance\n", ""))[0])
        self.assertFalse(check(BRIEF.replace("Modifiers: performance", "Modifiers: performance, migration"))[0])
        self.assertTrue(check(BRIEF.replace("Modifiers: performance", "Modifiers:"))[0])
        self.assertTrue(check(BRIEF.replace("Modifiers: performance", "Modifiers: performance, performance"))[0])
        self.assertTrue(check(BRIEF.replace("Modifiers: performance", "Modifiers: bug-fix"))[0])

    def test_legacy_fields_are_rejected_even_with_a_playbook(self):
        legacy = BRIEF.replace("Playbook: bug-fix", "Work type: bug\nNext action: implement")
        self.assertTrue(check(legacy)[0])
        self.assertTrue(check(BRIEF.replace("Playbook: bug-fix", "Playbook: bug-fix\nNext action: implement"))[0])

    def test_supported_and_contradicted_evidence_need_receipts(self):
        for status in ("supported", "contradicted"):
            with self.subTest(status=status):
                brief = BRIEF.replace("supported:", f"{status}:").replace("[Local run](evidence.md)", "")
                self.assertTrue(check(brief)[0])

    def test_code_example_is_not_evidence(self):
        embedded = BRIEF.replace("- supported:", "```markdown\n- supported:").replace(
            "\n## Scope", "\n```\n\n## Scope"
        )
        self.assertTrue(check(embedded)[0])

    def test_core_sections_remain_required(self):
        for heading in ("Outcome", "Evidence", "Next step"):
            with self.subTest(heading=heading):
                self.assertTrue(check(BRIEF.replace(f"## {heading}", f"## Missing {heading}"))[0])

    def test_long_brief_warns_without_discarding_requirements(self):
        errors, warnings = check(BRIEF + "\n" + "Required constraint. " * 310)
        self.assertFalse(errors)
        self.assertTrue(warnings)

    def test_source_link_can_include_a_quoted_path(self):
        self.assertFalse(check(BRIEF.replace("(evidence.md)", "(<receipts/local run.md>)"))[0])

    def test_wrapping_evidence_preserves_the_verdict(self):
        wrapped = BRIEF.replace("[Local run]", "\n  [Local run]")
        self.assertFalse(check(wrapped)[0])

    def test_cli_exit_codes_and_read_errors(self):
        checker = Path(__file__).with_name("check_brief.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "brief.md"
            for text, expected in ((BRIEF, 0), (BRIEF.replace("bug-fix", "unknown"), 1)):
                path.write_text(text, encoding="utf-8")
                result = subprocess.run([sys.executable, "-B", str(checker), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            path.unlink()
            result = subprocess.run([sys.executable, "-B", str(checker), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()

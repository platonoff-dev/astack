"""Regression checks for the brief's handoff rules. Run with python3 -B."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_brief import check


BRIEF = """# Example: Exports fail

Source: https://tracker.example/EX-1
Checked: 2026-08-31; source revision 2; commit abc123, clean; local fixture
Work type: bug, performance
Next action: implement

## Outcome
Complete an export for the supported fixture without timing out.

## Evidence
- supported: The fixture fails at the request deadline. [Local run](evidence.md)

## Scope
Keep existing export contents and the public API unchanged.

## Completion checks
- The original fixture completes and its output matches the expected contents.

## Next step
Fix the confirmed deadline handling and rerun the original fixture.
"""


class BriefChecks(unittest.TestCase):
    def test_supported_implementation_passes(self):
        self.assertEqual(check(BRIEF), ([], []))

    def test_unresolved_report_can_start_investigation_but_not_implementation(self):
        reported = BRIEF.replace(
            "- supported: The fixture fails at the request deadline. [Local run](evidence.md)",
            "- unresolved: Production failure reported; affected environment unavailable.",
        )
        self.assertTrue(check(reported)[0])
        self.assertFalse(check(reported.replace("Next action: implement", "Next action: investigate"))[0])
        self.assertTrue(check(reported.replace("Next action: implement", "Next action: no-change"))[0])

    def test_human_blocker_changes_implementation_to_decision(self):
        blocked = BRIEF + "\n## Questions\n- Owner: should exports finish in the background?\n"
        self.assertTrue(check(blocked)[0])
        self.assertFalse(check(blocked.replace("Next action: implement", "Next action: decide"))[0])
        self.assertTrue(check(BRIEF.replace("Next action: implement", "Next action: decide"))[0])

    def test_missing_receipt_does_not_support_claim(self):
        for status in ("supported", "contradicted"):
            with self.subTest(status=status):
                brief = BRIEF.replace("supported:", f"{status}:").replace("[Local run](evidence.md)", "")
                self.assertTrue(check(brief)[0])

    def test_code_example_is_not_evidence(self):
        embedded = BRIEF.replace("- supported:", "```markdown\n- supported:").replace(
            "\n## Scope", "\n```\n\n## Scope"
        )
        self.assertTrue(check(embedded)[0])

    def test_no_implementation_without_completion_check(self):
        self.assertTrue(check(BRIEF.replace("## Completion checks", "## Background"))[0])

    def test_split_requires_outcomes_checks_and_dependencies(self):
        split = BRIEF.replace("Next action: implement", "Next action: split")
        self.assertTrue(check(split)[0])
        children = "\n## Breakdown\n1. Export one fixture. Check: output matches. Depends on: none.\n"
        self.assertTrue(check(split + children)[0])
        children += "2. Support larger fixtures. Check: deadline respected. Depends on: 1.\n"
        self.assertFalse(check(split + children)[0])
        self.assertTrue(check((split + children).replace("Depends on: 1.", ""))[0])

    def test_ambiguous_duplicate_action_is_rejected(self):
        self.assertTrue(check(BRIEF.replace("Next action: implement", "Next action: decide\nNext action: implement"))[0])

    def test_long_brief_warns_without_discarding_requirements(self):
        errors, warnings = check(BRIEF + "\n" + "Required constraint. " * 310)
        self.assertFalse(errors)
        self.assertTrue(warnings)

    def test_source_link_can_include_a_quoted_path(self):
        self.assertFalse(check(BRIEF.replace("(evidence.md)", "(<receipts/local run.md>)"))[0])

    def test_wrapping_evidence_or_child_items_preserves_the_verdict(self):
        wrapped = BRIEF.replace("[Local run]", "\n  [Local run]")
        self.assertFalse(check(wrapped)[0])
        split = wrapped.replace("Next action: implement", "Next action: split")
        split += "\n## Breakdown\n1. First outcome.\n   Check: works.\n   Depends on: none.\n"
        split += "2. Second outcome.\n   Check: works.\n   Depends on: 1.\n"
        self.assertFalse(check(split)[0])

    def test_cli_exit_codes_and_read_errors(self):
        checker = Path(__file__).with_name("check_brief.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "brief.md"
            for text, expected in ((BRIEF, 0), (BRIEF.replace("implement", "unknown"), 1)):
                path.write_text(text, encoding="utf-8")
                result = subprocess.run([sys.executable, "-B", str(checker), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            path.unlink()
            result = subprocess.run([sys.executable, "-B", str(checker), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()

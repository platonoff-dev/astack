"""Regression checks for the brief's playbook-routing rules. Run with python3 -B."""

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
- The same fixture completes within the agreed deadline under comparable conditions.

## Next step
Follow the bug-fix playbook while retaining the performance measurement.
"""


class BriefChecks(unittest.TestCase):
    def test_supported_change_playbook_passes(self):
        self.assertEqual(check(BRIEF), ([], []))

    def test_unresolved_report_routes_to_investigation(self):
        reported = BRIEF.replace(
            "- supported: The fixture fails at the request deadline. [Local run](evidence.md)",
            "- unresolved: Production failure reported; affected environment unavailable.",
        ).replace("Playbook: bug-fix", "Playbook: investigation")
        self.assertFalse(check(reported)[0])
        self.assertTrue(check(reported.replace("Playbook: investigation", "Playbook: bug-fix"))[0])
        self.assertTrue(check(reported.replace("Playbook: investigation", "Playbook: no-change"))[0])

    def test_human_blocker_routes_to_decision(self):
        blocked = BRIEF + "\n## Questions\n- Owner: should exports finish in the background?\n"
        self.assertTrue(check(blocked)[0])
        self.assertFalse(check(blocked.replace("Playbook: bug-fix", "Playbook: decision"))[0])
        self.assertTrue(check(BRIEF.replace("Playbook: bug-fix", "Playbook: decision"))[0])

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

    def test_change_and_investigation_playbooks_require_completion_check(self):
        without_checks = BRIEF.replace("## Completion checks", "## Background")
        for playbook in ("bug-fix", "feature", "refactor", "performance", "migration", "investigation"):
            with self.subTest(playbook=playbook):
                self.assertTrue(check(without_checks.replace("Playbook: bug-fix", f"Playbook: {playbook}"))[0])

    def test_split_requires_outcomes_checks_and_dependencies(self):
        split = BRIEF.replace("Playbook: bug-fix", "Playbook: split")
        self.assertTrue(check(split)[0])
        children = "\n## Breakdown\n1. Export one fixture. Check: output matches. Depends on: none.\n"
        self.assertTrue(check(split + children)[0])
        children += "2. Support larger fixtures. Check: deadline respected. Depends on: 1.\n"
        self.assertFalse(check(split + children)[0])
        self.assertTrue(check((split + children).replace("Depends on: 1.", ""))[0])

    def test_playbook_is_one_supported_route(self):
        self.assertTrue(check(BRIEF.replace("Playbook: bug-fix", "Playbook: bug-fix, performance"))[0])
        self.assertTrue(check(BRIEF.replace("Playbook: bug-fix", "Playbook: unknown"))[0])
        duplicate = BRIEF.replace("Playbook: bug-fix", "Playbook: decision\nPlaybook: bug-fix")
        self.assertTrue(check(duplicate)[0])

    def test_each_playbook_accepts_its_required_shape(self):
        for playbook in ("investigation", "bug-fix", "feature", "refactor", "performance", "migration", "no-change"):
            with self.subTest(playbook=playbook):
                routed = BRIEF.replace("Playbook: bug-fix", f"Playbook: {playbook}")
                routed = routed.replace("Modifiers: performance\n", "")
                self.assertFalse(check(routed)[0])

        decision = BRIEF.replace("Playbook: bug-fix", "Playbook: decision")
        decision += "\n## Questions\n- Product owner: should exports finish in the background?\n"
        self.assertFalse(check(decision)[0])

        split = BRIEF.replace("Playbook: bug-fix", "Playbook: split")
        split += "\n## Breakdown\n1. First outcome. Check: works. Depends on: none.\n"
        split += "2. Second outcome. Check: works. Depends on: 1.\n"
        self.assertFalse(check(split)[0])

    def test_modifiers_are_optional_unique_and_not_the_primary_playbook(self):
        self.assertFalse(check(BRIEF.replace("Modifiers: performance\n", ""))[0])
        self.assertFalse(check(BRIEF.replace("Modifiers: performance", "Modifiers: performance, migration"))[0])
        self.assertTrue(check(BRIEF.replace("Modifiers: performance", "Modifiers:"))[0])
        self.assertTrue(check(BRIEF.replace("Modifiers: performance", "Modifiers: performance, performance"))[0])
        self.assertTrue(check(BRIEF.replace("Modifiers: performance", "Modifiers: bug-fix"))[0])

    def test_legacy_action_and_work_type_do_not_form_a_route(self):
        legacy = BRIEF.replace("Playbook: bug-fix\nModifiers: performance", "Work type: bug, performance\nNext action: implement")
        self.assertTrue(check(legacy)[0])
        self.assertTrue(check(BRIEF.replace("Playbook: bug-fix", "Playbook: bug-fix\nNext action: implement"))[0])

    def test_long_brief_warns_without_discarding_requirements(self):
        errors, warnings = check(BRIEF + "\n" + "Required constraint. " * 310)
        self.assertFalse(errors)
        self.assertTrue(warnings)

    def test_source_link_can_include_a_quoted_path(self):
        self.assertFalse(check(BRIEF.replace("(evidence.md)", "(<receipts/local run.md>)"))[0])

    def test_wrapping_evidence_or_child_items_preserves_the_verdict(self):
        wrapped = BRIEF.replace("[Local run]", "\n  [Local run]")
        self.assertFalse(check(wrapped)[0])
        split = wrapped.replace("Playbook: bug-fix", "Playbook: split")
        split += "\n## Breakdown\n1. First outcome.\n   Check: works.\n   Depends on: none.\n"
        split += "2. Second outcome.\n   Check: works.\n   Depends on: 1.\n"
        self.assertFalse(check(split)[0])

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

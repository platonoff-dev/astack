#!/usr/bin/env python3
"""Regression checks for weekly-report helpers, using only synthetic local data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--skill-dir", type=Path,
                    default=Path(__file__).resolve().parents[1] / "skills/weekly-report")
args, remaining = parser.parse_known_args()
SKILL = args.skill_dir.resolve()
sys.argv = [sys.argv[0], *remaining]


def issue(key, created, resolved, resolution="Done", status="Done"):
    return {"key": key, "fields": {
        "summary": "Save recovery", "created": created, "resolutiondate": resolved,
        "parent": {"key": "PROJ-400"},
        "status": {"name": status, "statusCategory": {
            "key": "done" if status == "Done" else "indeterminate"}},
        "resolution": {"name": resolution} if resolution else None,
    }}


class WeeklyReportHelpers(unittest.TestCase):
    def setUp(self):
        scratch = Path.cwd() / ".local/tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="weekly-report-", dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_helper(self, name, *arguments):
        return subprocess.run([sys.executable, "-B", str(SKILL / "scripts" / name),
                               *map(str, arguments)], text=True, capture_output=True)

    def tally(self, issues, *arguments):
        fixture = self.root / "issues.json"
        fixture.write_text(json.dumps({"issues": issues}))
        return self.run_helper("jira_tally.py", fixture, "--tally-only", *arguments)

    def test_historical_window_bounds_events_but_preserves_snapshot_progress(self):
        rows = [
            issue("PROJ-401", "2026-08-01", "2026-08-19T12:00:00Z"),
            issue("PROJ-402", "2026-08-02", "2026-08-21T12:00:00Z"),
            issue("PROJ-403", "2026-08-22", "2026-08-25T12:00:00Z", "Duplicate"),
            issue("PROJ-404", "2026-08-20", "2026-08-27T00:00:00Z"),
            issue("PROJ-405", "2026-08-28", "2026-08-30T12:00:00Z"),
            issue("PROJ-406", "2026-08-03", None, None, "In Progress"),
        ]
        result = self.tally(rows, "--since", "2026-08-20", "--until", "2026-08-27")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("+2 created", result.stdout)
        self.assertIn("2 resolved since", result.stdout)
        self.assertIn("[PROJ-402, PROJ-403]", result.stdout)
        self.assertIn("83% (5/6)", result.stdout)
        self.assertIn("resolved-Done=4", result.stdout)
        self.assertIn("closed without a Done resolution", result.stdout)

    def test_named_timezone_applies_to_bounds_and_respects_source_offsets(self):
        rows = [
            issue("PROJ-411", "2026-08-20T03:59:59Z", "2026-08-20T03:59:59Z"),
            issue("PROJ-412", "2026-08-20T06:00:00+02:00", "2026-08-20T06:00:00+02:00"),
            issue("PROJ-413", "2026-08-27T03:59:59Z", "2026-08-27T03:59:59Z"),
            issue("PROJ-414", "2026-08-27T04:00:00Z", "2026-08-27T04:00:00Z"),
        ]
        result = self.tally(rows, "--since", "2026-08-20", "--until", "2026-08-27",
                            "--timezone", "America/New_York")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("+2 created", result.stdout)
        self.assertIn("2 resolved since", result.stdout)
        self.assertIn("[PROJ-412, PROJ-413]", result.stdout)

    def test_explicit_offset_cutoffs_override_default_zone(self):
        rows = [issue("PROJ-420", "2026-08-19T23:30:00Z", "2026-08-19T23:30:00Z")]
        result = self.tally(rows, "--since", "2026-08-20T03:00:00+04:00",
                            "--until", "2026-08-20T04:00:00+04:00", "--timezone", "UTC")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("+1 created", result.stdout)
        self.assertIn("[PROJ-420]", result.stdout)

    def test_date_and_offset_free_values_use_selected_zone(self):
        rows = [issue("PROJ-421", "2026-08-20", "2026-08-20T00:00:00"),
                issue("PROJ-422", "2026-08-27", "2026-08-27T00:00:00")]
        result = self.tally(rows, "--since", "2026-08-19T20:00:00Z",
                            "--until", "2026-08-26T20:00:00Z", "--timezone", "Asia/Tbilisi")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("+1 created", result.stdout)
        self.assertIn("[PROJ-421]", result.stdout)

    def test_since_only_retains_open_ended_behavior(self):
        rows = [issue("PROJ-430", "2026-08-01", "2026-08-30T12:00:00Z")]
        result = self.tally(rows, "--since", "2026-08-20")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 resolved since 2026-08-20", result.stdout)
        self.assertIn("[PROJ-430]", result.stdout)

    def test_invalid_bounds_and_timezone_fail_before_output(self):
        cases = [
            ["--since", "not-a-date"],
            ["--since", "2026-08-27", "--until", "2026-08-20"],
            ["--since", "2026-08-20", "--until", "2026-08-20"],
            ["--until", "2026-08-27"],
            ["--timezone", "Invented/Nowhere"],
        ]
        for arguments in cases:
            with self.subTest(arguments=arguments):
                result = self.tally([], *arguments)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_invalid_source_timestamp_fails_before_partial_tally(self):
        rows = [issue("PROJ-440", "2026-08-20", "not-a-date")]
        result = self.tally(rows, "--since", "2026-08-20", "--until", "2026-08-27")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("PROJ-440 resolved", result.stderr)

    def test_week_queries_include_both_cutoffs_across_year_boundary(self):
        result = self.run_helper("week_window.py", "--date", "2025-12-31", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        window = json.loads(result.stdout)
        self.assertEqual((window["iso_year"], window["iso_week"]), (2026, 1))
        self.assertEqual(window["window_start"], "2025-12-25")
        self.assertEqual(window["window_end"], "2026-01-01")
        for field in ("updated", "resolved"):
            self.assertEqual(window["jql_" + field],
                             f'{field} >= "2025-12-25" AND {field} < "2026-01-01"')

    def lint_table(self, cells):
        text = "\n".join([
            "**Epics / Features in progress:**", "",
            "| Epic / Feature | Tracker | Status | Progress | ETA |",
            "| --- | --- | --- | --- | --- |",
            "| " + " | ".join(cells) + " |", "",
            "**Recently completed (since last week):**", "- *none*", "",
            "**This week:**", "- We merged 2 of the 4 fixes. Release follows next week.", "",
            "**Next week:**", "- Release the fixes ([PROJ-400](https://tracker.example.com/browse/PROJ-400)).", "",
            "**Blockers:** None", "",
        ])
        draft = self.root / "draft.md"
        draft.write_text(text)
        return self.run_helper("lint_report.py", draft, "--json")

    def test_known_table_facts_pass_lint(self):
        cells = ["Save recovery", "[PROJ-400](https://tracker.example.com/browse/PROJ-400)",
                 "Development", "50% (2/4)", "10/09/26"]
        result = self.lint_table(cells)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(any(f["severity"] == "ERROR" for f in json.loads(result.stdout)))

    def test_unresolved_placeholder_in_every_table_column_fails_lint(self):
        cells = ["Save recovery", "[PROJ-400](https://tracker.example.com/browse/PROJ-400)",
                 "Development", "50% (2/4)", "10/09/26"]
        for column in range(len(cells)):
            for placeholder in ("[?]", "TBD"):
                with self.subTest(column=column, placeholder=placeholder):
                    changed = list(cells)
                    changed[column] = placeholder
                    result = self.lint_table(changed)
                    self.assertEqual(result.returncode, 1, result.stdout)
                    failures = [f for f in json.loads(result.stdout)
                                if f["severity"] == "ERROR" and f["rule"] == "placeholder"]
                    self.assertEqual(len(failures), 1, result.stdout)
                    self.assertEqual(failures[0]["line"], 5)


if __name__ == "__main__":
    unittest.main()

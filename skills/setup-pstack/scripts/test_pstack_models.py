#!/usr/bin/env python3
"""Regression checks for the pstack model rule tool."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pstack_models as pm

CODEX_CACHE = {"gpt-5.6-sol": {"low", "medium", "high", "xhigh", "max", "ultra"}, "gpt-5.5": {"low", "medium", "high", "xhigh"}}


def mapping(value: str = "inherit-parent") -> dict[str, list[str]]:
    return {role: [value] for role in pm.ROLES}


class ValueTests(unittest.TestCase):
    def test_aliases_pass_on_both_harnesses(self) -> None:
        for harness in ("claude", "codex"):
            for alias in pm.ALIASES:
                self.assertIsNone(pm.validate_value(harness, alias, CODEX_CACHE))

    def test_claude_takes_agent_tool_aliases_only(self) -> None:
        self.assertIsNone(pm.validate_value("claude", "fable", None))
        self.assertIn("not an Agent tool model alias", pm.validate_value("claude", "claude-opus-5", None))

    def test_claude_rejects_effort_suffix(self) -> None:
        self.assertIn("no per-call effort", pm.validate_value("claude", "opus@high", None))

    def test_codex_checks_model_and_effort_against_cache(self) -> None:
        self.assertIsNone(pm.validate_value("codex", "gpt-5.6-sol@max", CODEX_CACHE))
        self.assertIn("does not offer effort", pm.validate_value("codex", "gpt-5.5@ultra", CODEX_CACHE))
        self.assertIn("not in Codex's model list", pm.validate_value("codex", "gpt-4o", CODEX_CACHE))

    def test_codex_without_cache_checks_syntax_only(self) -> None:
        self.assertIsNone(pm.validate_value("codex", "gpt-5.6-sol@max", None))
        self.assertIn("unsupported effort", pm.validate_value("codex", "gpt-5.6-sol@enormous", None))


class MappingTests(unittest.TestCase):
    def test_complete_mapping_with_panel_fanout_passes(self) -> None:
        m = mapping("sonnet")
        m["how critics"] = ["fable", "opus", "sonnet"]
        self.assertEqual(pm.validate("claude", m, None), [])

    def test_missing_role_and_non_panel_fanout_fail(self) -> None:
        m = mapping()
        m.pop("bug-fix")
        m["perf-issue"] = ["auto", "auto"]
        errors = pm.validate("claude", m, None)
        self.assertTrue(any("missing roles: bug-fix" in e for e in errors))
        self.assertTrue(any("not a panel" in e for e in errors))


class BlockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "AGENTS.md"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_roundtrip_and_check(self) -> None:
        m = mapping("gpt-5.5@high")
        m["arena runners"] = ["gpt-5.6-sol@max", "gpt-5.5@high"]
        pm.write_mapping("codex", self.path, m)
        text = self.path.read_text()
        self.assertEqual(pm.check_text("codex", text, CODEX_CACHE), [])
        parsed, errors = pm.parse_block("codex", pm.split_block(text)[1])
        self.assertEqual(errors, [])
        self.assertEqual(parsed, m)

    def test_block_replaces_only_itself_in_a_shared_file(self) -> None:
        self.path.write_text("# my rules\n\nbe brief\n")
        pm.write_mapping("codex", self.path, mapping())
        pm.write_mapping("codex", self.path, mapping("gpt-5.5"))
        text = self.path.read_text()
        self.assertTrue(text.startswith("# my rules\n\nbe brief\n"))
        self.assertEqual(text.count(pm.BEGIN), 1)
        self.assertEqual(text.count(pm.END), 1)
        self.assertIn("swarm workers: gpt-5.5\n", text)
        self.assertNotIn("swarm workers: inherit-parent", text)

    def test_content_after_the_block_survives(self) -> None:
        pm.write_mapping("codex", self.path, mapping())
        self.path.write_text(self.path.read_text() + "\nlater note\n")
        pm.write_mapping("codex", self.path, mapping("auto"))
        self.assertTrue(self.path.read_text().endswith("\nlater note\n"))

    def test_stray_line_inside_block_is_reported(self) -> None:
        pm.write_mapping("claude", self.path, mapping("sonnet"))
        text = self.path.read_text().replace(pm.END, "hardest task: fable\n" + pm.END)
        errors = pm.check_text("claude", text, None)
        self.assertTrue(any("unrecognised line" in e for e in errors), errors)

    def test_missing_block_is_an_error(self) -> None:
        self.assertEqual(pm.check_text("claude", "# nothing here\n", None), [f"no {pm.BEGIN} ... {pm.END} block"])


class HarnessTests(unittest.TestCase):
    def test_env_detection(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDECODE": "1"}, clear=True):
            self.assertEqual(pm.detect_harness(None), "claude")
        with mock.patch.dict(os.environ, {"CODEX_HOME": "/x"}, clear=True):
            self.assertEqual(pm.detect_harness(None), "codex")
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit):
                pm.detect_harness(None)
        self.assertEqual(pm.detect_harness("codex"), "codex")

    def test_codex_prefers_override_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"CODEX_HOME": tmp}):
            self.assertEqual(pm.target_path("codex"), Path(tmp) / "AGENTS.md")
            (Path(tmp) / "AGENTS.override.md").write_text("")
            self.assertEqual(pm.target_path("codex"), Path(tmp) / "AGENTS.override.md")


if __name__ == "__main__":
    unittest.main()

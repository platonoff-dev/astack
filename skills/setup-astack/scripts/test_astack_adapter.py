#!/usr/bin/env python3
"""Behavior checks using fictional bundles; no account or network access."""

import contextlib
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import astack_adapter as aa

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "skills/setup-tracker/scripts"))
import tracker_adapter as ta  # noqa: E402


class BundleTests(unittest.TestCase):
    def setUp(self):
        scratch = REPO / ".local/tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(temporary.cleanup)
        self.tmp = Path(temporary.name).resolve()
        self.repo = self.tmp / "project"
        self.repo.mkdir()
        (self.repo / ".git").write_text("gitdir: fictional-worktree\n")
        self.env = {k: v for k, v in os.environ.items()
                    if k not in (aa.ENV_VAR, ta.ENV_VAR)}
        for p in (patch.dict(os.environ, self.env, clear=True),
                  patch.object(aa, "USER_PATH", self.tmp / "user/adapter.toml"),
                  patch.object(ta, "USER_PATH", self.tmp / "user/tracker-adapter.toml")):
            p.start()
            self.addCleanup(p.stop)

    def bundle(self, path=None, text=None):
        path = path or self.repo / ".agents/astack/adapter.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text or '''version = 1
tracker_adapter = "tracker-adapter.toml"
[systems.work]
kind = "custom-service"
roles = ["tracker", "review"]
instructions = "systems/work.md"
[systems.work.facts]
project = "PROJ"
''')
        (path.parent / "systems").mkdir(exist_ok=True)
        (path.parent / "systems/work.md").write_text("# Work\nAccess not yet checked.\n")
        (path.parent / "tracker-adapter.toml").write_text(ta.TEMPLATE)
        return path

    def test_nearest_project_beats_root_and_user(self):
        self.bundle(aa.USER_PATH)
        self.bundle()
        child = self.repo / "src"
        chosen = self.bundle(child / ".claude/astack/adapter.toml")
        deep = child / "package"
        deep.mkdir()
        self.assertEqual(aa.resolve(deep)[0], chosen)

    def test_agents_precedes_claude_at_same_depth(self):
        chosen = self.bundle()
        self.bundle(self.repo / ".claude/astack/adapter.toml")
        self.assertEqual(aa.resolve(self.repo)[0], chosen)

    def test_worktree_boundary_does_not_select_outer_project(self):
        self.bundle(self.tmp / ".agents/astack/adapter.toml")
        self.assertIsNone(aa.resolve(self.repo))
        self.bundle(aa.USER_PATH)
        self.assertEqual(aa.resolve(self.repo)[0], aa.USER_PATH)

    def test_non_repository_does_not_search_ancestors(self):
        self.bundle(self.tmp / ".agents/astack/adapter.toml")
        child = self.tmp / "plain"
        child.mkdir()
        # Fixtures live inside this real repository's .local tree. Simulate
        # no Git ancestor without writing temporary files outside that tree.
        exists = Path.exists
        with patch.object(Path, "exists", lambda p: False if p.name == ".git" else exists(p)):
            self.assertIsNone(aa.resolve(child))

    def test_explicit_relative_path_wins_and_missing_override_fails(self):
        self.bundle()
        chosen = self.bundle(self.tmp / "selected/adapter.toml")
        os.environ[aa.ENV_VAR] = "../selected/adapter.toml"
        self.assertEqual(aa.resolve(self.repo)[0].resolve(), chosen)
        for value in ("../missing.toml", ""):
            with self.subTest(value=value):
                os.environ[aa.ENV_VAR] = value
                with self.assertRaises(aa.AdapterError):
                    aa.resolve(self.repo)

    def test_invalid_selected_index_does_not_fall_back(self):
        chosen = self.bundle(text="version = 99\n[systems]\n")
        self.bundle(aa.USER_PATH)
        self.assertEqual(aa.resolve(self.repo)[0], chosen)
        with self.assertRaises(aa.AdapterError):
            aa.load(chosen)
        with self.assertRaises(ta.AdapterError):
            ta.resolve(self.repo)

    def test_dangling_project_symlink_does_not_fall_back(self):
        chosen = self.repo / ".agents/astack/adapter.toml"
        chosen.parent.mkdir(parents=True)
        chosen.symlink_to("missing.toml")
        self.bundle(aa.USER_PATH)
        with self.assertRaises(aa.AdapterError):
            aa.resolve(self.repo)

    def test_role_filter_returns_resolved_paths_and_missing_roles(self):
        path = self.bundle()
        data = aa.load(path)
        result = aa.view(data, path, "test", ["review", "report"])
        self.assertEqual(set(result["systems"]), {"work"})
        self.assertEqual(result["unconfigured_roles"], ["report"])
        self.assertEqual(result["systems"]["work"]["instructions"],
                         str(path.parent / "systems/work.md"))
        self.assertEqual(result["tracker_adapter"], str(path.parent / "tracker-adapter.toml"))
        self.assertEqual(aa.view(data, path, "test", ["report"])["systems"], {})
        self.assertEqual(len(aa.view(data, path, "test", [])["systems"]), 1)

    def test_partial_bundle_and_custom_roles_are_valid(self):
        path = self.bundle(text="version = 1\n[systems]\n")
        self.assertEqual(aa.load(path)["systems"], {})
        data = {"version": 1, "systems": {"custom": {
            "kind": "anything", "roles": ["research"],
            "instructions": "systems/work.md", "facts": {"space": "fictional"}}}}
        self.assertEqual(aa.check(data, path), [])

    def test_schema_mistakes_are_rejected(self):
        path = self.bundle()
        original = aa.load(path)
        mutations = [
            lambda d: d.update(version=True),
            lambda d: d.update(version=2),
            lambda d: d.update(traker_adapter="typo.toml"),
            lambda d: d.update(tracker_adapter="missing.toml"),
            lambda d: d.update(systems=[]),
            lambda d: d["systems"].update(work="bad"),
            lambda d: d["systems"]["work"].update(role=["tracker"]),
            lambda d: d["systems"]["work"].update(kind=""),
            lambda d: d["systems"]["work"].update(roles=[]),
            lambda d: d["systems"]["work"].update(roles=["tracker", "tracker"]),
            lambda d: d["systems"]["work"].update(roles=[{}]),
            lambda d: d["systems"]["work"].update(facts=[]),
            lambda d: d["systems"]["work"].update(instructions="missing.md"),
        ]
        for i, mutate in enumerate(mutations):
            with self.subTest(case=i):
                data = copy.deepcopy(original)
                mutate(data)
                self.assertTrue(aa.check(data, path))

    def test_empty_or_non_utf8_guide_is_rejected(self):
        path = self.bundle()
        for content in (b" \n", b"\xff"):
            (path.parent / "systems/work.md").write_bytes(content)
            with self.assertRaises(aa.AdapterError):
                aa.load(path)

    def test_malformed_toml_is_reported(self):
        path = self.bundle(text="[broken\n")
        with self.assertRaises(aa.AdapterError):
            aa.load(path)

    def test_tracker_link_is_used_and_explicit_override_still_wins(self):
        path = self.bundle()
        linked = path.parent / "tracker-adapter.toml"
        self.assertEqual(ta.resolve(self.repo)[0], linked)
        override = self.tmp / "one-off.toml"
        override.write_text(ta.TEMPLATE)
        os.environ[ta.ENV_VAR] = str(override)
        self.assertEqual(ta.resolve(self.repo)[0], override)
        os.environ[ta.ENV_VAR] = str(self.tmp / "missing.toml")
        with self.assertRaises(ta.AdapterError):
            ta.resolve(self.repo)

    def test_partial_bundle_never_borrows_legacy_tracker(self):
        self.bundle(text="version = 1\n[systems]\n")
        ta.USER_PATH.parent.mkdir(parents=True)
        ta.USER_PATH.write_text(ta.TEMPLATE)
        with self.assertRaises(ta.AdapterError):
            ta.resolve(self.repo)

    def test_legacy_tracker_works_without_index(self):
        path = self.repo / ".agents/tracker-adapter.toml"
        path.parent.mkdir()
        path.write_text(ta.TEMPLATE)
        self.assertEqual(ta.resolve(self.repo)[0], path)
        self.assertEqual(ta.check(ta.load(path)), [])

    def test_cli_distinguishes_missing_invalid_and_valid(self):
        with patch.object(aa, "resolve", return_value=None), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(aa.main(["show", "--json"]), 2)
        path = self.bundle(text="version = 9\n[systems]\n")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(aa.main(["validate", str(path)]), 1)
        self.bundle(path)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            self.assertEqual(aa.main(["show", str(path), "--json", "--role", "tracker"]), 0)
        self.assertIn("work", json.loads(stream.getvalue())["systems"])

    def test_real_cli_from_other_directory_reads_bundle_and_tracker(self):
        path = self.bundle()
        env = {**os.environ, aa.ENV_VAR: str(path), "PYTHONDONTWRITEBYTECODE": "1"}
        for script, args in ((Path(aa.__file__), ["show", "--json", "--role", "review"]),
                             (Path(ta.__file__), ["show", "--json"])):
            run = subprocess.run([sys.executable, "-B", str(script), *args],
                                 cwd=self.tmp, env=env, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(run.stdout)
            if script == Path(aa.__file__):
                self.assertIn("work", result["systems"])
            else:
                self.assertEqual(result["tracker"]["project"], "PROJ")


if __name__ == "__main__":
    unittest.main(verbosity=2)

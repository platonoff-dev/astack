#!/usr/bin/env python3
"""Exercise vendoring against real local Git repositories; no network needed."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import shutil
import tempfile
import unittest
from unittest.mock import patch

import vendor
import sync_codex_policy


class VendorTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parent.parent / ".local" / "tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "plugin"
        self.root.mkdir()
        self.git(self.root, "init", "-q")  # Regression: staging is nested in a Git worktree.
        (self.root / "vendor.json").write_text('{"version": 1, "skills": []}\n')
        self.upstream = self.make_upstream("upstream")

    def git(self, cwd, *args):
        return subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=Test",
             "-c", "user.email=test@example.com", *args], cwd=cwd,
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def commit(self, repo):
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-qm", "fixture change")
        return self.git(repo, "rev-parse", "HEAD")

    def make_upstream(self, dirname, name="demo"):
        repo = self.base / dirname
        repo.mkdir()
        self.git(repo, "init", "-q", "-b", "main")
        skill = repo / "pack" / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Demonstrate vendoring.\n"
            "disable-model-invocation: true\n---\n\nOriginal body.\n"
        )
        (skill / "run.sh").write_text("#!/bin/sh\nexit 0\n")
        (skill / "run.sh").chmod(0o755)
        (repo / "LICENSE").write_text("Fixture license text\n")
        self.commit(repo)
        return repo

    def command(self, *args, code=0):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(vendor, "ROOT", self.root), redirect_stdout(stdout), redirect_stderr(stderr):
            result = vendor.main(list(args))
        output = stdout.getvalue() + stderr.getvalue()
        self.assertEqual(result, code, output)
        return output

    def add(self, name="demo", repo=None, extra=(), code=0):
        return self.command(
            "add", "--name", name, "--repo", str(repo or self.upstream),
            "--path", f"pack/skills/{name}", "--ref", "main", "--license", "MIT",
            *extra, code=code,
        )

    def state(self):
        return ((self.root / "vendor.json").read_bytes(), vendor.snapshot(self.root / "skills"))

    def entry(self, name="demo"):
        return next(e for e in json.loads((self.root / "vendor.json").read_text())["skills"] if e["name"] == name)

    def upstream_body(self, body, name="demo", repo=None):
        repo = repo or self.upstream
        skill = repo / "pack" / "skills" / name / "SKILL.md"
        skill.write_text(skill.read_text().replace("Original body.", body))
        return self.commit(repo)

    def compatibility_patch(self):
        path = self.root / "vendor" / "patches" / "demo.patch"
        path.parent.mkdir(parents=True)
        path.write_text(
            "diff --git a/SKILL.md b/SKILL.md\n--- a/SKILL.md\n+++ b/SKILL.md\n"
            "@@ -7 +7 @@\n-Original body.\n+Adapted body.\n"
        )
        return "vendor/patches/demo.patch"

    def test_add_check_update_and_sync(self):
        self.add()
        skill = self.root / "skills" / "demo"
        self.assertEqual((skill / "LICENSE").read_text(), "Fixture license text\n")
        self.assertTrue((skill / "run.sh").stat().st_mode & 0o111)
        self.assertIn("allow_implicit_invocation: false", (skill / "agents/openai.yaml").read_text())
        self.assertIn("CURRENT demo", self.command("check"))
        before = self.state()
        head = self.upstream_body("New body.")
        self.assertIn("UPDATE demo", self.command("check", code=1))
        self.assertEqual(self.state(), before)
        self.command("update", "demo")
        self.assertEqual(self.entry()["commit"], head)
        self.assertIn("New body.", (skill / "SKILL.md").read_text())
        after = self.state()
        self.command("sync")
        self.assertEqual(self.state(), after)

    def test_unrelated_commits_are_not_updates_but_license_changes_are(self):
        self.add()
        (self.upstream / "README.md").write_text("Unrelated change\n")
        self.commit(self.upstream)
        self.assertIn("CURRENT demo", self.command("check"))
        (self.upstream / "LICENSE").write_text("Updated fixture license\n")
        self.commit(self.upstream)
        self.assertIn("changed LICENSE", self.command("check", code=1))

    def test_local_changes_protected_and_explicit_force_restores(self):
        self.add()
        skill = self.root / "skills" / "demo"
        (skill / "SKILL.md").write_text("Local work\n")
        before = self.state()
        self.command("update", code=2)
        self.command("sync", code=2)
        self.assertEqual(self.state(), before)
        self.assertIn("EDITED demo", self.command("check", code=1))
        self.command("sync", "demo", "--force")
        self.assertIn("Original body.", (skill / "SKILL.md").read_text())

    def test_patch_applies_inside_ancestor_git_and_conflict_preserves_everything(self):
        patch_path = self.compatibility_patch()
        self.add(extra=("--patch", patch_path))
        self.assertIn("Adapted body.", (self.root / "skills/demo/SKILL.md").read_text())
        self.command("check")
        before = self.state()
        self.upstream_body("Conflicting body.")
        self.command("check", code=2)
        self.command("update", code=2)
        self.assertEqual(self.state(), before)

    def test_second_repo_and_batch_failure_leaves_first_pin_and_files_untouched(self):
        other = self.make_upstream("other", "second")
        self.add()
        self.add("second", other)
        before = self.state()
        self.upstream_body("New body.")
        (other / "LICENSE").unlink()
        self.commit(other)
        self.command("update", code=2)
        self.assertEqual(self.state(), before)
        self.assertIn("UPDATE demo", self.command("check", code=2))
        self.command("update", "demo")
        self.assertIn("New body.", (self.root / "skills/demo/SKILL.md").read_text())

    def test_failed_add_leaves_no_entry_or_skill(self):
        before = self.state()
        self.add(extra=("--license-path", "MISSING"), code=2)
        self.assertEqual(self.state(), before)
        self.assertFalse((self.root / "skills/demo").exists())

    def test_existing_first_party_skill_is_not_overwritten(self):
        target = self.root / "skills/demo"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("My skill")
        before = self.state()
        self.add(code=2)
        self.assertEqual(self.state(), before)

    def test_pin_old_commit_track_branch_and_annotated_tag(self):
        old = self.git(self.upstream, "rev-parse", "HEAD")
        head = self.upstream_body("New body.")
        self.add(extra=("--commit", old))
        self.assertEqual(self.entry()["commit"], old)
        self.command("check", code=1)
        self.command("update")
        self.assertEqual(self.entry()["commit"], head)
        self.git(self.upstream, "tag", "-am", "version", "v1")
        other_root = self.base / "tag-plugin"
        other_root.mkdir()
        (other_root / "vendor.json").write_text('{"version":1,"skills":[]}')
        self.root = other_root
        self.add(extra=("--ref", "refs/tags/v1"))
        self.assertEqual(self.entry()["commit"], head)
        self.command("check")

    def test_symlink_upstream_and_path_escape_rejected(self):
        self.add(extra=("--path", "../outside"), code=2)
        (self.upstream / "pack/skills/demo/link").symlink_to("/etc/passwd")
        self.commit(self.upstream)
        before = self.state()
        self.add(code=2)
        self.assertEqual(self.state(), before)

    def test_missing_skill_restored_and_mode_drift_detected(self):
        self.add()
        script = self.root / "skills/demo/run.sh"
        script.chmod(0o644)
        self.assertIn("changed run.sh", self.command("check", code=1))
        self.command("sync", "--force")
        shutil.rmtree(self.root / "skills/demo")
        self.command("sync")
        self.assertTrue(script.is_file())

    def test_upstream_policy_metadata_preserved(self):
        policy = self.upstream / "pack/skills/demo/agents/openai.yaml"
        policy.parent.mkdir()
        policy.write_text(
            "interface:\n  display_name: Custom title\n  short_description: Custom description\n"
            "policy:\n  allow_implicit_invocation: false\n"
        )
        self.commit(self.upstream)
        self.add()
        before = self.state()
        with patch.object(sync_codex_policy, "SKILLS", self.root / "skills"), patch("sys.argv", ["sync"]), redirect_stdout(io.StringIO()):
            self.assertEqual(sync_codex_policy.main(), 0)
        self.assertEqual(self.state(), before)
        self.assertEqual((self.root / "skills/demo/agents/openai.yaml").read_bytes(), policy.read_bytes())

    def test_write_failure_rolls_back_skill_and_manifest(self):
        self.add()
        self.upstream_body("New body.")
        before = self.state()
        original = Path.replace

        def fail_manifest(path, target):
            if target == self.root / "vendor.json":
                raise OSError("simulated manifest write failure")
            return original(path, target)

        with patch.object(Path, "replace", fail_manifest):
            self.command("update", code=2)
        self.assertEqual(self.state(), before)

    def test_root_skill_and_remote_default_branch(self):
        skill = self.upstream / "pack/skills/demo"
        for path in skill.iterdir():
            path.rename(self.upstream / path.name)
        shutil.rmtree(self.upstream / "pack")
        self.git(self.upstream, "branch", "-m", "trunk")
        self.commit(self.upstream)
        self.add(extra=("--path", ".", "--ref", "HEAD"))
        self.command("check")
        self.assertEqual((self.root / "skills/demo/LICENSE").read_text(), "Fixture license text\n")

    def test_patch_paths_cannot_escape_plugin(self):
        self.add(extra=("--patch", "vendor/patches/../../../outside.patch"), code=2)
        patch_dir = self.root / "vendor/patches"
        patch_dir.mkdir(parents=True)
        (patch_dir / "outside.patch").symlink_to(self.upstream / "LICENSE")
        self.add(extra=("--patch", "vendor/patches/outside.patch"), code=2)
        self.assertEqual(json.loads((self.root / "vendor.json").read_text())["skills"], [])

    def test_edit_during_network_preparation_is_not_lost(self):
        self.add()
        self.upstream_body("New body.")
        original = vendor.materialise
        manifest = (self.root / "vendor.json").read_bytes()

        def edit_after_fetch(*args):
            result = original(*args)
            (self.root / "skills/demo/run.sh").write_text("Work written while fetching\n")
            return result

        with patch.object(vendor, "materialise", edit_after_fetch):
            self.command("update", code=2)
        self.assertEqual((self.root / "vendor.json").read_bytes(), manifest)
        self.assertIn("Work written", (self.root / "skills/demo/run.sh").read_text())


if __name__ == "__main__":
    unittest.main()

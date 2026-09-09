#!/usr/bin/env python3
"""Unit tests for tracker_adapter.py. Stdlib only; run directly."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tracker_adapter as ta  # noqa: E402

MINIMAL = """
[tracker]
kind = "jira"
project = "PROJ"
key_pattern = "PROJ-\\\\d+"
browse_url = "https://example.atlassian.net/browse/{key}"

[statuses]
active = ["In Progress"]
parked = ["In Review"]
blocked = ["Blocked"]
excluded = ["Done"]
shovel_ready = ["Backlog"]
"""


def write(text, dirpath=None):
    d = Path(dirpath or tempfile.mkdtemp())
    d.mkdir(parents=True, exist_ok=True)
    p = d / ta.BASENAME
    p.write_text(text, encoding="utf-8")
    return p


class Schema(unittest.TestCase):
    def test_minimal_adapter_passes(self):
        self.assertEqual(ta.check(ta.load(write(MINIMAL))), [])

    def test_template_passes(self):
        self.assertEqual(ta.check(ta.load(write(ta.TEMPLATE))), [])

    def test_missing_tracker_section(self):
        errors = ta.check({})
        self.assertIn("[tracker]: missing", errors)
        self.assertIn("[statuses]: missing", errors)

    def test_every_bucket_role_is_required(self):
        text = MINIMAL.replace('shovel_ready = ["Backlog"]', "")
        self.assertIn(
            "statuses.shovel_ready: missing — every bucket needs a mapping",
            ta.check(ta.load(write(text))),
        )

    def test_a_status_may_not_carry_two_buckets(self):
        text = MINIMAL.replace('blocked = ["Blocked"]', 'blocked = ["In Progress"]')
        errors = ta.check(ta.load(write(text)))
        self.assertTrue(any("maps to exactly one bucket" in e for e in errors), errors)

    def test_unknown_role_is_rejected(self):
        text = MINIMAL + '\n[labels]\nurgent = ["p0"]\n'
        self.assertIn("labels.urgent: not a label role", ta.check(ta.load(write(text))))

    def test_key_pattern_must_compile(self):
        text = MINIMAL.replace('key_pattern = "PROJ-\\\\d+"', 'key_pattern = "PROJ-(\\\\d+"')
        errors = ta.check(ta.load(write(text)))
        self.assertTrue(any("not a valid regex" in e for e in errors), errors)

    def test_browse_url_must_carry_the_key(self):
        text = MINIMAL.replace("/browse/{key}", "/browse/")
        self.assertIn("tracker.browse_url: must contain {key}", ta.check(ta.load(write(text))))

    def test_ladder_must_end_in_other(self):
        text = MINIMAL + '\n[ladder]\nclasses = ["support", "critical"]\n'
        self.assertIn("ladder.classes: the last class must be 'other'", ta.check(ta.load(write(text))))

    def test_wip_cap_must_be_positive(self):
        text = MINIMAL + "\n[wip]\ncap = 0\n"
        self.assertIn("wip.cap: must be a positive integer", ta.check(ta.load(write(text))))

    def test_forge_requires_a_project(self):
        text = MINIMAL + '\n[review]\nforge = "gitlab"\n'
        self.assertIn("review.project: required when forge is 'gitlab'", ta.check(ta.load(write(text))))

    def test_bad_toml_is_reported_as_such(self):
        p = write("[tracker\nkind = 'jira'\n")
        with self.assertRaises(ta.AdapterError) as caught:
            ta.load(p)
        self.assertIn("not valid TOML", str(caught.exception))


class Resolution(unittest.TestCase):
    def setUp(self):
        self.env = os.environ.pop(ta.ENV_VAR, None)
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        (self.tmp / ".git").mkdir()

    def tearDown(self):
        if self.env is not None:
            os.environ[ta.ENV_VAR] = self.env

    def test_env_var_wins(self):
        chosen = write(MINIMAL, self.tmp / "elsewhere")
        write(MINIMAL, self.tmp / ".agents")
        os.environ[ta.ENV_VAR] = str(chosen)
        try:
            path, why = ta.resolve(self.tmp)
        finally:
            del os.environ[ta.ENV_VAR]
        self.assertEqual(path, chosen)
        self.assertIn(ta.ENV_VAR, why)

    def test_project_adapter_is_found_from_a_subdirectory(self):
        chosen = write(MINIMAL, self.tmp / ".agents")
        deep = self.tmp / "src" / "pkg"
        deep.mkdir(parents=True)
        path, why = ta.resolve(deep)
        self.assertEqual(path, chosen)
        self.assertEqual(why, "project .agents/")

    def test_search_stops_at_the_repository_root(self):
        outside = write(MINIMAL, self.tmp.parent / ".agents")
        try:
            with self.assertRaises(ta.AdapterError) as caught:
                ta.resolve(self.tmp)
            self.assertIn("no tracker adapter found", str(caught.exception))
        finally:
            outside.unlink()

    def test_missing_adapter_lists_where_it_looked(self):
        with self.assertRaises(ta.AdapterError) as caught:
            ta.resolve(self.tmp)
        message = str(caught.exception)
        self.assertIn(".agents/", message)
        self.assertIn("/setup-tracker", message)


class Resolved(unittest.TestCase):
    def test_every_role_is_present_even_when_unset(self):
        adapter = ta.resolved(ta.load(write(MINIMAL)))
        self.assertEqual(sorted(adapter["labels"]), sorted(ta.LABEL_ROLES))
        self.assertEqual(adapter["labels"]["ready_for_agent"], [])
        self.assertEqual(adapter["wip"], {"cap": 3, "stale_days": 5})
        self.assertEqual(adapter["ladder"]["classes"], ["other"])

    def test_render_names_the_source(self):
        p = write(MINIMAL)
        out = ta.render(ta.resolved(ta.load(p)), p, "user default")
        self.assertIn("user default", out)
        self.assertIn("PROJ", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)

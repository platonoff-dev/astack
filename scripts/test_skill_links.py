#!/usr/bin/env python3
"""Exercise missing-file and heading checks with isolated Markdown fixtures."""

from pathlib import Path
import tempfile
import unittest

from check_skill_links import check_links


class LinkTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parents[1] / ".local/tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_reference_move_requires_updating_caller(self):
        caller = self.write("SKILL.md", "[Read](references/old.md)\n")
        reference = self.write("references/old.md", "# Principle\n")
        self.assertEqual(check_links([caller]), [])
        reference.rename(reference.with_name("new.md"))
        self.assertEqual(len(check_links([caller])), 1)
        caller.write_text("[Read](references/new.md)\n")
        self.assertEqual(check_links([caller]), [])

    def test_headings_and_duplicate_heading_fragments(self):
        target = self.write("guide.md", "# A Guide\n\n## Same\n\n## Same\n")
        caller = self.write("SKILL.md", "[Top](guide.md#a-guide) [Second](guide.md#same-1)\n")
        self.assertEqual(check_links([caller]), [])
        target.write_text("# A Guide\n\n## Same\n")
        self.assertIn("missing heading", check_links([caller])[0])

    def test_relative_encoded_and_external_links(self):
        caller = self.write("references/nested.md", "[Local](../a%20guide.md#title) [Web](https://example.com/missing.md) [Template](browse_url)\n")
        self.write("a guide.md", "# Title\n")
        self.assertEqual(check_links([caller]), [])


if __name__ == "__main__":
    unittest.main()

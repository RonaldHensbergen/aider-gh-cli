"""Tests for aider_gh_cli.template."""

import unittest

from aider_gh_cli.template import (
    DEFAULT_TEMPLATE,
    load_template,
    render_template,
    strip_context,
)


class TestDefaultTemplate(unittest.TestCase):
    def test_default_template_contains_required_sections(self):
        for section in (
            "## Summary",
            "## Type Of Change",
            "## User Impact",
            "## Validation",
            "## Checklist",
        ):
            self.assertIn(section, DEFAULT_TEMPLATE)

    def test_default_template_has_checklist_items(self):
        for item in (
            "Bug fix",
            "Feature",
            "Refactor",
            "Docs",
            "Test only",
        ):
            self.assertIn(item, DEFAULT_TEMPLATE)

    def test_default_template_has_checklist_checkboxes(self):
        self.assertIn("- [ ] Tests added or updated", DEFAULT_TEMPLATE)
        self.assertIn("- [ ] Docs updated (README or docs)", DEFAULT_TEMPLATE)
        self.assertIn("- [ ] No secrets committed", DEFAULT_TEMPLATE)
        self.assertIn("- [ ] Generated artifacts excluded from git", DEFAULT_TEMPLATE)

    def test_default_template_has_validation_command(self):
        self.assertIn(
            'python -m unittest discover -s tests -p "*.py"',
            DEFAULT_TEMPLATE,
        )

    def test_default_template_has_aider_prompts(self):
        self.assertIn("/ask Write a concise PR summary", DEFAULT_TEMPLATE)
        self.assertIn("/ask Describe user-visible impact", DEFAULT_TEMPLATE)
        self.assertIn("run the code block below", DEFAULT_TEMPLATE)


class TestLoadTemplate(unittest.TestCase):
    def test_load_template_returns_default_when_no_path(self):
        result = load_template()
        self.assertEqual(result, DEFAULT_TEMPLATE)

    def test_load_template_reads_custom_file(self):
        import tempfile
        import os

        content = "# My Custom Template\n\n## Section\n\nContent here.\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = f.name
        try:
            result = load_template(tmp_path)
            self.assertEqual(result, content)
        finally:
            os.unlink(tmp_path)

    def test_load_template_raises_for_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_template("/nonexistent/path/template.md")


class TestRenderTemplate(unittest.TestCase):
    def test_render_prepends_context_block(self):
        result = render_template(
            DEFAULT_TEMPLATE,
            branch="feature/my-branch",
            commits=["abc1234 Add new feature"],
            diff_stat="src/foo.py | 5 +++++",
        )
        self.assertTrue(result.startswith("<!--"))
        self.assertIn("feature/my-branch", result)
        self.assertIn("Add new feature", result)
        self.assertIn("src/foo.py", result)

    def test_render_includes_template_after_context(self):
        result = render_template(
            DEFAULT_TEMPLATE,
            branch="main",
            commits=[],
            diff_stat="",
        )
        self.assertIn("## Summary", result)

    def test_render_shows_no_commits_when_empty(self):
        result = render_template(
            DEFAULT_TEMPLATE,
            branch="main",
            commits=[],
            diff_stat="",
        )
        self.assertIn("(no commits)", result)

    def test_render_shows_no_changes_when_empty_diff(self):
        result = render_template(
            DEFAULT_TEMPLATE,
            branch="main",
            commits=[],
            diff_stat="",
        )
        self.assertIn("(no changes)", result)


class TestStripContext(unittest.TestCase):
    def test_strip_removes_context_block(self):
        body = render_template(
            DEFAULT_TEMPLATE,
            branch="feature/x",
            commits=["abc Fix thing"],
            diff_stat="foo.py | 1 +",
        )
        stripped = strip_context(body)
        self.assertNotIn("<!--", stripped)
        self.assertNotIn("-->", stripped)
        self.assertIn("## Summary", stripped)

    def test_strip_leaves_body_without_context_unchanged(self):
        body = "# No context block here\n\nSome content.\n"
        self.assertEqual(strip_context(body), body)

    def test_strip_roundtrip(self):
        original = DEFAULT_TEMPLATE
        rendered = render_template(original, "branch", ["c1 msg"], "file.py | 1 +")
        recovered = strip_context(rendered)
        self.assertEqual(recovered, original)


if __name__ == "__main__":
    unittest.main()

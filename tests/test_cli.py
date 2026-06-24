"""Tests for aider_gh_cli.cli."""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from aider_gh_cli.cli import cli


class TestCreatePrCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def _patch_git(self, branch="feature/x", commits=None, diff_stat="foo.py | 1 +"):
        if commits is None:
            commits = ["abc1234 Add feature"]
        patches = [
            patch("aider_gh_cli.cli.get_current_branch", return_value=branch),
            patch("aider_gh_cli.cli.get_default_base", return_value="main"),
            patch("aider_gh_cli.cli.get_commits", return_value=commits),
            patch("aider_gh_cli.cli.get_diff_stat", return_value=diff_stat),
        ]
        return patches

    def test_dry_run_prints_title_and_body(self):
        patches = self._patch_git()
        for p in patches:
            p.start()
        try:
            result = self.runner.invoke(
                cli, ["create-pr", "--no-edit", "--dry-run", "--base", "main"]
            )
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("DRY RUN", result.output)
            self.assertIn("Add feature", result.output)
            self.assertIn("## Summary", result.output)
        finally:
            for p in patches:
                p.stop()

    def test_dry_run_uses_provided_title(self):
        patches = self._patch_git()
        for p in patches:
            p.start()
        try:
            result = self.runner.invoke(
                cli,
                ["create-pr", "--no-edit", "--dry-run", "--base", "main", "--title", "Custom Title"],
            )
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Custom Title", result.output)
        finally:
            for p in patches:
                p.stop()

    @patch("aider_gh_cli.cli.gh_available", return_value=True)
    @patch("aider_gh_cli.cli.create_pr", return_value="https://github.com/owner/repo/pull/1")
    def test_creates_pr_successfully(self, mock_create, _mock_gh):
        patches = self._patch_git()
        for p in patches:
            p.start()
        try:
            result = self.runner.invoke(
                cli, ["create-pr", "--no-edit", "--base", "main"]
            )
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("https://github.com/owner/repo/pull/1", result.output)
            mock_create.assert_called_once()
        finally:
            for p in patches:
                p.stop()

    @patch("aider_gh_cli.cli.gh_available", return_value=False)
    def test_exits_when_gh_not_available(self, _mock_gh):
        patches = self._patch_git()
        for p in patches:
            p.start()
        try:
            result = self.runner.invoke(
                cli, ["create-pr", "--no-edit", "--base", "main"]
            )
            self.assertNotEqual(result.exit_code, 0)
        finally:
            for p in patches:
                p.stop()

    @patch("aider_gh_cli.cli.gh_available", return_value=True)
    @patch(
        "aider_gh_cli.cli.create_pr",
        side_effect=subprocess.CalledProcessError(1, "gh", stderr="API error"),
    )
    def test_exits_on_gh_error(self, _mock_create, _mock_gh):
        patches = self._patch_git()
        for p in patches:
            p.start()
        try:
            result = self.runner.invoke(
                cli, ["create-pr", "--no-edit", "--base", "main"]
            )
            self.assertNotEqual(result.exit_code, 0)
        finally:
            for p in patches:
                p.stop()

    def test_version_flag(self):
        result = self.runner.invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("0.1.0", result.output)

    def test_draft_flag_passed_to_create_pr(self):
        patches = self._patch_git()
        for p in patches:
            p.start()
        try:
            with patch("aider_gh_cli.cli.gh_available", return_value=True), patch(
                "aider_gh_cli.cli.create_pr",
                return_value="https://github.com/owner/repo/pull/2",
            ) as mock_create:
                result = self.runner.invoke(
                    cli, ["create-pr", "--no-edit", "--base", "main", "--draft"]
                )
                self.assertEqual(result.exit_code, 0, result.output)
                _args, kwargs = mock_create.call_args
                self.assertTrue(kwargs.get("draft", False))
        finally:
            for p in patches:
                p.stop()

    @patch("aider_gh_cli.cli.subprocess.run")
    @patch("aider_gh_cli.cli.gh_available", return_value=True)
    @patch("aider_gh_cli.cli.create_pr", return_value="https://github.com/owner/repo/pull/3")
    def test_repo_option_sets_target_repository_cwd(
        self, mock_create, _mock_gh, mock_subprocess_run
    ):
        patches = self._patch_git()
        for p in patches:
            p.start()
        try:
            mock_subprocess_run.return_value = MagicMock()
            result = self.runner.invoke(
                cli,
                [
                    "create-pr",
                    "--no-edit",
                    "--base",
                    "main",
                    "--repo",
                    "/tmp",
                ],
            )
            self.assertEqual(result.exit_code, 0, result.output)
            mock_subprocess_run.assert_called_once()
            _args, kwargs = mock_subprocess_run.call_args
            self.assertEqual(kwargs.get("cwd"), "/tmp")
            _args, create_kwargs = mock_create.call_args
            self.assertEqual(create_kwargs.get("cwd"), "/tmp")
        finally:
            for p in patches:
                p.stop()


if __name__ == "__main__":
    unittest.main()

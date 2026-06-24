"""Tests for aider_gh_cli.gh_utils."""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from aider_gh_cli.gh_utils import create_pr, gh_available


class TestGhAvailable(unittest.TestCase):
    @patch("aider_gh_cli.gh_utils.shutil.which")
    def test_returns_true_when_gh_on_path(self, mock_which):
        mock_which.return_value = "/usr/bin/gh"
        self.assertTrue(gh_available())

    @patch("aider_gh_cli.gh_utils.shutil.which")
    def test_returns_false_when_gh_not_on_path(self, mock_which):
        mock_which.return_value = None
        self.assertFalse(gh_available())


class TestCreatePr(unittest.TestCase):
    @patch("aider_gh_cli.gh_utils.gh_available", return_value=True)
    @patch("aider_gh_cli.gh_utils.subprocess.run")
    def test_creates_pr_and_returns_url(self, mock_run, _mock_gh):
        mock_run.return_value = MagicMock(
            stdout="https://github.com/owner/repo/pull/42\n",
            returncode=0,
        )
        url = create_pr("Fix bug", "Body text", base="main")
        self.assertEqual(url, "https://github.com/owner/repo/pull/42")
        args = mock_run.call_args[0][0]
        self.assertIn("gh", args)
        self.assertIn("pr", args)
        self.assertIn("create", args)
        self.assertIn("--title", args)
        self.assertIn("Fix bug", args)
        self.assertIn("--body", args)
        self.assertIn("Body text", args)
        self.assertIn("--base", args)
        self.assertIn("main", args)

    @patch("aider_gh_cli.gh_utils.gh_available", return_value=True)
    @patch("aider_gh_cli.gh_utils.subprocess.run")
    def test_creates_draft_pr(self, mock_run, _mock_gh):
        mock_run.return_value = MagicMock(
            stdout="https://github.com/owner/repo/pull/43\n",
            returncode=0,
        )
        create_pr("Draft PR", "Body", base="main", draft=True)
        args = mock_run.call_args[0][0]
        self.assertIn("--draft", args)

    @patch("aider_gh_cli.gh_utils.gh_available", return_value=False)
    def test_raises_when_gh_not_available(self, _mock_gh):
        with self.assertRaises(FileNotFoundError):
            create_pr("Title", "Body", base="main")

    @patch("aider_gh_cli.gh_utils.gh_available", return_value=True)
    @patch("aider_gh_cli.gh_utils.subprocess.run")
    def test_raises_on_gh_command_failure(self, mock_run, _mock_gh):
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="error")
        with self.assertRaises(subprocess.CalledProcessError):
            create_pr("Title", "Body", base="main")


if __name__ == "__main__":
    unittest.main()

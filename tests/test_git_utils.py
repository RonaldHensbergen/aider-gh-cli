"""Tests for aider_gh_cli.git_utils."""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from aider_gh_cli.git_utils import (
    get_branch_title,
    get_commits,
    get_current_branch,
    get_default_base,
    get_diff_stat,
)


class TestGetCurrentBranch(unittest.TestCase):
    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_returns_branch_name(self, mock_run):
        mock_run.return_value = MagicMock(stdout="feature/my-branch\n", returncode=0)
        result = get_current_branch()
        self.assertEqual(result, "feature/my-branch")
        mock_run.assert_called_once()

    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_raises_on_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")
        with self.assertRaises(subprocess.CalledProcessError):
            get_current_branch()


class TestGetDefaultBase(unittest.TestCase):
    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_returns_main_when_available(self, mock_run):
        mock_run.return_value = MagicMock(stdout="abc123\n", returncode=0)
        result = get_default_base()
        self.assertEqual(result, "main")

    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_falls_back_to_master(self, mock_run):
        def side_effect(args, **kwargs):
            if "main" in args:
                raise subprocess.CalledProcessError(128, "git")
            return MagicMock(stdout="abc123\n", returncode=0)

        mock_run.side_effect = side_effect
        result = get_default_base()
        self.assertEqual(result, "master")

    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_falls_back_to_develop(self, mock_run):
        def side_effect(args, **kwargs):
            if "main" in args or "master" in args:
                raise subprocess.CalledProcessError(128, "git")
            return MagicMock(stdout="abc123\n", returncode=0)

        mock_run.side_effect = side_effect
        result = get_default_base()
        self.assertEqual(result, "develop")

    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_falls_back_to_main_when_none_found(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")
        result = get_default_base()
        self.assertEqual(result, "main")


class TestGetCommits(unittest.TestCase):
    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_returns_list_of_commits(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="abc1234 Fix bug\ndef5678 Add feature\n",
            returncode=0,
        )
        result = get_commits("main")
        self.assertEqual(result, ["abc1234 Fix bug", "def5678 Add feature"])

    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_returns_empty_list_on_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")
        result = get_commits("main")
        self.assertEqual(result, [])

    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_returns_empty_list_when_no_commits(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        result = get_commits("main")
        self.assertEqual(result, [])


class TestGetDiffStat(unittest.TestCase):
    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_returns_diff_stat_string(self, mock_run):
        stat = " src/foo.py | 5 +++++\n 1 file changed, 5 insertions(+)"
        mock_run.return_value = MagicMock(stdout=stat, returncode=0)
        result = get_diff_stat("main")
        self.assertEqual(result, stat.strip())

    @patch("aider_gh_cli.git_utils.subprocess.run")
    def test_returns_empty_string_on_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")
        result = get_diff_stat("main")
        self.assertEqual(result, "")


class TestGetBranchTitle(unittest.TestCase):
    def test_derives_title_from_first_commit(self):
        commits = ["abc1234 Add new feature", "def5678 Fix old bug"]
        self.assertEqual(get_branch_title(commits), "Add new feature")

    def test_returns_empty_string_for_no_commits(self):
        self.assertEqual(get_branch_title([]), "")

    def test_handles_commit_with_no_space(self):
        self.assertEqual(get_branch_title(["abc1234"]), "abc1234")


if __name__ == "__main__":
    unittest.main()

"""GitHub CLI (gh) integration for creating pull requests."""

import shutil
import subprocess


def gh_available():
    """Return True if the ``gh`` executable is found on PATH."""
    return shutil.which("gh") is not None


def create_pr(title, body, base, draft=False, cwd=None):
    """Create a pull request using the ``gh`` CLI.

    Args:
        title: PR title string.
        body: PR body (markdown) string.
        base: Base branch name.
        draft: If True, create the PR as a draft.
        cwd: Repository directory.

    Returns:
        URL of the newly created PR.

    Raises:
        subprocess.CalledProcessError: If ``gh pr create`` fails.
        FileNotFoundError: If ``gh`` is not installed.
    """
    if not gh_available():
        raise FileNotFoundError(
            "The 'gh' CLI is not installed or not on PATH. "
            "Install it from https://cli.github.com/"
        )

    cmd = [
        "gh",
        "pr",
        "create",
        "--title",
        title,
        "--body",
        body,
        "--base",
        base,
    ]
    if draft:
        cmd.append("--draft")

    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

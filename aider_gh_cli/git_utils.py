"""Git utilities for collecting branch changes."""

import subprocess


def _run(args, cwd=None):
    """Run a git command and return its stdout.

    Args:
        args: List of command arguments (including 'git').
        cwd: Working directory for the command.

    Returns:
        Stripped stdout string.

    Raises:
        subprocess.CalledProcessError: If the command exits non-zero.
    """
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_current_branch(cwd=None):
    """Return the name of the current git branch.

    Args:
        cwd: Repository directory.

    Returns:
        Branch name string.
    """
    return _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)


def get_default_base(cwd=None):
    """Detect the default base branch (main, master, or develop).

    Checks remote tracking branches and falls back to 'main'.

    Args:
        cwd: Repository directory.

    Returns:
        Base branch name string.
    """
    for candidate in ("main", "master", "develop"):
        try:
            _run(["git", "rev-parse", "--verify", candidate], cwd=cwd)
            return candidate
        except subprocess.CalledProcessError:
            pass
    return "main"


def get_commits(base, head="HEAD", cwd=None):
    """Return a list of commit subject lines between *base* and *head*.

    Args:
        base: Base branch or ref.
        head: Head ref (default ``HEAD``).
        cwd: Repository directory.

    Returns:
        List of commit subject strings, newest first.
    """
    try:
        output = _run(
            ["git", "log", f"{base}..{head}", "--oneline", "--no-merges"],
            cwd=cwd,
        )
    except subprocess.CalledProcessError:
        return []
    return [line for line in output.splitlines() if line]


def get_diff_stat(base, head="HEAD", cwd=None):
    """Return a diff-stat summary between *base* and *head*.

    Args:
        base: Base branch or ref.
        head: Head ref (default ``HEAD``).
        cwd: Repository directory.

    Returns:
        Diff-stat string.
    """
    try:
        return _run(
            ["git", "diff", "--stat", f"{base}...{head}"],
            cwd=cwd,
        )
    except subprocess.CalledProcessError:
        return ""


def get_branch_title(commits):
    """Derive a PR title from the first commit subject, if available.

    Args:
        commits: List of commit subject strings.

    Returns:
        A title string, or an empty string if *commits* is empty.
    """
    if not commits:
        return ""
    # Strip the short hash prefix produced by --oneline (e.g. "abc1234 Fix bug")
    parts = commits[0].split(" ", 1)
    return parts[1] if len(parts) == 2 else commits[0]

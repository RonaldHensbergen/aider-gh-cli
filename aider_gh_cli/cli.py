"""Command-line interface for aider-gh-cli."""

import os
import subprocess
import sys
import tempfile

import click

from . import __version__
from .gh_utils import create_pr, gh_available
from .git_utils import (
    get_branch_title,
    get_commits,
    get_current_branch,
    get_default_base,
    get_diff_stat,
)
from .template import load_template, render_template, strip_context


@click.group()
@click.version_option(__version__, prog_name="aider-gh-cli")
def cli():
    """aider-gh-cli: collect branch changes and open a GitHub pull request."""


@cli.command("create-pr")
@click.option(
    "--base",
    default=None,
    help="Base branch to compare against (default: auto-detected main/master/develop).",
)
@click.option(
    "--title",
    default=None,
    help="PR title. Defaults to the subject of the most recent commit.",
)
@click.option(
    "--template",
    "template_path",
    default=None,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a custom PR template file.",
)
@click.option(
    "--no-edit",
    is_flag=True,
    default=False,
    help="Skip opening an editor; submit the template as-is.",
)
@click.option(
    "--draft",
    is_flag=True,
    default=False,
    help="Open the pull request as a draft.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print the PR title and body without creating the PR.",
)
@click.pass_context
def create_pr_cmd(ctx, base, title, template_path, no_edit, draft, dry_run):
    """Collect branch changes and create a GitHub pull request.

    Steps:\n
      1. Detect the current branch and its commits vs BASE.\n
      2. Render the PR template with branch context.\n
      3. Open an editor so you can fill in the description (unless --no-edit).\n
      4. Create the PR with ``gh pr create``.\n
    """
    cwd = os.getcwd()

    # Resolve base branch
    if base is None:
        base = get_default_base(cwd=cwd)
        click.echo(f"Using base branch: {base}", err=True)

    # Gather branch information
    branch = get_current_branch(cwd=cwd)
    commits = get_commits(base, cwd=cwd)
    diff_stat = get_diff_stat(base, cwd=cwd)

    # Resolve PR title
    if title is None:
        title = get_branch_title(commits)
        if not title:
            title = branch
    click.echo(f"PR title: {title}", err=True)

    # Load and render template
    template = load_template(template_path)
    body = render_template(template, branch, commits, diff_stat)

    # Open editor unless --no-edit
    if not no_edit:
        body = _open_in_editor(body)

    # Strip the context comment block before submitting
    body = strip_context(body)

    if dry_run:
        click.echo("--- DRY RUN ---")
        click.echo(f"Title: {title}")
        click.echo(f"Base : {base}")
        click.echo(f"Draft: {draft}")
        click.echo("")
        click.echo(body)
        return

    if not gh_available():
        click.echo(
            "Error: 'gh' CLI is not installed. "
            "Install it from https://cli.github.com/",
            err=True,
        )
        sys.exit(1)

    try:
        url = create_pr(title, body, base=base, draft=draft, cwd=cwd)
        click.echo(f"Pull request created: {url}")
    except subprocess.CalledProcessError as exc:
        click.echo(f"Error creating PR:\n{exc.stderr}", err=True)
        sys.exit(1)


def _open_in_editor(content):
    """Write *content* to a temp file, open it in $EDITOR, and return the edited text."""
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or _default_editor()
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".md",
        prefix="aider_gh_pr_",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        subprocess.run([editor, tmp_path], check=True)
        with open(tmp_path, "r", encoding="utf-8") as f:
            return f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _default_editor():
    """Return a sensible default editor ('nano' on most systems, 'notepad' on Windows)."""
    if sys.platform.startswith("win"):
        return "notepad"
    return "nano"


def main():
    """Entry-point for the installed ``aider-gh-cli`` command."""
    cli()

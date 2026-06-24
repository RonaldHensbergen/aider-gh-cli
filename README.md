# aider-gh-cli

CLI tool that collects all changes from a local branch, creates a pull request description following a configurable template, and opens the PR using the `gh` CLI.

## Features

- Automatically detects commits and file changes between your branch and the base branch (`main`, `master`, or `develop`).
- Renders a structured PR description from a built-in default template (or a custom one you supply).
- Opens the draft description in your `$EDITOR` so you can fill it in before the PR is created.
- Creates the PR via `gh pr create` with the correct title, body, and base branch.
- Supports draft PRs and a `--dry-run` mode for previewing without creating anything.

## Requirements

- Python 3.8+
- [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated.

## Installation

```bash
pip install .
```

## Usage

```
aider-gh-cli create-pr [OPTIONS]
```

| Option | Description |
|---|---|
| `--base BRANCH` | Base branch to compare against (default: auto-detected `main`/`master`/`develop`). |
| `--title TEXT` | PR title. Defaults to the subject of the most recent commit. |
| `--template FILE` | Path to a custom Markdown template file. |
| `--no-edit` | Skip opening an editor; submit the template as-is. |
| `--draft` | Open the pull request as a draft. |
| `--dry-run` | Print the PR title and body without actually creating the PR. |

### Examples

```bash
# Auto-detect base branch, open editor to fill in description, then create PR
aider-gh-cli create-pr

# Preview what will be submitted without creating the PR
aider-gh-cli create-pr --dry-run

# Use a custom template and skip the editor
aider-gh-cli create-pr --template .github/pull_request_template.md --no-edit

# Create a draft PR against a specific base branch
aider-gh-cli create-pr --base develop --draft
```

## Default Template

The built-in PR description template looks like this:

```markdown
# Pull Request

## Summary

Describe what changed and why.

## Type Of Change

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor
- [ ] Docs
- [ ] Test only

## User Impact

What should users notice after this change?

## Validation

List commands run and outcomes.

\`\`\`bash
python -m unittest discover -s tests -p "*.py"
\`\`\`

## Checklist

- [ ] Tests added or updated
- [ ] Docs updated (README or docs)
- [ ] No secrets committed
- [ ] Generated artifacts excluded from git
```

## Running Tests

```bash
python -m unittest discover -s tests -p "*.py"
```

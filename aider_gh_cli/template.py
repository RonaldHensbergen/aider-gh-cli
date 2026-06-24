"""PR template management."""

import os

DEFAULT_TEMPLATE = """\
# Pull Request

## Summary

In aider, run:

```text
/ask Write a concise PR summary using the branch context above (what changed and why).
```

Then paste the result here.

## Type Of Change

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor
- [ ] Docs
- [ ] Test only

## User Impact

In aider, run:

```text
/ask Describe user-visible impact, behavior changes, and any migration notes.
```

Then paste the result here.

## Validation

In aider, run the code block below, then summarize the outcome (pass/fail and key output).

```bash
python -m unittest discover -s tests -p "*.py"
```

## Checklist

- [ ] Tests added or updated
- [ ] Docs updated (README or docs)
- [ ] No secrets committed
- [ ] Generated artifacts excluded from git
"""


def load_template(path=None):
    """Load the PR template from a file path, or return the default template.

    Args:
        path: Optional path to a custom template file.

    Returns:
        Template string.

    Raises:
        FileNotFoundError: If a custom path is given but the file does not exist.
    """
    if path is not None:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return DEFAULT_TEMPLATE


def render_template(template, branch, commits, diff_stat):
    """Inject branch context into the template as a header comment.

    The rendered string prepends a fenced context block so that the user
    can see what changed while editing the body, without polluting the
    final PR description.  The context block is stripped before the PR
    is submitted.

    Args:
        template: Template string.
        branch: Current branch name.
        commits: List of commit summary strings.
        diff_stat: Diff-stat string summarising file changes.

    Returns:
        Template string with a context block prepended.
    """
    commit_lines = "\n".join(f"  - {c}" for c in commits) if commits else "  (no commits)"
    context = (
        "<!--\n"
        f"Branch : {branch}\n"
        "\nCommits:\n"
        f"{commit_lines}\n"
        "\nChanged files:\n"
        f"{diff_stat or '  (no changes)'}\n"
        "-->\n\n"
    )
    return context + template


def strip_context(body):
    """Remove the leading context comment block added by render_template.

    Args:
        body: PR body string, possibly starting with a context block.

    Returns:
        Body string with the context comment removed.
    """
    if not body.startswith("<!--"):
        return body
    end = body.find("-->")
    if end == -1:
        return body
    return body[end + 3:].lstrip("\n")

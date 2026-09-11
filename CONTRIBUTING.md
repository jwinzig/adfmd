# Contributing to adfmd

Thanks for your interest in improving this library. This is a small MIT-licensed project; there is no CLA and no formal review process beyond a focused pull request.

## Commit messages

New commits should follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): summary
```

Existing history on `main` is informal English (`add support for media nodes`, `fix linebreaks in table cell content`) and **will not be rewritten**. The convention applies going forward.

### Types

| Type       | Use when you are…                                      |
| ---------- | ------------------------------------------------------ |
| `feat`     | Adding a capability (a new ADF node, CLI flag, etc.)   |
| `fix`      | Fixing a conversion or runtime bug                     |
| `docs`     | Changing documentation only                            |
| `test`     | Adding or adjusting tests without production changes   |
| `refactor` | Restructuring code without changing behavior           |
| `perf`     | Improving performance                                  |
| `build`    | Changing packaging, build backend, or published files  |
| `ci`       | Changing GitHub Actions or other automation            |
| `chore`    | Maintenance that does not fit the types above          |

Append `!` after the type (or `type(scope)!`) for a breaking change, and explain it in the body or a `BREAKING CHANGE:` footer.

### Scopes (optional)

Use a scope when it makes the change easier to scan. Common ones for this repo:

| Scope       | Area                                      |
| ----------- | ----------------------------------------- |
| `adf2md`    | ADF → Markdown conversion                 |
| `md2adf`    | Markdown → ADF conversion                 |
| `cli`       | The `adfmd` command-line entry point      |
| `packaging` | `pyproject.toml`, metadata, distributions |

Leave the scope off when the change is repo-wide (`docs: add contributing guide`).

### Examples

```
feat(adf2md): add support for media nodes
fix(adf2md): preserve linebreaks in table cell content
feat(md2adf): convert headings to ADF heading nodes
docs: document conventional commit style
ci: validate pull request titles
chore(packaging): bump version to 0.2.0
```

Prefer a short, imperative summary (`add`, `fix`, `document`) rather than a sentence.

### Git commit template (optional)

This repository includes a [`.gitmessage`](.gitmessage) you can use as a reminder:

```bash
git config commit.template .gitmessage
```

That setting is local to your clone; it is not required.

## Pull requests

- **PR title** must follow the same Conventional Commits format as commits. CI checks the title on `opened`, `edited`, `reopened`, and `synchronize`.
- Squash-merging with the PR title is a convenient way to land a Conventional Commit on `main` even if the branch has several commits.
- Keep the change set focused. Packaging/CI work and feature work belong in separate PRs when they are not tightly coupled.
- Describe *what* changed and *why*. Mention overlapping files if another open PR is likely to conflict.

## Development

```bash
pip install -e ".[dev]"
pytest
```

The `[dev]` extra installs pytest plus the tools used to build and check the package. `requirements.txt` is a shortcut for the same extra. Python 3.10+ is required; see `pyproject.toml`.

Please add or update fixtures under `test/data/` when you change conversion behavior.

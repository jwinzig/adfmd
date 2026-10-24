# adfmd

[![CI](https://github.com/jwinzig/adfmd/actions/workflows/ci.yml/badge.svg)](https://github.com/jwinzig/adfmd/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/jwinzig/adfmd?include_prereleases)](https://github.com/jwinzig/adfmd/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/jwinzig/adfmd)](LICENSE)

`adfmd` is a Python library and command-line tool for bidirectional conversion
between [Atlassian Document Format (ADF)][adf] and [Markdown][markdown]. It
converts common Markdown structures directly and uses HTML comments to preserve
ADF-specific metadata for round trips.

## Dependencies

- Python 3.10 or newer
- No third-party runtime dependencies

## Getting started

Install the library and CLI from a checkout:

```bash
pip install .
```

### Command line

Convert an ADF JSON document to Markdown:

```bash
adfmd input.json
adfmd input.json -o output.md
```

Convert Markdown to ADF JSON:

```bash
adfmd --type md2adf input.md
adfmd --type md2adf input.md -o output.json
```

Run `adfmd --help` for all options.

### Python

```python
from adfmd import from_markdown, to_markdown

adf = from_markdown("# Hello\n\nThis is **ADF**.")
markdown = to_markdown(adf)
```

For file-based conversion or custom converter registries, use the `ADFMD`
class:

```python
from adfmd import ADFMD

converter = ADFMD()
converter.to_markdown_file("input.json", "output.md")
converter.from_markdown_file("input.md", "output.json")
```

## Documentation

- [Supported nodes and marks](docs/supported-nodes/README.md) lists conversion
  behavior, round-trip metadata, and examples for ADF-specific content.
- [Contributing guide](CONTRIBUTING.md) explains how to submit changes and the
  commit conventions used by the project.

## Development

```bash
pip install -e ".[dev]"
pytest
```

The `dev` extra installs the test, build, and package-checking tools.

## References

- [Atlassian Document Format][adf]
- [Markdown syntax][markdown]

[adf]: https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
[markdown]: https://daringfireball.net/projects/markdown/syntax

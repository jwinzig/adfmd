# adfmd

`adfmd` is a Python library and command-line tool for bidirectional conversion
between [Atlassian Document Format (ADF)][adf] and [Markdown][markdown]. It
converts common Markdown structures directly and uses HTML comments to preserve
ADF-specific metadata for round trips.

Requires Python 3.10 or newer and has no third-party runtime dependencies.

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

## References

- [Atlassian Document Format][adf]
- [Markdown basic syntax][markdown]

## Development

```bash
pip install -e ".[dev]"
pytest
```

The `dev` extra installs the test, build, and package-checking tools.

[adf]: https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
[markdown]: https://www.markdownguide.org/basic-syntax/

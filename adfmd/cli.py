#!/usr/bin/env python3
"""
Command-line interface for adfmd - Convert ADF to Markdown.
"""

import argparse
import sys
from pathlib import Path

from adfmd import ADFMD


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Atlassian Document Format (ADF) JSON to Markdown"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to input ADF JSON file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to output Markdown file (default: stdout)",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        converter = ADFMD()
        if args.output:
            converter.to_markdown_file(input_path, args.output)
            print(f"Converted {input_path} to {args.output}", file=sys.stderr)
        else:
            markdown = converter.to_markdown_file(input_path)
            print(markdown)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


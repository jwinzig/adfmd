#!/usr/bin/env python3
"""
Command-line interface for adfmd - Convert between ADF and Markdown.
"""

import argparse
import sys
from pathlib import Path
import json
from adfmd import ADFMD


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert between Atlassian Document Format (ADF) JSON and Markdown"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to input file (ADF JSON or Markdown)",
    )
    parser.add_argument(
        "--type",
        "-t",
        type=str,
        help="Type of conversion: adf2md or md2adf",
        choices=["adf2md", "md2adf"],
        default="adf2md",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to output file (default: stdout)",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    converter = ADFMD()
    if args.type == "adf2md":
        result = converter.to_markdown_file(input_path, args.output)
    else:
        result = converter.from_markdown_file(input_path, args.output)


if __name__ == "__main__":
    main()

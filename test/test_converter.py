#!/usr/bin/env python3
"""
Pytest tests for adfmd - ADF to Markdown conversion.
"""

import sys
from pathlib import Path

# Add parent directory to path to import adfmd
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from adfmd import ADFMD


@pytest.mark.parametrize(
    "test_name",
    [
        "text_simple",
        "text_marks",

        "paragraph_simple",
        "paragraph_nested",
        "paragraph_complex",

        "bullet_list_simple",
        "bullet_list_nested",
        "bullet_list_complex",

        "ordered_list_simple",
        "ordered_list_nested",
        "ordered_list_complex",

        "heading_simple",
        "heading_marks",
        "heading_marks_complex",
        "heading_levels",

        "hard_break_simple",

        "link_simple",
        "link_complex",

        "inline_card_simple",
        "inline_card_complex",

        "rule_simple",
        "rule_with_content",

        "date_simple",
        "date_complex",
    ],
)
def test_adf_to_md(test_name):
    """Test ADF to Markdown conversion for a given test case using adfmd."""
    test_dir = Path(__file__).parent / "data"
    input_file = test_dir / f"{test_name}.json"
    expected_file = test_dir / f"{test_name}.md"

    # Check that test files exist
    assert input_file.exists(), f"Input file not found: {input_file}"
    assert expected_file.exists(), f"Expected file not found: {expected_file}"

    # Convert ADF to Markdown using adfmd
    converter = ADFMD()
    result = converter.convert_adf2md_file(str(input_file))

    # Read expected output
    with open(expected_file, "r", encoding="utf-8") as f:
        expected = f.read().rstrip()

    # Normalize line endings and compare
    result = result.rstrip()
    expected = expected.rstrip()

    assert result == expected, (
        f"Conversion mismatch for {test_name}:\n"
        f"Expected:\n{repr(expected)}\n"
        f"Got:\n{repr(result)}"
    )

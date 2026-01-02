#!/usr/bin/env python3
"""
Pytest tests for adfmd - ADF to Markdown conversion.
"""

import sys
from pathlib import Path

# Add parent directory to path to import adfmd
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import json
from adfmd import ADFMD, to_markdown


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
        "doc_simple",
        "doc_no_version",
        "doc_complex",
        "status_simple",
        "status_complex",
        "mention_simple",
        "mention_complex",
        "table_simple",
        "table_complex",
        "table_multiple_col_row_span",
        "table_nested_single",
        "table_nested",
        "blockquote_simple",
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
    result = converter.to_markdown_file(input_file)

    # Read expected output
    expected = expected_file.read_text(encoding="utf-8").rstrip()

    # Normalize line endings and compare
    result = result.rstrip()
    expected = expected.rstrip()
    assert result == expected, (
        f"Conversion mismatch for {test_name}:\nExpected:\n{repr(expected)}\nGot:\n{repr(result)}"
    )

    # Convert ADF to Markdown using to_markdown function
    result2 = to_markdown(json.loads(input_file.read_text(encoding="utf-8")))
    assert result == result2.rstrip(), "Conversion mismatch for to_markdown function"

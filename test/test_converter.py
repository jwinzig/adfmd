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
from adfmd import ADFMD, to_markdown, from_markdown
from adfmd.converter.md2adf import _order_node


TEST_CASES = [
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
    "code_block_simple",
    "emoji_simple",
    "panel_simple",
    "panel_complex",
    "media_single",
    "media_group",
    "media_inline",
    "expand",
    "nested_expand",
]


@pytest.mark.parametrize("test_name", TEST_CASES)
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


def _is_empty_paragraph(node):
    if not isinstance(node, dict) or node.get("type") != "paragraph":
        return False
    content = node.get("content")
    if not content:
        return True
    return all(isinstance(item, dict) and item.get("type") == "hardBreak" for item in content)


def _strip_local_ids_only(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, val in value.items():
            if key == "localId":
                continue
            if key == "adf" and isinstance(val, str):
                try:
                    cleaned_adf = _strip_local_ids_only(json.loads(val))
                    cleaned[key] = json.dumps(_order_node(cleaned_adf))
                    continue
                except json.JSONDecodeError:
                    pass
            cleaned[key] = _strip_local_ids_only(val)
        return cleaned
    if isinstance(value, list):
        return [_strip_local_ids_only(item) for item in value]
    return value


def _normalize_nested_tables(value):
    cleaned = _strip_local_ids_only(value)

    def normalize(item):
        if isinstance(item, dict):
            normalized = {}
            for key, val in item.items():
                if key == "adf" and isinstance(val, str):
                    try:
                        normalized[key] = json.dumps(normalize(json.loads(val)))
                        continue
                    except json.JSONDecodeError:
                        pass
                if key == "cxhtml":
                    continue
                normalized_val = normalize(val)
                if key == "attrs" and normalized_val == {}:
                    continue
                if key == "marks" and normalized_val == []:
                    continue
                normalized[key] = normalized_val
            return normalized
        if isinstance(item, list):
            normalized_items = []
            for entry in item:
                normalized_entry = normalize(entry)
                if _is_empty_paragraph(normalized_entry):
                    continue
                normalized_items.append(normalized_entry)
            return normalized_items
        return item

    return normalize(cleaned)


@pytest.mark.parametrize("test_name", TEST_CASES)
def test_md_to_adf(test_name):
    """Test Markdown to ADF conversion for a given test case using adfmd."""
    test_dir = Path(__file__).parent / "data"
    input_file = test_dir / f"{test_name}.md"
    expected_file = test_dir / f"{test_name}.json"

    # Check that test files exist
    assert input_file.exists(), f"Input file not found: {input_file}"
    assert expected_file.exists(), f"Expected file not found: {expected_file}"

    # Convert Markdown to ADF using adfmd
    converter = ADFMD()
    result = converter.from_markdown_file(input_file)

    # Read expected output
    expected = json.loads(expected_file.read_text(encoding="utf-8"))

    # Strip local ids for nested table tests.
    if test_name in ["table_nested", "table_nested_single"]:
        result = _normalize_nested_tables(result)
        expected = _normalize_nested_tables(expected)

    if isinstance(expected, list) and isinstance(result, dict):
        result = [result]
    assert result == expected, (
        f"Conversion mismatch for {test_name}:\nExpected:\n{repr(expected)}\nGot:\n{repr(result)}"
    )

    # Convert Markdown to ADF using from_markdown function
    result2 = from_markdown(input_file.read_text(encoding="utf-8"))

    # Strip local ids for nested table tests.
    if test_name in ["table_nested", "table_nested_single"]:
        result2 = _normalize_nested_tables(result2)

    if isinstance(expected, list) and isinstance(result2, dict):
        result2 = [result2]
    assert result2 == expected, "Conversion mismatch for from_markdown function"

    # Compare the result and expected as strings (incl. keys order), except for nested table tests.
    if test_name not in ["table_nested", "table_nested_single"]:
        result_str = json.dumps(result2, indent=2)
        expected_str = json.dumps(expected, indent=2)
        assert result_str == expected_str, (
            f"Conversion mismatch for {test_name}:\nExpected:\n{repr(expected_str)}\nGot:\n{repr(result_str)}"
        )

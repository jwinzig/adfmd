"""
adfmd - Convert between Atlassian Document Format (ADF) and Markdown.
"""

import json
from typing import Any, Dict, List, Optional, Union

from adfmd.converter import ADF2MDRegistry
from adfmd.nodes import ADFNode


class ADFMD:
    """Main class for adfmd - convert between ADF and Markdown."""

    def __init__(
        self,
        registry_adf2md: Optional[ADF2MDRegistry] = None,
    ):
        """
        Initialize adfmd.

        Args:
            registry_adf2md: Optional ADF to Markdown registry. If None, uses default.
            registry_md2adf: Optional Markdown to ADF registry. If None, uses default.
        """
        self.registry_adf2md = registry_adf2md or ADF2MDRegistry.create_default()

    def convert_adf2md(self, adf_json: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """
        Convert ADF JSON to Markdown string.

        Args:
            adf_json: ADF document as a dictionary or list of dictionaries

        Returns:
            Markdown string representation

        Raises:
            ValueError: If the document type is not supported
        """
        # Build internal node representation
        if isinstance(adf_json, list):
            nodes = [ADFNode.from_dict(node_dict) for node_dict in adf_json]
        else:
            nodes = [ADFNode.from_dict(adf_json)]

        # Convert nodes to markdown
        markdown_parts = [self.registry_adf2md.convert(node) for node in nodes]

        # Join markdown parts. Newlines are added by the converters. Remove trailing newlines.
        return "".join(markdown_parts).rstrip("\n")

    def convert_adf2md_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert an ADF JSON file to Markdown.

        Args:
            input_path: Path to input ADF JSON file
            output_path: Optional path to output Markdown file. If None, returns the result.

        Returns:
            Markdown string representation
        """
        with open(input_path, "r", encoding="utf-8") as f:
            adf_data = json.load(f)

        markdown = self.convert_adf2md(adf_data)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown)

        return markdown

"""
adfmd - Convert between Atlassian Document Format (ADF) and Markdown.
"""

import json
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from adfmd.converter import ADF2MDRegistry, MD2ADFRegistry
from adfmd.nodes import ADFNode


class ADFMD:
    """Main class for adfmd - convert between ADF and Markdown."""

    def __init__(
        self,
        registry_adf2md: Optional[ADF2MDRegistry] = None,
        registry_md2adf: Optional[MD2ADFRegistry] = None,
    ):
        """
        Initialize adfmd.

        Args:
            registry_adf2md: Optional ADF to Markdown registry. If None, uses default.
            registry_md2adf: Optional Markdown to ADF registry. If None, uses default.
        """
        self.registry_adf2md = registry_adf2md or ADF2MDRegistry.create_default()
        self.registry_md2adf = registry_md2adf or MD2ADFRegistry.create_default()

    def to_markdown(self, adf_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """
        Convert ADF JSON to Markdown string.

        Args:
            adf_data: ADF document as a dictionary or list of dictionaries

        Returns:
            Markdown string representation

        Raises:
            ValueError: If the document type is not supported
        """
        if isinstance(adf_data, list):
            nodes = [ADFNode.from_dict(node_dict) for node_dict in adf_data]
        else:
            nodes = [ADFNode.from_dict(adf_data)]

        shared_kwargs = {"nested_table_counter": {"count": 0}}
        markdown_parts = [self.registry_adf2md.convert(node, **shared_kwargs) for node in nodes]
        return "".join(markdown_parts).rstrip("\n")

    def to_markdown_file(
        self, input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """
        Convert an ADF JSON file to Markdown.

        Args:
            input_path: Path to input ADF JSON file (str or Path)
            output_path: Optional path to output Markdown file (str or Path). If None, returns the result.

        Returns:
            Markdown string representation
        """
        input_path = Path(input_path)
        with input_path.open("r", encoding="utf-8") as f:
            adf_data = json.load(f)

        markdown = self.to_markdown(adf_data)

        if output_path:
            output_path = Path(output_path)
            output_path.write_text(markdown, encoding="utf-8")

        return markdown

    def from_markdown(self, markdown: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Convert Markdown string to ADF JSON.

        Args:
            markdown: Markdown string to convert

        Returns:
            ADF document as a dictionary or list of dictionaries
        """
        return self.registry_md2adf.convert(markdown)

    def from_markdown_file(
        self, input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Convert a Markdown file to ADF JSON.

        Args:
            input_path: Path to input Markdown file (str or Path)
            output_path: Optional path to output JSON file (str or Path). If None, returns the result.

        Returns:
            ADF document as a dictionary or list of dictionaries
        """
        input_path = Path(input_path)
        markdown = input_path.read_text(encoding="utf-8")
        adf_data = self.from_markdown(markdown)

        if output_path:
            output_path = Path(output_path)
            output_path.write_text(json.dumps(adf_data, indent=2), encoding="utf-8")

        return adf_data

    ################################################################################################
    # Deprecated methods for backward compatibility
    # Will be removed in the next release.
    ################################################################################################
    def convert_adf2md(self, adf_json: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        warnings.warn(
            "convert_adf2md() is deprecated. Use to_markdown() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.to_markdown(adf_json)

    def convert_adf2md_file(
        self, input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None
    ) -> str:
        warnings.warn(
            "convert_adf2md_file() is deprecated. Use to_markdown_file() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.to_markdown_file(input_path, output_path)

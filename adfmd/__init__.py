"""
adfmd - Convert between Atlassian Document Format (ADF) and Markdown.
"""

from typing import Any, Dict, List, Optional, Union

from adfmd.adfmd import ADFMD
from adfmd.converter import ADF2MDRegistry

__all__ = ["ADFMD", "to_markdown", "from_markdown"]
__version__ = "0.1.0"


def to_markdown(
    adf_data: Union[Dict[str, Any], List[Dict[str, Any]]],
) -> str:
    """
    Convert ADF JSON to Markdown string.

    Convenience function for simple conversions. For advanced usage with
    custom registries or multiple conversions, use the ADFMD class directly.

    Args:
        adf_data: ADF document as a dictionary or list of dictionaries

    Returns:
        Markdown string representation

    Example:
        >>> import adfmd
        >>> adf = {"type": "paragraph", "content": [...]}
        >>> markdown = adfmd.to_markdown(adf)
    """
    return ADFMD().to_markdown(adf_data)


def from_markdown(
    markdown: str,
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Convert Markdown string to ADF JSON.

    Convenience function for simple conversions. For advanced usage with
    custom registries or multiple conversions, use the ADFMD class directly.

    Args:
        markdown: Markdown string to convert

    Returns:
        ADF document as a dictionary or list of dictionaries

    Example:
        >>> import adfmd
        >>> adf = adfmd.from_markdown("# Hello World")
    """
    return ADFMD().from_markdown(markdown)

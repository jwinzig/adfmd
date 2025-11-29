"""
ADF to Markdown converters for adfmd.
Contains base class, registry, and all converters for converting ADF nodes to Markdown format.
"""

from typing import Dict, Optional, Any

from abc import ABC, abstractmethod

from adfmd.nodes import (
    ADFNode,
    BulletListNode,
    ListItemNode,
    ParagraphNode,
    OrderedListNode,
    HardBreakNode,
    HeadingNode,
    TextNode,
)


class ADF2MDBaseConverter(ABC):
    """Base class for ADF to Markdown converters."""

    def __init__(self, registry: Optional["ADF2MDRegistry"] = None):
        """
        Initialize the converter.

        Args:
            registry: Optional registry to use for converting child nodes.
                     If None, converters must handle child nodes themselves.
        """
        self.registry = registry

    @abstractmethod
    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """
        Convert a node to Markdown. To be implemented by subclasses.

        Args:
            node: The ADF node dataclass instance
            **kwargs: Additional arguments for special cases (indent_level defaults to 0)

        Returns:
            Markdown string representation
        """
        pass

    def _convert_child(self, node: ADFNode, **kwargs: Any) -> str:
        """
        Convert a child node using the registry.

        This method performs input validation and delegates to the appropriate converter.

        Args:
            node: The ADF node dataclass instance
            **kwargs: Additional arguments to pass to converters for special cases (indent_level defaults to 0)

        Returns:
            Markdown string representation

        Raises:
            ValueError: If no registry is available or node type is not supported
        """
        if not self.registry:
            raise ValueError("Registry is required to convert child nodes")

        converter = self.registry.get_converter(node.type)
        if not converter:
            raise ValueError(f"Unsupported node type: {node.type}")

        return converter.convert(node, **kwargs)


class ADF2MDRegistry:
    """Registry for managing ADF to Markdown converters."""

    def __init__(self):
        """Initialize an empty registry."""
        self.converters: Dict[str, ADF2MDBaseConverter] = {}

    def register(self, node_type: str, converter: ADF2MDBaseConverter):
        """
        Register a converter for a node type.

        Args:
            node_type: The ADF node type (e.g., "bulletList", "paragraph")
            converter: Converter instance to register
        """
        # Set the registry on the converter so it can convert child nodes
        converter.registry = self
        self.converters[node_type] = converter

    def get_converter(self, node_type: str) -> Optional[ADF2MDBaseConverter]:
        """
        Get a converter for a node type.

        Args:
            node_type: The ADF node type

        Returns:
            Converter instance or None if not found
        """
        return self.converters.get(node_type)

    def has_converter(self, node_type: str) -> bool:
        """
        Check if a converter exists for a node type.

        Args:
            node_type: The ADF node type

        Returns:
            True if converter exists, False otherwise
        """
        return node_type in self.converters

    def convert(self, node: ADFNode) -> str:
        """
        Convert an ADF node to Markdown using the appropriate converter.

        Args:
            node: The ADF node dataclass instance

        Returns:
            Markdown string representation

        Raises:
            ValueError: If no converter is available for the node type
        """
        if not self.has_converter(node.type):
            raise ValueError(f"Unsupported node type: {node.type}")

        converter = self.get_converter(node.type)
        return converter.convert(node)

    @classmethod
    def create_default(cls) -> "ADF2MDRegistry":
        """
        Create a registry with all ADF to Markdown converters.

        Returns:
            ADF2MDRegistry instance with all converters registered
        """

        registry = cls()

        # Register converters
        registry.register("text", TextConverter())
        registry.register("paragraph", ParagraphConverter())
        registry.register("heading", HeadingConverter())
        registry.register("bulletList", BulletListConverter())
        registry.register("orderedList", OrderedListConverter())
        registry.register("hardBreak", HardBreakConverter())

        return registry


class TextConverter(ADF2MDBaseConverter):
    """Converter for text nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a text node to its string representation with markdown annotations."""
        if not isinstance(node, TextNode):
            raise ValueError(f"Expected TextNode, got {type(node)}")

        text = node.text
        marks = node.marks

        # Map ADF mark types to markdown formatting
        mark_formatters = {
            "code": lambda t: f"`{t}`",
            "em": lambda t: f"*{t}*",
            "strong": lambda t: f"**{t}**",
            "strike": lambda t: f"~~{t}~~",
            "underline": lambda t: t,  # Underline not supported in standard markdown
        }

        # Apply marks in order
        mark_order = ["code", "em", "strong", "strike", "underline"]
        for mark_type in mark_order:
            if mark_type in marks:
                formatter = mark_formatters.get(mark_type)
                if formatter:
                    text = formatter(text)

        return text


class ParagraphConverter(ADF2MDBaseConverter):
    """Converter for paragraph nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a paragraph node to Markdown."""
        if not isinstance(node, ParagraphNode):
            raise ValueError(f"Expected ParagraphNode, got {type(node)}")

        no_newlines = kwargs.get("no_newlines", False)
        text_parts = []
        for child_node in node.children:
            text_parts.append(self._convert_child(child_node))

        text = "".join(text_parts)
        text += "\n\n" if not no_newlines else ""
        return text


class HeadingConverter(ADF2MDBaseConverter):
    """Converter for heading nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a heading node to Markdown."""
        if not isinstance(node, HeadingNode):
            raise ValueError(f"Expected HeadingNode, got {type(node)}")

        # Convert children to text
        text_parts = []
        for child_node in node.children:
            text_parts.append(self._convert_child(child_node))

        heading_text = "".join(text_parts)

        # Create markdown heading with appropriate number of # symbols
        level = node.level
        if level < 1:
            level = 1
        elif level > 6:
            level = 6

        return f"{'#' * level} {heading_text}" + "\n\n"


class BulletListConverter(ADF2MDBaseConverter):
    """Converter for bullet list nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a bullet list node to Markdown."""
        if not isinstance(node, BulletListNode):
            raise ValueError(f"Expected BulletListNode, got {type(node)}")

        indent_level = kwargs.get("indent_level", 0)
        lines = []
        indent = "  " * indent_level

        for list_item in node.children:
            if not isinstance(list_item, ListItemNode):
                continue

            # Process the list item content
            item_text = ""
            nested_list = None

            for child_node in list_item.children:
                if isinstance(child_node, ParagraphNode):
                    item_text = self._convert_child(child_node, no_newlines=True)
                elif isinstance(child_node, BulletListNode):
                    nested_list = child_node

            # Add the main list item
            if item_text:
                lines.append(f"{indent}- {item_text}")

            # Add nested list if present
            if nested_list:
                nested_lines = self.convert(nested_list, indent_level=indent_level + 1)
                if nested_lines:
                    lines.append(nested_lines)

        return "\n".join(lines)


class OrderedListConverter(ADF2MDBaseConverter):
    """Converter for ordered list nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert an ordered list node to Markdown."""
        if not isinstance(node, OrderedListNode):
            raise ValueError(f"Expected OrderedListNode, got {type(node)}")

        indent_level = kwargs.get("indent_level", 0)
        lines = []
        indent = "  " * indent_level
        item_number = 1

        for list_item in node.children:
            if not isinstance(list_item, ListItemNode):
                continue

            # Process the list item content
            item_text = ""
            nested_list = None

            for child_node in list_item.children:
                if isinstance(child_node, ParagraphNode):
                    item_text = self._convert_child(child_node, no_newlines=True)
                elif isinstance(child_node, (OrderedListNode, BulletListNode)):
                    nested_list = child_node

            # Add the main list item
            if item_text:
                lines.append(f"{indent}{item_number}. {item_text}")
                item_number += 1

            # Add nested list if present
            if nested_list:
                nested_lines = self._convert_child(nested_list, indent_level=indent_level + 1)
                if nested_lines:
                    lines.append(nested_lines)

        return "\n".join(lines)


class HardBreakConverter(ADF2MDBaseConverter):
    """Converter for hard break nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a hard break node to Markdown."""
        if not isinstance(node, HardBreakNode):
            raise ValueError(f"Expected HardBreakNode, got {type(node)}")

        # In Markdown, a hard break within a paragraph is represented as two spaces
        # followed by a newline. This creates a line break without starting a new paragraph.
        return "  \n"

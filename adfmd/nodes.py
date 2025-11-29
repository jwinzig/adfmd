"""
ADF node dataclasses for adfmd.
Provides type-safe internal representation of ADF nodes.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ADFNode:
    """Base class for all ADF nodes."""

    type: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ADFNode":
        """
        Create an ADF node from a dictionary.

        Args:
            data: Dictionary containing node data

        Returns:
            Appropriate ADF node instance

        Raises:
            ValueError: If node type is not supported
        """
        node_type = data.get("type")
        if node_type == "text":
            return TextNode.from_dict(data)
        elif node_type == "paragraph":
            return ParagraphNode.from_dict(data)
        elif node_type == "bulletList":
            return BulletListNode.from_dict(data)
        elif node_type == "orderedList":
            return OrderedListNode.from_dict(data)
        elif node_type == "listItem":
            return ListItemNode.from_dict(data)
        else:
            raise ValueError(f"Unsupported node type: {node_type}")


@dataclass
class TextNode(ADFNode):
    """Represents a text node in ADF."""

    type: str = field(default="text", init=False)
    text: str
    marks: List[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextNode":
        """Create a TextNode from a dictionary."""
        return cls(text=data.get("text", ""), marks=[m["type"] for m in data.get("marks", [])])


@dataclass
class ParagraphNode(ADFNode):
    """Represents a paragraph node in ADF."""

    type: str = field(default="paragraph", init=False)
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParagraphNode":
        """Create a ParagraphNode from a dictionary."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(children=children)


@dataclass
class BulletListNode(ADFNode):
    """Represents a bullet list node in ADF."""

    type: str = field(default="bulletList", init=False)
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BulletListNode":
        """Create a BulletListNode from a dictionary, preserving all child nodes."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(children=children)


@dataclass
class OrderedListNode(ADFNode):
    """Represents an ordered list node in ADF."""

    type: str = field(default="orderedList", init=False)
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderedListNode":
        """Create an OrderedListNode from a dictionary, preserving all child nodes."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(children=children)


@dataclass
class ListItemNode(ADFNode):
    """Represents a list item node in ADF."""

    type: str = field(default="listItem", init=False)
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ListItemNode":
        """Create a ListItemNode from a dictionary, preserving all child nodes."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(children=children)

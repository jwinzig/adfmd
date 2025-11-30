"""
ADF node dataclasses for adfmd.
Provides type-safe internal representation of ADF nodes.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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
        elif node_type == "heading":
            return HeadingNode.from_dict(data)
        elif node_type == "hardBreak":
            return HardBreakNode.from_dict(data)
        elif node_type == "inlineCard":
            return InlineCardNode.from_dict(data)
        elif node_type == "rule":
            return RuleNode.from_dict(data)
        else:
            raise ValueError(f"Unsupported node type: {node_type}")


@dataclass
class TextNode(ADFNode):
    """Represents a text node in ADF."""

    type: str = field(default="text", init=False)
    text: str
    marks: List[str]
    url: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextNode":
        """Create a TextNode from a dictionary."""
        # Get text marks (excluding link)
        marks = [mark.get("type") for mark in data.get("marks", []) if mark.get("type") != "link"]

        # Get URL from link mark
        url = None
        for mark in data.get("marks", []):
            if mark.get("type") == "link":
                url = mark.get("attrs", {}).get("href", None)
                break

        return cls(text=data.get("text", ""), marks=marks, url=url)


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
class HeadingNode(ADFNode):
    """Represents a heading node in ADF."""

    type: str = field(default="heading", init=False)
    level: int = field(default=int)
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HeadingNode":
        """Create a HeadingNode from a dictionary, preserving all child nodes."""
        level = data.get("attrs", {}).get("level", None)
        if level is None:
            raise ValueError("Level is required for heading nodes")

        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(level=level, children=children)


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


@dataclass
class HardBreakNode(ADFNode):
    """Represents a hard break node in ADF."""

    type: str = field(default="hardBreak", init=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HardBreakNode":
        """Create a HardBreakNode from a dictionary."""
        return cls()


@dataclass
class InlineCardNode(ADFNode):
    """Represents an inlineCard node in ADF."""

    type: str = field(default="inlineCard", init=False)
    url: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InlineCardNode":
        """Create an InlineCardNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        # inlineCard can have url in attrs.url or attrs.data.url
        url = attrs.get("url") or (attrs.get("data", {}) or {}).get("url", "")
        if not url:
            raise ValueError("URL is required for inlineCard nodes")

        return cls(url=url)


@dataclass
class RuleNode(ADFNode):
    """Represents a rule (horizontal rule) node in ADF."""

    type: str = field(default="rule", init=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuleNode":
        """Create a RuleNode from a dictionary."""
        return cls()

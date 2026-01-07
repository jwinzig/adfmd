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
        elif node_type == "date":
            return DateNode.from_dict(data)
        elif node_type == "doc":
            return DocNode.from_dict(data)
        elif node_type == "status":
            return StatusNode.from_dict(data)
        elif node_type == "mention":
            return MentionNode.from_dict(data)
        elif node_type == "table":
            return TableNode.from_dict(data)
        elif node_type == "tableRow":
            return TableRowNode.from_dict(data)
        elif node_type == "tableCell":
            return TableCellNode.from_dict(data)
        elif node_type == "tableHeader":
            return TableHeaderNode.from_dict(data)
        elif node_type == "extension":
            return ExtensionNode.from_dict(data)
        elif node_type == "blockquote":
            return BlockquoteNode.from_dict(data)
        elif node_type == "codeBlock":
            return CodeBlockNode.from_dict(data)
        elif node_type == "emoji":
            return EmojiNode.from_dict(data)
        elif node_type == "panel":
            return PanelNode.from_dict(data)
        elif node_type == "mediaSingle":
            return MediaSingleNode.from_dict(data)
        elif node_type == "mediaGroup":
            return MediaGroupNode.from_dict(data)
        elif node_type == "media":
            return MediaNode.from_dict(data)
        elif node_type == "mediaInline":
            return MediaInlineNode.from_dict(data)
        elif node_type == "caption":
            return CaptionNode.from_dict(data)
        else:
            raise ValueError(f"Unsupported node type: {node_type}")


@dataclass
class TextNode(ADFNode):
    """Represents a text node in ADF."""

    type: str = field(default="text", init=False)
    text: str
    marks: List[str]
    url: Optional[str]
    background_color: Optional[str]
    text_color: Optional[str]
    subsup: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextNode":
        """Create a TextNode from a dictionary."""
        # Get text marks (excluding link)
        marks = [mark.get("type") for mark in data.get("marks", []) if mark.get("type") != "link"]

        # Get specific attributes from marks
        url = None
        subsup = None
        background_color = None
        text_color = None
        for mark in data.get("marks", []):
            if mark.get("type") == "link":
                url = mark.get("attrs", {}).get("href", None)
            elif mark.get("type") == "subsup":
                subsup = mark.get("attrs", {}).get("type", None)
            elif mark.get("type") == "textColor":
                text_color = mark.get("attrs", {}).get("color", None)
            elif mark.get("type") == "backgroundColor":
                background_color = mark.get("attrs", {}).get("color", None)

        return cls(
            text=data.get("text", ""),
            marks=marks,
            url=url,
            subsup=subsup,
            background_color=background_color,
            text_color=text_color,
        )


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
class BlockquoteNode(ADFNode):
    """Represents a blockquote node in ADF."""

    type: str = field(default="blockquote", init=False)
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockquoteNode":
        """Create a BlockquoteNode from a dictionary."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(children=children)


@dataclass
class CodeBlockNode(ADFNode):
    """Represents a codeBlock node in ADF."""

    type: str = field(default="codeBlock", init=False)
    language: Optional[str] = None
    text: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeBlockNode":
        """Create a CodeBlockNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        language = attrs.get("language")

        # codeBlock nodes contain one or more plain text nodes without marks
        text_parts: List[str] = []
        for item in data.get("content", []):
            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        text: str = "\n".join(text_parts)

        return cls(language=language, text=text)


@dataclass
class EmojiNode(ADFNode):
    """Represents an emoji node in ADF."""

    type: str = field(default="emoji", init=False)
    short_name: Optional[str] = None
    id: Optional[str] = None
    text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmojiNode":
        """Create an EmojiNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        short_name = attrs.get("shortName")
        id = attrs.get("id")
        text = attrs.get("text")

        return cls(short_name=short_name, id=id, text=text)


@dataclass
class PanelNode(ADFNode):
    """Represents a panel node in ADF."""

    type: str = field(default="panel", init=False)
    panel_type: Optional[str] = None
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PanelNode":
        """Create a PanelNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        panel_type = attrs.get("panelType")

        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))

        return cls(panel_type=panel_type, children=children)


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


@dataclass
class DateNode(ADFNode):
    """Represents a date node in ADF."""

    type: str = field(default="date", init=False)
    timestamp: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DateNode":
        """Create a DateNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        # Timestamp is a string of milliseconds since epoch
        timestamp = data.get("attrs", {}).get("timestamp")
        if timestamp is None:
            raise ValueError("Timestamp is required for date nodes")

        return cls(timestamp=timestamp)


@dataclass
class DocNode(ADFNode):
    """Represents a doc (document root) node in ADF."""

    type: str = field(default="doc", init=False)
    version: Optional[int] = None
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocNode":
        """Create a DocNode from a dictionary."""
        version = data.get("version")
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(version=version, children=children)


@dataclass
class StatusNode(ADFNode):
    """Represents a status node in ADF."""

    type: str = field(default="status", init=False)
    text: str
    color: Optional[str] = None
    local_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusNode":
        """Create a StatusNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        text = attrs.get("text")
        if text is None:
            raise ValueError("Text is required for status nodes")

        color = attrs.get("color")
        if color is None:
            raise ValueError("Color is required for status nodes")

        return cls(text=text, color=color)


@dataclass
class MentionNode(ADFNode):
    """Represents a mention node in ADF."""

    type: str = field(default="mention", init=False)
    id: str
    text: Optional[str] = None
    user_type: Optional[str] = None
    access_level: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MentionNode":
        """Create a MentionNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        id = attrs.get("id")
        if id is None:
            raise ValueError("ID is required for mention nodes")

        return cls(
            id=id,
            text=attrs.get("text"),
            user_type=attrs.get("userType"),
            access_level=attrs.get("accessLevel"),
        )


@dataclass
class TableNode(ADFNode):
    """Represents a table node in ADF."""

    type: str = field(default="table", init=False)
    children: List[ADFNode] = field(default_factory=list)
    is_number_column_enabled: Optional[bool] = None
    width: Optional[int] = None
    layout: Optional[str] = None
    display_mode: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TableNode":
        """Create a TableNode from a dictionary, preserving all child nodes."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))

        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        return cls(
            children=children,
            is_number_column_enabled=attrs.get("isNumberColumnEnabled"),
            width=attrs.get("width"),
            layout=attrs.get("layout"),
            display_mode=attrs.get("displayMode"),
        )


@dataclass
class TableRowNode(ADFNode):
    """Represents a table row node in ADF."""

    type: str = field(default="tableRow", init=False)
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TableRowNode":
        """Create a TableRowNode from a dictionary, preserving all child nodes."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(children=children)


@dataclass
class TableCellNode(ADFNode):
    """Represents a table cell node in ADF."""

    type: str = field(default="tableCell", init=False)
    children: List[ADFNode] = field(default_factory=list)
    background: Optional[str] = None
    colwidth: Optional[List[int]] = None
    colspan: Optional[int] = None
    rowspan: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TableCellNode":
        """Create a TableCellNode from a dictionary, preserving all child nodes."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))

        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        return cls(
            children=children,
            background=attrs.get("background"),
            colwidth=attrs.get("colwidth"),
            colspan=attrs.get("colspan"),
            rowspan=attrs.get("rowspan"),
        )


@dataclass
class TableHeaderNode(ADFNode):
    """Represents a table header node in ADF."""

    type: str = field(default="tableHeader", init=False)
    children: List[ADFNode] = field(default_factory=list)
    background: Optional[str] = None
    colwidth: Optional[List[int]] = None
    colspan: Optional[int] = None
    rowspan: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TableHeaderNode":
        """Create a TableHeaderNode from a dictionary, preserving all child nodes."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))

        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        return cls(
            children=children,
            background=attrs.get("background"),
            colwidth=attrs.get("colwidth"),
            colspan=attrs.get("colspan"),
            rowspan=attrs.get("rowspan"),
        )


@dataclass
class ExtensionNode(ADFNode):
    """Represents an extension node in ADF."""

    type: str = field(default="extension", init=False)
    extension_type: str
    extension_key: str
    text: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtensionNode":
        """Create an ExtensionNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        extension_type = attrs.get("extensionType")
        if extension_type is None:
            raise ValueError("extensionType is required for extension nodes")

        extension_key = attrs.get("extensionKey")
        if extension_key is None:
            raise ValueError("extensionKey is required for extension nodes")

        return cls(
            extension_type=extension_type,
            extension_key=extension_key,
            text=attrs.get("text"),
            parameters=attrs.get("parameters"),
        )


@dataclass
class MediaSingleNode(ADFNode):
    """Represents a mediaSingle node in ADF."""

    type: str = field(default="mediaSingle", init=False)
    layout: Optional[str] = None
    width: Optional[int] = None
    width_type: Optional[str] = None
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaSingleNode":
        """Create a MediaSingleNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))

        return cls(
            layout=attrs.get("layout"),
            width=attrs.get("width"),
            width_type=attrs.get("widthType"),
            children=children,
        )


@dataclass
class MediaGroupNode(ADFNode):
    """Represents a mediaGroup node in ADF."""

    type: str = field(default="mediaGroup", init=False)
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaGroupNode":
        """Create a MediaGroupNode from a dictionary."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(children=children)


@dataclass
class MediaNode(ADFNode):
    """Represents a media node in ADF."""

    type: str = field(default="media", init=False)
    id: str
    collection: str
    media_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    alt: Optional[str] = None
    border_size: Optional[int] = None
    border_color: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaNode":
        """Create a MediaNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        id = attrs.get("id")
        if id is None:
            raise ValueError("ID is required for media nodes")

        collection = attrs.get("collection")
        if collection is None:
            raise ValueError("Collection is required for media nodes")

        media_type = attrs.get("type")
        if media_type is None:
            raise ValueError("Type is required for media nodes")

        border_size = None
        border_color = None
        for mark in data.get("marks", []):
            if mark.get("type") == "border":
                border_attrs = mark.get("attrs", {})
                border_size = border_attrs.get("size")
                border_color = border_attrs.get("color")

        return cls(
            id=id,
            collection=collection,
            media_type=media_type,
            width=attrs.get("width"),
            height=attrs.get("height"),
            alt=attrs.get("alt"),
            border_size=border_size,
            border_color=border_color,
        )


@dataclass
class MediaInlineNode(ADFNode):
    """Represents a mediaInline node in ADF."""

    type: str = field(default="mediaInline", init=False)
    id: str
    collection: str
    media_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    alt: Optional[str] = None
    border_size: Optional[int] = None
    border_color: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaInlineNode":
        """Create a MediaInlineNode from a dictionary."""
        attrs = data.get("attrs", {})
        if attrs is None:
            attrs = {}

        id = attrs.get("id")
        if id is None:
            raise ValueError("ID is required for mediaInline nodes")

        collection = attrs.get("collection")
        if collection is None:
            raise ValueError("Collection is required for mediaInline nodes")

        media_type = attrs.get("type")
        if media_type is None:
            raise ValueError("Type is required for mediaInline nodes")

        border_size = None
        border_color = None
        for mark in data.get("marks", []):
            if mark.get("type") == "border":
                border_attrs = mark.get("attrs", {})
                border_size = border_attrs.get("size")
                border_color = border_attrs.get("color")

        return cls(
            id=id,
            collection=collection,
            media_type=media_type,
            width=attrs.get("width"),
            height=attrs.get("height"),
            alt=attrs.get("alt"),
            border_size=border_size,
            border_color=border_color,
        )


@dataclass
class CaptionNode(ADFNode):
    """Represents a caption node in ADF."""

    type: str = field(default="caption", init=False)
    children: List[ADFNode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaptionNode":
        """Create a CaptionNode from a dictionary."""
        children = []
        for item in data.get("content", []):
            children.append(ADFNode.from_dict(item))
        return cls(children=children)

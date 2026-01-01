"""
ADF to Markdown converters for adfmd.
Contains base class, registry, and all converters for converting ADF nodes to Markdown format.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
from typing import Any, Dict, Optional, List, Tuple


from adfmd.nodes import (
    ADFNode,
    BulletListNode,
    ListItemNode,
    ParagraphNode,
    OrderedListNode,
    HardBreakNode,
    HeadingNode,
    TextNode,
    InlineCardNode,
    RuleNode,
    DateNode,
    DocNode,
    StatusNode,
    MentionNode,
    TableNode,
    TableRowNode,
    TableCellNode,
    TableHeaderNode,
    ExtensionNode,
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

    def _convert_table_cell_or_header(self, node: ADFNode, marker_name: str, **kwargs: Any) -> str:
        """Shared conversion logic for table cells and headers."""
        attrs_parts = []
        if node.background is not None:
            attrs_parts.append(f'background="{node.background}"')
        if node.colwidth is not None:
            attrs_parts.append(f'colwidth="{",".join(map(str, node.colwidth))}"')
        if node.colspan is not None and node.colspan != 1:  # Default: "1"
            attrs_parts.append(f'colspan="{node.colspan}"')
        if node.rowspan is not None and node.rowspan != 1:  # Default: "1"
            attrs_parts.append(f'rowspan="{node.rowspan}"')

        attrs_str = ",".join(attrs_parts)
        start_marker = f"<!-- ADF:{marker_name}{':' + attrs_str if attrs_str else ''} -->"
        end_marker = f"<!-- /ADF:{marker_name} -->"

        text_parts = []
        for child_node in node.children:
            kwargs["no_newlines"] = child_node is node.children[-1]
            text_parts.append(self._convert_child(child_node, **kwargs))

        content = "".join(text_parts)
        content = content.replace("  \n", "<br/>").replace("\n", "<br/>")

        return f"{start_marker}{content}{end_marker}"


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

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """
        Convert an ADF node to Markdown using the appropriate converter.

        Args:
            node: The ADF node dataclass instance
            **kwargs: Additional arguments to pass to converters

        Returns:
            Markdown string representation

        Raises:
            ValueError: If no converter is available for the node type
        """
        if not self.has_converter(node.type):
            raise ValueError(f"Unsupported node type: {node.type}")

        converter = self.get_converter(node.type)
        return converter.convert(node, **kwargs)

    @classmethod
    def create_default(cls) -> "ADF2MDRegistry":
        """
        Create a registry with all ADF to Markdown converters.

        Returns:
            ADF2MDRegistry instance with all converters registered
        """

        registry = cls()

        # Register converters
        registry.register("doc", DocConverter())
        registry.register("text", TextConverter())
        registry.register("paragraph", ParagraphConverter())
        registry.register("heading", HeadingConverter())
        registry.register("bulletList", BulletListConverter())
        registry.register("orderedList", OrderedListConverter())
        registry.register("hardBreak", HardBreakConverter())
        registry.register("inlineCard", InlineCardConverter())
        registry.register("rule", RuleConverter())
        registry.register("date", DateConverter())
        registry.register("status", StatusConverter())
        registry.register("mention", MentionConverter())
        registry.register("table", TableConverter())
        registry.register("tableRow", TableRowConverter())
        registry.register("tableCell", TableCellConverter())
        registry.register("tableHeader", TableHeaderConverter())
        registry.register("extension", ExtensionConverter())

        return registry


class TextConverter(ADF2MDBaseConverter):
    """Converter for text nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a text node to its string representation with markdown annotations."""
        if not isinstance(node, TextNode):
            raise ValueError(f"Expected TextNode, got {type(node)}")

        text = node.text
        marks = node.marks
        url = node.url

        # Map ADF mark types to markdown formatting
        mark_formatters = {
            "code": lambda t: f"`{t}`",
            "em": lambda t: f"*{t}*",
            "strong": lambda t: f"**{t}**",
            "strike": lambda t: f"~~{t}~~",
        }

        # Apply marks in order
        mark_order = ["code", "em", "strong", "strike"]
        for mark_type in mark_order:
            if mark_type in marks:
                formatter = mark_formatters.get(mark_type)
                if formatter:
                    text = formatter(text)

        # Apply markdown URL formatting last (wraps all other formatting)
        if url:
            text = f"[{text}]({url})"

        # Add start and end markers for unsupported marks for round-trip conversion
        unsupported_marks = [
            m for m in marks if m in ["underline", "subsup", "textColor", "backgroundColor"]
        ]
        if unsupported_marks:
            if node.subsup:
                unsupported_marks.remove("subsup")
                unsupported_marks.append(f"subsup={node.subsup}")
            if node.text_color:
                unsupported_marks.remove("textColor")
                unsupported_marks.append(f"textColor={node.text_color}")
            if node.background_color:
                unsupported_marks.remove("backgroundColor")
                unsupported_marks.append(f"backgroundColor={node.background_color}")

            marks_str = ",".join(unsupported_marks)
            start_marker = f'<!-- ADF:text:marks="{marks_str}" -->'
            end_marker = "<!-- /ADF:text -->"
            return f"{start_marker}{text}{end_marker}"

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


class InlineCardConverter(ADF2MDBaseConverter):
    """Converter for inlineCard nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert an inlineCard node to Markdown link."""
        if not isinstance(node, InlineCardNode):
            raise ValueError(f"Expected InlineCardNode, got {type(node)}")

        # Store as markdown link using the URL as text
        return f"[{node.url}]({node.url})"


class RuleConverter(ADF2MDBaseConverter):
    """Converter for rule (horizontal rule) nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a rule node to Markdown horizontal rule."""
        if not isinstance(node, RuleNode):
            raise ValueError(f"Expected RuleNode, got {type(node)}")

        # In Markdown, a horizontal rule is represented as three or more dashes on their own line, # with blank lines before and after
        return "---\n\n"


class DateConverter(ADF2MDBaseConverter):
    """Converter for date nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """
        Convert a date node to Markdown.

        The timestamp is interpreted as milliseconds since Unix epoch.
        The date is formatted as ISO 8601 UTC timestamp (e.g., 2025-12-02T20:51:13Z).

        Start and end markers are added as HTML comments to preserve the original date node for round-trip conversion.
        """
        if not isinstance(node, DateNode):
            raise ValueError(f"Expected DateNode, got {type(node)}")

        dt = datetime.fromtimestamp(float(node.timestamp) / 1000, tz=timezone.utc)
        formatted_date = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        start_marker = f'<!-- ADF:date:timestamp="{node.timestamp}" -->'
        end_marker = "<!-- /ADF:date -->"
        return f"{start_marker}{formatted_date}{end_marker}"


class DocConverter(ADF2MDBaseConverter):
    """Converter for doc (document root) nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """
        Convert a doc node to Markdown.

        The doc node is the root node of an ADF document. It simply converts
        all its children to Markdown.

        Start and end markers are added as HTML comments to preserve the original doc node for round-trip conversion.
        """
        if not isinstance(node, DocNode):
            raise ValueError(f"Expected DocNode, got {type(node)}")

        text_parts = []
        for child_node in node.children:
            text_parts.append(self._convert_child(child_node))
        content = "".join(text_parts)

        if node.version is not None:
            start_marker = f'<!-- ADF:doc:version="{node.version}" -->'
        else:
            start_marker = "<!-- ADF:doc -->"
        end_marker = "<!-- /ADF:doc -->"

        return f"{start_marker}\n{content.rstrip()}\n{end_marker}"


class StatusConverter(ADF2MDBaseConverter):
    """Converter for status nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """
        Convert a status node to Markdown.

        Start and end markers are added as HTML comments to preserve the original status node for round-trip conversion.
        """
        if not isinstance(node, StatusNode):
            raise ValueError(f"Expected StatusNode, got {type(node)}")

        attrs_parts = [f'text="{node.text}"']
        attrs_parts.append(f'color="{node.color}"')

        attrs_str = ",".join(attrs_parts)
        start_marker = f"<!-- ADF:status:{attrs_str} -->"
        end_marker = "<!-- /ADF:status -->"

        return f"{start_marker}{node.text}{end_marker}"


class MentionConverter(ADF2MDBaseConverter):
    """Converter for mention nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """
        Convert a mention node to Markdown.

        Start and end markers are added as HTML comments to preserve the original mention node for round-trip conversion.
        """
        if not isinstance(node, MentionNode):
            raise ValueError(f"Expected MentionNode, got {type(node)}")

        attrs_parts = [f'id="{node.id}"']
        if node.text:
            attrs_parts.append(f'text="{node.text}"')
        if node.user_type:
            attrs_parts.append(f'userType="{node.user_type}"')
        if node.access_level:
            attrs_parts.append(f'accessLevel="{node.access_level}"')

        attrs_str = ",".join(attrs_parts)
        start_marker = f"<!-- ADF:mention:{attrs_str} -->"
        end_marker = "<!-- /ADF:mention -->"

        # Use text if available, otherwise use @mention with id
        display_text = node.text if node.text else f"@mention({node.id})"

        return f"{start_marker}{display_text}{end_marker}"


class TableConverter(ADF2MDBaseConverter):
    """Converter for table nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a table node to Markdown."""
        if not isinstance(node, TableNode):
            raise ValueError(f"Expected TableNode, got {type(node)}")

        kwargs.update({"inside_table": True})
        nested_tables = kwargs.get("nested_tables")
        if nested_tables is None:
            nested_tables = []
            kwargs.update({"nested_tables": nested_tables})

        # Generate HTML comments with table attributes
        attrs_parts = []
        if node.is_number_column_enabled is not None:
            attrs_parts.append(
                f'isNumberColumnEnabled="{str(node.is_number_column_enabled).lower()}"'
            )
        if node.width is not None and node.width != 760:  # Default: 760
            attrs_parts.append(f'width="{node.width}"')
        if node.layout and node.layout != "default":  # Default: "default"
            attrs_parts.append(f'layout="{node.layout}"')
        if node.display_mode and node.display_mode != "default":  # Default: "default"
            attrs_parts.append(f'displayMode="{node.display_mode}"')

        attrs_str = ",".join(attrs_parts)
        start_marker = f"<!-- ADF:table{':' + attrs_str if attrs_str else ''} -->"
        end_marker = "<!-- /ADF:table -->"

        rows: List[str] = []
        row_nodes: List[TableRowNode] = [c for c in node.children if isinstance(c, TableRowNode)]
        is_first_row: bool = True
        active_rowspans: List[Tuple[int, int, int]] = []  # (col_start, col_end, remaining_rows)

        for row_node in row_nodes:
            new_rowspans: List[Tuple[int, int, int]] = []  # (col_start, col_end, remaining_rows)
            kwargs.update({"active_rowspans": active_rowspans, "new_rowspans": new_rowspans})
            rows.append(self._convert_child(row_node, **kwargs))

            # Add separator row after first row
            if is_first_row:
                cell_count = len(rows[0].split("|")) - 2  # remove empty strings before and after
                rows.append("| " + " | ".join(["---"] * cell_count) + " |")
                is_first_row = False

            # Update active rowspans
            active_rowspans = [
                (col_start, col_end, remaining - 1)
                for col_start, col_end, remaining in active_rowspans
                if remaining > 1
            ]

            # Add new active rowspans
            active_rowspans.extend(new_rowspans)

        # Join rows with newlines
        table_markdown = "\n".join(rows)

        nested_tables_markdown = ""
        if nested_tables:
            nested_tables_markdown = "\n" + "\n".join(nested_tables)

        return f"{start_marker}\n{table_markdown}\n{end_marker}{nested_tables_markdown}\n\n"


class TableRowConverter(ADF2MDBaseConverter):
    """Converter for table row nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a table row node to Markdown."""
        if not isinstance(node, TableRowNode):
            raise ValueError(f"Expected TableRowNode, got {type(node)}")

        active_rowspans: List[Tuple[int, int, int]] = kwargs.get("active_rowspans", [])
        new_rowspans: List[Tuple[int, int, int]] = kwargs.get("new_rowspans", [])

        cells: List[str] = []
        current_col: int = 0

        for cell_node in [
            c for c in node.children if isinstance(c, (TableCellNode, TableHeaderNode))
        ]:
            # Add empty cells for active rowspans that cover columns before this cell
            while any(
                col_start <= current_col < col_end for col_start, col_end, _ in active_rowspans
            ):
                cells.append("")
                current_col += 1

            # Add the actual cell (pass through kwargs for nested tables)
            cells.append(" " + self._convert_child(cell_node, **kwargs) + " ")
            colspan = cell_node.colspan if cell_node.colspan else 1
            rowspan = cell_node.rowspan if cell_node.rowspan else 1

            # Add empty cells for colspan
            if colspan > 1:
                cells.extend(["" for _ in range(colspan - 1)])

            # Track rowspan if it spans multiple rows
            if rowspan > 1:
                new_rowspans.append((current_col, current_col + colspan, rowspan - 1))

            current_col += colspan

        # Add empty cells for remaining active rowspans
        max_col = max([col_end for _, col_end, _ in active_rowspans], default=current_col)
        while current_col < max_col:
            cells.append("")
            current_col += 1

        # Join cells with pipe separators
        return "|" + "|".join(cells) + "|"


class TableCellConverter(ADF2MDBaseConverter):
    """Converter for table cell nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a table cell node to Markdown."""
        if not isinstance(node, TableCellNode):
            raise ValueError(f"Expected TableCellNode, got {type(node)}")

        return self._convert_table_cell_or_header(node, "tableCell", **kwargs)


class TableHeaderConverter(ADF2MDBaseConverter):
    """Converter for table header nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert a table header node to Markdown."""
        if not isinstance(node, TableHeaderNode):
            raise ValueError(f"Expected TableHeaderNode, got {type(node)}")

        return self._convert_table_cell_or_header(node, "tableHeader", **kwargs)


class ExtensionConverter(ADF2MDBaseConverter):
    """Converter for extension nodes."""

    def convert(self, node: ADFNode, **kwargs: Any) -> str:
        """Convert an extension node to Markdown."""
        if not isinstance(node, ExtensionNode):
            raise ValueError(f"Expected ExtensionNode, got {type(node)}")

        no_newlines = kwargs.get("no_newlines", False)

        # Convert table extension node to markdown
        if (
            node.extension_type == "com.atlassian.confluence.migration"
            and node.extension_key == "nested-table"
            and node.parameters
            and "adf" in node.parameters
        ):
            inside_table = kwargs.get("inside_table", False)
            nested_tables = kwargs.get("nested_tables", [])
            nested_table_counter = kwargs.get("nested_table_counter")
            if nested_table_counter is None:
                kwargs.update({"nested_table_counter": {"count": 0}})

            nested_adf = json.loads(node.parameters["adf"])
            nested_doc = DocNode.from_dict(nested_adf)

            if inside_table:
                nested_table_counter["count"] += 1
                ref_id = f"nested-table-{nested_table_counter['count']}"

                nested_kwargs = kwargs.copy()
                nested_nested_tables = []
                nested_kwargs["nested_tables"] = nested_nested_tables
                nested_kwargs["nested_table_counter"] = nested_table_counter
                doc_converter = self.registry.get_converter("doc")
                nested_markdown = doc_converter.convert(nested_doc, **nested_kwargs)

                nested_tables.append(
                    f'<!-- ADF:nested-table:ref="{ref_id}" -->\n'
                    f'<a name="{ref_id}">**{ref_id}**</a>\n'
                    f"{nested_markdown.rstrip()}\n"
                    f"<!-- /ADF:nested-table -->"
                )

                start_marker = f'<!-- ADF:extension:extensionType="com.atlassian.confluence.migration",extensionKey="nested-table",ref="{ref_id}" -->'
                end_marker = "<!-- /ADF:extension -->"
                markdown_content = f"[**{ref_id}**](#{ref_id})"
            else:
                start_marker = '<!-- ADF:extension:extensionType="com.atlassian.confluence.migration",extensionKey="nested-table" -->'
                end_marker = "<!-- /ADF:extension -->"
                markdown_content = "\n" + self.registry.convert(nested_doc) + "\n"
            text = f"{start_marker}{markdown_content}{end_marker}"
            text += "\n" if not no_newlines else ""

        # Preserve unknown extension nodes as HTML comment
        else:
            attrs_parts = [f'extensionType="{node.extension_type}"']
            attrs_parts.append(f'extensionKey="{node.extension_key}"')
            if node.text:
                attrs_parts.append(f'text="{node.text}"')

            attrs_str = ",".join(attrs_parts)
            start_marker = f"<!-- ADF:extension:{attrs_str} -->"
            end_marker = "<!-- /ADF:extension -->"
            text = f"{start_marker}{end_marker}"

        return text

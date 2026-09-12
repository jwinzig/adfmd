"""
Markdown to ADF converters for adfmd.
Contains parser and registry for converting Markdown to ADF format.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union

ADF_NODE = Dict[str, Any]

INLINE_MARKER_RE = re.compile(r"<!--\s*ADF:([a-zA-Z0-9_-]+)(?::(.*?))?\s*-->")
START_MARKER_RE = re.compile(r"^\s*<!--\s*ADF:([a-zA-Z0-9_-]+)(?::([^>]*)?)?\s*-->\s*$")
END_MARKER_RE = re.compile(r"^\s*<!--\s*/ADF:([a-zA-Z0-9_-]+)\s*-->\s*$")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
MARK_ORDER = {
    "strong": 0,
    "em": 1,
    "code": 2,
    "strike": 3,
    "underline": 4,
    "textColor": 5,
    "backgroundColor": 6,
    "subsup": 7,
    "link": 8,
}
NESTED_TABLE_REASON = "A table in a table cell can't be created or edited in the new editor."

NODE_KEY_ORDER = {
    "doc": ["type", "version", "content"],
    "text": ["type", "text", "marks"],
    "paragraph": ["type", "content"],
    "heading": ["type", "attrs", "content"],
    "codeBlock": ["type", "attrs", "content"],
    "panel": ["type", "attrs", "content"],
    "expand": ["type", "attrs", "content"],
    "nestedExpand": ["type", "attrs", "content"],
    "bulletList": ["type", "content"],
    "orderedList": ["type", "content"],
    "listItem": ["type", "content"],
    "blockquote": ["type", "content"],
    "rule": ["type"],
    "hardBreak": ["type"],
    "status": ["type", "attrs"],
    "mention": ["type", "attrs"],
    "emoji": ["type", "attrs"],
    "date": ["type", "attrs"],
    "inlineCard": ["type", "attrs"],
    "media": ["type", "attrs", "marks"],
    "mediaInline": ["type", "attrs"],
    "mediaSingle": ["type", "attrs", "content"],
    "mediaGroup": ["type", "content"],
    "caption": ["type", "content"],
    "table": ["type", "attrs", "content"],
    "tableRow": ["type", "attrs", "content"],
    "tableCell": ["type", "attrs", "content"],
    "tableHeader": ["type", "attrs", "content"],
    "extension": ["type", "attrs"],
}

ATTR_KEY_ORDER = {
    "heading": ["level"],
    "codeBlock": ["language"],
    "panel": ["panelType"],
    "expand": ["title"],
    "nestedExpand": ["title"],
    "table": ["layout", "isNumberColumnEnabled", "width", "displayMode"],
    "tableCell": ["colspan", "rowspan", "colwidth", "background"],
    "tableHeader": ["colspan", "rowspan", "colwidth", "background"],
    "status": ["text", "color"],
    "mention": ["id", "text", "userType", "accessLevel"],
    "emoji": ["shortName", "id", "text"],
    "date": ["timestamp"],
    "media": ["id", "type", "collection", "alt", "width", "height"],
    "mediaInline": ["id", "type", "collection", "alt", "width", "height"],
    "mediaSingle": ["layout", "width", "widthType"],
    "extension": ["extensionType", "extensionKey", "text", "parameters"],
}

PARAMETER_KEY_ORDER = ["reason", "adf", "ref"]
MARK_KEY_ORDER = ["type", "attrs"]
MARK_ATTR_ORDER = {
    "link": ["href"],
    "textColor": ["color"],
    "backgroundColor": ["color"],
    "subsup": ["type"],
    "border": ["size", "color"],
}


def _normalize_marks(marks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not marks:
        return []
    return sorted(
        marks,
        key=lambda mark: (MARK_ORDER.get(mark.get("type"), 99), mark.get("type", "")),
    )


CODE_RE = re.compile(r"`([^`]+)`")
BOLD_ITALIC_RE = re.compile(r"\*\*\*([^*]+)\*\*\*")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
STRIKE_RE = re.compile(r"~~([^~]+)~~")
ITALIC_RE = re.compile(r"\*([^*]+)\*")


def _split_attrs(attr_str: str) -> List[str]:
    parts: List[str] = []
    current = []
    in_quotes = False
    for char in attr_str:
        if char == '"':
            in_quotes = not in_quotes
            current.append(char)
        elif char == "," and not in_quotes:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)
    if current:
        part = "".join(current).strip()
        if part:
            parts.append(part)
    return parts


def _parse_attrs(attr_str: Optional[str]) -> Dict[str, str]:
    attrs: Dict[str, str] = {}
    if not attr_str:
        return attrs
    for key, value in re.findall(r'([a-zA-Z0-9_-]+)="([^"]*)"', attr_str):
        attrs[key] = value
    if attrs:
        return attrs
    for part in _split_attrs(attr_str):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"')
        attrs[key] = value
    return attrs


def _parse_number(value: Optional[str]) -> Optional[Union[int, float]]:
    if value is None:
        return None
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return None


def _parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return None


def _order_dict_by_keys(
    data: Dict[str, Any], key_order: List[str], value_order_fn: Optional[Any] = None
) -> Dict[str, Any]:
    ordered: Dict[str, Any] = {}
    for key in key_order:
        if key in data:
            value = data[key]
            ordered[key] = value_order_fn(key, value) if value_order_fn else value
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value_order_fn(key, value) if value_order_fn else value
    return ordered


def _order_mark(mark: Dict[str, Any]) -> Dict[str, Any]:
    mark_type = mark.get("type")

    def order_mark_value(key: str, value: Any) -> Any:
        if key == "attrs" and isinstance(value, dict):
            attr_order = MARK_ATTR_ORDER.get(mark_type, [])
            return _order_dict_by_keys(value, attr_order)
        return value

    return _order_dict_by_keys(mark, MARK_KEY_ORDER, order_mark_value)


def _order_node(node: Any) -> Any:
    if isinstance(node, list):
        return [_order_node(item) for item in node]
    if not isinstance(node, dict):
        return node

    node_type = node.get("type")

    def order_node_value(key: str, value: Any) -> Any:
        if key == "attrs" and isinstance(value, dict):
            attr_order = ATTR_KEY_ORDER.get(node_type, [])

            def order_attr_value(attr_key: str, attr_value: Any) -> Any:
                if (
                    node_type == "extension"
                    and attr_key == "parameters"
                    and isinstance(attr_value, dict)
                ):
                    return _order_dict_by_keys(attr_value, PARAMETER_KEY_ORDER)
                return _order_node(attr_value)

            return _order_dict_by_keys(value, attr_order, order_attr_value)
        if key == "marks" and isinstance(value, list):
            return [_order_mark(mark) if isinstance(mark, dict) else mark for mark in value]
        return _order_node(value)

    key_order = NODE_KEY_ORDER.get(node_type)
    if key_order:
        return _order_dict_by_keys(node, key_order, order_node_value)
    return {key: order_node_value(key, value) for key, value in node.items()}


def _parse_marks(marks_str: str) -> List[Dict[str, Any]]:
    marks: List[Dict[str, Any]] = []
    if not marks_str:
        return marks
    for item in marks_str.split(","):
        item = item.strip()
        if not item:
            continue
        if item.startswith("textColor="):
            marks.append({"type": "textColor", "attrs": {"color": item.split("=", 1)[1]}})
        elif item.startswith("backgroundColor="):
            marks.append({"type": "backgroundColor", "attrs": {"color": item.split("=", 1)[1]}})
        elif item.startswith("subsup="):
            marks.append({"type": "subsup", "attrs": {"type": item.split("=", 1)[1]}})
        else:
            marks.append({"type": item})
    return marks


def _apply_marks(nodes: List[ADF_NODE], marks: List[Dict[str, Any]]) -> List[ADF_NODE]:
    if not marks:
        return nodes
    updated: List[ADF_NODE] = []
    for node in nodes:
        if node.get("type") == "text":
            node_marks = list(node.get("marks", [])) + marks
            node["marks"] = _normalize_marks(node_marks)
        updated.append(node)
    return updated


def _merge_text_nodes(nodes: List[ADF_NODE]) -> List[ADF_NODE]:
    merged: List[ADF_NODE] = []
    for node in nodes:
        if (
            merged
            and node.get("type") == "text"
            and merged[-1].get("type") == "text"
            and merged[-1].get("marks", []) == node.get("marks", [])
        ):
            merged[-1]["text"] = merged[-1].get("text", "") + node.get("text", "")
        else:
            merged.append(node)
    return merged


def _make_text(text: str, marks: Optional[List[Dict[str, Any]]] = None) -> ADF_NODE:
    normalized = _normalize_marks(list(marks or []))
    return {"type": "text", "text": text, "marks": normalized}


def _ensure_text_marks_recursive(node: Any, parent_type: Optional[str] = None) -> None:
    if isinstance(node, dict):
        node_type = node.get("type")
        if node_type == "text":
            if parent_type == "codeBlock":
                node.pop("marks", None)
            elif "marks" not in node:
                node["marks"] = []
        for value in node.values():
            _ensure_text_marks_recursive(value, node_type)
    elif isinstance(node, list):
        for item in node:
            _ensure_text_marks_recursive(item, parent_type)


class MD2ADFRegistry:
    """Registry for managing Markdown to ADF conversion."""

    def __init__(self):
        self.parser = MarkdownParser()

    def convert(self, markdown: str) -> Union[ADF_NODE, List[ADF_NODE]]:
        return self.parser.parse(markdown)

    @classmethod
    def create_default(cls) -> "MD2ADFRegistry":
        return cls()


class MarkdownParser:
    """Line-based Markdown to ADF parser tuned for adfmd output."""

    def __init__(self) -> None:
        self._nested_tables: Dict[str, ADF_NODE] = {}
        self._table_count = 0

    def parse(self, markdown: str) -> Union[ADF_NODE, List[ADF_NODE]]:
        lines = markdown.splitlines()
        nodes, _ = self._parse_blocks(lines, 0, len(lines))
        if self._nested_tables:
            self._attach_nested_tables(nodes)
        nodes = _merge_text_nodes(nodes)
        _ensure_text_marks_recursive(nodes)
        nodes = _order_node(nodes)
        if len(nodes) == 1 and nodes[0].get("type") == "doc":
            return nodes[0]
        if len(nodes) == 1:
            return nodes[0]
        return nodes

    def _attach_nested_tables(self, nodes: List[ADF_NODE]) -> None:
        for node in self._walk_nodes(nodes):
            if node.get("type") == "extension":
                attrs = node.get("attrs", {})
                if (
                    attrs.get("extensionType") == "com.atlassian.confluence.migration"
                    and attrs.get("extensionKey") == "nested-table"
                ):
                    attrs.setdefault("text", "")
                    params = attrs.setdefault("parameters", {})
                    ref = params.get("ref")
                    if ref and ref in self._nested_tables:
                        nested_doc = self._nested_tables[ref]
                        params["adf"] = json.dumps(nested_doc)
                        params.setdefault("reason", NESTED_TABLE_REASON)
                        params.pop("ref", None)

    def _walk_nodes(self, nodes: List[ADF_NODE]) -> List[ADF_NODE]:
        all_nodes: List[ADF_NODE] = []
        for node in nodes:
            all_nodes.append(node)
            if "content" in node and isinstance(node["content"], list):
                all_nodes.extend(self._walk_nodes(node["content"]))
        return all_nodes

    def _parse_blocks(self, lines: List[str], start: int, end: int) -> Tuple[List[ADF_NODE], int]:
        nodes: List[ADF_NODE] = []
        i = start
        while i < end:
            line = lines[i]
            if not line.strip():
                blank_count = 0
                while i < end and not lines[i].strip():
                    blank_count += 1
                    i += 1
                # Treat extra blank lines as empty paragraphs for consistency.
                # Two blank lines separate blocks; additional blanks become empty paragraphs.
                for _ in range(max(blank_count - 2, 0)):
                    nodes.append({"type": "paragraph"})
                continue

            start_marker = START_MARKER_RE.match(line)
            if start_marker:
                marker_type = start_marker.group(1)
                attrs = _parse_attrs(start_marker.group(2))
                if marker_type == "doc":
                    inner_lines, i = self._collect_until_end(lines, i + 1, end, marker_type)
                    content, _ = self._parse_blocks(inner_lines, 0, len(inner_lines))
                    doc_node: ADF_NODE = {"type": "doc", "content": content}
                    if attrs.get("version") is not None:
                        version = _parse_number(attrs.get("version"))
                        if version is not None:
                            doc_node["version"] = version
                    nodes.append(doc_node)
                    continue
                if marker_type == "panel":
                    inner_lines, i = self._collect_until_end(lines, i + 1, end, marker_type)
                    nodes.append(self._parse_panel(inner_lines, attrs))
                    continue
                if marker_type == "expand":
                    inner_lines, i = self._collect_until_end(lines, i + 1, end, marker_type)
                    nodes.append(self._parse_expand(inner_lines, attrs, "expand"))
                    continue
                if marker_type == "nestedExpand":
                    inner_lines, i = self._collect_until_end(lines, i + 1, end, marker_type)
                    nodes.append(self._parse_expand(inner_lines, attrs, "nestedExpand"))
                    continue
                if marker_type == "table":
                    inner_lines, i = self._collect_until_end(lines, i + 1, end, marker_type)
                    nodes.append(self._parse_table(inner_lines, attrs))
                    continue
                if marker_type == "mediaSingle":
                    inner_lines, i = self._collect_until_end(lines, i + 1, end, marker_type)
                    nodes.append(self._parse_media_single(inner_lines, attrs))
                    continue
                if marker_type == "mediaGroup":
                    inner_lines, i = self._collect_until_end(lines, i + 1, end, marker_type)
                    nodes.append(self._parse_media_group(inner_lines))
                    continue
                if marker_type == "nested-table":
                    inner_lines, i = self._collect_until_end(lines, i + 1, end, marker_type)
                    self._parse_nested_table(inner_lines, attrs)
                    continue
                if marker_type == "extension":
                    inner_lines, i = self._collect_until_end(lines, i + 1, end, marker_type)
                    extension_node = self._parse_extension_block(inner_lines, attrs)
                    if extension_node:
                        nodes.append(extension_node)
                    continue

            if line.startswith("```"):
                code_node, i = self._parse_code_block(lines, i, end)
                nodes.append(code_node)
                continue

            if line.lstrip().startswith(">"):
                quote_lines, i = self._collect_blockquote(lines, i, end)
                nodes.append(self._parse_blockquote(quote_lines))
                continue

            list_match = re.match(r"^(\s*)(- |\d+\. )", line)
            if list_match:
                list_node, i = self._parse_list(lines, i, end, len(list_match.group(1)))
                nodes.append(list_node)
                continue

            heading_match = re.match(r"^(#{1,6})\s+(.*)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                content = self._parse_inlines(text)
                nodes.append({"type": "heading", "attrs": {"level": level}, "content": content})
                i += 1
                continue

            if re.match(r"^\s*-{3,}\s*$", line):
                nodes.append({"type": "rule"})
                i += 1
                continue

            para_lines, i = self._collect_paragraph(lines, i, end)
            if para_lines:
                nodes.append(self._parse_paragraph(para_lines))
            else:
                i += 1

        return nodes, i

    def _collect_until_end(
        self, lines: List[str], start: int, end: int, marker_type: str
    ) -> Tuple[List[str], int]:
        inner: List[str] = []
        i = start
        while i < end:
            if (
                END_MARKER_RE.match(lines[i])
                and END_MARKER_RE.match(lines[i]).group(1) == marker_type
            ):
                return inner, i + 1
            inner.append(lines[i])
            i += 1
        return inner, i

    def _collect_blockquote(self, lines: List[str], start: int, end: int) -> Tuple[List[str], int]:
        collected: List[str] = []
        i = start
        while i < end and lines[i].lstrip().startswith(">"):
            collected.append(lines[i])
            i += 1
        return collected, i

    def _collect_paragraph(self, lines: List[str], start: int, end: int) -> Tuple[List[str], int]:
        collected: List[str] = []
        i = start
        while i < end:
            line = lines[i]
            if not line.strip():
                break
            if START_MARKER_RE.match(line):
                break
            if line.startswith("```"):
                break
            if line.lstrip().startswith(">"):
                break
            if re.match(r"^(\s*)(- |\d+\. )", line):
                break
            if re.match(r"^(#{1,6})\s+", line):
                break
            if re.match(r"^\s*-{3,}\s*$", line):
                break
            collected.append(line)
            i += 1
        return collected, i

    def _parse_blockquote(self, quote_lines: List[str]) -> ADF_NODE:
        dequoted = [re.sub(r"^\s*>\s?", "", line) for line in quote_lines]
        content, _ = self._parse_blocks(dequoted, 0, len(dequoted))
        return {"type": "blockquote", "content": content}

    def _parse_paragraph(self, lines: List[str]) -> ADF_NODE:
        content: List[ADF_NODE] = []
        for idx, line in enumerate(lines):
            hard_break = line.endswith("  ")
            line_text = line.rstrip()
            content.extend(self._parse_inlines(line_text))
            if hard_break:
                content.append({"type": "hardBreak"})
            elif idx < len(lines) - 1:
                content.append(_make_text(" "))
        if not content:
            content = [_make_text("")]
        merged = _merge_text_nodes(content)
        return {"type": "paragraph", "content": merged}

    def _parse_code_block(self, lines: List[str], start: int, end: int) -> Tuple[ADF_NODE, int]:
        fence = lines[start]
        language = fence[3:].strip() or None
        code_lines: List[str] = []
        i = start + 1
        while i < end and not lines[i].startswith("```"):
            code_lines.append(lines[i])
            i += 1
        if i < end:
            i += 1
        code_text = "\n".join(code_lines)
        node: ADF_NODE = {"type": "codeBlock", "content": [{"type": "text", "text": code_text}]}
        if language:
            node["attrs"] = {"language": language}
        return node, i

    def _parse_list(
        self, lines: List[str], start: int, end: int, base_indent: int
    ) -> Tuple[ADF_NODE, int]:
        first_line = lines[start]
        ordered = bool(re.match(rf"^\s{{{base_indent}}}\d+\.\s+", first_line))
        items: List[ADF_NODE] = []
        i = start
        while i < end:
            line = lines[i]
            match = re.match(r"^(\s*)(- |\d+\. )(.+)$", line)
            if not match:
                break
            indent = len(match.group(1))
            if indent != base_indent:
                break
            item_text = match.group(3).strip()
            paragraph = self._parse_paragraph([item_text])
            item_content: List[ADF_NODE] = [paragraph]
            i += 1
            if i < end:
                next_line = lines[i]
                next_match = re.match(r"^(\s*)(- |\d+\. )", next_line)
                if next_match and len(next_match.group(1)) > base_indent:
                    nested_node, i = self._parse_list(lines, i, end, len(next_match.group(1)))
                    item_content.append(nested_node)
            items.append({"type": "listItem", "content": item_content})
        list_type = "orderedList" if ordered else "bulletList"
        return {"type": list_type, "content": items}, i

    def _parse_panel(self, lines: List[str], attrs: Dict[str, str]) -> ADF_NODE:
        panel_type = attrs.get("panelType")
        dequoted: List[str] = []
        for line in lines:
            dequoted.append(re.sub(r"^\s*>\s?", "", line))
        if panel_type and dequoted:
            label = f"**{panel_type.upper()}**"
            if dequoted[0].strip().startswith(label):
                dequoted = dequoted[1:]
                if dequoted and not dequoted[0].strip():
                    dequoted = dequoted[1:]
        content, _ = self._parse_blocks(dequoted, 0, len(dequoted))
        node: ADF_NODE = {"type": "panel", "content": content}
        if panel_type:
            node["attrs"] = {"panelType": panel_type}
        return node

    def _parse_expand(self, lines: List[str], attrs: Dict[str, str], node_type: str) -> ADF_NODE:
        title = attrs.get("title")
        content_lines = list(lines)
        if content_lines:
            first = content_lines[0].strip()
            title_match = re.match(r"^\*\*(.+)\*\*$", first)
            if title_match:
                content_lines = content_lines[1:]
            if content_lines and not content_lines[0].strip():
                content_lines = content_lines[1:]
        content, _ = self._parse_blocks(content_lines, 0, len(content_lines))
        node: ADF_NODE = {"type": node_type, "content": content}
        if title:
            node["attrs"] = {"title": title}
        return node

    def _parse_table(self, lines: List[str], attrs: Dict[str, str]) -> ADF_NODE:
        self._table_count += 1
        is_first_table = self._table_count == 1
        rows: List[ADF_NODE] = []
        has_cell_attrs = any(re.search(r"(colwidth|colspan|rowspan)=", line) for line in lines)
        has_strong_text = any("**" in line for line in lines)
        for line in lines:
            if not line.strip():
                continue
            if re.match(r"^\s*\|\s*-{3,}", line):
                continue
            if "|" not in line:
                continue
            row = self._parse_table_row(line)
            if row:
                rows.append(row)
        table_attrs: Dict[str, Any] = {}
        is_number = _parse_bool(attrs.get("isNumberColumnEnabled"))
        if is_number is not None:
            table_attrs["isNumberColumnEnabled"] = is_number
        width = _parse_number(attrs.get("width"))
        if width is not None:
            table_attrs["width"] = width
        layout = attrs.get("layout")
        if layout:
            table_attrs["layout"] = layout
        display_mode = attrs.get("displayMode")
        if display_mode:
            table_attrs["displayMode"] = display_mode
        if has_cell_attrs or has_strong_text or table_attrs:
            table_attrs.setdefault("layout", "default")
            table_attrs.setdefault("width", 760.0)
            if (
                has_cell_attrs
                and not table_attrs.get("displayMode")
                and not table_attrs.get("isNumberColumnEnabled")
                and is_first_table
                and rows
            ):
                column_count = sum(
                    int(cell.get("attrs", {}).get("colspan", 1))
                    for cell in rows[0].get("content", [])
                )
                if column_count >= 3:
                    table_attrs["displayMode"] = "default"
        if table_attrs:
            for row in rows:
                for cell in row.get("content", []):
                    if cell.get("type") in {"tableCell", "tableHeader"}:
                        cell_attrs = cell.setdefault("attrs", {})
                        cell_attrs.setdefault("colspan", 1)
                        cell_attrs.setdefault("rowspan", 1)
        node: ADF_NODE = {"type": "table", "content": rows}
        if table_attrs:
            node["attrs"] = table_attrs
        return node

    def _parse_table_row(self, line: str) -> Optional[ADF_NODE]:
        row_text = line.strip()
        if row_text.startswith("|"):
            row_text = row_text[1:]
        if row_text.endswith("|"):
            row_text = row_text[:-1]
        cells = [cell.strip() for cell in row_text.split("|")]
        cell_nodes: List[ADF_NODE] = []
        for cell in cells:
            if not cell:
                continue
            cell_node = self._parse_table_cell(cell)
            if cell_node:
                cell_nodes.append(cell_node)
        if not cell_nodes:
            return None
        return {"type": "tableRow", "content": cell_nodes}

    def _parse_table_cell(self, cell: str) -> Optional[ADF_NODE]:
        start_match = INLINE_MARKER_RE.search(cell)
        if not start_match:
            return None
        marker_type = start_match.group(1)
        if marker_type not in {"tableCell", "tableHeader"}:
            return None
        attrs = _parse_attrs(start_match.group(2))
        end_marker = f"<!-- /ADF:{marker_type} -->"
        end_pos = cell.find(end_marker, start_match.end())
        if end_pos == -1:
            return None
        inner = cell[start_match.end() : end_pos]
        inner = re.sub(r"\n{2,}", "\n\n", inner.replace("<br/>", "\n"))
        blocks: List[ADF_NODE] = []
        for group in inner.split("\n\n"):
            if group == "":
                blocks.append({"type": "paragraph"})
                continue
            paragraph_nodes: List[ADF_NODE] = []
            lines = group.split("\n")
            for idx, line in enumerate(lines):
                for node in self._parse_inlines(line):
                    if node.get("type") == "extension":
                        if paragraph_nodes:
                            blocks.append(
                                {"type": "paragraph", "content": _merge_text_nodes(paragraph_nodes)}
                            )
                            paragraph_nodes = []
                        blocks.append(node)
                    else:
                        paragraph_nodes.append(node)
                if idx < len(lines) - 1:
                    paragraph_nodes.append({"type": "hardBreak"})
            if paragraph_nodes:
                blocks.append({"type": "paragraph", "content": _merge_text_nodes(paragraph_nodes)})
        if not blocks:
            blocks = [{"type": "paragraph", "content": [_make_text("")]}]
        cell_attrs: Dict[str, Any] = {}
        colwidth = attrs.get("colwidth")
        if colwidth:
            cell_attrs["colwidth"] = [
                _parse_number(item)
                for item in colwidth.split(",")
                if _parse_number(item) is not None
            ]
        colspan = _parse_number(attrs.get("colspan"))
        rowspan = _parse_number(attrs.get("rowspan"))
        background = attrs.get("background")
        has_attrs = bool(colwidth or colspan is not None or rowspan is not None or background)
        if has_attrs:
            cell_attrs["colspan"] = colspan if colspan is not None else 1
            cell_attrs["rowspan"] = rowspan if rowspan is not None else 1
        if colspan is not None:
            cell_attrs["colspan"] = colspan
        if rowspan is not None:
            cell_attrs["rowspan"] = rowspan
        if background:
            cell_attrs["background"] = background
        node: ADF_NODE = {"type": marker_type, "content": blocks}
        if cell_attrs:
            node["attrs"] = cell_attrs
        return node

    def _parse_media_single(self, lines: List[str], attrs: Dict[str, str]) -> ADF_NODE:
        content: List[ADF_NODE] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            start_marker = START_MARKER_RE.match(line)
            if start_marker:
                marker_type = start_marker.group(1)
                marker_attrs = _parse_attrs(start_marker.group(2))
                if marker_type == "media":
                    media_node, i = self._parse_media_block(lines, i, marker_attrs)
                    content.append(media_node)
                    continue
                if marker_type == "caption":
                    caption_node, i = self._parse_caption_block(lines, i)
                    content.append(caption_node)
                    continue
            i += 1
        node: ADF_NODE = {"type": "mediaSingle", "content": content}
        attrs_out: Dict[str, Any] = {}
        if "layout" in attrs:
            attrs_out["layout"] = attrs["layout"]
        width = _parse_number(attrs.get("width"))
        if width is not None:
            attrs_out["width"] = width
        if "widthType" in attrs:
            attrs_out["widthType"] = attrs["widthType"]
        if attrs_out:
            node["attrs"] = attrs_out
        return node

    def _parse_media_group(self, lines: List[str]) -> ADF_NODE:
        content: List[ADF_NODE] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            start_marker = START_MARKER_RE.match(line)
            if start_marker and start_marker.group(1) == "media":
                media_node, i = self._parse_media_block(
                    lines, i, _parse_attrs(start_marker.group(2))
                )
                content.append(media_node)
                continue
            i += 1
        return {"type": "mediaGroup", "content": content}

    def _parse_media_block(
        self, lines: List[str], start: int, attrs: Dict[str, str]
    ) -> Tuple[ADF_NODE, int]:
        i = start + 1
        while i < len(lines):
            if END_MARKER_RE.match(lines[i]) and END_MARKER_RE.match(lines[i]).group(1) == "media":
                break
            i += 1
        end_index = i + 1 if i < len(lines) else i
        node_attrs: Dict[str, Any] = {
            "id": attrs.get("id"),
            "collection": attrs.get("collection"),
            "type": attrs.get("type"),
        }
        node_attrs = {key: value for key, value in node_attrs.items() if value is not None}
        node_attrs = {key: value for key, value in node_attrs.items() if value is not None}
        width = _parse_number(attrs.get("width"))
        height = _parse_number(attrs.get("height"))
        if width is not None:
            node_attrs["width"] = width
        if height is not None:
            node_attrs["height"] = height
        if attrs.get("alt"):
            node_attrs["alt"] = attrs["alt"]
        node: ADF_NODE = {"type": "media", "attrs": node_attrs}
        border_size = _parse_number(attrs.get("borderSize"))
        border_color = attrs.get("borderColor")
        if border_size is not None or border_color:
            node["marks"] = [
                {"type": "border", "attrs": {"size": border_size, "color": border_color}}
            ]
        return node, end_index

    def _parse_caption_block(self, lines: List[str], start: int) -> Tuple[ADF_NODE, int]:
        inner_lines, end_index = self._collect_until_end(lines, start + 1, len(lines), "caption")
        text = "\n".join([line.strip() for line in inner_lines if line.strip()])
        if text.startswith("*") and text.endswith("*") and len(text) > 1:
            text = text[1:-1]
        content = self._parse_inlines(text)
        return {"type": "caption", "content": _merge_text_nodes(content)}, end_index

    def _parse_nested_table(self, lines: List[str], attrs: Dict[str, str]) -> None:
        ref = attrs.get("ref")
        if not ref:
            return
        filtered_lines = [line for line in lines if not line.strip().startswith("<a ")]
        nested_nodes, _ = self._parse_blocks(filtered_lines, 0, len(filtered_lines))
        if nested_nodes and nested_nodes[0].get("type") == "doc":
            self._nested_tables[ref] = nested_nodes[0]

    def _parse_extension_block(self, lines: List[str], attrs: Dict[str, str]) -> Optional[ADF_NODE]:
        extension_type = attrs.get("extensionType")
        extension_key = attrs.get("extensionKey")
        if not extension_type or not extension_key:
            return None
        content_nodes, _ = self._parse_blocks(lines, 0, len(lines))
        doc_node = (
            content_nodes[0] if content_nodes and content_nodes[0].get("type") == "doc" else None
        )
        extension_attrs: Dict[str, Any] = {
            "extensionType": extension_type,
            "extensionKey": extension_key,
            "text": attrs.get("text", ""),
        }
        parameters: Dict[str, Any] = {}
        if doc_node:
            parameters["adf"] = json.dumps(doc_node)
            if extension_key == "nested-table":
                parameters["reason"] = NESTED_TABLE_REASON
        if parameters:
            extension_attrs["parameters"] = parameters
        return {"type": "extension", "attrs": extension_attrs}

    def _parse_inlines(self, text: str) -> List[ADF_NODE]:
        nodes: List[ADF_NODE] = []
        remaining = text
        while remaining:
            match = INLINE_MARKER_RE.search(remaining)
            if not match:
                nodes.extend(self._parse_markdown_spans(remaining, []))
                break
            prefix = remaining[: match.start()]
            if prefix:
                nodes.extend(self._parse_markdown_spans(prefix, []))
            marker_type = match.group(1)
            attrs = _parse_attrs(match.group(2))
            end_marker = f"<!-- /ADF:{marker_type} -->"
            end_pos = remaining.find(end_marker, match.end())
            if end_pos == -1:
                nodes.extend(self._parse_markdown_spans(remaining, []))
                break
            inner = remaining[match.end() : end_pos]
            if marker_type == "text":
                marks = _parse_marks(attrs.get("marks", ""))
                inner_nodes = self._parse_markdown_spans(inner, [])
                nodes.extend(_apply_marks(inner_nodes, marks))
            elif marker_type == "mention":
                mention_attrs: Dict[str, Any] = {}
                if attrs.get("id"):
                    mention_attrs["id"] = attrs.get("id")
                if attrs.get("text"):
                    mention_attrs["text"] = attrs.get("text")
                if attrs.get("userType"):
                    mention_attrs["userType"] = attrs.get("userType")
                if attrs.get("accessLevel"):
                    mention_attrs["accessLevel"] = attrs.get("accessLevel")
                if mention_attrs.get("id"):
                    nodes.append({"type": "mention", "attrs": mention_attrs})
            elif marker_type == "status":
                status_attrs = {"text": attrs.get("text", inner.strip())}
                if attrs.get("color"):
                    status_attrs["color"] = attrs.get("color")
                nodes.append({"type": "status", "attrs": status_attrs})
            elif marker_type == "emoji":
                emoji_attrs: Dict[str, Any] = {}
                if attrs.get("shortName"):
                    emoji_attrs["shortName"] = attrs.get("shortName")
                if attrs.get("id"):
                    emoji_attrs["id"] = attrs.get("id")
                if attrs.get("text") or inner.strip():
                    emoji_attrs["text"] = attrs.get("text", inner.strip())
                nodes.append({"type": "emoji", "attrs": emoji_attrs})
            elif marker_type == "date":
                if attrs.get("timestamp"):
                    nodes.append({"type": "date", "attrs": {"timestamp": attrs.get("timestamp")}})
            elif marker_type == "mediaInline":
                media_inline = self._parse_media_inline(attrs)
                if media_inline:
                    nodes.append(media_inline)
            elif marker_type == "extension":
                extension_attrs: Dict[str, Any] = {}
                if attrs.get("extensionType"):
                    extension_attrs["extensionType"] = attrs.get("extensionType")
                if attrs.get("extensionKey"):
                    extension_attrs["extensionKey"] = attrs.get("extensionKey")
                if attrs.get("text"):
                    extension_attrs["text"] = attrs.get("text")
                if attrs.get("ref"):
                    extension_attrs["parameters"] = {"ref": attrs.get("ref")}
                if extension_attrs.get("extensionKey") == "nested-table":
                    extension_attrs.setdefault("text", "")
                if extension_attrs:
                    nodes.append({"type": "extension", "attrs": extension_attrs})
            remaining = remaining[end_pos + len(end_marker) :]
        return _merge_text_nodes(nodes)

    def _parse_media_inline(self, attrs: Dict[str, str]) -> Optional[ADF_NODE]:
        if not attrs.get("id") or not attrs.get("collection") or not attrs.get("type"):
            return None
        node_attrs: Dict[str, Any] = {
            "id": attrs.get("id"),
            "collection": attrs.get("collection"),
            "type": attrs.get("type"),
        }
        width = _parse_number(attrs.get("width"))
        height = _parse_number(attrs.get("height"))
        if width is not None:
            node_attrs["width"] = width
        if height is not None:
            node_attrs["height"] = height
        if attrs.get("alt"):
            node_attrs["alt"] = attrs.get("alt")
        node: ADF_NODE = {"type": "mediaInline", "attrs": node_attrs}
        border_size = _parse_number(attrs.get("borderSize"))
        border_color = attrs.get("borderColor")
        if border_size is not None or border_color:
            node["marks"] = [
                {"type": "border", "attrs": {"size": border_size, "color": border_color}}
            ]
        return node

    def _parse_markdown_spans(
        self, text: str, active_marks: List[Dict[str, Any]]
    ) -> List[ADF_NODE]:
        nodes: List[ADF_NODE] = []
        remaining = text
        while remaining:
            matches: List[Tuple[str, re.Match]] = []
            for name, regex in [
                ("link", LINK_RE),
                ("code", CODE_RE),
                ("bold_italic", BOLD_ITALIC_RE),
                ("bold", BOLD_RE),
                ("strike", STRIKE_RE),
                ("italic", ITALIC_RE),
            ]:
                match = regex.search(remaining)
                if match:
                    matches.append((name, match))
            if not matches:
                nodes.append(_make_text(remaining, active_marks))
                break
            matches.sort(
                key=lambda item: (
                    item[1].start(),
                    ["link", "code", "bold_italic", "bold", "strike", "italic"].index(item[0]),
                )
            )
            name, match = matches[0]
            if match.start() > 0:
                nodes.append(_make_text(remaining[: match.start()], active_marks))
            if name == "link":
                label = match.group(1)
                url = match.group(2)
                label_nodes = self._parse_markdown_spans(label, active_marks)
                if (
                    label == url
                    and len(label_nodes) == 1
                    and label_nodes[0].get("type") == "text"
                    and not label_nodes[0].get("marks")
                    and not active_marks
                ):
                    nodes.append({"type": "inlineCard", "attrs": {"url": url}})
                else:
                    link_mark = {"type": "link", "attrs": {"href": url}}
                    nodes.extend(_apply_marks(label_nodes, [link_mark]))
            elif name == "code":
                nodes.append(_make_text(match.group(1), active_marks + [{"type": "code"}]))
            elif name == "bold_italic":
                inner = match.group(1)
                nodes.extend(
                    self._parse_markdown_spans(
                        inner, active_marks + [{"type": "strong"}, {"type": "em"}]
                    )
                )
            elif name == "bold":
                inner = match.group(1)
                nodes.extend(self._parse_markdown_spans(inner, active_marks + [{"type": "strong"}]))
            elif name == "strike":
                inner = match.group(1)
                nodes.extend(self._parse_markdown_spans(inner, active_marks + [{"type": "strike"}]))
            elif name == "italic":
                inner = match.group(1)
                nodes.extend(self._parse_markdown_spans(inner, active_marks + [{"type": "em"}]))
            remaining = remaining[match.end() :]
        return _merge_text_nodes(nodes)

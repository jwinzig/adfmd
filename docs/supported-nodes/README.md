# Supported nodes and marks

`adfmd` converts standard Markdown constructs directly. ADF structures or
attributes that Markdown cannot represent are wrapped in HTML comments so they
can be restored when converting the Markdown back to ADF.

For installation and introductory examples, see the [project README](../../README.md).

## ADF to Markdown

### Nodes

| ADF node | Markdown representation |
| --- | --- |
| `doc` | Converted child content; document version is preserved in comments |
| `text` | Text with supported marks applied |
| `paragraph` | Paragraph |
| `heading` | Heading levels 1–6 |
| `blockquote` | Blockquote |
| `codeBlock` | Fenced code block, including its language |
| `bulletList`, `orderedList`, `listItem` | Lists, including nested lists |
| `hardBreak` | Markdown hard break |
| `rule` | Horizontal rule |
| `inlineCard` | Link |
| `emoji` | Unicode text, ADF text, or short name |
| `date` | UTC date and time; timestamp preserved in comments |
| `status`, `mention` | Visible text with ADF attributes preserved in comments |
| `panel` | Blockquote with panel type preserved in comments |
| `table`, `tableRow`, `tableCell`, `tableHeader` | Markdown table with ADF table and cell attributes preserved |
| `extension` | ADF extension metadata in comments; used for nested tables |
| `media`, `mediaSingle`, `mediaGroup`, `mediaInline`, `caption` | `fileId:` links and captions with ADF attributes preserved |
| `expand`, `nestedExpand` | Titled sections with ADF node type and title preserved |

An unregistered ADF node raises `ValueError` rather than silently discarding
content.

### Text marks

| ADF mark | Markdown representation |
| --- | --- |
| `code` | Inline code |
| `em` | Italic |
| `strong` | Bold |
| `strike` | Strikethrough |
| `link` | Link |
| `underline` | Preserved in an HTML comment |
| `subsup` | Preserved in an HTML comment |
| `textColor` | Preserved in an HTML comment |
| `backgroundColor` | Preserved in an HTML comment |

## Markdown to ADF

The Markdown parser converts these constructs to ADF:

- headings (levels 1–6) and paragraphs
- bold, italic, inline code, strikethrough, and links
- bullet and ordered lists, including nesting
- blockquotes and fenced code blocks
- horizontal rules and hard breaks
- tables

ADF comments emitted by `adfmd` restore document metadata and ADF-specific
nodes, including dates, statuses, mentions, emoji, panels, tables, media,
expand sections, extensions, and non-Markdown text marks.

## Round-trip comments

The general comment form is:

```markdown
<!-- ADF:node:attribute="value" -->content<!-- /ADF:node -->
```

For block nodes, the opening and closing comments appear on separate lines.
For example, a document version is retained around its Markdown content:

```markdown
<!-- ADF:doc:version="1" -->
# Example
<!-- /ADF:doc -->
```

Dates, statuses, and mentions keep readable content while retaining ADF
attributes:

```markdown
<!-- ADF:date:timestamp="1686820522000" -->2023-06-15T09:15:22Z<!-- /ADF:date -->

<!-- ADF:status:text="In Progress",color="blue" -->In Progress<!-- /ADF:status -->

<!-- ADF:mention:id="account-id",text="@Example User" -->@Example User<!-- /ADF:mention -->
```

Marks without a native Markdown equivalent are attached to text:

```markdown
<!-- ADF:text:marks="underline,textColor=#0000FF" -->underlined blue text<!-- /ADF:text -->
```

Do not remove or modify these comments if the Markdown needs to convert back to
the original ADF structure.

## Tables

Tables use Markdown pipe syntax. Comments preserve table nodes and attributes
such as column widths, row spans, and column spans:

```markdown
<!-- ADF:table -->
| <!-- ADF:tableHeader -->Name<!-- /ADF:tableHeader --> | <!-- ADF:tableHeader -->Age<!-- /ADF:tableHeader --> |
| --- | --- |
| <!-- ADF:tableCell -->Alice<!-- /ADF:tableCell --> | <!-- ADF:tableCell:rowspan="2" -->30<!-- /ADF:tableCell --> |
| <!-- ADF:tableCell:colspan="2" -->Bob<!-- /ADF:tableCell --> ||
<!-- /ADF:table -->
```

Nested tables use an ADF `extension` marker because Atlassian's new editor does
not allow a table directly inside a table cell.

## Panels and expand sections

Panels render as blockquotes:

```markdown
<!-- ADF:panel:panelType="info" -->
> **INFO**
> This is an informational panel.
<!-- /ADF:panel -->
```

Expand and nested-expand nodes render as titled sections:

```markdown
<!-- ADF:expand:title="Click to expand" -->
**Click to expand**

Content inside the expand section.
<!-- /ADF:expand -->
```

## Media

Media nodes use greppable `[alt text](fileId:id)` links. The surrounding
comments retain the original media type, collection, dimensions, layout, and
other ADF attributes:

```markdown
<!-- ADF:mediaSingle:layout="center",width="584",widthType="pixel" -->
<!-- ADF:media:id="file-id",collection="content-id",type="file",width="607",height="426",alt="image.png" -->
[image.png](fileId:file-id)
<!-- /ADF:media -->
<!-- ADF:caption -->
*Image caption*
<!-- /ADF:caption -->
<!-- /ADF:mediaSingle -->
```

After downloading an attachment, replace `fileId:<id>` with its local path if
the Markdown should reference the downloaded file:

```bash
sed -i "s|fileId:$FILE_ID|media/$FILE_ID.png|g" "$MARKDOWN_FILE"
```

The attachment download URL can be obtained from the
[Confluence attachments API][attachments].

[attachments]: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-attachment/

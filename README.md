# adfmd

Bidirectional converter between Atlassian Document Format (ADF) and Markdown.

## Installation

Requires Python 3.10 or newer. There are no third-party runtime dependencies.

```bash
pip install .
```

This installs the `adfmd` library and the `adfmd` command-line tool:

```bash
adfmd input.json
adfmd input.json -o output.md
adfmd --version
```

### Development

```bash
pip install -e ".[dev]"
pytest
```

The `[dev]` extra installs pytest plus the tools used to build and check the package. `requirements.txt` installs the same extra for convenience.

## ADF to Markdown Conversion

Supported Atlassian Document Format (ADF) elements for conversion to Markdown:

### Node Types

| ADF Node Type | Markdown Output Type                                                                            |
| ------------- | ----------------------------------------------------------------------------------------------- |
| doc           | Document root (converts children, version preserved via HTML comments if present)               |
| text          | Text with formatting marks (see text marks)                                                     |
| paragraph     | Paragraph text                                                                                  |
| blockquote    | Blockquote (`> ` prefix on each line)                                                           |
| codeBlock     | Code block (`language\ncode\n`)                                                                 |
| emoji         | Emoji (Unicode character or shortName as fallback)                                              |
| panel         | Panel content in blockquote - Node type preserved via HTML comments (see below)                 |
| heading       | Headings (`#` through `######`) incl. trailing newlines (`\n\n`)                                |
| bulletList    | Bullet list (`- ` prefix, with nesting)                                                         |
| orderedList   | Ordered list (numbered items, with nesting)                                                     |
| listItem      | List item (lines under `-`, `*`, or `1.`)                                                       |
| hardBreak     | Line break (`  \n` at the end of line)                                                          |
| rule          | Horizontal rule (`---`)                                                                         |
| inlineCard    | Link (`[URL](URL)`)                                                                             |
| date          | UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`) - Node type preserved via HTML comments (see below)      |
| status        | Status text - Node type preserved via HTML comments (see below)                                 |
| mention       | User mention - Node type preserved via HTML comments (see below)                                |
| table         | Markdown table with pipe separators (`\|`) - Attributes preserved via HTML comments (see below) |
| tableRow      | Markdown table row                                                                              |
| tableCell     | Markdown table cell                                                                             |
| tableHeader   | Markdown table header cell                                                                      |
| media         | Media link (`[alt-text](fileId:id)`) - Node type preserved via HTML comments (see below)        |
| mediaSingle   | Single media item with layout - Node type preserved via HTML comments (see below)               |
| mediaGroup    | Group of media items - Node type preserved via HTML comments (see below)                        |
| mediaInline   | Inline media item - Node type preserved via HTML comments (see below)                           |
| expand        | Expandable section with title - Node type preserved via HTML comments (see below)                |
| nestedExpand  | Nested expandable section with title - Node type preserved via HTML comments (see below)         |

### Text Marks

| Mark Type       | Markdown Output Type                    |
| --------------- | --------------------------------------- |
| code            | Inline code (`` `code` ``)              |
| em              | Italic (`*text*`)                       |
| strong          | Bold (`**text**`)                       |
| strike          | Strikethrough (`~~text~~`)              |
| link            | Link (`[text](URL)`)                    |
| underline       | Preserved via HTML comments (see below) |
| subsup          | Preserved via HTML comments (see below) |
| textColor       | Preserved via HTML comments (see below) |
| backgroundColor | Preserved via HTML comments (see below) |

### HTML Comments for Unsupported ADF Elements

ADF elements (nodes and marks) that are not supported by Markdown are marked with HTML comments to enable lossless round-trip conversion.

**Format:**

```
<!-- ADF:{node}:{attr}="{value}" -->{content}<!-- /ADF:{node} -->
```

**Examples:**

- Date node:

  ```
  <!-- ADF:date:timestamp="1686820522000" -->2023-06-15T09:15:22Z<!-- /ADF:date -->
  ```

- Text with unsupported marks:

  ```
  <!-- ADF:text:marks="underline,textColor=#0000FF" -->underlined blue text<!-- /ADF:text -->
  ```

- Doc node with version:

  ```
  <!-- ADF:doc:version="1" -->
  {content}
  <!-- /ADF:doc -->
  ```

- Doc node without version:

  ```
  <!-- ADF:doc -->
  {content}
  <!-- /ADF:doc -->
  ```

- Status node:

  ```
  <!-- ADF:status:text="In Progress",color="blue" -->In Progress<!-- /ADF:status -->
  ```

- Mention node:

  ```
  <!-- ADF:mention:id="ABCDE-ABCDE-ABCDE-ABCDE",text="@Bradley Ayers" -->@Bradley Ayers<!-- /ADF:mention -->
  ```

  With additional attributes:

  ```
  <!-- ADF:mention:id="FGHIJ-FGHIJ-FGHIJ-FGHIJ" -->@mention(FGHIJ-FGHIJ-FGHIJ-FGHIJ)<!-- /ADF:mention -->
  ```

- Table node:

  Tables are converted to Markdown table format with pipe separators. The first row automatically gets a separator row.

  ```
  <!-- ADF:table -->
  | <!-- ADF:tableHeader -->Name<!-- /ADF:tableHeader --> | <!-- ADF:tableHeader -->Age<!-- /ADF:tableHeader --> |
  | --- | --- | --- |
  | <!-- ADF:tableCell -->Alice<!-- /ADF:tableCell --> | <!-- ADF:tableCell -->30<!-- /ADF:tableCell --> |
  | <!-- ADF:tableCell -->Bob<!-- /ADF:tableCell --> | <!-- ADF:tableCell -->25<!-- /ADF:tableCell --> |
  <!-- /ADF:table -->
  ```

  With cells spanning multiple columns/rows:

  ```
  <!-- ADF:table -->
  | <!-- ADF:tableHeader:colwidth="225.0" -->**Name**<!-- /ADF:tableHeader --> | <!-- ADF:tableHeader:colwidth="349.0" -->**Age**<!-- /ADF:tableHeader --> |
  | --- | --- |
  | <!-- ADF:tableCell:colwidth="225.0" -->Alice<!-- /ADF:tableCell --> | <!-- ADF:tableCell:colwidth="349.0",rowspan="2" -->25<!-- /ADF:tableCell --> |
  | <!-- ADF:tableCell:colwidth="225.0" -->Bob<!-- /ADF:tableCell --> ||
  | <!-- ADF:tableCell:colwidth="225.0,349.0",colspan="2" -->Eve<!-- /ADF:tableCell --> ||
  <!-- /ADF:table -->
  ```

- Panel node:

  ```
  <!-- ADF:panel:panelType="info" -->
  > **INFO**
  > This is an informational panel.
  <!-- /ADF:panel -->
  ```

- Media nodes:

  Media nodes are converted to greppable markdown links with the format `[alt-text](fileId:id)` to enable easy replacement with local file paths.

  **mediaSingle node:**

  ```
  <!-- ADF:mediaSingle:layout="center",width="584",widthType="pixel" -->
  <!-- ADF:media:id="9aa8ffab-ed40-49b8-995b-29726c305374",collection="contentId-2719746",type="file",width="607",height="426",alt="image.png" -->
  [image.png](fileId:9aa8ffab-ed40-49b8-995b-29726c305374)
  <!-- /ADF:media -->
  <!-- ADF:caption -->
  *Image caption*
  <!-- /ADF:caption -->
  <!-- /ADF:mediaSingle -->
  ```

  **mediaGroup node:**

  ```
  <!-- ADF:mediaGroup -->
  <!-- ADF:media:id="file-id-1",collection="contentId-2719746",type="file",alt="image1.png" -->
  [image1.png](fileId:file-id-1)
  <!-- /ADF:media -->
  <!-- ADF:media:id="file-id-2",collection="contentId-2719746",type="file",alt="image2.png" -->
  [image2.png](fileId:file-id-2)
  <!-- /ADF:media -->
  <!-- /ADF:mediaGroup -->
  ```

  **mediaInline node:**

  ```
  Text before <!-- ADF:mediaInline:id="9aa8ffab-ed40-49b8-995b-29726c305374",collection="contentId-2719746",type="image",width="607",height="426",alt="image.png" -->[image.png](fileId:9aa8ffab-ed40-49b8-995b-29726c305374)<!-- /ADF:mediaInline --> text after
  ```

  **expand node:**
  
  ```
  <!-- ADF:expand:title="Click to expand" -->
  **Click to expand**
  
  This is the content inside the expand section.
  <!-- /ADF:expand -->
  ```

  **nestedExpand node:**
  
  ```
  <!-- ADF:nestedExpand:title="Nested Section" -->
  **Nested Section**
  
  This is the content inside the nested expand section.
  <!-- /ADF:nestedExpand -->
  ```

  **Retrieving and Replacing Media Files:**

  Media files are referenced using `fileId:<id>` links in the markdown output.
  These identifiers can be used to retrieve the media files and replace the links with their local
  filepath.

  Example:

  ```bash
  #!/bin/bash
  DOMAIN="your-domain"
  EMAIL="your-email"
  API_TOKEN="your-api-token"
  FILE_ID="your-file-id"
  MD_FILE="your-md-file.md"

  # Get download URL
  download_path=$(curl \
    -X GET \
    "https://$DOMAIN.atlassian.net/wiki/api/v2/attachments" \
    -u "$EMAIL:$API_TOKEN" \
    -H 'Accept: application/json' | \
    jq ".results[] | select(.fileId == \"$FILE_ID\") | ._links.download")
  download_url="https://$DOMAIN.atlassian.net/wiki${download_path//\"}"

  # Download the file
  curl -L -X GET \
    "$download_url" \
    -u "$EMAIL:$API_TOKEN" \
    -o "media/$FILE_ID.png"

  # Replace the media link with the local file path
  sed -i "s|fileId:$FILE_ID|media/$FILE_ID.png|g" "$MD_FILE"
  ```

### Missing ADF Nodes

\-

## Markdown to ADF Conversion

The converter supports bidirectional conversion, enabling lossless round-trip conversion between Markdown and ADF formats. All ADF node types and marks that are preserved via HTML comments in the Markdown output can be converted back to their original ADF structure.

### Supported Markdown Elements

All standard Markdown elements are supported for conversion to ADF:

- **Headings** (`#` through `######`) - Converted to ADF heading nodes with appropriate level
- **Paragraphs** - Converted to ADF paragraph nodes
- **Bold** (`**text**`) - Converted to strong mark
- **Italic** (`*text*`) - Converted to em mark  
- **Inline code** (`` `code` ``) - Converted to code mark
- **Strikethrough** (`~~text~~`) - Converted to strike mark
- **Links** (`[text](url)`) - Converted to link mark or inlineCard node
- **Bullet lists** (`-` prefix) - Converted to bulletList with listItem nodes
- **Ordered lists** (numbered items) - Converted to orderedList with listItem nodes
- **Blockquotes** (`>` prefix) - Converted to blockquote nodes
- **Code blocks** (triple backticks) - Converted to codeBlock nodes
- **Horizontal rules** (`---`) - Converted to rule nodes
- **Hard breaks** (two spaces at line end) - Converted to hardBreak nodes

### HTML Comment Preservation

All ADF-specific elements that were preserved via HTML comments during ADF to Markdown conversion are fully restored during Markdown to ADF conversion:

- **Date nodes** - Restored with timestamp attribute
- **Status nodes** - Restored with text and color attributes
- **Mention nodes** - Restored with id, text, userType, and accessLevel attributes
- **Emoji nodes** - Restored with shortName, id, and text attributes
- **Panel nodes** - Restored with panelType attribute
- **Table attributes** - Column widths, colspan, rowspan, and other table attributes
- **Media nodes** - Media, mediaSingle, mediaGroup, and mediaInline with all attributes
- **Expand nodes** - Expand and nestedExpand sections with titles
- **Extension nodes** - Including nested tables
- **Text marks** - Underline, textColor, backgroundColor, and subsup marks
- **Doc nodes** - Document root with version information

### Usage Example

```python
from adfmd import ADFMD, from_markdown, to_markdown

# Convert Markdown to ADF
converter = ADFMD()
markdown_text = """
# Hello World

This is a **bold** paragraph with *italic* text.

- Item 1
- Item 2
"""

adf_json = converter.from_markdown(markdown_text)

# Or use the convenience function
adf_json = from_markdown(markdown_text)

# Convert back to Markdown
markdown_output = to_markdown(adf_json)
```

### Round-Trip Conversion

The converter is designed for lossless round-trip conversion. When you convert from ADF to Markdown and back to ADF, all information is preserved:

```python
from adfmd import to_markdown, from_markdown

# Original ADF document
original_adf = {
    "type": "doc",
    "version": 1,
    "content": [
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Hello ", "marks": []},
                {"type": "text", "text": "World", "marks": [{"type": "strong"}]}
            ]
        }
    ]
}

# Convert to Markdown and back
markdown = to_markdown(original_adf)
restored_adf = from_markdown(markdown)

# restored_adf matches original_adf
assert restored_adf == original_adf
```

## References

- [Markdown Basic Syntax](https://www.markdownguide.org/basic-syntax/)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)

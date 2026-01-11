# adfmd

Bidirectional converter between Atlassian Document Format (ADF) and Markdown.

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

To be implemented.

## References

- [Markdown Basic Syntax](https://www.markdownguide.org/basic-syntax/)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)

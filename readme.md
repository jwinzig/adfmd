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
| codeBlock     | Code block (```language\ncode\n```)                                                             |
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

### Missing ADF Nodes

- emoji
- expand
- media
- mediaGroup
- mediaSingle
- nestedExpand
- panel

## Markdown to ADF Conversion

To be implemented.

## References

- [Markdown Basic Syntax](https://www.markdownguide.org/basic-syntax/)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)

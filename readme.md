# adfmd

Bidirectional converter between Atlassian Document Format (ADF) and Markdown.

## ADF to Markdown Conversion

Supported Atlassian Document Format (ADF) elements for conversion to Markdown:

### Node Types

| ADF Node Type  | Markdown Output Type                                             |
| -------------- | ---------------------------------------------------------------- |
| text           | Text with formatting marks (see text marks)                      |
| paragraph      | Paragraph text                                                   |
| heading        | Headings (`#` through `######`) incl. trailing newlines (`\n\n`) |
| bulletList     | Bullet list (`- ` prefix, with nesting)                         |
| orderedList    | Ordered list (numbered items, with nesting)                      |
| listItem       | List item (lines under `-`, `*`, or `1.`)                        |
| hardBreak      | Line break (`  \n` at the end of line)                           |
| rule           | Horizontal rule (`---`)                                          |
| InlineCardNode | Link (`[URL](URL)`)                                              |

### Text Marks

| Mark Type | Markdown Output Type       |
| --------- | -------------------------- |
| code      | Inline code (`` `code` ``) |
| em        | Italic (`*text*`)          |
| strong    | Bold (`**text**`)          |
| strike    | Strikethrough (`~~text~~`) |
| link      | Link (`[text](URL)`)       |

## Markdown to ADF Conversion

To be implemented.

## References

- [Markdown Basic Syntax](https://www.markdownguide.org/basic-syntax/)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)

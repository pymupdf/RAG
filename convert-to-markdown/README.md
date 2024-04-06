# PDF Page Conversion to Markdown Text
This script accepts a PDF document filename and converts it to a text file in Markdown format, compatible with the GitHub standard.
It must be invoked with the filename like this:

```python
$ python to_markdown.py input.pdf [-pages PAGES]
```

The "PAGES" parameter is a string (containing no spaces) of 1-based page numbers to consider for this conversion. Multiple page numbers and page number ranges may be specified if separated by a comma. Each item is either a single page number or a number range of the form "m-n". Use "N" as a symbolic value to specify the last page number.

The example: `"-pages 2-15,40,43-N"` will convert pages from 2 through 15, 40 and from 43 to the end of the file.

The script will produce a markdown text file called "input.md".

Pages in the produced output will separated by a line of 10 hyphens.

The text on each page will be sorted in Western reading order. Any table will be included in the text in markdown format as well.

# Use in some other script
Markdown conversion can also be invoked from within any script like this:

```python
import fitz
import pathlib
from to_markdown import to_markdown

doc = fitz.open("input.pdf")
page_list = [ list of 0-based page numbers ]
md_text = to_markdown(doc, pages=page_list)

# now for instance store the text in a file
pathlib.Path(f"{doc.name.replace('.pdf', '.md')}").write_text(md_text)
```

# Dependencies
PyMuPDF v1.24.0 or later.

# Copyright and License
Copyright: 2024 Artifex Software, Inc.
License: GNU Affero GPL 3.0
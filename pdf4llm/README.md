# Using PyMuPDF as Data Feeder in LLM / RAG Applications

This package converts the pages of a PDF to text in Markdown format using [PyMuPDF](https://pypi.org/project/PyMuPDF/).

Standard text and tables are detected, brought in the right reading sequence and then together converted to GitHub-compatible Markdown text.

Header lines are identified via the font size and appropriately prefixed with one or more '#' tags.

Bold, italic, mono-spaced text and code blocks are detected and formatted accordingly. Similar applies to ordered and unordered lists.

By default, all document pages are processed. If desired, a subset of pages can be specified by providing a list of 0-based page numbers.


# Installation

```bash
$ pip install -U pdf4llm
```

Then in your script do

```python
import pdf4llm

md_text = pdf4llm.to_markdown("input.pdf", pages=None)

# now work with the markdown text, e.g. store as a UTF8-encoded file
import pathlib
pathlib.Path("output.md").write_bytes(md_text.encode())
```

Instead of the filename string as above, one can also provide a PyMuPDF `Document`. The `pages` parameter may be a list of 0-based page numbers or `None` (the default) whch includes all pages.
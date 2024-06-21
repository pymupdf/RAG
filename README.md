# Using PyMuPDF as Data Feeder in LLM / RAG Applications

This package converts the pages of a PDF to text in Markdown format using [PyMuPDF](https://pypi.org/project/PyMuPDF/).

Standard text and tables are detected, brought in the right reading sequence and then together converted to
GitHub-compatible Markdown text.

Header lines are identified via the font size and appropriately prefixed with one or more '#' tags.

Bold, italic, mono-spaced text and code blocks are detected and formatted accordingly. Similar applies to ordered and
unordered lists.

By default, all document pages are processed. If desired, a subset of pages can be specified by providing a list of
0-based page numbers.

# Installation

```bash
$ pip install -U pymupdf4llm
```

> This command will automatically install [PyMuPDF](https://github.com/pymupdf/PyMuPDF) if required.

Then in your script do:

```python
from pymupdf4llm import process_document, join_chunks

md_text = join_chunks(process_document("input.pdf"))

# now work with the markdown text, e.g. store as a UTF8-encoded file
import pathlib

pathlib.Path("output.md").write_bytes(md_text.encode())
```

Instead of the filename string as above, one can also provide a PyMuPDF `Document`. By default, all pages in the PDF
will be processed. If desired, the parameter `pages=[...]` can be used to provide a list of zero-based page numbers to
consider.

As a first example for directly supporting LLM / RAG consumers, this version can output **LlamaIndex documents**:

```python
from pymupdf4llm.llama import LlamaMarkdownReader

md_read = LlamaMarkdownReader()
data = md_read.load_data("input.pdf")

# The result 'data' is of type List[LlamaIndexDocument]
# Every list item contains metadata and the markdown text of 1 page.
```

* A LlamaIndex document essentially corresponds to Python dictionary, where the markdown text of the page is one of the
  dictionary values. For instance the text of the first page is the the value of `data[0].to_dict().["text"]`.
* For details, please consult LlamaIndex documentation.
* Upon creation of the `LlamaMarkdownReader` all necessary LlamaIndex-related imports are executed. Required related
  package installations must have been done independently and will not be checked during pymupdf4llm installation.

# Document Support

While PDF is by far the most important document format worldwide, it is worthwhile mentioning that all examples and
helper scripts work in the same way and **_without change_**
for [all supported file types](https://pymupdf.readthedocs.io/en/latest/how-to-open-a-file.html#supported-file-types).

So for an XPS document or an eBook, simply provide the filename for instance as `"input.mobi"` and everything else will
work as before.

# About PyMuPDF

**PyMuPDF** adds **Python** bindings and abstractions to [MuPDF](https://mupdf.com/), a lightweight **PDF**, **XPS**,
and **eBook** viewer, renderer, and toolkit. Both **PyMuPDF** and **MuPDF** are maintained and developed
by [Artifex Software, Inc](https://artifex.com).

PyMuPDF's homepage is located on [GitHub](https://github.com/pymupdf/PyMuPDF).

# Community

Join us on **Discord** here: [#pymupdf](https://discord.gg/TSpYGBW4eq).

# License and Copyright

**PyMuPDF** is available under [open-source AGPL](https://www.gnu.org/licenses/agpl-3.0.html) and commercial license
agreements. If you determine you cannot meet the requirements of the **AGPL**, please
contact [Artifex](https://artifex.com/contact/pymupdf-inquiry.php) for more information regarding a commercial license.

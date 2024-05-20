# Using PyMuPDF in an RAG (Retrieval-Augmented Generation) Chatbot Environment

This repository contains examples showing how PyMuPDF can be used as a data feed for RAG-based chatbots.

Examples include scripts that start chatbots - either as simple CLI programs in REPL mode or browser-based GUIs.
Chatbot scripts follow this general structure:

1. **Extract Text**: Use PyMuPDF to extract text from one or more pages from one or more PDFs. Depending on the specific requirement this may be all text or only text contained in tables, the Table of Contents, etc.
This will generally be implemented as one or more Python functions called by any of the following events - which implement the actual chatbot functionality.
2. **Indexing the Extracted Text**: Index the extracted text for efficient retrieval. This index will act as the knowledge base for the chatbot.
3. **Query Processing**: When a user asks a question, process the query to determine the key information needed for a response.
4. **Retrieving Relevant Information**: Search your indexed knowledge base for the most relevant pieces of information related to the user's query.
5. **Generating a Response**: Use a generative model to generate a response based on the retrieved information.

# Installation

The Python package on PyPI [pymupdf4llm](https://pypi.org/project/pymupdf4llm/) (there also is an alias [pdf4llm](https://pypi.org/project/pdf4llm/)) is capable of converting PDF pages into **_text strings in Markdown format_** (GitHub compatible). This includes **standard text** as well as **table-based text** in a consistent and integrated view - a feature particularly important in RAG settings.

```bash
$ pip install -U pymupdf4llm
```

> This command will automatically install [PyMuPDF](https://github.com/pymupdf/PyMuPDF) if required.

Then in your script do

```python
import pymupdf4llm

md_text = pymupdf4llm.to_markdown("input.pdf")

# now work with the markdown text, e.g. store as a UTF8-encoded file
import pathlib
pathlib.Path("output.md").write_bytes(md_text.encode())
```

Instead of the filename string as above, one can also provide a PyMuPDF `Document`. By default, all pages in the PDF will be processed. If desired, the parameter `pages=[...]` can be used to provide a list of zero-based page numbers to consider.

Markdown text creation now also processes **multi-column pages**.

To create small **chunks of text** - as opposed to generating one large string for the whole document - the new (v0.0.2) option `page_chunks=True` can be used. The result of `.to_markdown("input.pdf", page_chunks=True)` will be a list of Python dictionaries, one for each page.

Also new in version 0.0.2 is the optional **extraction of images** and vector graphics: use of parameter `write_images=True`. The will store PNG images in the document's folder, and the Markdown text will appropriately refer to them. The images are named like `"input.pdf-page_number-index.png"`.

# Document Support

While PDF is by far the most important document format worldwide, it is worthwhile mentioning that all examples and helper scripts work in the same way and **_without change_** for [all supported file types](https://pymupdf.readthedocs.io/en/latest/how-to-open-a-file.html#supported-file-types).

So for an XPS document or an eBook, simply provide the filename for instance as `"input.mobi"` and everything else will work as before.


# About PyMuPDF
**PyMuPDF** adds **Python** bindings and abstractions to [MuPDF](https://mupdf.com/), a lightweight **PDF**, **XPS**, and **eBook** viewer, renderer, and toolkit. Both **PyMuPDF** and **MuPDF** are maintained and developed by [Artifex Software, Inc](https://artifex.com).

PyMuPDF's homepage is located on [GitHub](https://github.com/pymupdf/PyMuPDF).

# Community
Join us on **Discord** here: [#pymupdf](https://discord.gg/TSpYGBW4eq).

# License and Copyright
**PyMuPDF** is available under [open-source AGPL](https://www.gnu.org/licenses/agpl-3.0.html) and commercial license agreements. If you determine you cannot meet the requirements of the **AGPL**, please contact [Artifex](https://artifex.com/contact/pymupdf-inquiry.php) for more information regarding a commercial license.


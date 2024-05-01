

PyMuPDF4LLM
===========================================================================

**PyMuPDF4LLM** is based on `PyMuPDF <https://pymupdf.readthedocs.io>`_ - the fastest **PDF** extraction tool for **Python**.

This documentation explains how to use the **Python PDF4LLM** package as well as providing links to other related **RAG** & **LLM** resources for **PyMuPDF**.



- This package converts the pages of a **PDF** to text in **Markdown** format using **PyMuPDF**.

- Standard text and tables are detected, brought in the right reading sequence and then together converted to **GitHub**-compatible **Markdown** text.

- Header lines are identified via the font size and appropriately prefixed with one or more `#` tags.

- Bold, italic, mono-spaced text and code blocks are detected and formatted accordingly. Similar applies to ordered and unordered lists.

- By default, all document pages are processed. If desired, a subset of pages can be specified by providing a list of `0`-based page numbers.


Using in LLM / RAG Applications
--------------------------------------------------------------

To retrieve your document content in **Markdown** simply install the package and then use a couple of lines of **Python** code to get results.


Install the package via **pip** with:


.. code-block:: bash

    pip install pymupdf4llm


Then in your **Python** script do:


.. code-block:: python

    import pymupdf4llm
    md_text = pymupdf4llm.to_markdown("input.pdf", pages=None)



.. note::

    Instead of the filename string as above, one can also provide a `PyMuPDF Document`_. The `pages` parameter may be a list of `0`-based page numbers or `None` (the default) whch includes all pages.


If you want to store your **Markdown** file, e.g. store as a UTF8-encoded file, then do:


.. code-block:: python

    import pathlib
    pathlib.Path("output.md").write_bytes(md_text.encode())


Further Resources
-------------------


- `PyMuPDF on Github <https://github.com/pymupdf/PyMuPDF>`_


Sample code
~~~~~~~~~~~~~~~

- `Command line RAG Chatbot with PyMuPDF <https://github.com/pymupdf/RAG/tree/main/country-capitals>`_
- `Example of a Browser Application using Langchain and PyMuPDF <https://github.com/pymupdf/RAG/tree/main/GUI>`_


Blogs
~~~~~~~~~~~~~~

- `RAG/LLM and PDF: Enhanced Text Extraction <https://artifex.com/blog/rag-llm-and-pdf-enhanced-text-extraction>`_
- `Creating a RAG Chatbot with ChatGPT and PyMuPDF <https://artifex.com/blog/creating-a-rag-chatbot-with-chatgpt-and-pymupdf>`_
- `Building a RAG Chatbot GUI with the ChatGPT API and PyMuPDF <https://artifex.com/blog/building-a-rag-chatbot-gui-with-the-chatgpt-api-and-pymupdf>`_
- `RAG/LLM and PDF: Conversion to Markdown Text with PyMuPDF <https://artifex.com/blog/rag-llm-and-pdf-conversion-to-markdown-text-with-pymupdf>`_



.. include:: footer.rst




.. _PyMuPDF Document: https://pymupdf.readthedocs.io/en/latest/document.html



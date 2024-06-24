.. include:: header.rst



PyMuPDF4LLM
===========================================================================

**PyMuPDF4LLM** is based on `PyMuPDF <https://pymupdf.readthedocs.io>`_ - the fastest **PDF** extraction tool for **Python**.

This documentation explains how to use the **PyMuPDF4LLM** package as well as providing links to other related **RAG** & **LLM** resources for **PyMuPDF**.

Features
-------------------------------

    - Support for multi-column pages
    - Support for image and vector graphics extraction (and inclusion of references in the MD text)
    - Support for page chunking output.
    - Direct support for output as :ref:`LlamaIndex Documents <extracting_as_llamaindex>`.


Document support
~~~~~~~~~~~~~~~~~~~

**PyMuPDF4LLM** supports the following file types for text extraction:


.. list-table::
   :header-rows: 0

   * - **PDF**
     - **DOCX**
     - **XLSX**
     - **PPTX**
     - **HWPX**
   * - .. image:: images/icons/icon-pdf.svg
          :width: 40
          :height: 40
     - .. image:: images/icons/icon-docx.svg
          :width: 40
          :height: 40
     - .. image:: images/icons/icon-xlsx.svg
          :width: 40
          :height: 40
     - .. image:: images/icons/icon-pptx.svg
          :width: 40
          :height: 40
     - .. image:: images/icons/icon-hangul.svg
          :width: 40
          :height: 40
   * - **XPS**
     - **EPUB**
     - **MOBI**
     - **FB2**
     - **CBZ**
   * - .. image:: images/icons/icon-xps.svg
          :width: 40
          :height: 40
     - .. image:: images/icons/icon-epub.svg
          :width: 40
          :height: 40
     - .. image:: images/icons/icon-mobi.svg
          :width: 40
          :height: 40
     - .. image:: images/icons/icon-fb2.svg
          :width: 40
          :height: 40
     - .. image:: images/icons/icon-cbz.svg
          :width: 40
          :height: 40


- This package converts the pages of a file to text in **Markdown** format using **PyMuPDF**.

- Standard text and tables are detected, brought in the right reading sequence and then together converted to **GitHub**-compatible **Markdown** text.

- Header lines are identified via the font size and appropriately prefixed with one or more `#` tags.

- Bold, italic, mono-spaced text and code blocks are detected and formatted accordingly. Similar applies to ordered and unordered lists.

- By default, all document pages are processed. If desired, a subset of pages can be specified by providing a list of `0`-based page numbers.


Installation
----------------


Install the package via **pip** with:


.. code-block:: bash

    pip install pymupdf4llm



Using in LLM / RAG Applications
--------------------------------------------------------------

**PyMuPDF4LLM** is aimed to make it easier to extract **PDF** content in the format you need for **LLM** & **RAG** environments. It supports :ref:`Markdown extraction <extracting_as_md>` as well as :ref:`LlamaIndex document output <extracting_as_llamaindex>`.



.. _extracting_as_md:

Extracting a file as **Markdown**
--------------------------------------------------------------

To retrieve your document content in **Markdown** simply install the package and then use a couple of lines of **Python** code to get results.



Then in your **Python** script do:


.. code-block:: python

    import pymupdf4llm
    md_text = pymupdf4llm.to_markdown("input.pdf")


.. note::

    Instead of the filename string as above, one can also provide a `PyMuPDF Document`_. A second parameter may be a list of `0`-based page numbers, e.g. `[0,1]` would just select the first and second pages of the document.


If you want to store your **Markdown** file, e.g. store as a UTF8-encoded file, then do:


.. code-block:: python

    import pathlib
    pathlib.Path("output.md").write_bytes(md_text.encode())



.. _extracting_as_llamaindex:

Extracting a file as a **LlamaIndex** document
--------------------------------------------------------------

**PyMuPDF4LLM** supports direct conversion to a **LLamaIndex** document. A document is first converted into **Markdown** format and then a **LlamaIndex** document is returned as follows:



.. code-block:: python

    import pymupdf4llm
    llama_reader = pymupdf4llm.LlamaMarkdownReader()
    llama_docs = llama_reader.load_data("input.pdf")


API
-------

See :doc:`api`.


Change Log
------------

See :doc:`changes`.


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



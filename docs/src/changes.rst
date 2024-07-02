.. include:: header.rst


Change Log
===========================================================================

Changes in version 0.0.8
--------------------------

Fixes:
~~~~~~~

* `65 <https://github.com/pymupdf/RAG/issues/65>`_ Fix typo in `pymupdf_rag.py`.


Changes in version 0.0.7
--------------------------

Fixes:
~~~~~~~

* `54 <https://github.com/pymupdf/RAG/issues/54>`_ "Mistakes in orchestrating sentences". Additional fix: text extraction no longer uses the TEXT_DEHYPHNATE flag bit.

Improvements:
~~~~~~~~~~~~~~~~

* Improved the algorithm dealing with vector graphics. Vector graphics are now more reliably classified as irrelevant when they are simple background for text (quite often the case for code snippets).


Changes in version 0.0.6
--------------------------

Fixes:
~~~~~~~

* `55 <https://github.com/pymupdf/RAG/issues/55>`_ "Bug in helpers/multi_column.py - IndexError: list index out of range"
* `54 <https://github.com/pymupdf/RAG/issues/54>`_ "Mistakes in orchestrating sentences"
* `52 <https://github.com/pymupdf/RAG/issues/52>`_ "Chunking of text files"
* Partial fix for `41 <https://github.com/pymupdf/RAG/issues/41>`_ / `40 <https://github.com/pymupdf/RAG/issues/40>`_. Improved page column detection, but still no silver bullet for overly complex page layouts.

Improvements:
~~~~~~~~~~~~~~~~

* New parameter `dpi` to specify the resolution of images.
* New parameters `page_width` / `page_height` for easily processing reflowable documents (Text, Office, e-books).
* New parameter `graphics_limit` to avoid spending runtimes for value-less content.
* New parameter `table_strategy` to directly control the table detection strategy.

.. include:: footer.rst


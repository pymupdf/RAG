.. include:: header.rst


Change Log
===========================================================================

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


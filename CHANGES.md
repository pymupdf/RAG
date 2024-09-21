# Change Log


## Changes in version 0.0.17

### Fixes:


* [147](https://github.com/pymupdf/RAG/issues/147) - Error when page contains nothing but a table.
* [81](https://github.com/pymupdf/RAG/issues/81) - Issues with bullet points in PDFs.
* [78](https://github.com/pymupdf/RAG/issues/78) - multi column pdf file text extraction.


## Changes in version 0.0.15

### Fixes:


* [138](https://github.com/pymupdf/RAG/issues/138) - Table is not extracted and some text order was wrong.
* [135](https://github.com/pymupdf/RAG/issues/135) - Problem with multiple columns in simple text.
* [134](https://github.com/pymupdf/RAG/issues/134) - Exclude images based on size threshold parameter.
* [132](https://github.com/pymupdf/RAG/issues/132) - Optionally embed images as base64 string.
* [128](https://github.com/pymupdf/RAG/issues/128) - Enhanced image embedding format.


### Improvements

* New parameter `embed_images` (bool) **embeds** images and vector graphics in the markdown text as base64-encoded strings. Ignores `write_images` and `image_path` parameters.
* New parameter `image_size_limit` which is a float between 0 and 1, default is 0.05 (5%). Causes images to be ignored if their width or height values are smaller than the corresponding fraction of the page's width or height.
* The algorithm has been improved which determins the sequence of the text rectangles on multi-column pages.
* Change of the header identification algorithm: If more than six header levels are required for a document, then all text with a font size larger than body text is assumed to be a header of level 6 (i.e. HTML "h6" = "###### ").


## Changes in version 0.0.13


### Fixes

* [112](https://github.com/pymupdf/RAG/issues/112) - Invalid bandwriter header dimensions/setup.


### Improvements

* New parameter `ignore_code` suppresses special formatting of text in mono-spaced fonts.
* New parameter `extract_words` enforces `page_chunks=True` and adds a "words" list to each page dictionary.


## Changes in version 0.0.11


### Fixes

* [90](https://github.com/pymupdf/RAG/issues/90) - 'Quad' object has no attribute 'tl'.
* [88](https://github.com/pymupdf/RAG/issues/88) - Bug in `is_significant` function.


### Improvements

* Extended the list of known bullet point characters.


## Changes in version 0.0.10


### Fixes

* [73](https://github.com/pymupdf/RAG/issues/73) - bug in `to_markdown` internal function.
* [74](https://github.com/pymupdf/RAG/issues/74) - minimum area for images & vector graphics.
* [75](https://github.com/pymupdf/RAG/issues/75) - Poor Markdown Generation for Particular PDF.
* [76](https://github.com/pymupdf/RAG/issues/76) - suggestion on useful api parameters.


### Improvements

* Improved recognition of "insignificant" vector graphics. Graphics like text highlights or borders will be ignored.
* The format of saved images can now be controlled via new parameter `image_format`.
* Images can be stored in a specific folder via the new parameter `image_path`.
* Images are **not stored if contained** in another image on same page.
* Images are **not stored if too small:** if width or height are less than 5% of corresponding page dimension.
* All text is always written. If `write_images=True`, text on images / graphics can be suppressed by setting `force_text=False`.


## Changes in version 0.0.9


### Fixes

* [71](https://github.com/pymupdf/RAG/issues/71) - Unexpected results in pymupdf4llm but pymupdf works.
* [68](https://github.com/pymupdf/RAG/issues/68) - Issue with text extraction near footer of page.


### Improvements

* Improved identification of scattered text span particles. This should address most issues with out-of-sequence situations.
* We now correctly process rotated pages (see [issue 68](https://github.com/pymupdf/RAG/issues/68)).


## Changes in version 0.0.8


### Fixes


* [65](https://github.com/pymupdf/RAG/issues/65) - Fix typo in `pymupdf_rag.py`.


## Changes in version 0.0.7


### Fixes


* [54](https://github.com/pymupdf/RAG/issues/54) - Mistakes in orchestrating sentences. Additional fix: text extraction no longer uses the `TEXT_DEHYPHENATE` flag bit.

### Improvements

* Improved the algorithm dealing with vector graphics. Vector graphics are now more reliably classified as irrelevant: We now detect when "strokes" only exist in the neighborhood of the graphics boundary box border itself. This is quite often the case for code snippets.

## Changes in version 0.0.6


### Fixes


* [55](https://github.com/pymupdf/RAG/issues/55) - Bug in helpers/multi_column.py - IndexError: list index out of range.
* [54](https://github.com/pymupdf/RAG/issues/54) - Mistakes in orchestrating sentences.
* [52](https://github.com/pymupdf/RAG/issues/52) - Chunking of text files.
* Partial fix for [41](https://github.com/pymupdf/RAG/issues/41) / [40](https://github.com/pymupdf/RAG/issues/40) - Improved page column detection, but still no silver bullet for overly complex page layouts.

### Improvements

* New parameter `dpi` to specify the resolution of images.
* New parameters `page_width` / `page_height` for easily processing reflowable documents (Text, Office, e-books).
* New parameter `graphics_limit` to avoid spending runtimes for value-less content.
* New parameter `table_strategy` to directly control the table detection strategy.

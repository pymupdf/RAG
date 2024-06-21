"""
This script accepts a PDF document filename and converts it to a text file
in Markdown format, compatible with the GitHub standard.

It must be invoked with the filename like this:

python pymupdf_rag.py input.pdf [-pages PAGES]

The "PAGES" parameter is a string (containing no spaces) of comma-separated
page numbers to consider. Each item is either a single page number or a
number range "m-n". Use "N" to address the document's last page number.
Example: "-pages 2-15,40,43-N"

It will produce a markdown text file called "input.md".

Text will be sorted in Western reading order. Any table will be included in
the text in markdwn format as well.

Dependencies
-------------
PyMuPDF v1.24.2 or later

Copyright and License
----------------------
Copyright 2024 Artifex Software, Inc.
License GNU Affero GPL 3.0
"""

import os
from pathlib import Path
from typing import TypedDict, Callable, TypeAlias

from ._pymupdf import pymupdf
from .helpers.elements import TextElement, TableElement, ImageElement
from .helpers.multi_column import column_boxes
from .helpers.process_graphics import ProcessGraphicsProtocol, DefaultGraphicsProcessor
from .helpers.write_markdown import DefaultMarkdownWriter, WriteMarkdownProtocol

ImageFilterer = Callable[[pymupdf.Pixmap], bool]
M: TypeAlias = float | int
MarginsType: TypeAlias = tuple[M, M, M, M]
pymupdf.TOOLS.set_small_glyph_heights(True)


class ChunkData(TypedDict):
    metadata: dict
    image_elements: list[ImageElement]
    table_elements: list[TableElement]
    text: str


class Output(TypedDict):
    metadata: dict
    page_chunks: list[ChunkData]
    table_of_contents: list


def to_markdown(
    doc: str | Path | pymupdf.Document,
    *,
    pages: list[int] | None = None,
    margins: MarginsType = (0, 0, 0, 0),
    markdown_writer: WriteMarkdownProtocol = DefaultMarkdownWriter(),
    graphics_processor: ProcessGraphicsProtocol = DefaultGraphicsProcessor(),
) -> Output:
    """Process the document and return the text of its selected pages.

    Args:
        doc: a PDF filename, a Path object or a pymupdf.Document object.
        pages: list of page numbers to consider (0-based).
        margins: a tuple of 4 numbers (left, top, right, bottom) in points to
         crop the page.
        markdown_writer: an object with a 'write_markdown' method that will be used to format layout
         elements in markdown.
        graphics_processor: an object with a 'fit' method that will be used to process pdf graphics.
    """

    if not isinstance(doc, pymupdf.Document):  # open the document
        doc: pymupdf.Document = pymupdf.open(doc)

    if pages is None:  # use all pages if no selection given
        pages: list[int] = list(range(doc.page_count))

    if len(margins) == 4:
        margins = (margins[0], margins[1], margins[2], margins[3])
    else:
        raise ValueError("Margins must have length 4.")
    if not all(isinstance(m, M) for m in margins):
        raise ValueError("Margin values must be numbers")
    margins: tuple[M, M, M, M]

    markdown_writer.fit((doc.load_page(n) for n in pages))

    def get_page_output(doc, pno, margins, textflags):
        """Process one page.

        Args:
            doc: pymupdf.Document
            pno: 0-based page number
            margins: tuple of 4 numbers (left, top, right, bottom) in points to crop the page
            textflags: text extraction flag bits

        Returns:
            Markdown string of page content and image, table and vector
            graphics information.
        """
        page = doc[pno]
        left, top, right, bottom = margins
        clip = page.rect + (left, top, -right, -bottom)
        # make a TextPage for all later extractions
        # Locate all tables on page
        tables = page.find_tables(clip=clip, strategy="lines_strict")
        table_elements = []
        for t in tables:
            # Must include the header bbox (may exist outside tab.bbox)
            table_elements.append(
                TableElement(
                    rect=pymupdf.Rect(t.bbox) | pymupdf.Rect(t.header.bbox), table=t
                )
            )

        _ = graphics_processor.fit(page, table_elements=table_elements)
        image_elements = _["image_elements"]

        # Determine text column bboxes on page, avoiding tables and graphics
        textpage = page.get_textpage(flags=textflags)
        avoid_rects = [i.rect for i in image_elements] + [
            t.rect for t in table_elements
        ]

        text_rects = column_boxes(
            page,
            footer_margin=0,
            header_margin=0,
            textpage=textpage,
            graphic_rects=avoid_rects,
        )
        text_elements = [TextElement(r) for r in text_rects]
        md_string = markdown_writer.write_markdown(
            page,
            textpage,
            text_elements=text_elements,
            image_elements=image_elements,
            table_elements=table_elements,
        )
        return md_string, table_elements, image_elements

    # read the Table of Contents
    chunks: list[ChunkData] = []
    toc = pymupdf.utils.get_toc(doc, simple=False)
    textflags = pymupdf.TEXT_DEHYPHENATE | pymupdf.TEXT_MEDIABOX_CLIP
    for pno in pages:
        page_output, table_elements, image_elements = get_page_output(
            doc, pno, margins, textflags
        )
        chunk: ChunkData = {
            "metadata": {
                "page": pno + 1,
            },
            "text": page_output,
            "table_elements": table_elements,
            "image_elements": image_elements,
        }
        chunks.append(chunk)

    return {
        "metadata": doc.metadata,
        "page_chunks": chunks,
        "table_of_contents": toc,
    }


if __name__ == "__main__":
    import pathlib
    import sys
    import time

    try:
        filename = sys.argv[1]
    except IndexError:
        print(f"Usage:\npython {os.path.basename(__file__)} input.pdf")
        sys.exit()

    t0 = time.perf_counter()  # start a time

    doc = pymupdf.open(filename)  # open input file
    parms = sys.argv[2:]  # contains ["-pages", "PAGES"] or empty list
    pages = range(doc.page_count)  # default page range
    if len(parms) == 2 and parms[0] == "-pages":  # page sub-selection given
        pages = []  # list of desired page numbers

        # replace any variable "N" by page count
        pages_spec = parms[1].replace("N", f"{doc.page_count}")
        for spec in pages_spec.split(","):
            if "-" in spec:
                start, end = map(int, spec.split("-"))
                pages.extend(range(start - 1, end))
            else:
                pages.append(int(spec) - 1)

        # make a set of invalid page numbers
        wrong_pages = set([n + 1 for n in pages if n >= doc.page_count][:4])
        if wrong_pages != set():  # if any invalid numbers given, exit.
            sys.exit(f"Page number(s) {wrong_pages} not in '{doc}'.")

    # get the markdown string
    output = to_markdown(doc, pages=pages)
    # output to a text file with extension ".md"
    outname = doc.name.replace(".pdf", ".md")
    md_string = "\n\n-----\n\n".join([chunk["text"] for chunk in output["page_chunks"]])
    pathlib.Path(outname).write_bytes(md_string.encode())
    t1 = time.perf_counter()  # stop timer
    print(f"Markdown creation time for {doc.name=} {round(t1 - t0, 2)} sec.")

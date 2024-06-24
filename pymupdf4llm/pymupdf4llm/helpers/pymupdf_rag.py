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
import string

try:
    import pymupdf as fitz  # available with v1.24.3
except ImportError:
    import fitz

from pymupdf4llm.helpers.get_text_lines import get_raw_lines, is_white
from pymupdf4llm.helpers.multi_column import column_boxes

if fitz.pymupdf_version_tuple < (1, 24, 2):
    raise NotImplementedError("PyMuPDF version 1.24.2 or later is needed.")

bullet = (
    "- ",
    "* ",
    chr(0xF0A7),
    chr(0xF0B7),
    chr(0xB7),
    chr(8226),
    chr(9679),
)
GRAPHICS_TEXT = "\n![%s](%s)\n"


class IdentifyHeaders:
    """Compute data for identifying header text."""

    def __init__(
        self,
        doc: str,
        pages: list = None,
        body_limit: float = 12,
    ):
        """Read all text and make a dictionary of fontsizes.

        Args:
            pages: optional list of pages to consider
            body_limit: consider text with larger font size as some header
        """
        if isinstance(doc, fitz.Document):
            mydoc = doc
        else:
            mydoc = fitz.open(doc)

        if pages is None:  # use all pages if omitted
            pages = range(mydoc.page_count)

        fontsizes = {}
        for pno in pages:
            page = mydoc.load_page(pno)
            blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]
            for span in [  # look at all non-empty horizontal spans
                s
                for b in blocks
                for l in b["lines"]
                for s in l["spans"]
                if not is_white(s["text"])
            ]:
                fontsz = round(span["size"])
                count = fontsizes.get(fontsz, 0) + len(span["text"].strip())
                fontsizes[fontsz] = count

        if mydoc != doc:
            # if opened here, close it now
            mydoc.close()

        # maps a fontsize to a string of multiple # header tag characters
        self.header_id = {}

        # If not provided, choose the most frequent font size as body text.
        # If no text at all on all pages, just use 12.
        # In any case all fonts not exceeding
        temp = sorted(
            [(k, v) for k, v in fontsizes.items()],
            key=lambda i: i[1],
            reverse=True,
        )
        if temp:
            b_limit = max(body_limit, temp[0][0])
        else:
            b_limit = body_limit

        # identify up to 6 font sizes as header candidates
        sizes = sorted(
            [f for f in fontsizes.keys() if f > b_limit],
            reverse=True,
        )[:6]

        # make the header tag dictionary
        for i, size in enumerate(sizes):
            self.header_id[size] = "#" * (i + 1) + " "

    def get_header_id(self, span: dict, page=None) -> str:
        """Return appropriate markdown header prefix.

        Given a text span from a "dict"/"rawdict" extraction, determine the
        markdown header prefix string of 0 to n concatenated '#' characters.
        """
        fontsize = round(span["size"])  # compute fontsize
        hdr_id = self.header_id.get(fontsize, "")
        return hdr_id


def to_markdown(
    doc,
    *,
    pages: list = None,
    hdr_info=None,
    write_images: bool = False,
    page_chunks: bool = False,
    margins=(0, 50, 0, 50),
    dpi=150,
    page_width=612,
    page_height=None,
    table_strategy="lines_strict",
    graphics_limit=None,
) -> str:
    """Process the document and return the text of the selected pages.

    Args:
        doc: pymupdf.Document or string.
        pages: list of page numbers to consider (0-based).
        hdr_info: callable or object having a method named 'get_hdr_info'.
        write_images: (bool) whether to save images / drawing as files.
        page_chunks: (bool) whether to segment output by page.
        margins: do not consider content overlapping margin areas.
        dpi: (int) desired resolution for generated images.
        page_width: (float) assumption if page layout is variable.
        page_height: (float) assumption if page layout is variable.
        table_strategy: choose table detection strategy
        graphics_limit: (int) ignore page with too many vector graphics.

    """

    DPI = dpi
    GRAPHICS_LIMIT = graphics_limit
    if not isinstance(doc, fitz.Document):
        doc = fitz.open(doc)

    # for reflowable documents allow making 1 page for the whole document
    if doc.is_reflowable:
        if hasattr(page_height, "__float__"):
            # accept user page dimensions
            doc.layout(width=page_width, height=page_height)
        else:
            # no page height limit given: make 1 page for whole document
            doc.layout(width=page_width, height=792)
            page_count = doc.page_count
            height = 792 * page_count  # height that covers full document
            doc.layout(width=page_width, height=height)

    if pages is None:  # use all pages if no selection given
        pages = list(range(doc.page_count))

    if hasattr(margins, "__float__"):
        margins = [margins] * 4
    if len(margins) == 2:
        margins = (0, margins[0], 0, margins[1])
    if len(margins) != 4:
        raise ValueError(
            "margins must be a float or a sequence of 2 or 4 floats"
        )
    elif not all([hasattr(m, "__float__") for m in margins]):
        raise ValueError("margin values must be floats")

    # If "hdr_info" is not an object having method "get_header_id", scan the
    # document and use font sizes as header level indicators.
    if callable(hdr_info):
        get_header_id = hdr_info
    elif hasattr(hdr_info, "get_header_id") and callable(
        hdr_info.get_header_id
    ):
        get_header_id = hdr_info.get_header_id
    else:
        hdr_info = IdentifyHeaders(doc)
        get_header_id = hdr_info.get_header_id

    def resolve_links(links, span):
        """Accept a span and return a markdown link string.

        Args:
            links: a list as returned by page.get_links()
            span: a span dictionary as returned by page.get_text("dict")

        Returns:
            None or a string representing the link in MD format.
        """
        bbox = fitz.Rect(span["bbox"])  # span bbox
        # a link should overlap at least 70% of the span
        for link in links:
            hot = link["from"]  # the hot area of the link
            middle = (hot.tl + hot.br) / 2  # middle point of hot area
            if not middle in bbox:
                continue  # does not touch the bbox
            text = f'[{span["text"].strip()}]({link["uri"]})'
            return text

    def save_image(page, rect, i):
        """Optionally render the rect part of a page."""
        filename = page.parent.name.replace("\\", "/")
        image_path = f"{filename}-{page.number}-{i}.png"
        if write_images is True:
            page.get_pixmap(clip=rect, dpi=DPI).save(image_path)
            return os.path.basename(image_path)
        return ""

    def write_text(
        page: fitz.Page,
        textpage: fitz.TextPage,
        clip: fitz.Rect,
        tabs=None,
        tab_rects: dict = None,
        img_rects: dict = None,
        links: list = None,
    ) -> string:
        """Output the text found inside the given clip.

        This is an alternative for plain text in that it outputs
        text enriched with markdown styling.
        The logic is capable of recognizing headers, body text, code blocks,
        inline code, bold, italic and bold-italic styling.
        There is also some effort for list supported (ordered / unordered) in
        that typical characters are replaced by respective markdown characters.

        'tab_rects'/'img_rects' are dictionaries of table, respectively image
        or vector graphic rectangles.
        General Markdown text generation skips these areas. Tables are written
        via their own 'to_markdown' method. Images and vector graphics are
        optionally saved as files and pointed to by respective markdown text.
        """
        if clip is None:
            clip = textpage.rect
        out_string = ""

        # This is a list of tuples (linerect, spanlist)
        nlines = get_raw_lines(textpage, clip=clip, tolerance=3)

        tab_rects0 = list(tab_rects.values())
        img_rects0 = list(img_rects.values())

        prev_lrect = None  # previous line rectangle
        prev_bno = -1  # previous block number of line
        code = False  # mode indicator: outputting code
        prev_hdr_string = None

        for lrect, spans in nlines:
            # there may tables or images inside the text block: skip them
            if intersects_rects(lrect, tab_rects0) or intersects_rects(
                lrect, img_rects0
            ):
                continue

            # Pick up tables intersecting this text block
            for i, tab_rect in sorted(
                [
                    j
                    for j in tab_rects.items()
                    if j[1].y1 <= lrect.y0 and not (j[1] & clip).is_empty
                ],
                key=lambda j: (j[1].y1, j[1].x0),
            ):
                out_string += "\n" + tabs[i].to_markdown(clean=False) + "\n"
                del tab_rects[i]

            # Pick up images / graphics intersecting this text block
            for i, img_rect in sorted(
                [
                    j
                    for j in img_rects.items()
                    if j[1].y1 <= lrect.y0 and not (j[1] & clip).is_empty
                ],
                key=lambda j: (j[1].y1, j[1].x0),
            ):
                pathname = save_image(page, img_rect, i)
                if pathname:
                    out_string += GRAPHICS_TEXT % (pathname, pathname)
                del img_rects[i]

            text = " ".join([s["text"] for s in spans])

            # if the full line mono-spaced?
            all_mono = all([s["flags"] & 8 for s in spans])

            if all_mono:
                if not code:  # if not already in code output  mode:
                    out_string += "```\n"  # switch on "code" mode
                    code = True
                # compute approx. distance from left - assuming a width
                # of 0.5*fontsize.
                delta = int((lrect.x0 - clip.x0) / (spans[0]["size"] * 0.5))
                indent = " " * delta

                out_string += indent + text + "\n"
                continue  # done with this line

            span0 = spans[0]
            bno = span0["block"]  # block number of line
            if bno != prev_bno:
                out_string += "\n"
                prev_bno = bno

            if (  # check if we need another line break
                prev_lrect
                and lrect.y1 - prev_lrect.y1 > lrect.height * 1.5
                or span0["text"].startswith("[")
                or span0["text"].startswith(bullet)
                or span0["flags"] & 1  # superscript?
            ):
                out_string += "\n"
            prev_lrect = lrect

            # if line is a header, this will return multiple "#" characters
            hdr_string = get_header_id(span0, page=page)

            # intercept if header text has been broken in multiple lines
            if hdr_string and hdr_string == prev_hdr_string:
                out_string = out_string[:-1] + " " + text + "\n"
                continue

            prev_hdr_string = hdr_string
            if hdr_string.startswith("#"):  # if a header line skip the rest
                out_string += hdr_string + text + "\n"
                continue

            # this line is not all-mono, so switch off "code" mode
            if code:  # still in code output mode?
                out_string += "```\n"  # switch of code mode
                code = False

            for i, s in enumerate(spans):  # iterate spans of the line
                # decode font properties
                mono = s["flags"] & 8
                bold = s["flags"] & 16
                italic = s["flags"] & 2

                if mono:
                    # this is text in some monospaced font
                    out_string += f"`{s['text'].strip()}` "
                else:  # not a mono text
                    prefix = ""
                    suffix = ""
                    if hdr_string == "":
                        if bold:
                            prefix = "**"
                            suffix += "**"
                        if italic:
                            prefix += "_"
                            suffix = "_" + suffix

                    # convert intersecting link into markdown syntax
                    ltext = resolve_links(links, s)
                    if ltext:
                        text = f"{hdr_string}{prefix}{ltext}{suffix} "
                    else:
                        text = (
                            f"{hdr_string}{prefix}{s['text'].strip()}{suffix} "
                        )

                    if text.startswith(bullet):
                        text = "-  " + text[1:]
                    out_string += text
            if not code:
                out_string += "\n"
        out_string += "\n"
        if code:
            out_string += "```\n"  # switch of code mode
            code = False

        return (
            out_string.replace(" \n", "\n")
            .replace("  ", " ")
            .replace("\n\n\n", "\n\n")
        )

    def is_in_rects(rect, rect_list):
        """Check if rect is contained in a rect of the list."""
        for i, r in enumerate(rect_list, start=1):
            if rect in r:
                return i
        return 0

    def intersects_rects(rect, rect_list):
        """Check if middle of rect is contained in a rect of the list."""
        for i, r in enumerate(rect_list, start=1):
            if (rect.tl + rect.br) / 2 in r:  # middle point is inside r
                return i
        return 0

    def output_tables(tabs, text_rect, tab_rects):
        """Output tables above a text rectangle."""
        this_md = ""  # markdown string for table content
        if text_rect is not None:  # select tables above the text block
            for i, trect in sorted(
                [j for j in tab_rects.items() if j[1].y1 <= text_rect.y0],
                key=lambda j: (j[1].y1, j[1].x0),
            ):
                this_md += tabs[i].to_markdown(clean=False)
                del tab_rects[i]  # do not touch this table twice

        else:  # output all remaining table
            for i, trect in sorted(
                tab_rects.items(),
                key=lambda j: (j[1].y1, j[1].x0),
            ):
                this_md += tabs[i].to_markdown(clean=False)
                del tab_rects[i]  # do not touch this table twice
        return this_md

    def output_images(page, text_rect, img_rects):
        """Output images and graphics above text rectangle."""
        if img_rects is None:
            return ""
        this_md = ""  # markdown string
        if text_rect is not None:  # select tables above the text block
            for i, img_rect in sorted(
                [j for j in img_rects.items() if j[1].y1 <= text_rect.y0],
                key=lambda j: (j[1].y1, j[1].x0),
            ):
                pathname = save_image(page, img_rect, i)
                if pathname:
                    this_md += GRAPHICS_TEXT % (pathname, pathname)
                del img_rects[i]  # do not touch this image twice

        else:  # output all remaining table
            for i, img_rect in sorted(
                img_rects.items(),
                key=lambda j: (j[1].y1, j[1].x0),
            ):
                pathname = save_image(page, img_rect, i)
                if pathname:
                    this_md += GRAPHICS_TEXT % (pathname, pathname)
                del img_rects[i]  # do not touch this image twice
        return this_md

    def get_metadata(doc, pno):
        meta = doc.metadata.copy()
        meta["file_path"] = doc.name
        meta["page_count"] = doc.page_count
        meta["page"] = pno + 1
        return meta

    def get_page_output(doc, pno, margins, textflags):
        """Process one page.

        Args:
            doc: fitz.Document
            pno: 0-based page number
            textflags: text extraction flag bits

        Returns:
            Markdown string of page content and image, table and vector
            graphics information.
        """
        page = doc[pno]
        md_string = ""
        if GRAPHICS_LIMIT is not None:
            test_paths = page.get_cdrawings()
            if (excess := len(test_paths)) > GRAPHICS_LIMIT:
                md_string = f"\n**Ignoring page {page.number} with {excess} vector graphics.**"
                md_string += "\n\n-----\n\n"
                return md_string, [], [], []
        left, top, right, bottom = margins
        clip = page.rect + (left, top, -right, -bottom)
        # extract external links on page
        links = [l for l in page.get_links() if l["kind"] == fitz.LINK_URI]

        # make a TextPage for all later extractions
        textpage = page.get_textpage(flags=textflags, clip=clip)

        img_info = [
            img for img in page.get_image_info() if img["bbox"] in clip
        ]
        images = img_info[:]
        tables = []
        graphics = []

        # Locate all tables on page
        tabs = page.find_tables(clip=clip, strategy=table_strategy)

        # Make a list of table boundary boxes.
        # Must include the header bbox (which may exist outside tab.bbox)
        tab_rects = {}
        for i, t in enumerate(tabs):
            tab_rects[i] = fitz.Rect(t.bbox) | fitz.Rect(t.header.bbox)
            tab_dict = {
                "bbox": tuple(tab_rects[i]),
                "rows": t.row_count,
                "columns": t.col_count,
            }
            tables.append(tab_dict)

        # list of table rectangles
        tab_rects0 = list(tab_rects.values())

        # Select paths that are not contained in any table
        page_clip = page.rect + (36, 36, -36, -36)  # ignore full page graphics
        paths = [
            p
            for p in page.get_drawings()
            if not intersects_rects(p["rect"], tab_rects0)
            and p["rect"] in page_clip
            and p["rect"].width < page_clip.width
            and p["rect"].height < page_clip.height
        ]

        # Determine vector graphics outside any tables, ignoring any
        # fill-only (type "f") paths.
        vg_clusters = []
        for bbox in page.cluster_drawings(drawings=paths):
            include = False
            for p in [p for p in paths if p["rect"] in bbox]:
                if p["type"] != "f":
                    include = True
                    break
                if [item[0] for item in p["items"] if item[0] == "c"]:
                    include = True
                    break
            if include is True:
                vg_clusters.append(bbox)

        actual_paths = [
            p for p in paths if is_in_rects(p["rect"], vg_clusters)
        ]

        vg_clusters0 = [
            r
            for r in vg_clusters
            if not intersects_rects(r, tab_rects0) and r.height > 20
        ]

        if write_images is True:
            vg_clusters0 += [fitz.Rect(i["bbox"]) for i in img_info]

        vg_clusters = dict((i, r) for i, r in enumerate(vg_clusters0))

        # Determine text column bboxes on page, avoiding tables and graphics
        text_rects = column_boxes(
            page,
            paths=actual_paths,
            no_image_text=write_images,
            textpage=textpage,
            avoid=tab_rects0 + vg_clusters0,
            footer_margin=margins[3],
            header_margin=margins[1],
        )

        """Extract markdown text iterating over text rectangles.
        We also output any tables. They may live above, below or inside
        the text rectangles.
        """
        for text_rect in text_rects:
            # output tables above this block of text
            md_string += output_tables(tabs, text_rect, tab_rects)
            md_string += output_images(page, text_rect, vg_clusters)

            # output text inside this rectangle
            md_string += write_text(
                page,
                textpage,
                text_rect,
                tabs=tabs,
                tab_rects=tab_rects,
                img_rects=vg_clusters,
                links=links,
            )

        # write any remaining tables and images
        md_string += output_tables(tabs, None, tab_rects)
        md_string += output_images(None, tab_rects, None)
        md_string += "\n-----\n\n"
        while md_string.startswith("\n"):
            md_string = md_string[1:]
        return md_string, images, tables, graphics

    if page_chunks is False:
        document_output = ""
    else:
        document_output = []

    # read the Table of Contents
    toc = doc.get_toc()
    textflags = fitz.TEXT_DEHYPHENATE | fitz.TEXT_MEDIABOX_CLIP
    for pno in pages:
        page_output, images, tables, graphics = get_page_output(
            doc, pno, margins, textflags
        )
        if page_chunks is False:
            document_output += page_output
        else:
            # build subet of TOC for this page
            page_tocs = [t for t in toc if t[-1] == pno + 1]

            metadata = get_metadata(doc, pno)
            document_output.append(
                {
                    "metadata": metadata,
                    "toc_items": page_tocs,
                    "tables": tables,
                    "images": images,
                    "graphics": graphics,
                    "text": page_output,
                }
            )

    return document_output


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

    doc = fitz.open(filename)  # open input file
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
    md_string = to_markdown(doc, pages=pages)

    # output to a text file with extension ".md"
    outname = doc.name.replace(".pdf", ".md")
    pathlib.Path(outname).write_bytes(md_string.encode())
    t1 = time.perf_counter()  # stop timer
    print(f"Markdown creation time for {doc.name=} {round(t1-t0,2)} sec.")

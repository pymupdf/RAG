"""
This script accepts a PDF document filename and converts it to a text file.


Dependencies
-------------
PyMuPDF v1.24.2 or later

Copyright and License
----------------------
Copyright 2024 Artifex Software, Inc.
License GNU Affero GPL 3.0
"""

import string
import sys

try:
    import pymupdf as fitz  # available with v1.24.3
except ImportError:
    import fitz

WHITE = set(string.whitespace)


def is_white(text):
    return WHITE.issuperset(text)


def get_raw_lines(textpage, clip=None, tolerance=3):
    """Extract the text spans from a TextPage in a natural reading sequence.

    All spans roughly on the same line are joined to generate an improved line.
    This copes with MuPDF's algorithm that generates new lines also for spans
    whose horizontal distance is larger than some hreshold.

    Result is a sorted list of line objects that consist of the recomputed line
    rectangle and a sorted list of spans in that line.

    This result can then be easily converted e.g. to plain or markdown text.

    Args:
        textpage: (mandatory) TextPage object
        clip: (Rect) specifies a sub-rectangle of the textpage rect (which also
              may be based on some part of the original page).
        tolerance: (float) put spans on the same line if their top or bottom
              coordinate differ by no mor than this value.

    Returns:
        A sorted list of items (rect, [spans]), each representing a line. The
        spans are sorted left to right, Span dictionaries have been changed
        in that "bbox" is a Rect object and "line" is an integer representing
        the line number of the span. This allows to detect where MuPDF has
        generated line breaks to indicate large inter-span distances.
    """
    y_delta = tolerance  # allowable vertical coordinate deviation
    if clip == None:  # use TextPage if not provided
        clip = textpage.rect
    # extract text blocks - if bbox is not empty
    blocks = [
        b
        for b in textpage.extractDICT()["blocks"]
        if b["type"] == 0 and not fitz.Rect(b["bbox"]).is_empty
    ]
    spans = []  # all spans in TextPage here
    for bno, b in enumerate(blocks):
        for lno, line in enumerate(b["lines"]):
            lbbox = fitz.Rect(line["bbox"])
            for sno, s in enumerate(line["spans"]):
                sbbox = fitz.Rect(s["bbox"])  # turn to a Rect
                mpoint = (sbbox.tl + sbbox.br) / 2  # middle point
                if mpoint not in clip:
                    continue
                if is_white(s["text"]):  # ignore white text
                    continue
                if s["flags"] & 1 == 1:  # if a superscript, modify
                    i = 1 if sno == 0 else sno - 1
                    neighbor = line["spans"][i]
                    sbbox.y1 = neighbor["bbox"][3]
                    s["text"] = f"[{s['text']}]"
                s["bbox"] = sbbox  # update with the Rect version
                # include line identifier to facilitate separator insertion
                s["line"] = lno
                s["block"] = bno
                spans.append(s)

    if not spans:  # we may have no text at all
        return []

    spans.sort(
        key=lambda s: s["bbox"].y1
    )  # sort spans by assending bottom coord
    nlines = []  # final result
    line = [spans[0]]  # collects spans with fitting vertical coordinate
    lrect = spans[0]["bbox"]  # rectangle joined from span rectangles

    for s in spans[1:]:
        sbbox = s["bbox"]
        sbbox0 = line[-1]["bbox"]
        # if any of top or bottom coordinates are close enough, join...
        if (
            abs(sbbox.y1 - sbbox0.y1) <= y_delta
            or abs(sbbox.y0 - sbbox0.y0) <= y_delta
        ):
            line.append(s)  # append to this line
            lrect |= sbbox  # extend line rectangle
            continue

        # end of current line, sort its spans from left to right
        line.sort(key=lambda s: s["bbox"].x0)

        # append line rect and its spans to final output
        nlines.append([lrect, line])

        line = [s]  # start next line
        lrect = sbbox  # initialize its rectangle

    # need to append last line in the same way
    line.sort(key=lambda s: s["bbox"].x0)
    nlines.append([lrect, line])

    return nlines


def get_text_lines(
    page, *, textpage=None, clip=None, sep="\t", tolerance=3, ocr=False
):
    """Extract text by line keeping natural reading sequence.

    Notes:
        Internally uses "dict" to select lines and their spans.
        Returns plain text. If originally separate MuPDF lines in fact have
        (approximatly) the same baseline, they are joined into one line using
        the 'sep' character(s).
        This method can be used to extract text in reading sequence - even in
        cases of text replaced by way of redaction annotations.

    Args:
        page: (fitz.Page)
        textpage: (TextPage) if None a temporary one is created.
        clip: (rect-like) only consider spans inside this area
        sep: (str) use this string when joining multiple MuPDF lines.
    Returns:
        String of plain text in reading sequence.
    """
    page.remove_rotation()
    prect = page.rect if not clip else fitz.Rect(clip)  # area to consider

    xsep = sep if sep == "|" else ""

    # make a TextPage if required
    if textpage is None:
        if ocr is False:
            tp = page.get_textpage(clip=prect, flags=fitz.TEXTFLAGS_TEXT)
        else:
            tp = page.get_textpage_ocr(dpi=300, full=True)
    else:
        tp = textpage

    lines = get_raw_lines(tp, clip=prect, tolerance=tolerance)

    if not textpage:  # delete temp TextPage
        tp = None

    if not lines:
        return ""

    # Compose final text
    alltext = ""

    if not ocr:
        prev_bno = -1  # number of previous text block
        for lrect, line in lines:  # iterate through lines
            # insert extra line break if a different block
            bno = line[0]["block"]  # block number of this line
            if bno != prev_bno:
                alltext += "\n"
            prev_bno = bno

            line_no = line[0]["line"]  # store the line number of previous span
            for s in line:  # walk over the spans in the line
                lno = s["line"]
                stext = s["text"]
                if line_no == lno:
                    alltext += stext
                else:
                    alltext += sep + stext
                line_no = lno
            alltext += "\n"  # append line break after a line
        alltext += "\n"  # append line break at end of block
        return alltext

    """
    For OCR output, we try a rudimentary table recognition.
    """
    rows = []
    xvalues = []
    for lrect, line in lines:
        # if only 1 span in line and no columns identified yet...
        if len(line) == 1 and not xvalues:
            alltext += line[0]["text"] + "\n\n\n"
            continue
        # multiple spans in line and no columns identified yet
        elif not xvalues:  # define column borders
            xvalues = [s["bbox"].x0 for s in line] + [line[-1]["bbox"].x1]
            col_count = len(line)  # number of columns
        row = [""] * col_count
        for r, l in line:
            for i in range(len(xvalues) - 1):
                x0, x1 = xvalues[i], xvalues[i + 1]
                if abs(r.x0 - x0) <= 3 or abs(r.x1 - x1) <= 3:
                    row[i] = l
        rows.append(row)
    if rows:
        row = "|" + "|".join(rows[0]) + "|\n"
        alltext += row
        alltext += "|---" * len(rows[0]) + "|\n"
        for row in rows[1:]:
            alltext += "|" + "|".join(row) + "|\n"
        alltext += "\n"
    return alltext


if __name__ == "__main__":
    import pathlib

    filename = sys.argv[1]
    doc = fitz.open(filename)
    text = ""
    for page in doc:
        text += get_text_lines(page, sep=" ") + "\n" + chr(12) + "\n"
    pathlib.Path(f"{doc.name}.txt").write_bytes(text.encode())

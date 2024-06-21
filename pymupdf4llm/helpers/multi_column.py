"""
This is an advanced PyMuPDF utility for detecting multi-column pages.
It can be used in a shell script, or its main function can be imported and
invoked as descript below.

Features
---------
- Identify text belonging to (a variable number of) columns on the page.
- Text with different background color is handled separately, allowing for
  easier treatment of side remarks, comment boxes, etc.
- Uses text block detection capability to identify text blocks and
  uses the block bboxes as primary structuring principle.
- Supports ignoring footers via a footer margin parameter.
- Returns re-created text boundary boxes (integer coordinates), sorted ascending
  by the top, then by the left coordinates.

Restrictions
-------------
- Only supporting horizontal, left-to-right text
- Returns a list of text boundary boxes - not the text itself. The caller is
  expected to extract text from within the returned boxes.
- Text written above images is ignored altogether (option).
- This utility works as expected in most cases. The following situation cannot
  be handled correctly:
    * overlapping (non-disjoint) text blocks
    * image captions are not recognized and are handled like normal text

Usage
------
- As a CLI shell command use

  python multi_column.py input.pdf footer_margin header_margin

  Where margins are the height of the bottom / top stripes to ignore on each
  page.
  This code is intended to be modified according to your need.

- Use in a Python script as follows:

  ----------------------------------------------------------------------------------
  from multi_column import column_boxes

  # for each page execute
  bboxes = column_boxes(page, footer_margin=50, no_image_text=True)

  bboxes is a list of pymupdf.Rect objects, that are sorted ascending by their
  y0, then x0 coordinates. Their text content can be extracted by all PyMuPDF
  get_text() variants, like for instance the following:
  for rect in bboxes:
      print(page.get_text(clip=rect, sort=True))
  ----------------------------------------------------------------------------------

Dependencies
-------------
PyMuPDF v1.24.2 or later

Copyright and License
----------------------
Copyright 2024 Artifex Software, Inc.
License GNU Affero GPL 3.0
"""

from .rectangle_utils import is_in_rects, any_rect_between_over_y, intersects_rects
from .._pymupdf import pymupdf


def can_extend(temp, bb, bboxlist, vert_bboxes):
    """Determines whether rectangle 'temp' can be extended by 'bb'
    without intersecting any of the rectangles contained in 'bboxlist'.

    Items of bboxlist may be None if they have been removed.

    Returns:
        True if 'temp' has no intersections with items of 'bboxlist'.
    """
    for b in bboxlist:
        if not intersects_rects(temp, vert_bboxes) and (
            b is None or b == bb or (temp & b).is_empty
        ):
            continue
        return False

    return True


def extend_right(bboxes, width, vert_bboxes, graphics_bboxes):
    """Extend a bbox to the right page border.

    Whenever there is no text to the right of a bbox, enlarge it up
    to the right page border.

    Args:
        bboxes: (list[IRect]) bboxes to check
        width: (int) page width
        vert_bboxes: (list[IRect]) bboxes with vertical text
        graphics_bboxes: (list[IRect]) bboxes of images or graphics
    Returns:
        Potentially modified bboxes.
    """
    for i, bb in enumerate(bboxes):
        # do not extend text in images
        if is_in_rects(bb, graphics_bboxes):
            continue

        # temp extends bb to the right page border
        temp = +bb
        temp.x1 = width

        # do not cut through colored background or images
        if intersects_rects(temp, vert_bboxes + graphics_bboxes):
            continue

        # also, do not intersect other text bboxes
        check = can_extend(temp, bb, bboxes, vert_bboxes)
        if check:
            bboxes[i] = temp  # replace with enlarged bbox

    return [b for b in bboxes if b]


def column_boxes(
    page,
    *,
    footer_margin=50,
    header_margin=50,
    textpage=None,
    graphic_rects=None,
):
    """Determine bboxes which wrap a column on the page.

    Args:
        footer_margin: ignore text if distance from bottom is less
        header_margin: ignore text if distance from top is less
        textpage: use this textpage instead of creating one
        graphic_rects: ignore text in any of these areas
    """

    # compute relevant page area
    clip = +page.rect
    clip.y1 -= footer_margin  # Remove footer area
    clip.y0 += header_margin  # Remove header area

    if textpage is None:
        textpage = page.get_textpage(clip=clip, flags=pymupdf.TEXTFLAGS_TEXT)

    # bboxes of non-horizontal text
    # avoid when expanding horizontal text boxes
    vert_bboxes = []

    def clean_nblocks(nblocks):
        """Do some elementary cleaning."""

        # 1. remove any duplicate blocks.
        blen = len(nblocks)
        if blen < 2:
            return nblocks
        start = blen - 1
        for i in range(start, -1, -1):
            bb1 = nblocks[i]
            bb0 = nblocks[i - 1]
            if bb0 == bb1:
                del nblocks[i]

        # 2. repair sequence in special cases:
        # consecutive bboxes with almost same bottom value are sorted ascending
        # by x-coordinate.
        y1 = nblocks[0].y1  # first bottom coordinate
        i0 = 0  # its index
        i1 = -1  # index of last bbox with same bottom

        # Iterate over bboxes, identifying segments with approx. same bottom value.
        # Replace every segment by its sorted version.
        for i in range(1, len(nblocks)):
            b1 = nblocks[i]
            if abs(b1.y1 - y1) > 10:  # different bottom
                if i1 > i0:  # segment length > 1? Sort it!
                    nblocks[i0 : i1 + 1] = sorted(
                        nblocks[i0 : i1 + 1], key=lambda b: b.x0
                    )
                y1 = b1.y1  # store new bottom value
                i0 = i  # store its start index
            i1 = i  # store current index
        if i1 > i0:  # segment waiting to be sorted
            nblocks[i0 : i1 + 1] = sorted(nblocks[i0 : i1 + 1], key=lambda b: b.x0)
        return nblocks

    # blocks of text on page
    text_blocks = textpage.extractDICT()["blocks"]
    text_blocks = list(
        filter(lambda b: not is_in_rects(b["bbox"], graphic_rects), text_blocks)
    )
    bboxes = []

    # Make block rectangles, ignoring non-horizontal text
    for b in text_blocks:
        bbox = b["bbox"]
        # confirm first line to be horizontal
        line0 = b["lines"][0]  # get first line
        if line0["dir"] != (1, 0):  # only accept horizontal text
            vert_bboxes.append(bbox)
            continue

        srect = pymupdf.EMPTY_RECT()
        for line in b["lines"]:
            text = "".join([s["text"].strip() for s in line["spans"]])
            if text:
                lbbox = pymupdf.Rect(line["bbox"])
                srect |= lbbox
        bbox = +srect

        if not bbox.is_empty:
            bboxes.append(bbox)

    # immediately return of no text found
    if not bboxes:
        return []

    # Sort text bboxes by ascending background, top, then left coordinates
    bboxes.sort(key=lambda k: (k.y0, k.x0))
    # Extend bboxes to the right where possible
    bboxes = extend_right(bboxes, int(page.rect.width), vert_bboxes, graphic_rects)

    # --------------------------------------------------------------------
    # Join bboxes to establish some column structure
    # --------------------------------------------------------------------
    # the final block bboxes on page
    nblocks = [bboxes[0]]  # pre-fill with first bbox
    bboxes = bboxes[1:]  # remaining old bboxes

    temp = None
    for i, bb in enumerate(bboxes):  # iterate old bboxes
        check = False  # indicates unwanted joins

        j = None
        # check if bb can extend one of the new blocks
        for j in range(len(nblocks)):
            nbb = nblocks[j]  # a new block

            # never join across columns
            if bb is None or nbb.x1 < bb.x0 or bb.x1 < nbb.x0:
                continue

            # never join across figures
            if any_rect_between_over_y(nbb, bb, graphic_rects):
                continue

            # never join across text blocks
            if any_rect_between_over_y(nbb, bb, nblocks):
                continue

            temp = bb | nbb  # temporary extension of new block
            check = can_extend(temp, nbb, nblocks, vert_bboxes)
            if check:
                break

        if not check:  # bb cannot be used to extend any of the new bboxes
            nblocks.append(bb)  # so add it to the list
            j = len(nblocks) - 1  # index of it
            temp = nblocks[j]  # new bbox added

        if j is not None:
            if can_extend(temp, bb, bboxes, vert_bboxes):
                nblocks[j] = temp
            else:
                nblocks.append(bb)
        bboxes[i] = None

    # do some elementary cleaning
    nblocks = clean_nblocks(nblocks)

    # return identified text bboxes
    return nblocks


if __name__ == "__main__":
    """Only for debugging purposes, currently.

    Draw red borders around the returned text bboxes and insert
    the bbox number.
    Then save the file under the name "input-blocks.pdf".
    """
    import sys

    # get the file name
    filename = sys.argv[1]

    # check if footer margin is given
    if len(sys.argv) > 2:
        footer_margin = int(sys.argv[2])
    else:  # use default vaue
        footer_margin = 50

    # check if header margin is given
    if len(sys.argv) > 3:
        header_margin = int(sys.argv[3])
    else:  # use default vaue
        header_margin = 50

    # open document
    doc = pymupdf.open(filename)

    # iterate over the pages
    for page in doc:
        # get the text bboxes
        bboxes = column_boxes(
            page, footer_margin=footer_margin, header_margin=header_margin
        )

        # prepare a canvas to draw rectangles and text
        shape = page.new_shape()

        # iterate over the bboxes
        for i, rect in enumerate(bboxes):
            shape.draw_rect(rect)  # draw a border

            # write sequence number
            shape.insert_text(rect.tl + (5, 15), str(i), color=pymupdf.pdfcolor["red"])

        # finish drawing / text with color red
        shape.finish(color=pymupdf.pdfcolor["red"])
        shape.commit()  # store to the page

    # save document with text bboxes
    doc.ez_save(filename.replace(".pdf", "-blocks.pdf"))

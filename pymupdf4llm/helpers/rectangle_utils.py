from .._pymupdf import pymupdf


def is_in_rects(rect: pymupdf.Rect, rect_list: list[pymupdf.Rect]):
    """
    Check if rect is contained in a rect of the list.
    Return the index + 1 of the container rect.
    """
    for i, r in enumerate(rect_list, start=1):
        if rect in r:
            return i
    return 0


def intersects_rects(rect: pymupdf.Rect, rect_list: list[pymupdf.Rect]):
    """
    Check if rect intersects with any rect of the list.
    Return the index + 1 of the first intersecting rect.
    """
    for i, r in enumerate(rect_list, start=1):
        if not (rect & r).is_empty:
            return i
    return 0


def intersects_over_x(rect1: pymupdf.Rect, rect2: pymupdf.Rect):
    """
    Check if rect1 and rect2 intersect over x-axis.
    Actual meaning: one under the other.
    Return True if they intersect over x-axis.

        rect1: x0--------------x1
        rect2:          x0---------------x1
         or
        rect1:          x0---------------x1
        rect2: x0--------------x1
         or
        rect1: x0--------------x1
        rect2: x0--------------x1
         or
        rect1:          x0---------------x1
        rect2:             x0----------x1

         but
        rect1: x0--------------x1
        rect2:                   x0----------x1
    """

    return not (rect1.x1 < rect2.x0 or rect2.x1 < rect1.x0)


def intersects_over_y(rect1: pymupdf.Rect, rect2: pymupdf.Rect):
    """
    Check if rect1 and rect2 intersect over y-axis.
    Actual meaning: one beside the other.
    Return True if they intersect over y-axis.

        react1:           rect2
          y0
          |
          |
          |                y0
         y1                 |
                            |
                            |
                            |
                            y1
    """

    return not (rect1.y1 < rect2.y0 or rect2.y1 < rect1.y0)


def any_rect_between_over_y(
    rect1: pymupdf.Rect, rect2: pymupdf.Rect, rect_list: list[pymupdf.Rect]
):
    """
    Check if any rect of the list is between rect1 and rect2.
    Return the index + 1 of the first rect between rect1 and rect2.
    """

    for i, r in enumerate(rect_list, start=1):
        # check if r actually under some rect
        if intersects_over_x(rect1, r) or intersects_over_x(rect2, r):
            if rect1.y0 < r.y0 < rect2.y0:
                return i
    return 0


def any_rect_between_over_x(
    rect1: pymupdf.Rect, rect2: pymupdf.Rect, rect_list: list[pymupdf.Rect]
):
    """
    Check if any rect of the list is between rect1 and rect2.
    Return the index + 1 of the first rect between rect1 and rect2.
    """

    for i, r in enumerate(rect_list, start=1):
        # check if r actually under some rect
        if intersects_over_y(rect1, r) or intersects_over_y(rect2, r):
            if rect1.x0 < r.x0 < rect2.x0:
                return i
    return 0

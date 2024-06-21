import re
from typing import Protocol, Iterable
from urllib.parse import quote

from .elements import TextElement, TableElement, ImageElement
from .get_text_lines import get_raw_lines
from .identify_headers import IdentifyHeadersProtocol, DefaultHeadersIdentifier
from .rectangle_utils import intersects_rects
from .resolve_links import ResolveLinksProtocol, DefaultLinkResolver
from .._pymupdf import pymupdf


class WriteMarkdownProtocol(Protocol):
    def fit(self, pages: Iterable[pymupdf.Page]):
        """Read all text and prepare itself for markdown writing.
        Args:
            pages: list of pymupdf.Page objects to base the markdown writing on.
        """
        pass

    def write_markdown(
        self,
        page: pymupdf.Page,
        textpage: pymupdf.TextPage,
        text_elements: list[TextElement],
        image_elements: list[ImageElement],
        table_elements: list[TableElement],
    ) -> str:
        """Write markdown from page elements."""


GRAPHICS_TEXT = "\n![%s](%s)\n"
HEADER_TEXT = "<h%d>%s</h%d>"
LINK_TEXT = "<a href='%s'>%s</a>"
PLAIN_TEXT = "%s"
M_CODE = "<code>%s</code>"
B_CODE = "<b>%s</b>"
I_CODE = "<i>%s</i>"
TESSERACT_ANNOTATION = "<!--%s-->"

FMT_MAP = {
    "": PLAIN_TEXT,
    "m": M_CODE,
    "b": B_CODE,
    "i": I_CODE,
    "mb": M_CODE % B_CODE,
    "mi": M_CODE % I_CODE,
    "bi": B_CODE % I_CODE,
    "mbi": M_CODE % B_CODE % I_CODE,
}

BULLETS = ("- ", "* ", chr(0xF0A7), chr(0xF0B7), chr(0xB7), chr(8226), chr(9679))


class DefaultMarkdownWriter(WriteMarkdownProtocol):
    header_identifier: IdentifyHeadersProtocol
    link_resolver: ResolveLinksProtocol
    skip_footer: bool

    def __init__(
        self,
        header_identifier: IdentifyHeadersProtocol = None,
        link_resolver: ResolveLinksProtocol = None,
        skip_footer: bool = True,
    ):
        if header_identifier is None:
            header_identifier = DefaultHeadersIdentifier()
        if link_resolver is None:
            link_resolver = DefaultLinkResolver()
        self.header_identifier = header_identifier
        self.link_resolver = link_resolver
        self.skip_footer = skip_footer

    def fit(self, pages: Iterable[pymupdf.Page]):
        self.header_identifier.fit(pages)

    def write_text(
        self,
        page: pymupdf.Page,
        textpage: pymupdf.TextPage,
        clip: pymupdf.Rect,
        tab_rects: list[pymupdf.Rect] = None,
        img_rects: list[pymupdf.Rect] = None,
    ) -> str:
        """Output the text found inside the given clip.

        This is an alternative for plain text in that it outputs
        text enriched with markdown styling.
        The logic is capable of recognizing headers, body text, code blocks,
        inline code, bold, italic and bold-italic styling.
        There is also some effort for list supported (ordered / unordered) in
        that typical characters are replaced by respective markdown characters.

        'tab_rects'/'img_rects' are lists of table, respectively image
        or vector graphic rectangles.
        General Markdown text generation skips these areas. Tables are written
        via their own 'to_markdown' method. Images and vector graphics are
        optionally saved as files and pointed to by respective markdown text.
        """

        # This is a list of tuples (linerect, spanlist)
        nlines = get_raw_lines(textpage, clip=clip, tolerance=3)

        if tab_rects is None:
            tab_rects = []
        if img_rects is None:
            img_rects = []

        self.link_resolver.fit(page)

        prev_lrect = None  # previous line rectangle
        prev_bno = None  # previous block number of line
        stack = []
        footer_area = pymupdf.Rect(
            0, page.rect.height * 0.95, page.rect.width, page.rect.height
        )

        for lrect, spans in nlines:
            # there may table or image inside the text block: skip them
            if intersects_rects(lrect, tab_rects) or intersects_rects(lrect, img_rects):
                continue

            # it may be a footer
            if self.skip_footer and lrect in footer_area:
                continue

            span0 = spans[0]
            bno = span0["block"]  # block number of line
            if bno != prev_bno and prev_bno is not None:
                stack.append("\n")  # new block
                prev_bno = bno

            if (  # check if we need another line break
                prev_lrect
                and lrect.y1 - prev_lrect.y1 > lrect.height * 1.5
                or span0["text"].startswith("[")
                or span0["text"].startswith(BULLETS)
                or span0["flags"] & 1  # superscript?
            ):
                stack.append("\n")
            prev_lrect = lrect

            span_fmts = []
            span_texts = []
            for i, s in enumerate(spans):  # iterate spans of the line
                # decode font properties
                fmt = ""
                if s["flags"] & 8:
                    fmt += "m"
                if s["flags"] & 16:
                    fmt += "b"
                if s["flags"] & 2:
                    fmt += "i"
                span_fmts.append(fmt)
                link = self.link_resolver.resolve_link(s["bbox"])
                text = s["text"]
                if link:
                    text = LINK_TEXT % (link, text)
                span_texts.append(text)

            # group consecutive spans with same format
            _ = []
            for fmt, text in zip(span_fmts, span_texts):
                _.append(FMT_MAP[fmt] % text.strip())
            text_from_spans = " ".join(_)

            hdr_level = self.header_identifier.get_header_id(span0, page=page)
            if hdr_level is not None:
                text_from_spans = HEADER_TEXT % (hdr_level, text_from_spans, hdr_level)
            stack.append(text_from_spans)

            stack.append("\n")

        out_string = ""
        for s in stack:
            if not s.startswith("\n") and not s.startswith("<"):
                if not out_string.endswith("\n") and not out_string.endswith(" "):
                    out_string += " "
            out_string += s

        out_string = re.sub(r" \n", "\n", out_string)
        out_string = re.sub(r" {2,}", " ", out_string)
        out_string = re.sub(r"\n{3,}", "\n\n", out_string)

        return out_string

    def write_markdown(
        self,
        page: pymupdf.Page,
        textpage: pymupdf.TextPage,
        text_elements: list[TextElement],
        image_elements: list[ImageElement],
        table_elements: list[TableElement],
    ) -> str:
        sorted_layout = []
        sorted_layout.extend(text_elements)
        sorted_layout.extend(image_elements)
        sorted_layout.extend(table_elements)
        # top-to-bottom, left-to-right
        sorted_layout.sort(key=lambda j: (j.rect.y0, j.rect.x0))
        tab_rects = [obj.rect for obj in table_elements]
        img_rects = [obj.rect for obj in image_elements]

        md_string = ""

        for obj in sorted_layout:
            if isinstance(obj, TextElement):
                md_string += self.write_text(
                    page,
                    textpage,
                    obj.rect,
                    tab_rects=tab_rects,
                    img_rects=img_rects,
                )
            elif isinstance(obj, ImageElement):
                if obj.path:
                    md_string += GRAPHICS_TEXT % (obj.alt, quote(obj.path.as_posix()))
                if obj.annotation:
                    md_string += TESSERACT_ANNOTATION % obj.annotation
            elif isinstance(obj, TableElement):
                md_string += "\n" + obj.table.to_markdown(clean=True)

        md_string = md_string.strip()

        return md_string

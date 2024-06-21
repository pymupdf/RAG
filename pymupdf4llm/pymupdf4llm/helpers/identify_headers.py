__all__ = ["IdentifyHeadersProtocol", "DefaultHeadersIdentifier", "HeaderLevel"]

from collections import Counter
from enum import IntEnum
from typing import Protocol, Iterable

from .get_text_lines import is_white
from .._pymupdf import pymupdf


class HeaderLevel(IntEnum):
    """Header levels for text titles."""

    H1 = 1
    H2 = 2
    H3 = 3
    H4 = 4
    H5 = 5
    H6 = 6


class IdentifyHeadersProtocol(Protocol):
    def fit(self, pages: Iterable[pymupdf.Page]):
        """Read all text and make a dictionary of fontsizes.

        Args:
            pages: list of pymupdf.Page objects to base the header identification on.
        """
        pass

    def get_header_id(self, span: dict, page: pymupdf.Page) -> HeaderLevel | None:
        """Return appropriate header level or None.

        Args:
            span: dictionary of text span properties from a "dict"/"rawdict" extraction
            page: pymupdf.Page object.
        """
        pass


class DefaultHeadersIdentifier(IdentifyHeadersProtocol):
    """Compute data for identifying header text."""

    header_id: dict[int, HeaderLevel]
    body_limit: float
    header_levels_count: int

    def __init__(self, body_limit: float = 12, header_levels_count: int = 2):
        self.body_limit = body_limit
        self.header_levels_count = header_levels_count

    def get_header_id(self, span: dict, page: pymupdf.Page) -> HeaderLevel | None:
        fontsize = round(span["size"])  # compute fontsize
        hdr_id = self.header_id.get(fontsize, None)
        return hdr_id

    def fit(self, pages: Iterable[pymupdf.Page]):
        fontsize_x_symbols = Counter()

        for page in pages:
            dct = pymupdf.utils.get_text(page, "dict", flags=pymupdf.TEXTFLAGS_TEXT)

            for span in [  # look at all non-empty horizontal spans
                s
                for b in dct["blocks"]
                for line in b["lines"]
                for s in line["spans"]
                if not is_white(s["text"])
            ]:
                fontsize = round(span["size"])
                fontsize_x_symbols[fontsize] += len(span["text"].strip())

        # maps a fontsize to a header level
        self.header_id = {}

        # If not provided, choose the most frequent font size as body text.
        # If no text at all on all pages, just use 12.
        # In any case all fonts not exceeding
        sorted_by_frequency = sorted(
            list(fontsize_x_symbols.items()),
            key=lambda i: i[1],
            reverse=True,
        )

        if sorted_by_frequency:
            b_limit = max(self.body_limit, sorted_by_frequency[0][0])
        else:
            b_limit = self.body_limit

        # identify up to self.header_levels_count font sizes as header candidates
        sizes = sorted(
            filter(lambda f: f > b_limit, fontsize_x_symbols.keys()),
            reverse=True,
        )[: self.header_levels_count]

        # make the header tag dictionary
        for i, size in enumerate(sizes, start=1):
            self.header_id[size] = HeaderLevel(i)

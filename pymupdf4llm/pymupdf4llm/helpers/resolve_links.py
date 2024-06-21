from typing import Protocol

from .._pymupdf import pymupdf


class ResolveLinksProtocol(Protocol):
    def resolve_link(self, rect) -> str | None:
        """Accept a rect and return the URI of the link it belongs to or None."""
        pass

    def fit(self, page: pymupdf.Page):
        """Read all links from a page and store them to be used in resolve_links."""
        pass


class DefaultLinkResolver(ResolveLinksProtocol):
    """Resolve links in PDF files."""

    links: list
    overlap: float

    def __init__(self, overlap: float = 0.7):
        self.links = []
        self.overlap = overlap

    def resolve_link(self, rect: pymupdf.Rect):
        # a link should overlap at least xx% of the span
        bbox_area = self.overlap * abs(rect)
        for link in self.links:
            hot = link["from"]  # the hot area of the link
            if not abs(hot & rect) >= bbox_area:
                continue  # does not touch the bbox
            return link["uri"]
        return None

    def fit(self, page: pymupdf.Page):
        self.links = [
            link for link in pymupdf.utils.get_links(page) if link["kind"] == 2
        ]

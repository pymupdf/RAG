from dataclasses import dataclass
from pathlib import Path

from .._pymupdf import pymupdf


@dataclass
class TextElement:
    rect: pymupdf.Rect


@dataclass
class ImageElement:
    """
    Mardkown: ![{alt}]({path})
    HTML: <img src="path" alt="{alt}">
    """

    rect: pymupdf.Rect
    alt: str | None = None
    path: Path | None = None
    annotation: str | None = None


@dataclass
class TableElement:
    rect: pymupdf.Rect
    table: pymupdf.table.Table

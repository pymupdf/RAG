__all__ = ["to_markdown", "LlamaMarkdownReader"]

from pymupdf4llm.pymupdf4llm.to_markdown import to_markdown
from pymupdf4llm.pymupdf4llm.helpers.identify_headers import DefaultHeadersIdentifier

__version__ = "0.0.5"
version = __version__
version_tuple = tuple(map(int, version.split(".")))


def LlamaMarkdownReader(*args, **kwargs):
    from .llama import pdf_markdown_reader

    return pdf_markdown_reader.PDFMarkdownReader(*args, **kwargs)

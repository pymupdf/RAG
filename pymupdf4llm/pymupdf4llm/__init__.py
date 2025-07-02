import pymupdf
from .helpers.pymupdf_rag import IdentifyHeaders, TocHeaders, to_markdown
from .versions_file import MINIMUM_PYMUPDF_VERSION, VERSION

if tuple(map(int, pymupdf.__version__.split("."))) < MINIMUM_PYMUPDF_VERSION:
    raise ImportError(f"Requires PyMuPDF v. {MINIMUM_PYMUPDF_VERSION}, but you have {pymupdf.__version__}")

__version__ = VERSION
version = VERSION
version_tuple = tuple(map(int, version.split(".")))


def LlamaMarkdownReader(*args, **kwargs):
    from .llama import pdf_markdown_reader

    return pdf_markdown_reader.PDFMarkdownReader(*args, **kwargs)

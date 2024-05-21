import pymupdf4llm
from pymupdf4llm import *


__version__ = "0.0.9"
version = __version__
version_tuple = tuple(map(int, version.split(".")))


def LlamaMarkdownReader(*args, **kwargs):
    from pymupdf4llm.llama import pdf_markdown_reader

    return pymupdf4llm.llama.pdf_markdown_reader.PDFMarkdownReader(*args, **kwargs)

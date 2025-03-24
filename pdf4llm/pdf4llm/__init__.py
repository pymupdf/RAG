import pymupdf4llm
from pymupdf4llm import *


__version__ = pymupdf4llm.__version__
version = pymupdf4llm.version
version_tuple = pymupdf4llm.version_tuple


def LlamaMarkdownReader(*args, **kwargs):
    from pymupdf4llm.llama import pdf_markdown_reader

    return pymupdf4llm.llama.pdf_markdown_reader.PDFMarkdownReader(*args, **kwargs)

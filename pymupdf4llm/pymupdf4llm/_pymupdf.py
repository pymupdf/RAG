__all__ = ["pymupdf"]

try:
    import pymupdf  # available with v1.24.3
except ImportError:
    import fitz as pymupdf

if pymupdf.pymupdf_version_tuple < (1, 24, 2):
    raise NotImplementedError("PyMuPDF version 1.24.2 or later is needed.")

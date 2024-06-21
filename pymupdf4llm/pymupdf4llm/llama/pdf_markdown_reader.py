from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .. import to_markdown
from .._pymupdf import pymupdf

try:
    from llama_index.core.readers.base import BaseReader
    from llama_index.core.schema import Document as LlamaIndexDocument

    print("Successfully imported LlamaIndex")
except ImportError:
    raise NotImplementedError("Please install required 'llama_index'.")


class PDFMarkdownReader(BaseReader):
    """Read PDF files using PyMuPDF library."""

    meta_filter: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None

    def __init__(
        self,
        meta_filter: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        self.meta_filter = meta_filter

    def load_data(
        self,
        file_path: Union[Path, str],
        extra_info: Optional[Dict] = None,
        **load_kwargs: Any,
    ) -> List[LlamaIndexDocument]:
        """Loads list of documents from PDF file and also accepts extra information in dict format.

        Args:
            file_path (Union[Path, str]): The path to the PDF file.
            extra_info (Optional[Dict], optional): A dictionary containing extra information. Defaults to None.
            **load_kwargs (Any): Additional keyword arguments to be passed to the load method.

        Returns:
            List[LlamaIndexDocument]: A list of LlamaIndexDocument objects.
        """
        if not isinstance(file_path, str) and not isinstance(file_path, Path):
            raise TypeError("file_path must be a string or Path.")

        if not extra_info:
            extra_info = {}

        if extra_info and not isinstance(extra_info, dict):
            raise TypeError("extra_info must be a dictionary.")

        # extract text header information
        doc: pymupdf.Document = pymupdf.open(file_path)
        docs = []

        for page in doc:
            docs.append(self._process_doc_page(doc, extra_info, file_path, page.number))
        return docs

    # Helpers
    # ---

    def _process_doc_page(
        self,
        doc: pymupdf.Document,
        extra_info: Dict[str, Any],
        file_path: Union[Path, str],
        page_number: int,
    ):
        """Processes a single page of a PDF document."""
        extra_info = self._process_doc_meta(doc, file_path, page_number, extra_info)

        if self.meta_filter:
            extra_info = self.meta_filter(extra_info)

        output = to_markdown(doc, pages=[page_number])
        text = "\n\n-----\n\n".join([chunk["text"] for chunk in output["page_chunks"]])
        return LlamaIndexDocument(text=text, extra_info=extra_info)

    def _process_doc_meta(
        self,
        doc: pymupdf.Document,
        file_path: Union[Path, str],
        page_number: int,
        extra_info: Optional[Dict] = None,
    ):
        """Processes metas of a PDF document."""
        extra_info.update(doc.metadata)
        extra_info["page"] = page_number + 1
        extra_info["total_pages"] = len(doc)
        extra_info["file_path"] = str(file_path)

        return extra_info

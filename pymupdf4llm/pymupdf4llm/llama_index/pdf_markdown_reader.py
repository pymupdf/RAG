import asyncio
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import fitz
from fitz import Document as FitzDocument

try:
    from llama_index.core.readers.base import BaseReader
    from llama_index.core.schema import Document as LlamaIndexDocument

    print("All imports are successful.")
except ImportError:
    raise NotImplementedError("Please install 'llama_index' is needed.")


import pymupdf4llm


class PDFMardownReader(BaseReader):
    """Read PDF files using PyMuPDF library."""

    use_meta: bool = True
    meta_filter: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None

    def __init__(
        self,
        use_meta: bool = True,
        meta_filter: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        self.use_meta = use_meta
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

        doc: FitzDocument = fitz.open(file_path)

        docs = []
        for page in doc:
            docs.append(self._process_doc_page(doc, extra_info, file_path, page.number))
        return docs

    async def aload_data(
        self,
        file_path: Union[Path, str],
        extra_info: Optional[Dict] = None,
        **load_kwargs: Any,
    ) -> List[LlamaIndexDocument]:
        """Asynchronously loads list of documents from PDF file and also accepts extra information in dict format.

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

        doc: FitzDocument = fitz.open(file_path)

        tasks = []
        for page in doc:
            tasks.append(
                self._aprocess_doc_page(doc, extra_info, file_path, page.number)
            )
        return await asyncio.gather(*tasks)

    # Helpers
    # ---
    async def _aprocess_doc_page(
        self,
        doc: FitzDocument,
        extra_info: Dict[str, Any],
        file_path: str,
        page_number: int,
    ):
        """Asynchronously processes a single page of a PDF document."""
        return self._process_doc_page(doc, extra_info, file_path, page_number)

    def _process_doc_page(
        self,
        doc: FitzDocument,
        extra_info: Dict[str, Any],
        file_path: str,
        page_number: int,
    ):
        """Processes a single page of a PDF document."""
        if self.use_meta:
            extra_info = self._process_meta(doc, file_path, page_number, extra_info)

        text = pymupdf4llm.to_markdown(doc, [page_number])
        return LlamaIndexDocument(text=text, extra_info=extra_info)

    def _process_meta(
        self,
        doc: FitzDocument,
        file_path: Union[Path, str],
        page_number: int,
        extra_info: Optional[Dict] = None,
    ):
        """Processes metas of a PDF document."""
        extra_info.update(doc.metadata)
        extra_info["page_number"] = f"{page_number+1}"
        extra_info["total_pages"] = len(doc)
        extra_info["file_path"] = str(file_path)

        if self.meta_filter:
            extra_info = self.meta_filter(extra_info)

        return extra_info

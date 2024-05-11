import os

import pytest
from llama_index.core.schema import Document as LlamaIndexDocument

try:
    from llama_index.core.readers.base import BaseReader
    from llama_index.core.schema import Document as LlamaIndexDocument

    print("All imports are successful.")
except ImportError:
    raise NotImplementedError("Please install 'llama_index' is needed.")


from pymupdf4llm.pymupdf4llm.llama_index.pdf_markdown_reader import PDFMardownReader

PDF = "input.pdf"


def _get_test_file_path(file_name: str, __file__: str = __file__) -> str:
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        ".." "helpers",
        file_name,
    )
    file_path = os.path.normpath(file_path)
    return file_path


def test_load_data():
    # Arrange
    # ---
    pdf_reader = PDFMardownReader()
    path = _get_test_file_path(PDF, __file__)
    extra_info = {"test_key": "test_value"}

    # Act
    # ---
    documents = pdf_reader.load_data(path, extra_info)

    # Assert
    # ---
    assert isinstance(documents, list)
    for doc in documents:
        assert isinstance(doc, LlamaIndexDocument)


def test_load_data_with_invalid_file_path():
    # Arrange
    # ---
    pdf_reader = PDFMardownReader()
    extra_info = {"test_key": "test_value"}
    path = "fake/path"

    # Act & Assert
    # ---
    with pytest.raises(Exception):
        pdf_reader.load_data(path, extra_info)


def test_load_data_with_invalid_extra_info():
    # Arrange
    # ---
    pdf_reader = PDFMardownReader()
    extra_info = "invalid_extra_info"
    path = _get_test_file_path(PDF, __file__)

    # Act & Assert
    # ---
    with pytest.raises(TypeError):
        pdf_reader.load_data(path, extra_info)


@pytest.mark.asyncio
async def test_aload_data():
    # Arrange
    # ---
    pdf_reader = PDFMardownReader(use_meta=True)
    extra_info = {"test_key": "test_value"}
    path = _get_test_file_path(PDF, __file__)

    # Act
    # ---
    documents = await pdf_reader.aload_data(path, extra_info)

    # Assert
    # ---
    expected_key = "test_key"
    expected_value = "test_value"

    assert isinstance(documents, list)
    for doc in documents:
        assert expected_key in doc.metadata
        assert expected_value in doc.metadata.values()
        assert isinstance(doc, LlamaIndexDocument)


@pytest.mark.asyncio
async def test_aload_data_with_invalid_file_path():
    # Arrange
    # ---
    pdf_reader = PDFMardownReader()
    extra_info = {"test_key": "test_value"}

    # Act
    # ---
    path = "Fake/path"

    # Assert
    # ---
    with pytest.raises(Exception):
        await pdf_reader.aload_data(path, extra_info)


@pytest.mark.asyncio
async def test_aload_data_with_invalid_extra_info():
    # Arrange
    # ---
    pdf_reader = PDFMardownReader()
    extra_info = "invalid_extra_info"

    # Act
    # ---
    path = _get_test_file_path(PDF, __file__)

    # Assert
    # ---
    with pytest.raises(TypeError):
        await pdf_reader.aload_data(path, extra_info)

from dataclasses import dataclass

import pymupdf
import pytest


@dataclass
class Document:
    name: str
    url: str


# Inspired by https://github.com/py-pdf/benchmarks/blob/main/benchmark.py
docs = [
    Document(name="2201.00214", url="https://arxiv.org/pdf/2201.00214.pdf"),
    Document(name="2201.00151", url="https://arxiv.org/pdf/2201.00151.pdf"),
    Document(name="1707.09725", url="https://arxiv.org/pdf/1707.09725.pdf"),
    Document(name="2201.00021", url="https://arxiv.org/pdf/2201.00021.pdf"),
    Document(name="2201.00037", url="https://arxiv.org/pdf/2201.00037.pdf"),
    Document(name="2201.00069", url="https://arxiv.org/pdf/2201.00069.pdf"),
    Document(name="2201.00178", url="https://arxiv.org/pdf/2201.00178.pdf"),
    Document(name="2201.00201", url="https://arxiv.org/pdf/2201.00201.pdf"),
    Document(name="1602.06541", url="https://arxiv.org/pdf/1602.06541.pdf"),
    Document(name="2201.00200", url="https://arxiv.org/pdf/2201.00200.pdf"),
    Document(name="2201.00022", url="https://arxiv.org/pdf/2201.00022.pdf"),
    Document(name="2201.00029", url="https://arxiv.org/pdf/2201.00029.pdf"),
    Document(name="1601.03642", url="https://arxiv.org/pdf/1601.03642.pdf"),
]


async def fetch_file(doc: Document) -> bytes:
    import httpx

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(doc.url)
        return response.content


@pytest.mark.parametrize("doc", docs)
@pytest.mark.asyncio
async def test_extract_text(doc: Document):
    import pymupdf4llm

    content = await fetch_file(doc)
    as_pymupdf_doc = pymupdf.Document(stream=content, filetype="pdf")
    text = pymupdf4llm.to_markdown(as_pymupdf_doc, graphics_limit=1000)
    print(len(text))

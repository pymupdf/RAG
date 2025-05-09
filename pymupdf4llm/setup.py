import os

import setuptools

setup_py_cwd = os.path.dirname(__file__)
with open(os.path.join(setup_py_cwd, "README.md"), encoding="utf-8") as f:
    readme = f.read()

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Topic :: Utilities",
]
requires = ["pymupdf>=1.25.5"]

setuptools.setup(
    name="pymupdf4llm",
    version="0.0.23",
    author="Artifex",
    author_email="support@artifex.com",
    description="PyMuPDF Utilities for LLM/RAG",
    packages=setuptools.find_packages(),
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requires,
    license="GNU AFFERO GPL 3.0",
    url="https://github.com/pymupdf/RAG",
    classifiers=classifiers,
    package_data={
        "pymupdf4llm": ["LICENSE", "helpers/*.py", "llama/*.py"],
    },
    project_urls={
        "Documentation": "https://pymupdf.readthedocs.io/",
        "Source": "https://github.com/pymupdf/RAG/tree/main/pymupdf4llm/pymupdf4llm",
        "Tracker": "https://github.com/pymupdf/RAG/issues",
        "Changelog": "https://github.com/pymupdf/RAG/blob/main/CHANGES.md",
    },
)

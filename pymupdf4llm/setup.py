import os
import setuptools
from pathlib import Path

setup_py_cwd = os.path.dirname(__file__)
with open(os.path.join(setup_py_cwd, "README.md"), encoding="utf-8") as f:
    readme = f.read()

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Utilities",
]

version = "0.0.26"
requires = ["pymupdf>=1.26.3"]

text = requires[0].split("=")[1]
text = tuple(map(int, text.split(".")))
text = f"MINIMUM_PYMUPDF_VERSION = {text}\nVERSION = '{version}'\n"
Path("pymupdf4llm/versions_file.py").write_text(text)

setuptools.setup(
    name="pymupdf4llm",
    version=version,
    author="Artifex",
    author_email="support@artifex.com",
    description="PyMuPDF Utilities for LLM/RAG",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requires,
    python_requires=">=3.9",
    license="Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License",
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

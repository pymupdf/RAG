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
requires = ["pymupdf>=1.24.2"]

setuptools.setup(
    name="pdf4llm",
    version="0.0.1",
    author="Artifex",
    author_email="support@artifex.com",
    description="PyMuPDF Utilities for LLM/RAG",
    packages=setuptools.find_packages(),
    package_dir={"": "."},
    package_data={
        "pdf4llm": [
            "LICENSE",
            "helpers/input.pdf",
            "helpers/input2.pdf",
            "helpers/pymupdf_rag.py",
            "helpers/README.md",
            "country-capitals/country-capitals.py",
            "country-capitals/national-capitals.pdf",
            "country-capitals/README.md",
            "GUI/browser-app.py",
            "GUI/README.md",
        ]
    },
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requires,
    license="GNU AFFERO GPL 3.0",
    url="https://github.com/pymupdf/RAG",
    classifiers=classifiers,
    project_urls={},
)

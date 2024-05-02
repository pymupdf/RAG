# PyMuPDF4LLM documentation

Welcome to the documentation. This documentation relies on [Sphinx](https://www.sphinx-doc.org/en/master/) to publish HTML docs from markdown files written with [restructured text](https://en.wikipedia.org/wiki/ReStructuredText) (RST).


## Sphinx version

This README assumes you have [Sphinx v5.0.2 or above installed](https://www.sphinx-doc.org/en/master/usage/installation.html) on your system.


## Updating the documentation

Within `src` update the associated restructured text (`.rst`) files. These files represent the corresponding document pages.


## Building HTML documentation

- Ensure you have the `pydata` theme installed:

`pip install pydata-sphinx-theme`

- Ensure you have `Sphinx design` installed:

`pip install sphinx-design`

- Ensure you have `Sphinx Copy Button` installed:

`pip install sphinx-copybutton`

- From the "docs" location run:

`sphinx-build -b html src build/html`

This then creates the HTML documentation within `build/html`.

> Use: `sphinx-build -a -b html src build/html` to build all, including the assets in `_static` (important if you have updated CSS).


- Alternatively you can also use [Sphinx Autobuild](https://pypi.org/project/sphinx-autobuild/) and do:

`sphinx-autobuild src _build/html`

This will ensure that the documentation runs in a localhost and will also hot-reload changes.


## Building the Japanese documentation

- From the "src" location run:

`sphinx-build -a -b html -D language=ja . _build/html/ja`


- Updating, after changes on the `main` branch and a sync with the main `en` .rst files, from the "docs" location, do:

`sphinx-build -b gettext . _build/gettext`

then:

`sphinx-intl update -p _build/gettext -l ja`

---



For full details see: [Using Sphinx](https://www.sphinx-doc.org/en/master/usage/index.html) 




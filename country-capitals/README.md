# Demonstration of an RAG Chatbot Using PyMuPDF

This script starts an OpenAI RAG (Retrieval Augmented Generation) chatbot.

The data fed into to chatbot client are tabular data extracted from a 6-page
PDF.

## How it Works
The content of the data is a list of almost 200 countries, their capital
cities, city population and its percentage of the country's total
population.

The script is started like any Python script and without parameters. Upon
start, a function is invoked which calls PyMuPDF to read the PDF, extract the
table data and return a CSV-like string containing the table's content.

After the chatbot has finished interpreting the data, the user may start asking
questions via Read-Evaluate-Print loop (REPL).

## Information Retrieved for Responses
Remarkably, the chatbot "realizes" the geographic and demographic context
established by the PDF's data. This enables it to access the right knowledge
resources on the internet for completing the information required to answer the user 
questions.

For example, it will understand it has to look up **cities** and **countries** when being
asked for words that do not occur in the PDF.

For instance, the country
**Liechtenstein** is not in the PDF, but asking for it or its capital city,
Vaduz will deliver correct information, including population numbers or
short abstracts of city and country.

## Getting Started

Execute all of the following commands in a terminal:

```bash
python pip install -U pip
python pip install -U pymupdf
python pip install -U openai
```

Visit https://github.com/openai/openai-cookbook to learn how to register on
OpenAI's website and request an API key.

Copy this folder to your machine, then edit the script, type in your API key in this line `API_KEY = "your OpenAI API key goes here"` and save. Then open a terminal in the folder and execute the following command:

```bash
python country-capitals.py
```

After a few seconds, the following should be displayed.

## Example Session
Please note how the chatbot searches the internet for information required to answer the question whenever the loaded text is insufficient.

```bash
Loaded 204 table rows from file 'national-capitals.pdf'.

Ready - ask questions or exit with q/Q:
==> what is the capital of Germany?
Response:

The capital of Germany is Berlin.
----------
==> Berlin's population, absolute and relative?
Response:

Berlin's population as of 2021 is 3,677,472. This makes up about 4.4% of the total population of Germany.
----------
==> is Vaduz part of the text, and if not, do you know about it?
Response:

No, Vaduz is not part of the text. It is the capital of Liechtenstein.
----------
==> the 10 smallest capital cities of the world?
Response:

1. Vatican City (Vatican City) - 0.44 km²
2. Ngerulmud (Palau) - 0.57 km²
3. San Marino (San Marino) - 7.09 km²
4. Monaco (Monaco) - 2.02 km²
5. Gibraltar (Gibraltar) - 6 km²
6. Tuvalu (Funafuti) - 2.18 km²
7. Nauru (Yaren) - 21 km²
8. Malta (Valletta) - 0.8 km²
9. Andorra la Vella (Andorra) - 12.86 km²
10.
----------
==> the 10 smallest capital cities in terms of population?
Response:

1. Vatican City (Vatican City) - 453
2. Ngerulmud (Palau) - 271
3. Adamstown (Pitcairn Islands) - 40
4. Funafuti (Tuvalu) - 6,320
5. Alofi (Niue) - 597
6. Yaren (Nauru) - 747
7. South Tarawa (Kiribati) - 50,182
8. Stanley (Falkland Islands) - 2,460
9. Flying Fish Cove (Christmas Island) - 1,599
10. Roseau (Dominica) - 14,725
----------
```

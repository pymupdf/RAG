"""
This script implements an RAG chatbot using OpenAI and PyMuPDF.

It is intended as a simple example for demonstration purposes primarily.

When the chatbot is started, it will call PyMuPDF to read a PDF that contains
a list of countries, their capital cities and city populations.

This call to PyMuPDF will happen only once. Thereafter, the user can start
asking questions in a Read-Evaluate-Prompt loop - or end the session.

Although the data in the PDF are of course limited, the user may ask questions
that require accessing sources present in the internet and may refer to
almost arbitrary geographic or demographic information.

The chatbot is capable of integrating disparate information sources delivering
a meaningful response.
"""

import fitz
import textwrap
from openai import OpenAI

# Example for reading the OpenAI API key
API_KEY = "your OpenAI API key goes here"

# create an OpenAI client using the API key
client = OpenAI(api_key=API_KEY)


def extract_text_from_pdf(pdf_path):
    """Read table content only all pages in the document."""
    doc = fitz.open(pdf_path)
    text = ""
    lines = 0  # counts table rows
    header = ""
    for page in doc:  # only read the table rows
        tabs = page.find_tables()
        for t in tabs:
            # on first page prepend an external header where present
            if page.number == 0 and t.header.external:
                header = (
                    ";".join([n if n is not None else "" for n in t.header.names])
                    + "\n"
                )
                text += header

            for row in t.extract():  # read the table rows
                row_text = ";".join(row) + "\n"
                if row_text != header:  # only output header line once
                    text += row_text
                    lines += 1
    doc.close()
    print(f"Loaded {lines} table rows from file '{doc.name}'.\n")
    return text


# models "gpt-3.5-turbo-instruct" is for text
def generate_response_with_chatgpt(prompt):
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",  # Choose appropriate model
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()


filename = "national-capitals.pdf"
pdf_text = extract_text_from_pdf(filename)

print("Ready - ask questions or exit with q/Q:")
while True:
    user_query = input("==> ")
    if user_query.lower().strip() == "q":
        break
    prompt = pdf_text + "\n\n" + user_query
    response = generate_response_with_chatgpt(prompt)
    print("Response:\n")
    for line in textwrap.wrap(response, width=70):
        print(line)
    print("-" * 10)

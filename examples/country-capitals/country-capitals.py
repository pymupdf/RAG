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

import pymupdf
import textwrap
from openai import OpenAI

# Example for reading the OpenAI API key
API_KEY = "your OpenAI API key goes here"

# create an OpenAI client using the API key
client = OpenAI(api_key=API_KEY)


def extract_text_from_pdf(pdf_path):
    """Read table content only of all pages in the document.

    Chatbots typically have limitations on the amount of data that can
    can be passed in (number of tokens).

    We therefore only extract information on the PDF's pages that are
    contained in tables.
    As we even know that the PDF actually contains ONE logical table
    that has been segmented for reporting purposes, our approach
    is the following:
    * The cell contents of each table row are joined into one string
      separated by ";".
    * If table segment on the first page also has an external header row,
      join the column names separated by ";". Also ignore any subsequent
      table row that equals the header string. This deals with table
      header repeat situations.
    """
    # open document
    doc = pymupdf.open(pdf_path)

    text = ""  # we will return this string
    row_count = 0  # counts table rows
    header = ""  # overall table header: output this only once!

    # iterate over the pages
    for page in doc:
        # only read the table rows on each page, ignore other content
        tables = page.find_tables()  # a "TableFinder" object
        for table in tables:

            # on first page extract external column names if present
            if page.number == 0 and table.header.external:
                # build the overall table header string
                # technical note: incomplete / complex tables may have
                # "None" in some header cells. Just use empty string then.
                header = (
                    ";".join(
                        [
                            name if name is not None else ""
                            for name in table.header.names
                        ]
                    )
                    + "\n"
                )
                text += header
                row_count += 1  # increase row counter

            # output the table body
            for row in table.extract():  # iterate over the table rows

                # again replace any "None" in cells by an empty string
                row_text = (
                    ";".join([cell if cell is not None else "" for cell in row]) + "\n"
                )
                if row_text != header:  # omit duplicates of header row
                    text += row_text
                    row_count += 1  # increase row counter
    doc.close()  # close document
    print(f"Loaded {row_count} table rows from file '{doc.name}'.\n")
    return text


# use model "gpt-3.5-turbo-instruct" for text
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

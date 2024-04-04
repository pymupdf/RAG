# Using PyMuPDF in an RAG (Retrieval-Augmented Generation) Chatbot Environment

This repository contains examples showing how PyMuPDF can be used as a data feed for RAG-based chatbots.

Examples include scripts that start chatbots - either as simple CLI programs in REPL mode or browser-based GUIs.
Chatbot scripts follow this general structure:

1. **Extract Text**: Use PyMuPDF to extract text from one or more pages from one or more PDFs. Depending on the specific requirement this may be all text or only text contained in tables, the Table of Contents, etc.
This will generally be implemented as one or more Python functions called by any of the following events - which implement the actual chatbot functionality.
2. **Indexing the Extracted Text**: Index the extracted text for efficient retrieval. This index will act as the knowledge base for the chatbot.
3. **Query Processing**: When a user asks a question, process the query to determine the key information needed for a response.
4. **Retrieving Relevant Information**: Search your indexed knowledge base for the most relevant pieces of information related to the user's query.
5. **Generating a Response**: Use a generative model to generate a response based on the retrieved information.

As a specialty, folder "convert-to-markdown" contains a script that is capable to convert PDF pages into **_text strings in Markdown format_**, which includes standard text as well as table-based text in a consistent and integrated view. This is especially important in RAG environments.
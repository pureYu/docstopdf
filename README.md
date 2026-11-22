
# MS Word Document Parser and PDF Generator

## Overview
This Python application is designed to parse Microsoft Word documents that contain text and tables with data. The primary functionality includes parsing the content of the Word document, along with comments and changes history, and storing the resulting JSON data in MongoDB for further processing by other services. Additionally, the application can generate a PDF document from the parsed JSON data.

## Features
- Parsing Word documents with structured text and tables.
- Extracting comments and changes history.
- Storing parsing results in MongoDB in JSON format.
- Generating PDF documents from parsed data.

## File Structure
- Sample input files and resulting PDF files are placed in the `data/` folder.
- MongoDB data can be found in `mongodb_data` folder.

## Requirements
- Docker for setting up the application and MongoDB services.

## How to Run
1. Place your Word document in the `data/` folder.
2. Run `docker compose up` to start the services.
3. Run `python app.py ../data/sample_word_extended.docx` or just  `python app.py` (default file will be used if not input file provided)
4. The application will process the Word document and store the results in MongoDB.
5. PDF version of the document will be saved in the same folder.


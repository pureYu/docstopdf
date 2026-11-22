import pdfplumber
from .DocumentParser import DocumentParser

class PdfDocumentParser(DocumentParser):
    """
    Parser class for PDF documents.
    Extracts text and tables from a PDF file.
    """
    def __init__(self, file_path):
        super().__init__(file_path)

    def parse(self):
        try:
            with pdfplumber.open(self.file_path) as pdf:
                parsed_data = {
                    "paragraphs": self._parse_paragraphs(pdf),
                    "content": self._parse_groups(pdf)
                }
            self.logger.info("PDF document parsed successfully.")
        except Exception as e:
            self.logger.error(f"Error processing PDF document: {e}", exc_info=True)
            raise

        return parsed_data

    def _parse_paragraphs(self, pdf):
        paragraphs = []
        for page in pdf.pages:
            para_text = page.extract_text()
            paragraphs.append(self._process_text_string(para_text))
        return paragraphs

    def _parse_groups(self, pdf):
        tables = []
        for page in pdf.pages:
            for table in page.extract_tables():
                tables.append(table)
        return tables

import camelot
from pdfminer.high_level import extract_text
from .DocumentParser import DocumentParser

class PdfDocumentParser(DocumentParser):
    """
    Parser class for PDF documents.
    Extracts paragraphs and tables from a PDF file using pdfminer.six and camelot.
    """
    def __init__(self, file_path):
        super().__init__(file_path)

    def parse(self):
        try:
            parsed_data = {
                "paragraphs": self._parse_paragraphs(),
                "content": self._parse_tables()
            }
            self.logger.info("PDF document parsed successfully.")
            return parsed_data
        except Exception as e:
            self.logger.error(f"Error processing PDF document: {e}", exc_info=True)
            raise

    def _parse_paragraphs(self):
        paragraphs = []
        text = extract_text(self.file_path)
        if text:
            paragraphs.extend([{"type": "text", "content": para} for para in text.split('\n\n') if para.strip()])
        return paragraphs

    def _parse_tables(self):
        tables = camelot.read_pdf(self.file_path, pages="all", flavor="lattice")
        formatted_tables = []
        for table in tables:
            # Convert each table to a list of dictionaries (one per row)
            headers = table.df.iloc[0].tolist()
            rows = [dict(zip(headers, row)) for row in table.df.iloc[1:].values.tolist()]
            formatted_tables.append({"headers": headers, "rows": rows})
        return formatted_tables

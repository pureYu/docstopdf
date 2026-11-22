from .PdfDocumentParser import PdfDocumentParser
from .WordDocumentParser import WordDocumentParser


class DocumentParserFactory:
    @staticmethod
    def get_parser(file_path):
        if file_path.endswith(".docx"):
            return WordDocumentParser(file_path)
        elif file_path.endswith(".pdf"):
            return PdfDocumentParser(file_path)
        else:
            raise ValueError("Unsupported file format")

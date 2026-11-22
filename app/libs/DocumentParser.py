import logging
import re
from .MongoDBClient import MongoDBClient


class DocumentParser:

    def __init__(self, file_path):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
        self.mongo_client = MongoDBClient()
        self.errors = []
        self.warnings = []

    def parse(self):
        raise NotImplementedError("Parse method must be implemented by subclasses")

    def save_parse_results(self, parsed_data):
        document_id = self.mongo_client.insert_document(self.file_path, parsed_data, self.errors, self.warnings)
        self.logger.info(f"Document data saved into DB, id={document_id}")
        return document_id

    def _process_text_string(self, input_str):
        # checkboxes
        unchecked_checkbox = "\u2610"
        checked_checkbox = ["\u2611", "\u2612"]

        parts = re.split(f"({unchecked_checkbox}|{'|'.join(checked_checkbox)})", input_str)

        result = []
        for part in parts:
            if part == unchecked_checkbox:
                result.append({"type": "checkbox", "checked": False})
            elif part in checked_checkbox:
                result.append({"type": "checkbox", "checked": True})
            elif part.strip():  # Ensure it's not just whitespace
                result.append({"type": "text", "content": part.strip()})
        if not result:
            result.append({"type": "text", "content": ""})

        return result

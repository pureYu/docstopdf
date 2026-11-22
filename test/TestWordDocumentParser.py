import unittest
from unittest.mock import patch, MagicMock
from app.libs.WordDocumentParser import WordDocumentParser


class TestWordDocumentParser(unittest.TestCase):

    def setUp(self):
        self.doc_path = "data/sample_word.docx"
        self.mongo_patch = patch("app.libs.DocumentParser.MongoDBClient")
        self.mock_mongo = self.mongo_patch.start()
        self.mock_mongo.return_value.insert_document.return_value = "mocked_document_id"
        self.parser = WordDocumentParser(self.doc_path)

    def tearDown(self):
        self.mongo_patch.stop()

    @patch('app.libs.WordDocumentParser.Document')
    def test_document_initialization_failure(self, mock_doc):
        mock_doc.side_effect = Exception("Failed to open document")
        with self.assertRaises(Exception):
            WordDocumentParser(self.doc_path)

    def test_parse_paragraphs(self):
        parsed_data = self.parser.parse()
        self.assertIsNotNone(parsed_data)
        self.assertIn("paragraphs", parsed_data)
        self.assertTrue(isinstance(parsed_data['paragraphs'], list))

    def test_parse_tables(self):
        parsed_data = self.parser.parse()
        self.assertIn("content", parsed_data)
        self.assertTrue(isinstance(parsed_data['content'], list))

    def test_parse_table_structure(self):
        parsed_data = self.parser.parse()
        for table in parsed_data["content"]:
            self.assertIn("groupName", table)
            self.assertIn("content", table)

    def test_parse_comments(self):
        parsed_data = self.parser.parse()
        all_comments = [comment
                        for group in parsed_data["content"]
                        for item in group['content']
                        for key in item
                        if key != "key"  # Exclude the 'key' entries
                        for comment in item[key]["comments"]]
        self.assertTrue(isinstance(self.parser.comments, dict))
        self.assertEqual(len(all_comments), 2)

    def test_parse_cell_history(self):
        parsed_data = self.parser.parse()
        all_histories = [history_item
                         for group in parsed_data["content"]
                         for item in group["content"]
                         for key in item
                         if key != "key"
                         for history_item in item[key]["history"]]
        self.assertEqual(len(all_histories), 3)

    def test_document_validation_errors(self):
        self.parser.validator = MagicMock()
        self.parser.validator.validate.return_value = False
        self.parser.validator.get_errors.return_value = [{"type": "Error", "message": "Invalid Document"}]
        self.parser.validator.get_warnings.return_value = []

        result = self.parser.parse()
        self.assertIsNone(result)
        # kwargs = {"file_path": "data/sample_word.docx", "parsed_data": None, "errors": [{"type": "Error", "message": "Invalid Document"}], "warnings": []}
        self.assertEqual(result, None)
        self.parser.save_parse_results(result)
        self.parser.mongo_client.insert_document.assert_called_with("data/sample_word.docx",
                                                                    None,
                                                                    [{"type": "Error", "message": "Invalid Document"}],
                                                                    [])  # Ensure no DB interaction on validation failure

    def test_data_saving(self):
        parsed_data = self.parser.parse()
        self.parser.save_parse_results(parsed_data)
        self.parser.mongo_client.insert_document.assert_called_once()

    # @patch('app.libs.DocumentParser.logging')
    # def test_error_logging(self, mock_logging):
    #     self.parser.validator.side_effect = Exception("Validation Exception")
    #     with self.assertRaises(Exception):
    #         self.parser.parse()
    #     mock_logging.getLogger.return_value.error.assert_called_with("Validation Exception")


if __name__ == '__main__':
    unittest.main()

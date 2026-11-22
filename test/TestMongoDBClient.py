import unittest
from unittest.mock import MagicMock, patch
from app.libs.MongoDBClient import MongoDBClient
from bson import ObjectId
from pymongo.errors import PyMongoError


class TestMongoDBClient(unittest.TestCase):

    def setUp(self):
        self.mocked_mongo_client = MagicMock()
        self.patcher = patch('pymongo.MongoClient', return_value=self.mocked_mongo_client)
        self.patcher.start()
        self.db_uri = "mocked_uri"
        self.db_name = "mocked_db"
        self.collection_name = "mocked_collection"
        self.mongo_client = MongoDBClient()

    def tearDown(self):
        self.patcher.stop()

    def test_insert_document(self):
        mocked_insert_one = self.mocked_mongo_client[self.db_name][self.collection_name].insert_one
        mocked_insert_one.return_value.inserted_id = "mocked_id"
        file_path = "mocked_path"
        parsed_data = {"data_key": "data_value"}
        errors = []
        warnings = ["warning1", "warning2"]
        result = self.mongo_client.insert_document(file_path, parsed_data, errors, warnings)
        expected_document = {
            "file_path": file_path,
            "parsed_data": parsed_data,
            "errors": errors,
            "warnings": warnings
        }
        mocked_insert_one.assert_called_once_with(expected_document)
        self.assertEqual(result, "mocked_id")

    def test_insert_document_with_errors(self):
        mocked_insert_one = self.mocked_mongo_client[self.db_name][self.collection_name].insert_one
        mocked_insert_one.return_value.inserted_id = "mocked_id"
        file_path = "mocked_path"
        parsed_data = {"data_key": "data_value"}
        errors = ["error1", "error2"]
        warnings = []
        result = self.mongo_client.insert_document(file_path, parsed_data, errors, warnings)
        expected_document = {
            "file_path": file_path,
            "parsed_data": None,
            "errors": errors,
            "warnings": warnings
        }
        mocked_insert_one.assert_called_once_with(expected_document)
        self.assertEqual(result, "mocked_id")

    def test_insert_document_exception(self):
        self.mocked_mongo_client[self.db_name][self.collection_name].insert_one.side_effect = PyMongoError("Mocked error")
        file_path = "mocked_path"
        parsed_data = {"data_key": "data_value"}
        errors = []
        warnings = []
        with self.assertRaises(PyMongoError):
            self.mongo_client.insert_document(file_path, parsed_data, errors, warnings)

    def test_find_document(self):
        document_id = ObjectId()
        expected_document = {"_id": document_id, "data": "mocked_data"}
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.return_value = expected_document
        result = self.mongo_client.find_document(document_id)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.assert_called_with({"_id": document_id})
        self.assertEqual(result, expected_document)

    def test_find_document_not_found(self):
        document_id = ObjectId()
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.return_value = None
        result = self.mongo_client.find_document(document_id)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.assert_called_with({"_id": document_id})
        self.assertIsNone(result)

    def test_find_document_exception(self):
        document_id = ObjectId()
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.side_effect = PyMongoError("Mocked error")
        with self.assertRaises(PyMongoError):
            self.mongo_client.find_document(document_id)

    def test_update_document_successful(self):
        document_id = ObjectId()
        update_values = {"field": "updated_value"}
        mock_update_result = MagicMock(matched_count=1, modified_count=1)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].update_one.return_value = mock_update_result
        result = self.mongo_client.update_document(document_id, update_values)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].update_one.assert_called_with({"_id": document_id}, {"$set": update_values})
        self.assertEqual(result, mock_update_result)

    def test_update_document_failure(self):
        document_id = ObjectId()
        update_values = {"field": "updated_value"}
        mock_update_result = MagicMock(matched_count=0, modified_count=0)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].update_one.return_value = mock_update_result
        result = self.mongo_client.update_document(document_id, update_values)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].update_one.assert_called_with({"_id": document_id}, {"$set": update_values})
        self.assertEqual(result, mock_update_result)

    def test_update_document_exception(self):
        document_id = ObjectId()
        update_values = {"field": "updated_value"}
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].update_one.side_effect = PyMongoError("Mocked error")
        with self.assertRaises(PyMongoError):
            self.mongo_client.update_document(document_id, update_values)

    def test_delete_document_successful(self):
        document_id = ObjectId()
        mock_delete_result = MagicMock(deleted_count=1)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].delete_one.return_value = mock_delete_result
        result = self.mongo_client.delete_document(document_id)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].delete_one.assert_called_with({"_id": document_id})
        self.assertEqual(result, mock_delete_result)

    def test_delete_document_failure(self):
        document_id = ObjectId()
        mock_delete_result = MagicMock(deleted_count=0)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].delete_one.return_value = mock_delete_result
        result = self.mongo_client.delete_document(document_id)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].delete_one.assert_called_with({"_id": document_id})
        self.assertEqual(result, mock_delete_result)

    def test_delete_document_exception(self):
        document_id = ObjectId()
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].delete_one.side_effect = PyMongoError("Mocked error")
        with self.assertRaises(PyMongoError):
            self.mongo_client.delete_document(document_id)

    def test_get_parsed_data_by_id_found(self):
        document_id = ObjectId()
        mock_document = {"_id": document_id, "parsed_data": {"some_key": "some_value"}}
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.return_value = mock_document
        result = self.mongo_client.get_parsed_data_by_id(document_id)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.assert_called_with({"_id": document_id}, {"parsed_data": 1})
        self.assertEqual(result, mock_document["parsed_data"])

    def test_get_parsed_data_by_id_not_found(self):
        document_id = ObjectId()
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.return_value = None
        result = self.mongo_client.get_parsed_data_by_id(document_id)
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.assert_called_with({"_id": document_id}, {"parsed_data": 1})
        self.assertIsNone(result)

    def test_get_parsed_data_by_id_exception(self):
        document_id = ObjectId()
        self.mocked_mongo_client[self.mongo_client.db_name][self.mongo_client.collection_name].find_one.side_effect = PyMongoError("Mocked error")
        with self.assertRaises(PyMongoError):
            self.mongo_client.get_parsed_data_by_id(document_id)

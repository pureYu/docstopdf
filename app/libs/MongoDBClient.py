import os
import logging
import pymongo
from bson import ObjectId
from pymongo.errors import PyMongoError

class MongoDBClient:
    def __init__(self):
        # MongoDB config:
        self.db_uri = os.getenv("MONGO_DB_URI", "mongodb://mongodb:27017")
        self.db_name = os.getenv("MONGO_DB_NAME", "dbname")
        self.collection_name = os.getenv("MONGO_COLLECTION_NAME", "collection")
        self.logger = logging.getLogger(self.__class__.__name__)

        try:
            self.client = pymongo.MongoClient(self.db_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
        except PyMongoError as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def insert_document(self, file_path, parsed_data, errors, warnings):
        try:
            document = {
                "file_path": file_path,
                "parsed_data": parsed_data if not errors else None,
                "errors": errors,
                "warnings": warnings
            }
            return self.collection.insert_one(document).inserted_id
        except PyMongoError as e:
            self.logger.error(f"Error inserting document: {e}")
            raise

    def find_document(self, document_id):
        try:
            return self.collection.find_one({"_id": ObjectId(document_id)})
        except PyMongoError as e:
            self.logger.error(f"Error finding document: {e}")
            raise

    def update_document(self, document_id, update_values):
        try:
            return self.collection.update_one({"_id": ObjectId(document_id)}, {"$set": update_values})
        except PyMongoError as e:
            self.logger.error(f"Error updating document: {e}")
            raise

    def delete_document(self, document_id):
        try:
            return self.collection.delete_one({"_id": ObjectId(document_id)})
        except PyMongoError as e:
            self.logger.error(f"Error deleting document: {e}")
            raise

    def get_parsed_data_by_id(self, document_id):
        try:
            document = self.collection.find_one({"_id": ObjectId(document_id)}, {"parsed_data": 1})
            return document.get("parsed_data") if document else None
        except PyMongoError as e:
            self.logger.error(f"Error retrieving parsed data: {e}")
            raise

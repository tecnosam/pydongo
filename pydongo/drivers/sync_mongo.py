from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Optional

from pydongo.drivers.base import AbstractMongoDBDriver


class DefaultMongoDBDriver(AbstractMongoDBDriver):
    """
    Default synchronous MongoDB driver using pymongo.
    """

    def __init__(self, connection_string: str, database_name: str):
        super().__init__(connection_string, database_name)
        self.client: Optional[MongoClient] = None

    def connect(self) -> bool:
        """
        Establish a connection to MongoDB using pymongo.
        """
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            return True
        except PyMongoError as e:
            raise RuntimeError(f"Failed to connect to MongoDB: {e}")

    def close(self) -> None:
        """
        Close the MongoDB connection.
        """
        if self.client:
            self.client.close()

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a single document into a collection.
        """
        result = self.db[collection].insert_one(document)
        return {"inserted_id": str(result.inserted_id)}

    def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insert multiple documents into a collection.
        """
        result = self.db[collection].insert_many(documents)
        return {"inserted_ids": [str(_id) for _id in result.inserted_ids]}

    def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the query.
        """
        return self.db[collection].find_one(query)

    def find_many(
        self, collection: str, query: Dict[str, Any], limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents matching the query.
        """
        cursor = self.db[collection].find(query)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def update_one(
        self, collection: str, query: Dict[str, Any], update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a single document matching the query.
        """
        result = self.db[collection].update_one(query, update)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }

    def delete_one(self, collection: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a single document matching the query.
        """
        result = self.db[collection].delete_one(query)
        return {"deleted_count": result.deleted_count}

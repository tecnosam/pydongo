from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Optional, Iterable

from pydongo.drivers.base import AbstractSyncMongoDBDriver


class DefaultMongoDBDriver(AbstractSyncMongoDBDriver):
    """
    Default synchronous MongoDB driver using pymongo.
    """

    def __init__(self, connection_string: str, database_name: str):
        super().__init__(connection_string, database_name)
        self.client: Optional[MongoClient] = None

    def connect(self) -> bool:
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            return True
        except PyMongoError as e:
            raise RuntimeError(f"Failed to connect to MongoDB: {e}")

    def close(self) -> None:
        if self.client:
            self.client.close()

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        result = self.db[collection].insert_one(document)
        return {"inserted_id": str(result.inserted_id)}

    def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        result = self.db[collection].insert_many(documents)
        return {"inserted_ids": [str(_id) for _id in result.inserted_ids]}

    def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return self.db[collection].find_one(query)

    def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, Any],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        cursor = self.db[collection].find(query)

        if sort_criteria:
            cursor = cursor.sort([(k, v) for k, v in sort_criteria.items()])

        if offset:
            cursor = cursor.skip(offset)

        if limit:
            cursor = cursor.limit(limit)

        return cursor

    def update_one(
        self, collection: str, query: Dict[str, Any], update: Dict[str, Any]
    ) -> Dict[str, Any]:
        result = self.db[collection].update_one(query, update)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }

    def delete_one(self, collection: str, query: Dict[str, Any]) -> Dict[str, Any]:
        result = self.db[collection].delete_one(query)
        return {"deleted_count": result.deleted_count}

    def count(self, collection: str, query: Dict[str, Any]) -> int:
        return self.db[collection].count_documents(query)

    def exists(self, collection: str, query: Dict[str, Any]) -> bool:
        return self.db[collection].count_documents(query, limit=1) > 0

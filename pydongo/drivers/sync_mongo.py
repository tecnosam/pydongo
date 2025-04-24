from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Optional, Iterable, Tuple

from pydongo.drivers.base import AbstractSyncMongoDBDriver
from pydongo.expressions.index import IndexExpression


class DefaultMongoDBDriver(AbstractSyncMongoDBDriver):
    """
    Default synchronous MongoDB driver implementation using PyMongo.

    This driver connects to a real MongoDB instance and executes
    blocking operations such as insert, update, query, and delete.
    """

    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize the driver with a MongoDB connection URI and database name.

        Args:
            connection_string (str): MongoDB URI (e.g., "mongodb://localhost:27017").
            database_name (str): The target database to operate on.
        """
        super().__init__(connection_string, database_name)
        self.client: Optional[MongoClient] = None

    def connect(self) -> bool:
        """
        Establish a connection to the MongoDB server.

        Returns:
            bool: True if the connection is successful.

        Raises:
            RuntimeError: If connection to MongoDB fails.
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

        Args:
            collection (str): Name of the collection.
            document (dict): Document to insert.

        Returns:
            dict: Result of the insert operation, including the inserted ID.
        """
        result = self.db[collection].insert_one(document)
        return {"inserted_id": str(result.inserted_id)}

    def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insert multiple documents into a collection.

        Args:
            collection (str): Name of the collection.
            documents (list): List of documents to insert.

        Returns:
            dict: Result including inserted IDs.
        """
        result = self.db[collection].insert_many(documents)
        return {"inserted_ids": [str(_id) for _id in result.inserted_ids]}

    def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document that matches the query.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB filter query.

        Returns:
            dict or None: The found document, or None if not found.
        """
        return self.db[collection].find_one(query)

    def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, Any],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        Find multiple documents that match the query.

        Args:
            collection (str): Name of the collection.
            query (dict): Filter conditions.
            sort_criteria (dict): Sorting fields and directions.
            offset (int, optional): Number of records to skip.
            limit (int, optional): Maximum number of documents to return.

        Returns:
            Iterable[dict]: Cursor for matching documents.
        """
        cursor = self.db[collection].find(query)

        if sort_criteria:
            cursor = cursor.sort([(k, v) for k, v in sort_criteria.items()])

        if offset:
            cursor = cursor.skip(offset)

        if limit:
            cursor = cursor.limit(limit)

        return cursor

    def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Dict[str, Any]:
        """
        Update a single document matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): Filter conditions.
            update (dict): Update operations (e.g., {"$set": {...}}).
            upsert (bool): Whether to insert the document if it doesn't exist.

        Returns:
            dict: Update result with match, modification, and upsert info.
        """
        result = self.db[collection].update_one(query, update, upsert=upsert)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }

    def delete_one(self, collection: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a single document matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): Filter conditions.

        Returns:
            dict: Delete result with count of deleted documents.
        """
        result = self.db[collection].delete_one(query)
        return {"deleted_count": result.deleted_count}

    def count(self, collection: str, query: Dict[str, Any]) -> int:
        """
        Count the number of documents matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): Filter conditions.

        Returns:
            int: Number of documents matching the filter.
        """
        return self.db[collection].count_documents(query)

    def exists(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Check if at least one document exists that matches the query.

        Args:
            collection (str): Name of the collection.
            query (dict): Filter conditions.

        Returns:
            bool: True if a matching document exists.
        """
        return self.db[collection].count_documents(query, limit=1) > 0

    def create_index(self, collection: str, index: Tuple[IndexExpression]):
        """
        Create an index on a collection in the MongoDB Database

        Args:
            collection (str): The collection name.
            index (tuple[IndexExpression]):
                A tuple of IndexExpression objects representing the index to create
                NOTE: Multiple elements in tuple indicate a single compound index
                not multiple indexes

        """

        index_key: List[tuple] = []
        final_kwargs = {}

        for expr in index:
            index_key.extend(expr.serialize().items())
            final_kwargs.update(expr.build_kwargs())

        self.db[collection].create_index(index_key, **final_kwargs)

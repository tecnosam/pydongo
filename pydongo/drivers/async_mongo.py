from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Optional, Iterable, Tuple

from pydongo.drivers.base import AbstractAsyncMongoDBDriver
from pydongo.expressions.index import IndexExpression


class AsyncDefaultMongoDBDriver(AbstractAsyncMongoDBDriver):
    """
    Default asynchronous MongoDB driver using Motor (async wrapper for PyMongo).

    This driver connects to a real MongoDB instance and provides async methods
    for insert, update, query, and delete operations.
    """

    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize the driver with a MongoDB URI and target database name.

        Args:
            connection_string (str): MongoDB connection URI.
            database_name (str): Name of the database to use.
        """
        super().__init__(connection_string, database_name)
        self.client: Optional[AsyncIOMotorClient] = None

    async def connect(self) -> bool:
        """
        Asynchronously establish a connection to the MongoDB server.

        Returns:
            bool: True if the connection is successful.

        Raises:
            RuntimeError: If unable to connect to MongoDB.
        """
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            return True
        except PyMongoError as e:
            raise RuntimeError(f"Failed to connect to MongoDB: {e}")

    async def close(self) -> None:
        """
        Asynchronously close the MongoDB connection.
        """
        if self.client:
            self.client.close()

    async def insert_one(
        self, collection: str, document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert a single document into the specified collection.

        Args:
            collection (str): Name of the collection.
            document (dict): Document to insert.

        Returns:
            dict: Result including the inserted document ID.
        """
        result = await self.db[collection].insert_one(document)
        return {"inserted_id": str(result.inserted_id)}

    async def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insert multiple documents into the specified collection.

        Args:
            collection (str): Name of the collection.
            documents (list): Documents to insert.

        Returns:
            dict: Result including inserted document IDs.
        """
        result = await self.db[collection].insert_many(documents)
        return {"inserted_ids": [str(_id) for _id in result.inserted_ids]}

    async def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document that matches the query.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB query object.

        Returns:
            dict or None: The matching document or None.
        """
        return await self.db[collection].find_one(query)

    async def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, int],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        Find multiple documents matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB filter query.
            sort_criteria (dict): Sort order (e.g., {"created_at": -1}).
            offset (int, optional): Number of documents to skip.
            limit (int, optional): Max number of documents to return.

        Returns:
            Iterable[dict]: A cursor of matching documents.
        """
        cursor = self.db[collection].find(query)

        if sort_criteria:
            cursor = cursor.sort(sort_criteria)

        if offset is not None:
            cursor = cursor.skip(offset)

        if limit is not None:
            cursor = cursor.limit(limit)

        return cursor  # type: ignore

    async def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Dict[str, Any]:
        """
        Update a single document that matches the filter.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB filter.
            update (dict): MongoDB update expression.
            upsert (bool): If True, create the document if it does not exist.

        Returns:
            dict: Result of the update operation.
        """
        result = await self.db[collection].update_one(query, update, upsert=upsert)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }

    async def delete_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Delete a single document matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB filter.

        Returns:
            dict: Result including count of deleted documents.
        """
        result = await self.db[collection].delete_one(query)
        return {"deleted_count": result.deleted_count}

    async def count(self, collection: str, query: Dict[str, Any]) -> int:
        """
        Count documents matching the given filter.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB filter.

        Returns:
            int: Number of matching documents.
        """
        return await self.db[collection].count_documents(query)

    async def exists(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Check if at least one document exists that matches the filter.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB filter.

        Returns:
            bool: True if a matching document exists.
        """
        return await self.db[collection].count_documents(query, limit=1) > 0

    async def create_index(self, collection: str, index: Tuple[IndexExpression]):
        """
        Create an index on a collection in the MongoDB Database (Async version using Motor).

        Args:
            collection (str): The collection name.
            index (tuple[IndexExpression]):
                A tuple of IndexExpression objects representing the index to create.
                NOTE: Multiple elements in the tuple indicate a single compound index,
                not multiple separate indexes.
        """

        index_key: List[tuple] = []
        final_kwargs = {}

        for expr in index:
            index_key.extend(expr.serialize().items())
            final_kwargs.update(expr.build_kwargs())

        await self.db[collection].create_index(index_key, **final_kwargs)

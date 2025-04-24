import uuid

from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple
from copy import deepcopy

from pydongo.drivers.base import AbstractSyncMongoDBDriver, AbstractAsyncMongoDBDriver
from pydongo.expressions.index import IndexExpression


class MockMongoDBDriver(AbstractSyncMongoDBDriver):
    """
    In-memory mock implementation of the AbstractSyncMongoDBDriver.

    This mock driver mimics MongoDB behavior for unit testing without requiring
    a real database connection. Data is stored in-memory in Python dictionaries.
    """

    def __init__(self, connection_string: str = "", database_name: str = "mockdb"):
        """
        Initialize the mock driver with an empty in-memory store.

        Args:
            connection_string (str): Ignored.
            database_name (str): Name of the fake database.
        """
        super().__init__(connection_string, database_name)
        self._collections: Dict[str, List[Dict[str, Any]]] = {}
        self.indexes: defaultdict = defaultdict(lambda: [])

    def connect(self) -> bool:
        """
        Simulate a successful connection.

        Returns:
            bool: Always True.
        """
        return True

    def close(self) -> None:
        """
        Close the connection (noop for the mock driver).
        """
        pass

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a document into the in-memory collection.

        Args:
            collection (str): Name of the collection.
            document (dict): Document to insert.

        Returns:
            dict: Insert result including generated `_id`.
        """
        document = deepcopy(document)
        document["_id"] = str(uuid.uuid4())
        self._collections.setdefault(collection, []).append(document)
        return {"inserted_id": document["_id"]}

    def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insert multiple documents into the in-memory collection.

        Args:
            collection (str): Name of the collection.
            documents (list): List of documents to insert.

        Returns:
            dict: Insert result with list of `_id`s.
        """
        inserted_ids = []
        for doc in documents:
            inserted = self.insert_one(collection, doc)
            inserted_ids.append(inserted["inserted_id"])
        return {"inserted_ids": inserted_ids}

    def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB-style filter.

        Returns:
            dict or None: Matching document or None if not found.
        """
        for doc in self._collections.get(collection, []):
            if all(doc.get(k) == v for k, v in query.items()):
                return deepcopy(doc)
        return None

    def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, Any],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB-style filter.
            sort_criteria (dict): Ignored in the mock.
            offset (int, optional): Skip the first N results.
            limit (int, optional): Limit the number of results returned.

        Returns:
            list: List of matching documents.
        """
        result = [
            deepcopy(doc)
            for doc in self._collections.get(collection, [])
            if all(doc.get(k) == v for k, v in query.items())
        ]
        return result[offset:limit] if limit else result

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
            query (dict): Filter query.
            update (dict): Update operations (only supports "$set").

        Returns:
            dict: Update result with matched and modified count.
        """
        for doc in self._collections.get(collection, []):
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update.get("$set", {}))
                return {"matched_count": 1, "modified_count": 1, "upserted_id": None}
        return {"matched_count": 0, "modified_count": 0, "upserted_id": None}

    def delete_one(self, collection: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete the first document matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): Filter query.

        Returns:
            dict: Delete result.
        """
        docs = self._collections.get(collection, [])
        for i, doc in enumerate(docs):
            if all(doc.get(k) == v for k, v in query.items()):
                del docs[i]
                return {"deleted_count": 1}
        return {"deleted_count": 0}

    def count(self, collection: str, query: Dict[str, Any]) -> int:
        """
        Count documents that match the query.

        Args:
            collection (str): Name of the collection.
            query (dict): Filter query.

        Returns:
            int: Number of matching documents.
        """
        return sum(
            1
            for doc in self._collections.get(collection, [])
            if all(doc.get(k) == v for k, v in query.items())
        )

    def exists(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Check if at least one document matches the query.

        Args:
            collection (str): Name of the collection.
            query (dict): Filter query.

        Returns:
            bool: True if at least one document matches.
        """
        return any(
            all(doc.get(k) == v for k, v in query.items())
            for doc in self._collections.get(collection, [])
        )

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

        self.indexes[collection].append(index)


class MockAsyncMongoDBDriver(AbstractAsyncMongoDBDriver):
    """
    In-memory mock implementation of the AbstractAsyncMongoDBDriver.

    This async mock mirrors the behavior of MongoDB using native async/await
    and an in-memory store. Ideal for use in async unit tests.
    """

    def __init__(self, connection_string: str = "", database_name: str = "mockdb"):
        """
        Initialize the async mock with an in-memory store.

        Args:
            connection_string (str): Ignored.
            database_name (str): Mock database name.
        """
        super().__init__(connection_string, database_name)
        self._collections: Dict[str, List[Dict[str, Any]]] = {}
        self.indexes: defaultdict = defaultdict(lambda: [])

    async def connect(self) -> bool:
        """
        Simulate async connection success.

        Returns:
            bool: Always True.
        """
        return True

    async def close(self) -> None:
        """
        Simulate async close (noop).
        """
        pass

    async def insert_one(
        self, collection: str, document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Asynchronously insert a document into the mock store.

        Args:
            collection (str): Collection name.
            document (dict): Document to insert.

        Returns:
            dict: Insert result with `_id`.
        """
        document = deepcopy(document)
        document["_id"] = str(uuid.uuid4())
        self._collections.setdefault(collection, []).append(document)
        return {"inserted_id": document["_id"]}

    async def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Asynchronously insert multiple documents.

        Args:
            collection (str): Collection name.
            documents (list): List of documents.

        Returns:
            dict: Insert result with `_id`s.
        """
        inserted_ids = []
        for doc in documents:
            inserted = await self.insert_one(collection, doc)
            inserted_ids.append(inserted["inserted_id"])
        return {"inserted_ids": inserted_ids}

    async def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Asynchronously find a single matching document.

        Args:
            collection (str): Collection name.
            query (dict): Filter.

        Returns:
            dict or None: Matching document or None.
        """
        for doc in self._collections.get(collection, []):
            if all(doc.get(k) == v for k, v in query.items()):
                return deepcopy(doc)
        return None

    async def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, Any],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Asynchronously return a list of matching documents.

        Args:
            collection (str): Collection name.
            query (dict): Filter.
            sort_criteria (dict): Ignored.
            offset (int, optional): Skip N docs.
            limit (int, optional): Limit docs returned.

        Returns:
            list: Matching documents.
        """
        result = [
            deepcopy(doc)
            for doc in self._collections.get(collection, [])
            if all(doc.get(k) == v for k, v in query.items())
        ]
        return result[offset:limit] if limit else result

    async def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Dict[str, Any]:
        """
        Asynchronously update a single matching document.

        Args:
            collection (str): Collection name.
            query (dict): Filter.
            update (dict): Update expression.

        Returns:
            dict: Update result.
        """
        for doc in self._collections.get(collection, []):
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update.get("$set", {}))
                return {"matched_count": 1, "modified_count": 1, "upserted_id": None}
        return {"matched_count": 0, "modified_count": 0, "upserted_id": None}

    async def delete_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Asynchronously delete a single matching document.

        Args:
            collection (str): Collection name.
            query (dict): Filter.

        Returns:
            dict: Delete result.
        """
        docs = self._collections.get(collection, [])
        for i, doc in enumerate(docs):
            if all(doc.get(k) == v for k, v in query.items()):
                del docs[i]
                return {"deleted_count": 1}
        return {"deleted_count": 0}

    async def count(self, collection: str, query: Dict[str, Any]) -> int:
        """
        Asynchronously count matching documents.

        Args:
            collection (str): Collection name.
            query (dict): Filter.

        Returns:
            int: Number of matches.
        """
        return sum(
            1
            for doc in self._collections.get(collection, [])
            if all(doc.get(k) == v for k, v in query.items())
        )

    async def exists(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Asynchronously check if any document matches the filter.

        Args:
            collection (str): Collection name.
            query (dict): Filter.

        Returns:
            bool: True if at least one match exists.
        """
        return any(
            all(doc.get(k) == v for k, v in query.items())
            for doc in self._collections.get(collection, [])
        )

    async def create_index(self, collection: str, index: Tuple[IndexExpression]):
        """
        Create an index on a collection in the MongoDB Database

        Args:
            collection (str): The collection name.
            index (tuple[IndexExpression]):
                A tuple of IndexExpression objects representing the index to create
                NOTE: Muiltiple elements in tuple indicate a single compound index
                not multiple indexes

        """

        self.indexes[collection].append(index)

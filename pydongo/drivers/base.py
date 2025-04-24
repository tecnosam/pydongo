import contextvars
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterable, Tuple

from pydongo.expressions.index import IndexExpression


class AbstractMongoDBDriver(ABC):
    """
    Abstract base class for MongoDB drivers.
    """


class AbstractSyncMongoDBDriver(AbstractMongoDBDriver):
    """
    Abstract base class for synchronous MongoDB drivers.
    Provides context management support and coroutine/thread-safe access
    to the currently active driver instance via contextvars.
    """

    _current: contextvars.ContextVar["AbstractSyncMongoDBDriver"] = (
        contextvars.ContextVar("mongo_driver_current")
    )

    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize the MongoDB driver with a connection string and database name.

        Args:
            connection_string (str): MongoDB connection URI.
            database_name (str): Target database name.
        """
        self.connection_string = connection_string
        self.database_name = database_name

    def __enter__(self):
        """
        Enter the context manager, connect to MongoDB, and set the current driver context.
        """
        self.connect()
        self._token = self._current.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager, close the connection, and reset the driver context.
        """
        self.close()
        self._current.reset(self._token)

    @classmethod
    def current(cls) -> "AbstractSyncMongoDBDriver":
        """
        Get the current MongoDB driver instance for this coroutine/thread.

        Returns:
            AbstractMongoDBDriver: The active driver instance.

        Raises:
            RuntimeError: If no driver is currently in context.
        """
        try:
            return cls._current.get()
        except LookupError:
            raise RuntimeError("No active MongoDBDriver context found")

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish a connection to the MongoDB server.
        Returns:
            bool: True if connection was successful.
        """

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection to the MongoDB server.
        """

    @abstractmethod
    def insert_one(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a single document into the specified collection.

        Args:
            collection (str): The collection name.
            document (dict): The document to insert.

        Returns:
            dict: Result of the insert operation.
        """

    @abstractmethod
    def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insert multiple documents into the specified collection.

        Args:
            collection (str): The collection name.
            documents (list): List of documents to insert.

        Returns:
            dict: Result of the insert operation.
        """

    @abstractmethod
    def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            dict or None: The found document or None if not found.
        """

    @abstractmethod
    def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, Any],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        Find multiple documents matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.
            sort_criteria (dict): How to order the results
            offset (int, optional): Number of records to skip (useful for pagination)
            limit (int, optional): Max number of documents to return.

        Returns:
            iterator for result: Iterable sequence of matching documents.
        """

    @abstractmethod
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
            collection (str): The collection name.
            query (dict): The filter query.
            update (dict): The update document.

        Returns:
            dict: Result of the update operation.
        """

    @abstractmethod
    def delete_one(self, collection: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a single document matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            dict: Result of the delete operation.
        """

    @abstractmethod
    def count(self, collection: str, query: dict[str, Any]) -> int:
        """
        Count how many records are in a collection that match the specified query

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            int: Number of documents that match the specified query
        """

    @abstractmethod
    def exists(self, collection: str, query: dict[str, Any]) -> bool:
        """
        Check if at least one document exists in the collection that matches the
        specified query

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            bool: True if a document exists and False if it doesn't
        """

    @abstractmethod
    def create_index(self, collection: str, index: Tuple[IndexExpression]):
        """
        Create an index on a collection in the MongoDB Database

        Args:
            collection (str): The collection name.
            index (tuple[IndexExpression]):
                A tuple of IndexExpression objects representing the index to create
                NOTE: Multiple elements in tuple indicate a single compound index
        """


class AbstractAsyncMongoDBDriver(AbstractMongoDBDriver):
    """
    Abstract base class for asynchronous MongoDB drivers.
    Provides async context management and coroutine-safe access
    to the currently active driver instance via contextvars.
    """

    _current: contextvars.ContextVar["AbstractAsyncMongoDBDriver"] = (
        contextvars.ContextVar("mongo_driver_current")
    )

    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize the MongoDB driver with a connection string and database name.

        Args:
            connection_string (str): MongoDB connection URI.
            database_name (str): Target database name.
        """
        self.connection_string = connection_string
        self.database_name = database_name

    async def __aenter__(self):
        """
        Enter the async context manager, connect to MongoDB, and set the current driver context.
        """
        await self.connect()
        self._token = self._current.set(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the async context manager, close the connection, and reset the driver context.
        """
        await self.close()
        self._current.reset(self._token)

    @classmethod
    def current(cls) -> "AbstractAsyncMongoDBDriver":
        """
        Get the current MongoDB driver instance for this coroutine.

        Returns:
            AbstractAsyncMongoDBDriver: The active driver instance.

        Raises:
            RuntimeError: If no driver is currently in context.
        """
        try:
            return cls._current.get()
        except LookupError:
            raise RuntimeError("No active MongoDBDriver context found")

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish a connection to the MongoDB server.
        Returns:
            bool: True if connection was successful.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Close the connection to the MongoDB server.
        """

    @abstractmethod
    async def insert_one(
        self, collection: str, document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert a single document into the specified collection.

        Args:
            collection (str): The collection name.
            document (dict): The document to insert.

        Returns:
            dict: Result of the insert operation.
        """

    @abstractmethod
    async def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insert multiple documents into the specified collection.

        Args:
            collection (str): The collection name.
            documents (list): List of documents to insert.

        Returns:
            dict: Result of the insert operation.
        """

    @abstractmethod
    async def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            dict or None: The found document or None if not found.
        """

    @abstractmethod
    async def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, Any],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        """
        Find multiple documents matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.
            sort_criteria (dict): How to order the results
            offset (int, optional): Number of records to skip (useful for pagination)
            limit (int, optional): Max number of documents to return.

        Returns:
            iterable sequence: Iterable sequence of matching documents.
        """

    @abstractmethod
    async def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Dict[str, Any]:
        """
        Update a single document matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.
            update (dict): The update document.

        Returns:
            dict: Result of the update operation.
        """

    @abstractmethod
    async def delete_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Delete a single document matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            dict: Result of the delete operation.
        """

    @abstractmethod
    async def count(self, collection: str, query: dict[str, Any]) -> int:
        """
        Count how many records are in a collection that match the specified query

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            int: Number of documents that match the specified query
        """

    @abstractmethod
    async def exists(self, collection: str, query: dict[str, Any]) -> bool:
        """
        Check if at least one document exists in the collection that matches the
        specified query

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            bool: True if a document exists and False if it doesn't
        """

    @abstractmethod
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

import contextvars
from abc import ABC, abstractmethod
from collections.abc import Iterable
from types import TracebackType
from typing import Any, Self

from pydongo.expressions.index import IndexExpression


class AbstractMongoDBDriver(ABC):  # noqa: B024
    """Abstract base class for MongoDB drivers."""


class AbstractSyncMongoDBDriver(AbstractMongoDBDriver):
    """Abstract base class for synchronous MongoDB drivers.

    Provides context management support and coroutine/thread-safe access
    to the currently active driver instance via contextvars.
    """

    _current: contextvars.ContextVar["AbstractSyncMongoDBDriver"] = contextvars.ContextVar("mongo_driver_current")

    def __enter__(self) -> Self:
        """Enter the context manager, connect to MongoDB, and set the current driver context."""
        self.connect()
        self._token = self._current.set(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager, close the connection, and reset the driver context."""
        self.close()
        self._current.reset(self._token)

    @classmethod
    def current(cls) -> "AbstractSyncMongoDBDriver":
        """Get the current MongoDB driver instance for this coroutine/thread.

        Returns:
            AbstractMongoDBDriver: The active driver instance.

        Raises:
            RuntimeError: If no driver is currently in context.
        """
        try:
            return cls._current.get()
        except LookupError as e:
            raise RuntimeError("No active MongoDBDriver context found") from e

    @abstractmethod
    def connect(self) -> bool:
        """Establish a connection to the MongoDB server.

        Returns:
            bool: True if connection was successful.
        """

    @abstractmethod
    def close(self) -> None:
        """Close the connection to the MongoDB server."""

    @abstractmethod
    def insert_one(self, collection: str, document: dict[str, Any]) -> dict[str, Any]:
        """Insert a single document into the specified collection.

        Args:
            collection (str): The collection name.
            document (dict): The document to insert.

        Returns:
            dict: Result of the insert operation.
        """

    @abstractmethod
    def insert_many(self, collection: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
        """Insert multiple documents into the specified collection.

        Args:
            collection (str): The collection name.
            documents (list): List of documents to insert.

        Returns:
            dict: Result of the insert operation.
        """

    @abstractmethod
    def find_one(self, collection: str, query: dict[str, Any]) -> dict[str, Any] | None:
        """Find a single document matching the query.

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
        query: dict[str, Any],
        sort_criteria: dict[str, Any],
        offset: int | None = None,
        limit: int | None = None,
    ) -> Iterable[dict[str, Any]]:
        """Find multiple documents matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.
            sort_criteria (dict): How to order the results
            offset (Union[int, None]): Number of records to skip (useful for pagination)
            limit (Union[int, None]): Max number of documents to return.

        Returns:
            iterator for result: Iterable sequence of matching documents.
        """

    @abstractmethod
    def update_one(
        self,
        collection: str,
        query: dict[str, Any],
        update: dict[str, Any],
        upsert: bool = False,
    ) -> dict[str, Any]:
        """Update a single document matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.
            update (dict): The update document.
            upsert (bool): Whether to insert a new document if no match is found.

        Returns:
            dict: Result of the update operation.
        """

    @abstractmethod
    def delete_one(self, collection: str, query: dict[str, Any]) -> dict[str, Any]:
        """Delete a single document matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            dict: Result of the delete operation.
        """

    @abstractmethod
    def count(self, collection: str, query: dict[str, Any]) -> int:
        """Count how many records are in a collection that match the specified query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            int: Number of documents that match the specified query
        """

    @abstractmethod
    def exists(self, collection: str, query: dict[str, Any]) -> bool:
        """Check if at least one document exists in the collection that matches the specified query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            bool: True if a document exists and False if it doesn't
        """

    @abstractmethod
    def create_index(self, collection: str, index: tuple[IndexExpression]) -> None:
        """Create an index on a collection in the MongoDB Database.

        Args:
            collection (str): The collection name.
            index (tuple[IndexExpression]):
                A tuple of IndexExpression objects representing the index to create
                NOTE: Multiple elements in tuple indicate a single compound index
        """

    @abstractmethod
    def update_many(
        self,
        collection: str,
        query: dict[str, Any],
        update: dict[str, Any],
    ) -> dict[str, Any]:
        """Update multiple documents matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB filter.
            update (dict): MongoDB update expression.

        Returns:
            dict: Result of the update operation.
        """


class AbstractAsyncMongoDBDriver(AbstractMongoDBDriver):
    """Abstract base class for asynchronous MongoDB drivers.

    Provides async context management and coroutine-safe access
    to the currently active driver instance via contextvars.
    """

    _current: contextvars.ContextVar["AbstractAsyncMongoDBDriver"] = contextvars.ContextVar("mongo_driver_current")

    async def __aenter__(self) -> Self:
        """Enter the async context manager, connect to MongoDB, and set the current driver context."""
        await self.connect()
        self._token = self._current.set(self)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager, close the connection, and reset the driver context."""
        await self.close()
        self._current.reset(self._token)

    @classmethod
    def current(cls) -> "AbstractAsyncMongoDBDriver":
        """Get the current MongoDB driver instance for this coroutine.

        Returns:
            AbstractAsyncMongoDBDriver: The active driver instance.

        Raises:
            RuntimeError: If no driver is currently in context.
        """
        try:
            return cls._current.get()
        except LookupError as e:
            raise RuntimeError("No active MongoDBDriver context found") from e

    @abstractmethod
    async def connect(self) -> bool:
        """Establish a connection to the MongoDB server.

        Returns:
            bool: True if connection was successful.
        """

    @abstractmethod
    async def close(self) -> None:
        """Close the connection to the MongoDB server."""

    @abstractmethod
    async def insert_one(self, collection: str, document: dict[str, Any]) -> dict[str, Any]:
        """Insert a single document into the specified collection.

        Args:
            collection (str): The collection name.
            document (dict): The document to insert.

        Returns:
            dict: Result of the insert operation.
        """

    @abstractmethod
    async def insert_many(self, collection: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
        """Insert multiple documents into the specified collection.

        Args:
            collection (str): The collection name.
            documents (list): List of documents to insert.

        Returns:
            dict: Result of the insert operation.
        """

    @abstractmethod
    async def find_one(self, collection: str, query: dict[str, Any]) -> dict[str, Any] | None:
        """Find a single document matching the query.

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
        query: dict[str, Any],
        sort_criteria: dict[str, Any],
        offset: int | None = None,
        limit: int | None = None,
    ) -> Iterable[dict[str, Any]]:
        """Find multiple documents matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.
            sort_criteria (dict): How to order the results
            offset (Union[int, None]): Number of records to skip (useful for pagination)
            limit (Union[int, None]): Max number of documents to return.

        Returns:
            iterable sequence: Iterable sequence of matching documents.
        """

    @abstractmethod
    async def update_one(
        self,
        collection: str,
        query: dict[str, Any],
        update: dict[str, Any],
        upsert: bool = False,
    ) -> dict[str, Any]:
        """Update a single document matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.
            update (dict): The update document.
            upsert (bool): Whether to insert a new document if no match is found.

        Returns:
            dict: Result of the update operation.
        """

    @abstractmethod
    async def delete_one(self, collection: str, query: dict[str, Any]) -> dict[str, Any]:
        """Delete a single document matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            dict: Result of the delete operation.
        """

    @abstractmethod
    async def count(self, collection: str, query: dict[str, Any]) -> int:
        """Count how many records are in a collection that match the specified query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            int: Number of documents that match the specified query
        """

    @abstractmethod
    async def exists(self, collection: str, query: dict[str, Any]) -> bool:
        """Check if at least one document exists in the collection that matches the specified query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.

        Returns:
            bool: True if a document exists and False if it doesn't
        """

    @abstractmethod
    async def create_index(self, collection: str, index: tuple[IndexExpression]) -> None:
        """Create an index on a collection in the MongoDB Database.

        Args:
            collection (str): The collection name.
            index (tuple[IndexExpression]):
                A tuple of IndexExpression objects representing the index to create
                NOTE: Muiltiple elements in tuple indicate a single compound index
                not multiple indexes
        """

    @abstractmethod
    async def update_many(
        self,
        collection: str,
        query: dict[str, Any],
        update: dict[str, Any],
    ) -> dict[str, Any]:
        """Update multiple documents matching the query.

        Args:
            collection (str): Name of the collection.
            query (dict): MongoDB filter.
            update (dict): MongoDB update expression.

        Returns:
            dict: Result of the update operation.
        """

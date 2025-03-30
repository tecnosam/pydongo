import contextvars
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class AbstractMongoDBDriver(ABC):
    """
    Abstract base class for synchronous MongoDB drivers.
    Provides context management support and coroutine/thread-safe access
    to the currently active driver instance via contextvars.
    """

    _current: contextvars.ContextVar["AbstractMongoDBDriver"] = contextvars.ContextVar(
        "mongo_driver_current"
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
    def current(cls) -> "AbstractMongoDBDriver":
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
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection to the MongoDB server.
        """
        pass

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
        pass

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
        pass

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
        pass

    @abstractmethod
    def find_many(
        self, collection: str, query: Dict[str, Any], limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.
            limit (int, optional): Max number of documents to return.

        Returns:
            list: List of matching documents.
        """
        pass

    @abstractmethod
    def update_one(
        self, collection: str, query: Dict[str, Any], update: Dict[str, Any]
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
        pass

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
        pass


class AbstractAsyncMongoDBDriver(ABC):
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
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close the connection to the MongoDB server.
        """
        pass

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
        pass

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
        pass

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
        pass

    @abstractmethod
    async def find_many(
        self, collection: str, query: Dict[str, Any], limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents matching the query.

        Args:
            collection (str): The collection name.
            query (dict): The filter query.
            limit (int, optional): Max number of documents to return.

        Returns:
            list: List of matching documents.
        """
        pass

    @abstractmethod
    async def update_one(
        self, collection: str, query: Dict[str, Any], update: Dict[str, Any]
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
        pass

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
        pass

from typing import Any, Generic, TypeVar, Union

from bson import ObjectId
from pydantic import BaseModel

from pydongo.drivers.base import AbstractAsyncMongoDBDriver, AbstractSyncMongoDBDriver
from pydongo.utils.serializer import replace_unserializable_fields

T = TypeVar("T", bound=BaseModel)


def as_document(
    pydantic_object: T,
    driver: AbstractSyncMongoDBDriver | AbstractAsyncMongoDBDriver,
    collection_name: str | None = None,
) -> Union["DocumentWorker", "AsyncDocumentWorker"]:
    """Wraps a Pydantic object in either a synchronous or asynchronous document worker, depending on the provided MongoDB driver.

    Args:
        pydantic_object (T): A Pydantic model instance.
        driver (Union[AbstractMongoDBDriver, AbstractAsyncMongoDBDriver]): The MongoDB driver in use.
        collection_name (Union[str, None]): Optionally set the name of the collection to persist the document to.


    Returns:
        Union[DocumentWorker, AsyncDocumentWorker]: A document wrapper with persistence methods.
    """  # noqa: E501
    if issubclass(driver.__class__, AbstractAsyncMongoDBDriver):
        return AsyncDocumentWorker(
            pydantic_object=pydantic_object,
            driver=driver,
            collection_name=collection_name,
        )
    return DocumentWorker(
        pydantic_object=pydantic_object,
        driver=driver,
        collection_name=collection_name,
    )


class BaseDocumentWorker(Generic[T]):
    """Base class for document-level operations like serialization, query generation, and collection detection.

    This class provides common functionality for both synchronous and asynchronous document workers.
    """

    def __init__(  # noqa: D417
        self,
        pydantic_object: T,
        objectId: str | None = None,  # noqa: N803
        collection_name: str | None = None,
        *args: Any,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Initialize the document wrapper.

        Args:
            pydantic_object (T): The Pydantic model to wrap.
            objectId (Union[str, None]): MongoDB ObjectId of the document.
            collection_name (Union[str, None]): Optionally set the name of the collection to persist the document to
        """
        self.pydantic_object = pydantic_object
        self.objectId = ObjectId(objectId) if objectId else None

        self.__collection_name = collection_name

    @property
    def collection_name(self) -> str:
        """Returns the MongoDB collection name associated with the model.

        Returns:
            str: The collection name.
        """
        if self.__collection_name is None:
            self.__collection_name = str(
                self.pydantic_object.model_config.get(
                    "collection_name",
                    self.pydantic_object.__class__.__name__.lower().rstrip("s") + "s",
                )
            )

        return self.__collection_name

    def get_query(self) -> dict[str, Any]:
        """Builds a MongoDB query to uniquely identify the current document.

        Returns:
            dict: A MongoDB query dict.
        """
        if self.objectId:
            return {"_id": ObjectId(self.objectId)}
        return self.serialize()

    def serialize(self) -> dict[str, Any]:
        """Serializes the Pydantic model to a dictionary suitable for MongoDB storage.

        Returns:
            dict: Serialized representation of the document.
        """
        dump = self.pydantic_object.model_dump()
        return replace_unserializable_fields(dump)

    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the underlying Pydantic model.

        Args:
            name (str): The attribute name.

        Returns:
            Any: Attribute value from the Pydantic model.
        """
        return getattr(self.pydantic_object, name)

    def __repr__(self) -> str:
        """Returns a human-readable string representation of the document.

        Returns:
            str: Representation of the document wrapper.
        """
        return f"{self.__class__.__name__}(<{self.pydantic_object}>)"

    def __setattr__(self, name: str, value: Any) -> None:
        """Pipe updates to the pydantic object where applicable."""
        if name == "pydantic_object":
            return super().__setattr__(name, value)

        if hasattr(self.pydantic_object, name):
            setattr(self.pydantic_object, name, value)

        return super().__setattr__(name, value)


class DocumentWorker(BaseDocumentWorker):  # type: ignore[type-arg]
    """Document wrapper for synchronous MongoDB operations.

    Provides methods to save and delete documents from MongoDB.
    """

    def __init__(
        self,
        pydantic_object: T,
        driver: AbstractSyncMongoDBDriver,
        objectId: str | None = None,  # noqa: N803
        collection_name: str | None = None,
    ) -> None:
        """Initialize the sync document worker.

        Args:
            pydantic_object (T): The Pydantic model to wrap.
            driver (AbstractSyncMongoDBDriver): The sync MongoDB driver.
            objectId (Union[str, None]): ObjectId for the document.
            collection_name (Union[str, None]): Optionally set the name of the collection to persist the document to.
        """
        super().__init__(
            pydantic_object=pydantic_object,
            objectId=objectId,
            collection_name=collection_name,
        )
        self.driver = driver

    def save(self) -> dict[str, Any]:
        """Save the document to MongoDB. Performs an insert if no ObjectId is present, or an update otherwise.

        Returns:
            dict: Result of the MongoDB insert or update operation.
        """
        payload = self.serialize()
        if self.objectId is None:
            response = self.driver.insert_one(self.collection_name, payload)
            self.objectId = response.get("inserted_id")
        else:
            query = {"_id": ObjectId(self.objectId)}
            response = self.driver.update_one(self.collection_name, query=query, update={"$set": payload})

        return response

    def delete(self) -> dict[str, Any]:
        """Delete the document from MongoDB using its ObjectId.

        Returns:
            dict: Result of the delete operation.
        """
        query = self.get_query()
        return self.driver.delete_one(collection=self.collection_name, query=query)


class AsyncDocumentWorker(BaseDocumentWorker):  # type: ignore[type-arg]
    """Document wrapper for asynchronous MongoDB operations.

    Provides async methods to save and delete documents.
    """

    def __init__(
        self,
        pydantic_object: T,
        driver: AbstractAsyncMongoDBDriver,
        objectId: str | None = None,  # noqa: N803
        collection_name: str | None = None,
    ):
        """Initialize the async document worker.

        Args:
            pydantic_object (T): The Pydantic model to wrap.
            driver (AbstractAsyncMongoDBDriver): The async MongoDB driver.
            objectId (Union[str, None]): ObjectId for the document.
            collection_name (Union[str, None]): Optionally set the name of the collection to persist the document to.
        """
        super().__init__(
            pydantic_object=pydantic_object,
            objectId=objectId,
            collection_name=collection_name,
        )
        self.driver = driver

    async def save(self) -> dict[str, Any]:
        """Save the document to MongoDB asynchronously. Inserts if no ObjectId is present, or updates otherwise.

        Returns:
            dict: Result of the insert or update operation.
        """
        payload = self.serialize()

        if self.objectId is None:
            response = await self.driver.insert_one(self.collection_name, payload)
            self.objectId = response.get("inserted_id")
        else:
            query = {"_id": ObjectId(self.objectId)}
            response = await self.driver.update_one(self.collection_name, query=query, update={"$set": payload})

        return response

    async def delete(self) -> dict[str, Any]:
        """Delete the document from MongoDB asynchronously using its ObjectId.

        Returns:
            dict: Result of the delete operation.
        """
        query = self.get_query()
        return await self.driver.delete_one(collection=self.collection_name, query=query)

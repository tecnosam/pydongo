from typing import Any, Generic, TypeVar, Optional, Union
from pydantic import BaseModel

from pydongo.drivers.base import (
    AbstractSyncMongoDBDriver,
    AbstractAsyncMongoDBDriver,
    AbstractMongoDBDriver,
)
from pydongo.utils.serializer import replace_unserializable_fields


T = TypeVar("T", bound=BaseModel)


def as_document(
    pydantic_object: T, driver: AbstractMongoDBDriver
) -> Union["DocumentWorker", "AsyncDocumentWorker"]:
    if issubclass(driver.__class__, AbstractAsyncMongoDBDriver):
        return AsyncDocumentWorker(pydantic_object=pydantic_object, driver=driver)  # type: ignore
    return DocumentWorker(pydantic_object=pydantic_object, driver=driver)  # type: ignore


class SaveResponse(BaseModel):
    inserted_id: Optional[str] = None
    modified_id: Optional[str] = None


class DeleteResponse(BaseModel):
    delete_count: int = 0


class BaseDocumentWorker(Generic[T]):
    def __init__(
        self, pydantic_object: T, objectId: Optional[str] = None, *args, **kwargs
    ):
        self.pydantic_object = pydantic_object
        self.objectId = objectId

    @property
    def collection_name(self):
        """
        Figure out the right collection name based on the pydantic
        model parsed.
        """
        if hasattr(self.pydantic_object, "collection_name"):
            return self.pydantic_object.collection_name

        # todo: find a nicer way to do this
        return self.pydantic_object.__class__.__name__

    def get_query(self) -> dict:
        """
        Returns a mongodb query that will yield the object when parsed to mongodb
        """
        # TODO: system for figuring out primary key from pydantic model
        return self.pydantic_object.model_dump()

    def serialize(self) -> dict:
        """
        Returns a JSON serializable dictionary of the pydantic object
        """

        clean_object = replace_unserializable_fields(self.pydantic_object)
        return clean_object.model_dump()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.pydantic_object, name)


class DocumentWorker(BaseDocumentWorker):
    def __init__(
        self,
        pydantic_object: T,
        objectId: Optional[None],
        driver: AbstractSyncMongoDBDriver,
    ):
        super().__init__(pydantic_object=pydantic_object, objectId=objectId)
        self.driver = driver

    def save(self):
        # TODO: sanity check for non-json serializable fields

        payload = self.serialize()
        if self.objectId is None:
            response = self.driver.insert_one(self.collection_name, payload)
            self.objectId = response.get("insertion_id")
        else:
            query = {"_id": self.objectId}
            response = self.driver.update_one(
                self.collection_name, query=query, update=payload
            )

    def delete(self) -> DeleteResponse:
        query = self.get_query()
        response = self.driver.delete_one(collection=self.collection_name, query=query)
        # TODO: this should return the correct delete count
        # TODO: update DeleteResponse to contain reference to deleted object
        return DeleteResponse(delete_count=1)


class AsyncDocumentWorker(BaseDocumentWorker):
    def __init__(
        self,
        pydantic_object: T,
        objectId: Optional[None],
        driver: AbstractAsyncMongoDBDriver,
    ):
        super().__init__(pydantic_object=pydantic_object, objectId=objectId)
        self.driver = driver

    async def save(self):
        payload = self.serialize()
        if self.objectId is None:
            response = await self.driver.insert_one(self.collection_name, payload)
            self.objectId = response.get("insertion_id")
        else:
            query = {"_id": self.objectId}
            response = await self.driver.update_one(
                self.collection_name, query=query, update=payload
            )

    async def delete(self) -> DeleteResponse:
        query = self.get_query()
        response = await self.driver.delete_one(
            collection=self.collection_name, query=query
        )

        # TODO: this should return the correct delete count
        # TODO: update DeleteResponse to contain reference to deleted object
        return DeleteResponse(delete_count=1)

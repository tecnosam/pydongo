from abc import ABC
from typing import (
    Generic,
    Iterable,
    Optional,
    Sequence,
    Set,
    Type,
    TypeVar,
    Union,
    get_origin,
)
from pydantic import BaseModel

from pydongo.expressions.field import ArrayFieldExpression, FieldExpression
from pydongo.expressions.filter import CollectionFilterExpression

from pydongo.drivers.base import (
    AbstractMongoDBDriver,
    AbstractSyncMongoDBDriver,
    AbstractAsyncMongoDBDriver,
)
from pydongo.utils.serializer import restore_unserializable_fields

from .document import DocumentWorker, AsyncDocumentWorker, BaseDocumentWorker


T = TypeVar("T", bound=BaseModel)


def as_collection(
    pydantic_model: Type[T],
    driver: Union[AbstractSyncMongoDBDriver, AbstractAsyncMongoDBDriver],
) -> "CollectionWorker":
    return CollectionWorker(pydantic_model=pydantic_model, driver=driver)


class CollectionWorker(Generic[T]):
    def __init__(
        self,
        pydantic_model: Type[T],
        driver: Union[AbstractSyncMongoDBDriver, AbstractAsyncMongoDBDriver],
    ):
        self.pydantic_model = pydantic_model
        self.driver = driver

        self.response_builder_class = (
            AsyncCollectionResponseBuilder
            if issubclass(type(driver), AbstractAsyncMongoDBDriver)
            else SyncCollectionResponseBuilder
        )

    def find_one(
        self, expression: CollectionFilterExpression
    ) -> Optional[DocumentWorker]:
        """
        Takes in filter expression, queries the database and returns a pydantic
        model if found
        """

        if issubclass(type(self.driver), AbstractAsyncMongoDBDriver):
            raise AttributeError(
                "Use the afind_one method instead as you're using an async driver"
            )
        result = self.driver.find_one(self.collection_name, expression.serialize())

        return (
            CollectionResponseBuilder.serialize_document(  # type: ignore
                document=result,  # type: ignore
                document_worker_class=DocumentWorker,
                pydantic_model=self.pydantic_model,
                driver=self.driver,
            )
            if result
            else None
        )

    async def afind_one(
        self, expression: CollectionFilterExpression
    ) -> Optional[AsyncDocumentWorker]:
        """
        Takes in filter expression, queries the database and returns a pydantic
        model if found
        """

        if issubclass(type(self.driver), AbstractSyncMongoDBDriver):
            raise AttributeError(
                "Use the find_one method instead as you're using a sync driver"
            )
        result = await self.driver.find_one(
            self.collection_name, expression.serialize()
        )  # type: ignore

        return (
            CollectionResponseBuilder.serialize_document(  # type: ignore
                document=result,  # type: ignore
                document_worker_class=AsyncDocumentWorker,
                pydantic_model=self.pydantic_model,
                driver=self.driver,
            )
            if result
            else None
        )

    def find(
        self, expression: Optional[CollectionFilterExpression] = None
    ) -> "CollectionResponseBuilder":
        """
        Takes in a filter expression, and returns a CollectionResponseBuilder
        that can be used to fetch the actual results from the database
        """
        expression = expression or CollectionFilterExpression({})

        return self.response_builder_class(
            expression=expression,
            pydantic_model=self.pydantic_model,
            driver=self.driver,  # type: ignore
            collection_name=self.collection_name,
        )

    def __getattr__(self, name: str) -> FieldExpression:
        if name not in self.pydantic_model.model_fields:
            raise AttributeError(
                f"'{self.pydantic_model.__name__}' has no field named '{name}'"
            )
        annotation = self.pydantic_model.model_fields[name].annotation

        # TODO: handle Optional fields or Unions elegantly
        data_type = get_origin(annotation) or annotation
        if issubclass(data_type, (Sequence, Set)):  # type: ignore
            return ArrayFieldExpression(name, annotation=annotation)
        return FieldExpression(name, annotation=annotation)

    @property
    def collection_name(self):
        """
        Figure out the right collection name based on the pydantic
        model parsed.
        """
        if hasattr(self.pydantic_model, "collection_name"):
            return self.pydantic_model.collection_name

        # todo: find a nicer way to do this
        return self.pydantic_model.__name__


class CollectionResponseBuilder(ABC, Generic[T]):
    """
    Used to stack response commands like sort(), limit(), find()
    """

    def __init__(
        self,
        expression: CollectionFilterExpression,
        pydantic_model: Type[T],
        driver: Union[AbstractSyncMongoDBDriver, AbstractAsyncMongoDBDriver],
        collection_name: str,
    ):
        self._expression = expression
        self._sort_criteria: Sequence[FieldExpression] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None

        self.model = pydantic_model
        self.driver = driver
        self.collection_name = collection_name

    def skip(self, offset: int) -> "CollectionResponseBuilder":
        self._offset = offset
        return self

    def limit(self, limit_value: int) -> "CollectionResponseBuilder":
        self._limit = limit_value
        return self

    def sort(
        self, sort_criteria: Union[FieldExpression, Sequence[FieldExpression]]
    ) -> "CollectionResponseBuilder":
        self._sort_criteria = (
            [sort_criteria]
            if isinstance(sort_criteria, FieldExpression)
            else sort_criteria
        )
        return self

    def build_kwargs(self) -> dict:
        """
        Return a dictionary consisting of all the information needed to query the database
        """
        query = self._expression.serialize()
        sortby = {
            expr.field_name: 1 if expr.sort_ascending else -1
            for expr in self._sort_criteria
        }

        return {
            "query": query,
            "sort_criteria": sortby,
            "offset": self._offset,
            "limit": self._limit,
        }

    @classmethod
    def serialize_document(
        cls,
        document: dict,
        document_worker_class: Type[BaseDocumentWorker],
        pydantic_model: Type[T],
        driver: AbstractMongoDBDriver,
    ) -> BaseDocumentWorker:
        deserialized_doc = restore_unserializable_fields(document=document)
        pydantic_object = pydantic_model(**deserialized_doc)
        objectId = deserialized_doc.get("_id")
        return document_worker_class(
            pydantic_object=pydantic_object, driver=driver, objectId=objectId
        )


class SyncCollectionResponseBuilder(CollectionResponseBuilder):
    def __init__(
        self,
        expression: CollectionFilterExpression,
        pydantic_model: Type[T],
        driver: AbstractSyncMongoDBDriver,
        collection_name: str,
    ):
        if issubclass(type(driver), AbstractAsyncMongoDBDriver):
            raise AttributeError(
                "Use the AsyncCollectionResponseBuilder instead as you're using an async driver"
            )
        super().__init__(expression, pydantic_model, driver, collection_name)

    def exists(self) -> bool:
        """
        Check the database to see if an object that matches the filter exists

        Could be synchronous or asynchronous
        """

        return self.driver.exists(self.collection_name, self._expression.serialize())  # type: ignore

    def count(self) -> int:
        """
        Count the number of documents that match the filter.

        Could be synchronous or asynchronous
        """

        return self.driver.count(self.collection_name, self._expression.serialize())  # type: ignore

    def all(self) -> Iterable[DocumentWorker]:
        """
        Returns an iteratable element of all the documents marshaled with
        the pydantic model.

        Could be synchronous or asynchronous
        """

        kwargs = self.build_kwargs()
        documents = self.driver.find_many(collection=self.collection_name, **kwargs)  # type: ignore

        for doc in documents:  # type: ignore
            yield self.serialize_document(
                document=doc,
                document_worker_class=DocumentWorker,
                pydantic_model=self.model,
                driver=self.driver,
            )  # type: ignore

    def paginate(self, page_size: int, page_number: int) -> Iterable[T]:
        """
        Returns the response from mongodb in an iterator for the data paginated (in batches)

        Could be synchronous or asynchronous
        """

        self.skip((page_number - 1) * page_size)
        self.limit(page_size)

        return []


class AsyncCollectionResponseBuilder(CollectionResponseBuilder):
    def __init__(
        self,
        expression: CollectionFilterExpression,
        pydantic_model: Type[T],
        driver: AbstractAsyncMongoDBDriver,
        collection_name: str,
    ):
        super().__init__(expression, pydantic_model, driver, collection_name)
        if issubclass(type(self.driver), AbstractSyncMongoDBDriver):
            raise AttributeError(
                "Use the SyncCollectionResponseBuilder instead as you're using a sync driver"
            )

    async def exists(self) -> bool:
        """
        Check the database to see if an object that matches the filter exists
        """

        return await self.driver.exists(
            self.collection_name, self._expression.serialize()
        )  # type: ignore

    async def count(self) -> int:
        """
        Count the number of documents that match the filter.
        """

        return await self.driver.count(
            self.collection_name, self._expression.serialize()
        )  # type: ignore

    async def all(self) -> Iterable[AsyncDocumentWorker]:
        """
        Returns an iteratable element of all the documents marshaled with
        the pydantic model.
        """
        kwargs = self.build_kwargs()
        documents = await self.driver.find_many(
            collection=self.collection_name, **kwargs
        )  # type: ignore

        return [
            self.serialize_document(
                document,
                AsyncDocumentWorker,
                pydantic_model=self.model,
                driver=self.driver,
            )  # type: ignore
            async for document in documents
        ]

    async def paginate(self, page_size: int, page_number: int) -> Iterable[Iterable[T]]:
        """
        Returns the response from mongodb in an iterator for the data paginated (in batches)
        """

        return []

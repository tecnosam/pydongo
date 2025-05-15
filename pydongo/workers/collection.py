from abc import ABC
from typing import (
    Generic,
    Iterable,
    Optional,
    Sequence,
    Type,
    Tuple,
    Set,
    TypeVar,
    Union,
)
from pydantic import BaseModel

from pydongo.expressions.field import FieldExpression
from pydongo.expressions.filter import CollectionFilterExpression
from pydongo.expressions.index import IndexExpression

from pydongo.drivers.base import (
    AbstractMongoDBDriver,
    AbstractSyncMongoDBDriver,
    AbstractAsyncMongoDBDriver,
)
from pydongo.utils.annotations import resolve_annotation
from pydongo.utils.serializer import restore_unserializable_fields

from .document import DocumentWorker, AsyncDocumentWorker, BaseDocumentWorker


T = TypeVar("T", bound=BaseModel)


def as_collection(
    pydantic_model: Type[T],
    driver: Union[AbstractSyncMongoDBDriver, AbstractAsyncMongoDBDriver],
    collection_name: Optional[str] = None,
) -> "CollectionWorker":
    return CollectionWorker(
        pydantic_model=pydantic_model,
        driver=driver,
        collection_name=collection_name,
    )


class CollectionWorker(Generic[T]):
    """
    Entry point for querying and interacting with a MongoDB collection.

    Wraps a Pydantic model and MongoDB driver, and exposes queryable field expressions
    and high-level `find_one`, `afind_one`, and `find` methods.

    Supports both sync and async drivers via conditional branching.
    """

    def __init__(
        self,
        pydantic_model: Type[T],
        driver: Union[AbstractSyncMongoDBDriver, AbstractAsyncMongoDBDriver],
        collection_name: Optional[str] = None,
    ):
        self.pydantic_model = pydantic_model
        self.driver = driver
        self._indexes: Set[Tuple[IndexExpression]] = set()
        self.__collection_name = collection_name

        self.response_builder_class = (
            AsyncCollectionResponseBuilder
            if issubclass(type(driver), AbstractAsyncMongoDBDriver)
            else SyncCollectionResponseBuilder
        )

    def find_one(
        self, expression: CollectionFilterExpression
    ) -> Optional[DocumentWorker]:
        """
        Query the database for a single document that matches the filter expression.
        Only works with a synchronous driver.

        Args:
            expression (CollectionFilterExpression): The MongoDB-style filter expression.

        Returns:
            Optional[DocumentWorker]: A wrapped Pydantic object if found, otherwise None.
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
        Asynchronously query the database for a single document matching the filter expression.
        Only works with an async driver.

        Args:
            expression (CollectionFilterExpression): The MongoDB-style filter expression.

        Returns:
            Optional[AsyncDocumentWorker]: A wrapped Pydantic object if found, otherwise None.
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
        Initiates a fluent response builder chain for querying multiple documents.

        Args:
            expression (Optional[CollectionFilterExpression]): Optional filter expression.

        Returns:
            CollectionResponseBuilder: Builder for fluent chaining (e.g., .limit(), .sort()).
        """
        expression = expression or CollectionFilterExpression({})

        return self.response_builder_class(
            expression=expression,
            pydantic_model=self.pydantic_model,
            driver=self.driver,  # type: ignore
            collection_name=self.collection_name,
            indexes=self._indexes,
        )

    def use_index(
        self,
        index: Union[IndexExpression, Tuple[IndexExpression]],
    ):
        """
        Registers an index (or compound index) on the collection.

        Accepts IndexExpression(s)

        Args:
            index: A single IndexExpression, or a tuple of them.

        Returns:
            CollectionWorker: Self, for method chaining.
        """

        index = (index,) if isinstance(index, IndexExpression) else index
        self._indexes.add(index)
        return self

    def __getattr__(self, name: str) -> FieldExpression:
        """
        Returns a field expression object to enable DSL-style querying using comparison
        operators or dot notation for nested objects.

        Args:
            name (str): Field name in the Pydantic model.

        Returns:
            FieldExpression: Expression object tied to the field.

        Raises:
            AttributeError: If the field does not exist on the model.
        """
        if name not in self.pydantic_model.model_fields:
            raise AttributeError(
                f"'{self.pydantic_model.__name__}' has no field named '{name}'"
            )
        annotation = self.pydantic_model.model_fields[name].annotation
        annotation = resolve_annotation(annotation=annotation)
        return FieldExpression.get_field_expression(name, annotation)

    @property
    def collection_name(self) -> str:
        """
        Derives the MongoDB collection name from the model or falls back to the class name.

        Returns:
            str: The name of the collection.
        """

        if self.__collection_name is None:
            self.__collection_name = str(
                self.pydantic_model.model_config.get(
                    "collection_name",
                    self.pydantic_model.__name__.lower().rstrip("s") + "s",
                )
            )

        return self.__collection_name


class CollectionResponseBuilder(ABC, Generic[T]):
    """
    Fluent builder for composing queries and retrieving lists of documents.

    Can build the final MongoDB query structure with sort, skip, and limit options.
    """

    def __init__(
        self,
        expression: CollectionFilterExpression,
        pydantic_model: Type[T],
        driver: Union[AbstractSyncMongoDBDriver, AbstractAsyncMongoDBDriver],
        collection_name: str,
        indexes: Iterable[Tuple[IndexExpression]],
    ):
        self._expression = expression
        self._sort_criteria: Sequence[FieldExpression] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None

        self._indexes = indexes
        self._indexes_created = False

        self.model = pydantic_model
        self.driver = driver
        self.collection_name = collection_name

    def skip(self, offset: int) -> "CollectionResponseBuilder":
        """
        Skip the first N documents in the query result.

        Args:
            offset (int): Number of documents to skip.

        Returns:
            CollectionResponseBuilder: For chaining.
        """
        self._offset = offset
        return self

    def limit(self, limit_value: int) -> "CollectionResponseBuilder":
        """
        Limit the number of documents returned.

        Args:
            limit_value (int): Maximum number of documents to return.

        Returns:
            CollectionResponseBuilder: For chaining.
        """
        self._limit = limit_value
        return self

    def sort(
        self, sort_criteria: Union[FieldExpression, Sequence[FieldExpression]]
    ) -> "CollectionResponseBuilder":
        """
        Apply sort criteria to the query.

        Args:
            sort_criteria (Union[FieldExpression, Sequence[FieldExpression]]): Sort instructions.

        Returns:
            CollectionResponseBuilder: For chaining.
        """
        self._sort_criteria = (
            [sort_criteria]
            if isinstance(sort_criteria, FieldExpression)
            else sort_criteria
        )
        return self

    def build_kwargs(self) -> dict:
        """
        Assembles the query, sort, offset, and limit into a single dictionary.

        Returns:
            dict: MongoDB-compatible query parameters.
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
        """
        Deserialize a raw MongoDB document and wrap it in a DocumentWorker.

        Args:
            document (dict): Raw document from the database.
            document_worker_class (Type): Either DocumentWorker or AsyncDocumentWorker.
            pydantic_model (Type): Model class to hydrate.
            driver (AbstractMongoDBDriver): Driver used to perform operations.

        Returns:
            BaseDocumentWorker: Wrapped document instance.
        """
        deserialized_doc = restore_unserializable_fields(document=document)
        pydantic_object = pydantic_model(**deserialized_doc)
        objectId = deserialized_doc.get("_id")
        return document_worker_class(
            pydantic_object=pydantic_object, driver=driver, objectId=objectId
        )


class SyncCollectionResponseBuilder(CollectionResponseBuilder):
    """
    Response builder for synchronous drivers.

    Provides direct methods to count, check existence, and iterate documents.
    """

    def __init__(
        self,
        expression: CollectionFilterExpression,
        pydantic_model: Type[T],
        driver: AbstractSyncMongoDBDriver,
        collection_name: str,
        indexes: Iterable[Tuple[IndexExpression]],
    ):
        if issubclass(type(driver), AbstractAsyncMongoDBDriver):
            raise AttributeError(
                "Use the AsyncCollectionResponseBuilder instead as you're using an async driver"
            )
        super().__init__(expression, pydantic_model, driver, collection_name, indexes)

    def exists(self) -> bool:
        """
        Check if any document matches the filter expression.

        Returns:
            bool: True if at least one document exists.
        """

        self.create_indexes()
        return self.driver.exists(self.collection_name, self._expression.serialize())  # type: ignore

    def count(self) -> int:
        """
        Count how many documents match the filter expression.

        Returns:
            int: Number of matching documents.
        """

        self.create_indexes()
        return self.driver.count(self.collection_name, self._expression.serialize())  # type: ignore

    def all(self) -> Iterable[DocumentWorker]:
        """
        Retrieve all documents that match the current query builder state.

        Returns:
            Iterable[DocumentWorker]: Generator of hydrated documents.
        """

        self.create_indexes()
        kwargs = self.build_kwargs()
        documents = self.driver.find_many(collection=self.collection_name, **kwargs)  # type: ignore

        for doc in documents:  # type: ignore
            yield self.serialize_document(
                document=doc,
                document_worker_class=DocumentWorker,
                pydantic_model=self.model,
                driver=self.driver,
            )  # type: ignore

    def create_indexes(self):
        """
        Creates indexes on the MongoDB database.
        """

        if self._indexes_created:
            return
        for index in self._indexes:
            self.driver.create_index(self.collection_name, index)
        self._indexes_created = True


class AsyncCollectionResponseBuilder(CollectionResponseBuilder):
    """
    Response builder for asynchronous drivers.

    Supports async versions of exists, count, and all().
    """

    def __init__(
        self,
        expression: CollectionFilterExpression,
        pydantic_model: Type[T],
        driver: AbstractAsyncMongoDBDriver,
        collection_name: str,
        indexes: Iterable[Tuple[IndexExpression]],
    ):
        super().__init__(expression, pydantic_model, driver, collection_name, indexes)
        if issubclass(type(self.driver), AbstractSyncMongoDBDriver):
            raise AttributeError(
                "Use the SyncCollectionResponseBuilder instead as you're using a sync driver"
            )

    async def exists(self) -> bool:
        """
        Asynchronously check if any document matches the filter.

        Returns:
            bool: True if a match exists.
        """

        await self.create_indexes()
        return await self.driver.exists(
            self.collection_name, self._expression.serialize()
        )  # type: ignore

    async def count(self) -> int:
        """
        Asynchronously count how many documents match the filter.

        Returns:
            int: Number of matching documents.
        """

        await self.create_indexes()
        return await self.driver.count(
            self.collection_name, self._expression.serialize()
        )  # type: ignore

    async def all(self) -> Iterable[AsyncDocumentWorker]:
        """
        Asynchronously retrieve all matching documents.

        Returns:
            Iterable[AsyncDocumentWorker]: List of wrapped async document objects.
        """

        await self.create_indexes()
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

    async def create_indexes(self):
        """
        Asynchronously creates indexes on the MongoDB database.
        """

        if self._indexes_created:
            return
        for index in self._indexes:
            await self.driver.create_index(self.collection_name, index)
        self._indexes_created = True

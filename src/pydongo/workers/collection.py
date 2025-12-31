from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import Any, Generic, Self, TypeVar

from pydantic import BaseModel

from pydongo.drivers.base import AbstractAsyncMongoDBDriver, AbstractMongoDBDriver, AbstractSyncMongoDBDriver
from pydongo.expressions.field import FieldExpression
from pydongo.expressions.filter import CollectionFilterExpression
from pydongo.expressions.index import IndexExpression
from pydongo.expressions.mutation import MutationExpression, MutationExpressionContext
from pydongo.utils.annotations import resolve_annotation
from pydongo.utils.serializer import restore_unserializable_fields
from pydongo.workers.document import AsyncDocumentWorker, BaseDocumentWorker, DocumentWorker

T = TypeVar("T", bound=BaseModel)


def as_collection(
    pydantic_model: type[T],
    driver: AbstractSyncMongoDBDriver | AbstractAsyncMongoDBDriver,
    collection_name: str | None = None,
) -> "CollectionWorker[T]":
    """Wraps a Pydantic model in a CollectionWorker for querying and interacting with the corresponding MongoDB collection.

    Args:
        pydantic_model (type[T]): The Pydantic model class to wrap.
        driver (Union[AbstractSyncMongoDBDriver, AbstractAsyncMongoDBDriver]): The MongoDB driver to use.
        collection_name (Union[str, None]): The name of the MongoDB collection. Defaults to None.

    Returns:
        CollectionWorker: A CollectionWorker instance.
    """  # noqa: E501
    return CollectionWorker(
        pydantic_model=pydantic_model,
        driver=driver,
        collection_name=collection_name,
    )


def _get_field_expression(
    name: str, model: type[T], mutation_ctx: MutationExpressionContext | None = None
) -> FieldExpression:
    if name not in model.model_fields:
        raise AttributeError(f"'{model.__name__}' has no field named '{name}'")
    annotation = model.model_fields[name].annotation
    annotation = resolve_annotation(annotation=annotation)

    return FieldExpression.get_field_expression(name, annotation, mutation_ctx)


class CollectionWorker(Generic[T]):
    """Entry point for querying and interacting with a MongoDB collection.

    Wraps a Pydantic model and MongoDB driver, and exposes queryable field expressions
    and high-level `find_one`, `afind_one`, and `find` methods.

    Supports both sync and async drivers via conditional branching.
    """

    def __init__(
        self,
        pydantic_model: type[T],
        driver: AbstractSyncMongoDBDriver | AbstractAsyncMongoDBDriver,
        collection_name: str | None = None,
    ):
        self.pydantic_model = pydantic_model
        self.driver = driver
        self._indexes: set[tuple[IndexExpression]] = set()
        self.__collection_name = collection_name

        self.response_builder_class = (
            AsyncCollectionResponseBuilder
            if issubclass(type(driver), AbstractAsyncMongoDBDriver)
            else SyncCollectionResponseBuilder
        )

    def find_one(self, expression: CollectionFilterExpression) -> BaseDocumentWorker[T] | None:
        """Query the database for a single document that matches the filter expression.

        Only works with a synchronous driver.

        Args:
            expression (CollectionFilterExpression): The MongoDB-style filter expression.

        Returns:
            Union[DocumentWorker, None]: A wrapped Pydantic object if found, otherwise None.
        """
        if issubclass(type(self.driver), AbstractAsyncMongoDBDriver):
            raise AttributeError("Use the afind_one method instead as you're using an async driver")
        result = self.driver.find_one(self.collection_name, expression.serialize())

        return (
            CollectionResponseBuilder.serialize_document(
                document=result,  # type: ignore[arg-type]
                document_worker_class=DocumentWorker,
                pydantic_model=self.pydantic_model,
                driver=self.driver,
            )
            if result
            else None
        )

    async def afind_one(self, expression: CollectionFilterExpression) -> BaseDocumentWorker[T] | None:
        """Asynchronously query the database for a single document matching the filter expression.

        Only works with an async driver.

        Args:
            expression (CollectionFilterExpression): The MongoDB-style filter expression.

        Returns:
            Union[BaseDocumentWorker[T], None]: A wrapped Pydantic object if found, otherwise None.
        """
        if issubclass(type(self.driver), AbstractSyncMongoDBDriver):
            raise AttributeError("Use the find_one method instead as you're using a sync driver")
        result = await self.driver.find_one(self.collection_name, expression.serialize())

        return (
            CollectionResponseBuilder.serialize_document(
                document=result,
                document_worker_class=AsyncDocumentWorker,
                pydantic_model=self.pydantic_model,
                driver=self.driver,
            )
            if result
            else None
        )

    def find(self, expression: CollectionFilterExpression | None = None) -> "CollectionResponseBuilder[T]":
        """Initiates a fluent response builder chain for querying multiple documents.

        Args:
            expression (Union[CollectionFilterExpression, None]): Optional filter expression.

        Returns:
            CollectionResponseBuilder: Builder for fluent chaining (e.g., .limit(), .sort()).
        """
        expression = expression or CollectionFilterExpression({})

        return self.response_builder_class(
            expression=expression,
            pydantic_model=self.pydantic_model,
            driver=self.driver,  # type: ignore[arg-type]
            collection_name=self.collection_name,
            indexes=self._indexes,
        )

    def use_index(
        self,
        index: IndexExpression | tuple[IndexExpression, ...],
    ) -> Self:
        """Registers an index (or compound index) on the collection.

        Accepts IndexExpression(s)

        Args:
            index: A single IndexExpression, or a tuple of them.

        Returns:
            CollectionWorker: Self, for method chaining.
        """
        index = (index,) if isinstance(index, IndexExpression) else index
        self._indexes.add(index)  # type: ignore[arg-type]
        return self

    def __getattr__(self, name: str) -> FieldExpression:
        """Returns a field expression object to enable DSL-style querying using comparison operators or dot notation for nested objects.

        Args:
            name (str): Field name in the Pydantic model.

        Returns:
            FieldExpression: Expression object tied to the field.

        Raises:
            AttributeError: If the field does not exist on the model.
        """  # noqa: E501
        return _get_field_expression(name, self.pydantic_model)

    @property
    def collection_name(self) -> str:
        """Derives the MongoDB collection name from the model or falls back to the class name.

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
    """Fluent builder for composing queries and retrieving lists of documents.

    Can build the final MongoDB query structure with sort, skip, and limit options.
    """

    def __init__(
        self,
        expression: CollectionFilterExpression,
        pydantic_model: type[T],
        collection_name: str,
        indexes: Iterable[tuple[IndexExpression]],
        **kwargs: dict[str, Any],
    ):
        self.model = pydantic_model
        self._expression = expression
        self._sort_criteria: Sequence[FieldExpression] = []
        self._limit: int | None = None
        self._offset: int | None = None

        self._indexes = indexes
        self._indexes_created = False

        self.collection_name = collection_name

        self.__mutation_ctx = MutationExpressionContext()
        self._other_kwargs = kwargs

    def skip(self, offset: int) -> "CollectionResponseBuilder[T]":
        """Skip the first N documents in the query result.

        Args:
            offset (int): Number of documents to skip.

        Returns:
            CollectionResponseBuilder: For chaining.
        """
        self._offset = offset
        return self

    def limit(self, limit_value: int) -> "CollectionResponseBuilder[T]":
        """Limit the number of documents returned.

        Args:
            limit_value (int): Maximum number of documents to return.

        Returns:
            CollectionResponseBuilder: For chaining.
        """
        self._limit = limit_value
        return self

    def sort(self, sort_criteria: FieldExpression | Sequence[FieldExpression]) -> "CollectionResponseBuilder[T]":
        """Apply sort criteria to the query.

        Args:
            sort_criteria (Union[FieldExpression, Sequence[FieldExpression]]): Sort instructions.

        Returns:
            CollectionResponseBuilder: For chaining.
        """
        self._sort_criteria = [sort_criteria] if isinstance(sort_criteria, FieldExpression) else sort_criteria
        return self

    def build_kwargs(self) -> dict[str, Any]:
        """Assembles the query, sort, offset, and limit into a single dictionary.

        Returns:
            dict: MongoDB-compatible query parameters.
        """
        query = self._expression.serialize()
        sortby = {expr.field_name: 1 if expr.sort_ascending else -1 for expr in self._sort_criteria}

        return {
            "query": query,
            "sort_criteria": sortby,
            "offset": self._offset,
            "limit": self._limit,
        }

    def get_mutations(self) -> dict[str, Any]:
        """Get current mutation context."""
        return self.__mutation_ctx.get_mutations()

    def mutate(self) -> dict[str, Any]:
        """Run mutations through driver."""
        if isinstance(self.driver, AbstractSyncMongoDBDriver):
            update = self.driver.update_many(self.collection_name, self._expression.serialize(), self.get_mutations())

            self.__mutation_ctx.clear()
            return update

        raise AttributeError("Use the amutate method instead for async drivers")

    async def amutate(self) -> dict[str, Any]:
        """Run mutations through driver."""
        if isinstance(self.driver, AbstractAsyncMongoDBDriver):
            update = await self.driver.update_many(
                self.collection_name, self._expression.serialize(), self.get_mutations()
            )
            self.__mutation_ctx.clear()
            return update

        raise AttributeError("Use the mutate method instead for sync drivers")

    @classmethod
    def serialize_document(
        cls,
        document: dict[str, Any],
        document_worker_class: type[BaseDocumentWorker[T]],
        pydantic_model: type[T],
        driver: AbstractMongoDBDriver,
    ) -> BaseDocumentWorker[T]:
        """Deserialize a raw MongoDB document and wrap it in a DocumentWorker.

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
        object_id = deserialized_doc.get("_id")
        return document_worker_class(pydantic_object=pydantic_object, driver=driver, objectId=object_id)

    @property
    @abstractmethod
    def driver(self) -> AbstractSyncMongoDBDriver | AbstractAsyncMongoDBDriver:
        """The MongoDB driver instance.

        Returns:
            AbstractMongoDBDriver: The driver used for database operations.
        """

    def __setattr__(self, name: str, value: Any) -> None:
        """Push a mutation when setting an attribute on the fictional document worker.

        Args:
            name (str): The field name.
            value (Any): The value to set.

        Returns:
            None
        """
        if name == "model":
            return super().__setattr__(name, value)

        if name not in self.model.model_fields:
            return super().__setattr__(name, value)

        if isinstance(value, MutationExpression):
            self.__mutation_ctx.add_mutation(value)
            return None

        expression: FieldExpression = _get_field_expression(
            name=name, model=self.model, mutation_ctx=self.__mutation_ctx
        )

        self.__mutation_ctx.add_mutation(expression.set_value(value))
        return None

    def __getattr__(self, name: str) -> FieldExpression:
        """Returns a field expression object to enable DSL-style querying using comparison operators or dot notation for nested objects.

        Args:
            name (str): Field name in the Pydantic model.

        Returns:
            FieldExpression: Expression object tied to the field.

        Raises:
            AttributeError: If the field does not exist on the model.
        """  # noqa: E501
        return _get_field_expression(name, self.model, mutation_ctx=self.__mutation_ctx)


class SyncCollectionResponseBuilder(CollectionResponseBuilder[T]):
    """Response builder for synchronous drivers.

    Provides direct methods to count, chec§k existence, and iterate documents.
    """

    def __init__(
        self,
        expression: CollectionFilterExpression,
        pydantic_model: type[T],
        driver: AbstractSyncMongoDBDriver,
        collection_name: str,
        indexes: Iterable[tuple[IndexExpression]],
    ):
        if issubclass(type(driver), AbstractAsyncMongoDBDriver):
            raise AttributeError("Use the AsyncCollectionResponseBuilder instead as you're using an async driver")

        super().__init__(expression, pydantic_model, collection_name, indexes)
        self.__driver = driver

    def exists(self) -> bool:
        """Check if any document matches the filter expression.

        Returns:
            bool: True if at least one document exists.
        """
        self.create_indexes()
        return self.driver.exists(self.collection_name, self._expression.serialize())

    def count(self) -> int:
        """Count how many documents match the filter expression.

        Returns:
            int: Number of matching documents.
        """
        self.create_indexes()
        return self.driver.count(self.collection_name, self._expression.serialize())

    def all(self) -> Iterable[DocumentWorker]:
        """Retrieve all documents that match the current query builder state.

        Returns:
            Iterable[DocumentWorker]: Generator of hydrated documents.
        """
        self.create_indexes()
        kwargs = self.build_kwargs()
        documents = self.driver.find_many(collection=self.collection_name, **kwargs)

        for doc in documents:
            yield self.serialize_document(
                document=doc,
                document_worker_class=DocumentWorker,
                pydantic_model=self.model,
                driver=self.driver,
            )

    def create_indexes(self) -> None:
        """Creates indexes on the MongoDB database."""
        if self._indexes_created:
            return
        for index in self._indexes:
            self.driver.create_index(self.collection_name, index)
        self._indexes_created = True

    @property
    def driver(self) -> AbstractSyncMongoDBDriver:
        """The MongoDB driver instance.

        Returns:
            AbstractSyncMongoDBDriver: The driver used for database operations.
        """
        return self.__driver


class AsyncCollectionResponseBuilder(CollectionResponseBuilder[T]):
    """Response builder for asynchronous drivers.

    Supports async versions of exists, count, and all().
    """

    def __init__(
        self,
        expression: CollectionFilterExpression,
        pydantic_model: type[T],
        driver: AbstractAsyncMongoDBDriver,
        collection_name: str,
        indexes: Iterable[tuple[IndexExpression]],
    ):
        super().__init__(expression, pydantic_model, collection_name, indexes)
        if issubclass(type(driver), AbstractSyncMongoDBDriver):
            raise AttributeError("Use the SyncCollectionResponseBuilder instead as you're using a sync driver")
        self.__driver = driver

    async def exists(self) -> bool:
        """Asynchronously check if any document matches the filter.

        Returns:
            bool: True if a match exists.
        """
        await self.create_indexes()
        return await self.driver.exists(self.collection_name, self._expression.serialize())

    async def count(self) -> int:
        """Asynchronously count how many documents match the filter.

        Returns:
            int: Number of matching documents.
        """
        await self.create_indexes()
        return await self.driver.count(self.collection_name, self._expression.serialize())

    async def all(self) -> Iterable[AsyncDocumentWorker]:
        """Asynchronously retrieve all matching documents.

        Returns:
            Iterable[AsyncDocumentWorker]: List of wrapped async document objects.
        """
        await self.create_indexes()
        kwargs = self.build_kwargs()
        documents = await self.driver.find_many(collection=self.collection_name, **kwargs)

        if hasattr(documents, "__aiter__"):
            return [
                self.serialize_document(
                    document,
                    AsyncDocumentWorker,
                    pydantic_model=self.model,
                    driver=self.driver,
                )
                async for document in documents
            ]

        return [
            self.serialize_document(
                document,
                AsyncDocumentWorker,
                pydantic_model=self.model,
                driver=self.driver,
            )
            for document in documents
        ]

    async def create_indexes(self) -> None:
        """Asynchronously creates indexes on the MongoDB database."""
        if self._indexes_created:
            return
        for index in self._indexes:
            await self.driver.create_index(self.collection_name, index)
        self._indexes_created = True

    @property
    def driver(self) -> AbstractAsyncMongoDBDriver:
        """The MongoDB driver instance.

        Returns:
            AbstractAsyncMongoDBDriver: The driver used for database operations.
        """
        return self.__driver

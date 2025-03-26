from abc import ABC
from typing import Generic, Iterable, Optional, Type, TypeVar
from pydantic import BaseModel

from pydongo.expressions.filter import CollectionFilterExpression, FieldExpression
from pydongo.expressions.sort import CollectionSortExpression


T = TypeVar("T", bound=BaseModel)


def as_collection(pydantic_model: Type[T]) -> "CollectionWorker":
    return CollectionWorker(pydantic_model=pydantic_model)


class CollectionWorker(Generic[T]):
    def __init__(self, pydantic_model: Type[T]):
        self.pydantic_model = pydantic_model

    def find_one(self, expression: CollectionFilterExpression) -> Optional[T]:
        """
        Takes in filter expression, queries the database and returns a pydantic
        model if found
        """

        return None

    def find(
        self, expression: CollectionFilterExpression
    ) -> "CollectionResponseBuilder":
        """
        Takes in a filter expression, and returns a CollectionResponseBuilder
        that can be used to fetch the actual results from the database
        """

        return SyncCollectionResponseBuilder(
            expression=expression, pydantic_model=self.pydantic_model
        )

    def __getattr__(self, name: str) -> FieldExpression:
        if name not in self.pydantic_model.model_fields:
            raise AttributeError(
                f"'{self.pydantic_model.__name__}' has no field named '{name}'"
            )
        return FieldExpression(name)


class CollectionResponseBuilder(ABC, Generic[T]):
    """
    Used to stack response commands like sort(), limit(), find()
    """

    def __init__(self, expression: CollectionFilterExpression, pydantic_model: Type[T]):
        self._expression = expression
        self._sort_criteria: Optional[CollectionSortExpression] = None
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None

        self.model = pydantic_model

    def skip(self, offset: int) -> "CollectionResponseBuilder":
        self._offset = offset
        return self

    def limit(self, limit_value: int) -> "CollectionResponseBuilder":
        self._limit = limit_value
        return self

    def sort(
        self, sort_criteria: CollectionSortExpression
    ) -> "CollectionResponseBuilder":
        self._sort_criteria = sort_criteria
        return self

    def build_kwargs(self) -> dict:
        """
        Return a dictionary consisting of all the information needed to query the database
        """
        query = self._expression.serialize()
        sortby = self._sort_criteria.serialize() if self._sort_criteria else None
        return {"query": query, "sort": sortby}


class SyncCollectionResponseBuilder(CollectionResponseBuilder):
    def exists(self) -> bool:
        """
        Check the database to see if an object that matches the filter exists

        Could be synchronous or asynchronous
        """

        return True

    def count(self) -> int:
        """
        Count the number of documents that match the filter.

        Could be synchronous or asynchronous
        """

        return 0

    def all(self) -> Iterable[T]:
        """
        Returns an iteratable element of all the documents marshaled with
        the pydantic model.

        Could be synchronous or asynchronous
        """

        return []

    def paginate(self, page_size: int, page_number: int) -> Iterable[Iterable[T]]:
        """
        Returns the response from mongodb in an iterator for the data paginated (in batches)

        Could be synchronous or asynchronous
        """

        return []

        # TODO: return type should be PaginatedResponse[T] containing page information and data


class AsyncCollectionResponseBuilder(CollectionResponseBuilder):
    async def exists(self) -> bool:
        """
        Check the database to see if an object that matches the filter exists
        """

        return True

    async def count(self) -> int:
        """
        Count the number of documents that match the filter.
        """

        return 0

    async def all(self) -> Iterable[T]:
        """
        Returns an iteratable element of all the documents marshaled with
        the pydantic model.
        """
        return []

    async def paginate(self, page_size: int, page_number: int) -> Iterable[Iterable[T]]:
        """
        Returns the response from mongodb in an iterator for the data paginated (in batches)
        """

        return []
        # TODO: return type should be PaginatedResponse[T] containing page information and data

import contextvars
from types import TracebackType
from typing import Any

from pydantic import BaseModel

from pydongo.expressions.base import BaseExpression


class MutationExpression(BaseExpression):
    """Expression representing a mutation operation on a document field.

    Args:
        field_name (str): The name of the field to mutate.
        operation (str): The mutation operation (e.g., "$set", "$inc").
        value (Any): The value associated with the mutation operation.
    """

    def __init__(
        self,
        field_name: str,
        operation: str,
        value: Any,
    ):
        self.field_name = field_name
        self.operation = operation
        self.value = value

    def serialize(self) -> dict[str, dict[str, Any]]:
        """Serializes the mutation expression into a MongoDB-style update operation.

        Returns:
            dict: A dictionary representing the mutation operation.
        """
        value = self.value
        if isinstance(value, BaseModel):
            value = value.model_dump()
        return {self.operation: {self.field_name: value}}


class MutationExpressionContext:
    """Context Manager for Mutation expressions across the call stack."""

    _mutations: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar("mutations")

    def __enter__(self) -> "MutationExpressionContext":
        """Enter context."""
        self._token = self._mutations.set({})
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        """Exit current context."""
        self._mutations.reset(self._token)

    @classmethod
    def add_mutation(cls, mutation: "MutationExpression") -> None:
        """Add mutations to context."""
        mutations = cls._mutations.get()
        serialized = mutation.serialize()

        for operator, values in serialized.items():
            mutations.setdefault(operator, {}).update(values)

    @classmethod
    def get_mutations(cls) -> dict[str, Any]:
        """Get mutations from context."""
        return cls._mutations.get()

    @classmethod
    def clear(cls) -> None:
        """Clear the current context."""
        cls._mutations.set({})

    @classmethod
    def has_context(cls) -> bool:
        """Check if current execution has context."""
        try:
            cls._mutations.get()
            return True
        except LookupError:
            return False

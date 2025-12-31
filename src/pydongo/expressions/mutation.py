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

    def __init__(self) -> None:
        self.__mutations: dict[str, Any] = {}

    def add_mutation(self, mutation: "MutationExpression") -> None:
        """Add mutations to context."""
        serialized = mutation.serialize()

        for operator, values in serialized.items():
            self.__mutations.setdefault(operator, {}).update(values)

    def get_mutations(self) -> dict[str, Any]:
        """Get mutations from context."""
        return self.__mutations

    def clear(self) -> None:
        """Clear the current context."""
        self.__mutations = {}

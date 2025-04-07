from typing import Any, Optional
from pydongo.expressions.base import BaseExpression
from pydongo.utils.serializer import HANDLER_MAPPING


# todo: support for field expression on deep nested fields and array fields
# todo: expression values in CollectionFilterExpression should be json serializable data.
# todo: query should be optimized


class CollectionFilterExpression(BaseExpression):
    """
    Generate a Boolean expression used to query the database

    CollectionWorker.field == scalar.

    FilterExpressions can be combined with other filter expressions to form
    another fileter expression:

        1. or: FilterExpression | FilterExpression -> FilterExpression
        2. and: FilterExpression & FilterExpression -> FilterExpression
        3. not: ~FilterExpression -> FilterExpression
    """

    def __init__(self, expression: Optional[dict] = None):
        super().__init__()

        self.expression = expression or {}

    def with_expression(
        self, field_name: str, operator: str, value: Any
    ) -> "CollectionFilterExpression":
        value_class = type(value)
        if value_class in HANDLER_MAPPING:
            value = HANDLER_MAPPING[value_class].serialize(value)

        self.expression[field_name] = {operator: value}
        return self

    def serialize(self) -> dict:
        """
        Serialize a filter expression into a mongodb query
        """

        return self.expression

    def __and__(
        self, other: "CollectionFilterExpression"
    ) -> "CollectionFilterExpression":
        expression = {"$and": [self.expression, other.expression]}
        return CollectionFilterExpression(expression=expression)

    def __or__(
        self, other: "CollectionFilterExpression"
    ) -> "CollectionFilterExpression":
        expression = {"$or": [self.expression, other.expression]}
        return CollectionFilterExpression(expression=expression)

    def __invert__(self) -> "CollectionFilterExpression":
        expression = {"$not": self.expression}
        return CollectionFilterExpression(expression=expression)

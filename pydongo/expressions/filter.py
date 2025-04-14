from typing import Optional
from pydongo.expressions.base import BaseExpression


class CollectionFilterExpression(BaseExpression):
    """
    Generate a Boolean expression used to query the database

    CollectionWorker.field == scalar.

    FilterExpressions can be combined with other filter expressions to form
    another filter expression:

        1. or: FilterExpression | FilterExpression -> FilterExpression
        2. and: FilterExpression & FilterExpression -> FilterExpression
        3. not: ~FilterExpression -> FilterExpression
    """

    def __init__(self, expression: Optional[dict] = None):
        super().__init__()

        self.expression = expression or {}

    def with_expression(self, expression: dict) -> "CollectionFilterExpression":
        self.expression.update(expression)
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

    def __repr__(self):
        return f"<CollectionFilterExpression {self.serialize()}>"

from typing import Any, Optional
from pydongo.expressions.base import BaseExpression


class FieldExpression:
    def __init__(self, field_name: str):
        self.field_name = field_name

    def __eq__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(self.field_name, "$eq", other)

    def __ne__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(self.field_name, "$ne", other)

    def __gt__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(self.field_name, "$gt", other)

    def __ge__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(self.field_name, "$gte", other)

    def __lt__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(self.field_name, "$lt", other)

    def __le__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(self.field_name, "$lte", other)


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

    def with_expression(self, field_name: str, operator: str, value: Any) -> "CollectionFilterExpression":

        self.expressions[field_name] = {operator: value}
        return self

    def serialize(self) -> dict:
        """
        Serialize a filter expression into a mongodb query
        """

        return self.expression

    def __and__(self, other: "CollectionFilterExpression") -> "CollectionFilterExpression":

        expression = {"$and": [self.expression, other.expression]}
        return CollectionFilterExpression(expression=expression)

    def __or__(self, other: "CollectionFilterExpression") -> "CollectionFilterExpression":

        expression = {"$or": [self.expression, other.expression]}
        return CollectionFilterExpression(expression=expression)

    def __invert__(self) -> "CollectionFilterExpression":

        expression = {"$not": self.expression}
        return CollectionFilterExpression(expression=expression)

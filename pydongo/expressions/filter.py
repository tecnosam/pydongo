from typing import Optional
from pydongo.expressions.base import BaseExpression


class CollectionFilterExpression(BaseExpression):
    """
    Represents a boolean filter expression used to query a MongoDB collection.

    These expressions are composable using:
        - Logical OR (`|`)
        - Logical AND (`&`)
        - Logical NOT (`~`)

    Example usage:
        filter_1 = User.age > 18
        filter_2 = User.name == "Samuel"
        combined = filter_1 & filter_2

    The resulting expression can be serialized and passed to the database driver.
    """

    def __init__(self, expression: Optional[dict] = None):
        """
        Initialize the filter expression with an optional initial dictionary.

        Args:
            expression (Optional[dict]): A MongoDB-style query dictionary.
        """
        super().__init__()
        self.expression = expression or {}

    def with_expression(self, expression: dict) -> "CollectionFilterExpression":
        """
        Mutate the internal expression by merging in a new dictionary.

        Args:
            expression (dict): A MongoDB-style query to merge into the current expression.

        Returns:
            CollectionFilterExpression: The current instance (for chaining).
        """
        self.expression.update(expression)
        return self

    def serialize(self) -> dict:
        """
        Serialize the filter expression into a MongoDB-compatible query object.

        Returns:
            dict: Serialized MongoDB query.
        """
        return self.expression

    def __and__(
        self, other: "CollectionFilterExpression"
    ) -> "CollectionFilterExpression":
        """
        Combine this filter with another using a logical AND.

        Args:
            other (CollectionFilterExpression): Another filter to combine with.

        Returns:
            CollectionFilterExpression: A new combined filter.
        """
        expression = {"$and": [self.expression, other.expression]}
        return CollectionFilterExpression(expression=expression)

    def __or__(
        self, other: "CollectionFilterExpression"
    ) -> "CollectionFilterExpression":
        """
        Combine this filter with another using a logical OR.

        Args:
            other (CollectionFilterExpression): Another filter to combine with.

        Returns:
            CollectionFilterExpression: A new combined filter.
        """
        expression = {"$or": [self.expression, other.expression]}
        return CollectionFilterExpression(expression=expression)

    def __invert__(self) -> "CollectionFilterExpression":
        """
        Invert the current filter using a logical NOT.

        Returns:
            CollectionFilterExpression: A new filter expression wrapped in `$not`.
        """
        expression = {"$not": self.expression}
        return CollectionFilterExpression(expression=expression)

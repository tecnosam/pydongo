from enum import Enum, IntEnum
from typing import Any

from pydongo.expressions.base import BaseExpression
from pydongo.expressions.filter import CollectionFilterExpression


class IndexSortOrder(IntEnum):
    """Enum representing index sort order in MongoDB."""

    ASCENDING = 1
    DESCENDING = -1


class IndexType(str, Enum):
    """Enum representing different types of MongoDB indexes."""

    TEXT = "text"
    HASHED = "hashed"
    TWO_DIMENSIONAL = "2d"
    TWO_DIMENSIONAL_SPHERE = "2dsphere"


class CollationStrength(IntEnum):
    """Enum representing the strength levels for string comparison in MongoDB collation."""

    PRIMARY = 1  # Only base characters (e.g., "a" == "A", "é" == "e")
    SECONDARY = 2  # Case-insensitive, accent-sensitive (e.g., "a" == "A", "é" != "e")
    TERTIARY = 3  # Case- and accent-sensitive (e.g., "a" != "A", "é" != "e")
    QUATERNARY = 4  # Includes case, accent, punctuation (e.g., "$a" != "a")
    IDENTICAL = 5  # Everything is compared (e.g., code point level)

    def description(self) -> str:
        """Provides a human-readable description of the collation strength level.

        Returns:
            str: A description of the collation strength level.
        """
        return {
            CollationStrength.PRIMARY: "Base characters only (case-insensitive, accent-insensitive)",
            CollationStrength.SECONDARY: "Accent-sensitive, case-insensitive",
            CollationStrength.TERTIARY: "Case- and accent-sensitive (default)",
            CollationStrength.QUATERNARY: "Includes case, accent, and punctuation",
            CollationStrength.IDENTICAL: "Full Unicode comparison, includes code points",
        }[self]


class IndexExpression(BaseExpression):
    """Represents a MongoDB index definition."""

    def __init__(  # noqa: PLR0913
        self,
        field_name: str,
        index_type: IndexType | None = None,
        sort_order: IndexSortOrder = IndexSortOrder.ASCENDING,
        expires_after_seconds: float | None = None,  # For TTL indexes
        is_sparse: bool | None = None,
        is_unique: bool | None = None,
        is_hidden: bool | None = None,
        collation_locale: str = "en",
        collation_strength: CollationStrength | None = None,
        partial_expression: CollectionFilterExpression | None = None,
        index_name: str | None = None,
    ):
        self.field_name = field_name
        self.index_type = index_type
        self.sort_order = sort_order
        self.expires_after_seconds = expires_after_seconds
        self.is_sparse = is_sparse
        self.is_unique = is_unique
        self.is_hidden = is_hidden
        self.collation_locale = collation_locale
        self.collation_strength = collation_strength
        self.partial_expression = partial_expression
        self.index_name = index_name

    def serialize(self) -> dict[str, Any]:
        """Serialize the index definition into a MongoDB-compatible format."""
        if self.index_type:
            return {self.field_name: self.index_type}
        return {self.field_name: self.sort_order}

    def build_kwargs(self) -> dict[str, Any]:
        """Additional specifications for the index to be passed to MongoDB's create_index.

        Only includes non-null values.
        """
        kwargs: dict[str, Any] = {}

        if self.index_name:
            kwargs["name"] = self.index_name

        if self.expires_after_seconds is not None:
            if self.index_type in (IndexType.TEXT, IndexType.HASHED):
                # TODO: Warning log that the TTL will not be applied as
                # it's not supported with Text
                pass
            else:
                kwargs["expireAfterSeconds"] = self.expires_after_seconds

        if self.is_sparse is not None:
            kwargs["sparse"] = self.is_sparse

        if self.is_unique is not None:
            kwargs["unique"] = self.is_unique

        if self.is_hidden is not None:
            kwargs["hidden"] = self.is_hidden

        if self.collation_strength is not None or self.collation_locale:
            kwargs["collation"] = {
                "locale": self.collation_locale,
                **({"strength": self.collation_strength.value} if self.collation_strength is not None else {}),
            }

        if self.partial_expression is not None:
            kwargs["partialFilterExpression"] = self.partial_expression.serialize()

        return kwargs

    def __hash__(self) -> int:
        """Generate a hash based on the index properties.

        Returns:
            int: A hash value representing the index.
        """
        return hash(
            (
                self.field_name,
                self.index_type,
                self.sort_order,
                self.expires_after_seconds,
                self.is_sparse,
                self.is_unique,
                self.is_hidden,
                self.collation_locale,
                self.collation_strength,
                self.index_name,
                self.partial_expression,
            )
        )

    def __eq__(self, expr: object) -> bool:
        """Compare this index expression with another for equality.

        Args:
            expr (object): The expression to compare against.

        Returns:
            bool: True if the expressions are equal, False otherwise.
        """
        if isinstance(expr, self.__class__):
            return self.build_kwargs() == expr.build_kwargs() and self.serialize() == expr.serialize()

        if isinstance(expr, str):
            return self.field_name == expr
        return False


class IndexExpressionBuilder:
    """Builder pattern for constructing IndexExpression instances with a fluent interface."""

    def __init__(self, field_name: str):
        self.field_name = field_name
        self.kwargs: dict[str, Any] = {"field_name": field_name}

    def use_sort_order(self, sort_order: IndexSortOrder) -> "IndexExpressionBuilder":
        """Set the sort order for the index.

        Args:
            sort_order (IndexSortOrder): The sort order to use.

        Returns:
            IndexExpressionBuilder: The builder instance for chaining.
        """
        self.kwargs["sort_order"] = sort_order
        return self

    def use_index_type(self, index_type: IndexType) -> "IndexExpressionBuilder":
        """Set the index type for the index.

        Args:
            index_type (IndexType): The index type to use.

        Returns:
            IndexExpressionBuilder: The builder instance for chaining.
        """
        self.kwargs["index_type"] = index_type
        return self

    def use_collation(self, locale: str, strength: CollationStrength) -> "IndexExpressionBuilder":
        """Set the collation settings for the index.

        Args:
            locale (str): The locale for string comparison.
            strength (CollationStrength): The collation strength to use.

        Returns:
            IndexExpressionBuilder: The builder instance for chaining.
        """
        self.kwargs["collation_locale"] = locale
        self.kwargs["collation_strength"] = strength
        return self

    def use_partial_expression(self, expression: CollectionFilterExpression) -> "IndexExpressionBuilder":
        """Set a partial filter expression for the index.

        Args:
            expression (CollectionFilterExpression): The partial filter expression to use.

        Returns:
            IndexExpressionBuilder: The builder instance for chaining.
        """
        self.kwargs["partial_expression"] = expression
        return self

    def use_index_name(self, index_name: str) -> "IndexExpressionBuilder":
        """Set a custom name for the index.

        Args:
            index_name (str): The custom name for the index.

        Returns:
            IndexExpressionBuilder: The builder instance for chaining.
        """
        self.kwargs["index_name"] = index_name
        return self

    def use_sparse(self, is_sparse: bool = True) -> "IndexExpressionBuilder":
        """Set whether the index should be sparse.

        Args:
            is_sparse (bool): Whether the index should be sparse. Defaults to True.

        Returns:
            IndexExpressionBuilder: The builder instance for chaining.
        """
        self.kwargs["is_sparse"] = is_sparse
        return self

    def use_unique(self, is_unique: bool = True) -> "IndexExpressionBuilder":
        """Set whether the index should enforce uniqueness.

        Args:
            is_unique (bool): Whether the index should enforce uniqueness. Defaults to True.

        Returns:
            IndexExpressionBuilder: The builder instance for chaining.
        """
        self.kwargs["is_unique"] = is_unique
        return self

    def use_hidden(self, is_hidden: bool = True) -> "IndexExpressionBuilder":
        """Set whether the index should be hidden.

        Args:
            is_hidden (bool): Whether the index should be hidden. Defaults to True.

        Returns:
            IndexExpressionBuilder: The builder instance for chaining.
        """
        self.kwargs["is_hidden"] = is_hidden
        return self

    def use_ttl(self, seconds: float) -> "IndexExpressionBuilder":
        """Set the TTL (time-to-live) for the index.

        Args:
            seconds (float): The time-to-live value in seconds.

        Returns:
            IndexExpressionBuilder: The builder instance for chaining.
        """
        self.kwargs["expires_after_seconds"] = seconds
        return self

    def build_index(self) -> IndexExpression:
        """Construct the IndexExpression instance with the configured properties.

        Returns:
            IndexExpression: The constructed IndexExpression instance.
        """
        return IndexExpression(**self.kwargs)

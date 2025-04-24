from typing import Any, Iterable, get_args, get_origin, Sequence, Set

from pydantic import BaseModel
from pydongo.expressions.filter import CollectionFilterExpression
from pydongo.expressions.index import (
    IndexExpression,
    IndexSortOrder,
    IndexType,
    IndexExpressionBuilder,
)
from pydongo.utils.annotations import resolve_annotation
from pydongo.utils.serializer import HANDLER_MAPPING


class FieldExpression:
    """
    Represents a scalar field in a MongoDB query.

    This class supports operator overloading to build query expressions using:
        ==, !=, >, >=, <, <=

    It also supports nested attribute access (e.g., user.address.city).
    """

    def __init__(self, field_name: str, annotation=None, sort_ascending: bool = True):
        """
        Initialize a field expression.

        Args:
            field_name (str): The full dot-path name of the field.
            annotation (Any): The Pydantic type annotation for the field.
            sort_ascending (bool): Whether sorting on this field is ascending by default.
        """
        self._field_name = field_name
        self.annotation = annotation
        self.sort_ascending = sort_ascending

    def to_index(self) -> IndexExpression:
        """
        Returns a complete, ready-to-use `IndexExpression` for this field.

        This is a convenience method for quickly generating a basic index configuration
        using the default sort order and inferred index type (e.g., TEXT for strings).
        """

        return self.as_index().build_index()

    def as_index(self) -> IndexExpressionBuilder:
        """
        Returns an `IndexExpressionBuilder` initialized with this field.

        This allows users to customize the index further, such as adding uniqueness,
        TTL, collation, or partial filter expressions—before building the final index object.
        """

        sort_order = (
            IndexSortOrder.ASCENDING
            if self.sort_ascending
            else IndexSortOrder.DESCENDING
        )

        builder = IndexExpressionBuilder(field_name=self.field_name).use_sort_order(
            sort_order=sort_order
        )

        datatype = get_origin(self.annotation) or self.annotation

        if issubclass(datatype, str):
            return builder.use_index_type(IndexType.TEXT)

        return builder

    def _get_comparative_expression(self, operator: str, value: Any) -> dict:
        """
        Build a MongoDB filter expression using the given operator and value.

        Args:
            operator (str): MongoDB comparison operator (e.g., "$gt").
            value (Any): The value to compare against.

        Returns:
            dict: A MongoDB-compatible filter clause.
        """
        value_class = type(value)
        if value_class in HANDLER_MAPPING:
            value = HANDLER_MAPPING[value_class].serialize(value)

        return {self.field_name: {operator: value}}

    def __eq__(self, other: Any) -> "CollectionFilterExpression":  # type: ignore
        """Build an equality expression (`==`)."""
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$eq", other)
        )

    def __ne__(self, other: Any) -> "CollectionFilterExpression":  # type: ignore
        """Build an inequality expression (`!=`)."""
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$ne", other)
        )

    def __gt__(self, other: Any) -> "CollectionFilterExpression":
        """Build a greater-than expression (`>`)."""
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$gt", other)
        )

    def __ge__(self, other: Any) -> "CollectionFilterExpression":
        """Build a greater-than-or-equal expression (`>=`)."""
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$gte", other)
        )

    def __lt__(self, other: Any) -> "CollectionFilterExpression":
        """Build a less-than expression (`<`)."""
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$lt", other)
        )

    def __le__(self, other: Any) -> "CollectionFilterExpression":
        """Build a less-than-or-equal expression (`<=`)."""
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$lte", other)
        )

    def __neg__(self) -> "FieldExpression":
        """
        Flip the default sort order.

        Returns:
            FieldExpression: A new instance with reversed sort order.
        """
        return FieldExpression(
            field_name=self.field_name,
            annotation=self.annotation,
            sort_ascending=not self.sort_ascending,
        )

    @property
    def field_name(self):
        """The full field name, including nested paths if applicable."""
        return self._field_name

    def __getattr__(self, name: str) -> "FieldExpression":
        """
        Support for chained dot notation, e.g. `user.address.city`.

        Args:
            name (str): Subfield name.

        Returns:
            FieldExpression: A new field expression for the nested field.
        """
        return self._getattr(self.field_name, self.annotation, name)

    @classmethod
    def _getattr(cls, field_name: str, annotation: Any, name: str) -> "FieldExpression":
        """
        Helper to resolve nested fields.

        Args:
            field_name (str): Current field name path.
            annotation (Any): Type annotation of the current field.
            name (str): Next subfield name.

        Returns:
            FieldExpression: A new expression with nested field access.

        Raises:
            AttributeError: If the annotation is not a Pydantic model or field is invalid.
        """
        annotation = resolve_annotation(annotation=annotation)
        field_name = ".".join((field_name, name))

        if not issubclass(annotation, BaseModel):
            raise AttributeError(
                f"'{annotation.__name__}' is not an object but a scalar value"
            )
        if name not in annotation.model_fields:
            raise AttributeError(f"'{annotation.__name__}' has no field named '{name}'")

        annotation = annotation.model_fields[name].annotation
        return cls.get_field_expression(field_name, annotation)

    @staticmethod
    def get_field_expression(field_name: str, annotation: Any) -> "FieldExpression":
        dtype = get_origin(annotation) or annotation
        if isinstance(dtype, type) and issubclass(dtype, (Sequence, Set)):  # type: ignore
            return ArrayFieldExpression(field_name, annotation=annotation)
        return FieldExpression(field_name, annotation=annotation)


class ArraySizeFieldExpression(FieldExpression):
    """
    Represents an expression for the size of an array field.

    Used for queries like: `len(User.tags) > 2`
    """

    def _get_comparative_expression(self, operator: str, value: int) -> dict:
        """
        Build a MongoDB `$expr` query comparing the size of an array.

        Args:
            operator (str): Comparison operator (e.g., "$gt").
            value (int): Value to compare the array size against.

        Returns:
            dict: MongoDB `$expr` query.
        """
        return {"$expr": {operator: [{"$size": f"${self.field_name}"}, value]}}


class ArrayFieldExpression(FieldExpression):
    """
    Represents an array field in a MongoDB document.

    Adds support for array-specific operations like `.contains()`, `.size()`, and `.matches()`.
    """

    def size(self) -> ArraySizeFieldExpression:
        """
        Get an expression that targets the array's length.

        Returns:
            ArraySizeFieldExpression: An expression targeting the array's size.
        """
        return ArraySizeFieldExpression(self.field_name, self.annotation)

    def matches(
        self, values: Iterable[Any], match_order: bool = False
    ) -> CollectionFilterExpression:
        """
        Check if the array exactly matches the provided values.

        Args:
            values (Iterable[Any]): Values to match against.
            match_order (bool): If True, requires order-sensitive match.

        Returns:
            CollectionFilterExpression: MongoDB `$all` or exact match query.
        """
        if match_order:
            return CollectionFilterExpression().with_expression(
                {self.field_name: list(values)}
            )

        expression = {self.field_name: {"$all": list(values)}}
        return CollectionFilterExpression().with_expression(expression)

    def contains(self, value: Any) -> CollectionFilterExpression:
        """
        Check if the array contains one or more values.

        Args:
            value (Any): A scalar or iterable to check presence for.

        Returns:
            CollectionFilterExpression: MongoDB `$in` expression.
        """
        expression = {self.field_name: {"$in": value}}
        return CollectionFilterExpression().with_expression(expression)

    def excludes(self, value: Any) -> CollectionFilterExpression:
        """
        Check if the array excludes one or more values.

        Args:
            value (Any): A scalar or iterable to check absence for.

        Returns:
            CollectionFilterExpression: MongoDB `$nin` expression.
        """
        expression = {self.field_name: {"$nin": value}}
        return CollectionFilterExpression().with_expression(expression)

    def __getattr__(self, name: str) -> FieldExpression:
        """
        Support accessing subfields within an array of objects.

        Args:
            name (str): Name of the subfield.

        Returns:
            FieldExpression: Field expression for the nested field.

        Raises:
            TypeError: If element type can't be inferred.
        """
        args = get_args(self.annotation)
        if not args:
            raise TypeError(f"Cannot extract element type from {self.annotation}")

        element_type = args[0]
        return self._getattr(self.field_name, element_type, name)

    def __len__(self) -> ArraySizeFieldExpression:
        """
        Return an expression for the array's size (using `len()`).

        Returns:
            ArraySizeFieldExpression: Expression targeting array length.
        """
        return self.size()

    def __contains__(self, value: Any) -> CollectionFilterExpression:
        """
        Python-style containment check using `in` syntax.

        Args:
            value (Any): Element to check for.

        Returns:
            CollectionFilterExpression: MongoDB `$in` expression.
        """
        return self.contains(value=value)

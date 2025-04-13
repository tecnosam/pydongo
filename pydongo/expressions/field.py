from typing import Any, Iterable, get_args

from pydantic import BaseModel
from pydongo.expressions.filter import CollectionFilterExpression
from pydongo.utils.serializer import HANDLER_MAPPING


class FieldExpression:
    def __init__(self, field_name: str, annotation=None, sort_ascending: bool = True):
        self._field_name = field_name
        self.annotation = annotation
        self.sort_ascending = sort_ascending

    def _get_comparative_expression(self, operator: str, value: Any) -> dict:
        value_class = type(value)
        if value_class in HANDLER_MAPPING:
            value = HANDLER_MAPPING[value_class].serialize(value)

        return {self.field_name: {operator: value}}

    def __eq__(self, other: Any) -> "CollectionFilterExpression":  # type: ignore
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$eq", other)
        )

    def __ne__(self, other: Any) -> "CollectionFilterExpression":  # type: ignore
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$ne", other)
        )

    def __gt__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$gt", other)
        )

    def __ge__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$gte", other)
        )

    def __lt__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$lt", other)
        )

    def __le__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(
            self._get_comparative_expression("$lte", other)
        )

    def __neg__(self) -> "FieldExpression":
        return FieldExpression(
            field_name=self.field_name,
            annotation=self.annotation,
            sort_ascending=not self.sort_ascending,
        )

    @property
    def field_name(self):
        return self._field_name

    def __getattr__(self, name: str) -> "FieldExpression":
        return self._getattr(self.field_name, self.annotation, name)

    @staticmethod
    def _getattr(field_name: str, annotation: Any, name: str) -> "FieldExpression":
        if not issubclass(annotation, BaseModel):
            raise AttributeError(
                f"'{annotation.__name__}' is not an object but a scalar value"
            )

        if name not in annotation.model_fields:
            raise AttributeError(f"'{annotation.__name__}' has no field named '{name}'")

        field_name = ".".join((field_name, name))
        annotation = annotation.model_fields[name].annotation
        return FieldExpression(field_name=field_name, annotation=annotation)


class ArraySizeFieldExpression(FieldExpression):
    def _get_comparative_expression(self, operator: str, value: int) -> dict:
        return {"$expr": {operator: [{"$size": f"${self.field_name}"}, value]}}


class ArrayFieldExpression(FieldExpression):
    def size(self) -> ArraySizeFieldExpression:
        """
        Return a ArraySizeFieldExpression of the length of the array.
        """

        return ArraySizeFieldExpression(self.field_name, self.annotation)

    def matches(
        self, values: Iterable[Any], match_order: bool = False
    ) -> CollectionFilterExpression:
        """
        Check if the array field directly matches an array of values
        """
        if match_order:
            CollectionFilterExpression().with_expression(
                {self.field_name: list(values)}
            )

        expression = {self.field_name: {"$all": list(values)}}
        return CollectionFilterExpression().with_expression(expression)

    def contains(self, value: Any) -> CollectionFilterExpression:
        """
        Check if the array field contains `value`.
        If `value` is an iterable iterable is parsed, check if field contains any of the
         elements in `value`
        """

        expression = {self.field_name: {"$in": value}}
        return CollectionFilterExpression().with_expression(expression)

    def excludes(self, value: Any) -> CollectionFilterExpression:
        """
        Check if the array field does not contain `value`.
        If `value` is an iterable iterable is parsed, check if field does not
        contain any of the elements in `value`
        """

        expression = {self.field_name: {"$nin": value}}
        return CollectionFilterExpression().with_expression(expression)

    def __getattr__(self, name: str) -> FieldExpression:
        """
        Return a field expression to match the sub key
        """
        args = get_args(self.annotation)
        if not args:
            raise TypeError(f"Cannot extract element type from {self.annotation}")

        element_type = args[0]
        return self._getattr(self.field_name, element_type, name)

    def __len__(self) -> ArraySizeFieldExpression:
        """
        Return a ArraySizeFieldExpression of the length of the array.
        """

        return self.size()

    def __contains__(self, value: Any) -> CollectionFilterExpression:
        """
        Used to check if value is present inside an array.
        Value can be an object or an array.
        """

        return self.contains(value=value)

from typing import Any, List

from pydantic import BaseModel
from pydongo.expressions.filter import CollectionFilterExpression


class FieldExpression:
    def __init__(self, field_name: str, annotation=None, sort_ascending: bool = True):
        self._field_name = field_name
        self.annotation = annotation
        self.sort_ascending = sort_ascending

    def __eq__(self, other: Any) -> "CollectionFilterExpression":  # type: ignore
        return CollectionFilterExpression().with_expression(
            self.field_name, "$eq", other
        )

    def __ne__(self, other: Any) -> "CollectionFilterExpression":  # type: ignore
        return CollectionFilterExpression().with_expression(
            self.field_name, "$ne", other
        )

    def __gt__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(
            self.field_name, "$gt", other
        )

    def __ge__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(
            self.field_name, "$gte", other
        )

    def __lt__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(
            self.field_name, "$lt", other
        )

    def __le__(self, other: Any) -> "CollectionFilterExpression":
        return CollectionFilterExpression().with_expression(
            self.field_name, "$lte", other
        )

    def __neg__(self):
        return FieldExpression(
            field_name=self.field_name,
            annotation=self.annotation,
            sort_ascending=not self.sort_ascending,
        )

    @property
    def field_name(self):
        return self._field_name

    def __getattr__(self, name: str) -> "FieldExpression":
        if not issubclass(self.annotation, BaseModel):
            raise AttributeError(
                f"'{self.annotation.__name__}' is not an object but a scalar value"
            )

        if name not in self.annotation.model_fields:
            raise AttributeError(
                f"'{self.annotation.__name__}' has no field named '{name}'"
            )

        field_name = ".".join((self.field_name, name))
        annotation = self.annotation.model_fields[name].annotation
        return FieldExpression(field_name=field_name, annotation=annotation)


class ArrayExpression(FieldExpression):
    def __len__(self) -> FieldExpression:
        """
        Return a CollectionFilterExpression of the length of the array.
        """

    def __contains__(self, value: Any) -> CollectionFilterExpression:
        """
        Used to check if value is present inside an array.
        Value can be an object or an array.
        """

    def matches(
        self, value: List[Any], match_order: bool = False
    ) -> CollectionFilterExpression:
        """
        Check if the array field directly matches an array of values wit
        """

    def __getattr__(self, name: str) -> "FieldExpression":
        """
        Return a field expression to match the sub key
        """

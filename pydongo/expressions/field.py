from typing import Any, List
from pydongo.expressions.filter import CollectionFilterExpression


class FieldExpression:
    def __init__(self, field_name: str, field_model=None, sort_ascending: bool = True):
        self.field_name = field_name
        self.field_model = field_model
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
            field_model=self.field_model,
            sort_ascending=not self.sort_ascending,
        )


class NestedObjectExpression(FieldExpression):
    def __getattr__(self, name: str) -> "FieldExpression":
        if not self.field_model:
            raise AttributeError(
                f"'{self.field_model.__name__}' is not an object but a scalar value"
            )

        if name not in self.field_model.model_fields:
            raise AttributeError(
                f"'{self.field_model.__name__}' has no field named '{name}'"
            )
        return FieldExpression(name)


class ArrayExpression(FieldExpression):
    def __len__(self) -> FieldExpression:
        """
        Return a field expression of the length of the array.
        """
        # todo: return a modified expression that resolves to the length of the array
        return FieldExpression(self.field_name, self.field_model)

    def includes(self, value: Any) -> FieldExpression:
        """
        Used to check if value is present inside an array
        """
        # todo: return a modified expression that resolves to the $in operation
        return FieldExpression(self.field_name, self.field_model)

    def matches(self, value: List[Any], match_order: bool = False) -> FieldExpression:
        """
        Check if the array field directly matches an array of values wit
        """
        # todo: return a modified expression that resolves to the $all operation
        return FieldExpression(self.field_name, self.field_model)

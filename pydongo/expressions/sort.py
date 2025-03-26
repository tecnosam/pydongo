from pydongo.expressions.base import BaseExpression


class CollectionSortExpression(BaseExpression):
    """
    Generate a Boolean expression used to sort collection results

    """

    def serialize(self) -> dict:
        """
        Serialize a filter expression into a mongodb query
        """

        return {}

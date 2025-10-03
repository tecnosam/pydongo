"""Test filter expressions."""

from pydongo.expressions.filter import CollectionFilterExpression


def test_with_expression_merges_dict() -> None:
    """Test that with_expression merges the given dictionary into the existing expression."""
    expr = CollectionFilterExpression()
    expr.with_expression({"name": {"$eq": "Alice"}})

    assert expr.serialize() == {"name": {"$eq": "Alice"}}


def test_and_combines_two_expressions() -> None:
    """Test that the `&` operator combines two filter expressions with `$and`."""
    expr1 = CollectionFilterExpression({"name": {"$eq": "Alice"}})
    expr2 = CollectionFilterExpression({"age": {"$gt": 20}})
    combined = expr1 & expr2

    assert combined.serialize() == {"$and": [{"name": {"$eq": "Alice"}}, {"age": {"$gt": 20}}]}


def test_or_combines_two_expressions() -> None:
    """Test that the `|` operator combines two filter expressions with `$or`."""
    expr1 = CollectionFilterExpression({"name": {"$eq": "Alice"}})
    expr2 = CollectionFilterExpression({"name": {"$eq": "Bob"}})
    combined = expr1 | expr2

    assert combined.serialize() == {"$or": [{"name": {"$eq": "Alice"}}, {"name": {"$eq": "Bob"}}]}


def test_not_inverts_expression() -> None:
    """Test that the `~` operator negates the filter expression with `$not`."""
    expr = CollectionFilterExpression({"age": {"$gt": 18}})
    negated = ~expr

    assert negated.serialize() == {"$not": {"age": {"$gt": 18}}}

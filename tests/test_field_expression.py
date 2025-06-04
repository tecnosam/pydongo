"""Test field expressions."""

from pydongo.expressions.field import (
    ArrayFieldExpression,
    ArraySizeFieldExpression,
    FieldExpression,
)
from pydongo.expressions.filter import CollectionFilterExpression
from tests.resources import Friend, User


def test_comparative_operators_resolve_correct_queries() -> None:
    """Test that comparative operators resolve to the correct MongoDB queries."""
    field = FieldExpression("age")

    eq_expr = (field == 30).serialize()
    ne_expr = (field != 25).serialize()
    gt_expr = (field > 18).serialize()
    gte_expr = (field >= 21).serialize()
    lt_expr = (field < 60).serialize()
    lte_expr = (field <= 65).serialize()

    assert eq_expr == {"age": {"$eq": 30}}
    assert ne_expr == {"age": {"$ne": 25}}
    assert gt_expr == {"age": {"$gt": 18}}
    assert gte_expr == {"age": {"$gte": 21}}
    assert lt_expr == {"age": {"$lt": 60}}
    assert lte_expr == {"age": {"$lte": 65}}


def test_nested_fields() -> None:
    """Test nested fields in field expressions."""
    parent = FieldExpression("friend", annotation=Friend)
    child = parent.username
    assert isinstance(child, FieldExpression)
    assert child.field_name == "friend.username"

    user = FieldExpression("user", annotation=User)
    child = user.close_friend.username
    assert isinstance(child, FieldExpression)
    assert child.field_name == "user.close_friend.username"

    # Test field with optional tag
    user = FieldExpression("user", annotation=User)
    child = user.best_friend.username
    assert isinstance(child, FieldExpression)
    assert child.field_name == "user.best_friend.username"


def test_array_field_size_expression() -> None:
    """Test size expression on an array field."""
    tags = ArrayFieldExpression("tags", annotation=list[str])
    size_expr = tags.size() > 2
    assert isinstance(size_expr, CollectionFilterExpression)
    assert size_expr.serialize() == {"$expr": {"$gt": [{"$size": "$tags"}, 2]}}


def test_array_field_contains_and_excludes() -> None:
    """Test contains and excludes expressions on an array field."""
    tags = ArrayFieldExpression("tags", annotation=list[str])
    contains_expr = tags.contains("python")
    excludes_expr = tags.excludes("java")

    assert contains_expr.serialize() == {"tags": {"$in": "python"}}
    assert excludes_expr.serialize() == {"tags": {"$nin": "java"}}


def test_array_field_matches_with_and_without_order() -> None:
    """Test matches expressions on an array field."""
    tags = ArrayFieldExpression("tags", annotation=list[str])
    expr_ordered = tags.matches(["a", "b"], match_order=True)
    expr_unordered = tags.matches(["a", "b"], match_order=False)

    assert expr_ordered.serialize() == {"tags": ["a", "b"]}
    assert expr_unordered.serialize() == {"tags": {"$all": ["a", "b"]}}


def test_len_and_contains_sugar() -> None:
    """Test length and contains sugar syntax."""
    tags = ArrayFieldExpression("tags", annotation=list[str])
    assert isinstance(tags.size(), ArraySizeFieldExpression)

    expr = tags.contains("python")
    assert expr.serialize() == {"tags": {"$in": "python"}}

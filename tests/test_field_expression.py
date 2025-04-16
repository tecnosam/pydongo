from pydantic import BaseModel
from typing import List, Optional
from pydongo.expressions.field import (
    FieldExpression,
    ArrayFieldExpression,
    ArraySizeFieldExpression,
)
from pydongo.expressions.filter import CollectionFilterExpression


class DummyModel(BaseModel):
    name: str
    age: int
    tags: List[str]
    friends: List["Friend"]


class Friend(BaseModel):
    username: str


class User(BaseModel):
    best_friend: Optional[Friend]
    close_friend: Friend


def test_comparative_operators_resolve_correct_queries():
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


def test_nested_fields():
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


def test_array_field_size_expression():
    tags = ArrayFieldExpression("tags", annotation=List[str])
    size_expr = tags.size() > 2
    assert isinstance(size_expr, CollectionFilterExpression)
    assert size_expr.serialize() == {"$expr": {"$gt": [{"$size": "$tags"}, 2]}}


def test_array_field_contains_and_excludes():
    tags = ArrayFieldExpression("tags", annotation=List[str])
    contains_expr = tags.contains("python")
    excludes_expr = tags.excludes("java")

    assert contains_expr.serialize() == {"tags": {"$in": "python"}}
    assert excludes_expr.serialize() == {"tags": {"$nin": "java"}}


def test_array_field_matches_with_and_without_order():
    tags = ArrayFieldExpression("tags", annotation=List[str])
    expr_ordered = tags.matches(["a", "b"], match_order=True)
    expr_unordered = tags.matches(["a", "b"], match_order=False)

    assert expr_ordered.serialize() == {"tags": ["a", "b"]}
    assert expr_unordered.serialize() == {"tags": {"$all": ["a", "b"]}}


def test_len_and_contains_sugar():
    tags = ArrayFieldExpression("tags", annotation=List[str])
    assert isinstance(tags.size(), ArraySizeFieldExpression)

    expr = tags.contains("python")
    assert expr.serialize() == {"tags": {"$in": "python"}}

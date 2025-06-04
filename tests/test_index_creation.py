"""Test index creation."""

from typing import Any

import pytest

from pydongo.drivers.mock import MockMongoDBDriver
from pydongo.expressions.index import (
    CollationStrength,
    IndexExpression,
    IndexExpressionBuilder,
    IndexSortOrder,
    IndexType,
)
from pydongo.workers.collection import CollectionWorker


def _assert_index_registered(collection: CollectionWorker, driver: MockMongoDBDriver, expected_count: int) -> None:
    """Assert that the index is registered in the collection and driver."""
    assert len(collection._indexes) == expected_count, ("Index should be registered in collection")
    assert len(driver.indexes[collection.collection_name]) == expected_count, ("Driver should contain the index")
    assert all(isinstance(ix, IndexExpression) for index in collection._indexes for ix in index)


def test_single_key_index(setup: tuple[CollectionWorker[Any], MockMongoDBDriver]) -> None:
    """Test creation of a single key index."""
    collection, driver = setup
    index = collection.name.as_index().use_unique().build_index()

    assert isinstance(index, IndexExpression)
    collection.use_index(index)
    collection.find().count()

    _assert_index_registered(collection, driver, 1)


def test_compound_index(setup: tuple[CollectionWorker[Any], MockMongoDBDriver]) -> None:
    """Test creation of a compound index with multiple fields."""
    collection, driver = setup

    index1 = (
        collection.name.as_index()
        .use_sort_order(IndexSortOrder.ASCENDING)
        .build_index()
    )
    index2 = (
        collection.email.as_index()
        .use_sort_order(IndexSortOrder.DESCENDING)
        .build_index()
    )

    assert isinstance(index1, IndexExpression)
    assert isinstance(index2, IndexExpression)

    collection.use_index((index1, index2))
    collection.find().count()

    _assert_index_registered(collection, driver, 1)

    compound = next(iter(driver.indexes[collection.collection_name]))
    assert len(compound) == 2


def test_text_and_hash_index(setup: tuple[CollectionWorker[Any], MockMongoDBDriver],) -> None:
    """Test creation of text and hash indexes."""
    collection, driver = setup

    text_index = collection.bio.as_index().use_index_type(IndexType.TEXT).build_index()
    hash_index = (
        collection.hash_id.as_index().use_index_type(IndexType.HASHED).build_index()
    )

    assert isinstance(text_index, IndexExpression)
    assert isinstance(hash_index, IndexExpression)

    collection.use_index(text_index)
    collection.use_index(hash_index)
    collection.find().count()

    _assert_index_registered(collection, driver, 2)

    index_types = [
        ix[0].index_type for ix in driver.indexes[collection.collection_name]
    ]
    assert IndexType.TEXT in index_types
    assert IndexType.HASHED in index_types


def test_geo_index_types(setup: tuple[CollectionWorker[Any], MockMongoDBDriver]) -> None:
    """Test creation of 2D and 2D Sphere geo indexes."""
    collection, driver = setup

    index_2d = (
        collection.latlon.as_index()
        .use_index_type(IndexType.TWO_DIMENSIONAL)
        .build_index()
    )
    index_2dsphere = (
        collection.point.as_index()
        .use_index_type(IndexType.TWO_DIMENSIONAL_SPHERE)
        .build_index()
    )

    assert isinstance(index_2d, IndexExpression)
    assert isinstance(index_2dsphere, IndexExpression)

    collection.use_index(index_2d)
    collection.use_index(index_2dsphere)
    collection.find().count()

    _assert_index_registered(collection, driver, 2)

    index_types = [
        ix[0].index_type for ix in driver.indexes[collection.collection_name]
    ]
    assert IndexType.TWO_DIMENSIONAL in index_types
    assert IndexType.TWO_DIMENSIONAL_SPHERE in index_types


def test_index_with_special_kwargs(setup: tuple[CollectionWorker[Any], MockMongoDBDriver]) -> None:
    """Test creation of an index with special kwargs like unique, sparse, and collation."""
    collection, driver = setup

    index = (
        collection.email.as_index()
        .use_unique()
        .use_sparse()
        .use_index_name("email_index")
        .use_ttl(3600)
        .use_collation(locale="en", strength=CollationStrength.SECONDARY)
        .build_index()
    )

    assert isinstance(index, IndexExpression)
    collection.use_index(index)
    collection.find().count()

    _assert_index_registered(collection, driver, 1)

    created = driver.indexes[collection.collection_name][0][0]
    kwargs = created.build_kwargs()

    assert kwargs.get("unique") is True
    assert kwargs.get("sparse") is True
    assert kwargs.get("expireAfterSeconds") is None, "TTL for text should be NULL"
    assert kwargs.get("collation") == {"locale": "en", "strength": 2}


@pytest.mark.parametrize(
    ("index_type", "expect_ttl"),
    [
        (IndexType.TEXT, False),
        (IndexType.HASHED, False),
        (IndexType.TWO_DIMENSIONAL, True),
        (IndexType.TWO_DIMENSIONAL_SPHERE, True),
        (None, True),  # regular ascending/descending index
    ],
)
def test_ttl_behavior_for_text_and_other_index_types(index_type: IndexType, expect_ttl: bool) -> None:
    """Test TTL behavior for different index types."""
    builder = IndexExpressionBuilder(field_name="test_field").use_ttl(3600)

    if index_type:
        builder.use_index_type(index_type)

    index: IndexExpression = builder.build_index()
    kwargs = index.build_kwargs()

    if expect_ttl:
        assert "expireAfterSeconds" in kwargs
        assert kwargs["expireAfterSeconds"] == 3600
    else:
        assert "expireAfterSeconds" not in kwargs

import pytest
import pytest_asyncio
from typing import List
from pydantic import BaseModel, Field
from pydongo import as_collection
from pydongo.expressions.index import (
    IndexSortOrder,
    IndexType,
    CollationStrength,
    IndexExpression,
)
from pydongo.drivers.mock import MockAsyncMongoDBDriver


class DemoModel(BaseModel):
    name: str
    email: str
    bio: str
    hash_id: str
    latlon: List[float] = Field(default_factory=lambda: [0.0, 0.0])
    point: dict = Field(
        default_factory=lambda: {"type": "Point", "coordinates": [0.0, 0.0]}
    )


def _assert_index_registered(collection, driver, expected_count):
    assert len(collection._indexes) == expected_count, (
        "Index should be registered in collection"
    )
    assert len(driver.indexes[collection.collection_name]) == expected_count, (
        "Driver should contain the index"
    )
    assert all(
        isinstance(ix, IndexExpression) for index in collection._indexes for ix in index
    )


@pytest_asyncio.fixture
async def setup_async_collection():
    driver = MockAsyncMongoDBDriver()
    await driver.connect()
    collection = as_collection(DemoModel, driver)
    return collection, driver


@pytest.mark.asyncio
async def test_single_key_index_async(setup_async_collection):
    collection, driver = setup_async_collection
    index = collection.name.as_index().use_unique().build_index()

    assert isinstance(index, IndexExpression)
    collection.use_index(index)
    await collection.find().count()

    _assert_index_registered(collection, driver, 1)


@pytest.mark.asyncio
async def test_compound_index_async(setup_async_collection):
    collection, driver = setup_async_collection
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
    await collection.find().count()

    _assert_index_registered(collection, driver, 1)

    compound = next(iter(driver.indexes[collection.collection_name]))
    assert len(compound) == 2


@pytest.mark.asyncio
async def test_text_and_hash_index_async(setup_async_collection):
    collection, driver = setup_async_collection
    text_index = collection.bio.as_index().use_index_type(IndexType.TEXT).build_index()
    hash_index = (
        collection.hash_id.as_index().use_index_type(IndexType.HASHED).build_index()
    )

    assert isinstance(text_index, IndexExpression)
    assert isinstance(hash_index, IndexExpression)

    collection.use_index(text_index)
    collection.use_index(hash_index)
    await collection.find().count()

    _assert_index_registered(collection, driver, 2)

    index_types = [
        ix[0].index_type for ix in driver.indexes[collection.collection_name]
    ]
    assert IndexType.TEXT in index_types
    assert IndexType.HASHED in index_types


@pytest.mark.asyncio
async def test_geo_index_types_async(setup_async_collection):
    collection, driver = setup_async_collection
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
    await collection.find().count()

    _assert_index_registered(collection, driver, 2)

    index_types = [
        ix[0].index_type for ix in driver.indexes[collection.collection_name]
    ]
    assert IndexType.TWO_DIMENSIONAL in index_types
    assert IndexType.TWO_DIMENSIONAL_SPHERE in index_types


@pytest.mark.asyncio
async def test_index_with_special_kwargs_async(setup_async_collection):
    collection, driver = setup_async_collection
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
    await collection.find().count()

    _assert_index_registered(collection, driver, 1)

    created = driver.indexes[collection.collection_name][0][0]
    kwargs = created.build_kwargs()
    assert kwargs.get("unique") is True
    assert kwargs.get("sparse") is True
    assert kwargs.get("expireAfterSeconds") is None
    assert kwargs.get("collation") == {"locale": "en", "strength": 2}

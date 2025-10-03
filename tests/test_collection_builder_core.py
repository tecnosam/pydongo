"""Test collection builder core functionality."""

from pydongo.drivers.mock import MockMongoDBDriver
from pydongo.workers.collection import as_collection
from tests.resources import User


def test_collection_builder_sort_limit_skip_multi_sort(driver: MockMongoDBDriver) -> None:
    """Test sorting, limiting, and skipping functionality."""
    driver.connect()

    collection = as_collection(User, driver)

    # 1. Ascending sort
    q1 = collection.find().sort(collection.age)
    kwargs1 = q1.build_kwargs()
    assert kwargs1["sort_criteria"] == {"age": 1}

    # 2. Descending sort using -field
    q2 = collection.find().sort(-collection.name)
    kwargs2 = q2.build_kwargs()
    assert kwargs2["sort_criteria"] == {"name": -1}

    # 3. Multi-field sort
    q3 = collection.find().sort([collection.age, -collection.joined])
    kwargs3 = q3.build_kwargs()
    assert kwargs3["sort_criteria"] == {"age": 1, "joined": -1}

    # 4. Sort + skip + limit together
    q4 = collection.find(collection.age > 21).sort(collection.name).limit(10).skip(3)
    kwargs4 = q4.build_kwargs()

    assert kwargs4["query"] == {"age": {"$gt": 21}}
    assert kwargs4["sort_criteria"] == {"name": 1}
    assert kwargs4["limit"] == 10
    assert kwargs4["offset"] == 3


def test_collection_builder_null_state_defaults(driver: MockMongoDBDriver) -> None:
    """Test that the collection builder defaults to no filters, sorts, limits, or skips."""
    driver.connect()

    collection = as_collection(User, driver)
    query = collection.find()

    kwargs = query.build_kwargs()

    assert kwargs["query"] == {}  # no filter
    assert kwargs["sort_criteria"] == {}  # no sort
    assert kwargs.get("limit") is None  # no limit
    assert kwargs.get("offset") is None  # no skip

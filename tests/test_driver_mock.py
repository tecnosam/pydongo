# tests/test_driver_mock.py

from pydongo.drivers.mock import MockMongoDBDriver


def test_insert_and_find_one():
    driver = MockMongoDBDriver()
    driver.connect()

    data = {"name": "Alice", "age": 30}
    result = driver.insert_one("users", data)

    assert "inserted_id" in result

    found = driver.find_one("users", {"name": "Alice"})
    assert found is not None
    assert found["age"] == 30


def test_update_and_delete():
    driver = MockMongoDBDriver()
    driver.connect()

    driver.insert_one("users", {"name": "Bob", "age": 25})
    driver.update_one("users", {"name": "Bob"}, {"$set": {"age": 26}})
    updated = driver.find_one("users", {"name": "Bob"})

    assert updated["age"] == 26

    deleted = driver.delete_one("users", {"name": "Bob"})
    assert deleted["deleted_count"] == 1

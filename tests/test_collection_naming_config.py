"""Test collection naming configuration."""


from src.pydongo.drivers.mock import MockMongoDBDriver
from src.pydongo.workers.collection import as_collection
from src.pydongo.workers.document import as_document
from tests.resources import User
from tests.resources import UserWithModelConfig


def test_default_collection_name_set_correctly(driver: MockMongoDBDriver) -> None:
    """Test that the default collection name is set correctly for a Pydantic model."""
    expected_collection_name = "users"

    collection = as_collection(User, driver)
    assert collection.collection_name == expected_collection_name

    document = as_document(User(), driver)
    assert document.collection_name == expected_collection_name


def test_configured_collection_name_set_correctly(driver: MockMongoDBDriver) -> None:
    """Test that the collection name set in the model config is used correctly."""
    expected_collection_name = "customusers"
    collection = as_collection(UserWithModelConfig, driver)
    assert collection.collection_name == expected_collection_name

    document = as_document(UserWithModelConfig(), driver)
    assert document.collection_name == expected_collection_name


def test_custom_collection_name_set_correctly(driver: MockMongoDBDriver) -> None:
    """Test that a custom collection name can be set correctly."""
    collection_name = "myusers"

    collection = as_collection(User, driver=driver, collection_name=collection_name)
    assert collection.collection_name == collection_name
    collection = as_collection(
        UserWithModelConfig, driver=driver, collection_name=collection_name
    )
    assert collection.collection_name == collection_name

    document = as_document(User(), driver=driver, collection_name=collection_name)
    assert document.collection_name == collection_name
    document = as_document(
        UserWithModelConfig(), driver=driver, collection_name=collection_name
    )
    assert document.collection_name == collection_name

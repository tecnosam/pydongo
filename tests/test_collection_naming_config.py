from pydantic import BaseModel, ConfigDict
from pydongo import as_collection, as_document
from pydongo.drivers.mock import MockMongoDBDriver


class UserWithModelConfig(BaseModel):

    age: int = 19
    n_likes: int = 0

    model_config = ConfigDict(collection_name="customusers")


class User(BaseModel):

    age: int = 19
    n_likes: int = 0


def test_default_collection_name_set_correctly(driver):

    expected_collection_name = "users"

    collection = as_collection(User, driver)
    assert collection.collection_name == expected_collection_name

    document = as_document(User(), driver)
    assert document.collection_name == expected_collection_name


def test_configured_collection_name_set_correctly(driver):

    expected_collection_name = "customusers"
    collection = as_collection(UserWithModelConfig, driver)
    assert collection.collection_name == expected_collection_name

    document = as_document(UserWithModelConfig(), driver)
    assert document.collection_name == expected_collection_name


def test_custom_collection_name_set_correctly(driver):

    collection_name = "myusers"

    collection = as_collection(User, driver=driver, collection_name=collection_name)
    assert collection.collection_name == collection_name
    collection = as_collection(UserWithModelConfig, driver=driver, collection_name=collection_name)
    assert collection.collection_name == collection_name

    document = as_document(User(), driver=driver, collection_name=collection_name)
    assert document.collection_name == collection_name
    document = as_document(UserWithModelConfig(), driver=driver, collection_name=collection_name)
    assert document.collection_name == collection_name

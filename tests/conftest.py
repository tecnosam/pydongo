import pytest
from pydongo.drivers.mock import MockMongoDBDriver, MockAsyncMongoDBDriver


@pytest.fixture
def driver():
    return MockMongoDBDriver()


@pytest.fixture
def async_driver():
    return MockAsyncMongoDBDriver()

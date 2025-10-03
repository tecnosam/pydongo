"""."""

import datetime
from typing import Any

import pytest
import pytest_asyncio

from src.pydongo import as_collection
from src.pydongo.drivers.mock import MockAsyncMongoDBDriver
from src.pydongo.drivers.mock import MockMongoDBDriver
from src.pydongo.workers.collection import CollectionWorker
from tests.resources import AsyncDemoModel
from tests.resources import DemoModel


@pytest.fixture
def driver() -> MockMongoDBDriver:
    """Synchronous MongoDB driver for tests."""
    return MockMongoDBDriver()


@pytest.fixture
def async_driver() -> MockAsyncMongoDBDriver:
    """Asynchronous MongoDB driver for tests."""
    return MockAsyncMongoDBDriver()


@pytest.fixture
def current_date() -> datetime.date:
    """Fixture to provide the current date."""
    return datetime.datetime.now(tz=datetime.timezone.utc).date()


@pytest.fixture
def setup(driver: MockMongoDBDriver) -> tuple["CollectionWorker", MockMongoDBDriver]:
    """Fixture to set up the database and collection."""
    driver.connect()
    collection = as_collection(DemoModel, driver)
    return collection, driver


@pytest_asyncio.fixture
async def setup_async_collection(
    async_driver: MockAsyncMongoDBDriver,
) -> tuple[CollectionWorker[Any], MockAsyncMongoDBDriver]:
    """."""
    # driver = MockAsyncMongoDBDriver()
    await async_driver.connect()
    collection = as_collection(AsyncDemoModel, async_driver)
    return collection, async_driver

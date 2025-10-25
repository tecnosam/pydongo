"""pydongo."""

import importlib.metadata

__version__ = importlib.metadata.version("pydongo")


from pydongo.drivers.async_mongo import PyMongoAsyncDriver
from pydongo.drivers.motor import MotorMongoDBDriver
from pydongo.drivers.sync_mongo import PyMongoDriver
from pydongo.workers.collection import CollectionWorker, as_collection
from pydongo.workers.document import AsyncDocumentWorker, DocumentWorker, as_document

__all__ = [
    "AsyncDocumentWorker",
    "CollectionWorker",
    "DocumentWorker",
    "MotorMongoDBDriver",
    "PyMongoAsyncDriver",
    "PyMongoDriver",
    "__version__",
    "as_collection",
    "as_document",
]

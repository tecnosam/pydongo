"""pydongo."""

import importlib.metadata

__version__ = importlib.metadata.version("pydongo")


from pydongo.drivers.async_mongo import AsyncDefaultMongoDBDriver
from pydongo.drivers.sync_mongo import DefaultMongoDBDriver
from pydongo.workers.collection import CollectionWorker
from pydongo.workers.collection import as_collection
from pydongo.workers.document import AsyncDocumentWorker
from pydongo.workers.document import DocumentWorker
from pydongo.workers.document import as_document

__all__ = [
    "AsyncDefaultMongoDBDriver",
    "AsyncDocumentWorker",
    "CollectionWorker",
    "DefaultMongoDBDriver",
    "DocumentWorker",
    "__version__",
    "as_collection",
    "as_document",
]

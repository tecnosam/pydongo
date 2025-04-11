import uuid
from typing import List, Dict, Any, Optional
from copy import deepcopy

from pydongo.drivers.base import AbstractSyncMongoDBDriver, AbstractAsyncMongoDBDriver


class MockMongoDBDriver(AbstractSyncMongoDBDriver):
    """
    In-memory mock implementation of AbstractMongoDBDriver for testing.
    """

    def __init__(self, connection_string: str = "", database_name: str = "mockdb"):
        super().__init__(connection_string, database_name)
        self._collections: Dict[str, List[Dict[str, Any]]] = {}

    def connect(self) -> bool:
        return True  # nothing to connect to

    def close(self) -> None:
        pass  # nothing to close

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        document = deepcopy(document)
        document["_id"] = str(uuid.uuid4())
        self._collections.setdefault(collection, []).append(document)
        return {"inserted_id": document["_id"]}

    def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        inserted_ids = []
        for doc in documents:
            inserted = self.insert_one(collection, doc)
            inserted_ids.append(inserted["inserted_id"])
        return {"inserted_ids": inserted_ids}

    def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        for doc in self._collections.get(collection, []):
            if all(doc.get(k) == v for k, v in query.items()):
                return deepcopy(doc)
        return None

    def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, Any],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        result = [
            deepcopy(doc)
            for doc in self._collections.get(collection, [])
            if all(doc.get(k) == v for k, v in query.items())
        ]
        return result[offset:limit] if limit else result

    def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Dict[str, Any]:
        for doc in self._collections.get(collection, []):
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update.get("$set", {}))
                return {"matched_count": 1, "modified_count": 1, "upserted_id": None}
        return {"matched_count": 0, "modified_count": 0, "upserted_id": None}

    def delete_one(self, collection: str, query: Dict[str, Any]) -> Dict[str, Any]:
        docs = self._collections.get(collection, [])
        for i, doc in enumerate(docs):
            if all(doc.get(k) == v for k, v in query.items()):
                del docs[i]
                return {"deleted_count": 1}
        return {"deleted_count": 0}

    def count(self, collection: str, query: Dict[str, Any]) -> int:
        """
        Count how many records match the specified query.
        """
        return sum(
            1
            for doc in self._collections.get(collection, [])
            if all(doc.get(k) == v for k, v in query.items())
        )

    def exists(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Check if at least one document exists that matches the query.
        """
        return any(
            all(doc.get(k) == v for k, v in query.items())
            for doc in self._collections.get(collection, [])
        )


class MockAsyncMongoDBDriver(AbstractAsyncMongoDBDriver):
    """
    In-memory mock implementation of AbstractAsyncMongoDBDriver for async tests.
    """

    def __init__(self, connection_string: str = "", database_name: str = "mockdb"):
        super().__init__(connection_string, database_name)
        self._collections: Dict[str, List[Dict[str, Any]]] = {}

    async def connect(self) -> bool:
        return True

    async def close(self) -> None:
        pass

    async def insert_one(
        self, collection: str, document: Dict[str, Any]
    ) -> Dict[str, Any]:
        document = deepcopy(document)
        document["_id"] = str(uuid.uuid4())
        self._collections.setdefault(collection, []).append(document)
        return {"inserted_id": document["_id"]}

    async def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        inserted_ids = []
        for doc in documents:
            inserted = await self.insert_one(collection, doc)
            inserted_ids.append(inserted["inserted_id"])
        return {"inserted_ids": inserted_ids}

    async def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        for doc in self._collections.get(collection, []):
            if all(doc.get(k) == v for k, v in query.items()):
                return deepcopy(doc)
        return None

    async def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, Any],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        result = [
            deepcopy(doc)
            for doc in self._collections.get(collection, [])
            if all(doc.get(k) == v for k, v in query.items())
        ]
        return result[offset:limit] if limit else result

    async def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Dict[str, Any]:
        for doc in self._collections.get(collection, []):
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update.get("$set", {}))
                return {"matched_count": 1, "modified_count": 1, "upserted_id": None}
        return {"matched_count": 0, "modified_count": 0, "upserted_id": None}

    async def delete_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Dict[str, Any]:
        docs = self._collections.get(collection, [])
        for i, doc in enumerate(docs):
            if all(doc.get(k) == v for k, v in query.items()):
                del docs[i]
                return {"deleted_count": 1}
        return {"deleted_count": 0}

    async def count(self, collection: str, query: Dict[str, Any]) -> int:
        """
        Count how many records match the specified query.
        """
        return sum(
            1
            for doc in self._collections.get(collection, [])
            if all(doc.get(k) == v for k, v in query.items())
        )

    async def exists(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Check if at least one document exists that matches the query.
        """
        return any(
            all(doc.get(k) == v for k, v in query.items())
            for doc in self._collections.get(collection, [])
        )

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Optional, Iterable

from pydongo.drivers.base import AbstractAsyncMongoDBDriver


class AsyncDefaultMongoDBDriver(AbstractAsyncMongoDBDriver):
    """
    Default asynchronous MongoDB driver using Motor (async wrapper for PyMongo).
    """

    def __init__(self, connection_string: str, database_name: str):
        super().__init__(connection_string, database_name)
        self.client: Optional[AsyncIOMotorClient] = None

    async def connect(self) -> bool:
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            return True
        except PyMongoError as e:
            raise RuntimeError(f"Failed to connect to MongoDB: {e}")

    async def close(self) -> None:
        if self.client:
            self.client.close()

    async def insert_one(
        self, collection: str, document: Dict[str, Any]
    ) -> Dict[str, Any]:
        result = await self.db[collection].insert_one(document)
        return {"inserted_id": str(result.inserted_id)}

    async def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        result = await self.db[collection].insert_many(documents)
        return {"inserted_ids": [str(_id) for _id in result.inserted_ids]}

    async def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        return await self.db[collection].find_one(query)

    async def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        sort_criteria: Dict[str, Any],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Iterable[Dict[str, Any]]:
        cursor = self.db[collection].find(query)

        if sort_criteria:
            cursor = cursor.sort([(k, v) for k, v in sort_criteria.items()])

        if offset:
            cursor = cursor.skip(offset)

        if limit:
            cursor = cursor.limit(limit)

        return cursor  # type: ignore

    async def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> Dict[str, Any]:
        result = await self.db[collection].update_one(query, update, upsert=upsert)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }

    async def delete_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Dict[str, Any]:
        result = await self.db[collection].delete_one(query)
        return {"deleted_count": result.deleted_count}

    async def count(self, collection: str, query: Dict[str, Any]) -> int:
        return await self.db[collection].count_documents(query)

    async def exists(self, collection: str, query: Dict[str, Any]) -> bool:
        return await self.db[collection].count_documents(query, limit=1) > 0

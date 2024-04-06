from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from src.database.collection import Collection
from src.entities.config import Config

DB = "LemonTCG"

class Database():
    _instance = None

    def __init__(self) -> None:
        if Database._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of Database.")
        config = Config.load_state()
        self.client = AsyncIOMotorClient(config.db_url)
        self.db = self.client[DB]

    @staticmethod
    def get_instance() -> 'Database':
        if Database._instance is None:
            Database._instance = Database()
        return Database._instance
    
    async def find_one(self, collection: Collection, **kwargs) -> Optional[dict]:
        if not isinstance(collection, Collection) or collection == Collection.NONE:
            raise RuntimeError(f"Database method find_one received an invalid collection")
        response = await self.db[collection.value].find_one(filter=kwargs)
        if isinstance(response, dict):
            response["id"] = str(response.pop("_id"))
        return response
    
    async def find_all(self, collection: Collection, **kwargs) -> list[dict]:
        if not isinstance(collection, Collection) or collection == Collection.NONE:
            raise RuntimeError(f"Database method find_all received an invalid collection")
        cursor = self.db[collection.value].find(filter=kwargs)
        results = []
        async for document in cursor:
            if isinstance(document, dict):
                document['id'] = str(document.pop("_id"))
            results.append(document)
        return results
    
    async def save(self, collection: Collection, document: dict, unique_keys: list[str] = []) -> None:
        if not isinstance(collection, Collection) or collection == Collection.NONE:
            raise RuntimeError(f"Database method save received an invalid collection")
        id = document.pop("id")
        if isinstance(id, str):
            # Update entry
            await self.db[collection.value].replace_one({"_id": ObjectId(id)}, document)
        else:
            # Insert new entry & check for unique keys
            for key in unique_keys:
                value = document.get(key, None)
                result = await self.find_one(collection=collection, **{key: value})
                if isinstance(result, dict):
                    raise RuntimeError(f"Key '{key}' is a unique key, but entry with value '{value}' already exists.")
            await self.db[collection.value].insert_one(document)

    async def delete(self, collection: Collection, document_id: str) -> None:
        if not isinstance(collection, Collection) or collection == Collection.NONE:
            raise RuntimeError(f"Database method delete received an invalid collection")
        await self.db[collection.value].delete_one({"_id": ObjectId(document_id)})
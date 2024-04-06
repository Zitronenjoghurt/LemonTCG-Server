from pydantic import BaseModel
from typing import ClassVar, Optional
from src.database.collection import Collection
from src.database.database import Database

DB = Database.get_instance()

class DatabaseEntity(BaseModel):
    COLLECTION: ClassVar[Collection] = Collection.NONE
    UNIQUE_FIELDS: ClassVar[list[str]] = []
    id: Optional[str] = None

    @classmethod
    async def find_one(cls, **kwargs):
        result = await DB.find_one(collection=cls.COLLECTION, **kwargs)
        if isinstance(result, dict):
            return cls.model_validate(result)
        
    @classmethod
    async def find_all(cls, **kwargs):
        result = await DB.find_all(collection=cls.COLLECTION, **kwargs)
        entities = []
        for data in result:
            entity = cls.model_validate(data)
            entities.append(entity)
        return entities
    
    async def save(self) -> None:
        document = self.model_dump()
        await DB.save(collection=self.COLLECTION, document=document, unique_keys=self.UNIQUE_FIELDS)

    async def delete(self) -> None:
        if not isinstance(self.id, str):
            return
        await DB.delete(collection=self.COLLECTION, document_id=self.id)
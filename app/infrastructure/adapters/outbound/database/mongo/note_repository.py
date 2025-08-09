from typing import List, Optional, Any
from uuid import UUID
from domain.models.entities.note import Note
from domain.ports.outbound.database.base_repository_port import BaseRepositoryPort
from domain.ports.outbound.logger.logger_port import LoggerPort
from infrastructure.adapters.outbound.cache.redis_adapter import AsyncRedisCacheRepository
from datetime import datetime
from domain.exceptions import DatabaseException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import Binary, UUID_SUBTYPE
from bson.binary import Binary as BsonBinary

class AsyncMongoNoteRepository(BaseRepositoryPort[Note]):
    def __init__(self, collection: Any, cache: AsyncRedisCacheRepository, logger: LoggerPort):
        self.collection = collection
        self.cache = cache
        self.logger = logger.bind(component="AsyncMongoNoteRepository")

    async def list(self, user_id: Optional[UUID], skip: int, limit: int, request_id: str) -> List[Note]:
        try:
            query = {"owner_id": Binary(user_id.bytes, UUID_SUBTYPE)} if user_id else {}
            self.logger.debug(f"Listing notes with query={query}, skip={skip}, limit={limit}", request_id=request_id)
            cursor = self.collection.find(query).skip(skip).limit(limit)
            notes = []
            async for doc in cursor:
                note = self._to_entity(doc)
                notes.append(note)
            self.logger.debug(f"Found {len(notes)} notes", request_id=request_id)
            return notes
        except Exception as e:
            self.logger.error("Database error in list", error=str(e), request_id=request_id)
            raise DatabaseException(f"Failed to list notes: {e}")

    async def create(self, entity: Note, request_id: str) -> Note:
        try:
            doc = self._to_document(entity)
            await self.collection.insert_one(doc)
            self.logger.debug(f"Note created with id={entity.id}", request_id=request_id)
            return entity
        except Exception as e:
            self.logger.error("Database error in create", error=str(e), request_id=request_id)
            raise DatabaseException(f"Failed to create note: {e}")

    async def get_by_id(self, entity_id: UUID, request_id: str) -> Optional[Note]:
        try:
            cache_key = f"note:{entity_id}"
            cached = await self.cache.get(cache_key)
            if cached:
                self.logger.debug("Cache hit for note", entity_id=str(entity_id), request_id=request_id)
                return Note(**cached)

            doc = await self.collection.find_one({"id": Binary(entity_id.bytes, UUID_SUBTYPE)})
            if doc:
                note = self._to_entity(doc)
                await self.cache.set(cache_key, note.__dict__, ttl=3600)
                self.logger.debug(f"Note fetched from DB with id={entity_id}", request_id=request_id)
                return note
            self.logger.debug(f"Note not found with id={entity_id}", request_id=request_id)
            return None
        except Exception as e:
            self.logger.error("Database error in get_by_id", error=str(e), request_id=request_id)
            raise DatabaseException(f"Failed to get note: {e}")

    async def update(self, entity: Note, request_id: str) -> Note:
        try:
            entity.updated_at = datetime.utcnow()
            cache_key = f"note:{entity.id}"
            doc = self._to_document(entity)
            await self.collection.replace_one({"id": Binary(entity.id.bytes, UUID_SUBTYPE)}, doc)
            await self.cache.set(cache_key, entity.__dict__, ttl=3600)
            self.logger.debug(f"Note updated with id={entity.id}", request_id=request_id)
            return entity
        except Exception as e:
            self.logger.error("Database error in update", error=str(e), request_id=request_id)
            raise DatabaseException(f"Failed to update note: {e}")

    async def delete(self, entity_id: UUID, request_id: str) -> None:
        try:
            cache_key = f"note:{entity_id}"
            await self.collection.delete_one({"id": Binary(entity_id.bytes, UUID_SUBTYPE)})
            await self.cache.delete(cache_key)
            self.logger.debug(f"Note deleted with id={entity_id}", request_id=request_id)
        except Exception as e:
            self.logger.error("Database error in delete", error=str(e), request_id=request_id)
            raise DatabaseException(f"Failed to delete note: {e}")

    async def count_by_user_id(self, user_id: UUID, request_id: str) -> int:
        try:
            count = await self.collection.count_documents({"owner_id": Binary(user_id.bytes, UUID_SUBTYPE)})
            self.logger.debug(f"Counted {count} notes for user_id={user_id}", request_id=request_id)
            return count
        except Exception as e:
            self.logger.error("Database error in count_by_user_id", error=str(e), request_id=request_id)
            raise DatabaseException(f"Failed to count notes: {e}")

    def _to_entity(self, doc: dict) -> Note:
        # Handle both UUID and Binary objects for id and owner_id
        note_id = doc["id"] if isinstance(doc["id"], UUID) else UUID(bytes=doc["id"].as_uuid().bytes)
        owner_id = doc["owner_id"] if isinstance(doc["owner_id"], UUID) else UUID(bytes=doc["owner_id"].as_uuid().bytes)
        return Note(
            id=note_id,
            title=doc["title"],
            content=doc["content"],
            owner_id=owner_id,
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    def _to_document(self, entity: Note) -> dict:
        return {
            "id": Binary(entity.id.bytes, UUID_SUBTYPE),
            "title": entity.title,
            "content": entity.content,
            "owner_id": Binary(entity.owner_id.bytes, UUID_SUBTYPE),
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }
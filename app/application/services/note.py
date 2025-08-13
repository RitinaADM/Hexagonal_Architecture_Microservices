from domain.exceptions import AccessDeniedError, NotFoundError, ValidationException
from domain.ports.outbound.event.event_publisher import EventPublisherPort
from domain.models.entities.note import Note
from application.dto.note import (
    NoteCreateDTO, NoteGetDTO, NoteListDTO,
    NoteUpdateDTO, NoteDeleteDTO, NoteResponseDTO, NoteListResponseDTO
)
from domain import exceptions
from application.services.base import BaseService
from uuid import uuid4, UUID
from datetime import datetime
from infrastructure.config import settings

class AsyncNoteService(BaseService[
    NoteCreateDTO,
    NoteGetDTO,
    NoteListDTO,
    NoteUpdateDTO,
    NoteDeleteDTO,
    NoteResponseDTO,
    Note
]):
    def __init__(self, repo, logger, event_publisher: EventPublisherPort):
        super().__init__(repo, logger, "Note")
        self.publisher = event_publisher

    def _create_entity(self, create_dto: NoteCreateDTO, user_id: UUID) -> Note:
        now = datetime.utcnow()
        return Note(
            id=uuid4(),
            title=create_dto.title,
            content=create_dto.content,
            owner_id=user_id,
            created_at=now,
            updated_at=now
        )

    def _update_entity(self, entity: Note, update_dto: NoteUpdateDTO) -> None:
        entity.title = update_dto.title
        entity.content = update_dto.content

    def _to_response_dto(self, entity: Note) -> NoteResponseDTO:
        return NoteResponseDTO.from_entity(entity)

    async def create(self, create_dto: NoteCreateDTO, user_id: UUID, role: str, request_id: str) -> NoteResponseDTO:
        logger = self.logger.bind(request_id=request_id, user_id=str(user_id), role=role)
        try:
            logger.info("Starting Note creation process")
            if role != "user":
                logger.error("Invalid role provided")
                raise exceptions.AuthenticationError(f"Invalid role: {role}")

            current_count = await self.repo.count_by_user_id(user_id, request_id)
            if current_count >= settings.max_docs_per_user:
                logger.error(f"Note limit exceeded for user", user_id=str(user_id))
                raise exceptions.LimitExceededError(self.entity_name, settings.max_docs_per_user)

            entity = self._create_entity(create_dto, user_id)
            created_entity = await self.repo.create(entity, request_id)
            response = self._to_response_dto(created_entity)
            logger.info(f"Note created successfully", entity_id=str(created_entity.id))

            await self.publisher.publish("note.created", {
                "id": str(created_entity.id),
                "title": created_entity.title,
                "owner_id": str(created_entity.owner_id),
                "created_at": created_entity.created_at.isoformat()
            })

            return response
        except Exception as e:
            logger.exception(f"Failed to create Note", error=str(e))
            raise

    async def get(self, get_dto: NoteGetDTO, user_id: UUID, role: str, request_id: str) -> NoteResponseDTO:
        logger = self.logger.bind(request_id=request_id, entity_id=str(get_dto.id), user_id=str(user_id), role=role)
        try:
            logger.info("Fetching Note")
            entity = await self.repo.get_by_id(get_dto.id, request_id)
            if not entity:
                logger.warning("Note not found")
                raise NotFoundError(self.entity_name, str(get_dto.id))
            if role == "user" and entity.owner_id != user_id:
                logger.error("Access denied to Note")
                raise AccessDeniedError(f"Access to this Note is denied")
            response = self._to_response_dto(entity)
            logger.info("Note fetched successfully")
            return response
        except Exception as e:
            logger.exception(f"Failed to get Note", error=str(e))
            raise

    async def list(self, list_dto: NoteListDTO, user_id: UUID, role: str, request_id: str) -> NoteListResponseDTO:
        logger = self.logger.bind(request_id=request_id, user_id=str(user_id), role=role, skip=list_dto.skip, limit=list_dto.limit)
        try:
            logger.info("Listing Notes")
            target_user_id = user_id if role == "user" else None
            entities = await self.repo.list(target_user_id, list_dto.skip, list_dto.limit, request_id)
            total = await self.repo.count_by_user_id(target_user_id, request_id) if target_user_id else 0
            response = NoteListResponseDTO(
                notes=[self._to_response_dto(entity) for entity in entities],
                total=total,
                skip=list_dto.skip,
                limit=list_dto.limit
            )
            logger.info(f"Notes listed successfully", count=len(response.notes), total=total)
            return response
        except Exception as e:
            logger.exception(f"Failed to list Notes", error=str(e))
            raise

    async def update(self, update_dto: NoteUpdateDTO, user_id: UUID, role: str, request_id: str) -> NoteResponseDTO:
        logger = self.logger.bind(request_id=request_id, entity_id=str(update_dto.id), user_id=str(user_id), role=role)
        try:
            logger.info("Updating Note")
            entity = await self.repo.get_by_id(update_dto.id, request_id)
            if not entity:
                logger.warning("Note not found")
                raise NotFoundError(self.entity_name, str(update_dto.id))
            if role == "user" and entity.owner_id != user_id:
                logger.error("Access denied to Note")
                raise AccessDeniedError(f"Access to this Note is denied")
            self._update_entity(entity, update_dto)
            entity.updated_at = datetime.utcnow()
            updated_entity = await self.repo.update(entity, request_id)
            if not updated_entity:
                logger.warning("Note not found after update")
                raise NotFoundError(self.entity_name, str(update_dto.id))
            response = self._to_response_dto(updated_entity)
            logger.info("Note updated successfully")

            await self.publisher.publish("note.updated", {
                "id": str(updated_entity.id),
                "title": updated_entity.title,
                "owner_id": str(updated_entity.owner_id),
                "updated_at": updated_entity.updated_at.isoformat()
            })

            return response
        except Exception as e:
            logger.exception(f"Failed to update Note", error=str(e))
            raise

    async def delete(self, delete_dto: NoteDeleteDTO, user_id: UUID, role: str, request_id: str) -> bool:
        logger = self.logger.bind(request_id=request_id, entity_id=str(delete_dto.id), user_id=str(user_id), role=role)
        try:
            logger.info("Deleting Note")
            entity = await self.repo.get_by_id(delete_dto.id, request_id)
            if not entity:
                logger.warning("Note not found")
                raise NotFoundError(self.entity_name, str(delete_dto.id))
            if role == "user" and entity.owner_id != user_id:
                logger.error("Access denied to Note")
                raise AccessDeniedError(f"Access to this Note is denied")
            await self.repo.delete(delete_dto.id, request_id)
            logger.info("Note deleted successfully")

            await self.publisher.publish("note.deleted", {
                "id": str(delete_dto.id),
                "owner_id": str(user_id)
            })

            return True
        except Exception as e:
            logger.exception(f"Failed to delete Note", error=str(e))
            raise
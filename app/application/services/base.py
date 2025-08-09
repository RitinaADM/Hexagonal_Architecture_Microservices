from abc import abstractmethod
from uuid import UUID
from typing import TypeVar, Generic, List, Optional
from datetime import datetime

from domain.exceptions import NotFoundError, AccessDeniedError, AuthenticationError, LimitExceededError

from domain.ports.outbound.database.base_repository_port import BaseRepositoryPort
from domain.ports.outbound.logger.logger_port import LoggerPort


from infrastructure.config import settings
from application.dto.base import BaseCreateDTO, BaseGetDTO, BaseListDTO, BaseUpdateDTO, BaseDeleteDTO, BaseResponseDTO


T_CreateDTO = TypeVar("T_CreateDTO", bound=BaseCreateDTO)
T_GetDTO = TypeVar("T_GetDTO", bound=BaseGetDTO)
T_ListDTO = TypeVar("T_ListDTO", bound=BaseListDTO)
T_UpdateDTO = TypeVar("T_UpdateDTO", bound=BaseUpdateDTO)
T_DeleteDTO = TypeVar("T_DeleteDTO", bound=BaseDeleteDTO)
T_ResponseDTO = TypeVar("T_ResponseDTO", bound=BaseResponseDTO)
T_Entity = TypeVar("T_Entity")

class BaseService(Generic[T_CreateDTO, T_GetDTO, T_ListDTO, T_UpdateDTO, T_DeleteDTO, T_ResponseDTO, T_Entity]):
    def __init__(self, repo: BaseRepositoryPort[T_Entity], logger: LoggerPort, entity_name: str):
        self.repo = repo
        self.logger = logger.bind(service=f"{entity_name}Service")
        self.entity_name = entity_name

    async def create(self, create_dto: T_CreateDTO, user_id: UUID, role: str, request_id: str) -> T_ResponseDTO:
        logger = self.logger.bind(request_id=request_id, user_id=str(user_id), role=role)
        try:
            logger.info(f"Starting {self.entity_name} creation process")
            if role == "admin" and create_dto.user_id:
                target_user_id = create_dto.user_id
                logger.debug(f"Admin creating {self.entity_name} for user", target_user_id=str(target_user_id))
            elif role == "user":
                target_user_id = user_id
                logger.debug(f"User creating {self.entity_name} for themselves")
            else:
                logger.error("Invalid role provided")
                raise AuthenticationError(f"Invalid role: {role}")

            current_count = await self.repo.count_by_user_id(target_user_id, request_id)
            if current_count >= settings.max_docs_per_user:
                logger.error(f"{self.entity_name} limit exceeded for user", user_id=str(target_user_id))
                raise LimitExceededError(self.entity_name, settings.max_docs_per_user)

            entity = self._create_entity(create_dto, target_user_id)
            created_entity = await self.repo.create(entity, request_id)
            response = self._to_response_dto(created_entity)
            logger.info(f"{self.entity_name} created successfully", entity_id=str(created_entity.id))
            return response
        except Exception as e:
            logger.exception(f"Failed to create {self.entity_name}", error=str(e))
            raise

    async def get(self, get_dto: T_GetDTO, user_id: UUID, role: str, request_id: str) -> T_ResponseDTO:
        logger = self.logger.bind(request_id=request_id, entity_id=str(get_dto.id), user_id=str(user_id), role=role)
        try:
            logger.info(f"Fetching {self.entity_name}")
            entity = await self.repo.get_by_id(get_dto.id, request_id)
            if not entity:
                logger.warning(f"{self.entity_name} not found")
                raise NotFoundError(f"{self.entity_name} with ID {get_dto.id} not found")
            if role == "user" and entity.user_id != user_id:
                logger.error(f"Access denied to {self.entity_name}")
                raise AccessDeniedError(f"Access to this {self.entity_name} is denied")
            response = self._to_response_dto(entity)
            logger.info(f"{self.entity_name} fetched successfully")
            return response
        except Exception as e:
            logger.exception(f"Failed to get {self.entity_name}", error=str(e))
            raise

    async def list(self, list_dto: T_ListDTO, user_id: UUID, role: str, request_id: str) -> List[T_ResponseDTO]:
        logger = self.logger.bind(request_id=request_id, user_id=str(user_id), role=role, skip=list_dto.skip, limit=list_dto.limit)
        try:
            logger.info(f"Listing {self.entity_name}s")
            target_user_id = user_id if role == "user" else (list_dto.user_id if list_dto.user_id else None)
            entities = await self.repo.list(target_user_id, list_dto.skip, list_dto.limit, request_id)
            response = [self._to_response_dto(entity) for entity in entities]
            logger.info(f"{self.entity_name}s listed successfully", count=len(response))
            return response
        except Exception as e:
            logger.exception(f"Failed to list {self.entity_name}s", error=str(e))
            raise

    async def update(self, update_dto: T_UpdateDTO, user_id: UUID, role: str, request_id: str) -> T_ResponseDTO:
        logger = self.logger.bind(request_id=request_id, entity_id=str(update_dto.id), user_id=str(user_id), role=role)
        try:
            logger.info(f"Updating {self.entity_name}")
            entity = await self.repo.get_by_id(update_dto.id, request_id)
            if not entity:
                logger.warning(f"{self.entity_name} not found")
                raise NotFoundError(f"{self.entity_name} with ID {update_dto.id} not found")
            if role == "user" and entity.user_id != user_id:
                logger.error(f"Access denied to {self.entity_name}")
                raise AccessDeniedError(f"Access to this {self.entity_name} is denied")
            self._update_entity(entity, update_dto)
            entity._updated_at = datetime.utcnow()
            updated_entity = await self.repo.update(entity, request_id)
            if not updated_entity:
                logger.warning(f"{self.entity_name} not found after update")
                raise NotFoundError(f"{self.entity_name} with ID {update_dto.id} not found")
            response = self._to_response_dto(updated_entity)
            logger.info(f"{self.entity_name} updated successfully")
            return response
        except Exception as e:
            logger.exception(f"Failed to update {self.entity_name}", error=str(e))
            raise

    async def delete(self, delete_dto: T_DeleteDTO, user_id: UUID, role: str, request_id: str) -> bool:
        logger = self.logger.bind(request_id=request_id, entity_id=str(delete_dto.id), user_id=str(user_id), role=role)
        try:
            logger.info(f"Deleting {self.entity_name}")
            entity = await self.repo.get_by_id(delete_dto.id, request_id)
            if not entity:
                logger.warning(f"{self.entity_name} not found")
                raise NotFoundError(f"{self.entity_name} with ID {delete_dto.id} not found")
            if role == "user" and entity.user_id != user_id:
                logger.error(f"Access denied to {self.entity_name}")
                raise AccessDeniedError(f"Access to this {self.entity_name} is denied")
            await self.repo.delete(delete_dto.id, request_id)
            logger.info(f"{self.entity_name} deleted successfully")
            return True
        except Exception as e:
            logger.exception(f"Failed to delete {self.entity_name}", error=str(e))
            raise

    @abstractmethod
    def _create_entity(self, create_dto: T_CreateDTO, user_id: UUID) -> T_Entity:
        pass

    @abstractmethod
    def _update_entity(self, entity: T_Entity, update_dto: T_UpdateDTO) -> None:
        pass

    @abstractmethod
    def _to_response_dto(self, entity: T_Entity) -> T_ResponseDTO:
        pass
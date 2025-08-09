from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

T_Entity = TypeVar("T_Entity")

class BaseRepositoryPort(ABC, Generic[T_Entity]):
    @abstractmethod
    async def list(self, user_id: Optional[UUID], skip: int, limit: int, request_id: str) -> List[T_Entity]:
        pass


    @abstractmethod
    async def create(self, entity: T_Entity, request_id: str) -> T_Entity:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID, request_id: str) -> Optional[T_Entity]:
        pass

    @abstractmethod
    async def update(self, entity: T_Entity, request_id: str) -> T_Entity:
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID, request_id: str) -> None:
        pass

    @abstractmethod
    async def count_by_user_id(self, user_id: UUID, request_id: str) -> int:
        pass
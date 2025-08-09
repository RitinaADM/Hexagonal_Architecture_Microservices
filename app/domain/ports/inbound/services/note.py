from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
from application.dto.note import NoteCreateDTO, NoteGetDTO, NoteListDTO, NoteUpdateDTO, NoteDeleteDTO, NoteResponseDTO

class NoteServicePort(ABC):
    @abstractmethod
    async def create(self, dto: NoteCreateDTO, user_id: UUID, role: str, request_id: str) -> NoteResponseDTO:
        ...

    @abstractmethod
    async def get(self, dto: NoteGetDTO, user_id: UUID, role: str, request_id: str) -> NoteResponseDTO:
        ...

    @abstractmethod
    async def list(self, dto: NoteListDTO, user_id: UUID, role: str, request_id: str) -> List[NoteResponseDTO]:
        ...

    @abstractmethod
    async def update(self, dto: NoteUpdateDTO, user_id: UUID, role: str, request_id: str) -> NoteResponseDTO:
        ...

    @abstractmethod
    async def delete(self, dto: NoteDeleteDTO, user_id: UUID, role: str, request_id: str) -> bool:
        ...

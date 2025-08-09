from uuid import UUID
from datetime import datetime
from pydantic import Field
from typing import List
from application.dto.base import (
    BaseCreateDTO, BaseGetDTO, BaseListDTO,
    BaseUpdateDTO, BaseDeleteDTO, BaseResponseDTO
)
from domain.models.entities.note import Note

class NoteCreateDTO(BaseCreateDTO):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

class NoteGetDTO(BaseGetDTO):
    pass

class NoteListDTO(BaseListDTO):
    pass

class NoteUpdateDTO(BaseUpdateDTO):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

class NoteDeleteDTO(BaseDeleteDTO):
    pass

class NoteResponseDTO(BaseResponseDTO[Note]):
    title: str
    content: str

    @classmethod
    def from_entity(cls, entity: Note) -> "NoteResponseDTO":
        return cls(
            id=entity.id,
            title=entity.title,
            content=entity.content,
            owner_id=entity.owner_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

class NoteListResponseDTO(BaseListDTO):
    notes: List[NoteResponseDTO] = Field(default_factory=list)
    total: int = 0
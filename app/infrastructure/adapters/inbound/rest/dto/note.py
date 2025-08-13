from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List

class RestNoteCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

class RestNoteGetDTO(BaseModel):
    entity_id: UUID = Field(...)

class RestNoteListDTO(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

class RestNoteUpdateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

class RestNoteDeleteDTO(BaseModel):
    entity_id: UUID = Field(...)

class RestNoteResponseDTO(BaseModel):
    id: UUID
    title: str
    content: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        }

class RestNoteListResponseDTO(BaseModel):
    notes: List[RestNoteResponseDTO] = Field(default_factory=list)
    total: int = 0
    skip: int = 0
    limit: int = 100
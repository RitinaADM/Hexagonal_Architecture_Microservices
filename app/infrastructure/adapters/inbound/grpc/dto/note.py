from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List

class GrpcNoteCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

class GrpcNoteGetDTO(BaseModel):
    entity_id: str = Field(...)  # Строковый UUID для соответствия Protobuf

class GrpcNoteListDTO(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

class GrpcNoteUpdateDTO(BaseModel):
    entity_id: str = Field(...)  # Строковый UUID для соответствия Protobuf
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

class GrpcNoteDeleteDTO(BaseModel):
    entity_id: str = Field(...)  # Строковый UUID для соответствия Protobuf

class GrpcNoteResponseDTO(BaseModel):
    id: str  # Строковый UUID для соответствия Protobuf
    title: str
    content: str
    owner_id: str  # Строковый UUID для соответствия Protobuf
    created_at: str  # ISO-строка для соответствия Protobuf
    updated_at: str  # ISO-строка для соответствия Protobuf

class GrpcNoteListResponseDTO(BaseModel):
    notes: List[GrpcNoteResponseDTO] = Field(default_factory=list)
    total: int = 0
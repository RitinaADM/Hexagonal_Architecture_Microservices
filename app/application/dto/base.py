from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, TypeVar, Generic, Any

T = TypeVar("T")

class BaseCreateDTO(BaseModel):
    pass  # Удаляем user_id

class BaseGetDTO(BaseModel):
    id: UUID = Field(..., alias="entity_id")

class BaseListDTO(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

class BaseUpdateDTO(BaseModel):
    id: UUID = Field(..., alias="entity_id")

class BaseDeleteDTO(BaseModel):
    id: UUID = Field(..., alias="entity_id")

class BaseResponseDTO(BaseModel, Generic[T]):
    id: UUID
    created_at: datetime
    updated_at: datetime
    owner_id: UUID  # Изменено на owner_id

    @classmethod
    def from_entity(cls, entity: Any) -> "BaseResponseDTO":
        raise NotImplementedError

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        }

class BaseListResponseDTO(BaseModel, Generic[T]):
    entities: List[T]
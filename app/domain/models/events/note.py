from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class NoteCreatedEvent(BaseModel):
    id: UUID
    title: str
    owner_id: UUID
    created_at: datetime

class NoteUpdatedEvent(BaseModel):
    id: UUID
    title: str
    owner_id: UUID
    updated_at: datetime

class NoteDeletedEvent(BaseModel):
    id: UUID
    owner_id: UUID
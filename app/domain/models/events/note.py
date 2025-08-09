from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class NoteCreatedEvent(BaseModel):
    id: UUID
    title: str
    owner_id: UUID  # Изменено на owner_id
    created_at: datetime
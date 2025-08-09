from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Note:
    id: UUID
    title: str
    content: str
    owner_id: UUID  # Изменено на owner_id
    created_at: datetime
    updated_at: datetime
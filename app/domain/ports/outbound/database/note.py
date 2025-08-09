from abc import ABC
from domain.ports.outbound.database.base_repository_port import BaseRepositoryPort
from domain.models.entities.note import Note

class NoteRepositoryPort(BaseRepositoryPort[Note], ABC):
    pass
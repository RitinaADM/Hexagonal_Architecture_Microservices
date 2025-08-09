from abc import ABC, abstractmethod
from typing import Any

class EventHandlerPort(ABC):
    @abstractmethod
    async def handle_event(self, event_name: str, payload: dict[str, Any]) -> None:
        ...

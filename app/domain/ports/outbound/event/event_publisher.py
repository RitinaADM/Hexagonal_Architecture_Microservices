from abc import ABC, abstractmethod
from typing import Any

class EventPublisherPort(ABC):
    @abstractmethod
    async def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        ...

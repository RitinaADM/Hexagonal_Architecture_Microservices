from abc import ABC, abstractmethod
from typing import Any

class CachePort(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any:
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        ...

import json
from typing import Any, Optional
from uuid import UUID
from datetime import datetime
from redis.asyncio import Redis
from domain.ports.outbound.cache.cache_port import CachePort
from infrastructure.adapters.outbound.logger.structlog_adapter import StructlogAdapter

class AsyncRedisCacheRepository(CachePort):
    def __init__(self, redis: Redis, logger: StructlogAdapter):
        self.redis = redis
        self.logger = logger.bind(component="AsyncRedisCache")

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.redis.get(key)
            if value:
                self.logger.debug("Cache hit", key=key)
                deserialized = json.loads(value)
                # Convert string UUIDs and datetimes back to their respective types
                if isinstance(deserialized, dict):
                    for field in ["id", "owner_id"]:
                        if field in deserialized and isinstance(deserialized[field], str):
                            try:
                                deserialized[field] = UUID(deserialized[field])
                            except ValueError:
                                self.logger.error(f"Invalid UUID format for {field} in cache", key=key)
                                return None
                    for field in ["created_at", "updated_at"]:
                        if field in deserialized and isinstance(deserialized[field], str):
                            try:
                                deserialized[field] = datetime.fromisoformat(deserialized[field])
                            except ValueError:
                                self.logger.error(f"Invalid datetime format for {field} in cache", key=key)
                                return None
                return deserialized
            self.logger.debug("Cache miss", key=key)
            return None
        except Exception as e:
            self.logger.error("Cache get error", error=str(e), key=key)
            return None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        try:
            # Convert UUID and datetime objects to strings for JSON serialization
            if isinstance(value, dict):
                value = value.copy()  # Avoid modifying the original dict
                for field in ["id", "owner_id"]:
                    if field in value and isinstance(value[field], UUID):
                        value[field] = str(value[field])
                for field in ["created_at", "updated_at"]:
                    if field in value and isinstance(value[field], datetime):
                        value[field] = value[field].isoformat()
            serialized = json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            self.logger.debug("Cache set", key=key, ttl=ttl)
        except Exception as e:
            self.logger.error("Cache set error", error=str(e), key=key)
            raise

    async def delete(self, key: str) -> None:
        try:
            await self.redis.delete(key)
            self.logger.debug("Cache deleted", key=key)
        except Exception as e:
            self.logger.error("Cache delete error", error=str(e), key=key)
            raise
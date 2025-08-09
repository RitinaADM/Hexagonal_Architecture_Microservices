from dishka import Provider, Scope, provide
from redis.asyncio import Redis as AsyncRedis
from infrastructure.config import settings
from domain.ports.outbound.logger.logger_port import LoggerPort


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_async_redis(self, logger: LoggerPort) -> AsyncRedis:
        logger = logger.bind(component="AsyncRedisProvider")
        redis = AsyncRedis.from_url(settings.redis_uri)
        logger.info("Async Redis client initialized")
        return redis
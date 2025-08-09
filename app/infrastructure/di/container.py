from dishka import make_async_container, AsyncContainer
from infrastructure.di.base_provider import BaseProvider
from infrastructure.di.providers.mongo import MongoProvider
from infrastructure.di.providers.redis import RedisProvider
from infrastructure.di.providers.note import NoteProvider
from infrastructure.di.providers.event import EventProvider
from infrastructure.di.providers.security import SecurityProvider
from domain.ports.outbound.logger.logger_port import LoggerPort


async def get_container() -> AsyncContainer:
    container = make_async_container(
        BaseProvider(),
        MongoProvider(),
        RedisProvider(),
        NoteProvider(),
        EventProvider(),
        SecurityProvider(),
    )
    logger = await container.get(LoggerPort)
    logger.bind(component="DI").info("Async DI container initialized")
    return container
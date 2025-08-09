from dishka import Provider, Scope, provide
from motor.motor_asyncio import AsyncIOMotorClient
from infrastructure.config import settings
from domain.ports.outbound.logger.logger_port import LoggerPort


class MongoProvider(Provider):
    @provide(scope=Scope.APP)
    def get_async_mongo_client(self, logger: LoggerPort) -> AsyncIOMotorClient:
        logger = logger.bind(component="AsyncMongoProvider")
        logger.info("Async Mongo client initialized")
        return AsyncIOMotorClient(
            settings.mongo_uri,
            uuidRepresentation=settings.mongo_uuid_representation
        )
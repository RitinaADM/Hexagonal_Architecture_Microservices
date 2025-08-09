from dishka import Provider, Scope, provide
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis as AsyncRedis
from domain.ports.outbound.database.base_repository_port import BaseRepositoryPort
from domain.models.entities.note import Note
from domain.ports.outbound.logger.logger_port import LoggerPort
from domain.ports.outbound.event.event_publisher import EventPublisherPort
from domain.ports.outbound.security.auth_port import AuthPort
from infrastructure.config import settings
from infrastructure.adapters.outbound.database.mongo.note_repository import AsyncMongoNoteRepository
from infrastructure.adapters.outbound.cache.redis_adapter import AsyncRedisCacheRepository
from infrastructure.adapters.inbound.grpc.note_service import NoteServiceServicer
from application.services.note import AsyncNoteService


class NoteProvider(Provider):
    @provide(scope=Scope.APP)
    def get_async_note_repository(
            self,
            mongo: AsyncIOMotorClient,
            redis: AsyncRedis,
            logger: LoggerPort,
    ) -> BaseRepositoryPort[Note]:
        db = mongo[settings.mongo_db]
        collection = db["notes"]
        logger = logger.bind(component="AsyncNoteRepository")
        return AsyncMongoNoteRepository(collection, AsyncRedisCacheRepository(redis, logger), logger)

    @provide(scope=Scope.APP)
    def get_async_note_service(
        self,
        repo: BaseRepositoryPort[Note],
        logger: LoggerPort,
        event_publisher: EventPublisherPort
    ) -> AsyncNoteService:
        logger = logger.bind(component="AsyncNoteService")
        return AsyncNoteService(repo, logger, event_publisher)

    @provide(scope=Scope.APP)
    def get_grpc_note_service(
        self,
        note_service: AsyncNoteService,
        logger: LoggerPort,
        auth: AuthPort
    ) -> NoteServiceServicer:
        logger = logger.bind(component="AsyncNoteGrpcService")
        return NoteServiceServicer(note_service, logger, auth)
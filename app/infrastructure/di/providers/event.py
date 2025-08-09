from dishka import Provider, Scope, provide
from infrastructure.adapters.outbound.broker.rabbitmq_producer import AsyncRabbitMQPublisher
from domain.ports.outbound.event.event_publisher import EventPublisherPort
from domain.ports.outbound.logger.logger_port import LoggerPort


class EventProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_event_publisher(self, logger: LoggerPort) -> EventPublisherPort:
        publisher = AsyncRabbitMQPublisher(logger)  # Remove settings.rabbitmq_uri
        await publisher.startup()  # Call startup to establish connection
        return publisher
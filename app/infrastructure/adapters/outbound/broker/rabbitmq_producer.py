import json
from typing import Any
import aio_pika
import asyncio
from infrastructure.config import settings
from domain.ports.outbound.event.event_publisher import EventPublisherPort


class AsyncRabbitMQPublisher(EventPublisherPort):
    def __init__(self, logger):
        self.logger = logger.bind(component="AsyncRabbitMQPublisher")
        self.connection = None
        self.channel = None
        self.exchange = None

    async def startup(self):
        self.logger.info("Starting RabbitMQ connection")
        retries = 5
        for attempt in range(retries):
            try:
                self.connection = await aio_pika.connect_robust(settings.rabbitmq_uri)
                self.channel = await self.connection.channel()
                # Attempt to delete the existing exchange to resolve durable mismatch
                try:
                    await self.channel.exchange_delete("events")
                    self.logger.info("Existing 'events' exchange deleted to resolve durable mismatch")
                except Exception as e:
                    self.logger.debug("No existing 'events' exchange to delete or error occurred", error=str(e))
                self.exchange = await self.channel.declare_exchange(
                    "events",
                    aio_pika.ExchangeType.TOPIC,
                    durable=True
                )
                self.logger.info("RabbitMQ connection established")
                return
            except Exception as e:
                self.logger.error(f"Failed to connect to RabbitMQ, attempt {attempt + 1}/{retries}", error=str(e))
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    async def shutdown(self):
        self.logger.info("Closing RabbitMQ connection")
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        self.logger.info("RabbitMQ connection closed")

    async def publish(self, event_name: str, data: Any) -> None:
        self.logger.info(f"Publishing event", event_name=event_name)
        try:
            # Serialize the data to JSON and encode to bytes
            message_body = json.dumps(data).encode('utf-8')
            message = aio_pika.Message(
                body=message_body,
                content_type='application/json',
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            await self.exchange.publish(
                message,
                routing_key=event_name
            )
            self.logger.debug(f"Event published successfully", event_name=event_name)
        except Exception as e:
            self.logger.exception(f"Failed to publish event", event_name=event_name, error=str(e))
            raise
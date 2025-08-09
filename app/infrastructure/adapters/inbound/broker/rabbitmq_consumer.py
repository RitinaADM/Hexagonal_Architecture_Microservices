from aio_pika import connect_robust, IncomingMessage, ExchangeType
from domain.ports.inbound.event_handler import EventHandlerPort
from domain.ports.outbound.logger.logger_port import LoggerPort
import json
import asyncio


async def start_consumer(uri: str, handler: EventHandlerPort, logger: LoggerPort):
    logger = logger.bind(component="RabbitMQConsumer")
    connection = None
    try:
        connection = await connect_robust(uri)
        channel = await connection.channel()
        exchange = await channel.declare_exchange("events", ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue("note_queue", durable=True)  # Use named, durable queue
        await queue.bind(exchange, routing_key="note.*")

        async def on_message(message: IncomingMessage):
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    logger.info("Event received", routing_key=message.routing_key, payload=payload)
                    await handler.handle_event(message.routing_key, payload)
                except Exception as e:
                    logger.exception("Failed to process message", error=str(e))

        await queue.consume(on_message)
        logger.info("RabbitMQ consumer started successfully")
        # Keep consumer running until interrupted
        await asyncio.Event().wait()
    except Exception as e:
        logger.exception("Failed to start RabbitMQ consumer", error=str(e))
        raise
    finally:
        if connection:
            await connection.close()
            logger.info("RabbitMQ consumer connection closed")
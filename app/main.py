import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response
from dishka.integrations.fastapi import setup_dishka
from infrastructure.di.container import get_container
from infrastructure.adapters.inbound.broker.rabbitmq_consumer import start_consumer
from infrastructure.adapters.inbound.grpc.server import start_grpc_server
from infrastructure.adapters.inbound.grpc.auth_interceptor import AuthInterceptor
from infrastructure.adapters.inbound.grpc.note_service import NoteServiceServicer
from infrastructure.adapters.inbound.rest.note_router import router
from application.event_handlers.note_event_handler import NoteEventHandler
from domain.ports.outbound.security.auth_port import AuthPort
from domain.ports.outbound.logger.logger_port import LoggerPort
from domain.ports.outbound.event.event_publisher import EventPublisherPort
from infrastructure.config import settings
import uuid
import structlog.contextvars
import structlog

app = FastAPI(title="Note Service")
app.include_router(router)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    endpoint = request.url.path
    client_ip = request.client.host if request.client else "unknown"

    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        endpoint=endpoint,
        client_ip=client_ip,
    )

    logger = structlog.get_logger().bind(
        component="RESTMiddleware",
        method=request.method,
    )
    logger.info("Received request")

    try:
        response = await call_next(request)
        logger.info("Request completed", status_code=response.status_code)
        return response
    except Exception as e:
        logger.exception("Request failed", error=str(e))
        raise
    finally:
        structlog.contextvars.clear_contextvars()

async def main():
    container = await get_container()
    logger = await container.get(LoggerPort)
    handler = NoteEventHandler(logger)
    note_service = await container.get(NoteServiceServicer)
    auth = await container.get(AuthPort)
    publisher = await container.get(EventPublisherPort)

    auth_interceptor = AuthInterceptor(auth, logger)
    setup_dishka(container, app)

    # Start RabbitMQ consumer
    logger.info("Starting RabbitMQ consumer")
    consumer_task = asyncio.create_task(start_consumer(settings.rabbitmq_uri, handler, logger))

    # Start async gRPC server
    logger.info("Starting gRPC server")
    grpc_task = asyncio.create_task(start_grpc_server(note_service, auth_interceptor, logger))

    # Start FastAPI server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=settings.rest_port,
        log_level="info"
    )
    server = uvicorn.Server(config)

    logger.info("Application started")
    try:
        await server.serve()
    except asyncio.CancelledError:
        logger.info("Received shutdown signal")
    finally:
        # Gracefully shut down
        logger.info("Shutting down application")
        consumer_task.cancel()
        await publisher.shutdown()
        try:
            await consumer_task
            logger.info("Consumer task cancelled")
        except asyncio.CancelledError:
            logger.info("Consumer task cancellation confirmed")
        await container.close()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
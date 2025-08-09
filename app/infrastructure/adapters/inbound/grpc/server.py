import grpc
from grpc_reflection.v1alpha import reflection
from . import note_pb2, note_pb2_grpc
from infrastructure.adapters.inbound.grpc.note_service import NoteServiceServicer
from infrastructure.adapters.inbound.grpc.auth_interceptor import AuthInterceptor
from domain.ports.outbound.logger.logger_port import LoggerPort

async def start_grpc_server(
    note_service: NoteServiceServicer, auth_interceptor: AuthInterceptor, logger: LoggerPort
):
    server = grpc.aio.server(interceptors=[auth_interceptor])
    note_pb2_grpc.add_NoteServiceServicer_to_server(note_service, server)

    # Enable gRPC reflection
    SERVICE_NAMES = (
        note_pb2.DESCRIPTOR.services_by_name["NoteService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port("[::]:50051")
    logger.info("Starting async gRPC server on port 50051 with reflection enabled")
    await server.start()
    logger.info("Async gRPC server started successfully")
    await server.wait_for_termination()
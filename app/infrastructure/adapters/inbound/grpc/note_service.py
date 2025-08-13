import grpc
from typing import Tuple
from uuid import UUID, uuid4
from domain.exceptions.auth import AuthenticationError
from domain.ports.outbound.security.auth_port import AuthPort
from domain.ports.outbound.logger.logger_port import LoggerPort
from application.services.note import AsyncNoteService
from infrastructure.adapters.inbound.grpc import note_pb2, note_pb2_grpc
from infrastructure.adapters.inbound.grpc.dto.note import (
    GrpcNoteCreateDTO, GrpcNoteGetDTO, GrpcNoteListDTO, GrpcNoteUpdateDTO,
    GrpcNoteDeleteDTO, GrpcNoteResponseDTO, GrpcNoteListResponseDTO
)
from infrastructure.adapters.inbound.grpc.mappers import (
    proto_to_grpc_create_dto, proto_to_grpc_get_dto, proto_to_grpc_list_dto,
    proto_to_grpc_update_dto, proto_to_grpc_delete_dto,
    grpc_to_service_create_dto, grpc_to_service_get_dto, grpc_to_service_list_dto,
    grpc_to_service_update_dto, grpc_to_service_delete_dto,
    service_to_grpc_response_dto, service_to_grpc_list_response_dto,
    grpc_to_proto_response, grpc_to_proto_list_response
)
from infrastructure.adapters.inbound.grpc.utils import async_handle_grpc_exceptions, log_execution_time


class NoteServiceServicer(note_pb2_grpc.NoteServiceServicer):
    def __init__(self, service: AsyncNoteService, logger: LoggerPort, auth: AuthPort):
        self.service = service
        self.logger = logger.bind(component="AsyncNoteGrpcService")
        self.auth = auth
        self.logger.debug("NoteServiceServicer initialized")

    def _extract_metadata(self, context: grpc.aio.ServicerContext, method: str) -> Tuple[UUID, str, str]:
        metadata = dict(context.invocation_metadata())
        self.logger.debug(f"Metadata received: {metadata}", endpoint=method)

        token = metadata.get("authorization", "").replace("Bearer ", "")
        if not token:
            self.logger.error("No token provided", metadata=metadata)
            raise AuthenticationError("No token provided")

        try:
            user_id, role = self.auth.verify_token(token)
            request_id = metadata.get("request_id", str(uuid4()))
            self.logger.debug(f"Token verified, user_id={user_id}, role={role}, request_id={request_id}")
            return user_id, role, request_id
        except AuthenticationError as e:
            self.logger.error("Authentication failed", error=str(e), metadata=metadata)
            raise

    @async_handle_grpc_exceptions
    @log_execution_time
    async def CreateNote(self, request, context):
        user_id, role, request_id = self._extract_metadata(context, "CreateNote")
        logger = self.logger.bind(request_id=request_id, endpoint="CreateNote")
        logger.debug(f"Entering CreateNote with user_id={user_id}, role={role}")

        grpc_dto = proto_to_grpc_create_dto(request)
        service_dto = grpc_to_service_create_dto(grpc_dto)
        result = await self.service.create(service_dto, user_id, role, request_id)
        logger.info("Note created successfully")
        return grpc_to_proto_response(service_to_grpc_response_dto(result))

    @async_handle_grpc_exceptions
    @log_execution_time
    async def GetNote(self, request, context):
        user_id, role, request_id = self._extract_metadata(context, "GetNote")
        logger = self.logger.bind(request_id=request_id, endpoint="GetNote")
        logger.debug(f"Entering GetNote with entity_id={request.entity_id}")

        grpc_dto = proto_to_grpc_get_dto(request)
        service_dto = grpc_to_service_get_dto(grpc_dto)
        result = await self.service.get(service_dto, user_id, role, request_id)
        logger.info("Note retrieved successfully")
        return grpc_to_proto_response(service_to_grpc_response_dto(result))

    @async_handle_grpc_exceptions
    @log_execution_time
    async def ListNotes(self, request, context):
        user_id, role, request_id = self._extract_metadata(context, "ListNotes")
        logger = self.logger.bind(request_id=request_id, endpoint="ListNotes")
        logger.debug(f"Entering ListNotes with skip={request.skip}, limit={request.limit}")

        grpc_dto = proto_to_grpc_list_dto(request)
        service_dto = grpc_to_service_list_dto(grpc_dto)
        result = await self.service.list(service_dto, user_id, role, request_id)
        logger.info("Notes listed successfully")
        return grpc_to_proto_list_response(service_to_grpc_list_response_dto(result))

    @async_handle_grpc_exceptions
    @log_execution_time
    async def UpdateNote(self, request, context):
        user_id, role, request_id = self._extract_metadata(context, "UpdateNote")
        logger = self.logger.bind(request_id=request_id, endpoint="UpdateNote")
        logger.debug(f"Entering UpdateNote with entity_id={request.entity_id}")

        grpc_dto = proto_to_grpc_update_dto(request)
        service_dto = grpc_to_service_update_dto(grpc_dto)
        result = await self.service.update(service_dto, user_id, role, request_id)
        logger.info("Note updated successfully")
        return grpc_to_proto_response(service_to_grpc_response_dto(result))

    @async_handle_grpc_exceptions
    @log_execution_time
    async def DeleteNote(self, request, context):
        user_id, role, request_id = self._extract_metadata(context, "DeleteNote")
        logger = self.logger.bind(request_id=request_id, endpoint="DeleteNote")
        logger.debug(f"Entering DeleteNote with entity_id={request.entity_id}")

        grpc_dto = proto_to_grpc_delete_dto(request)
        service_dto = grpc_to_service_delete_dto(grpc_dto)
        await self.service.delete(service_dto, user_id, role, request_id)
        logger.info("Note deleted successfully")
        return note_pb2.DeleteNoteResponse()
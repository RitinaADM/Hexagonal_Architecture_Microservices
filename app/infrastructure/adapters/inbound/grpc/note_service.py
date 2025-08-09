import grpc
import uuid
from typing import Tuple
from uuid import UUID
from domain.exceptions.auth import AuthenticationError
from domain.ports.outbound.security.auth_port import AuthPort
from domain.ports.outbound.logger.logger_port import LoggerPort
from application.services.note import AsyncNoteService
from application.dto.note import NoteCreateDTO, NoteGetDTO, NoteListDTO, NoteUpdateDTO, NoteDeleteDTO, NoteResponseDTO, NoteListResponseDTO
from infrastructure.adapters.inbound.grpc import note_pb2, note_pb2_grpc
from infrastructure.adapters.inbound.grpc.utils import async_handle_grpc_exceptions, log_execution_time

def map_to_note_response(note: NoteResponseDTO) -> note_pb2.NoteResponse:
    return note_pb2.NoteResponse(
        id=str(note.id),
        title=note.title,
        content=note.content,
        owner_id=str(note.owner_id),
        created_at=note.created_at.isoformat(),
        updated_at=note.updated_at.isoformat()
    )

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
            request_id = metadata.get("request_id", str(uuid.uuid4()))
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

        dto = NoteCreateDTO(title=request.title, content=request.content)
        result = await self.service.create(dto, user_id, role, request_id)
        logger.info("Note created successfully")
        return map_to_note_response(result)

    @async_handle_grpc_exceptions
    @log_execution_time
    async def GetNote(self, request, context):
        user_id, role, request_id = self._extract_metadata(context, "GetNote")
        logger = self.logger.bind(request_id=request_id, endpoint="GetNote")
        logger.debug(f"Entering GetNote with entity_id={request.entity_id}")

        dto = NoteGetDTO(entity_id=UUID(request.entity_id))
        result = await self.service.get(dto, user_id, role, request_id)
        logger.info("Note retrieved successfully")
        return map_to_note_response(result)

    @async_handle_grpc_exceptions
    @log_execution_time
    async def ListNotes(self, request, context):
        user_id, role, request_id = self._extract_metadata(context, "ListNotes")
        logger = self.logger.bind(request_id=request_id, endpoint="ListNotes")
        logger.debug(f"Entering ListNotes with skip={request.skip}, limit={request.limit}")

        dto = NoteListDTO(skip=request.skip, limit=request.limit)
        result = await self.service.list(dto, user_id, role, request_id)
        logger.info("Notes listed successfully")
        return note_pb2.ListNotesResponse(notes=[map_to_note_response(note) for note in result.notes])

    @async_handle_grpc_exceptions
    @log_execution_time
    async def UpdateNote(self, request, context):
        user_id, role, request_id = self._extract_metadata(context, "UpdateNote")
        logger = self.logger.bind(request_id=request_id, endpoint="UpdateNote")
        logger.debug(f"Entering UpdateNote with entity_id={request.entity_id}")

        dto = NoteUpdateDTO(entity_id=UUID(request.entity_id), title=request.title, content=request.content)
        result = await self.service.update(dto, user_id, role, request_id)
        logger.info("Note updated successfully")
        return map_to_note_response(result)

    @async_handle_grpc_exceptions
    @log_execution_time
    async def DeleteNote(self, request, context):
        user_id, role, request_id = self._extract_metadata(context, "DeleteNote")
        logger = self.logger.bind(request_id=request_id, endpoint="DeleteNote")
        logger.debug(f"Entering DeleteNote with entity_id={request.entity_id}")

        dto = NoteDeleteDTO(entity_id=UUID(request.entity_id))
        await self.service.delete(dto, user_id, role, request_id)
        logger.info("Note deleted successfully")
        return note_pb2.DeleteNoteResponse()
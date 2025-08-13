from uuid import UUID
from datetime import datetime
from application.dto.note import (
    NoteCreateDTO, NoteGetDTO, NoteListDTO, NoteUpdateDTO, NoteDeleteDTO,
    NoteResponseDTO, NoteListResponseDTO
)
from infrastructure.adapters.inbound.grpc.dto.note import (
    GrpcNoteCreateDTO, GrpcNoteGetDTO, GrpcNoteListDTO, GrpcNoteUpdateDTO,
    GrpcNoteDeleteDTO, GrpcNoteResponseDTO, GrpcNoteListResponseDTO
)
from infrastructure.adapters.inbound.grpc import note_pb2

def grpc_to_service_create_dto(grpc_dto: GrpcNoteCreateDTO) -> NoteCreateDTO:
    return NoteCreateDTO(title=grpc_dto.title, content=grpc_dto.content)

def grpc_to_service_get_dto(grpc_dto: GrpcNoteGetDTO) -> NoteGetDTO:
    return NoteGetDTO(entity_id=UUID(grpc_dto.entity_id))

def grpc_to_service_list_dto(grpc_dto: GrpcNoteListDTO) -> NoteListDTO:
    return NoteListDTO(skip=grpc_dto.skip, limit=grpc_dto.limit)

def grpc_to_service_update_dto(grpc_dto: GrpcNoteUpdateDTO) -> NoteUpdateDTO:
    return NoteUpdateDTO(
        entity_id=UUID(grpc_dto.entity_id),
        title=grpc_dto.title,
        content=grpc_dto.content
    )

def grpc_to_service_delete_dto(grpc_dto: GrpcNoteDeleteDTO) -> NoteDeleteDTO:
    return NoteDeleteDTO(entity_id=UUID(grpc_dto.entity_id))

def service_to_grpc_response_dto(service_dto: NoteResponseDTO) -> GrpcNoteResponseDTO:
    return GrpcNoteResponseDTO(
        id=str(service_dto.id),
        title=service_dto.title,
        content=service_dto.content,
        owner_id=str(service_dto.owner_id),
        created_at=service_dto.created_at.isoformat(),
        updated_at=service_dto.updated_at.isoformat()
    )

def service_to_grpc_list_response_dto(service_dto: NoteListResponseDTO) -> GrpcNoteListResponseDTO:
    return GrpcNoteListResponseDTO(
        notes=[service_to_grpc_response_dto(note) for note in service_dto.notes],
        total=service_dto.total
    )

def proto_to_grpc_create_dto(request: note_pb2.CreateNoteRequest) -> GrpcNoteCreateDTO:
    return GrpcNoteCreateDTO(title=request.title, content=request.content)

def proto_to_grpc_get_dto(request: note_pb2.GetNoteRequest) -> GrpcNoteGetDTO:
    return GrpcNoteGetDTO(entity_id=request.entity_id)

def proto_to_grpc_list_dto(request: note_pb2.ListNotesRequest) -> GrpcNoteListDTO:
    return GrpcNoteListDTO(skip=request.skip, limit=request.limit)

def proto_to_grpc_update_dto(request: note_pb2.UpdateNoteRequest) -> GrpcNoteUpdateDTO:
    return GrpcNoteUpdateDTO(
        entity_id=request.entity_id,
        title=request.title,
        content=request.content
    )

def proto_to_grpc_delete_dto(request: note_pb2.DeleteNoteRequest) -> GrpcNoteDeleteDTO:
    return GrpcNoteDeleteDTO(entity_id=request.entity_id)

def grpc_to_proto_response(grpc_dto: GrpcNoteResponseDTO) -> note_pb2.NoteResponse:
    return note_pb2.NoteResponse(
        id=grpc_dto.id,
        title=grpc_dto.title,
        content=grpc_dto.content,
        owner_id=grpc_dto.owner_id,
        created_at=grpc_dto.created_at,
        updated_at=grpc_dto.updated_at
    )

def grpc_to_proto_list_response(grpc_dto: GrpcNoteListResponseDTO) -> note_pb2.ListNotesResponse:
    return note_pb2.ListNotesResponse(
        notes=[grpc_to_proto_response(note) for note in grpc_dto.notes],
        total=grpc_dto.total
    )
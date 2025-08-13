from uuid import UUID
from application.dto.note import (
    NoteCreateDTO, NoteGetDTO, NoteListDTO, NoteUpdateDTO, NoteDeleteDTO,
    NoteResponseDTO, NoteListResponseDTO
)
from infrastructure.adapters.inbound.rest.dto.note import (
    RestNoteCreateDTO, RestNoteGetDTO, RestNoteListDTO, RestNoteUpdateDTO,
    RestNoteDeleteDTO, RestNoteResponseDTO, RestNoteListResponseDTO
)

def rest_to_service_create_dto(rest_dto: RestNoteCreateDTO) -> NoteCreateDTO:
    return NoteCreateDTO(title=rest_dto.title, content=rest_dto.content)

def rest_to_service_get_dto(rest_dto: RestNoteGetDTO) -> NoteGetDTO:
    return NoteGetDTO(entity_id=rest_dto.entity_id)

def rest_to_service_list_dto(rest_dto: RestNoteListDTO) -> NoteListDTO:
    return NoteListDTO(skip=rest_dto.skip, limit=rest_dto.limit)

def rest_to_service_update_dto(rest_dto: RestNoteUpdateDTO, entity_id: UUID) -> NoteUpdateDTO:
    return NoteUpdateDTO(entity_id=entity_id, title=rest_dto.title, content=rest_dto.content)

def rest_to_service_delete_dto(rest_dto: RestNoteDeleteDTO) -> NoteDeleteDTO:
    return NoteDeleteDTO(entity_id=rest_dto.entity_id)

def service_to_rest_response_dto(service_dto: NoteResponseDTO) -> RestNoteResponseDTO:
    return RestNoteResponseDTO(
        id=service_dto.id,
        title=service_dto.title,
        content=service_dto.content,
        owner_id=service_dto.owner_id,
        created_at=service_dto.created_at,
        updated_at=service_dto.updated_at
    )

def service_to_rest_list_response_dto(service_dto: NoteListResponseDTO) -> RestNoteListResponseDTO:
    return RestNoteListResponseDTO(
        notes=[service_to_rest_response_dto(note) for note in service_dto.notes],
        total=service_dto.total,
        skip=service_dto.skip,
        limit=service_dto.limit
    )
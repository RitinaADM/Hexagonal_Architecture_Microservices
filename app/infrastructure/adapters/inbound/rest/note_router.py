from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID, uuid4
from application.services.note import AsyncNoteService
from infrastructure.adapters.inbound.rest.dto.note import (
    RestNoteCreateDTO, RestNoteGetDTO, RestNoteListDTO, RestNoteUpdateDTO,
    RestNoteDeleteDTO, RestNoteResponseDTO, RestNoteListResponseDTO
)
from infrastructure.adapters.inbound.rest.mappers import (
    rest_to_service_create_dto, rest_to_service_get_dto, rest_to_service_list_dto,
    rest_to_service_update_dto, rest_to_service_delete_dto,
    service_to_rest_response_dto, service_to_rest_list_response_dto
)
from domain.exceptions import AuthenticationError, NotFoundError, AccessDeniedError, LimitExceededError
from domain.ports.outbound.logger.logger_port import LoggerPort
from infrastructure.di.container import get_container
from .auth import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/", response_model=RestNoteResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_note(
    dto: RestNoteCreateDTO,
    user: tuple[UUID, str] = Depends(get_current_user),
):
    container = await get_container()
    service = await container.get(AsyncNoteService)
    logger = await container.get(LoggerPort)
    request_id = str(uuid4())
    logger = logger.bind(request_id=request_id, endpoint="create_note")
    try:
        user_id, role = user
        service_dto = rest_to_service_create_dto(dto)
        result = await service.create(service_dto, user_id, role, request_id)
        logger.info("Note created successfully")
        return service_to_rest_response_dto(result)
    except LimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.exception("Failed to create note", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{entity_id}", response_model=RestNoteResponseDTO)
async def get_note(
    entity_id: UUID,
    user: tuple[UUID, str] = Depends(get_current_user),
):
    container = await get_container()
    service = await container.get(AsyncNoteService)
    logger = await container.get(LoggerPort)
    request_id = str(uuid4())
    logger = logger.bind(request_id=request_id, endpoint="get_note")
    try:
        user_id, role = user
        dto = rest_to_service_get_dto(RestNoteGetDTO(entity_id=entity_id))
        result = await service.get(dto, user_id, role, request_id)
        logger.info("Note retrieved successfully")
        return service_to_rest_response_dto(result)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.exception("Failed to get note", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=RestNoteListResponseDTO)
async def list_notes(
    skip: int = 0,
    limit: int = 100,
    user: tuple[UUID, str] = Depends(get_current_user),
):
    container = await get_container()
    service = await container.get(AsyncNoteService)
    logger = await container.get(LoggerPort)
    request_id = str(uuid4())
    logger = logger.bind(request_id=request_id, endpoint="list_notes")
    try:
        user_id, role = user
        dto = rest_to_service_list_dto(RestNoteListDTO(skip=skip, limit=limit))
        result = await service.list(dto, user_id, role, request_id)
        logger.info("Notes listed successfully")
        return service_to_rest_list_response_dto(result)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.exception("Failed to list notes", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{entity_id}", response_model=RestNoteResponseDTO)
async def update_note(
    entity_id: UUID,
    dto: RestNoteUpdateDTO,
    user: tuple[UUID, str] = Depends(get_current_user),
):
    container = await get_container()
    service = await container.get(AsyncNoteService)
    logger = await container.get(LoggerPort)
    request_id = str(uuid4())
    logger = logger.bind(request_id=request_id, endpoint="update_note")
    try:
        user_id, role = user
        service_dto = rest_to_service_update_dto(dto, entity_id)
        result = await service.update(service_dto, user_id, role, request_id)
        logger.info("Note updated successfully")
        return service_to_rest_response_dto(result)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.exception("Failed to update note", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    entity_id: UUID,
    user: tuple[UUID, str] = Depends(get_current_user),
):
    container = await get_container()
    service = await container.get(AsyncNoteService)
    logger = await container.get(LoggerPort)
    request_id = str(uuid4())
    logger = logger.bind(request_id=request_id, endpoint="delete_note")
    try:
        user_id, role = user
        dto = rest_to_service_delete_dto(RestNoteDeleteDTO(entity_id=entity_id))
        await service.delete(dto, user_id, role, request_id)
        logger.info("Note deleted successfully")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.exception("Failed to delete note", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
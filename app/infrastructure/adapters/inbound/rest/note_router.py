from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID, uuid4
from application.services.note import AsyncNoteService
from application.dto.note import (
    NoteCreateDTO, NoteGetDTO, NoteListDTO,
    NoteUpdateDTO, NoteDeleteDTO, NoteResponseDTO, NoteListResponseDTO
)
from domain.exceptions import AuthenticationError, NotFoundError, AccessDeniedError, LimitExceededError
from domain.ports.outbound.logger.logger_port import LoggerPort
from infrastructure.di.container import get_container
from .auth import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/", response_model=NoteResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_note(
    dto: NoteCreateDTO,
    user: tuple[UUID, str] = Depends(get_current_user),
):
    container = await get_container()
    service = await container.get(AsyncNoteService)
    logger = await container.get(LoggerPort)
    request_id = str(uuid4())
    logger = logger.bind(request_id=request_id, endpoint="create_note")
    try:
        user_id, role = user
        result = await service.create(dto, user_id, role, request_id)
        logger.info("Note created successfully")
        return result
    except LimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.exception("Failed to create note", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{entity_id}", response_model=NoteResponseDTO)
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
        dto = NoteGetDTO(entity_id=entity_id)
        result = await service.get(dto, user_id, role, request_id)
        logger.info("Note retrieved successfully")
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.exception("Failed to get note", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=NoteListResponseDTO)
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
        dto = NoteListDTO(skip=skip, limit=limit)
        result = await service.list(dto, user_id, role, request_id)
        logger.info("Notes listed successfully")
        return result
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.exception("Failed to list notes", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{entity_id}", response_model=NoteResponseDTO)
async def update_note(
    entity_id: UUID,
    dto: NoteUpdateDTO,
    user: tuple[UUID, str] = Depends(get_current_user),
):
    container = await get_container()
    service = await container.get(AsyncNoteService)
    logger = await container.get(LoggerPort)
    request_id = str(uuid4())
    logger = logger.bind(request_id=request_id, endpoint="update_note")
    try:
        user_id, role = user
        dto.entity_id = entity_id
        result = await service.update(dto, user_id, role, request_id)
        logger.info("Note updated successfully")
        return result
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
        dto = NoteDeleteDTO(entity_id=entity_id)
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
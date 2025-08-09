from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from domain.ports.outbound.security.auth_port import AuthPort
from domain.ports.outbound.logger.logger_port import LoggerPort
from domain.exceptions import AuthenticationError
from infrastructure.di.container import get_container

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> tuple[UUID, str]:
    container = await get_container()
    auth = await container.get(AuthPort)
    logger = await container.get(LoggerPort)
    logger = logger.bind(component="RESTAuth")
    try:
        token = credentials.credentials
        user_id, role = auth.verify_token(token)
        logger.info("User authenticated successfully", user_id=str(user_id), role=role)
        return user_id, role
    except AuthenticationError as e:
        logger.error("Authentication failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
from uuid import UUID
from jose import jwt, JWTError
from domain.ports.outbound.security.auth_port import AuthPort
from domain.ports.outbound.logger.logger_port import LoggerPort
from domain.exceptions import AuthenticationError
from infrastructure.config import settings

class JWTAuthAdapter(AuthPort):
    def __init__(self, logger: LoggerPort):
        self.logger = logger.bind(component="JWTAuthAdapter")
        self.algorithm = "HS256"

    def verify_token(self, token: str) -> tuple[UUID, str]:
        logger = self.logger.bind(token=token)
        try:
            if not token:
                logger.error("No token provided")
                raise AuthenticationError("No token provided")
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            role = payload.get("role", "user")
            if not user_id:
                logger.error("Invalid token: no user_id")
                raise AuthenticationError("Invalid token: no user_id")
            try:
                user_id = UUID(user_id)
            except ValueError:
                logger.error("Invalid user_id format")
                raise AuthenticationError("Invalid user_id format")
            logger.info("Token verified successfully")
            return user_id, role
        except JWTError as e:
            logger.error(f"Failed to verify token", error=str(e))
            raise AuthenticationError(f"Invalid token: {str(e)}")
from .base import AppBaseException

class AuthenticationError(AppBaseException):
    """Ошибка аутентификации."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)
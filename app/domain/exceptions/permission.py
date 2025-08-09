from .base import AppBaseException

class AccessDeniedError(AppBaseException):
    """Ошибка доступа."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message)
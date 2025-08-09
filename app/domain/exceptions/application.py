from .base import AppBaseException

class ValidationException(AppBaseException):
    """Ошибка валидации входных данных."""
    def __init__(self, field: str, message: str):
        super().__init__(f"Validation failed for '{field}': {message}")


class UseCaseException(AppBaseException):
    """Ошибка на уровне бизнес-логики в Application слое."""
    pass

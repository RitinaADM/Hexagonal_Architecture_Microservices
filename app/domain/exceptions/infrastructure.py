from .base import AppBaseException

class DatabaseException(AppBaseException):
    """Ошибка взаимодействия с базой данных."""
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message)


class ExternalServiceException(AppBaseException):
    """Ошибка вызова внешнего сервиса."""
    def __init__(self, service_name: str, message: str = ""):
        msg = f"External service '{service_name}' failed"
        if message:
            msg += f": {message}"
        super().__init__(msg)


class MessageBrokerException(AppBaseException):
    """Ошибка брокера сообщений."""
    def __init__(self, message: str):
        super().__init__(f"Message broker error: {message}")

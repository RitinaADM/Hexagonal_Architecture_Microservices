class AppBaseException(Exception):
    """Базовое приложение исключение."""
    pass


class InternalError(AppBaseException):
    """Внутренняя ошибка приложения."""
    def __init__(self, message="Internal server error"):
        super().__init__(message)

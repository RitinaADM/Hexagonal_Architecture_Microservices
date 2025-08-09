from .base import AppBaseException

class LimitExceededError(AppBaseException):
    """Превышение лимита."""
    def __init__(self, entity_name: str, limit: int):
        super().__init__(f"{entity_name} limit of {limit} exceeded")
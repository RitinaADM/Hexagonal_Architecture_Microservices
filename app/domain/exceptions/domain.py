from .base import AppBaseException

class EntityNotFound(AppBaseException):
    """Сущность не найдена в домене."""
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(f"{entity_name} with ID '{entity_id}' not found")


class BusinessRuleViolation(AppBaseException):
    """Нарушение бизнес-правила."""
    def __init__(self, rule_description: str):
        super().__init__(f"Business rule violated: {rule_description}")

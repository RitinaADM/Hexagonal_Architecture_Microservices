from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

class AuthPort(ABC):
    @abstractmethod
    def verify_token(self, token: str) -> tuple[UUID, str]:
        """
        Проверяет JWT-токен и возвращает user_id и role.
        Args:
            token: JWT-токен.
        Returns:
            tuple[UUID, str]: Кортеж из user_id и role.
        Raises:
            AuthenticationError: Если токен недействителен.
        """
        pass
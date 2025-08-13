from abc import ABC, abstractmethod
from pydantic import ValidationError
from domain.ports.inbound.event_handler import EventHandlerPort
from domain.ports.outbound.logger.logger_port import LoggerPort

class BaseEventHandler(EventHandlerPort, ABC):
    def __init__(self, logger: LoggerPort):
        self.logger = logger.bind(component="BaseEventHandler")

    async def handle_event(self, event_name: str, payload: dict) -> None:
        """
        Базовая обработка событий: логирование, валидация и вызов специфичной логики.
        """
        self.logger.info("Received event", event_name=event_name, payload=payload)
        try:
            # Вызов специфичной логики обработки события
            await self._process_event(event_name, payload)
        except ValidationError as e:
            self.logger.error("Invalid event payload", error=str(e), event_name=event_name, payload=payload)
        except Exception as e:
            self.logger.exception("Failed to handle event", error=str(e), event_name=event_name)

    @abstractmethod
    async def _process_event(self, event_name: str, payload: dict) -> None:
        """
        Абстрактный метод для реализации специфичной логики обработки событий.
        """
        pass
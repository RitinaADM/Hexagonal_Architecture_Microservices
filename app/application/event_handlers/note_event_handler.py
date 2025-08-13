from pydantic import ValidationError
from domain.ports.outbound.logger.logger_port import LoggerPort
from domain.models.events.note import NoteCreatedEvent, NoteUpdatedEvent, NoteDeletedEvent
from application.event_handlers.base_event_handler import BaseEventHandler

class NoteEventHandler(BaseEventHandler):
    def __init__(self, logger: LoggerPort):
        super().__init__(logger.bind(component="NoteEventHandler"))

    async def _process_event(self, event_name: str, payload: dict) -> None:
        """
        Специфичная логика обработки событий для сущности Note.
        """
        if event_name == "note.created":
            event = NoteCreatedEvent(**payload)
            self.logger.info("Processing note.created event", note_id=str(event.id))
            # TODO: Добавить логику, например, отправку уведомления или обновление метрик
        elif event_name == "note.updated":
            event = NoteUpdatedEvent(**payload)
            self.logger.info("Processing note.updated event", note_id=str(event.id))
            # TODO: Добавить логику, например, обновление поискового индекса
        elif event_name == "note.deleted":
            event = NoteDeletedEvent(**payload)
            self.logger.info("Processing note.deleted event", note_id=str(event.id))
            # TODO: Добавить логику, например, удаление из внешних систем
        else:
            self.logger.warning("Unknown event", event_name=event_name)
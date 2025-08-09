from domain.ports.inbound.event_handler import EventHandlerPort
from domain.ports.outbound.logger.logger_port import LoggerPort


class NoteEventHandler(EventHandlerPort):
    def __init__(self, logger: LoggerPort):
        self.logger = logger.bind(component="NoteEventHandler")

    async def handle_event(self, event_name: str, payload: dict):
        self.logger.info("Handling event", event_name=event_name, payload=payload)
        if event_name == "note.created":
            self.logger.info("Processing note.created event", note_id=payload.get("id"))
            # Example: Notify external system or update metrics
            # Add logic here, e.g., send to analytics service
        else:
            self.logger.warning("Unknown event", event_name=event_name)
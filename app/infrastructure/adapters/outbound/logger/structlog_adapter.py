import structlog
from domain.ports.outbound.logger.logger_port import LoggerPort


class StructlogAdapter(LoggerPort):
    def __init__(self, logger=None):
        self._logger = logger or structlog.get_logger()

    def bind(self, **kwargs) -> LoggerPort:
        return StructlogAdapter(self._logger.bind(**kwargs))

    def info(self, message: str, **kwargs) -> None:
        self._logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        self._logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self._logger.error(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        self._logger.exception(message, **kwargs)

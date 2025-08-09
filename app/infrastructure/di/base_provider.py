from dishka import Provider, Scope, provide
from domain.ports.outbound.logger.logger_port import LoggerPort
from infrastructure.adapters.outbound.logger.structlog_adapter import StructlogAdapter
from infrastructure.adapters.outbound.logger import configure_structlog


class BaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_logger(self) -> LoggerPort:
        configure_structlog()
        logger = StructlogAdapter()
        logger.info("Logger initialized")
        return logger
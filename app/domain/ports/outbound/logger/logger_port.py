# domain/ports/logger_port.py
from abc import ABC, abstractmethod

class LoggerPort(ABC):
    @abstractmethod
    def bind(self, **kwargs) -> "LoggerPort":
        ...

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        ...

    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        ...

    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        ...

    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        ...

    @abstractmethod
    def exception(self, message: str, **kwargs) -> None:
        ...

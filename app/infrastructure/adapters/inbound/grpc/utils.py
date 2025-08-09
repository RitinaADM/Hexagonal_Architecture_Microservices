from functools import wraps
import time
import grpc
from domain.ports.outbound.logger.logger_port import LoggerPort
from domain.exceptions import (
    NotFoundError, AccessDeniedError, AuthenticationError, LimitExceededError, DatabaseException
)

def log_execution_time(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = await func(self, *args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger: LoggerPort = self.logger.bind(endpoint=func.__name__)
        logger.info(f"Execution time for {func.__name__}: {duration:.3f} seconds")
        return result
    return wrapper

def async_handle_grpc_exceptions(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except ValueError as e:
            await args[1].abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except NotFoundError as e:
            await args[1].abort(grpc.StatusCode.NOT_FOUND, str(e))
        except AccessDeniedError as e:
            await args[1].abort(grpc.StatusCode.PERMISSION_DENIED, str(e))
        except AuthenticationError as e:
            await args[1].abort(grpc.StatusCode.UNAUTHENTICATED, str(e))
        except LimitExceededError as e:
            await args[1].abort(grpc.StatusCode.RESOURCE_EXHAUSTED, str(e))
        except DatabaseException as e:
            await args[1].abort(grpc.StatusCode.INTERNAL, str(e))
        except Exception as e:
            self.logger.exception(f"Unexpected error in {func.__name__}", error=str(e))
            await args[1].abort(grpc.StatusCode.INTERNAL, "Internal server error")
    return wrapper
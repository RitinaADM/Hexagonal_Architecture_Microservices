import uuid
import grpc
from domain.exceptions.auth import AuthenticationError
from domain.ports.outbound.logger.logger_port import LoggerPort
from domain.ports.outbound.security.auth_port import AuthPort
from typing import Callable, Any, Awaitable
import structlog.contextvars

class AuthInterceptor(grpc.aio.ServerInterceptor):
    def __init__(self, auth: AuthPort, logger: LoggerPort):
        self.auth = auth
        self.logger = logger.bind(component="AuthInterceptor")
        self._excluded_methods = {"/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo"}

    async def intercept_service(
        self,
        continuation: Callable[[Any], Awaitable[Any]],
        handler_call_details: grpc.HandlerCallDetails
    ) -> Any:
        method = handler_call_details.method
        metadata = dict(handler_call_details.invocation_metadata)
        request_id = metadata.get("request_id", str(uuid.uuid4()))  # Generate request_id if not provided
        logger = self.logger.bind(request_id=request_id, endpoint=method)

        if method in self._excluded_methods:
            logger.debug("Skipping auth for reflection endpoint")
            return await continuation(handler_call_details)

        token = metadata.get("authorization", "").replace("Bearer ", "")
        if not token:
            logger.error("No token provided", metadata=metadata)
            raise grpc.RpcError(grpc.StatusCode.UNAUTHENTICATED, "No token provided")

        try:
            user_id, role = self.auth.verify_token(token)
            logger.debug(f"Token verified, user_id={user_id}, role={role}")
            # Set context variables for the servicer
            structlog.contextvars.bind_contextvars(
                user_id=str(user_id),
                role=role,
                request_id=request_id
            )
            try:
                result = await continuation(handler_call_details)
                return result
            finally:
                structlog.contextvars.clear_contextvars()
        except AuthenticationError as e:
            logger.error("Authentication failed", error=str(e), metadata=metadata)
            raise grpc.RpcError(grpc.StatusCode.UNAUTHENTICATED, str(e))
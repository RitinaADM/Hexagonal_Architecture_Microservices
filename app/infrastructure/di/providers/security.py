from dishka import Provider, Scope, provide
from domain.ports.outbound.security.auth_port import AuthPort
from domain.ports.outbound.logger.logger_port import LoggerPort
from infrastructure.adapters.outbound.security.jwt_adapter import JWTAuthAdapter

class SecurityProvider(Provider):
    @provide(scope=Scope.APP)
    def get_auth(self, logger: LoggerPort) -> AuthPort:
        logger = logger.bind(component="SecurityProvider")
        logger.info("JWT auth adapter initialized")
        return JWTAuthAdapter(logger)
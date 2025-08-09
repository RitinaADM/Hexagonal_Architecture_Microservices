from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    pythonioencoding: str = Field(..., env="PYTHONIOENCODING")
    mongo_uri: str = Field(..., env="MONGO_URI")
    mongo_db: str = Field("task_service", env="MONGO_DB")
    mongo_uuid_representation: str = Field("standard", env="MONGO_UUID_REPRESENTATION")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY", min_length=32)
    grpc_port: int = Field(50051, env="GRPC_PORT")
    rest_port: int = Field(8000, env="REST_PORT")
    redis_uri: str = Field("redis://redis:6379/0", env="REDIS_URI")
    redis_ttl: int = Field(3600, env="REDIS_TTL")
    max_docs_per_user: int = Field(1, env="MAX_DOCS_PER_USER", ge=1)
    rabbitmq_uri: str = Field("amqp://guest:guest@localhost/", env="RABBITMQ_URI")
    rabbit_exchange_name: str = Field("events", env="RABBIT_EXCHANGE_NAME")  # Added

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
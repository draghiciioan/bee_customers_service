import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "BeeConect Customer Service"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "Customer management service for BeeConect platform"

    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/bee_customers"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def ensure_async_driver(cls, v: str) -> str:
        """Ensure PostgreSQL URLs use the asyncpg driver."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # JWT settings for authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    # External services
    AUTH_SERVICE_URL: Optional[str] = os.getenv(
        "AUTH_SERVICE_URL", "http://localhost:8001"
    )
    ORDERS_SERVICE_URL: Optional[str] = os.getenv(
        "ORDERS_SERVICE_URL", "http://localhost:8002"
    )
    SCHEDULING_SERVICE_URL: Optional[str] = os.getenv(
        "SCHEDULING_SERVICE_URL", "http://localhost:8003"
    )
    LOG_SERVICE_URL: Optional[str] = os.getenv("LOG_SERVICE_URL")

    # Rate limiting
    CUSTOMER_PATCH_RATE: str = os.getenv("CUSTOMER_PATCH_RATE", "5/minute")

    # RabbitMQ settings
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RABBITMQ_EXCHANGE: str = "bee.customers.events"

    # Redis settings for local queueing
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

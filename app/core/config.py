import os
from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "BeeConect Customer Service"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "Customer management service for BeeConect platform"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bee_customers")
    
    # JWT settings for authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    
    # External services
    AUTH_SERVICE_URL: Optional[str] = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    ORDERS_SERVICE_URL: Optional[str] = os.getenv("ORDERS_SERVICE_URL", "http://localhost:8002")
    SCHEDULING_SERVICE_URL: Optional[str] = os.getenv("SCHEDULING_SERVICE_URL", "http://localhost:8003")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

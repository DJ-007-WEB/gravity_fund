from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Gravity Fund"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "test", "production"] = "development"
    DEBUG: bool = False
    
    # Database configuration
    DATABASE_URL: str
    
    # Redis configuration
    REDIS_URL: str
    
    # Authentication settings
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Read environment variables from a .env file
    model_config = SettingsConfigDict(
        # Supports running either from backend/ or the repository root.
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8", 
        case_sensitive=True
    )


settings = Settings()

"""
Configuration settings for Brahma Blueprint Engine
"""

from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    """
    Brahma Blueprint Engine Configuration
    """
    
    # Application settings
    APP_NAME: str = Field(default="Brahma Blueprint Engine", env="APP_NAME")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8001, env="PORT")
    
    # Database settings
    DATABASE_URL: str = Field(
        default=(
            "postgresql://postgres:${POSTGRES_PASSWORD}@"
            "localhost:5432/aetheredge"
        ),
        env="DATABASE_URL"
    )
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # AI/ML settings
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    AI_MODEL_PATH: str = Field(default="./models", env="AI_MODEL_PATH")
    
    # Template repository
    TEMPLATE_REPO_PATH: str = Field(default="./templates", env="TEMPLATE_REPO_PATH")  # noqa: E501
    
    # Cache settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

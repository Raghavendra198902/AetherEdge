"""
Configuration settings for Shiva Healer Engine
"""

from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    """
    Shiva Healer Engine Configuration
    """
    
    # Application settings
    APP_NAME: str = Field(default="Shiva Healer Engine", env="APP_NAME")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8003, env="PORT")
    
    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://postgres:changeme@localhost:5432/aetheredge",
        env="DATABASE_URL"
    )
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # ML/AI settings
    ML_MODEL_PATH: str = Field(default="./models", env="ML_MODEL_PATH")
    HEALING_MODEL_ENDPOINT: str = Field(default="", env="HEALING_MODEL_ENDPOINT")
    
    # Monitoring settings
    PROMETHEUS_URL: str = Field(default="http://localhost:9090", env="PROMETHEUS_URL")  # noqa: E501
    GRAFANA_URL: str = Field(default="http://localhost:3000", env="GRAFANA_URL")
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200", env="ELASTICSEARCH_URL")  # noqa: E501
    
    # Auto-healing settings
    AUTO_HEALING_ENABLED: bool = Field(default=True, env="AUTO_HEALING_ENABLED")
    MAX_HEALING_ATTEMPTS: int = Field(default=3, env="MAX_HEALING_ATTEMPTS")
    HEALING_TIMEOUT_SECONDS: int = Field(default=300, env="HEALING_TIMEOUT_SECONDS")  # noqa: E501
    
    # Cache settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

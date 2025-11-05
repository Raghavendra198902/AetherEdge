"""
Configuration settings for AetherEdge API

Manages all configuration settings using Pydantic BaseSettings
for type validation and environment variable loading.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "AetherEdge Platform API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")
    
    # Security
    API_TOKEN: str = Field(default="dev-token-change-in-production", description="API authentication token")
    SECRET_KEY: str = Field(default="change-this-secret-key-in-production", description="Secret key for signing")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration")
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"], description="Allowed hosts")
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000"], description="CORS allowed origins")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://aetheredge:password@localhost:5432/aetheredge",
        description="Database connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_CACHE_TTL: int = Field(default=300, description="Redis cache TTL in seconds")
    
    # Monitoring
    PROMETHEUS_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    JAEGER_AGENT_HOST: str = Field(default="localhost", description="Jaeger agent host")
    JAEGER_AGENT_PORT: int = Field(default=6831, description="Jaeger agent port")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per minute")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # External Services
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200", description="Elasticsearch URL")
    MINIO_ENDPOINT: str = Field(default="localhost:9000", description="MinIO endpoint")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="MinIO access key")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", description="MinIO secret key")
    
    # Module Settings
    BRAHMA_ENABLED: bool = Field(default=True, description="Enable Brahma module")
    VISHNU_ENABLED: bool = Field(default=True, description="Enable Vishnu module")
    SHIVA_ENABLED: bool = Field(default=True, description="Enable Shiva module")
    LAKSHMI_ENABLED: bool = Field(default=True, description="Enable Lakshmi module")
    KALI_ENABLED: bool = Field(default=True, description="Enable Kali module")
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting"""
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be one of: development, staging, production")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level setting"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Environment-specific configurations
def get_database_url() -> str:
    """Get database URL based on environment"""
    if settings.ENVIRONMENT == "test":
        return "sqlite:///./test.db"
    return settings.DATABASE_URL


def get_redis_url() -> str:
    """Get Redis URL based on environment"""
    if settings.ENVIRONMENT == "test":
        return "redis://localhost:6379/1"
    return settings.REDIS_URL


def is_production() -> bool:
    """Check if running in production environment"""
    return settings.ENVIRONMENT == "production"


def is_development() -> bool:
    """Check if running in development environment"""
    return settings.ENVIRONMENT == "development"

"""
🎯 Saraswati Knowledge Engine Configuration
==========================================

Configuration settings for the divine knowledge management system.
Saraswati, the goddess of knowledge and wisdom, manages organizational intelligence.
"""

import os
from pydantic import BaseSettings, Field
from typing import List, Optional


class Settings(BaseSettings):
    """Configuration settings for Saraswati Knowledge Engine"""
    
    # Service Configuration
    SERVICE_NAME: str = "saraswati-knowledge"
    HOST: str = Field(default="0.0.0.0", env="SARASWATI_HOST")
    PORT: int = Field(default=8084, env="SARASWATI_PORT")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://saraswati_user:${POSTGRES_PASSWORD}@postgres:5432/saraswati_knowledge",
        env="SARASWATI_DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Knowledge Management
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    VECTOR_DIMENSIONS: int = Field(default=384, env="VECTOR_DIMENSIONS")
    SIMILARITY_THRESHOLD: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    MAX_SEARCH_RESULTS: int = Field(default=50, env="MAX_SEARCH_RESULTS")
    
    # Document Processing
    MAX_DOCUMENT_SIZE_MB: int = Field(default=50, env="MAX_DOCUMENT_SIZE_MB")
    SUPPORTED_FORMATS: List[str] = Field(
        default=["pdf", "docx", "txt", "md", "html", "json", "yaml"],
        env="SUPPORTED_FORMATS"
    )
    CHUNK_SIZE: int = Field(default=1000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # AI/ML Configuration
    LLM_MODEL: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL")
    LLM_API_KEY: str = Field(default="", env="LLM_API_KEY")
    LLM_MAX_TOKENS: int = Field(default=4000, env="LLM_MAX_TOKENS")
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    
    # Search & Indexing
    ELASTICSEARCH_URL: str = Field(default="http://elasticsearch:9200", env="ELASTICSEARCH_URL")
    INDEX_PREFIX: str = Field(default="saraswati", env="INDEX_PREFIX")
    REFRESH_INTERVAL: str = Field(default="5s", env="REFRESH_INTERVAL")
    
    # Caching
    REDIS_URL: str = Field(default="redis://redis:6379/4", env="REDIS_URL")
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    # Security
    JWT_SECRET_KEY: str = Field(default="${API_SECRET_KEY}", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Knowledge Categories
    KNOWLEDGE_CATEGORIES: List[str] = Field(
        default=[
            "documentation", "runbooks", "procedures", "troubleshooting",
            "architecture", "policies", "compliance", "training",
            "best_practices", "lessons_learned", "incident_reports"
        ],
        env="KNOWLEDGE_CATEGORIES"
    )
    
    # Quality Assurance
    AUTO_CATEGORIZE: bool = Field(default=True, env="AUTO_CATEGORIZE")
    QUALITY_SCORE_THRESHOLD: float = Field(default=0.8, env="QUALITY_SCORE_THRESHOLD")
    ENABLE_VERSION_CONTROL: bool = Field(default=True, env="ENABLE_VERSION_CONTROL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get database URL with secret expansion"""
    db_url = settings.DATABASE_URL
    
    # Replace secret placeholders with actual values
    if "${POSTGRES_PASSWORD}" in db_url:
        try:
            with open("/run/secrets/postgres_password", "r") as f:
                password = f.read().strip()
            db_url = db_url.replace("${POSTGRES_PASSWORD}", password)
        except FileNotFoundError:
            # Fallback to environment variable in development
            password = os.getenv("POSTGRES_PASSWORD", "defaultpassword")
            db_url = db_url.replace("${POSTGRES_PASSWORD}", password)
    
    return db_url


def get_jwt_secret() -> str:
    """Get JWT secret with secret expansion"""
    secret = settings.JWT_SECRET_KEY
    
    # Replace secret placeholders with actual values
    if "${API_SECRET_KEY}" in secret:
        try:
            with open("/run/secrets/api_secret_key", "r") as f:
                api_key = f.read().strip()
            secret = secret.replace("${API_SECRET_KEY}", api_key)
        except FileNotFoundError:
            # Fallback to environment variable in development
            api_key = os.getenv("API_SECRET_KEY", "default-secret-key")
            secret = secret.replace("${API_SECRET_KEY}", api_key)
    
    return secret

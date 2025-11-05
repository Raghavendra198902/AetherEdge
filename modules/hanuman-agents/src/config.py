"""
🐒 Hanuman Agents Engine Configuration
=====================================

Configuration settings for the divine agent management system.
Hanuman, the devoted messenger, coordinates intelligent automation agents.
"""

import os
from pydantic import BaseSettings, Field
from typing import List, Optional


class Settings(BaseSettings):
    """Configuration settings for Hanuman Agents Engine"""
    
    # Service Configuration
    SERVICE_NAME: str = "hanuman-agents"
    HOST: str = Field(default="0.0.0.0", env="HANUMAN_HOST")
    PORT: int = Field(default=8087, env="HANUMAN_PORT")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://hanuman_user:${POSTGRES_PASSWORD}@postgres:5432/hanuman_agents",
        env="HANUMAN_DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Agent Management
    MAX_CONCURRENT_AGENTS: int = Field(default=100, env="MAX_CONCURRENT_AGENTS")
    AGENT_HEARTBEAT_INTERVAL: int = Field(default=30, env="AGENT_HEARTBEAT_INTERVAL")
    AGENT_TIMEOUT_SECONDS: int = Field(default=300, env="AGENT_TIMEOUT_SECONDS")
    AUTO_SCALING_ENABLED: bool = Field(default=True, env="AUTO_SCALING_ENABLED")
    
    # Task Orchestration
    TASK_QUEUE_SIZE: int = Field(default=1000, env="TASK_QUEUE_SIZE")
    TASK_RETRY_ATTEMPTS: int = Field(default=3, env="TASK_RETRY_ATTEMPTS")
    TASK_TIMEOUT_MINUTES: int = Field(default=60, env="TASK_TIMEOUT_MINUTES")
    PRIORITY_LEVELS: int = Field(default=5, env="PRIORITY_LEVELS")
    
    # Agent Types
    SUPPORTED_AGENT_TYPES: List[str] = Field(
        default=[
            "monitoring", "deployment", "maintenance", "backup",
            "security", "compliance", "cost_optimization", "troubleshooting"
        ],
        env="SUPPORTED_AGENT_TYPES"
    )
    
    # Communication
    MESSAGE_BROKER_URL: str = Field(default="redis://redis:6379/7", env="MESSAGE_BROKER_URL")
    WEBSOCKET_ENABLED: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    AGENT_COMMUNICATION_PROTOCOL: str = Field(default="websocket", env="AGENT_COMMUNICATION_PROTOCOL")
    
    # Security
    AGENT_AUTHENTICATION: bool = Field(default=True, env="AGENT_AUTHENTICATION")
    SECURE_COMMUNICATION: bool = Field(default=True, env="SECURE_COMMUNICATION")
    JWT_SECRET_KEY: str = Field(default="${API_SECRET_KEY}", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # Monitoring & Telemetry
    METRICS_COLLECTION: bool = Field(default=True, env="METRICS_COLLECTION")
    PERFORMANCE_MONITORING: bool = Field(default=True, env="PERFORMANCE_MONITORING")
    LOG_AGGREGATION: bool = Field(default=True, env="LOG_AGGREGATION")
    
    # Automation Workflows
    WORKFLOW_ENGINE: bool = Field(default=True, env="WORKFLOW_ENGINE")
    PARALLEL_EXECUTION: bool = Field(default=True, env="PARALLEL_EXECUTION")
    DEPENDENCY_RESOLUTION: bool = Field(default=True, env="DEPENDENCY_RESOLUTION")
    
    # Caching
    REDIS_URL: str = Field(default="redis://redis:6379/7", env="REDIS_URL")
    CACHE_TTL_SECONDS: int = Field(default=300, env="CACHE_TTL_SECONDS")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Integration
    KUBERNETES_ENABLED: bool = Field(default=True, env="KUBERNETES_ENABLED")
    DOCKER_ENABLED: bool = Field(default=True, env="DOCKER_ENABLED")
    ANSIBLE_INTEGRATION: bool = Field(default=True, env="ANSIBLE_INTEGRATION")
    TERRAFORM_INTEGRATION: bool = Field(default=True, env="TERRAFORM_INTEGRATION")
    
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

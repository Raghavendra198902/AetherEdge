"""
Configuration settings for Vishnu Orchestrator Engine
"""

from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    """
    Vishnu Orchestrator Engine Configuration
    """
    
    # Application settings
    APP_NAME: str = Field(default="Vishnu Orchestrator Engine", env="APP_NAME")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8002, env="PORT")
    
    # Database settings
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="vishnu_db", env="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(
        default="/run/secrets/postgres_password",
        env="POSTGRES_PASSWORD"
    )
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Kubernetes settings
    KUBERNETES_CONFIG_PATH: str = Field(default="~/.kube/config", env="KUBERNETES_CONFIG_PATH")  # noqa: E501
    KUBERNETES_NAMESPACE: str = Field(default="aetheredge", env="KUBERNETES_NAMESPACE")  # noqa: E501
    
    # Policy engine settings
    POLICY_ENGINE: str = Field(default="opa", env="POLICY_ENGINE")
    OPA_URL: str = Field(default="http://localhost:8181", env="OPA_URL")
    
    # Workflow orchestrator
    WORKFLOW_ENGINE: str = Field(default="argo", env="WORKFLOW_ENGINE")
    ARGO_WORKFLOWS_URL: str = Field(default="http://localhost:2746", env="ARGO_WORKFLOWS_URL")  # noqa: E501
    
    # Cache settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

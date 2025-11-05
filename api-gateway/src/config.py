"""
Configuration settings for Indra Divine API Gateway
"""

from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    """
    Divine Gateway Configuration
    """
    
    # Application settings
    APP_NAME: str = Field(default="Indra Divine Gateway", env="APP_NAME")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security settings
    SECRET_KEY: str = Field(
        default="please-change-this-secret-key-in-production-use-32-byte-random-string", 
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, 
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"],
        env="ALLOWED_HOSTS"
    )
    
    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://postgres:changeme@localhost:5432/aetheredge",
        env="DATABASE_URL"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Service ports
    BRAHMA_PORT: int = Field(default=8001, env="BRAHMA_PORT")
    VISHNU_PORT: int = Field(default=8002, env="VISHNU_PORT")
    SHIVA_PORT: int = Field(default=8003, env="SHIVA_PORT")
    SARASWATI_PORT: int = Field(default=8004, env="SARASWATI_PORT")
    LAKSHMI_PORT: int = Field(default=8005, env="LAKSHMI_PORT")
    KALI_PORT: int = Field(default=8006, env="KALI_PORT")
    HANUMAN_PORT: int = Field(default=8007, env="HANUMAN_PORT")
    GANESHA_PORT: int = Field(default=8008, env="GANESHA_PORT")
    
    # External service URLs
    BRAHMA_SERVICE_URL: str = Field(default="http://localhost:8001", env="BRAHMA_SERVICE_URL")
    VISHNU_SERVICE_URL: str = Field(default="http://localhost:8002", env="VISHNU_SERVICE_URL")
    SHIVA_SERVICE_URL: str = Field(default="http://localhost:8003", env="SHIVA_SERVICE_URL")
    SARASWATI_SERVICE_URL: str = Field(default="http://localhost:8004", env="SARASWATI_SERVICE_URL")
    LAKSHMI_SERVICE_URL: str = Field(default="http://localhost:8005", env="LAKSHMI_SERVICE_URL")
    KALI_SERVICE_URL: str = Field(default="http://localhost:8006", env="KALI_SERVICE_URL")
    HANUMAN_SERVICE_URL: str = Field(default="http://localhost:8007", env="HANUMAN_SERVICE_URL")
    GANESHA_SERVICE_URL: str = Field(default="http://localhost:8008", env="GANESHA_SERVICE_URL")
    
    # Monitoring settings
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Vault settings
    VAULT_URL: str = Field(default="http://localhost:8200", env="VAULT_URL")
    VAULT_TOKEN: str = Field(default="", env="VAULT_TOKEN")
    
    # Kubernetes settings (when deployed in K8s)
    KUBERNETES_NAMESPACE: str = Field(default="aetheredge", env="KUBERNETES_NAMESPACE")
    SERVICE_ACCOUNT_TOKEN_PATH: str = Field(
        default="/var/run/secrets/kubernetes.io/serviceaccount/token",
        env="SERVICE_ACCOUNT_TOKEN_PATH"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

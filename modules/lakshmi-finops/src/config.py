"""
💰 Lakshmi FinOps Engine Configuration
=====================================

Configuration settings for the divine financial operations system.
Lakshmi, the goddess of wealth and prosperity, manages cost optimization.
"""

import os
from pydantic import BaseSettings, Field
from typing import List, Optional, Dict


class Settings(BaseSettings):
    """Configuration settings for Lakshmi FinOps Engine"""
    
    # Service Configuration
    SERVICE_NAME: str = "lakshmi-finops"
    HOST: str = Field(default="0.0.0.0", env="LAKSHMI_HOST")
    PORT: int = Field(default=8085, env="LAKSHMI_PORT")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://lakshmi_user:${POSTGRES_PASSWORD}@postgres:5432/lakshmi_finops",
        env="LAKSHMI_DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Cloud Provider APIs
    AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    
    AZURE_CLIENT_ID: str = Field(default="", env="AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET: str = Field(default="", env="AZURE_CLIENT_SECRET")
    AZURE_TENANT_ID: str = Field(default="", env="AZURE_TENANT_ID")
    AZURE_SUBSCRIPTION_ID: str = Field(default="", env="AZURE_SUBSCRIPTION_ID")
    
    GCP_PROJECT_ID: str = Field(default="", env="GCP_PROJECT_ID")
    GCP_SERVICE_ACCOUNT_KEY: str = Field(default="", env="GCP_SERVICE_ACCOUNT_KEY")
    
    # Cost Management
    COST_UPDATE_INTERVAL_HOURS: int = Field(default=6, env="COST_UPDATE_INTERVAL_HOURS")
    COST_THRESHOLD_WARNING: float = Field(default=80.0, env="COST_THRESHOLD_WARNING")
    COST_THRESHOLD_CRITICAL: float = Field(default=95.0, env="COST_THRESHOLD_CRITICAL")
    CURRENCY: str = Field(default="USD", env="CURRENCY")
    
    # Budget Management
    AUTO_BUDGET_ALERTS: bool = Field(default=True, env="AUTO_BUDGET_ALERTS")
    BUDGET_VARIANCE_THRESHOLD: float = Field(default=10.0, env="BUDGET_VARIANCE_THRESHOLD")
    DEFAULT_BUDGET_PERIOD: str = Field(default="monthly", env="DEFAULT_BUDGET_PERIOD")
    
    # Optimization
    AUTO_OPTIMIZATION: bool = Field(default=False, env="AUTO_OPTIMIZATION")
    OPTIMIZATION_SCHEDULE: str = Field(default="0 2 * * *", env="OPTIMIZATION_SCHEDULE")
    MIN_SAVINGS_THRESHOLD: float = Field(default=5.0, env="MIN_SAVINGS_THRESHOLD")
    
    # Recommendations
    RECOMMENDATION_ENGINE: bool = Field(default=True, env="RECOMMENDATION_ENGINE")
    ML_MODEL_PATH: str = Field(default="/models/cost_optimization", env="ML_MODEL_PATH")
    RECOMMENDATION_CONFIDENCE_THRESHOLD: float = Field(default=0.8, env="RECOMMENDATION_CONFIDENCE_THRESHOLD")
    
    # Reporting
    REPORT_GENERATION_SCHEDULE: str = Field(default="0 8 * * 1", env="REPORT_GENERATION_SCHEDULE")
    REPORT_RETENTION_DAYS: int = Field(default=90, env="REPORT_RETENTION_DAYS")
    AUTO_REPORT_DISTRIBUTION: bool = Field(default=True, env="AUTO_REPORT_DISTRIBUTION")
    
    # Caching
    REDIS_URL: str = Field(default="redis://redis:6379/5", env="REDIS_URL")
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
    
    # Cost Categories
    COST_CATEGORIES: List[str] = Field(
        default=[
            "compute", "storage", "networking", "database", "security",
            "monitoring", "backup", "analytics", "machine_learning", "other"
        ],
        env="COST_CATEGORIES"
    )
    
    # Alert Channels
    SLACK_WEBHOOK_URL: str = Field(default="", env="SLACK_WEBHOOK_URL")
    EMAIL_SMTP_SERVER: str = Field(default="", env="EMAIL_SMTP_SERVER")
    EMAIL_SMTP_PORT: int = Field(default=587, env="EMAIL_SMTP_PORT")
    EMAIL_USERNAME: str = Field(default="", env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field(default="", env="EMAIL_PASSWORD")
    
    # Forecasting
    FORECASTING_HORIZON_DAYS: int = Field(default=90, env="FORECASTING_HORIZON_DAYS")
    FORECASTING_MODEL: str = Field(default="prophet", env="FORECASTING_MODEL")
    SEASONALITY_DETECTION: bool = Field(default=True, env="SEASONALITY_DETECTION")
    
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


# Cloud Provider Configuration
def get_aws_config() -> Dict[str, str]:
    """Get AWS configuration"""
    return {
        "access_key_id": settings.AWS_ACCESS_KEY_ID,
        "secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
        "region": settings.AWS_REGION
    }


def get_azure_config() -> Dict[str, str]:
    """Get Azure configuration"""
    return {
        "client_id": settings.AZURE_CLIENT_ID,
        "client_secret": settings.AZURE_CLIENT_SECRET,
        "tenant_id": settings.AZURE_TENANT_ID,
        "subscription_id": settings.AZURE_SUBSCRIPTION_ID
    }


def get_gcp_config() -> Dict[str, str]:
    """Get GCP configuration"""
    return {
        "project_id": settings.GCP_PROJECT_ID,
        "service_account_key": settings.GCP_SERVICE_ACCOUNT_KEY
    }

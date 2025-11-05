"""
🔱 Kali Security Engine Configuration
====================================

Configuration settings for the divine security and protection system.
Kali, the fierce goddess of protection, guards against all threats.
"""

import os
from pydantic import BaseSettings, Field
from typing import List, Optional


class Settings(BaseSettings):
    """Configuration settings for Kali Security Engine"""
    
    # Service Configuration
    SERVICE_NAME: str = "kali-security"
    HOST: str = Field(default="0.0.0.0", env="KALI_HOST")
    PORT: int = Field(default=8086, env="KALI_PORT")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://kali_user:${POSTGRES_PASSWORD}@postgres:5432/kali_security",
        env="KALI_DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Security Scanning
    VULNERABILITY_SCAN_INTERVAL: int = Field(default=24, env="VULNERABILITY_SCAN_INTERVAL")
    THREAT_DETECTION_SENSITIVITY: str = Field(default="high", env="THREAT_DETECTION_SENSITIVITY")
    AUTO_REMEDIATION: bool = Field(default=False, env="AUTO_REMEDIATION")
    QUARANTINE_ENABLED: bool = Field(default=True, env="QUARANTINE_ENABLED")
    
    # Threat Intelligence
    THREAT_INTEL_FEEDS: List[str] = Field(
        default=["cisa", "mitre", "nist", "owasp"],
        env="THREAT_INTEL_FEEDS"
    )
    THREAT_SCORE_THRESHOLD: float = Field(default=7.0, env="THREAT_SCORE_THRESHOLD")
    IOC_RETENTION_DAYS: int = Field(default=365, env="IOC_RETENTION_DAYS")
    
    # Compliance Frameworks
    COMPLIANCE_FRAMEWORKS: List[str] = Field(
        default=["ISO27001", "SOC2", "PCI-DSS", "GDPR", "HIPAA"],
        env="COMPLIANCE_FRAMEWORKS"
    )
    COMPLIANCE_SCAN_SCHEDULE: str = Field(default="0 2 * * *", env="COMPLIANCE_SCAN_SCHEDULE")
    
    # Incident Response
    INCIDENT_AUTO_CLASSIFICATION: bool = Field(default=True, env="INCIDENT_AUTO_CLASSIFICATION")
    INCIDENT_ESCALATION_THRESHOLD: int = Field(default=8, env="INCIDENT_ESCALATION_THRESHOLD")
    MAX_INCIDENT_AGE_HOURS: int = Field(default=72, env="MAX_INCIDENT_AGE_HOURS")
    
    # Security Monitoring
    SIEM_INTEGRATION: bool = Field(default=True, env="SIEM_INTEGRATION")
    LOG_RETENTION_DAYS: int = Field(default=90, env="LOG_RETENTION_DAYS")
    ALERT_CORRELATION_WINDOW: int = Field(default=300, env="ALERT_CORRELATION_WINDOW")
    
    # Network Security
    FIREWALL_MANAGEMENT: bool = Field(default=True, env="FIREWALL_MANAGEMENT")
    IDS_IPS_ENABLED: bool = Field(default=True, env="IDS_IPS_ENABLED")
    NETWORK_SEGMENTATION: bool = Field(default=True, env="NETWORK_SEGMENTATION")
    
    # Identity & Access Management
    MFA_ENFORCEMENT: bool = Field(default=True, env="MFA_ENFORCEMENT")
    PRIVILEGED_ACCESS_MONITORING: bool = Field(default=True, env="PRIVILEGED_ACCESS_MONITORING")
    ACCESS_REVIEW_SCHEDULE: str = Field(default="0 0 1 * *", env="ACCESS_REVIEW_SCHEDULE")
    
    # Encryption & Data Protection
    ENCRYPTION_AT_REST: bool = Field(default=True, env="ENCRYPTION_AT_REST")
    ENCRYPTION_IN_TRANSIT: bool = Field(default=True, env="ENCRYPTION_IN_TRANSIT")
    KEY_ROTATION_DAYS: int = Field(default=90, env="KEY_ROTATION_DAYS")
    
    # Caching
    REDIS_URL: str = Field(default="redis://redis:6379/6", env="REDIS_URL")
    CACHE_TTL_SECONDS: int = Field(default=300, env="CACHE_TTL_SECONDS")
    
    # Security
    JWT_SECRET_KEY: str = Field(default="${API_SECRET_KEY}", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Security Categories
    SECURITY_CATEGORIES: List[str] = Field(
        default=[
            "vulnerability", "malware", "intrusion", "data_breach",
            "policy_violation", "compliance", "insider_threat", "ddos",
            "phishing", "ransomware", "lateral_movement", "privilege_escalation"
        ],
        env="SECURITY_CATEGORIES"
    )
    
    # Alert Channels
    SLACK_WEBHOOK_URL: str = Field(default="", env="SLACK_WEBHOOK_URL")
    EMAIL_SMTP_SERVER: str = Field(default="", env="EMAIL_SMTP_SERVER")
    EMAIL_SMTP_PORT: int = Field(default=587, env="EMAIL_SMTP_PORT")
    EMAIL_USERNAME: str = Field(default="", env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field(default="", env="EMAIL_PASSWORD")
    
    # Integration APIs
    CROWDSTRIKE_API_KEY: str = Field(default="", env="CROWDSTRIKE_API_KEY")
    SENTINEL_ONE_API_KEY: str = Field(default="", env="SENTINEL_ONE_API_KEY")
    QUALYS_API_KEY: str = Field(default="", env="QUALYS_API_KEY")
    TENABLE_API_KEY: str = Field(default="", env="TENABLE_API_KEY")
    
    # Machine Learning
    ML_THREAT_DETECTION: bool = Field(default=True, env="ML_THREAT_DETECTION")
    ANOMALY_DETECTION_MODEL: str = Field(default="isolation_forest", env="ANOMALY_DETECTION_MODEL")
    BEHAVIOR_ANALYSIS: bool = Field(default=True, env="BEHAVIOR_ANALYSIS")
    
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

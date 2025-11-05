"""
Ganesha RCA Engine Configuration
Sacred wisdom for problem resolution
"""

import os

# Database Configuration
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.getenv("MONGODB_PORT", "27017"))
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "aetheredge")
MONGODB_USER = os.getenv("MONGODB_USER", "aetheredge")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "sacred_password")

# Service Configuration
SERVICE_NAME = "ganesha-rca"
SERVICE_PORT = int(os.getenv("GANESHA_PORT", "8005"))
SERVICE_HOST = os.getenv("GANESHA_HOST", "0.0.0.0")

# API Configuration
API_PREFIX = "/api/v1/ganesha"
API_VERSION = "1.0.0"

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class Config:
    """Configuration class for Ganesha RCA Engine"""
    
    # Database
    MONGODB_HOST = MONGODB_HOST
    MONGODB_PORT = MONGODB_PORT
    MONGODB_DATABASE = MONGODB_DATABASE
    MONGODB_USER = MONGODB_USER
    MONGODB_PASSWORD = MONGODB_PASSWORD
    
    # Service
    SERVICE_NAME = SERVICE_NAME
    SERVICE_PORT = SERVICE_PORT
    SERVICE_HOST = SERVICE_HOST
    
    # API
    API_PREFIX = API_PREFIX
    API_VERSION = API_VERSION
    
    # Environment
    ENVIRONMENT = ENVIRONMENT
    DEBUG = DEBUG
    LOG_LEVEL = LOG_LEVEL


# Global config instance
config = Config()

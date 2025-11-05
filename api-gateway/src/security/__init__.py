"""
🔒 Security Module
==================

Security utilities and middleware for AetherEdge platform.
"""

from .validation import (
    generate_secure_secret_key,
    validate_password_strength,
    validate_database_url,
    validate_cors_origins,
    validate_jwt_configuration,
    security_audit_config,
    log_security_audit,
    get_secure_headers
)

from .headers import (
    SecurityHeadersMiddleware,
    CSRFProtectionMiddleware
)

__all__ = [
    "generate_secure_secret_key",
    "validate_password_strength", 
    "validate_database_url",
    "validate_cors_origins",
    "validate_jwt_configuration",
    "security_audit_config",
    "log_security_audit",
    "get_secure_headers",
    "SecurityHeadersMiddleware",
    "CSRFProtectionMiddleware"
]

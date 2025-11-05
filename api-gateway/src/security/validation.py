"""
🔒 Security Configuration Validation
====================================

Security utilities and configuration validation for AetherEdge platform.
"""

import secrets
import string
import os
import warnings
from typing import List, Dict, Any
import hashlib


def generate_secure_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure secret key
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength according to security best practices
    """
    issues = []
    score = 0
    
    # Length check
    if len(password) < 12:
        issues.append("Password should be at least 12 characters long")
    else:
        score += 1
    
    # Complexity checks
    if not any(c.isupper() for c in password):
        issues.append("Password should contain uppercase letters")
    else:
        score += 1
        
    if not any(c.islower() for c in password):
        issues.append("Password should contain lowercase letters")
    else:
        score += 1
        
    if not any(c.isdigit() for c in password):
        issues.append("Password should contain numbers")
    else:
        score += 1
        
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("Password should contain special characters")
    else:
        score += 1
    
    # Common password checks
    common_passwords = ["password", "123456", "admin", "changeme", "divine_password"]
    if password.lower() in common_passwords:
        issues.append("Password is too common")
        score = 0
    
    strength_level = "weak"
    if score >= 4:
        strength_level = "strong"
    elif score >= 2:
        strength_level = "medium"
    
    return {
        "is_secure": len(issues) == 0,
        "strength": strength_level,
        "score": score,
        "issues": issues
    }


def validate_database_url(db_url: str) -> Dict[str, Any]:
    """
    Validate database URL for security issues
    """
    issues = []
    
    # Check for default/weak passwords
    weak_passwords = ["password", "changeme", "admin", "root", "divine_password"]
    for weak_pass in weak_passwords:
        if weak_pass in db_url.lower():
            issues.append(f"Database URL contains weak password: {weak_pass}")
    
    # Check for unencrypted connections in production
    if "sslmode=disable" in db_url or ("postgresql://" in db_url and "sslmode" not in db_url):
        issues.append("Database connection should use SSL in production")
    
    # Check for localhost in production
    if "localhost" in db_url or "127.0.0.1" in db_url:
        issues.append("Database URL should not use localhost in production")
    
    return {
        "is_secure": len(issues) == 0,
        "issues": issues
    }


def validate_cors_origins(origins: List[str]) -> Dict[str, Any]:
    """
    Validate CORS origins for security
    """
    issues = []
    
    # Check for wildcard origins
    if "*" in origins:
        issues.append("CORS should not allow all origins (*) in production")
    
    # Check for localhost in production
    localhost_origins = [origin for origin in origins if "localhost" in origin or "127.0.0.1" in origin]
    if localhost_origins and os.getenv("ENVIRONMENT", "").lower() == "production":
        issues.append(f"CORS should not include localhost origins in production: {localhost_origins}")
    
    # Check for HTTP origins in production
    http_origins = [origin for origin in origins if origin.startswith("http://")]
    if http_origins and os.getenv("ENVIRONMENT", "").lower() == "production":
        issues.append(f"CORS should use HTTPS origins in production: {http_origins}")
    
    return {
        "is_secure": len(issues) == 0,
        "issues": issues
    }


def validate_jwt_configuration(secret_key: str, algorithm: str) -> Dict[str, Any]:
    """
    Validate JWT configuration
    """
    issues = []
    
    # Check secret key strength
    if len(secret_key) < 32:
        issues.append("JWT secret key should be at least 32 characters long")
    
    # Check for weak secret keys
    weak_secrets = [
        "divine-secret-key-change-in-production",
        "secret",
        "changeme",
        "please-change-this-secret-key-in-production-use-32-byte-random-string"
    ]
    if secret_key in weak_secrets:
        issues.append("JWT secret key is using a default/weak value")
    
    # Check algorithm security
    weak_algorithms = ["none", "HS256"]  # HS256 is considered weak for some use cases
    if algorithm.lower() in ["none"]:
        issues.append(f"JWT algorithm '{algorithm}' is insecure")
    elif algorithm == "HS256":
        issues.append("Consider using RS256 for better security in distributed systems")
    
    return {
        "is_secure": len(issues) == 0,
        "issues": issues
    }


def security_audit_config(config: Any) -> Dict[str, Any]:
    """
    Perform a comprehensive security audit of application configuration
    """
    audit_results = {
        "overall_secure": True,
        "critical_issues": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Database URL validation
    if hasattr(config, 'DATABASE_URL'):
        db_validation = validate_database_url(config.DATABASE_URL)
        if not db_validation["is_secure"]:
            audit_results["critical_issues"].extend(db_validation["issues"])
            audit_results["overall_secure"] = False
    
    # CORS validation
    if hasattr(config, 'ALLOWED_ORIGINS'):
        cors_validation = validate_cors_origins(config.ALLOWED_ORIGINS)
        if not cors_validation["is_secure"]:
            audit_results["warnings"].extend(cors_validation["issues"])
    
    # JWT validation
    if hasattr(config, 'SECRET_KEY') and hasattr(config, 'ALGORITHM'):
        jwt_validation = validate_jwt_configuration(config.SECRET_KEY, config.ALGORITHM)
        if not jwt_validation["is_secure"]:
            audit_results["critical_issues"].extend(jwt_validation["issues"])
            audit_results["overall_secure"] = False
    
    # Environment checks
    if hasattr(config, 'ENVIRONMENT'):
        if config.ENVIRONMENT.lower() == "production":
            # Production-specific checks
            if hasattr(config, 'DEBUG') and config.DEBUG:
                audit_results["critical_issues"].append("DEBUG should be False in production")
                audit_results["overall_secure"] = False
            
            if hasattr(config, 'docs_url') and config.docs_url:
                audit_results["warnings"].append("API docs should be disabled in production")
    
    # Recommendations
    audit_results["recommendations"].extend([
        "Use environment variables for all sensitive configuration",
        "Implement proper secrets management (e.g., HashiCorp Vault)",
        "Enable TLS/SSL for all external communications",
        "Implement rate limiting and DDoS protection",
        "Use strong authentication and authorization",
        "Enable security headers (HSTS, CSP, etc.)",
        "Implement proper logging and monitoring",
        "Regular security updates and dependency scanning"
    ])
    
    return audit_results


def log_security_audit(audit_results: Dict[str, Any], logger=None):
    """
    Log security audit results
    """
    if logger is None:
        import logging
        logger = logging.getLogger("security_audit")
    
    if not audit_results["overall_secure"]:
        logger.error("❌ SECURITY AUDIT FAILED - Critical issues found:")
        for issue in audit_results["critical_issues"]:
            logger.error(f"  🚨 CRITICAL: {issue}")
    
    if audit_results["warnings"]:
        logger.warning("⚠️  Security warnings:")
        for warning in audit_results["warnings"]:
            logger.warning(f"  ⚠️  {warning}")
    
    if audit_results["overall_secure"]:
        logger.info("✅ Security audit passed - Configuration appears secure")
    
    logger.info("💡 Security recommendations:")
    for rec in audit_results["recommendations"][:5]:  # Show top 5 recommendations
        logger.info(f"  💡 {rec}")


# Security headers middleware configuration
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}


def get_secure_headers() -> Dict[str, str]:
    """
    Get security headers for HTTP responses
    """
    return SECURITY_HEADERS.copy()

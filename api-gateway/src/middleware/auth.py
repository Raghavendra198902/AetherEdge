"""
🛡️ Divine Authentication Middleware
===================================

Authentication and authorization middleware for the Divine API Gateway.
Implements JWT-based authentication with role-based access control.
"""

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

from ..config import settings

logger = logging.getLogger(__name__)

# Divine roles hierarchy
DIVINE_ROLES = {
    "supreme_admin": {
        "level": 10,
        "permissions": ["*"],
        "description": "Supreme Divine Administrator"
    },
    "brahma_admin": {
        "level": 8,
        "permissions": ["brahma:*", "read:*"],
        "description": "Blueprint Creation Administrator"
    },
    "vishnu_admin": {
        "level": 8,
        "permissions": ["vishnu:*", "read:*"],
        "description": "Orchestration Administrator"
    },
    "shiva_admin": {
        "level": 9,
        "permissions": ["shiva:*", "read:*"],
        "description": "Healing & Transformation Administrator"
    },
    "kali_admin": {
        "level": 9,
        "permissions": ["kali:*", "security:*", "read:*"],
        "description": "Security Administrator"
    },
    "operator": {
        "level": 5,
        "permissions": ["read:*", "execute:basic"],
        "description": "System Operator"
    },
    "auditor": {
        "level": 3,
        "permissions": ["read:audit", "read:compliance"],
        "description": "Compliance Auditor"
    },
    "viewer": {
        "level": 1,
        "permissions": ["read:basic"],
        "description": "Read-only Viewer"
    }
}

class TokenData:
    """Token data structure"""
    def __init__(self, username: str, roles: List[str], permissions: List[str]):
        self.username = username
        self.roles = roles
        self.permissions = permissions

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials) -> TokenData:
    """
    Verify JWT token and extract user information
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate divine credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        roles: List[str] = payload.get("roles", [])
        
        if username is None:
            raise credentials_exception
            
        # Calculate permissions based on roles
        permissions = []
        for role in roles:
            if role in DIVINE_ROLES:
                permissions.extend(DIVINE_ROLES[role]["permissions"])
        
        # Remove duplicates
        permissions = list(set(permissions))
        
        token_data = TokenData(
            username=username, 
            roles=roles, 
            permissions=permissions
        )
        
    except JWTError:
        logger.error(f"JWT validation failed for token")
        raise credentials_exception
    
    return token_data

def check_permission(required_permission: str, user_permissions: List[str]) -> bool:
    """
    Check if user has required permission
    """
    # Super admin has all permissions
    if "*" in user_permissions:
        return True
    
    # Check exact match
    if required_permission in user_permissions:
        return True
    
    # Check wildcard permissions
    for permission in user_permissions:
        if permission.endswith(":*"):
            prefix = permission[:-2]
            if required_permission.startswith(prefix + ":"):
                return True
    
    return False

def require_permission(permission: str):
    """
    Decorator to require specific permission
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract credentials from kwargs or request
            credentials = None
            for key, value in kwargs.items():
                if isinstance(value, HTTPAuthorizationCredentials):
                    credentials = value
                    break
            
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            token_data = verify_token(credentials)
            
            if not check_permission(permission, token_data.permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: str):
    """
    Decorator to require specific role
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            credentials = None
            for key, value in kwargs.items():
                if isinstance(value, HTTPAuthorizationCredentials):
                    credentials = value
                    break
            
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            token_data = verify_token(credentials)
            
            if role not in token_data.roles and "supreme_admin" not in token_data.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Audit logging for authentication events
def log_auth_event(event_type: str, username: str, details: Dict = None):
    """
    Log authentication events for audit trail
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "username": username,
        "details": details or {}
    }
    
    logger.info(f"AUTH_EVENT: {log_entry}")
    
    # TODO: Send to audit log storage (ELK, Splunk, etc.)

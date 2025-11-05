"""
🔐 Authentication Middleware
============================

Authentication and authorization middleware for the Brahma Blueprint module.
Handles JWT token validation and permission checking.
"""

import logging
from typing import List, Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import os

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")
JWT_ALGORITHM = "HS256"

security = HTTPBearer()


class TokenData(BaseModel):
    """Token payload data"""
    username: str
    roles: List[str]
    permissions: List[str]
    exp: int


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Verify JWT token and extract user information
    """
    try:
        token = credentials.credentials
        
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Extract user information
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )
        
        roles = payload.get("roles", [])
        permissions = payload.get("permissions", [])
        exp = payload.get("exp", 0)
        
        return TokenData(
            username=username,
            roles=roles,
            permissions=permissions,
            exp=exp
        )
        
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        ) from exc
    except Exception as e:
        logger.error("Token verification error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        ) from e


def require_permission(permission: str):
    """
    Decorator to require specific permission
    """
    def permission_checker(token_data: TokenData = Depends(verify_token)):
        # Check if user has supreme admin role
        if "supreme_admin" in token_data.roles:
            return token_data
        
        # Check if user has required permission
        if permission not in token_data.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}"
            )
        
        return token_data
    
    return permission_checker


def require_role(role: str):
    """
    Decorator to require specific role
    """
    def role_checker(token_data: TokenData = Depends(verify_token)):
        # Check if user has supreme admin role
        if "supreme_admin" in token_data.roles:
            return token_data
        
        # Check if user has required role
        if role not in token_data.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required role: {role}"
            )
        
        return token_data
    
    return role_checker


def get_current_user(
    token_data: TokenData = Depends(verify_token)
) -> str:
    """
    Get current authenticated username
    """
    return token_data.username


def get_user_permissions(
    token_data: TokenData = Depends(verify_token)
) -> List[str]:
    """
    Get current user's permissions
    """
    return token_data.permissions


# Helper function to create tokens (for testing)
def create_access_token(
    username: str,
    roles: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None,
    expires_in_hours: int = 24
) -> str:
    """
    Create JWT access token for testing purposes
    """
    import time
    
    payload = {
        "sub": username,
        "roles": roles or [],
        "permissions": permissions or [],
        "exp": int(time.time()) + (expires_in_hours * 3600),
        "iat": int(time.time())
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

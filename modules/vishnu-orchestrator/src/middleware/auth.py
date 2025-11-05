"""
🛡️ Vishnu Authentication Middleware
===================================

JWT-based authentication middleware for Vishnu orchestration services.
"""

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import os
from datetime import datetime, timezone

security = HTTPBearer()


class TokenData:
    """Token data model"""
    def __init__(self, username: str, user_id: str, permissions: list):
        self.username = username
        self.user_id = user_id
        self.permissions = permissions


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Verify JWT token and extract user information
    """
    try:
        token = credentials.credentials
        secret_key = os.getenv("JWT_SECRET_KEY")
        if not secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable is required")
        
        # Decode JWT token
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # Extract token data
        username = payload.get("sub")
        user_id = payload.get("user_id")
        permissions = payload.get("permissions", [])
        exp = payload.get("exp")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check token expiration
        if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(username=username, user_id=user_id, permissions=permissions)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permission(permission: str):
    """
    Decorator factory for permission-based access control
    """
    def permission_decorator(token_data: TokenData = Depends(verify_token)):
        if permission not in token_data.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return token_data
    
    return permission_decorator


def create_access_token(data: Dict[str, Any], expires_in: int = 3600) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc).timestamp() + expires_in
    to_encode.update({"exp": expire})
    
    secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    
    return encoded_jwt

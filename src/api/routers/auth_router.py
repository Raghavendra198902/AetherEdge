"""
Authentication router for AetherEdge API

Handles API token validation, user authentication, and authorization.
"""

from fastapi import APIRouter, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import jwt
import hashlib
from datetime import datetime, timedelta, timezone

from ..core.config import settings

router = APIRouter()
security = HTTPBearer()


class TokenRequest(BaseModel):
    """Token request model"""
    username: str
    password: str
    expires_in: Optional[int] = 3600  # 1 hour default


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    expires_in: int
    expires_at: str


class UserInfo(BaseModel):
    """User information model"""
    user_id: str
    username: str
    permissions: List[str]
    organization: str
    created_at: str


class ValidateTokenResponse(BaseModel):
    """Token validation response"""
    valid: bool
    user_info: Optional[UserInfo] = None
    expires_at: Optional[str] = None


# Simple in-memory user store (in production, use proper auth service)
USERS = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "permissions": ["read", "write", "admin"],
        "organization": "default",
        "created_at": "2024-01-01T00:00:00Z"
    },
    "user": {
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "permissions": ["read"],
        "organization": "default",
        "created_at": "2024-01-01T00:00:00Z"
    }
}


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash


def create_access_token(data: Dict[str, Any],
                        expires_delta: int = 3600) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/token", response_model=TokenResponse)
async def create_token(token_request: TokenRequest):
    """Create access token for user authentication"""
    
    # Validate user credentials
    user_data = USERS.get(token_request.username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not verify_password(token_request.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create token payload
    token_data = {
        "sub": token_request.username,
        "permissions": user_data["permissions"],
        "organization": user_data["organization"],
        "iat": int(time.time())
    }
    
    # Create access token
    access_token = create_access_token(
        token_data,
        expires_delta=token_request.expires_in
    )
    
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=token_request.expires_in
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=token_request.expires_in,
        expires_at=expires_at.isoformat()
    )


@router.post("/validate", response_model=ValidateTokenResponse)
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Validate access token"""
    
    try:
        payload = verify_token(credentials.credentials)
        
        # Get user info
        username = payload.get("sub")
        user_data = USERS.get(username, {})
        
        user_info = UserInfo(
            user_id=username,
            username=username,
            permissions=payload.get("permissions", []),
            organization=payload.get("organization", "default"),
            created_at=user_data.get("created_at", "")
        )
        
        # Get expiration time
        exp_timestamp = payload.get("exp")
        expires_at = None
        if exp_timestamp:
            expires_at = datetime.fromtimestamp(
                exp_timestamp,
                tz=timezone.utc
            ).isoformat()
        
        return ValidateTokenResponse(
            valid=True,
            user_info=user_info,
            expires_at=expires_at
        )
        
    except HTTPException:
        return ValidateTokenResponse(valid=False)


@router.delete("/revoke")
async def revoke_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Revoke access token (placeholder - would implement token blacklist)"""
    
    # Verify token is valid
    verify_token(credentials.credentials)
    
    # In production, add token to blacklist/revocation list
    # For now, just return success
    
    return {
        "message": "Token revoked successfully",
        "revoked_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/me", response_model=UserInfo)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get current user information"""
    
    payload = verify_token(credentials.credentials)
    username = payload.get("sub")
    
    if not username or username not in USERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = USERS[username]
    
    return UserInfo(
        user_id=username,
        username=username,
        permissions=payload.get("permissions", []),
        organization=payload.get("organization", "default"),
        created_at=user_data.get("created_at", "")
    )


@router.get("/permissions")
async def get_user_permissions(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get current user permissions"""
    
    payload = verify_token(credentials.credentials)
    
    return {
        "permissions": payload.get("permissions", []),
        "organization": payload.get("organization", "default")
    }

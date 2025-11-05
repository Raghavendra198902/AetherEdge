"""
⚡ Divine Rate Limiting Middleware
=================================

Rate limiting middleware for the Divine API Gateway.
Implements sliding window rate limiting with Redis backend.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import asyncio
import logging
from typing import Dict, Optional
import hashlib
import json

from ..config import settings

logger = logging.getLogger(__name__)

# In-memory rate limit store (for development - use Redis in production)
_rate_limit_store: Dict[str, Dict] = {}


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""
    def __init__(self, message: str, retry_after: int):
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)


def get_client_identifier(request: Request) -> str:
    """
    Get unique identifier for the client
    """
    # Priority order: API key > User ID > IP address
    
    # Check for API key in headers
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
    
    # Check for authenticated user
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # Extract username from token (simplified)
        try:
            from ..middleware.auth import verify_token
            from fastapi.security import HTTPAuthorizationCredentials
            
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer", 
                credentials=auth_header[7:]
            )
            token_data = verify_token(credentials)
            return f"user:{token_data.username}"
        except Exception:
            pass
    
    # Fall back to IP address
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    return f"ip:{client_ip}"


def get_rate_limit_key(client_id: str, endpoint: str) -> str:
    """
    Generate rate limit key for specific client and endpoint
    """
    return f"rate_limit:{client_id}:{endpoint}"


async def check_rate_limit(
    client_id: str,
    endpoint: str,
    limit: int = None,
    window: int = None
) -> Dict:
    """
    Check if client has exceeded rate limit
    """
    if limit is None:
        limit = settings.RATE_LIMIT_REQUESTS
    if window is None:
        window = settings.RATE_LIMIT_WINDOW
    
    key = get_rate_limit_key(client_id, endpoint)
    current_time = int(time.time())
    window_start = current_time - window
    
    # Get existing data
    if key not in _rate_limit_store:
        _rate_limit_store[key] = {
            "requests": [],
            "first_request": current_time
        }
    
    data = _rate_limit_store[key]
    
    # Clean up old requests (sliding window)
    data["requests"] = [
        req_time for req_time in data["requests"] 
        if req_time > window_start
    ]
    
    # Check if limit exceeded
    current_requests = len(data["requests"])
    
    if current_requests >= limit:
        # Calculate retry after time
        oldest_request = min(data["requests"]) if data["requests"] else current_time
        retry_after = oldest_request + window - current_time
        
        raise RateLimitExceeded(
            f"Rate limit exceeded. Limit: {limit} requests per {window} seconds",
            retry_after
        )
    
    # Add current request
    data["requests"].append(current_time)
    
    # Return rate limit info
    return {
        "limit": limit,
        "remaining": limit - current_requests - 1,
        "reset": window_start + window,
        "retry_after": 0
    }


def get_endpoint_limits(endpoint: str) -> Dict[str, int]:
    """
    Get specific rate limits for endpoints
    """
    # Default limits
    default_limit = settings.RATE_LIMIT_REQUESTS
    default_window = settings.RATE_LIMIT_WINDOW
    
    # Endpoint-specific limits
    endpoint_limits = {
        # Authentication endpoints - stricter limits
        "/api/v1/auth/login": {"limit": 5, "window": 300},  # 5 per 5 minutes
        "/api/v1/auth/register": {"limit": 3, "window": 3600},  # 3 per hour
        "/api/v1/auth/reset-password": {"limit": 3, "window": 3600},
        
        # Resource creation endpoints - moderate limits
        "/api/v1/brahma/blueprints": {"limit": 50, "window": 3600},
        "/api/v1/vishnu/policies": {"limit": 30, "window": 3600},
        "/api/v1/shiva/incidents": {"limit": 100, "window": 3600},
        
        # Analytics endpoints - higher limits
        "/api/v1/analytics": {"limit": 200, "window": 3600},
        "/api/v1/metrics": {"limit": 500, "window": 3600},
        
        # Health check endpoints - unlimited
        "/api/v1/health": {"limit": 1000, "window": 60},
        "/health": {"limit": 1000, "window": 60},
        "/readiness": {"limit": 1000, "window": 60},
        "/liveness": {"limit": 1000, "window": 60},
    }
    
    # Check for exact match
    if endpoint in endpoint_limits:
        return endpoint_limits[endpoint]
    
    # Check for pattern matches
    for pattern, limits in endpoint_limits.items():
        if endpoint.startswith(pattern.replace("*", "")):
            return limits
    
    return {"limit": default_limit, "window": default_window}


class RateLimitMiddleware:
    """
    Rate limiting middleware
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            # Get client identifier
            client_id = get_client_identifier(request)
            
            # Get endpoint
            endpoint = request.url.path
            
            # Get rate limits for this endpoint
            limits = get_endpoint_limits(endpoint)
            
            # Check rate limit
            rate_info = await check_rate_limit(
                client_id,
                endpoint,
                limits["limit"],
                limits["window"]
            )
            
            # Add rate limit headers to response
            async def add_rate_limit_headers(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.extend([
                        (b"X-RateLimit-Limit", str(rate_info["limit"]).encode()),
                        (b"X-RateLimit-Remaining", str(rate_info["remaining"]).encode()),
                        (b"X-RateLimit-Reset", str(rate_info["reset"]).encode()),
                    ])
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, add_rate_limit_headers)
            
        except RateLimitExceeded as e:
            # Return rate limit exceeded response
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": e.message,
                    "retry_after": e.retry_after
                },
                headers={
                    "Retry-After": str(e.retry_after),
                    "X-RateLimit-Limit": str(limits["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + e.retry_after)
                }
            )
            await response(scope, receive, send)
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Continue without rate limiting if there's an error
            await self.app(scope, receive, send)


# Redis-based rate limiting (for production)
class RedisRateLimitMiddleware:
    """
    Redis-based rate limiting middleware for production use
    """
    
    def __init__(self, app, redis_client=None):
        self.app = app
        self.redis = redis_client
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        if not self.redis:
            # Fall back to in-memory rate limiting
            middleware = RateLimitMiddleware(self.app)
            await middleware(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            client_id = get_client_identifier(request)
            endpoint = request.url.path
            limits = get_endpoint_limits(endpoint)
            
            # Use Redis for rate limiting
            key = get_rate_limit_key(client_id, endpoint)
            
            # Sliding window implementation with Redis
            current_time = int(time.time())
            window_start = current_time - limits["window"]
            
            pipe = self.redis.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiry
            pipe.expire(key, limits["window"])
            
            results = await pipe.execute()
            current_requests = results[1]
            
            if current_requests >= limits["limit"]:
                # Get oldest request for retry-after calculation
                oldest = await self.redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(oldest[0][1]) + limits["window"] - current_time
                else:
                    retry_after = limits["window"]
                
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Rate limit exceeded. Limit: {limits['limit']} requests per {limits['window']} seconds",
                        "retry_after": retry_after
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(limits["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(current_time + retry_after)
                    }
                )
                await response(scope, receive, send)
                return
            
            # Add rate limit headers
            async def add_rate_limit_headers(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    remaining = limits["limit"] - current_requests - 1
                    headers.extend([
                        (b"X-RateLimit-Limit", str(limits["limit"]).encode()),
                        (b"X-RateLimit-Remaining", str(remaining).encode()),
                        (b"X-RateLimit-Reset", str(current_time + limits["window"]).encode()),
                    ])
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, add_rate_limit_headers)
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {str(e)}")
            # Continue without rate limiting if there's an error
            await self.app(scope, receive, send)


# Rate limit status endpoint
async def get_rate_limit_status(client_id: str, endpoint: str = None):
    """
    Get current rate limit status for a client
    """
    if endpoint:
        endpoints = [endpoint]
    else:
        # Get all endpoints for this client
        endpoints = [
            key.split(":")[-1] for key in _rate_limit_store.keys()
            if key.startswith(f"rate_limit:{client_id}:")
        ]
    
    status_info = {}
    
    for ep in endpoints:
        key = get_rate_limit_key(client_id, ep)
        if key in _rate_limit_store:
            data = _rate_limit_store[key]
            limits = get_endpoint_limits(ep)
            
            current_time = int(time.time())
            window_start = current_time - limits["window"]
            
            # Clean up old requests
            active_requests = [
                req_time for req_time in data["requests"] 
                if req_time > window_start
            ]
            
            status_info[ep] = {
                "limit": limits["limit"],
                "window": limits["window"],
                "current_requests": len(active_requests),
                "remaining": limits["limit"] - len(active_requests),
                "reset_time": current_time + limits["window"]
            }
    
    return status_info

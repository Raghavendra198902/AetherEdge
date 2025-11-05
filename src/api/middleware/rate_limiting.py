"""
Rate limiting middleware for AetherEdge API

Implements request rate limiting using token bucket algorithm
with Redis backend for distributed rate limiting.
"""

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
import time
import logging
import asyncio
from typing import Dict, Optional
import redis.asyncio as redis

from ..core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Rate limiting middleware using token bucket algorithm"""
    
    def __init__(self, app):
        self.app = app
        self.redis_client: Optional[redis.Redis] = None
        self.local_store: Dict[str, Dict] = {}
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window_seconds = settings.RATE_LIMIT_WINDOW
        
    async def __call__(self, request: Request, call_next):
        """Apply rate limiting to incoming requests"""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Check rate limit
        allowed, retry_after = await self._check_rate_limit(client_id)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        self._add_rate_limit_headers(response, client_id)
        
        return response
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get API key from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Use hash of token for privacy
            import hashlib
            token = auth_header[7:]
            return f"token:{hashlib.sha256(token.encode()).hexdigest()[:16]}"
        
        # Fallback to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _check_rate_limit(self, client_id: str) -> tuple[bool, int]:
        """Check if request is within rate limit"""
        try:
            if self.redis_client:
                return await self._check_redis_rate_limit(client_id)
            else:
                return self._check_local_rate_limit(client_id)
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            # Allow request on error
            return True, 0
    
    async def _check_redis_rate_limit(
        self, client_id: str
    ) -> tuple[bool, int]:
        """Check rate limit using Redis backend"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Redis key for the client
        key = f"rate_limit:{client_id}"
        
        try:
            # Use Redis sorted set for sliding window
            pipe = self.redis_client.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiration
            pipe.expire(key, self.window_seconds)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            # Check if limit exceeded
            if current_requests >= self.max_requests:
                # Calculate retry after
                oldest_request = await self.redis_client.zrange(key, 0, 0)
                if oldest_request:
                    retry_after = int(
                        float(oldest_request[0]) + self.window_seconds - now
                    )
                    return False, max(retry_after, 1)
                return False, self.window_seconds
            
            return True, 0
            
        except Exception as e:
            logger.error(f"Redis rate limit error: {str(e)}")
            return True, 0
    
    def _check_local_rate_limit(
        self, client_id: str
    ) -> tuple[bool, int]:
        """Check rate limit using local memory store"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get or create client data
        if client_id not in self.local_store:
            self.local_store[client_id] = {"requests": [], "last_cleanup": now}
        
        client_data = self.local_store[client_id]
        
        # Clean up old requests
        client_data["requests"] = [
            req_time for req_time in client_data["requests"]
            if req_time > window_start
        ]
        
        # Check limit
        if len(client_data["requests"]) >= self.max_requests:
            # Calculate retry after
            oldest_request = min(client_data["requests"])
            retry_after = int(oldest_request + self.window_seconds - now)
            return False, max(retry_after, 1)
        
        # Add current request
        client_data["requests"].append(now)
        client_data["last_cleanup"] = now
        
        return True, 0
    
    def _add_rate_limit_headers(self, response: Response, client_id: str):
        """Add rate limit information to response headers"""
        try:
            # Get current usage
            if client_id in self.local_store:
                current_requests = len(self.local_store[client_id]["requests"])
            else:
                current_requests = 0
            
            response.headers["X-RateLimit-Limit"] = str(self.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, self.max_requests - current_requests)
            )
            response.headers["X-RateLimit-Reset"] = str(
                int(time.time() + self.window_seconds)
            )
            
        except Exception as e:
            logger.error(f"Error adding rate limit headers: {str(e)}")
    
    async def _setup_redis(self):
        """Setup Redis connection for distributed rate limiting"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis rate limiting enabled")
            
        except Exception as e:
            logger.warning(
                f"Redis connection failed, using local store: {str(e)}"
            )
            self.redis_client = None
    
    async def cleanup_local_store(self):
        """Periodic cleanup of local rate limit store"""
        while True:
            try:
                now = time.time()
                cleanup_threshold = now - (self.window_seconds * 2)
                
                # Remove old client data
                expired_clients = [
                    client_id for client_id, data in self.local_store.items()
                    if data.get("last_cleanup", 0) < cleanup_threshold
                ]
                
                for client_id in expired_clients:
                    del self.local_store[client_id]
                
                if expired_clients:
                    logger.debug(
                        f"Cleaned up {len(expired_clients)} "
                        "expired rate limit entries"
                    )
                
                # Sleep for cleanup interval
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Rate limit cleanup error: {str(e)}")
                await asyncio.sleep(60)

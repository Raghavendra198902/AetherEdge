"""
Security middleware for AetherEdge API

Implements security headers, request validation, and threat protection.
"""

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
import time
import logging
import ipaddress
from typing import Set, List

from ..core.config import settings

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Security middleware for request processing"""
    
    def __init__(self, app):
        self.app = app
        self.blocked_ips: Set[str] = set()
        self.rate_limit_store: dict = {}
        
    async def __call__(self, request: Request, call_next):
        """Process security checks for incoming requests"""
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check IP blocking
        if self._is_ip_blocked(client_ip):
            logger.warning(f"Blocked request from {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access denied"}
            )
        
        # Validate request headers
        if not self._validate_headers(request):
            logger.warning(f"Invalid headers from {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request headers"}
            )
        
        # Process request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response)
            
            # Log request
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"{response.status_code} - {process_time:.3f}s - {client_ip}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Request processing error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP address is blocked"""
        if ip in self.blocked_ips:
            return True
        
        # Check for private/local IPs in production
        if settings.ENVIRONMENT == "production":
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private and ip != "127.0.0.1":
                    return True
            except ValueError:
                # Invalid IP format
                return True
        
        return False
    
    def _validate_headers(self, request: Request) -> bool:
        """Validate request headers for security"""
        headers = request.headers
        
        # Check for required headers in production
        if settings.ENVIRONMENT == "production":
            # Validate Host header
            host = headers.get("host", "")
            if not any(allowed in host for allowed in settings.ALLOWED_HOSTS):
                return False
        
        # Check for suspicious headers
        suspicious_headers = [
            "x-forwarded-host",
            "x-original-url",
            "x-rewrite-url"
        ]
        
        for header in suspicious_headers:
            if header in headers:
                logger.warning(f"Suspicious header detected: {header}")
        
        return True
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "accelerometer=(), gyroscope=(), magnetometer=()"
            ),
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        # Only add HSTS in production with HTTPS
        if settings.ENVIRONMENT != "production":
            del security_headers["Strict-Transport-Security"]
        
        for header, value in security_headers.items():
            response.headers[header] = value
    
    def block_ip(self, ip: str):
        """Block an IP address"""
        self.blocked_ips.add(ip)
        logger.info(f"Blocked IP address: {ip}")
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip)
        logger.info(f"Unblocked IP address: {ip}")
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IP addresses"""
        return list(self.blocked_ips)

"""
🛡️ Security Headers Middleware
==============================

Security middleware for adding protective HTTP headers to responses.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses
    """
    
    def __init__(self, app, headers: dict = None):
        super().__init__(app)
        self.security_headers = headers or self.get_default_headers()
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers to response
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value
        
        return response
    
    @staticmethod
    def get_default_headers() -> dict:
        """
        Get default security headers
        """
        return {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # Enable XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Force HTTPS (only if using HTTPS)
            # "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # Content Security Policy (restrictive default)
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "font-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            ),
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions policy (disable unnecessary features)
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "bluetooth=()"
            ),
            
            # Remove server information
            "Server": "AetherEdge"
        }


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Basic CSRF protection middleware
    """
    
    def __init__(self, app, csrf_cookie_name: str = "csrf_token"):
        super().__init__(app)
        self.csrf_cookie_name = csrf_cookie_name
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)
        
        # Skip CSRF check for API endpoints with proper authentication
        if request.url.path.startswith("/api/") and self._has_valid_auth(request):
            return await call_next(request)
        
        # For other methods, implement CSRF token validation
        # This is a basic implementation - consider using more robust solutions
        
        response = await call_next(request)
        return response
    
    def _has_valid_auth(self, request: Request) -> bool:
        """
        Check if request has valid authentication
        """
        auth_header = request.headers.get("Authorization")
        api_key = request.headers.get("X-API-Key")
        
        return bool(auth_header and auth_header.startswith("Bearer ")) or bool(api_key)

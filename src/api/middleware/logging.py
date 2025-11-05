"""
Logging middleware for AetherEdge API

Provides structured logging, request tracking, and audit trails.
"""

from fastapi import Request, Response
import time
import logging
import uuid
import json
from typing import Dict, Any
import asyncio
from datetime import datetime, timezone

from ..core.config import settings
from ..core.monitoring import metrics

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Middleware for request/response logging and monitoring"""
    
    def __init__(self, app):
        self.app = app
        self.sensitive_headers = {
            "authorization", "cookie", "x-api-key", "x-auth-token"
        }
        self.sensitive_fields = {
            "password", "secret", "token", "key", "credential"
        }
        
    async def __call__(self, request: Request, call_next):
        """Process and log HTTP requests"""
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request
        await self._log_request(request, request_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            self._log_response(request, response, request_id, process_time)
            
            # Update metrics
            metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=process_time
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log error
            self._log_error(request, e, request_id, process_time)
            
            # Re-raise exception
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details"""
        try:
            # Get request body for POST/PUT/PATCH requests
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await self._get_request_body(request)
            
            # Prepare log data
            log_data = {
                "event": "request",
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": self._sanitize_headers(dict(request.headers)),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
                "content_length": request.headers.get("content-length", 0),
                "body": self._sanitize_body(body) if body else None
            }
            
            # Log at appropriate level
            if settings.LOG_LEVEL == "DEBUG":
                logger.debug(f"Request: {json.dumps(log_data, indent=2)}")
            else:
                logger.info(
                    f"{request.method} {request.url.path} - "
                    f"{self._get_client_ip(request)} - {request_id}"
                )
                
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")
    
    def _log_response(self, request: Request, response: Response,
                      request_id: str, process_time: float):
        """Log response details"""
        try:
            log_data = {
                "event": "response",
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
                "response_headers": self._sanitize_headers(dict(response.headers)),
                "content_length": response.headers.get("content-length", 0)
            }
            
            # Log at appropriate level based on status code
            if response.status_code >= 500:
                logger.error(f"Response: {json.dumps(log_data, indent=2)}")
            elif response.status_code >= 400:
                logger.warning(f"Response: {json.dumps(log_data, indent=2)}")
            elif settings.LOG_LEVEL == "DEBUG":
                logger.debug(f"Response: {json.dumps(log_data, indent=2)}")
            else:
                logger.info(
                    f"{request.method} {request.url.path} - "
                    f"{response.status_code} - {process_time:.3f}s"
                )
                
        except Exception as e:
            logger.error(f"Error logging response: {str(e)}")
    
    def _log_error(self, request: Request, error: Exception,
                   request_id: str, process_time: float):
        """Log error details"""
        try:
            log_data = {
                "event": "error",
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": request.method,
                "path": request.url.path,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "process_time": round(process_time, 3),
                "client_ip": self._get_client_ip(request)
            }
            
            logger.error(f"Request Error: {json.dumps(log_data, indent=2)}")
            
        except Exception as e:
            logger.error(f"Error logging error: {str(e)}")
    
    async def _get_request_body(self, request: Request) -> bytes:
        """Get request body safely"""
        try:
            body = await request.body()
            # Reset body for downstream processing
            if hasattr(request, '_body'):
                request._body = body
            return body
        except Exception as e:
            logger.warning(f"Could not read request body: {str(e)}")
            return b""
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive information from headers"""
        sanitized = {}
        
        for key, value in headers.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in self.sensitive_headers):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_body(self, body: bytes) -> Any:
        """Remove sensitive information from request body"""
        try:
            # Only process JSON bodies
            if not body:
                return None
            
            # Try to parse as JSON
            body_str = body.decode('utf-8')
            data = json.loads(body_str)
            
            # Recursively sanitize
            return self._sanitize_dict(data)
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Not JSON or invalid encoding
            return "[BINARY_DATA]"
        except Exception:
            return "[PARSE_ERROR]"
    
    def _sanitize_dict(self, data: Any) -> Any:
        """Recursively sanitize dictionary data"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in self.sensitive_fields):
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self._sanitize_dict(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_dict(item) for item in data]
        else:
            return data

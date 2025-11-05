"""
📊 Divine Logging Middleware
============================

Comprehensive logging middleware for the Divine API Gateway.
Implements structured logging with correlation IDs and performance metrics.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import logging
import json
from typing import Dict, Any
from datetime import datetime, timezone

from ..config import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive logging middleware
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        
        # Add correlation ID to request state
        request.state.correlation_id = correlation_id
        
        # Start timing
        start_time = time.time()
        
        # Log incoming request
        await self.log_request(request, correlation_id)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            await self.log_response(request, response, process_time, correlation_id)
            
            return response
            
        except Exception as e:
            # Calculate processing time for errors too
            process_time = time.time() - start_time
            
            # Log error
            await self.log_error(request, e, process_time, correlation_id)
            
            # Re-raise the exception
            raise
    
    async def log_request(self, request: Request, correlation_id: str):
        """
        Log incoming request details
        """
        try:
            # Extract client information
            client_ip = self.get_client_ip(request)
            user_agent = request.headers.get("User-Agent", "Unknown")
            
            # Extract user information if available
            user_info = await self.extract_user_info(request)
            
            # Prepare log data
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": correlation_id,
                "event_type": "request_start",
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": self.sanitize_headers(dict(request.headers)),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "user_info": user_info,
                "request_size": request.headers.get("Content-Length", "0")
            }
            
            # Log based on environment
            if settings.ENVIRONMENT == "development":
                logger.info(f"REQUEST: {request.method} {request.url.path} [{correlation_id}]")  # noqa: E501
            else:
                logger.info(json.dumps(log_data))
                
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")
    
    async def log_response(
        self, 
        request: Request, 
        response: Response, 
        process_time: float, 
        correlation_id: str
    ):
        """
        Log response details
        """
        try:
            # Prepare log data
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": correlation_id,
                "event_type": "request_complete",
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "status_code": response.status_code,
                "response_headers": self.sanitize_headers(dict(response.headers)),
                "process_time_ms": round(process_time * 1000, 2),
                "response_size": response.headers.get("Content-Length", "0")
            }
            
            # Determine log level based on status code
            if response.status_code >= 500:
                log_level = "error"
            elif response.status_code >= 400:
                log_level = "warning"
            else:
                log_level = "info"
            
            # Log based on environment
            if settings.ENVIRONMENT == "development":
                logger.log(
                    getattr(logging, log_level.upper()),
                    f"RESPONSE: {response.status_code} {request.method} {request.url.path} "  # noqa: E501
                    f"[{correlation_id}] {process_time*1000:.2f}ms"
                )
            else:
                logger.log(getattr(logging, log_level.upper()), json.dumps(log_data))  # noqa: E501
                
        except Exception as e:
            logger.error(f"Failed to log response: {str(e)}")
    
    async def log_error(
        self, 
        request: Request, 
        error: Exception, 
        process_time: float, 
        correlation_id: str
    ):
        """
        Log error details
        """
        try:
            # Prepare log data
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": correlation_id,
                "event_type": "request_error",
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "process_time_ms": round(process_time * 1000, 2)
            }
            
            # Log based on environment
            if settings.ENVIRONMENT == "development":
                logger.error(
                    f"ERROR: {type(error).__name__} {request.method} {request.url.path} "  # noqa: E501
                    f"[{correlation_id}] {process_time*1000:.2f}ms - {str(error)}"
                )
            else:
                logger.error(json.dumps(log_data))
                
        except Exception as e:
            logger.error(f"Failed to log error: {str(e)}")
    
    def get_client_ip(self, request: Request) -> str:
        """
        Get client IP address considering proxies
        """
        # Check X-Forwarded-For header (most common)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Check CF-Connecting-IP (Cloudflare)
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip:
            return cf_ip.strip()
        
        # Fall back to direct connection
        return request.client.host if request.client else "unknown"
    
    def sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize headers to remove sensitive information
        """
        sensitive_headers = {
            "authorization", "x-api-key", "cookie", "set-cookie",
            "x-auth-token", "authentication", "proxy-authorization"
        }
        
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def extract_user_info(self, request: Request) -> Dict[str, Any]:
        """
        Extract user information from request if available
        """
        try:
            # Check for Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                from ..middleware.auth import verify_token
                from fastapi.security import HTTPAuthorizationCredentials
                
                try:
                    credentials = HTTPAuthorizationCredentials(
                        scheme="Bearer",
                        credentials=auth_header[7:]
                    )
                    token_data = verify_token(credentials)
                    
                    return {
                        "username": token_data.username,
                        "roles": token_data.roles,
                        "permissions": token_data.permissions[:5]  # Limit for log size  # noqa: E501
                    }
                except Exception:
                    return {"authentication": "invalid_token"}
            
            # Check for API key
            api_key = request.headers.get("X-API-Key")
            if api_key:
                return {
                    "authentication": "api_key",
                    "api_key_hash": api_key[:8] + "..." if len(api_key) > 8 else api_key  # noqa: E501
                }
            
            return {"authentication": "none"}
            
        except Exception as e:
            logger.debug(f"Failed to extract user info: {str(e)}")
            return {"authentication": "error"}


class PerformanceMetricsMiddleware(BaseHTTPMiddleware):
    """
    Performance metrics collection middleware
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics = {
            "request_count": 0,
            "error_count": 0,
            "total_processing_time": 0.0,
            "endpoint_metrics": {}
        }
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Increment request count
        self.metrics["request_count"] += 1
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            self.metrics["total_processing_time"] += process_time
            
            # Update endpoint metrics
            endpoint = f"{request.method} {request.url.path}"
            if endpoint not in self.metrics["endpoint_metrics"]:
                self.metrics["endpoint_metrics"][endpoint] = {
                    "count": 0,
                    "total_time": 0.0,
                    "avg_time": 0.0,
                    "min_time": float('inf'),
                    "max_time": 0.0,
                    "error_count": 0
                }
            
            endpoint_metrics = self.metrics["endpoint_metrics"][endpoint]
            endpoint_metrics["count"] += 1
            endpoint_metrics["total_time"] += process_time
            endpoint_metrics["avg_time"] = endpoint_metrics["total_time"] / endpoint_metrics["count"]  # noqa: E501
            endpoint_metrics["min_time"] = min(endpoint_metrics["min_time"], process_time)  # noqa: E501
            endpoint_metrics["max_time"] = max(endpoint_metrics["max_time"], process_time)  # noqa: E501
            
            # Count errors
            if response.status_code >= 400:
                self.metrics["error_count"] += 1
                endpoint_metrics["error_count"] += 1
            
            return response
            
        except Exception as e:
            # Count errors
            self.metrics["error_count"] += 1
            
            # Update endpoint error metrics
            endpoint = f"{request.method} {request.url.path}"
            if endpoint in self.metrics["endpoint_metrics"]:
                self.metrics["endpoint_metrics"][endpoint]["error_count"] += 1
            
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics
        """
        total_requests = self.metrics["request_count"]
        avg_processing_time = (
            self.metrics["total_processing_time"] / total_requests 
            if total_requests > 0 else 0
        )
        
        return {
            "total_requests": total_requests,
            "total_errors": self.metrics["error_count"],
            "error_rate": (
                self.metrics["error_count"] / total_requests 
                if total_requests > 0 else 0
            ),
            "avg_processing_time_ms": round(avg_processing_time * 1000, 2),
            "endpoint_metrics": self.metrics["endpoint_metrics"]
        }


# Correlation ID utility
def get_correlation_id(request: Request) -> str:
    """
    Get correlation ID from request state or generate new one
    """
    return getattr(request.state, 'correlation_id', str(uuid.uuid4()))


# Security logging functions
def log_security_event(
    event_type: str, 
    details: Dict[str, Any], 
    severity: str = "info",
    correlation_id: str = None
):
    """
    Log security-related events
    """
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "event_type": f"security_{event_type}",
        "severity": severity,
        "details": details
    }
    
    log_level = getattr(logging, severity.upper(), logging.INFO)
    logger.log(log_level, f"SECURITY_EVENT: {json.dumps(log_data)}")


def log_audit_event(
    action: str, 
    resource: str, 
    user_id: str, 
    details: Dict[str, Any] = None,
    correlation_id: str = None
):
    """
    Log audit trail events
    """
    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "event_type": "audit",
        "action": action,
        "resource": resource,
        "user_id": user_id,
        "details": details or {}
    }
    
    logger.info(f"AUDIT_EVENT: {json.dumps(log_data)}")


# Performance monitoring
class PerformanceMonitor:
    """
    Performance monitoring utilities
    """
    
    @staticmethod
    def track_execution_time(func_name: str):
        """
        Decorator to track function execution time
        """
        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    log_data = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "event_type": "function_performance",
                        "function": func_name,
                        "execution_time_ms": round(execution_time * 1000, 2),
                        "status": "success"
                    }
                    
                    logger.debug(f"PERF: {json.dumps(log_data)}")
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    log_data = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "event_type": "function_performance",
                        "function": func_name,
                        "execution_time_ms": round(execution_time * 1000, 2),
                        "status": "error",
                        "error": str(e)
                    }
                    
                    logger.error(f"PERF_ERROR: {json.dumps(log_data)}")
                    raise
            
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    log_data = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "event_type": "function_performance",
                        "function": func_name,
                        "execution_time_ms": round(execution_time * 1000, 2),
                        "status": "success"
                    }
                    
                    logger.debug(f"PERF: {json.dumps(log_data)}")
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    log_data = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "event_type": "function_performance",
                        "function": func_name,
                        "execution_time_ms": round(execution_time * 1000, 2),
                        "status": "error",
                        "error": str(e)
                    }
                    
                    logger.error(f"PERF_ERROR: {json.dumps(log_data)}")
                    raise
            
            # Return appropriate wrapper based on function type
            if hasattr(func, '__call__') and hasattr(func, '__await__'):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator

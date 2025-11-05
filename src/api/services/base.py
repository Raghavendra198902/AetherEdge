"""
Base service class for AetherEdge API

Provides common functionality for all service classes.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ..core.monitoring import metrics

logger = logging.getLogger(__name__)


class BaseService:
    """Base service class with common functionality"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(f"services.{service_name}")
        
    def log_operation(self, operation: str,
                      details: Optional[Dict[str, Any]] = None):
        """Log service operation"""
        log_data = {
            "service": self.service_name,
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if details:
            log_data.update(details)
            
        self.logger.info(f"Operation: {operation}", extra=log_data)
    
    def record_metrics(self, operation: str, success: bool):
        """Record operation metrics"""
        try:
            # Record operation metrics
            if hasattr(metrics, 'record_cache_operation'):
                result = "success" if success else "error"
                metrics.record_cache_operation(operation, result)
                
        except Exception as e:
            self.logger.error(f"Failed to record metrics: {str(e)}")
    
    def handle_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Handle and format service errors"""
        error_details = {
            "service": self.service_name,
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.error(
            f"Service error in {operation}: {str(error)}",
            extra=error_details
        )
        
        return error_details
    
    def validate_input(self, data: Dict[str, Any],
                       required_fields: list) -> bool:
        """Validate input data has required fields"""
        missing_fields = [
            field for field in required_fields if field not in data
        ]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
            
        return True
    
    def format_response(self, data: Any,
                        message: str = "Success") -> Dict[str, Any]:
        """Format service response"""
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def format_error_response(
        self, error: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format error response"""
        response = {
            "success": False,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if details:
            response["details"] = details
            
        return response

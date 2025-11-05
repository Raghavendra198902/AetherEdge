"""
Pydantic models for AetherEdge API

Shared data models and schemas used across the API.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class ResourceType(str, Enum):
    """Resource types in the platform"""
    SERVER = "server"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK = "network"
    APPLICATION = "application"


class ResourceStatus(str, Enum):
    """Resource status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class SeverityLevel(str, Enum):
    """Severity levels for alerts and issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BaseResource(BaseModel):
    """Base resource model"""
    resource_id: str = Field(..., description="Unique resource identifier")
    name: str = Field(..., description="Resource name")
    resource_type: ResourceType = Field(..., description="Type of resource")
    status: ResourceStatus = Field(..., description="Current status")
    tags: Optional[Dict[str, str]] = Field(
        default={}, description="Resource tags"
    )
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(
        None, description="Last update timestamp"
    )
    
    @validator('resource_id')
    def validate_resource_id(cls, v):
        """Validate resource ID format"""
        if not v or len(v) < 3:
            raise ValueError('Resource ID must be at least 3 characters')
        return v


class Alert(BaseModel):
    """Alert model"""
    alert_id: str = Field(..., description="Unique alert identifier")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    severity: SeverityLevel = Field(..., description="Alert severity")
    resource_id: Optional[str] = Field(None, description="Related resource ID")
    status: str = Field(default="active", description="Alert status")
    created_at: str = Field(..., description="Alert creation time")
    acknowledged_at: Optional[str] = Field(
        None, description="Acknowledgment time"
    )
    resolved_at: Optional[str] = Field(None, description="Resolution time")


class MetricData(BaseModel):
    """Metric data point"""
    timestamp: str = Field(..., description="Metric timestamp")
    value: Union[float, int] = Field(..., description="Metric value")
    unit: str = Field(..., description="Metric unit")
    labels: Optional[Dict[str, str]] = Field(
        default={}, description="Metric labels"
    )


class PerformanceMetrics(BaseModel):
    """Performance metrics collection"""
    resource_id: str = Field(..., description="Resource identifier")
    metric_type: str = Field(..., description="Type of metric")
    data_points: List[MetricData] = Field(
        ..., description="Metric data points"
    )
    aggregation_period: str = Field(
        default="1h", description="Data aggregation period"
    )
    collected_at: str = Field(..., description="Collection timestamp")


class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")
    
    @validator('page')
    def validate_page(cls, v):
        """Validate page number"""
        if v < 1:
            raise ValueError('Page number must be at least 1')
        return v
    
    @validator('page_size')
    def validate_page_size(cls, v):
        """Validate page size"""
        if v < 1 or v > 1000:
            raise ValueError('Page size must be between 1 and 1000')
        return v


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackgroundTask(BaseModel):
    """Background task model"""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task")
    status: TaskStatus = Field(..., description="Task status")
    progress: int = Field(default=0, description="Task progress percentage")
    result: Optional[Any] = Field(None, description="Task result")
    error_message: Optional[str] = Field(None, description="Error message")
    started_at: str = Field(..., description="Task start time")
    completed_at: Optional[str] = Field(
        None, description="Task completion time"
    )
    
    @validator('progress')
    def validate_progress(cls, v):
        """Validate progress percentage"""
        if v < 0 or v > 100:
            raise ValueError('Progress must be between 0 and 100')
        return v


class AuditLog(BaseModel):
    """Audit log entry"""
    log_id: str = Field(..., description="Unique log identifier")
    user_id: str = Field(..., description="User who performed the action")
    action: str = Field(..., description="Action performed")
    resource_type: Optional[str] = Field(None, description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource identifier")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional details"
    )
    ip_address: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    timestamp: str = Field(..., description="Action timestamp")


class ErrorResponse(BaseModel):
    """Error response model"""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
    trace_id: Optional[str] = Field(None, description="Request trace ID")
    timestamp: str = Field(..., description="Error timestamp")


class HealthStatus(str, Enum):
    """Health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ServiceHealth(BaseModel):
    """Service health status"""
    service_name: str = Field(..., description="Service name")
    status: HealthStatus = Field(..., description="Health status")
    version: Optional[str] = Field(None, description="Service version")
    uptime_seconds: Optional[float] = Field(None, description="Service uptime")
    response_time_ms: Optional[float] = Field(
        None, description="Response time in milliseconds"
    )
    dependencies: Optional[List[str]] = Field(
        None, description="Service dependencies"
    )
    last_check: str = Field(..., description="Last health check time")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional health details"
    )

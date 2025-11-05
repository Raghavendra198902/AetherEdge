"""
Health check router for AetherEdge API

Provides health status endpoints for monitoring and load balancing.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Any
import time
import psutil
from datetime import datetime, timezone

from ..core.config import settings
from ..core.database import check_db_health
from ..core.monitoring import get_health_metrics

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str
    environment: str
    uptime_seconds: float
    services: Dict[str, Any]
    system: Dict[str, Any]


class HealthSummary(BaseModel):
    """Simple health status"""
    status: str
    timestamp: str


@router.get("/", response_model=HealthSummary, status_code=status.HTTP_200_OK)
async def health_check():
    """Simple health check endpoint"""
    return HealthSummary(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/detailed", response_model=HealthResponse,
            status_code=status.HTTP_200_OK)
async def detailed_health_check():
    """Detailed health check with service status"""
    
    # Check database health
    db_health = await check_db_health()
    
    # Get system metrics
    try:
        disk_usage = psutil.disk_usage('/')
        disk_percent = disk_usage.percent
    except Exception:
        disk_percent = 0
        
    try:
        if hasattr(psutil, 'getloadavg'):
            load_avg = psutil.getloadavg()
        else:
            load_avg = None
    except Exception:
        load_avg = None
    
    system_metrics = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": disk_percent,
        "load_average": load_avg
    }
    
    # Check service health
    services = {
        "database": db_health,
        "redis": {"status": "unknown"},  # Would implement Redis health check
        "modules": {
            "brahma": {
                "status": "healthy" if settings.BRAHMA_ENABLED else "disabled"
            },
            "vishnu": {
                "status": "healthy" if settings.VISHNU_ENABLED else "disabled"
            },
            "shiva": {
                "status": "healthy" if settings.SHIVA_ENABLED else "disabled"
            },
            "lakshmi": {
                "status": "healthy" if settings.LAKSHMI_ENABLED else "disabled"
            },
            "kali": {
                "status": "healthy" if settings.KALI_ENABLED else "disabled"
            }
        }
    }
    
    # Calculate overall status
    overall_status = "healthy"
    if db_health.get("status") != "healthy":
        overall_status = "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        uptime_seconds=time.time(),  # Would track actual uptime
        services=services,
        system=system_metrics
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Kubernetes readiness probe endpoint"""
    # Check if all required services are ready
    db_health = await check_db_health()
    
    if db_health.get("status") != "healthy":
        return {"status": "not_ready", "reason": "database_unavailable"}
    
    return {"status": "ready"}


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    # Basic liveness check - if the API is responding, it's alive
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/metrics")
async def health_metrics():
    """Get health-related metrics"""
    return get_health_metrics()

"""
🏥 Health Router - System Health Gateway
========================================

Routes for overall system health monitoring and diagnostics.
Provides consolidated health checks across all divine modules.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Any
import httpx
import logging
from datetime import datetime, timezone
import asyncio

from ..config import settings

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1/health",
    tags=["System Health"],
    responses={404: {"description": "Not found"}},
)

# Service endpoints mapping
SERVICES = {
    "brahma-blueprint": f"http://brahma-blueprint:{settings.BRAHMA_PORT}",
    "vishnu-orchestrator": f"http://vishnu-orchestrator:{settings.VISHNU_PORT}",  # noqa: E501
    "shiva-healer": f"http://shiva-healer:{settings.SHIVA_PORT}",
    "saraswati-knowledge": f"http://saraswati-knowledge:{settings.SARASWATI_PORT}",  # noqa: E501
    "lakshmi-finops": f"http://lakshmi-finops:{settings.LAKSHMI_PORT}",
    "kali-security": f"http://kali-security:{settings.KALI_PORT}",
    "hanuman-agents": f"http://hanuman-agents:{settings.HANUMAN_PORT}",
    "ganesha-rca": f"http://ganesha-rca:{settings.GANESHA_PORT}",
}


async def check_service_health(service_name: str, service_url: str) -> Dict[str, Any]:  # noqa: E501
    """Check health of a single service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{service_url}/health",
                timeout=5.0
            )
            return {
                "service": service_name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",  # noqa: E501
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "timestamp": datetime.now(timezone.utc),
                "details": response.json() if response.status_code == 200 else None  # noqa: E501
            }
    except Exception as e:
        return {
            "service": service_name,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        }


@router.get("/", status_code=status.HTTP_200_OK)
async def overall_health():
    """Check overall system health"""
    try:
        # Check all services concurrently
        health_checks = [
            check_service_health(name, url)
            for name, url in SERVICES.items()
        ]
        
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Process results
        service_statuses = []
        healthy_count = 0
        total_count = len(SERVICES)
        
        for result in results:
            if isinstance(result, Exception):
                service_statuses.append({
                    "service": "unknown",
                    "status": "error",
                    "error": str(result),
                    "timestamp": datetime.now(timezone.utc)
                })
            else:
                service_statuses.append(result)
                if result.get("status") == "healthy":
                    healthy_count += 1
        
        # Determine overall status
        if healthy_count == total_count:
            overall_status = "healthy"
        elif healthy_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc),
            "services": service_statuses,
            "summary": {
                "total_services": total_count,
                "healthy_services": healthy_count,
                "unhealthy_services": total_count - healthy_count,
                "health_percentage": (healthy_count / total_count) * 100
            },
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/services/{service_name}")
async def service_health(service_name: str):
    """Check health of a specific service"""
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {service_name} not found"
        )
    
    try:
        service_url = SERVICES[service_name]
        result = await check_service_health(service_name, service_url)
        
        if result.get("status") == "unhealthy":
            return result
        else:
            return result
            
    except Exception as e:
        logger.error(f"Health check for {service_name} failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check for {service_name} failed: {str(e)}"
        )


@router.get("/services")
async def list_services():
    """List all available services"""
    return {
        "services": list(SERVICES.keys()),
        "count": len(SERVICES),
        "timestamp": datetime.now(timezone.utc)
    }


@router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe endpoint"""
    try:
        # Quick health check of critical services (Trinity)
        critical_services = ["brahma-blueprint", "vishnu-orchestrator", "shiva-healer"]  # noqa: E501
        
        health_checks = [
            check_service_health(name, SERVICES[name])
            for name in critical_services
        ]
        
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        healthy_critical = 0
        for result in results:
            if not isinstance(result, Exception) and result.get("status") == "healthy":  # noqa: E501
                healthy_critical += 1
        
        # System is ready if at least 2 out of 3 critical services are healthy
        is_ready = healthy_critical >= 2
        
        return {
            "ready": is_ready,
            "critical_services_healthy": healthy_critical,
            "critical_services_total": len(critical_services),
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        }


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    try:
        # Simple liveness check - API Gateway is responsive
        return {
            "alive": True,
            "timestamp": datetime.now(timezone.utc),
            "uptime_seconds": 0  # TODO: Track actual uptime
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Liveness check failed: {str(e)}"
        )


@router.get("/metrics")
async def health_metrics():
    """Get health metrics for monitoring systems"""
    try:
        # Check all services
        health_checks = [
            check_service_health(name, url)
            for name, url in SERVICES.items()
        ]
        
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Calculate metrics
        metrics = {
            "aetheredge_services_total": len(SERVICES),
            "aetheredge_services_healthy": 0,
            "aetheredge_services_unhealthy": 0,
            "aetheredge_health_percentage": 0.0,
            "aetheredge_response_times": {}
        }
        
        for result in results:
            if isinstance(result, Exception):
                metrics["aetheredge_services_unhealthy"] += 1
            else:
                if result.get("status") == "healthy":
                    metrics["aetheredge_services_healthy"] += 1
                    # Record response time
                    service_name = result.get("service", "unknown")
                    response_time = result.get("response_time_ms", 0)
                    metrics["aetheredge_response_times"][service_name] = response_time  # noqa: E501
                else:
                    metrics["aetheredge_services_unhealthy"] += 1
        
        # Calculate health percentage
        total = metrics["aetheredge_services_total"]
        healthy = metrics["aetheredge_services_healthy"]
        metrics["aetheredge_health_percentage"] = (healthy / total) * 100 if total > 0 else 0  # noqa: E501
        
        return {
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Health metrics failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health metrics failed: {str(e)}"
        )


@router.get("/dashboard")
async def health_dashboard():
    """Get comprehensive health dashboard data"""
    try:
        # Get detailed health information
        health_checks = [
            check_service_health(name, url)
            for name, url in SERVICES.items()
        ]
        
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Organize by service categories
        trinity_services = []
        intelligence_services = []
        execution_services = []
        
        for result in results:
            if isinstance(result, Exception):
                continue
                
            service_name = result.get("service", "")
            
            if service_name in ["brahma-blueprint", "vishnu-orchestrator", "shiva-healer"]:  # noqa: E501
                trinity_services.append(result)
            elif service_name in ["saraswati-knowledge", "lakshmi-finops", "kali-security"]:  # noqa: E501
                intelligence_services.append(result)
            elif service_name in ["hanuman-agents", "ganesha-rca"]:
                execution_services.append(result)
        
        return {
            "dashboard": {
                "trinity_core": {
                    "services": trinity_services,
                    "healthy_count": len([s for s in trinity_services if s.get("status") == "healthy"])  # noqa: E501
                },
                "intelligence_layer": {
                    "services": intelligence_services,
                    "healthy_count": len([s for s in intelligence_services if s.get("status") == "healthy"])  # noqa: E501
                },
                "execution_layer": {
                    "services": execution_services,
                    "healthy_count": len([s for s in execution_services if s.get("status") == "healthy"])  # noqa: E501
                }
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Health dashboard failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health dashboard failed: {str(e)}"
        )

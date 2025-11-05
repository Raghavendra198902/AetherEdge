"""
🔥 Shiva Router - Healing Gateway
=================================

Routes for the Shiva Healer Engine.
Shiva, the transformer, provides AI healing and auto-remediation capabilities.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Dict, Any
import httpx
import logging
from datetime import datetime, timezone
from pydantic import BaseModel

from ..config import settings
from ..middleware.auth import verify_token

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1/shiva",
    tags=["Shiva - Healer"],
    responses={404: {"description": "Not found"}},
)

# Shiva service URL
SHIVA_SERVICE_URL = f"http://shiva-healer:{settings.SHIVA_PORT}"


# Request/Response Models
class IncidentRequest(BaseModel):
    title: str
    description: str
    severity: str  # "critical", "high", "medium", "low"
    affected_resources: List[str]
    symptoms: List[str]
    metadata: Optional[Dict[str, Any]] = {}
    auto_heal: bool = True


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    status: str  # "open", "investigating", "healing", "resolved", "closed"
    affected_resources: List[str]
    symptoms: List[str]
    root_cause: Optional[str] = None
    resolution_steps: List[str] = []
    healing_actions: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    auto_heal_enabled: bool = True


class HealingActionRequest(BaseModel):
    name: str
    description: str
    action_type: str  # "script", "playbook", "api_call", "manual"
    parameters: Dict[str, Any]
    conditions: Optional[Dict[str, Any]] = {}
    retry_config: Optional[Dict[str, Any]] = {}
    enabled: bool = True


class HealingActionResponse(BaseModel):
    id: str
    name: str
    description: str
    action_type: str
    parameters: Dict[str, Any]
    conditions: Dict[str, Any]
    retry_config: Dict[str, Any]
    enabled: bool
    success_rate: float = 0.0
    execution_count: int = 0
    last_executed: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class DiagnosticRequest(BaseModel):
    resource_id: str
    resource_type: str
    symptoms: List[str]
    context: Optional[Dict[str, Any]] = {}


# Health check endpoint
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Check Shiva service health"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SHIVA_SERVICE_URL}/health",
                timeout=10.0
            )
            return {
                "service": "shiva-healer",
                "status": "healthy" if response.status_code == 200 else "unhealthy",  # noqa: E501
                "timestamp": datetime.now(timezone.utc),
                "version": "1.0.0"
            }
    except Exception as e:
        logger.error(f"Shiva health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Shiva service unavailable: {str(e)}"
        )


# Incident Management Endpoints
@router.post("/incidents", response_model=IncidentResponse)
async def create_incident(
    incident: IncidentRequest,
    token: str = Depends(verify_token)
):
    """Create a new incident for healing"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SHIVA_SERVICE_URL}/api/v1/incidents",
                json=incident.dict(),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to create incident: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create incident: {str(e)}"
        )


@router.get("/incidents", response_model=List[IncidentResponse])
async def list_incidents(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    status_filter: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """List all incidents with optional filtering"""
    try:
        params = {"skip": skip, "limit": limit}
        if severity:
            params["severity"] = severity
        if status_filter:
            params["status"] = status_filter

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SHIVA_SERVICE_URL}/api/v1/incidents",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to list incidents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list incidents: {str(e)}"
        )


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    token: str = Depends(verify_token)
):
    """Get a specific incident by ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SHIVA_SERVICE_URL}/api/v1/incidents/{incident_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        logger.error(f"Failed to get incident: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get incident: {str(e)}"
        )


@router.post("/incidents/{incident_id}/heal")
async def heal_incident(
    incident_id: str,
    manual_actions: Optional[List[str]] = None,
    token: str = Depends(verify_token)
):
    """Trigger healing for an incident"""
    try:
        payload = {"manual_actions": manual_actions or []}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SHIVA_SERVICE_URL}/api/v1/incidents/{incident_id}/heal",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=60.0  # Healing can take longer
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        logger.error(f"Failed to heal incident: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to heal incident: {str(e)}"
        )


@router.post("/incidents/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    resolution_summary: str,
    resolution_steps: List[str],
    token: str = Depends(verify_token)
):
    """Mark an incident as resolved"""
    try:
        payload = {
            "resolution_summary": resolution_summary,
            "resolution_steps": resolution_steps
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SHIVA_SERVICE_URL}/api/v1/incidents/{incident_id}/resolve",  # noqa: E501
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        logger.error(f"Failed to resolve incident: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve incident: {str(e)}"
        )


# Healing Actions Management
@router.post("/healing-actions", response_model=HealingActionResponse)
async def create_healing_action(
    action: HealingActionRequest,
    token: str = Depends(verify_token)
):
    """Create a new healing action"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SHIVA_SERVICE_URL}/api/v1/healing-actions",
                json=action.dict(),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to create healing action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create healing action: {str(e)}"
        )


@router.get("/healing-actions", response_model=List[HealingActionResponse])
async def list_healing_actions(
    skip: int = 0,
    limit: int = 100,
    action_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    token: str = Depends(verify_token)
):
    """List all healing actions with optional filtering"""
    try:
        params = {"skip": skip, "limit": limit}
        if action_type:
            params["action_type"] = action_type
        if enabled is not None:
            params["enabled"] = enabled

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SHIVA_SERVICE_URL}/api/v1/healing-actions",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to list healing actions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list healing actions: {str(e)}"
        )


@router.get("/healing-actions/{action_id}", response_model=HealingActionResponse)  # noqa: E501
async def get_healing_action(
    action_id: str,
    token: str = Depends(verify_token)
):
    """Get a specific healing action by ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SHIVA_SERVICE_URL}/api/v1/healing-actions/{action_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Healing action {action_id} not found"
            )
        logger.error(f"Failed to get healing action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get healing action: {str(e)}"
        )


@router.post("/healing-actions/{action_id}/execute")
async def execute_healing_action(
    action_id: str,
    execution_context: Optional[Dict[str, Any]] = None,
    token: str = Depends(verify_token)
):
    """Execute a healing action manually"""
    try:
        payload = {"execution_context": execution_context or {}}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SHIVA_SERVICE_URL}/api/v1/healing-actions/{action_id}/execute",  # noqa: E501
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=60.0  # Execution can take longer
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Healing action {action_id} not found"
            )
        logger.error(f"Failed to execute healing action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute healing action: {str(e)}"
        )


# Diagnostics
@router.post("/diagnostics/analyze")
async def analyze_resource(
    diagnostic: DiagnosticRequest,
    token: str = Depends(verify_token)
):
    """Analyze a resource for potential issues"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SHIVA_SERVICE_URL}/api/v1/diagnostics/analyze",
                json=diagnostic.dict(),
                headers={"Authorization": f"Bearer {token}"},
                timeout=60.0  # Analysis can take longer
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to analyze resource: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze resource: {str(e)}"
        )


@router.get("/diagnostics/health-summary")
async def get_health_summary(
    resource_type: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """Get overall health summary of monitored resources"""
    try:
        params = {}
        if resource_type:
            params["resource_type"] = resource_type

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SHIVA_SERVICE_URL}/api/v1/diagnostics/health-summary",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get health summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get health summary: {str(e)}"
        )


# Auto-scaling
@router.post("/autoscaling/rules")
async def create_autoscaling_rule(
    rule_config: Dict[str, Any],
    token: str = Depends(verify_token)
):
    """Create an auto-scaling rule"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SHIVA_SERVICE_URL}/api/v1/autoscaling/rules",
                json=rule_config,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to create autoscaling rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create autoscaling rule: {str(e)}"
        )


@router.get("/autoscaling/rules")
async def list_autoscaling_rules(
    skip: int = 0,
    limit: int = 100,
    resource_type: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """List auto-scaling rules"""
    try:
        params = {"skip": skip, "limit": limit}
        if resource_type:
            params["resource_type"] = resource_type

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SHIVA_SERVICE_URL}/api/v1/autoscaling/rules",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to list autoscaling rules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list autoscaling rules: {str(e)}"
        )


# Analytics & Metrics
@router.get("/analytics/healing-stats")
async def get_healing_statistics(
    days: int = 30,
    token: str = Depends(verify_token)
):
    """Get healing statistics and metrics"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SHIVA_SERVICE_URL}/api/v1/analytics/healing-stats",
                params={"days": days},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get healing statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get healing statistics: {str(e)}"
        )


@router.get("/analytics/incident-trends")
async def get_incident_trends(
    days: int = 30,
    token: str = Depends(verify_token)
):
    """Get incident trends and patterns"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SHIVA_SERVICE_URL}/api/v1/analytics/incident-trends",
                params={"days": days},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get incident trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get incident trends: {str(e)}"
        )

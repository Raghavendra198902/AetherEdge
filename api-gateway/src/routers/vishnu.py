"""
🔱 Vishnu Router - Orchestration Gateway
========================================

Routes for the Vishnu Orchestrator Engine.
Vishnu, the preserver, manages policy enforcement and orchestration.
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
    prefix="/api/v1/vishnu",
    tags=["Vishnu - Orchestrator"],
    responses={404: {"description": "Not found"}},
)

# Vishnu service URL
VISHNU_SERVICE_URL = f"http://vishnu-orchestrator:{settings.VISHNU_PORT}"


# Request/Response Models
class PolicyRequest(BaseModel):
    name: str
    description: str
    policy_type: str  # "security", "compliance", "resource", etc.
    rules: Dict[str, Any]
    enabled: bool = True
    priority: int = 100
    tags: Optional[List[str]] = []


class PolicyResponse(BaseModel):
    id: str
    name: str
    description: str
    policy_type: str
    rules: Dict[str, Any]
    enabled: bool
    priority: int
    status: str
    created_at: datetime
    updated_at: datetime
    applied_count: int = 0
    violation_count: int = 0


class WorkflowRequest(BaseModel):
    name: str
    description: str
    trigger_type: str  # "manual", "schedule", "event"
    trigger_config: Dict[str, Any]
    steps: List[Dict[str, Any]]
    enabled: bool = True
    tags: Optional[List[str]] = []


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str
    trigger_type: str
    trigger_config: Dict[str, Any]
    steps: List[Dict[str, Any]]
    enabled: bool
    status: str
    created_at: datetime
    updated_at: datetime
    execution_count: int = 0
    success_rate: float = 0.0


# Health check endpoint
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Check Vishnu service health"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VISHNU_SERVICE_URL}/health",
                timeout=10.0
            )
            return {
                "service": "vishnu-orchestrator",
                "status": "healthy" if response.status_code == 200 else "unhealthy",  # noqa: E501
                "timestamp": datetime.now(timezone.utc),
                "version": "1.0.0"
            }
    except Exception as e:
        logger.error(f"Vishnu health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Vishnu service unavailable: {str(e)}"
        )


# Policy Management Endpoints
@router.post("/policies", response_model=PolicyResponse)
async def create_policy(
    policy: PolicyRequest,
    token: str = Depends(verify_token)
):
    """Create a new policy"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{VISHNU_SERVICE_URL}/api/v1/policies",
                json=policy.dict(),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to create policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create policy: {str(e)}"
        )


@router.get("/policies", response_model=List[PolicyResponse])
async def list_policies(
    skip: int = 0,
    limit: int = 100,
    policy_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    token: str = Depends(verify_token)
):
    """List all policies with optional filtering"""
    try:
        params = {"skip": skip, "limit": limit}
        if policy_type:
            params["policy_type"] = policy_type
        if enabled is not None:
            params["enabled"] = enabled

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VISHNU_SERVICE_URL}/api/v1/policies",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to list policies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list policies: {str(e)}"
        )


@router.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    token: str = Depends(verify_token)
):
    """Get a specific policy by ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VISHNU_SERVICE_URL}/api/v1/policies/{policy_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy {policy_id} not found"
            )
        logger.error(f"Failed to get policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get policy: {str(e)}"
        )


@router.put("/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    policy: PolicyRequest,
    token: str = Depends(verify_token)
):
    """Update an existing policy"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{VISHNU_SERVICE_URL}/api/v1/policies/{policy_id}",
                json=policy.dict(),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy {policy_id} not found"
            )
        logger.error(f"Failed to update policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update policy: {str(e)}"
        )


@router.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: str,
    token: str = Depends(verify_token)
):
    """Delete a policy"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{VISHNU_SERVICE_URL}/api/v1/policies/{policy_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return {"message": f"Policy {policy_id} deleted successfully"}
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy {policy_id} not found"
            )
        logger.error(f"Failed to delete policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete policy: {str(e)}"
        )


# Workflow Management Endpoints
@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowRequest,
    token: str = Depends(verify_token)
):
    """Create a new workflow"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{VISHNU_SERVICE_URL}/api/v1/workflows",
                json=workflow.dict(),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to create workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    trigger_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    token: str = Depends(verify_token)
):
    """List all workflows with optional filtering"""
    try:
        params = {"skip": skip, "limit": limit}
        if trigger_type:
            params["trigger_type"] = trigger_type
        if enabled is not None:
            params["enabled"] = enabled

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VISHNU_SERVICE_URL}/api/v1/workflows",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to list workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    token: str = Depends(verify_token)
):
    """Get a specific workflow by ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VISHNU_SERVICE_URL}/api/v1/workflows/{workflow_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )
        logger.error(f"Failed to get workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow: {str(e)}"
        )


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    execution_params: Optional[Dict[str, Any]] = None,
    token: str = Depends(verify_token)
):
    """Execute a workflow manually"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{VISHNU_SERVICE_URL}/api/v1/workflows/{workflow_id}/execute",  # noqa: E501
                json=execution_params or {},
                headers={"Authorization": f"Bearer {token}"},
                timeout=60.0  # Execution can take longer
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )
        logger.error(f"Failed to execute workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}"
        )


# Policy Enforcement
@router.post("/policies/{policy_id}/enforce")
async def enforce_policy(
    policy_id: str,
    target_resources: Optional[List[str]] = None,
    token: str = Depends(verify_token)
):
    """Enforce a policy on target resources"""
    try:
        payload = {"target_resources": target_resources or []}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{VISHNU_SERVICE_URL}/api/v1/policies/{policy_id}/enforce",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy {policy_id} not found"
            )
        logger.error(f"Failed to enforce policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enforce policy: {str(e)}"
        )


@router.get("/policies/{policy_id}/violations")
async def get_policy_violations(
    policy_id: str,
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(verify_token)
):
    """Get policy violations"""
    try:
        params = {"skip": skip, "limit": limit}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VISHNU_SERVICE_URL}/api/v1/policies/{policy_id}/violations",  # noqa: E501
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy {policy_id} not found"
            )
        logger.error(f"Failed to get policy violations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get policy violations: {str(e)}"
        )


# Analytics & Metrics
@router.get("/analytics/policies")
async def get_policy_analytics(
    days: int = 30,
    token: str = Depends(verify_token)
):
    """Get policy analytics"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VISHNU_SERVICE_URL}/api/v1/analytics/policies",
                params={"days": days},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get policy analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get policy analytics: {str(e)}"
        )


@router.get("/analytics/workflows")
async def get_workflow_analytics(
    days: int = 30,
    token: str = Depends(verify_token)
):
    """Get workflow execution analytics"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VISHNU_SERVICE_URL}/api/v1/analytics/workflows",
                params={"days": days},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get workflow analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow analytics: {str(e)}"
        )

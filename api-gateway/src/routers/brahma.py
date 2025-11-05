"""
🎨 Brahma Router - Blueprint Generation Gateway
==============================================

Routes for the Brahma Blueprint Engine.
Brahma, the creator, generates divine blueprints for infrastructure.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import httpx
import logging
from datetime import datetime
from pydantic import BaseModel

from ..config import settings
from ..middleware.auth import verify_token

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1/brahma",
    tags=["Brahma - Blueprint Engine"],
    responses={404: {"description": "Not found"}},
)

# Brahma service URL
BRAHMA_SERVICE_URL = f"http://brahma-blueprint:{settings.BRAHMA_PORT}"

# Request/Response Models
class BlueprintRequest(BaseModel):
    name: str
    description: str
    infrastructure_type: str  # "kubernetes", "terraform", "ansible", etc.
    requirements: Dict[str, Any]
    tags: Optional[List[str]] = []

class BlueprintResponse(BaseModel):
    id: str
    name: str
    description: str
    infrastructure_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Health check endpoint
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Check Brahma service health"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BRAHMA_SERVICE_URL}/health", timeout=10.0)
            return {
                "service": "brahma-blueprint",
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "timestamp": datetime.utcnow(),
                "version": "1.0.0"
            }
    except Exception as e:
        logger.error(f"Brahma health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Brahma service unavailable: {str(e)}"
        )

# Blueprint Management Endpoints

@router.post("/blueprints", response_model=BlueprintResponse)
async def create_blueprint(
    blueprint: BlueprintRequest,
    token: str = Depends(verify_token)
):
    """Create a new infrastructure blueprint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BRAHMA_SERVICE_URL}/api/v1/blueprints",
                json=blueprint.dict(),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to create blueprint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create blueprint: {str(e)}"
        )

@router.get("/blueprints", response_model=List[BlueprintResponse])
async def list_blueprints(
    skip: int = 0,
    limit: int = 100,
    infrastructure_type: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """List all blueprints with optional filtering"""
    try:
        params = {"skip": skip, "limit": limit}
        if infrastructure_type:
            params["infrastructure_type"] = infrastructure_type
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BRAHMA_SERVICE_URL}/api/v1/blueprints",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to list blueprints: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list blueprints: {str(e)}"
        )

@router.get("/blueprints/{blueprint_id}", response_model=BlueprintResponse)
async def get_blueprint(
    blueprint_id: str,
    token: str = Depends(verify_token)
):
    """Get a specific blueprint by ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BRAHMA_SERVICE_URL}/api/v1/blueprints/{blueprint_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint {blueprint_id} not found"
            )
        logger.error(f"Failed to get blueprint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get blueprint: {str(e)}"
        )

@router.put("/blueprints/{blueprint_id}", response_model=BlueprintResponse)
async def update_blueprint(
    blueprint_id: str,
    blueprint: BlueprintRequest,
    token: str = Depends(verify_token)
):
    """Update an existing blueprint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{BRAHMA_SERVICE_URL}/api/v1/blueprints/{blueprint_id}",
                json=blueprint.dict(),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint {blueprint_id} not found"
            )
        logger.error(f"Failed to update blueprint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update blueprint: {str(e)}"
        )

@router.delete("/blueprints/{blueprint_id}")
async def delete_blueprint(
    blueprint_id: str,
    token: str = Depends(verify_token)
):
    """Delete a blueprint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{BRAHMA_SERVICE_URL}/api/v1/blueprints/{blueprint_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return {"message": f"Blueprint {blueprint_id} deleted successfully"}
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint {blueprint_id} not found"
            )
        logger.error(f"Failed to delete blueprint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete blueprint: {str(e)}"
        )

# Blueprint Generation Endpoints

@router.post("/blueprints/{blueprint_id}/generate")
async def generate_blueprint(
    blueprint_id: str,
    generate_params: Optional[Dict[str, Any]] = None,
    token: str = Depends(verify_token)
):
    """Generate infrastructure code from blueprint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BRAHMA_SERVICE_URL}/api/v1/blueprints/{blueprint_id}/generate",
                json=generate_params or {},
                headers={"Authorization": f"Bearer {token}"},
                timeout=60.0  # Generation can take longer
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint {blueprint_id} not found"
            )
        logger.error(f"Failed to generate blueprint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate blueprint: {str(e)}"
        )

@router.post("/blueprints/{blueprint_id}/validate")
async def validate_blueprint(
    blueprint_id: str,
    token: str = Depends(verify_token)
):
    """Validate a blueprint configuration"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BRAHMA_SERVICE_URL}/api/v1/blueprints/{blueprint_id}/validate",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blueprint {blueprint_id} not found"
            )
        logger.error(f"Failed to validate blueprint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate blueprint: {str(e)}"
        )

# Template Management

@router.get("/templates")
async def list_templates(
    template_type: Optional[str] = None,
    token: str = Depends(verify_token)
):
    """List available blueprint templates"""
    try:
        params = {}
        if template_type:
            params["template_type"] = template_type
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BRAHMA_SERVICE_URL}/api/v1/templates",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to list templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )

@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    token: str = Depends(verify_token)
):
    """Get a specific template"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BRAHMA_SERVICE_URL}/api/v1/templates/{template_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found"
            )
        logger.error(f"Failed to get template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )

# Analytics & Metrics

@router.get("/analytics/usage")
async def get_usage_analytics(
    days: int = 30,
    token: str = Depends(verify_token)
):
    """Get blueprint usage analytics"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BRAHMA_SERVICE_URL}/api/v1/analytics/usage",
                params={"days": days},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get usage analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage analytics: {str(e)}"
        )

@router.get("/analytics/popular-templates")
async def get_popular_templates(
    limit: int = 10,
    token: str = Depends(verify_token)
):
    """Get most popular blueprint templates"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BRAHMA_SERVICE_URL}/api/v1/analytics/popular-templates",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to get popular templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get popular templates: {str(e)}"
        )

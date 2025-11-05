"""
Ganesha RCA Engine - API Routes
Sacred problem resolution and root cause analysis endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..database.connection import rca_db

# Configure divine logging
logger = logging.getLogger("ganesha.wisdom")

# Sacred router for wisdom endpoints
router = APIRouter(prefix="/api/v1/ganesha", tags=["ganesha", "rca"])


@router.get("/", response_model=Dict[str, Any])
async def get_wisdom_status():
    """Get Ganesha RCA Engine status and divine wisdom"""
    return {
        "deity": "Ganesha",
        "domain": "Wisdom & Problem Resolution",
        "status": "active",
        "blessing": "May divine wisdom illuminate the path to resolution",
        "capabilities": [
            "Root Cause Analysis",
            "Incident Management",
            "Problem Resolution",
            "Knowledge Management",
            "Automated Remediation",
            "Pattern Recognition"
        ],
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# ============================================================================
# Incident Management
# ============================================================================

@router.post("/incidents", response_model=Dict[str, str])
async def create_incident(incident_data: Dict[str, Any]):
    """Create a new incident"""
    try:
        incident_id = await rca_db.store_incident(incident_data)
        return {"incident_id": incident_id, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating incident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents", response_model=List[Dict[str, Any]])
async def get_incidents(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    service: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get incidents with filtering"""
    try:
        filters = {}
        if severity:
            filters["severity"] = severity
        if status:
            filters["status"] = status
        if service:
            filters["affected_services"] = {"$in": [service]}
        
        incidents = await rca_db.get_incidents(
            filters=filters, limit=limit, skip=skip
        )
        return incidents
    except Exception as e:
        logger.error(f"Error retrieving incidents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/incidents/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    status: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """Update incident status"""
    try:
        updated = await rca_db.update_incident_status(
            incident_id, status, metadata
        )
        if updated:
            return {"status": "updated"}
        else:
            raise HTTPException(status_code=404, detail="Incident not found")
    except Exception as e:
        logger.error(f"Error updating incident status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RCA Analysis
# ============================================================================

@router.post("/analyses", response_model=Dict[str, str])
async def create_rca_analysis(analysis_data: Dict[str, Any]):
    """Create a new RCA analysis"""
    try:
        analysis_id = await rca_db.store_rca_analysis(analysis_data)
        return {"analysis_id": analysis_id, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating RCA analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyses", response_model=List[Dict[str, Any]])
async def get_rca_analyses(
    incident_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get RCA analyses with filtering"""
    try:
        filters = {}
        if incident_id:
            filters["incident_id"] = incident_id
        if status:
            filters["status"] = status
        
        analyses = await rca_db.get_rca_analyses(
            filters=filters, limit=limit, skip=skip
        )
        return analyses
    except Exception as e:
        logger.error(f"Error retrieving RCA analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Knowledge Base
# ============================================================================

@router.post("/knowledge", response_model=Dict[str, str])
async def create_knowledge_entry(knowledge_data: Dict[str, Any]):
    """Create a new knowledge base entry"""
    try:
        entry_id = await rca_db.store_knowledge_entry(knowledge_data)
        return {"entry_id": entry_id, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating knowledge entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/search", response_model=List[Dict[str, Any]])
async def search_knowledge_base(
    symptoms: List[str] = Query(..., description="Symptoms to search for"),
    problem_type: Optional[str] = None
):
    """Search knowledge base for similar problems"""
    try:
        entries = await rca_db.search_knowledge_base(
            symptoms=symptoms, problem_type=problem_type
        )
        return entries
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Metrics & Dashboard
# ============================================================================

@router.get("/metrics", response_model=Dict[str, Any])
async def get_rca_metrics(timeframe_hours: int = Query(24, ge=1, le=168)):
    """Get RCA metrics for dashboard"""
    try:
        metrics = await rca_db.get_rca_metrics(timeframe_hours)
        return metrics
    except Exception as e:
        logger.error(f"Error retrieving RCA metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_rca_dashboard():
    """Get comprehensive RCA dashboard data"""
    try:
        # Get metrics for different timeframes
        metrics_24h = await rca_db.get_rca_metrics(24)
        metrics_7d = await rca_db.get_rca_metrics(168)
        
        # Get recent incidents
        recent_incidents = await rca_db.get_incidents(limit=20)
        
        # Get active analyses
        active_analyses = await rca_db.get_rca_analyses(
            filters={"status": {"$in": ["pending", "in_progress"]}},
            limit=10
        )
        
        return {
            "metrics_24h": metrics_24h,
            "metrics_7d": metrics_7d,
            "recent_incidents": recent_incidents,
            "active_analyses": active_analyses,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating RCA dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint for Ganesha RCA Engine"""
    try:
        # Check database connection
        db_status = "connected" if rca_db.connected else "disconnected"
        
        return {
            "status": "healthy" if rca_db.connected else "unhealthy",
            "database": db_status,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

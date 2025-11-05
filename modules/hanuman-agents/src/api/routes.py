"""
Hanuman Agents Engine - API Routes
Sacred execution and distributed agent management endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..models.agents import AgentStatus, TaskStatus, AgentType
from ..database.connection import agents_db

# Configure divine logging
logger = logging.getLogger("hanuman.execution")

# Sacred router for execution endpoints
router = APIRouter(prefix="/api/v1/hanuman", tags=["hanuman", "agents"])


@router.get("/", response_model=Dict[str, Any])
async def get_execution_status():
    """Get Hanuman Agents Engine status and divine execution"""
    return {
        "deity": "Hanuman",
        "domain": "Execution & Agents",
        "status": "active",
        "blessing": "May divine strength empower your automation",
        "capabilities": [
            "Distributed Agent Management",
            "Task Orchestration",
            "Workflow Automation",
            "Resource Scaling",
            "Multi-Cloud Execution",
            "Edge Computing"
        ],
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# ============================================================================
# Agent Management
# ============================================================================

@router.post("/agents", response_model=Dict[str, str])
async def register_agent(agent_data: Dict[str, Any]):
    """Register a new agent"""
    try:
        agent_id = await agents_db.store_agent(agent_data)
        return {"agent_id": agent_id, "status": "registered"}
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents", response_model=List[Dict[str, Any]])
async def get_agents(
    status: Optional[AgentStatus] = None,
    agent_type: Optional[AgentType] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get agents with filtering"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if agent_type:
            filters["agent_type"] = agent_type
        
        agents = await agents_db.get_agents(
            filters=filters, limit=limit, skip=skip
        )
        return agents
    except Exception as e:
        logger.error(f"Error retrieving agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agents/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status: AgentStatus,
    metadata: Optional[Dict[str, Any]] = None
):
    """Update agent status and heartbeat"""
    try:
        updated = await agents_db.update_agent_status(
            agent_id, status, metadata
        )
        if updated:
            return {"status": "updated"}
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except Exception as e:
        logger.error(f"Error updating agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/available", response_model=List[Dict[str, Any]])
async def get_available_agents(
    capabilities: Optional[List[str]] = Query(None),
    agent_type: Optional[AgentType] = None
):
    """Get available agents for task assignment"""
    try:
        agents = await agents_db.get_available_agents(
            capabilities=capabilities, agent_type=agent_type
        )
        return agents
    except Exception as e:
        logger.error(f"Error getting available agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Task Management
# ============================================================================

@router.post("/tasks", response_model=Dict[str, str])
async def create_task(task_data: Dict[str, Any]):
    """Create a new task"""
    try:
        task_id = await agents_db.store_task(task_data)
        return {"task_id": task_id, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks", response_model=List[Dict[str, Any]])
async def get_tasks(
    status: Optional[TaskStatus] = None,
    agent_id: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get tasks with filtering"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if agent_id:
            filters["agent_id"] = agent_id
        if task_type:
            filters["task_type"] = task_type
        
        tasks = await agents_db.get_tasks(
            filters=filters, limit=limit, skip=skip
        )
        return tasks
    except Exception as e:
        logger.error(f"Error retrieving tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    status: TaskStatus,
    result_data: Optional[Dict[str, Any]] = None
):
    """Update task status and result"""
    try:
        updated = await agents_db.update_task_status(
            task_id, status, result_data
        )
        if updated:
            return {"status": "updated"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        logger.error(f"Error updating task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Metrics & Dashboard
# ============================================================================

@router.get("/metrics", response_model=Dict[str, Any])
async def get_agent_metrics(timeframe_hours: int = Query(24, ge=1, le=168)):
    """Get agent metrics for dashboard"""
    try:
        metrics = await agents_db.get_agent_metrics(timeframe_hours)
        return metrics
    except Exception as e:
        logger.error(f"Error retrieving agent metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_agents_dashboard():
    """Get comprehensive agents dashboard data"""
    try:
        # Get metrics for different timeframes
        metrics_24h = await agents_db.get_agent_metrics(24)
        metrics_7d = await agents_db.get_agent_metrics(168)
        
        # Get recent tasks
        recent_tasks = await agents_db.get_tasks(limit=20)
        
        # Get active agents
        active_agents = await agents_db.get_agents(
            filters={"status": {"$in": ["active", "idle"]}},
            limit=50
        )
        
        return {
            "metrics_24h": metrics_24h,
            "metrics_7d": metrics_7d,
            "recent_tasks": recent_tasks,
            "active_agents": active_agents,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating agents dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint for Hanuman Agents Engine"""
    try:
        # Check database connection
        db_status = "connected" if agents_db.connected else "disconnected"
        
        return {
            "status": "healthy" if agents_db.connected else "unhealthy",
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

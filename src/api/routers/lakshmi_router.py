"""
Lakshmi (FinOps Intelligence) API Router

Provides API endpoints for cost optimization, budget management,
and financial operations intelligence.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from ..core.config import settings
from ..core.database import get_db
from ..core.monitoring import metrics

router = APIRouter()


class CostAnalysis(BaseModel):
    """Cost analysis response"""
    resource_id: str
    current_cost: float
    projected_cost: float
    optimization_potential: float
    recommendations: List[str]
    period: str


class BudgetAlert(BaseModel):
    """Budget alert"""
    alert_id: str
    budget_name: str
    current_spend: float
    budget_limit: float
    threshold_percent: float
    severity: str
    created_at: str


class OptimizationRequest(BaseModel):
    """Cost optimization request"""
    resource_ids: List[str] = Field(..., description="Resources to optimize")
    optimization_type: str = Field(
        default="cost", description="Type of optimization"
    )


@router.get("/cost-analysis")
async def get_cost_analysis(
    resource_id: Optional[str] = None,
    period: str = "monthly",
    db=Depends(get_db)
):
    """Get cost analysis for resources"""
    
    if not settings.LAKSHMI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Lakshmi service is disabled"
        )
    
    try:
        # Mock data
        analysis = CostAnalysis(
            resource_id=resource_id or "all-resources",
            current_cost=1250.50,
            projected_cost=1400.75,
            optimization_potential=200.25,
            recommendations=[
                "Right-size EC2 instances",
                "Use reserved instances",
                "Optimize storage costs"
            ],
            period=period
        )
        
        metrics.record_module_status("lakshmi", True)
        
        return analysis
        
    except Exception as e:
        metrics.record_module_status("lakshmi", False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cost analysis failed: {str(e)}"
        )


@router.get("/budget-alerts")
async def get_budget_alerts(db=Depends(get_db)):
    """Get budget alerts"""
    
    try:
        # Mock data
        alerts = [
            BudgetAlert(
                alert_id=str(uuid.uuid4()),
                budget_name="Monthly Infrastructure",
                current_spend=850.0,
                budget_limit=1000.0,
                threshold_percent=85.0,
                severity="warning",
                created_at=datetime.now(timezone.utc).isoformat()
            )
        ]
        
        return {"alerts": alerts, "total": len(alerts)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get budget alerts: {str(e)}"
        )


@router.post("/optimize")
async def optimize_costs(request: OptimizationRequest, db=Depends(get_db)):
    """Generate cost optimization recommendations"""
    
    try:
        optimization_id = str(uuid.uuid4())
        
        recommendations = []
        for resource_id in request.resource_ids:
            recommendations.append({
                "resource_id": resource_id,
                "current_cost": 150.0,
                "optimized_cost": 120.0,
                "savings": 30.0,
                "actions": ["downsize", "schedule"]
            })
        
        return {
            "optimization_id": optimization_id,
            "type": request.optimization_type,
            "recommendations": recommendations,
            "total_savings": sum(r["savings"] for r in recommendations),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cost optimization failed: {str(e)}"
        )


@router.get("/spending-trends")
async def get_spending_trends(
    period: str = "30d",
    granularity: str = "daily",
    db=Depends(get_db)
):
    """Get spending trends and forecasts"""
    
    try:
        # Mock trend data
        trends = {
            "period": period,
            "granularity": granularity,
            "current_spend": 1250.50,
            "previous_period": 1100.25,
            "trend": "increasing",
            "forecast": 1400.0,
            "data_points": [
                {"date": "2024-01-01", "amount": 35.50},
                {"date": "2024-01-02", "amount": 42.25}
            ]
        }
        
        return trends
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get spending trends: {str(e)}"
        )

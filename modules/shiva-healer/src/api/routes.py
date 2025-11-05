"""
⚡ Shiva - Divine Healing Engine
===============================

The transformation module that performs adaptive healing and auto-remediation.
Shiva, the destroyer and transformer, eliminates dysfunction and regenerates 
optimal system states through AI-powered healing cycles.

Features:
- Predictive failure detection
- Automated healing workflows
- Performance optimization
- Capacity auto-scaling
- Chaos engineering
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import uuid

from ..services.anomaly_detector import AnomalyDetector
from ..services.healing_engine import HealingEngine
from ..services.performance_optimizer import PerformanceOptimizer
from ..services.chaos_engineer import ChaosEngineer
from ..models.healing import HealingAction, HealingStatus, AnomalyReport
from ..middleware.auth import verify_token, require_permission

logger = logging.getLogger(__name__)

router = APIRouter()


class AnomalyDetectionRequest(BaseModel):
    """Request for anomaly detection analysis"""
    resource_ids: List[str] = Field(..., description="Resources to analyze")
    time_window: int = Field(default=24, description="Hours of historical data")
    sensitivity: str = Field(default="medium", description="Detection sensitivity")
    include_predictions: bool = Field(default=True, description="Include future predictions")


class HealingRequest(BaseModel):
    """Request for automated healing action"""
    resource_id: str = Field(..., description="Target resource for healing")
    issue_type: str = Field(..., description="Type of issue to heal")
    healing_strategy: str = Field(default="conservative", description="Healing approach")
    auto_approve: bool = Field(default=False, description="Auto-approve healing actions")
    rollback_enabled: bool = Field(default=True, description="Enable automatic rollback")


class PerformanceOptimizationRequest(BaseModel):
    """Request for performance optimization"""
    target_resources: List[str] = Field(..., description="Resources to optimize")
    optimization_goals: List[str] = Field(..., description="Optimization objectives")
    constraints: Dict[str, Any] = Field(default={}, description="Optimization constraints")
    duration: int = Field(default=30, description="Optimization duration in days")


class ChaosExperimentRequest(BaseModel):
    """Request for chaos engineering experiment"""
    experiment_name: str = Field(..., description="Experiment name")
    target_environment: str = Field(..., description="Target environment")
    failure_scenarios: List[Dict[str, Any]] = Field(..., description="Failure scenarios")
    duration_minutes: int = Field(default=30, description="Experiment duration")
    abort_conditions: List[str] = Field(default=[], description="Auto-abort conditions")


# Initialize services
anomaly_detector = AnomalyDetector()
healing_engine = HealingEngine()
performance_optimizer = PerformanceOptimizer()
chaos_engineer = ChaosEngineer()


@router.post("/anomalies/detect")
@require_permission("shiva:anomaly:detect")
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    background_tasks: BackgroundTasks,
    token_data=Depends(verify_token)
):
    """
    🔍 Detect anomalies using AI-powered analysis
    
    Like Shiva's third eye that sees beyond the surface, this endpoint
    reveals hidden patterns and emerging issues in your infrastructure.
    """
    try:
        detection_id = str(uuid.uuid4())
        
        logger.info(f"Starting anomaly detection {detection_id} for {len(request.resource_ids)} resources")
        
        # Start background anomaly detection
        background_tasks.add_task(
            detect_anomalies_async,
            detection_id,
            request,
            token_data.username
        )
        
        return {
            "detection_id": detection_id,
            "status": "analyzing",
            "resource_count": len(request.resource_ids),
            "estimated_completion": datetime.utcnow() + timedelta(minutes=5)
        }
        
    except Exception as e:
        logger.error(f"Error starting anomaly detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start anomaly detection")


@router.get("/anomalies/{detection_id}")
@require_permission("shiva:anomaly:read")
async def get_anomaly_report(detection_id: str, token_data=Depends(verify_token)):
    """
    📊 Get anomaly detection results
    """
    try:
        report = await AnomalyReport.get(detection_id)
        if not report:
            raise HTTPException(status_code=404, detail="Anomaly report not found")
        
        return {
            "detection_id": report.id,
            "status": report.status,
            "anomalies": report.anomalies,
            "risk_score": report.overall_risk_score,
            "predictions": report.future_predictions,
            "recommendations": report.healing_recommendations,
            "created_at": report.created_at
        }
        
    except Exception as e:
        logger.error(f"Error retrieving anomaly report {detection_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve report")


@router.post("/healing/actions")
@require_permission("shiva:healing:create")
async def create_healing_action(
    request: HealingRequest,
    background_tasks: BackgroundTasks,
    token_data=Depends(verify_token)
):
    """
    ⚡ Create and execute healing action
    
    Channel Shiva's transformative power to heal infrastructure issues
    and restore optimal performance states.
    """
    try:
        healing_id = str(uuid.uuid4())
        
        logger.info(f"Creating healing action {healing_id} for resource {request.resource_id}")
        
        # Validate healing strategy
        strategy_validation = await healing_engine.validate_strategy(
            resource_id=request.resource_id,
            issue_type=request.issue_type,
            strategy=request.healing_strategy
        )
        
        if not strategy_validation.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid healing strategy: {strategy_validation.errors}"
            )
        
        # Create healing action record
        healing_action = HealingAction(
            id=healing_id,
            resource_id=request.resource_id,
            issue_type=request.issue_type,
            healing_strategy=request.healing_strategy,
            status=HealingStatus.PLANNED,
            auto_approve=request.auto_approve,
            rollback_enabled=request.rollback_enabled,
            created_by=token_data.username,
            created_at=datetime.utcnow()
        )
        
        await healing_action.save()
        
        # Execute healing if auto-approved
        if request.auto_approve:
            background_tasks.add_task(
                execute_healing_async,
                healing_id,
                token_data.username
            )
            status = "executing"
        else:
            status = "pending_approval"
        
        return {
            "healing_id": healing_id,
            "status": status,
            "resource_id": request.resource_id,
            "estimated_duration": strategy_validation.estimated_duration
        }
        
    except Exception as e:
        logger.error(f"Error creating healing action: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create healing action")


@router.get("/healing/actions/{healing_id}")
@require_permission("shiva:healing:read")
async def get_healing_action(healing_id: str, token_data=Depends(verify_token)):
    """
    📊 Get healing action status and results
    """
    try:
        healing_action = await HealingAction.get(healing_id)
        if not healing_action:
            raise HTTPException(status_code=404, detail="Healing action not found")
        
        return {
            "healing_id": healing_action.id,
            "resource_id": healing_action.resource_id,
            "status": healing_action.status,
            "progress": healing_action.progress_percentage,
            "steps_completed": healing_action.steps_completed,
            "total_steps": healing_action.total_steps,
            "results": healing_action.execution_results,
            "rollback_available": healing_action.rollback_enabled and healing_action.rollback_data,
            "created_at": healing_action.created_at,
            "completed_at": healing_action.completed_at
        }
        
    except Exception as e:
        logger.error(f"Error retrieving healing action {healing_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve healing action")


@router.post("/healing/actions/{healing_id}/approve")
@require_permission("shiva:healing:approve")
async def approve_healing_action(
    healing_id: str,
    background_tasks: BackgroundTasks,
    token_data=Depends(verify_token)
):
    """
    ✅ Approve pending healing action for execution
    """
    try:
        healing_action = await HealingAction.get(healing_id)
        if not healing_action:
            raise HTTPException(status_code=404, detail="Healing action not found")
        
        if healing_action.status != HealingStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=400,
                detail="Healing action is not pending approval"
            )
        
        # Update status and execute
        healing_action.status = HealingStatus.APPROVED
        healing_action.approved_by = token_data.username
        healing_action.approved_at = datetime.utcnow()
        await healing_action.save()
        
        # Start execution
        background_tasks.add_task(
            execute_healing_async,
            healing_id,
            token_data.username
        )
        
        return {
            "healing_id": healing_id,
            "status": "approved",
            "message": "Healing action approved and execution started"
        }
        
    except Exception as e:
        logger.error(f"Error approving healing action {healing_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to approve healing action")


@router.post("/optimization/performance")
@require_permission("shiva:optimization:create")
async def optimize_performance(
    request: PerformanceOptimizationRequest,
    background_tasks: BackgroundTasks,
    token_data=Depends(verify_token)
):
    """
    🚀 Start performance optimization campaign
    
    Harness Shiva's transformative energy to continuously optimize
    resource performance and eliminate inefficiencies.
    """
    try:
        optimization_id = str(uuid.uuid4())
        
        logger.info(f"Starting performance optimization {optimization_id}")
        
        # Validate optimization goals
        validation_result = await performance_optimizer.validate_goals(
            resources=request.target_resources,
            goals=request.optimization_goals,
            constraints=request.constraints
        )
        
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid optimization configuration: {validation_result.errors}"
            )
        
        # Start optimization process
        background_tasks.add_task(
            run_performance_optimization_async,
            optimization_id,
            request,
            token_data.username
        )
        
        return {
            "optimization_id": optimization_id,
            "status": "initializing",
            "target_resources": request.target_resources,
            "goals": request.optimization_goals,
            "duration_days": request.duration
        }
        
    except Exception as e:
        logger.error(f"Error starting performance optimization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start optimization")


@router.post("/chaos/experiments")
@require_permission("shiva:chaos:create")
async def create_chaos_experiment(
    request: ChaosExperimentRequest,
    background_tasks: BackgroundTasks,
    token_data=Depends(verify_token)
):
    """
    🌪️ Create and execute chaos engineering experiment
    
    Invoke Shiva's destructive aspect to test system resilience
    through controlled failure scenarios.
    """
    try:
        experiment_id = str(uuid.uuid4())
        
        logger.info(f"Creating chaos experiment {experiment_id}: {request.experiment_name}")
        
        # Validate experiment safety
        safety_check = await chaos_engineer.validate_experiment_safety(
            environment=request.target_environment,
            scenarios=request.failure_scenarios
        )
        
        if not safety_check.is_safe:
            raise HTTPException(
                status_code=400,
                detail=f"Unsafe experiment configuration: {safety_check.warnings}"
            )
        
        # Start chaos experiment
        background_tasks.add_task(
            run_chaos_experiment_async,
            experiment_id,
            request,
            token_data.username
        )
        
        return {
            "experiment_id": experiment_id,
            "status": "initializing",
            "name": request.experiment_name,
            "duration_minutes": request.duration_minutes,
            "scenarios_count": len(request.failure_scenarios)
        }
        
    except Exception as e:
        logger.error(f"Error creating chaos experiment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create chaos experiment")


@router.get("/chaos/experiments/{experiment_id}")
@require_permission("shiva:chaos:read")
async def get_chaos_experiment(experiment_id: str, token_data=Depends(verify_token)):
    """
    📊 Get chaos experiment status and results
    """
    try:
        experiment = await chaos_engineer.get_experiment(experiment_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="Chaos experiment not found")
        
        return {
            "experiment_id": experiment.id,
            "name": experiment.name,
            "status": experiment.status,
            "progress": experiment.progress_percentage,
            "scenarios_executed": experiment.scenarios_executed,
            "total_scenarios": experiment.total_scenarios,
            "resilience_score": experiment.resilience_score,
            "issues_discovered": experiment.issues_discovered,
            "started_at": experiment.started_at,
            "completed_at": experiment.completed_at
        }
        
    except Exception as e:
        logger.error(f"Error retrieving chaos experiment {experiment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve experiment")


@router.get("/healing/dashboard")
@require_permission("shiva:healing:read")
async def get_healing_dashboard(token_data=Depends(verify_token)):
    """
    📊 Get comprehensive healing and optimization dashboard
    """
    try:
        dashboard_data = await healing_engine.get_dashboard_metrics()
        
        return {
            "system_health_score": dashboard_data.overall_health_score,
            "active_healings": dashboard_data.active_healing_count,
            "recent_anomalies": dashboard_data.recent_anomalies,
            "performance_trends": dashboard_data.performance_trends,
            "optimization_savings": dashboard_data.optimization_savings,
            "chaos_resilience_score": dashboard_data.chaos_resilience_score,
            "recommendations": dashboard_data.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error retrieving healing dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard")


# Background task functions
async def detect_anomalies_async(
    detection_id: str,
    request: AnomalyDetectionRequest,
    username: str
):
    """
    Background task for anomaly detection
    """
    try:
        logger.info(f"Running anomaly detection {detection_id}")
        
        anomalies = []
        predictions = []
        
        for resource_id in request.resource_ids:
            # Detect current anomalies
            resource_anomalies = await anomaly_detector.detect_resource_anomalies(
                resource_id=resource_id,
                time_window_hours=request.time_window,
                sensitivity=request.sensitivity
            )
            anomalies.extend(resource_anomalies)
            
            # Generate predictions if requested
            if request.include_predictions:
                resource_predictions = await anomaly_detector.predict_future_issues(
                    resource_id=resource_id,
                    prediction_horizon_hours=24
                )
                predictions.extend(resource_predictions)
        
        # Calculate overall risk score
        risk_score = sum(a.severity_score for a in anomalies) / len(anomalies) if anomalies else 0
        
        # Generate healing recommendations
        recommendations = await healing_engine.generate_recommendations(anomalies)
        
        # Save results
        report = AnomalyReport(
            id=detection_id,
            anomalies=anomalies,
            future_predictions=predictions,
            overall_risk_score=risk_score,
            healing_recommendations=recommendations,
            status="completed",
            created_by=username,
            created_at=datetime.utcnow()
        )
        
        await report.save()
        
        logger.info(f"Anomaly detection {detection_id} completed")
        
    except Exception as e:
        logger.error(f"Error in anomaly detection {detection_id}: {str(e)}")


async def execute_healing_async(healing_id: str, username: str):
    """
    Background task for healing execution
    """
    try:
        logger.info(f"Executing healing action {healing_id}")
        
        healing_action = await HealingAction.get(healing_id)
        healing_action.status = HealingStatus.EXECUTING
        healing_action.executed_by = username
        healing_action.started_at = datetime.utcnow()
        await healing_action.save()
        
        # Execute healing steps
        execution_result = await healing_engine.execute_healing(
            resource_id=healing_action.resource_id,
            issue_type=healing_action.issue_type,
            strategy=healing_action.healing_strategy
        )
        
        # Update status based on result
        if execution_result.success:
            healing_action.status = HealingStatus.COMPLETED
            healing_action.execution_results = execution_result.results
        else:
            healing_action.status = HealingStatus.FAILED
            healing_action.error_message = execution_result.error_message
        
        healing_action.completed_at = datetime.utcnow()
        await healing_action.save()
        
        logger.info(f"Healing action {healing_id} completed")
        
    except Exception as e:
        logger.error(f"Error executing healing action {healing_id}: {str(e)}")


async def run_performance_optimization_async(
    optimization_id: str,
    request: PerformanceOptimizationRequest,
    username: str
):
    """
    Background task for performance optimization
    """
    try:
        logger.info(f"Running performance optimization {optimization_id}")
        
        optimization_results = await performance_optimizer.optimize_resources(
            resources=request.target_resources,
            goals=request.optimization_goals,
            constraints=request.constraints,
            duration_days=request.duration
        )
        
        logger.info(f"Performance optimization {optimization_id} completed")
        
    except Exception as e:
        logger.error(f"Error in performance optimization {optimization_id}: {str(e)}")


async def run_chaos_experiment_async(
    experiment_id: str,
    request: ChaosExperimentRequest,
    username: str
):
    """
    Background task for chaos experiment execution
    """
    try:
        logger.info(f"Running chaos experiment {experiment_id}")
        
        experiment_results = await chaos_engineer.execute_experiment(
            experiment_id=experiment_id,
            name=request.experiment_name,
            environment=request.target_environment,
            scenarios=request.failure_scenarios,
            duration_minutes=request.duration_minutes,
            abort_conditions=request.abort_conditions
        )
        
        logger.info(f"Chaos experiment {experiment_id} completed")
        
    except Exception as e:
        logger.error(f"Error in chaos experiment {experiment_id}: {str(e)}")

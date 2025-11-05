"""
🛡️ Vishnu - Divine Orchestration Engine
=======================================

The preservation module that maintains system harmony through policy orchestration.
Vishnu, the preserver, ensures continuous compliance and operational balance.

Features:
- Policy-as-Code enforcement
- Continuous compliance monitoring
- Automated remediation workflows
- Multi-cloud orchestration
- Service mesh management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import uuid

from ..services.policy_engine import PolicyEngine
from ..services.compliance_monitor import ComplianceMonitor
from ..services.orchestration_engine import OrchestrationEngine
from ..models.policy import Policy, PolicyStatus, ComplianceResult
from ..middleware.auth import verify_token, require_permission

logger = logging.getLogger(__name__)

router = APIRouter()


class PolicyRequest(BaseModel):
    """Request model for policy creation"""
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    policy_type: str = Field(..., description="Policy type (security, cost, compliance)")
    rules: Dict[str, Any] = Field(..., description="Policy rules in OPA Rego format")
    scope: List[str] = Field(..., description="Resource scope for policy")
    enforcement_mode: str = Field(default="monitor", description="enforce, monitor, or warn")
    compliance_framework: Optional[str] = Field(None, description="Associated compliance framework")
    severity: str = Field(default="medium", description="Policy violation severity")


class PolicyResponse(BaseModel):
    """Response model for policy operations"""
    policy_id: str
    name: str
    status: PolicyStatus
    created_at: datetime
    last_evaluated: Optional[datetime] = None
    compliance_score: Optional[float] = None
    violations_count: int = 0
    enforcement_actions: List[str] = []


class OrchestrationRequest(BaseModel):
    """Request model for orchestration workflows"""
    workflow_name: str = Field(..., description="Workflow name")
    target_resources: List[str] = Field(..., description="Target resource IDs")
    actions: List[Dict[str, Any]] = Field(..., description="Orchestration actions")
    schedule: Optional[str] = Field(None, description="Cron schedule for recurring workflows")
    approval_required: bool = Field(default=False, description="Require manual approval")


class ComplianceCheckRequest(BaseModel):
    """Request model for compliance checks"""
    resources: List[str] = Field(..., description="Resources to check")
    frameworks: List[str] = Field(..., description="Compliance frameworks to validate")
    generate_report: bool = Field(default=True, description="Generate compliance report")


# Initialize services
policy_engine = PolicyEngine()
compliance_monitor = ComplianceMonitor()
orchestration_engine = OrchestrationEngine()


@router.post("/policies", response_model=PolicyResponse)
@require_permission("vishnu:policy:create")
async def create_policy(
    request: PolicyRequest,
    token_data=Depends(verify_token)
):
    """
    🛡️ Create a new policy for continuous enforcement
    
    Like Vishnu's divine laws that maintain cosmic order, these policies 
    ensure infrastructure remains aligned with organizational dharma.
    """
    try:
        policy_id = str(uuid.uuid4())
        
        logger.info(f"Creating policy {policy_id} for user {token_data.username}")
        
        # Validate policy rules
        validation_result = await policy_engine.validate_policy_rules(request.rules)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid policy rules: {validation_result.errors}"
            )
        
        # Create policy record
        policy = Policy(
            id=policy_id,
            name=request.name,
            description=request.description,
            policy_type=request.policy_type,
            rules=request.rules,
            scope=request.scope,
            enforcement_mode=request.enforcement_mode,
            compliance_framework=request.compliance_framework,
            severity=request.severity,
            status=PolicyStatus.ACTIVE,
            created_by=token_data.username,
            created_at=datetime.utcnow()
        )
        
        await policy.save()
        
        # Deploy policy to enforcement engine
        await policy_engine.deploy_policy(policy)
        
        return PolicyResponse(
            policy_id=policy_id,
            name=request.name,
            status=PolicyStatus.ACTIVE,
            created_at=policy.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating policy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create policy: {str(e)}")


@router.get("/policies/{policy_id}", response_model=PolicyResponse)
@require_permission("vishnu:policy:read")
async def get_policy(policy_id: str, token_data=Depends(verify_token)):
    """
    📖 Get policy details and compliance status
    """
    try:
        policy = await Policy.get(policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Get latest compliance metrics
        compliance_metrics = await compliance_monitor.get_policy_metrics(policy_id)
        
        return PolicyResponse(
            policy_id=policy.id,
            name=policy.name,
            status=policy.status,
            created_at=policy.created_at,
            last_evaluated=compliance_metrics.last_evaluated,
            compliance_score=compliance_metrics.compliance_score,
            violations_count=compliance_metrics.violations_count,
            enforcement_actions=compliance_metrics.recent_actions
        )
        
    except Exception as e:
        logger.error(f"Error retrieving policy {policy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve policy")


@router.get("/policies")
@require_permission("vishnu:policy:read")
async def list_policies(
    skip: int = 0,
    limit: int = 100,
    policy_type: Optional[str] = None,
    status: Optional[PolicyStatus] = None,
    token_data=Depends(verify_token)
):
    """
    📚 List all policies with filtering options
    """
    try:
        policies = await Policy.list(
            skip=skip,
            limit=limit,
            policy_type=policy_type,
            status=status
        )
        
        return {
            "policies": [
                PolicyResponse(
                    policy_id=p.id,
                    name=p.name,
                    status=p.status,
                    created_at=p.created_at
                ) for p in policies
            ],
            "total": len(policies)
        }
        
    except Exception as e:
        logger.error(f"Error listing policies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list policies")


@router.post("/compliance/check")
@require_permission("vishnu:compliance:check")
async def run_compliance_check(
    request: ComplianceCheckRequest,
    background_tasks: BackgroundTasks,
    token_data=Depends(verify_token)
):
    """
    🔍 Run compliance check against specified frameworks
    """
    try:
        check_id = str(uuid.uuid4())
        
        logger.info(f"Starting compliance check {check_id} for {len(request.resources)} resources")
        
        # Start background compliance check
        background_tasks.add_task(
            run_compliance_check_async,
            check_id,
            request,
            token_data.username
        )
        
        return {
            "check_id": check_id,
            "status": "initiated",
            "resources_count": len(request.resources),
            "frameworks": request.frameworks
        }
        
    except Exception as e:
        logger.error(f"Error initiating compliance check: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate compliance check")


@router.post("/orchestration/workflows")
@require_permission("vishnu:orchestration:create")
async def create_workflow(
    request: OrchestrationRequest,
    background_tasks: BackgroundTasks,
    token_data=Depends(verify_token)
):
    """
    🔄 Create and execute orchestration workflow
    """
    try:
        workflow_id = str(uuid.uuid4())
        
        logger.info(f"Creating workflow {workflow_id}: {request.workflow_name}")
        
        # Validate workflow actions
        validation_result = await orchestration_engine.validate_workflow(request.actions)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid workflow: {validation_result.errors}"
            )
        
        # Create workflow execution
        if request.approval_required:
            # Queue for approval
            workflow_status = "pending_approval"
        else:
            # Execute immediately
            background_tasks.add_task(
                execute_workflow_async,
                workflow_id,
                request,
                token_data.username
            )
            workflow_status = "executing"
        
        return {
            "workflow_id": workflow_id,
            "status": workflow_status,
            "target_resources": request.target_resources,
            "actions_count": len(request.actions)
        }
        
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create workflow")


@router.get("/orchestration/workflows/{workflow_id}")
@require_permission("vishnu:orchestration:read")
async def get_workflow_status(workflow_id: str, token_data=Depends(verify_token)):
    """
    📊 Get workflow execution status and results
    """
    try:
        workflow = await orchestration_engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_id": workflow.id,
            "name": workflow.name,
            "status": workflow.status,
            "progress": workflow.progress_percentage,
            "started_at": workflow.started_at,
            "completed_at": workflow.completed_at,
            "results": workflow.execution_results,
            "errors": workflow.error_messages
        }
        
    except Exception as e:
        logger.error(f"Error retrieving workflow {workflow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workflow")


@router.get("/compliance/dashboard")
@require_permission("vishnu:compliance:read")
async def get_compliance_dashboard(token_data=Depends(verify_token)):
    """
    📊 Get overall compliance dashboard metrics
    """
    try:
        dashboard_data = await compliance_monitor.get_dashboard_metrics()
        
        return {
            "overall_compliance_score": dashboard_data.overall_score,
            "frameworks": dashboard_data.framework_scores,
            "critical_violations": dashboard_data.critical_violations,
            "trending": dashboard_data.trending_metrics,
            "recent_checks": dashboard_data.recent_checks,
            "policy_coverage": dashboard_data.policy_coverage,
            "remediation_status": dashboard_data.remediation_status
        }
        
    except Exception as e:
        logger.error(f"Error retrieving compliance dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard")


@router.post("/policies/{policy_id}/remediate")
@require_permission("vishnu:policy:remediate")
async def remediate_policy_violations(
    policy_id: str,
    background_tasks: BackgroundTasks,
    token_data=Depends(verify_token)
):
    """
    🔧 Trigger automated remediation for policy violations
    """
    try:
        policy = await Policy.get(policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Get current violations
        violations = await compliance_monitor.get_policy_violations(policy_id)
        
        if not violations:
            return {
                "message": "No violations found for remediation",
                "policy_id": policy_id
            }
        
        # Start remediation process
        remediation_id = str(uuid.uuid4())
        background_tasks.add_task(
            remediate_violations_async,
            remediation_id,
            policy_id,
            violations,
            token_data.username
        )
        
        return {
            "remediation_id": remediation_id,
            "policy_id": policy_id,
            "violations_count": len(violations),
            "status": "initiated"
        }
        
    except Exception as e:
        logger.error(f"Error starting remediation for policy {policy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start remediation")


# Background task functions
async def run_compliance_check_async(
    check_id: str,
    request: ComplianceCheckRequest,
    username: str
):
    """
    Background task to run comprehensive compliance check
    """
    try:
        logger.info(f"Running compliance check {check_id}")
        
        check_results = []
        
        for framework in request.frameworks:
            for resource in request.resources:
                result = await compliance_monitor.check_resource_compliance(
                    resource_id=resource,
                    framework=framework
                )
                check_results.append(result)
        
        # Store results
        compliance_result = ComplianceResult(
            check_id=check_id,
            framework_results=check_results,
            overall_score=sum(r.score for r in check_results) / len(check_results),
            checked_by=username,
            checked_at=datetime.utcnow()
        )
        
        await compliance_result.save()
        
        # Generate report if requested
        if request.generate_report:
            await compliance_monitor.generate_compliance_report(check_id)
        
        logger.info(f"Compliance check {check_id} completed")
        
    except Exception as e:
        logger.error(f"Error in compliance check {check_id}: {str(e)}")


async def execute_workflow_async(
    workflow_id: str,
    request: OrchestrationRequest,
    username: str
):
    """
    Background task to execute orchestration workflow
    """
    try:
        logger.info(f"Executing workflow {workflow_id}")
        
        execution_results = []
        
        for action in request.actions:
            result = await orchestration_engine.execute_action(
                action=action,
                target_resources=request.target_resources
            )
            execution_results.append(result)
        
        logger.info(f"Workflow {workflow_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {str(e)}")


async def remediate_violations_async(
    remediation_id: str,
    policy_id: str,
    violations: List[Any],
    username: str
):
    """
    Background task for automated violation remediation
    """
    try:
        logger.info(f"Starting remediation {remediation_id} for policy {policy_id}")
        
        remediation_results = []
        
        for violation in violations:
            result = await policy_engine.remediate_violation(violation)
            remediation_results.append(result)
        
        logger.info(f"Remediation {remediation_id} completed")
        
    except Exception as e:
        logger.error(f"Error in remediation {remediation_id}: {str(e)}")

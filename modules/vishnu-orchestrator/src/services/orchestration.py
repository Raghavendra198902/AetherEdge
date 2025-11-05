"""
🛡️ Vishnu Orchestration Engine
===============================

Core orchestration engine that manages infrastructure workflows,
policy enforcement, and system preservation across the platform.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PolicySeverity(Enum):
    """Policy violation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class WorkflowStep:
    """Individual workflow step"""
    id: str
    name: str
    type: str  # blueprint, deploy, validate, approve
    depends_on: List[str]
    parameters: Dict[str, Any]
    timeout_seconds: int = 300
    retry_count: int = 3
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class Workflow:
    """Complete workflow definition"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: WorkflowStatus
    created_by: str
    created_at: datetime
    metadata: Dict[str, Any]
    policies: List[str] = None


@dataclass
class PolicyRule:
    """Policy enforcement rule"""
    id: str
    name: str
    description: str
    condition: str  # Policy condition expression
    action: str  # allow, deny, warn, require_approval
    severity: PolicySeverity
    tags: List[str]
    enabled: bool = True


class OrchestrationEngine:
    """
    Core orchestration engine for managing infrastructure workflows
    """
    
    def __init__(self):
        self.active_workflows: Dict[str, Workflow] = {}
        self.policy_rules: Dict[str, PolicyRule] = {}
        self.step_executors = self._initialize_step_executors()
        self._initialize_default_policies()
    
    async def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        created_by: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Convert step dictionaries to WorkflowStep objects
            workflow_steps = []
            for step_data in steps:
                step = WorkflowStep(
                    id=step_data.get("id", str(uuid.uuid4())),
                    name=step_data["name"],
                    type=step_data["type"],
                    depends_on=step_data.get("depends_on", []),
                    parameters=step_data.get("parameters", {}),
                    timeout_seconds=step_data.get("timeout_seconds", 300),
                    retry_count=step_data.get("retry_count", 3)
                )
                workflow_steps.append(step)
            
            # Create workflow
            workflow = Workflow(
                id=workflow_id,
                name=name,
                description=description,
                steps=workflow_steps,
                status=WorkflowStatus.PENDING,
                created_by=created_by,
                created_at=datetime.now(timezone.utc),
                metadata=metadata or {},
                policies=[]
            )
            
            # Validate workflow
            await self._validate_workflow(workflow)
            
            # Apply policy checks
            policy_violations = await self._check_policies(workflow)
            if policy_violations:
                logger.warning(
                    "Policy violations found for workflow %s: %s",
                    workflow_id, policy_violations
                )
            
            # Store workflow
            self.active_workflows[workflow_id] = workflow
            
            logger.info("Workflow created: %s", workflow_id)
            return workflow_id
            
        except Exception as e:
            logger.error("Error creating workflow: %s", str(e))
            raise
    
    async def start_workflow(self, workflow_id: str) -> bool:
        """Start workflow execution"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if workflow.status != WorkflowStatus.PENDING:
                raise ValueError(
                    f"Workflow {workflow_id} is not in pending state"
                )
            
            workflow.status = WorkflowStatus.RUNNING
            
            # Start workflow execution in background
            asyncio.create_task(self._execute_workflow(workflow))
            
            logger.info("Workflow started: %s", workflow_id)
            return True
            
        except Exception as e:
            logger.error("Error starting workflow %s: %s", workflow_id, str(e))
            raise
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "created_by": workflow.created_by,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "type": step.type,
                    "status": step.status.value,
                    "started_at": (
                        step.started_at.isoformat() if step.started_at else None
                    ),
                    "completed_at": (
                        step.completed_at.isoformat() if step.completed_at else None
                    ),
                    "error_message": step.error_message
                }
                for step in workflow.steps
            ]
        }
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause workflow execution"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.PAUSED
            logger.info("Workflow paused: %s", workflow_id)
            return True
        
        return False
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume paused workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if workflow.status == WorkflowStatus.PAUSED:
            workflow.status = WorkflowStatus.RUNNING
            asyncio.create_task(self._execute_workflow(workflow))
            logger.info("Workflow resumed: %s", workflow_id)
            return True
        
        return False
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel workflow execution"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.status = WorkflowStatus.CANCELLED
        logger.info("Workflow cancelled: %s", workflow_id)
        return True
    
    async def _execute_workflow(self, workflow: Workflow):
        """Execute workflow steps"""
        try:
            logger.info("Executing workflow: %s", workflow.id)
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(workflow.steps)
            
            # Execute steps in dependency order
            completed_steps = set()
            
            while len(completed_steps) < len(workflow.steps):
                if workflow.status != WorkflowStatus.RUNNING:
                    logger.info(
                        "Workflow execution stopped: %s (status: %s)",
                        workflow.id, workflow.status.value
                    )
                    break
                
                # Find steps ready to execute
                ready_steps = []
                for step in workflow.steps:
                    if (step.status == WorkflowStatus.PENDING and
                        all(dep in completed_steps for dep in step.depends_on)):
                        ready_steps.append(step)
                
                if not ready_steps:
                    # Check if we're waiting for something or if there's a deadlock
                    running_steps = [
                        s for s in workflow.steps 
                        if s.status == WorkflowStatus.RUNNING
                    ]
                    
                    if not running_steps:
                        logger.error(
                            "Workflow deadlock detected: %s", workflow.id
                        )
                        workflow.status = WorkflowStatus.FAILED
                        break
                    
                    # Wait for running steps to complete
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    task = asyncio.create_task(self._execute_step(step))
                    tasks.append(task)
                
                # Wait for steps to complete
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Update completed steps
                    for step in ready_steps:
                        if step.status == WorkflowStatus.COMPLETED:
                            completed_steps.add(step.id)
                        elif step.status == WorkflowStatus.FAILED:
                            logger.error(
                                "Step failed: %s in workflow %s",
                                step.id, workflow.id
                            )
                            workflow.status = WorkflowStatus.FAILED
                            return
            
            # Check final status
            if len(completed_steps) == len(workflow.steps):
                workflow.status = WorkflowStatus.COMPLETED
                logger.info("Workflow completed successfully: %s", workflow.id)
            
        except Exception as e:
            logger.error(
                "Error executing workflow %s: %s", workflow.id, str(e)
            )
            workflow.status = WorkflowStatus.FAILED
    
    async def _execute_step(self, step: WorkflowStep):
        """Execute a single workflow step"""
        try:
            step.status = WorkflowStatus.RUNNING
            step.started_at = datetime.now(timezone.utc)
            
            logger.info("Executing step: %s (%s)", step.name, step.type)
            
            # Get step executor
            executor = self.step_executors.get(step.type)
            if not executor:
                raise ValueError(f"No executor found for step type: {step.type}")
            
            # Execute step with timeout and retries
            for attempt in range(step.retry_count + 1):
                try:
                    result = await asyncio.wait_for(
                        executor(step.parameters),
                        timeout=step.timeout_seconds
                    )
                    
                    step.status = WorkflowStatus.COMPLETED
                    step.completed_at = datetime.now(timezone.utc)
                    
                    logger.info(
                        "Step completed: %s (attempt %d)",
                        step.name, attempt + 1
                    )
                    return result
                    
                except asyncio.TimeoutError:
                    logger.warning(
                        "Step timeout: %s (attempt %d/%d)",
                        step.name, attempt + 1, step.retry_count + 1
                    )
                    if attempt == step.retry_count:
                        raise
                except Exception as e:
                    logger.warning(
                        "Step execution failed: %s (attempt %d/%d): %s",
                        step.name, attempt + 1, step.retry_count + 1, str(e)
                    )
                    if attempt == step.retry_count:
                        raise
                    
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)
            
        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.completed_at = datetime.now(timezone.utc)
            step.error_message = str(e)
            logger.error("Step failed: %s - %s", step.name, str(e))
    
    async def _validate_workflow(self, workflow: Workflow):
        """Validate workflow definition"""
        # Check for circular dependencies
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id: str) -> bool:
            if step_id in rec_stack:
                return True
            if step_id in visited:
                return False
            
            visited.add(step_id)
            rec_stack.add(step_id)
            
            # Find step
            step = next((s for s in workflow.steps if s.id == step_id), None)
            if step:
                for dep in step.depends_on:
                    if has_cycle(dep):
                        return True
            
            rec_stack.remove(step_id)
            return False
        
        # Check each step for cycles
        for step in workflow.steps:
            if has_cycle(step.id):
                raise ValueError(f"Circular dependency detected in workflow")
        
        # Validate step dependencies exist
        step_ids = {step.id for step in workflow.steps}
        for step in workflow.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise ValueError(
                        f"Step {step.id} depends on non-existent step {dep}"
                    )
    
    async def _check_policies(self, workflow: Workflow) -> List[str]:
        """Check workflow against policies"""
        violations = []
        
        for policy_id, policy in self.policy_rules.items():
            if not policy.enabled:
                continue
            
            # Simple policy evaluation (in production, use proper policy engine)
            if self._evaluate_policy_condition(policy.condition, workflow):
                if policy.action == "deny":
                    violations.append(
                        f"Policy {policy.name} denies this workflow"
                    )
                elif policy.action == "warn":
                    violations.append(
                        f"Policy {policy.name} warns about this workflow"
                    )
        
        return violations
    
    def _evaluate_policy_condition(
        self, condition: str, workflow: Workflow
    ) -> bool:
        """Evaluate policy condition (simplified)"""
        # In production, use a proper policy evaluation engine
        # This is a simplified version for demonstration
        
        if "production" in condition and "production" in workflow.metadata.get(
            "environment", ""
        ):
            return True
        
        if "sensitive_data" in condition:
            # Check if workflow involves sensitive data
            for step in workflow.steps:
                if "sensitive" in step.parameters.get("tags", []):
                    return True
        
        return False
    
    def _build_dependency_graph(
        self, steps: List[WorkflowStep]
    ) -> Dict[str, List[str]]:
        """Build dependency graph for steps"""
        graph = {}
        for step in steps:
            graph[step.id] = step.depends_on.copy()
        return graph
    
    def _initialize_step_executors(self) -> Dict[str, callable]:
        """Initialize step execution handlers"""
        return {
            "blueprint": self._execute_blueprint_step,
            "deploy": self._execute_deploy_step,
            "validate": self._execute_validate_step,
            "approve": self._execute_approve_step,
            "notify": self._execute_notify_step
        }
    
    async def _execute_blueprint_step(self, parameters: Dict[str, Any]):
        """Execute blueprint generation step"""
        # Simulate blueprint generation
        await asyncio.sleep(2)
        return {"status": "success", "blueprint_id": str(uuid.uuid4())}
    
    async def _execute_deploy_step(self, parameters: Dict[str, Any]):
        """Execute deployment step"""
        # Simulate deployment
        await asyncio.sleep(3)
        return {"status": "success", "deployment_id": str(uuid.uuid4())}
    
    async def _execute_validate_step(self, parameters: Dict[str, Any]):
        """Execute validation step"""
        # Simulate validation
        await asyncio.sleep(1)
        return {"status": "success", "validation_result": "passed"}
    
    async def _execute_approve_step(self, parameters: Dict[str, Any]):
        """Execute approval step"""
        # Simulate approval process
        await asyncio.sleep(1)
        return {"status": "success", "approved_by": "system"}
    
    async def _execute_notify_step(self, parameters: Dict[str, Any]):
        """Execute notification step"""
        # Simulate notification
        await asyncio.sleep(0.5)
        return {"status": "success", "notification_sent": True}
    
    def _initialize_default_policies(self):
        """Initialize default policy rules"""
        default_policies = [
            PolicyRule(
                id="prod_approval",
                name="Production Approval Required",
                description="All production deployments require approval",
                condition="environment == 'production'",
                action="require_approval",
                severity=PolicySeverity.ERROR,
                tags=["production", "approval"]
            ),
            PolicyRule(
                id="sensitive_data",
                name="Sensitive Data Handling",
                description="Workflows with sensitive data require encryption",
                condition="contains_sensitive_data == true",
                action="warn",
                severity=PolicySeverity.WARNING,
                tags=["security", "data"]
            ),
            PolicyRule(
                id="cost_limit",
                name="Cost Limit Check",
                description="Workflows exceeding cost limit require approval",
                condition="estimated_cost > 1000",
                action="require_approval",
                severity=PolicySeverity.WARNING,
                tags=["cost", "approval"]
            )
        ]
        
        for policy in default_policies:
            self.policy_rules[policy.id] = policy

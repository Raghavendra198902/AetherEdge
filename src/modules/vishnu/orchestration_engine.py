"""
AetherEdge - Vishnu Module: Policy & Orchestration Engine
The Preserver - Maintains service continuity and compliance

This module embodies the cosmic principle of Vishnu (Preserver) in digital form,
maintaining infrastructure harmony through policy enforcement and workflow
orchestration.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import yaml

# Setup logging
logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of policies"""
    SECURITY = "security"
    COMPLIANCE = "compliance"
    COST = "cost"
    PERFORMANCE = "performance"
    ACCESS = "access"
    BACKUP = "backup"
    MONITORING = "monitoring"


class PolicySeverity(Enum):
    """Policy violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class Policy:
    """Infrastructure policy definition"""
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    severity: PolicySeverity
    rules: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


@dataclass
class PolicyViolation:
    """Policy violation record"""
    violation_id: str
    policy_id: str
    resource_id: str
    resource_type: str
    violation_details: Dict[str, Any]
    severity: PolicySeverity
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    status: str = "open"  # open, resolved, ignored
    remediation_actions: List[str] = field(default_factory=list)


@dataclass
class WorkflowStep:
    """Individual workflow step"""
    step_id: str
    name: str
    step_type: str  # terraform, ansible, script, approval, condition
    config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout_minutes: int = 30
    retry_count: int = 3
    enabled: bool = True


@dataclass
class Workflow:
    """Infrastructure workflow definition"""
    workflow_id: str
    name: str
    description: str
    trigger_type: str  # manual, scheduled, event, policy
    steps: List[WorkflowStep]
    created_at: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    triggered_by: str = "system"
    context: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class PolicyEngine:
    """Policy management and enforcement engine"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.violations: List[PolicyViolation] = []
        self.load_default_policies()
        logger.info("Policy Engine initialized")
    
    def load_default_policies(self):
        """Load default enterprise policies"""
        default_policies = [
            Policy(
                policy_id="sec_001",
                name="Encryption at Rest Required",
                description="All storage resources must have encryption enabled",
                policy_type=PolicyType.SECURITY,
                severity=PolicySeverity.HIGH,
                rules={
                    "resource_types": ["storage", "database", "s3", "ebs"],
                    "required_attributes": ["encryption_enabled"],
                    "condition": "encryption_enabled == true"
                }
            ),
            Policy(
                policy_id="sec_002",
                name="No Public Database Access",
                description="Database instances cannot be publicly accessible",
                policy_type=PolicyType.SECURITY,
                severity=PolicySeverity.CRITICAL,
                rules={
                    "resource_types": ["database", "rds", "sql"],
                    "prohibited_attributes": ["publicly_accessible"],
                    "condition": "publicly_accessible != true"
                }
            ),
            Policy(
                policy_id="cost_001",
                name="Instance Size Limits",
                description="Restrict large instance types in non-prod environments",
                policy_type=PolicyType.COST,
                severity=PolicySeverity.MEDIUM,
                rules={
                    "resource_types": ["compute", "ec2", "vm"],
                    "environment_conditions": {
                        "dev": {"max_instance_size": "medium"},
                        "staging": {"max_instance_size": "large"}
                    }
                }
            ),
            Policy(
                policy_id="comp_001",
                name="Resource Tagging Required",
                description="All resources must have required tags",
                policy_type=PolicyType.COMPLIANCE,
                severity=PolicySeverity.MEDIUM,
                rules={
                    "resource_types": ["*"],
                    "required_tags": [
                        "Environment", "Owner", "Project", "CostCenter"
                    ]
                }
            )
        ]
        
        for policy in default_policies:
            self.policies[policy.policy_id] = policy
        
        logger.info(f"Loaded {len(default_policies)} default policies")
    
    def create_policy(self, policy: Policy) -> bool:
        """Create a new policy"""
        try:
            self.policies[policy.policy_id] = policy
            logger.info(f"Policy created: {policy.policy_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating policy {policy.policy_id}: {str(e)}")
            return False
    
    def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing policy"""
        try:
            if policy_id not in self.policies:
                logger.error(f"Policy not found: {policy_id}")
                return False
            
            policy = self.policies[policy_id]
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            policy.updated_at = datetime.now()
            logger.info(f"Policy updated: {policy_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating policy {policy_id}: {str(e)}")
            return False
    
    def evaluate_resource(self, resource: Dict[str, Any]) -> List[PolicyViolation]:
        """Evaluate resource against all applicable policies"""
        violations = []
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            
            violation = self._check_policy_compliance(resource, policy)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_policy_compliance(
        self, resource: Dict[str, Any], policy: Policy
    ) -> Optional[PolicyViolation]:
        """Check if resource complies with specific policy"""
        try:
            resource_type = resource.get("type", "").lower()
            rules = policy.rules
            
            # Check if policy applies to this resource type
            applicable_types = rules.get("resource_types", [])
            if "*" not in applicable_types and resource_type not in applicable_types:
                return None
            
            # Check required attributes
            required_attrs = rules.get("required_attributes", [])
            for attr in required_attrs:
                if attr not in resource.get("attributes", {}):
                    return self._create_violation(
                        resource, policy, f"Missing required attribute: {attr}"
                    )
            
            # Check prohibited attributes
            prohibited_attrs = rules.get("prohibited_attributes", [])
            for attr in prohibited_attrs:
                if resource.get("attributes", {}).get(attr) is True:
                    return self._create_violation(
                        resource, policy, f"Prohibited attribute present: {attr}"
                    )
            
            # Check required tags
            required_tags = rules.get("required_tags", [])
            resource_tags = resource.get("tags", {})
            for tag in required_tags:
                if tag not in resource_tags:
                    return self._create_violation(
                        resource, policy, f"Missing required tag: {tag}"
                    )
            
            # Check environment-specific conditions
            env_conditions = rules.get("environment_conditions", {})
            environment = resource.get("environment", "")
            if environment in env_conditions:
                conditions = env_conditions[environment]
                for condition, value in conditions.items():
                    if not self._evaluate_condition(resource, condition, value):
                        return self._create_violation(
                            resource, policy, 
                            f"Environment condition failed: {condition}"
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking policy compliance: {str(e)}")
            return None
    
    def _create_violation(
        self, resource: Dict[str, Any], policy: Policy, details: str
    ) -> PolicyViolation:
        """Create a policy violation record"""
        violation = PolicyViolation(
            violation_id=f"viol_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            policy_id=policy.policy_id,
            resource_id=resource.get("id", "unknown"),
            resource_type=resource.get("type", "unknown"),
            violation_details={"message": details, "resource": resource},
            severity=policy.severity
        )
        
        self.violations.append(violation)
        logger.warning(f"Policy violation detected: {violation.violation_id}")
        return violation
    
    def _evaluate_condition(
        self, resource: Dict[str, Any], condition: str, expected_value: Any
    ) -> bool:
        """Evaluate a condition against resource"""
        # Simple condition evaluation - can be extended
        if condition == "max_instance_size":
            instance_size = resource.get("attributes", {}).get("instance_type", "")
            size_order = ["micro", "small", "medium", "large", "xlarge"]
            
            try:
                resource_idx = size_order.index(instance_size.split(".")[-1])
                expected_idx = size_order.index(expected_value)
                return resource_idx <= expected_idx
            except (ValueError, IndexError):
                return False
        
        return True
    
    def get_violations(
        self, status: Optional[str] = None, 
        severity: Optional[PolicySeverity] = None
    ) -> List[PolicyViolation]:
        """Get policy violations with optional filtering"""
        violations = self.violations
        
        if status:
            violations = [v for v in violations if v.status == status]
        
        if severity:
            violations = [v for v in violations if v.severity == severity]
        
        return violations
    
    def resolve_violation(self, violation_id: str, resolution_note: str = "") -> bool:
        """Mark a violation as resolved"""
        try:
            for violation in self.violations:
                if violation.violation_id == violation_id:
                    violation.status = "resolved"
                    violation.resolved_at = datetime.now()
                    logger.info(f"Violation resolved: {violation_id}")
                    return True
            
            logger.error(f"Violation not found: {violation_id}")
            return False
        except Exception as e:
            logger.error(f"Error resolving violation {violation_id}: {str(e)}")
            return False


class WorkflowOrchestrator:
    """Workflow orchestration engine"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.load_default_workflows()
        logger.info("Workflow Orchestrator initialized")
    
    def load_default_workflows(self):
        """Load default workflows"""
        # Infrastructure provisioning workflow
        provision_workflow = Workflow(
            workflow_id="wf_provision_001",
            name="Infrastructure Provisioning",
            description="Standard infrastructure provisioning workflow",
            trigger_type="manual",
            steps=[
                WorkflowStep(
                    step_id="step_001",
                    name="Validate Blueprint",
                    step_type="terraform",
                    config={"action": "plan", "auto_approve": False}
                ),
                WorkflowStep(
                    step_id="step_002",
                    name="Security Review",
                    step_type="approval",
                    config={"approvers": ["security_team"], "timeout_hours": 24},
                    dependencies=["step_001"]
                ),
                WorkflowStep(
                    step_id="step_003",
                    name="Deploy Infrastructure",
                    step_type="terraform",
                    config={"action": "apply", "auto_approve": True},
                    dependencies=["step_002"]
                ),
                WorkflowStep(
                    step_id="step_004",
                    name="Configure Resources",
                    step_type="ansible",
                    config={"playbook": "configure.yml"},
                    dependencies=["step_003"]
                ),
                WorkflowStep(
                    step_id="step_005",
                    name="Validate Deployment",
                    step_type="script",
                    config={"script": "validate_deployment.py"},
                    dependencies=["step_004"]
                )
            ]
        )
        
        self.workflows[provision_workflow.workflow_id] = provision_workflow
        logger.info("Default workflows loaded")
    
    def create_workflow(self, workflow: Workflow) -> bool:
        """Create a new workflow"""
        try:
            self.workflows[workflow.workflow_id] = workflow
            logger.info(f"Workflow created: {workflow.workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating workflow {workflow.workflow_id}: {str(e)}")
            return False
    
    def execute_workflow(
        self, workflow_id: str, context: Dict[str, Any] = None
    ) -> Optional[WorkflowExecution]:
        """Execute a workflow"""
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow not found: {workflow_id}")
                return None
            
            workflow = self.workflows[workflow_id]
            if not workflow.enabled:
                logger.error(f"Workflow disabled: {workflow_id}")
                return None
            
            execution = WorkflowExecution(
                execution_id=f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                context=context or {}
            )
            
            self.executions[execution.execution_id] = execution
            
            # Start workflow execution (simplified)
            execution.status = WorkflowStatus.RUNNING
            self._execute_workflow_steps(execution, workflow)
            
            logger.info(f"Workflow execution started: {execution.execution_id}")
            return execution
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
            return None
    
    def _execute_workflow_steps(
        self, execution: WorkflowExecution, workflow: Workflow
    ):
        """Execute workflow steps (simplified implementation)"""
        try:
            for step in workflow.steps:
                if not step.enabled:
                    continue
                
                # Check dependencies
                if not self._check_dependencies(step, execution):
                    logger.warning(f"Dependencies not met for step: {step.step_id}")
                    continue
                
                # Execute step
                result = self._execute_step(step, execution)
                execution.step_results[step.step_id] = result
                
                if not result.get("success", False):
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = result.get("error", "Step failed")
                    execution.completed_at = datetime.now()
                    return
            
            execution.status = WorkflowStatus.SUCCESS
            execution.completed_at = datetime.now()
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            logger.error(f"Workflow execution failed: {str(e)}")
    
    def _check_dependencies(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> bool:
        """Check if step dependencies are satisfied"""
        for dep_id in step.dependencies:
            if dep_id not in execution.step_results:
                return False
            
            dep_result = execution.step_results[dep_id]
            if not dep_result.get("success", False):
                return False
        
        return True
    
    def _execute_step(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute individual workflow step"""
        try:
            logger.info(f"Executing step: {step.step_id}")
            
            if step.step_type == "terraform":
                return self._execute_terraform_step(step, execution)
            elif step.step_type == "ansible":
                return self._execute_ansible_step(step, execution)
            elif step.step_type == "script":
                return self._execute_script_step(step, execution)
            elif step.step_type == "approval":
                return self._execute_approval_step(step, execution)
            else:
                return {"success": False, "error": f"Unknown step type: {step.step_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_terraform_step(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute Terraform step"""
        # Simplified implementation
        action = step.config.get("action", "plan")
        logger.info(f"Executing Terraform {action}")
        
        # In real implementation, this would execute actual Terraform commands
        return {
            "success": True,
            "action": action,
            "output": f"Terraform {action} completed successfully"
        }
    
    def _execute_ansible_step(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute Ansible step"""
        # Simplified implementation
        playbook = step.config.get("playbook", "site.yml")
        logger.info(f"Executing Ansible playbook: {playbook}")
        
        # In real implementation, this would execute actual Ansible playbooks
        return {
            "success": True,
            "playbook": playbook,
            "output": f"Ansible playbook {playbook} completed successfully"
        }
    
    def _execute_script_step(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute script step"""
        # Simplified implementation
        script = step.config.get("script", "")
        logger.info(f"Executing script: {script}")
        
        # In real implementation, this would execute actual scripts
        return {
            "success": True,
            "script": script,
            "output": f"Script {script} completed successfully"
        }
    
    def _execute_approval_step(
        self, step: WorkflowStep, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute approval step"""
        # Simplified implementation - in real implementation, 
        # this would wait for human approval
        approvers = step.config.get("approvers", [])
        logger.info(f"Approval step - required approvers: {approvers}")
        
        return {
            "success": True,
            "approvers": approvers,
            "output": "Approval granted (auto-approved in demo)"
        }
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        return self.executions.get(execution_id)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel workflow execution"""
        try:
            if execution_id not in self.executions:
                return False
            
            execution = self.executions[execution_id]
            if execution.status in [WorkflowStatus.SUCCESS, WorkflowStatus.FAILED]:
                return False
            
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now()
            logger.info(f"Workflow execution cancelled: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling execution {execution_id}: {str(e)}")
            return False


class OrchestrationEngine:
    """Main Policy & Orchestration Engine (Vishnu)"""
    
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.workflow_orchestrator = WorkflowOrchestrator()
        logger.info("Vishnu Policy & Orchestration Engine initialized")
    
    def evaluate_infrastructure(
        self, resources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate infrastructure against all policies"""
        all_violations = []
        
        for resource in resources:
            violations = self.policy_engine.evaluate_resource(resource)
            all_violations.extend(violations)
        
        return {
            "total_resources": len(resources),
            "total_violations": len(all_violations),
            "violations_by_severity": self._group_violations_by_severity(all_violations),
            "compliance_score": self._calculate_compliance_score(resources, all_violations),
            "violations": [
                {
                    "violation_id": v.violation_id,
                    "policy_id": v.policy_id,
                    "resource_id": v.resource_id,
                    "severity": v.severity.value,
                    "details": v.violation_details
                }
                for v in all_violations
            ]
        }
    
    def _group_violations_by_severity(
        self, violations: List[PolicyViolation]
    ) -> Dict[str, int]:
        """Group violations by severity"""
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for violation in violations:
            severity_counts[violation.severity.value] += 1
        
        return severity_counts
    
    def _calculate_compliance_score(
        self, resources: List[Dict[str, Any]], violations: List[PolicyViolation]
    ) -> float:
        """Calculate overall compliance score"""
        if not resources:
            return 100.0
        
        total_resources = len(resources)
        total_violations = len(violations)
        
        # Weight violations by severity
        violation_weight = 0
        for violation in violations:
            if violation.severity == PolicySeverity.CRITICAL:
                violation_weight += 4
            elif violation.severity == PolicySeverity.HIGH:
                violation_weight += 3
            elif violation.severity == PolicySeverity.MEDIUM:
                violation_weight += 2
            else:  # LOW
                violation_weight += 1
        
        # Calculate score (0-100)
        max_possible_weight = total_resources * 4  # Assuming worst case
        if max_possible_weight == 0:
            return 100.0
        
        compliance_score = max(0, 100 - (violation_weight / max_possible_weight * 100))
        return round(compliance_score, 2)
    
    def provision_infrastructure(
        self, blueprint_id: str, context: Dict[str, Any] = None
    ) -> Optional[WorkflowExecution]:
        """Provision infrastructure using standard workflow"""
        workflow_id = "wf_provision_001"
        execution_context = context or {}
        execution_context["blueprint_id"] = blueprint_id
        
        return self.workflow_orchestrator.execute_workflow(workflow_id, execution_context)
    
    def get_policy_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive policy compliance report"""
        all_violations = self.policy_engine.get_violations()
        open_violations = self.policy_engine.get_violations(status="open")
        
        return {
            "report_generated_at": datetime.now().isoformat(),
            "total_policies": len(self.policy_engine.policies),
            "total_violations": len(all_violations),
            "open_violations": len(open_violations),
            "violations_by_type": self._group_violations_by_type(all_violations),
            "violations_by_severity": self._group_violations_by_severity(all_violations),
            "recent_violations": [
                {
                    "violation_id": v.violation_id,
                    "policy_id": v.policy_id,
                    "resource_id": v.resource_id,
                    "severity": v.severity.value,
                    "detected_at": v.detected_at.isoformat()
                }
                for v in sorted(all_violations, key=lambda x: x.detected_at, reverse=True)[:10]
            ]
        }
    
    def _group_violations_by_type(
        self, violations: List[PolicyViolation]
    ) -> Dict[str, int]:
        """Group violations by policy type"""
        type_counts = {}
        
        for violation in violations:
            policy = self.policy_engine.policies.get(violation.policy_id)
            if policy:
                policy_type = policy.policy_type.value
                type_counts[policy_type] = type_counts.get(policy_type, 0) + 1
        
        return type_counts


# Export main classes
__all__ = [
    "OrchestrationEngine", "PolicyEngine", "WorkflowOrchestrator",
    "Policy", "PolicyViolation", "Workflow", "WorkflowExecution"
]

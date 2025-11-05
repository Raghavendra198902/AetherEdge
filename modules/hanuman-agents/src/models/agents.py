"""
Hanuman Agents Engine - Data Models
Sacred execution and distributed agent management
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class AgentType(str, Enum):
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    VM = "vm"
    CLOUD = "cloud"
    EDGE = "edge"
    NETWORK = "network"
    DATABASE = "database"
    MONITORING = "monitoring"
    SECURITY = "security"
    BACKUP = "backup"


class AgentStatus(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class TaskStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRY = "retry"


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ExecutionMode(str, Enum):
    SYNC = "sync"
    ASYNC = "async"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"


class Agent(BaseModel):
    """Distributed agent for task execution"""
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    agent_type: AgentType = Field(..., description="Type of agent")
    
    # Agent configuration
    version: str = Field(..., description="Agent version")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    supported_tasks: List[str] = Field(..., description="Supported task types")
    max_concurrent_tasks: int = Field(default=5, description="Max concurrent tasks")
    
    # Connection and location
    hostname: str = Field(..., description="Agent hostname")
    ip_address: str = Field(..., description="Agent IP address")
    port: int = Field(default=8080, description="Agent listening port")
    endpoint: str = Field(..., description="Agent API endpoint")
    
    # Environment and context
    environment: str = Field(..., description="Environment (dev/staging/prod)")
    region: str = Field(..., description="Geographic region")
    availability_zone: Optional[str] = Field(None, description="Availability zone")
    cluster: Optional[str] = Field(None, description="Cluster identifier")
    
    # Status and health
    status: AgentStatus = Field(default=AgentStatus.INITIALIZING)
    health_status: str = Field(default="unknown", description="Health status")
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    uptime: int = Field(default=0, description="Uptime in seconds")
    
    # Resource usage
    cpu_usage: float = Field(default=0.0, description="CPU usage percentage")
    memory_usage: float = Field(default=0.0, description="Memory usage percentage")
    disk_usage: float = Field(default=0.0, description="Disk usage percentage")
    network_io: Dict[str, float] = Field(default_factory=dict, description="Network I/O")
    
    # Task execution metrics
    total_tasks_executed: int = Field(default=0, description="Total tasks executed")
    current_task_count: int = Field(default=0, description="Current running tasks")
    success_rate: float = Field(default=1.0, description="Task success rate")
    average_execution_time: float = Field(default=0.0, description="Avg execution time")
    
    # Configuration and metadata
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")
    tags: Dict[str, str] = Field(default_factory=dict, description="Agent tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Registration and lifecycle
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    registered_by: str = Field(..., description="Registration source")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "agent_k8s_prod_us_east_001",
                "name": "Kubernetes Production Agent - US East",
                "agent_type": "kubernetes",
                "version": "1.0.0",
                "capabilities": ["pod_management", "deployment", "scaling"],
                "supported_tasks": ["deploy", "scale", "restart", "logs"],
                "hostname": "k8s-agent-001.prod.company.com",
                "ip_address": "10.0.1.100",
                "endpoint": "https://k8s-agent-001.prod.company.com:8080",
                "environment": "production",
                "region": "us-east-1",
                "cluster": "prod-cluster-01",
                "status": "active",
                "registered_by": "hanuman_engine"
            }
        }


class Task(BaseModel):
    """Task definition and execution tracking"""
    id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    
    # Task definition
    task_type: str = Field(..., description="Type of task")
    action: str = Field(..., description="Action to perform")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")
    script: Optional[str] = Field(None, description="Script content")
    script_type: Optional[str] = Field(None, description="Script type (bash, python, etc.)")
    
    # Execution configuration
    execution_mode: ExecutionMode = Field(default=ExecutionMode.ASYNC)
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    timeout: int = Field(default=300, description="Timeout in seconds")
    retry_count: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: int = Field(default=60, description="Retry delay in seconds")
    
    # Scheduling
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled execution time")
    cron_expression: Optional[str] = Field(None, description="Cron schedule expression")
    recurring: bool = Field(default=False, description="Recurring task")
    
    # Target specification
    target_agents: List[str] = Field(..., description="Target agent IDs")
    target_selector: Optional[Dict[str, str]] = Field(None, description="Agent selector")
    target_environment: Optional[str] = Field(None, description="Target environment")
    
    # Execution tracking
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    assigned_agent: Optional[str] = Field(None, description="Assigned agent ID")
    execution_id: Optional[str] = Field(None, description="Execution identifier")
    
    # Results and output
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    output: Optional[str] = Field(None, description="Task output")
    error_message: Optional[str] = Field(None, description="Error message")
    exit_code: Optional[int] = Field(None, description="Exit code")
    
    # Timing information
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")
    duration: Optional[float] = Field(None, description="Execution duration in seconds")
    
    # Context and relationships
    parent_task_id: Optional[str] = Field(None, description="Parent task ID")
    child_tasks: List[str] = Field(default_factory=list, description="Child task IDs")
    workflow_id: Optional[str] = Field(None, description="Workflow ID")
    correlation_id: Optional[str] = Field(None, description="Correlation ID")
    
    # Metadata
    created_by: str = Field(..., description="Task creator")
    tags: Dict[str, str] = Field(default_factory=dict, description="Task tags")
    labels: Dict[str, str] = Field(default_factory=dict, description="Task labels")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "task_deploy_web_app_001",
                "name": "Deploy Web Application",
                "description": "Deploy web application to production cluster",
                "task_type": "deployment",
                "action": "deploy",
                "parameters": {
                    "image": "webapp:v1.2.3",
                    "replicas": 3,
                    "namespace": "production"
                },
                "execution_mode": "async",
                "priority": "high",
                "timeout": 600,
                "target_agents": ["agent_k8s_prod_us_east_001"],
                "created_by": "vishnu_orchestrator"
            }
        }


class Workflow(BaseModel):
    """Workflow definition for complex task orchestration"""
    id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    version: str = Field(..., description="Workflow version")
    
    # Workflow definition
    tasks: List[str] = Field(..., description="Task IDs in workflow")
    dependencies: Dict[str, List[str]] = Field(
        default_factory=dict, description="Task dependencies"
    )
    parallel_execution: bool = Field(default=False, description="Allow parallel execution")
    failure_strategy: str = Field(default="stop", description="Failure handling strategy")
    
    # Execution configuration
    timeout: int = Field(default=3600, description="Workflow timeout in seconds")
    retry_policy: Dict[str, Any] = Field(
        default_factory=dict, description="Retry policy"
    )
    notification_policy: Dict[str, Any] = Field(
        default_factory=dict, description="Notification policy"
    )
    
    # Status and execution
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    current_step: Optional[str] = Field(None, description="Current executing step")
    progress: float = Field(default=0.0, description="Completion percentage")
    
    # Results and metrics
    result: Optional[Dict[str, Any]] = Field(None, description="Workflow result")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Execution metrics")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    duration: Optional[float] = Field(None, description="Total duration in seconds")
    
    # Context
    created_by: str = Field(..., description="Workflow creator")
    triggered_by: Optional[str] = Field(None, description="Trigger source")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "workflow_app_deployment",
                "name": "Complete Application Deployment",
                "description": "End-to-end application deployment workflow",
                "version": "1.0.0",
                "tasks": ["build", "test", "deploy", "verify"],
                "dependencies": {
                    "test": ["build"],
                    "deploy": ["test"],
                    "verify": ["deploy"]
                },
                "parallel_execution": False,
                "timeout": 3600,
                "created_by": "brahma_blueprint"
            }
        }


class ExecutionResult(BaseModel):
    """Task or workflow execution result"""
    execution_id: str = Field(..., description="Unique execution identifier")
    task_id: Optional[str] = Field(None, description="Task ID")
    workflow_id: Optional[str] = Field(None, description="Workflow ID")
    agent_id: str = Field(..., description="Executing agent ID")
    
    # Execution details
    status: TaskStatus = Field(..., description="Execution status")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    
    # Results and output
    success: bool = Field(..., description="Execution success")
    return_code: Optional[int] = Field(None, description="Return code")
    stdout: Optional[str] = Field(None, description="Standard output")
    stderr: Optional[str] = Field(None, description="Standard error")
    result_data: Dict[str, Any] = Field(default_factory=dict, description="Result data")
    
    # Resource usage
    cpu_time: Optional[float] = Field(None, description="CPU time used")
    memory_peak: Optional[int] = Field(None, description="Peak memory usage")
    disk_io: Optional[Dict[str, int]] = Field(None, description="Disk I/O statistics")
    network_io: Optional[Dict[str, int]] = Field(None, description="Network I/O stats")
    
    # Error information
    error_type: Optional[str] = Field(None, description="Error type")
    error_message: Optional[str] = Field(None, description="Error message")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    
    # Artifacts and outputs
    artifacts: List[str] = Field(default_factory=list, description="Generated artifacts")
    logs: List[str] = Field(default_factory=list, description="Log file URLs")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Execution metrics")
    
    class Config:
        schema_extra = {
            "example": {
                "execution_id": "exec_12345_67890",
                "task_id": "task_deploy_web_app_001",
                "agent_id": "agent_k8s_prod_us_east_001",
                "status": "completed",
                "started_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:35:30Z",
                "duration": 330.0,
                "success": True,
                "return_code": 0,
                "stdout": "Deployment successful",
                "result_data": {"pods_created": 3, "service_url": "https://webapp.prod.com"}
            }
        }


class AgentCommand(BaseModel):
    """Command to send to an agent"""
    command: str = Field(..., description="Command to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    timeout: int = Field(default=300, description="Command timeout in seconds")
    async_execution: bool = Field(default=True, description="Asynchronous execution")
    
    class Config:
        schema_extra = {
            "example": {
                "command": "deploy_application",
                "parameters": {
                    "image": "webapp:v1.2.3",
                    "replicas": 3,
                    "namespace": "production"
                },
                "timeout": 600,
                "async_execution": True
            }
        }


class AgentMetrics(BaseModel):
    """Agent performance and health metrics"""
    agent_id: str = Field(..., description="Agent identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # System metrics
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    network_rx: int = Field(..., description="Network bytes received")
    network_tx: int = Field(..., description="Network bytes transmitted")
    
    # Agent metrics
    active_tasks: int = Field(..., description="Currently active tasks")
    queued_tasks: int = Field(..., description="Queued tasks")
    completed_tasks: int = Field(..., description="Completed tasks today")
    failed_tasks: int = Field(..., description="Failed tasks today")
    
    # Performance metrics
    average_task_duration: float = Field(..., description="Average task duration")
    success_rate: float = Field(..., description="Task success rate")
    response_time: float = Field(..., description="Agent response time")
    uptime: int = Field(..., description="Agent uptime in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "agent_k8s_prod_us_east_001",
                "cpu_usage": 45.2,
                "memory_usage": 68.7,
                "disk_usage": 23.1,
                "network_rx": 1024000,
                "network_tx": 512000,
                "active_tasks": 3,
                "queued_tasks": 1,
                "completed_tasks": 47,
                "failed_tasks": 2,
                "average_task_duration": 125.5,
                "success_rate": 0.958,
                "response_time": 0.15,
                "uptime": 86400
            }
        }

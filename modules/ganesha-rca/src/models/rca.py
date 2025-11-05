"""
Ganesha RCA Engine - Data Models
Sacred problem resolution and root cause analysis
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RemediationStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Incident(BaseModel):
    """Incident definition and tracking"""
    id: str = Field(..., description="Unique incident identifier")
    title: str = Field(..., description="Incident title")
    description: str = Field(..., description="Detailed incident description")
    
    # Classification
    severity: IncidentSeverity = Field(..., description="Incident severity")
    category: str = Field(..., description="Incident category")
    subcategory: Optional[str] = Field(None, description="Incident subcategory")
    service_impact: str = Field(..., description="Service impact description")
    
    # Status and assignment
    status: IncidentStatus = Field(default=IncidentStatus.OPEN)
    assigned_to: Optional[str] = Field(None, description="Assigned analyst")
    escalated: bool = Field(default=False, description="Escalated incident")
    escalated_to: Optional[str] = Field(None, description="Escalation target")
    
    # Affected resources
    affected_services: List[str] = Field(..., description="Affected service names")
    affected_hosts: List[str] = Field(default_factory=list, description="Affected hosts")
    affected_users: Optional[int] = Field(None, description="Number of affected users")
    business_impact: str = Field(..., description="Business impact assessment")
    
    # Detection and timing
    detected_at: datetime = Field(..., description="Detection timestamp")
    reported_by: str = Field(..., description="Reporter/detector")
    detection_method: str = Field(..., description="How incident was detected")
    
    # Resolution tracking
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment time")
    resolved_at: Optional[datetime] = Field(None, description="Resolution time")
    closed_at: Optional[datetime] = Field(None, description="Closure time")
    
    # Time metrics
    time_to_detect: Optional[int] = Field(None, description="Detection time in minutes")
    time_to_acknowledge: Optional[int] = Field(None, description="Ack time in minutes")
    time_to_resolve: Optional[int] = Field(None, description="Resolution time in minutes")
    
    # Related information
    related_incidents: List[str] = Field(default_factory=list, description="Related incident IDs")
    parent_incident_id: Optional[str] = Field(None, description="Parent incident ID")
    duplicate_of: Optional[str] = Field(None, description="Duplicate incident ID")
    
    # External references
    external_ticket_id: Optional[str] = Field(None, description="External ticket ID")
    communication_channels: List[str] = Field(default_factory=list, description="Communication channels")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Incident tags")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "inc_web_service_down_001",
                "title": "Web Service Unavailable",
                "description": "Primary web service returning 503 errors",
                "severity": "critical",
                "category": "availability",
                "service_impact": "Complete service outage",
                "affected_services": ["web-frontend", "api-gateway"],
                "business_impact": "Customer-facing service unavailable",
                "detected_at": "2024-01-15T14:30:00Z",
                "reported_by": "monitoring_system",
                "detection_method": "automated_monitoring"
            }
        }


class RootCauseAnalysis(BaseModel):
    """Root cause analysis for incidents"""
    id: str = Field(..., description="Unique RCA identifier")
    incident_id: str = Field(..., description="Associated incident ID")
    title: str = Field(..., description="RCA title")
    
    # Analysis details
    methodology: str = Field(..., description="RCA methodology used")
    timeline: List[Dict[str, Any]] = Field(..., description="Event timeline")
    symptoms: List[str] = Field(..., description="Observed symptoms")
    contributing_factors: List[str] = Field(..., description="Contributing factors")
    
    # Root cause findings
    root_cause: str = Field(..., description="Identified root cause")
    root_cause_category: str = Field(..., description="Root cause category")
    confidence_level: float = Field(..., description="Confidence in root cause")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    
    # Impact analysis
    impact_scope: str = Field(..., description="Scope of impact")
    business_impact: str = Field(..., description="Business impact details")
    technical_impact: str = Field(..., description="Technical impact details")
    
    # Prevention and lessons learned
    lessons_learned: List[str] = Field(default_factory=list, description="Lessons learned")
    preventive_measures: List[str] = Field(default_factory=list, description="Preventive measures")
    process_improvements: List[str] = Field(default_factory=list, description="Process improvements")
    
    # Analysis status
    status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    analyst: str = Field(..., description="Conducting analyst")
    reviewed_by: Optional[str] = Field(None, description="Reviewer")
    approved_by: Optional[str] = Field(None, description="Approver")
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    
    # Related information
    related_rcas: List[str] = Field(default_factory=list, description="Related RCA IDs")
    references: List[str] = Field(default_factory=list, description="Reference documents")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "rca_web_service_down_001",
                "incident_id": "inc_web_service_down_001",
                "title": "Web Service Outage - Database Connection Pool Exhaustion",
                "methodology": "5_whys",
                "root_cause": "Database connection pool exhausted due to memory leak",
                "root_cause_category": "software_defect",
                "confidence_level": 0.95,
                "impact_scope": "All web services",
                "analyst": "sre_team_lead"
            }
        }


class RemediationAction(BaseModel):
    """Remediation action for incidents and problems"""
    id: str = Field(..., description="Unique action identifier")
    incident_id: Optional[str] = Field(None, description="Associated incident ID")
    rca_id: Optional[str] = Field(None, description="Associated RCA ID")
    
    # Action details
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Detailed action description")
    action_type: str = Field(..., description="Type of action")
    priority: str = Field(..., description="Action priority")
    
    # Implementation details
    implementation_plan: str = Field(..., description="Implementation plan")
    estimated_effort: str = Field(..., description="Estimated effort")
    required_resources: List[str] = Field(default_factory=list, description="Required resources")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies")
    
    # Ownership and tracking
    owner: str = Field(..., description="Action owner")
    assignee: str = Field(..., description="Action assignee")
    due_date: Optional[datetime] = Field(None, description="Due date")
    status: RemediationStatus = Field(default=RemediationStatus.NOT_STARTED)
    
    # Progress tracking
    progress_percentage: float = Field(default=0.0, description="Completion percentage")
    progress_notes: List[str] = Field(default_factory=list, description="Progress updates")
    blockers: List[str] = Field(default_factory=list, description="Current blockers")
    
    # Validation and testing
    validation_criteria: List[str] = Field(default_factory=list, description="Validation criteria")
    test_plan: Optional[str] = Field(None, description="Test plan")
    validation_results: Optional[str] = Field(None, description="Validation results")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    
    # Automation
    automated: bool = Field(default=False, description="Automated action")
    automation_script: Optional[str] = Field(None, description="Automation script")
    automation_parameters: Dict[str, Any] = Field(default_factory=dict, description="Script parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "action_fix_connection_pool",
                "incident_id": "inc_web_service_down_001",
                "title": "Fix Database Connection Pool Configuration",
                "description": "Update connection pool settings to prevent exhaustion",
                "action_type": "configuration_change",
                "priority": "high",
                "implementation_plan": "Update config, restart service, monitor",
                "estimated_effort": "2 hours",
                "owner": "database_team",
                "assignee": "db_admin_001"
            }
        }


class ProblemPattern(BaseModel):
    """Problem pattern for predictive analysis"""
    id: str = Field(..., description="Unique pattern identifier")
    name: str = Field(..., description="Pattern name")
    description: str = Field(..., description="Pattern description")
    
    # Pattern definition
    pattern_type: str = Field(..., description="Type of pattern")
    indicators: List[Dict[str, Any]] = Field(..., description="Pattern indicators")
    conditions: List[Dict[str, Any]] = Field(..., description="Pattern conditions")
    thresholds: Dict[str, float] = Field(..., description="Detection thresholds")
    
    # Detection and matching
    confidence_threshold: float = Field(..., description="Confidence threshold")
    match_algorithm: str = Field(..., description="Pattern matching algorithm")
    time_window: int = Field(..., description="Time window in minutes")
    
    # Historical data
    historical_incidents: List[str] = Field(default_factory=list, description="Historical incident IDs")
    occurrence_frequency: float = Field(default=0.0, description="Occurrence frequency")
    last_occurrence: Optional[datetime] = Field(None, description="Last occurrence")
    
    # Prediction and prevention
    lead_time: int = Field(..., description="Lead time for prediction in minutes")
    prevention_actions: List[str] = Field(default_factory=list, description="Prevention action IDs")
    mitigation_steps: List[str] = Field(default_factory=list, description="Mitigation steps")
    
    # Performance metrics
    detection_accuracy: float = Field(default=0.0, description="Detection accuracy")
    false_positive_rate: float = Field(default=0.0, description="False positive rate")
    false_negative_rate: float = Field(default=0.0, description="False negative rate")
    
    # Metadata
    created_by: str = Field(..., description="Pattern creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    enabled: bool = Field(default=True, description="Pattern enabled")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "pattern_memory_leak_detection",
                "name": "Memory Leak Leading to Service Failure",
                "description": "Pattern for detecting memory leaks before service failure",
                "pattern_type": "predictive",
                "thresholds": {"memory_growth_rate": 5.0, "duration_minutes": 30},
                "confidence_threshold": 0.85,
                "match_algorithm": "statistical_analysis",
                "time_window": 60,
                "lead_time": 15,
                "created_by": "ml_engine"
            }
        }


class KnowledgeBase(BaseModel):
    """Knowledge base entry for problems and solutions"""
    id: str = Field(..., description="Unique knowledge entry identifier")
    title: str = Field(..., description="Knowledge entry title")
    summary: str = Field(..., description="Brief summary")
    content: str = Field(..., description="Detailed content")
    
    # Classification
    category: str = Field(..., description="Knowledge category")
    subcategory: Optional[str] = Field(None, description="Knowledge subcategory")
    problem_type: str = Field(..., description="Type of problem")
    solution_type: str = Field(..., description="Type of solution")
    
    # Problem and solution
    problem_symptoms: List[str] = Field(..., description="Problem symptoms")
    root_cause: str = Field(..., description="Root cause")
    solution_steps: List[str] = Field(..., description="Solution steps")
    verification_steps: List[str] = Field(default_factory=list, description="Verification steps")
    
    # Context and applicability
    applicable_services: List[str] = Field(default_factory=list, description="Applicable services")
    applicable_environments: List[str] = Field(default_factory=list, description="Applicable environments")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")
    limitations: List[str] = Field(default_factory=list, description="Solution limitations")
    
    # Quality and validation
    confidence_score: float = Field(..., description="Solution confidence score")
    success_rate: float = Field(default=0.0, description="Historical success rate")
    validation_count: int = Field(default=0, description="Times validated")
    feedback_score: float = Field(default=0.0, description="User feedback score")
    
    # Usage analytics
    usage_count: int = Field(default=0, description="Times used")
    last_used: Optional[datetime] = Field(None, description="Last usage time")
    effectiveness_rating: float = Field(default=0.0, description="Effectiveness rating")
    
    # References and relationships
    related_incidents: List[str] = Field(default_factory=list, description="Related incident IDs")
    related_knowledge: List[str] = Field(default_factory=list, description="Related knowledge IDs")
    external_references: List[str] = Field(default_factory=list, description="External references")
    
    # Metadata
    created_by: str = Field(..., description="Knowledge creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0", description="Knowledge version")
    tags: List[str] = Field(default_factory=list, description="Knowledge tags")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "kb_database_connection_pool_fix",
                "title": "Database Connection Pool Exhaustion Resolution",
                "summary": "How to resolve database connection pool exhaustion issues",
                "content": "Detailed steps to diagnose and fix connection pool issues...",
                "category": "database",
                "problem_type": "performance",
                "solution_type": "configuration",
                "problem_symptoms": ["503 errors", "slow response times", "connection timeouts"],
                "root_cause": "Insufficient connection pool size or connection leaks",
                "solution_steps": ["Check pool configuration", "Increase pool size", "Fix connection leaks"],
                "confidence_score": 0.95,
                "created_by": "database_team"
            }
        }


class CorrelationRule(BaseModel):
    """Event correlation rule for pattern detection"""
    id: str = Field(..., description="Unique correlation rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    
    # Rule definition
    rule_type: str = Field(..., description="Type of correlation rule")
    conditions: List[Dict[str, Any]] = Field(..., description="Correlation conditions")
    time_window: int = Field(..., description="Time window in seconds")
    event_sources: List[str] = Field(..., description="Event sources to correlate")
    
    # Pattern matching
    pattern: Dict[str, Any] = Field(..., description="Pattern definition")
    threshold: float = Field(..., description="Correlation threshold")
    confidence_threshold: float = Field(..., description="Confidence threshold")
    
    # Actions and responses
    trigger_actions: List[str] = Field(default_factory=list, description="Triggered actions")
    create_incident: bool = Field(default=False, description="Auto-create incident")
    incident_template: Optional[str] = Field(None, description="Incident template ID")
    notification_targets: List[str] = Field(default_factory=list, description="Notification targets")
    
    # Performance metrics
    match_count: int = Field(default=0, description="Number of matches")
    true_positives: int = Field(default=0, description="True positive matches")
    false_positives: int = Field(default=0, description="False positive matches")
    accuracy: float = Field(default=0.0, description="Rule accuracy")
    
    # Metadata
    enabled: bool = Field(default=True, description="Rule enabled")
    priority: int = Field(default=1, description="Rule priority")
    created_by: str = Field(..., description="Rule creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "rule_web_service_failure_correlation",
                "name": "Web Service Failure Correlation",
                "description": "Correlates web service failures with infrastructure events",
                "rule_type": "temporal_correlation",
                "time_window": 300,
                "event_sources": ["web_logs", "infrastructure_metrics", "database_logs"],
                "threshold": 0.8,
                "confidence_threshold": 0.9,
                "create_incident": True,
                "created_by": "correlation_engine"
            }
        }

"""
💰 Lakshmi FinOps Models
========================

Pydantic models for financial operations, cost management, and optimization.
Lakshmi embodies wealth, prosperity, and financial intelligence.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ORACLE = "oracle"
    ALIBABA = "alibaba"
    ON_PREMISES = "on_premises"
    HYBRID = "hybrid"
    MULTI_CLOUD = "multi_cloud"


class ResourceType(str, Enum):
    """Resource types for cost categorization"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORKING = "networking"
    DATABASE = "database"
    SERVERLESS = "serverless"
    CONTAINER = "container"
    AI_ML = "ai_ml"
    SECURITY = "security"
    MONITORING = "monitoring"
    BACKUP = "backup"
    CDN = "cdn"
    DNS = "dns"


class CostCategory(str, Enum):
    """Cost categories for financial tracking"""
    INFRASTRUCTURE = "infrastructure"
    PLATFORM = "platform"
    APPLICATION = "application"
    DATA = "data"
    SECURITY = "security"
    MANAGEMENT = "management"
    SUPPORT = "support"
    TRAINING = "training"
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class BudgetStatus(str, Enum):
    """Budget status tracking"""
    UNDER_BUDGET = "under_budget"
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    OVER_BUDGET = "over_budget"
    EXCEEDED = "exceeded"


class OptimizationStatus(str, Enum):
    """Optimization recommendation status"""
    IDENTIFIED = "identified"
    ANALYZED = "analyzed"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    REJECTED = "rejected"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


# Base Models
class CostEntry(BaseModel):
    """Base cost entry model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str = Field(..., description="Resource identifier")
    resource_name: str = Field(..., description="Resource name")
    resource_type: ResourceType = Field(..., description="Resource type")
    
    # Provider information
    cloud_provider: CloudProvider = Field(..., description="Cloud provider")
    region: str = Field(..., description="Cloud region")
    availability_zone: Optional[str] = Field(None, description="Availability zone")
    
    # Cost details
    cost_amount: Decimal = Field(..., description="Cost amount")
    currency: str = Field(default="USD", description="Currency code")
    billing_period_start: date = Field(..., description="Billing period start")
    billing_period_end: date = Field(..., description="Billing period end")
    
    # Organization
    account_id: str = Field(..., description="Cloud account ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    department: Optional[str] = Field(None, description="Department")
    team: Optional[str] = Field(None, description="Team")
    environment: Optional[str] = Field(None, description="Environment")
    
    # Categorization
    category: CostCategory = Field(..., description="Cost category")
    tags: Dict[str, str] = Field(default={}, description="Resource tags")
    
    # Metadata
    usage_quantity: Optional[Decimal] = Field(None, description="Usage quantity")
    usage_unit: Optional[str] = Field(None, description="Usage unit")
    rate: Optional[Decimal] = Field(None, description="Rate per unit")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True
        use_enum_values = True


class Budget(BaseModel):
    """Budget model for financial planning"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Budget name")
    description: Optional[str] = Field(None, description="Budget description")
    
    # Budget scope
    account_ids: List[str] = Field(..., description="Account IDs")
    project_ids: List[str] = Field(default=[], description="Project IDs")
    departments: List[str] = Field(default=[], description="Departments")
    categories: List[CostCategory] = Field(default=[], description="Cost categories")
    
    # Budget amounts
    total_amount: Decimal = Field(..., description="Total budget amount")
    currency: str = Field(default="USD", description="Currency code")
    
    # Time period
    period_start: date = Field(..., description="Budget period start")
    period_end: date = Field(..., description="Budget period end")
    
    # Thresholds
    warning_threshold: float = Field(default=80.0, description="Warning threshold %")
    critical_threshold: float = Field(default=95.0, description="Critical threshold %")
    
    # Status tracking
    current_spend: Decimal = Field(default=Decimal("0.00"), description="Current spend")
    forecasted_spend: Optional[Decimal] = Field(None, description="Forecasted spend")
    status: BudgetStatus = Field(default=BudgetStatus.ON_TRACK)
    
    # Metadata
    created_by: str = Field(..., description="Budget creator")
    approved_by: Optional[str] = Field(None, description="Budget approver")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True
        use_enum_values = True


class OptimizationRecommendation(BaseModel):
    """Cost optimization recommendation"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    
    # Target resource
    resource_id: str = Field(..., description="Target resource ID")
    resource_name: str = Field(..., description="Resource name")
    resource_type: ResourceType = Field(..., description="Resource type")
    cloud_provider: CloudProvider = Field(..., description="Cloud provider")
    
    # Optimization details
    optimization_type: str = Field(..., description="Type of optimization")
    current_cost: Decimal = Field(..., description="Current monthly cost")
    optimized_cost: Decimal = Field(..., description="Projected cost after optimization")
    savings_amount: Decimal = Field(..., description="Potential savings")
    savings_percentage: float = Field(..., description="Savings percentage")
    
    # Implementation
    implementation_effort: str = Field(..., description="Implementation effort level")
    implementation_steps: List[str] = Field(default=[], description="Implementation steps")
    prerequisites: List[str] = Field(default=[], description="Prerequisites")
    risks: List[str] = Field(default=[], description="Implementation risks")
    
    # Priority and confidence
    priority: str = Field(..., description="Priority level")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    
    # Status tracking
    status: OptimizationStatus = Field(default=OptimizationStatus.IDENTIFIED)
    assigned_to: Optional[str] = Field(None, description="Assigned team/person")
    due_date: Optional[date] = Field(None, description="Target implementation date")
    
    # Metadata
    category: CostCategory = Field(..., description="Cost category")
    tags: List[str] = Field(default=[], description="Recommendation tags")
    
    # Timestamps
    identified_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    implemented_at: Optional[datetime] = Field(None)
    
    class Config:
        orm_mode = True
        use_enum_values = True


class CostAlert(BaseModel):
    """Cost alert model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    
    # Alert details
    severity: AlertSeverity = Field(..., description="Alert severity")
    alert_type: str = Field(..., description="Type of alert")
    
    # Trigger conditions
    trigger_resource: Optional[str] = Field(None, description="Triggering resource")
    trigger_account: Optional[str] = Field(None, description="Triggering account")
    trigger_amount: Optional[Decimal] = Field(None, description="Triggering amount")
    threshold_amount: Optional[Decimal] = Field(None, description="Threshold amount")
    
    # Resolution
    is_resolved: bool = Field(default=False, description="Alert resolution status")
    resolved_by: Optional[str] = Field(None, description="Resolver")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    
    # Timestamps
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(None)
    
    class Config:
        orm_mode = True
        use_enum_values = True


class CostForecast(BaseModel):
    """Cost forecasting model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    scope: str = Field(..., description="Forecast scope")
    
    # Forecast details
    forecast_period_start: date = Field(..., description="Forecast period start")
    forecast_period_end: date = Field(..., description="Forecast period end")
    forecasted_amount: Decimal = Field(..., description="Forecasted amount")
    confidence_interval_lower: Decimal = Field(..., description="Lower confidence bound")
    confidence_interval_upper: Decimal = Field(..., description="Upper confidence bound")
    confidence_level: float = Field(default=0.95, description="Confidence level")
    
    # Model information
    model_type: str = Field(..., description="Forecasting model used")
    model_accuracy: Optional[float] = Field(None, description="Model accuracy score")
    
    # Historical data
    historical_period_days: int = Field(..., description="Historical data period")
    trend_direction: str = Field(..., description="Trend direction")
    seasonality_detected: bool = Field(default=False, description="Seasonality detection")
    
    # Metadata
    currency: str = Field(default="USD", description="Currency code")
    
    # Timestamps
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True


# Request/Response Models
class BudgetCreateRequest(BaseModel):
    """Request to create a new budget"""
    name: str = Field(..., description="Budget name")
    description: Optional[str] = Field(None, description="Budget description")
    account_ids: List[str] = Field(..., description="Account IDs")
    project_ids: List[str] = Field(default=[], description="Project IDs")
    departments: List[str] = Field(default=[], description="Departments")
    categories: List[CostCategory] = Field(default=[], description="Cost categories")
    total_amount: Decimal = Field(..., description="Total budget amount")
    currency: str = Field(default="USD", description="Currency code")
    period_start: date = Field(..., description="Budget period start")
    period_end: date = Field(..., description="Budget period end")
    warning_threshold: float = Field(default=80.0, description="Warning threshold %")
    critical_threshold: float = Field(default=95.0, description="Critical threshold %")


class CostAnalysisRequest(BaseModel):
    """Request for cost analysis"""
    start_date: date = Field(..., description="Analysis start date")
    end_date: date = Field(..., description="Analysis end date")
    account_ids: List[str] = Field(default=[], description="Account IDs filter")
    resource_types: List[ResourceType] = Field(default=[], description="Resource types filter")
    categories: List[CostCategory] = Field(default=[], description="Categories filter")
    group_by: List[str] = Field(default=["category"], description="Grouping dimensions")
    include_forecasting: bool = Field(default=False, description="Include forecasting")


class CostSummary(BaseModel):
    """Cost summary response"""
    total_cost: Decimal = Field(..., description="Total cost")
    currency: str = Field(..., description="Currency code")
    period_start: date = Field(..., description="Period start")
    period_end: date = Field(..., description="Period end")
    cost_breakdown: Dict[str, Decimal] = Field(default={}, description="Cost breakdown")
    top_resources: List[Dict[str, Any]] = Field(default=[], description="Top cost resources")
    trend_data: List[Dict[str, Any]] = Field(default=[], description="Trend data")


class FinOpsResponse(BaseModel):
    """Standard FinOps API response"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FinOpsDashboard(BaseModel):
    """FinOps dashboard data"""
    total_monthly_cost: Decimal = Field(..., description="Total monthly cost")
    monthly_trend: float = Field(..., description="Monthly trend percentage")
    active_budgets: int = Field(..., description="Number of active budgets")
    budget_alerts: int = Field(..., description="Number of budget alerts")
    optimization_opportunities: int = Field(..., description="Optimization opportunities")
    potential_savings: Decimal = Field(..., description="Potential monthly savings")
    
    # Top items
    top_cost_accounts: List[Dict[str, Any]] = Field(default=[], description="Top cost accounts")
    top_cost_resources: List[Dict[str, Any]] = Field(default=[], description="Top cost resources")
    recent_alerts: List[CostAlert] = Field(default=[], description="Recent cost alerts")
    pending_recommendations: List[OptimizationRecommendation] = Field(default=[], description="Pending recommendations")
    
    # Charts data
    cost_trend_data: List[Dict[str, Any]] = Field(default=[], description="Cost trend chart data")
    category_breakdown: Dict[str, Decimal] = Field(default={}, description="Category breakdown")
    provider_breakdown: Dict[str, Decimal] = Field(default={}, description="Provider breakdown")
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BudgetAlert(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class CostData(BaseModel):
    """Cost data point for resources and services"""
    id: str = Field(..., description="Unique cost data identifier")
    resource_id: str = Field(..., description="Resource identifier")
    resource_name: str = Field(..., description="Human-readable resource name")
    resource_type: ResourceType = Field(..., description="Type of resource")
    
    # Provider and location
    cloud_provider: CloudProvider = Field(..., description="Cloud provider")
    region: str = Field(..., description="Cloud region")
    availability_zone: Optional[str] = Field(None, description="AZ if applicable")
    
    # Cost information
    cost: Decimal = Field(..., description="Cost amount")
    currency: str = Field(default="USD", description="Currency code")
    billing_period: str = Field(..., description="Billing period (YYYY-MM)")
    usage_quantity: Optional[float] = Field(None, description="Usage quantity")
    usage_unit: Optional[str] = Field(None, description="Usage unit")
    
    # Categorization
    cost_category: CostCategory = Field(..., description="Cost category")
    department: Optional[str] = Field(None, description="Department/team")
    project: Optional[str] = Field(None, description="Project identifier")
    environment: str = Field(..., description="Environment (dev/staging/prod)")
    
    # Tags and metadata
    tags: Dict[str, str] = Field(default_factory=dict, description="Resource tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Temporal information
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "cost_ec2_prod_web_001",
                "resource_id": "i-1234567890abcdef0",
                "resource_name": "prod-web-server-01",
                "resource_type": "compute",
                "cloud_provider": "aws",
                "region": "us-east-1",
                "cost": "156.78",
                "currency": "USD",
                "billing_period": "2024-01",
                "usage_quantity": 744.0,
                "usage_unit": "hours",
                "cost_category": "infrastructure",
                "department": "engineering",
                "project": "web-platform",
                "environment": "production"
            }
        }


class Budget(BaseModel):
    """Budget definition and tracking"""
    id: str = Field(..., description="Unique budget identifier")
    name: str = Field(..., description="Budget name")
    description: str = Field(..., description="Budget description")
    
    # Budget parameters
    amount: Decimal = Field(..., description="Budget amount")
    currency: str = Field(default="USD", description="Currency code")
    period_type: str = Field(..., description="Period type (monthly/quarterly/annual)")
    start_date: date = Field(..., description="Budget start date")
    end_date: date = Field(..., description="Budget end date")
    
    # Scope and filters
    scope: Dict[str, Any] = Field(..., description="Budget scope filters")
    departments: List[str] = Field(default_factory=list, description="Departments")
    projects: List[str] = Field(default_factory=list, description="Projects")
    environments: List[str] = Field(default_factory=list, description="Environments")
    cost_categories: List[CostCategory] = Field(default_factory=list, description="Cost categories")
    
    # Alerts and thresholds
    alert_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {"warning": 80.0, "critical": 95.0},
        description="Alert thresholds as percentages"
    )
    notification_emails: List[str] = Field(default_factory=list, description="Alert recipients")
    
    # Current status
    current_spend: Decimal = Field(default=Decimal("0"), description="Current spend")
    remaining_budget: Decimal = Field(default=Decimal("0"), description="Remaining budget")
    utilization_percentage: float = Field(default=0.0, description="Budget utilization %")
    
    # Metadata
    created_by: str = Field(..., description="Budget creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "budget_engineering_2024_q1",
                "name": "Engineering Q1 2024 Budget",
                "description": "Quarterly budget for engineering infrastructure",
                "amount": "50000.00",
                "currency": "USD",
                "period_type": "quarterly",
                "start_date": "2024-01-01",
                "end_date": "2024-03-31",
                "scope": {"departments": ["engineering"], "environments": ["production"]},
                "alert_thresholds": {"warning": 80.0, "critical": 95.0},
                "notification_emails": ["finops@company.com"]
            }
        }


class CostOptimization(BaseModel):
    """Cost optimization opportunity and recommendation"""
    id: str = Field(..., description="Unique optimization identifier")
    title: str = Field(..., description="Optimization title")
    description: str = Field(..., description="Detailed description")
    
    # Optimization details
    optimization_type: str = Field(..., description="Type of optimization")
    resource_type: ResourceType = Field(..., description="Target resource type")
    cloud_provider: CloudProvider = Field(..., description="Cloud provider")
    
    # Financial impact
    potential_savings: Decimal = Field(..., description="Potential monthly savings")
    current_cost: Decimal = Field(..., description="Current monthly cost")
    savings_percentage: float = Field(..., description="Savings percentage")
    currency: str = Field(default="USD", description="Currency code")
    
    # Implementation details
    effort_level: str = Field(..., description="Implementation effort (low/medium/high)")
    implementation_time: str = Field(..., description="Estimated implementation time")
    risk_level: str = Field(..., description="Risk level (low/medium/high)")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")
    
    # Resources affected
    affected_resources: List[str] = Field(default_factory=list, description="Resource IDs")
    affected_services: List[str] = Field(default_factory=list, description="Service names")
    
    # Status and tracking
    status: OptimizationStatus = Field(default=OptimizationStatus.IDENTIFIED)
    priority: str = Field(..., description="Priority (low/medium/high/critical)")
    confidence_score: float = Field(..., description="Confidence in recommendation")
    
    # Actions and automation
    automated: bool = Field(default=False, description="Can be automated")
    automation_script: Optional[str] = Field(None, description="Automation script path")
    manual_steps: List[str] = Field(default_factory=list, description="Manual steps")
    
    # Metadata
    identified_by: str = Field(..., description="Who/what identified this")
    identified_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = Field(None, description="Assignee")
    due_date: Optional[date] = Field(None, description="Target completion date")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "opt_rightsizing_web_servers",
                "title": "Rightsize Overprovisioned Web Servers",
                "description": "Web servers showing low CPU utilization",
                "optimization_type": "rightsizing",
                "resource_type": "compute",
                "cloud_provider": "aws",
                "potential_savings": "2450.00",
                "current_cost": "4900.00",
                "savings_percentage": 50.0,
                "effort_level": "low",
                "implementation_time": "2 hours",
                "risk_level": "low",
                "status": "identified",
                "priority": "medium",
                "confidence_score": 0.85
            }
        }


class CostForecast(BaseModel):
    """Cost forecasting data and predictions"""
    id: str = Field(..., description="Unique forecast identifier")
    name: str = Field(..., description="Forecast name")
    description: str = Field(..., description="Forecast description")
    
    # Forecast parameters
    forecast_period: str = Field(..., description="Forecast period")
    start_date: date = Field(..., description="Forecast start date")
    end_date: date = Field(..., description="Forecast end date")
    granularity: str = Field(..., description="Granularity (daily/weekly/monthly)")
    
    # Scope and filters
    scope: Dict[str, Any] = Field(..., description="Forecast scope")
    cost_categories: List[CostCategory] = Field(default_factory=list)
    cloud_providers: List[CloudProvider] = Field(default_factory=list)
    
    # Forecast data
    historical_data: List[Dict[str, Any]] = Field(
        default_factory=list, description="Historical cost data"
    )
    predicted_data: List[Dict[str, Any]] = Field(
        default_factory=list, description="Predicted cost data"
    )
    
    # Model information
    model_type: str = Field(..., description="Forecasting model used")
    model_accuracy: float = Field(..., description="Model accuracy score")
    confidence_intervals: Dict[str, float] = Field(
        default_factory=dict, description="Confidence intervals"
    )
    
    # Key insights
    total_forecasted_cost: Decimal = Field(..., description="Total forecasted cost")
    growth_rate: float = Field(..., description="Projected growth rate")
    seasonal_patterns: List[str] = Field(
        default_factory=list, description="Identified seasonal patterns"
    )
    anomalies: List[Dict[str, Any]] = Field(
        default_factory=list, description="Detected anomalies"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="Forecast creator")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "forecast_q2_2024_infrastructure",
                "name": "Q2 2024 Infrastructure Forecast",
                "description": "Quarterly infrastructure cost forecast",
                "forecast_period": "quarterly",
                "start_date": "2024-04-01",
                "end_date": "2024-06-30",
                "granularity": "monthly",
                "model_type": "arima",
                "model_accuracy": 0.92,
                "total_forecasted_cost": "75000.00",
                "growth_rate": 15.5
            }
        }


class FinOpsReport(BaseModel):
    """Financial operations report"""
    id: str = Field(..., description="Unique report identifier")
    name: str = Field(..., description="Report name")
    report_type: str = Field(..., description="Type of report")
    
    # Report parameters
    period_start: date = Field(..., description="Report period start")
    period_end: date = Field(..., description="Report period end")
    scope: Dict[str, Any] = Field(..., description="Report scope")
    
    # Summary metrics
    total_cost: Decimal = Field(..., description="Total cost for period")
    cost_change: Decimal = Field(..., description="Cost change from previous period")
    cost_change_percentage: float = Field(..., description="Cost change percentage")
    
    # Cost breakdown
    cost_by_category: Dict[str, Decimal] = Field(
        default_factory=dict, description="Cost breakdown by category"
    )
    cost_by_provider: Dict[str, Decimal] = Field(
        default_factory=dict, description="Cost breakdown by provider"
    )
    cost_by_department: Dict[str, Decimal] = Field(
        default_factory=dict, description="Cost breakdown by department"
    )
    
    # Optimization insights
    optimization_opportunities: List[str] = Field(
        default_factory=list, description="Optimization opportunity IDs"
    )
    potential_savings: Decimal = Field(
        default=Decimal("0"), description="Total potential savings"
    )
    
    # Trends and analysis
    trends: Dict[str, Any] = Field(
        default_factory=dict, description="Cost trends and patterns"
    )
    anomalies: List[Dict[str, Any]] = Field(
        default_factory=list, description="Cost anomalies detected"
    )
    
    # Report artifacts
    charts: List[str] = Field(
        default_factory=list, description="Chart/visualization URLs"
    )
    data_export_url: Optional[str] = Field(None, description="Data export URL")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = Field(..., description="Report generator")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "report_monthly_jan_2024",
                "name": "January 2024 Monthly FinOps Report",
                "report_type": "monthly_summary",
                "period_start": "2024-01-01",
                "period_end": "2024-01-31",
                "total_cost": "45678.90",
                "cost_change": "3456.78",
                "cost_change_percentage": 8.2,
                "potential_savings": "5432.10"
            }
        }


class BudgetAlert(BaseModel):
    """Budget alert notification"""
    id: str = Field(..., description="Unique alert identifier")
    budget_id: str = Field(..., description="Associated budget ID")
    alert_type: BudgetAlert = Field(..., description="Alert severity level")
    
    # Alert details
    message: str = Field(..., description="Alert message")
    current_spend: Decimal = Field(..., description="Current spend amount")
    budget_amount: Decimal = Field(..., description="Budget amount")
    utilization_percentage: float = Field(..., description="Budget utilization")
    threshold_exceeded: float = Field(..., description="Threshold that was exceeded")
    
    # Projections
    projected_spend: Optional[Decimal] = Field(None, description="Projected end-of-period spend")
    projected_overage: Optional[Decimal] = Field(None, description="Projected overage")
    days_remaining: int = Field(..., description="Days remaining in budget period")
    
    # Response tracking
    acknowledged: bool = Field(default=False, description="Alert acknowledged")
    acknowledged_by: Optional[str] = Field(None, description="Who acknowledged")
    acknowledged_at: Optional[datetime] = Field(None, description="When acknowledged")
    
    # Metadata
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    sent_to: List[str] = Field(default_factory=list, description="Recipients")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "alert_budget_eng_q1_critical",
                "budget_id": "budget_engineering_2024_q1",
                "alert_type": "critical",
                "message": "Engineering Q1 budget at 95% utilization",
                "current_spend": "47500.00",
                "budget_amount": "50000.00",
                "utilization_percentage": 95.0,
                "threshold_exceeded": 95.0,
                "days_remaining": 15
            }
        }

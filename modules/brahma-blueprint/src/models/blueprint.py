"""
📊 Blueprint Data Models
========================

Data models for the Brahma Blueprint Engine using SQLAlchemy ORM.
Represents the cosmic blueprints and their lifecycle states.
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Enum, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Dict, List, Optional, Any
import uuid

from ..database.connection import Base


class BlueprintStatus(PyEnum):
    """Blueprint lifecycle status enumeration"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATING = "validating"
    VALIDATED = "validated"
    VALIDATION_FAILED = "validation_failed"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    DEPLOYMENT_FAILED = "deployment_failed"
    DRY_RUN_COMPLETED = "dry_run_completed"
    ARCHIVED = "archived"


class CloudProvider(PyEnum):
    """Supported cloud providers"""
    AZURE = "azure"
    AWS = "aws"
    GCP = "gcp"
    HYBRID = "hybrid"
    ON_PREMISES = "on_premises"


class Environment(PyEnum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DR = "disaster_recovery"


class Blueprint(Base):
    """
    Divine Blueprint entity representing infrastructure-as-code templates
    """
    __tablename__ = "blueprints"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Core blueprint data
    intent = Column(Text, nullable=False)  # Natural language intent
    cloud_provider = Column(Enum(CloudProvider), nullable=False)
    region = Column(String(50), nullable=False)
    environment = Column(Enum(Environment), nullable=False)
    
    # Generated artifacts
    terraform_code = Column(Text)
    ansible_playbooks = Column(JSON)
    helm_charts = Column(JSON)
    architecture_diagram = Column(Text)  # Mermaid or PlantUML
    
    # Analysis results
    cost_estimate = Column(JSON)
    security_recommendations = Column(JSON)
    compliance_results = Column(JSON)
    validation_results = Column(JSON)
    
    # Budget and constraints
    budget_limit = Column(Float)
    compliance_requirements = Column(JSON)  # List of frameworks
    
    # Metadata and tags
    tags = Column(JSON)
    custom_attributes = Column(JSON)
    
    # Lifecycle management
    status = Column(
        Enum(BlueprintStatus),
        default=BlueprintStatus.DRAFT,
        index=True
    )
    version = Column(String(20), default="1.0.0")
    parent_blueprint_id = Column(UUID(as_uuid=True))  # For versioning
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    completed_at = Column(DateTime)
    validated_at = Column(DateTime)
    deployed_at = Column(DateTime)
    deleted_at = Column(DateTime)  # Soft delete
    
    # User tracking
    created_by = Column(String(255), nullable=False, index=True)
    updated_by = Column(String(255))
    validated_by = Column(String(255))
    deployed_by = Column(String(255))
    deleted_by = Column(String(255))
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Deployment tracking
    deployment_id = Column(String(255))
    deployment_status = Column(String(50))
    deployment_logs = Column(Text)
    
    # Metrics
    generation_duration_seconds = Column(Float)
    validation_duration_seconds = Column(Float)
    deployment_duration_seconds = Column(Float)
    
    # Soft delete flag
    is_deleted = Column(Boolean, default=False, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert blueprint to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "intent": self.intent,
            "cloud_provider": (
                self.cloud_provider.value if self.cloud_provider else None
            ),
            "region": self.region,
            "environment": (
                self.environment.value if self.environment else None
            ),
            "status": self.status.value if self.status else None,
            "version": self.version,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
            "created_by": self.created_by,
            "tags": self.tags or {},
            "cost_estimate": self.cost_estimate,
            "security_recommendations": self.security_recommendations or [],
            "compliance_results": self.compliance_results,
            "validation_results": self.validation_results
        }

    @classmethod
    async def get(cls, blueprint_id: str) -> Optional['Blueprint']:
        """Get blueprint by ID"""
        from ..repositories.blueprint import BlueprintRepository
        from ..database.connection import get_db_session
        
        async with get_db_session() as session:
            repo = BlueprintRepository(session)
            return await repo.get_by_id(blueprint_id)

    @classmethod
    async def list(
        cls,
        skip: int = 0,
        limit: int = 100,
        status: Optional[BlueprintStatus] = None,
        created_by: Optional[str] = None
    ) -> List['Blueprint']:
        """List blueprints with filtering"""
        from ..repositories.blueprint import BlueprintRepository
        from ..database.connection import get_db_session
        
        async with get_db_session() as session:
            repo = BlueprintRepository(session)
            return await repo.list_blueprints(
                skip=skip,
                limit=limit,
                status=status,
                created_by=created_by
            )

    async def save(self) -> None:
        """Save blueprint to database"""
        from ..repositories.blueprint import BlueprintRepository
        from ..database.connection import get_db_session
        
        async with get_db_session() as session:
            repo = BlueprintRepository(session)
            # Check if this is a new blueprint or update
            if hasattr(self, '_is_new') or not self.id:
                # Create new blueprint
                blueprint_data = {
                    key: getattr(self, key)
                    for key in self.__table__.columns.keys()
                    if hasattr(self, key) and getattr(self, key) is not None
                }
                await repo.create(blueprint_data)
            else:
                # Update existing blueprint
                update_data = {
                    key: getattr(self, key)
                    for key in self.__table__.columns.keys()
                    if hasattr(self, key)
                }
                await repo.update(
                    str(self.id),
                    update_data,
                    self.updated_by or "system"
                )

    async def delete(self) -> None:
        """Soft delete blueprint"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        await self.save()


class BlueprintTemplate(Base):
    """
    Reusable blueprint templates for common patterns
    """
    __tablename__ = "blueprint_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), nullable=False, index=True)
    
    # Template content
    template_code = Column(Text, nullable=False)
    template_variables = Column(JSON)  # Variable definitions
    default_values = Column(JSON)  # Default variable values
    
    # Metadata
    cloud_providers = Column(JSON)  # Supported providers
    use_cases = Column(JSON)  # Common use cases
    complexity_level = Column(String(20))  # beginner, intermediate, advanced
    
    # Lifecycle
    is_public = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255), nullable=False)
    
    # Usage metrics
    usage_count = Column(Float, default=0)
    average_rating = Column(Float, default=0.0)


class BlueprintDeployment(Base):
    """
    Deployment instances of blueprints
    """
    __tablename__ = "blueprint_deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blueprint_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Deployment metadata
    deployment_name = Column(String(255), nullable=False)
    target_subscription = Column(String(255), nullable=False)
    target_resource_group = Column(String(255))
    
    # Configuration
    deployment_parameters = Column(JSON)
    terraform_state = Column(Text)
    ansible_outputs = Column(JSON)
    
    # Status tracking
    status = Column(String(50), nullable=False, index=True)
    progress_percentage = Column(Float, default=0.0)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # User tracking
    deployed_by = Column(String(255), nullable=False)
    
    # Results
    deployment_outputs = Column(JSON)
    resource_ids = Column(JSON)  # Created resource IDs
    
    # Error handling
    error_message = Column(Text)
    deployment_logs = Column(Text)
    
    # Cost tracking
    estimated_cost = Column(Float)
    actual_cost = Column(Float)


class BlueprintAuditLog(Base):
    """
    Audit trail for blueprint operations
    """
    __tablename__ = "blueprint_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blueprint_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Event details
    event_type = Column(
        String(50),
        nullable=False,
        index=True
    )  # created, updated, deployed, etc.
    event_description = Column(Text)
    event_data = Column(JSON)  # Additional event context
    
    # User and system context
    user_id = Column(String(255), nullable=False)
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    session_id = Column(String(255))
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Compliance and security
    risk_level = Column(String(20))  # low, medium, high, critical
    compliance_impact = Column(JSON)
    
    # System metadata
    api_version = Column(String(20))
    service_version = Column(String(20))
    correlation_id = Column(String(255))  # For distributed tracing

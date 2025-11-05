"""
🧠 Saraswati Knowledge Models
============================

Pydantic models for knowledge management, document processing, and search.
Saraswati embodies wisdom, learning, and the organization of knowledge.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid


class KnowledgeCategory(str, Enum):
    """Knowledge categories for organization"""
    DOCUMENTATION = "documentation"
    RUNBOOKS = "runbooks"
    PROCEDURES = "procedures"
    TROUBLESHOOTING = "troubleshooting"
    ARCHITECTURE = "architecture"
    POLICIES = "policies"
    COMPLIANCE = "compliance"
    TRAINING = "training"
    BEST_PRACTICES = "best_practices"
    LESSONS_LEARNED = "lessons_learned"
    INCIDENT_REPORTS = "incident_reports"


class DocumentFormat(str, Enum):
    """Supported document formats"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "md"
    HTML = "html"
    JSON = "json"
    YAML = "yaml"


class KnowledgeStatus(str, Enum):
    """Knowledge article status"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class SearchScope(str, Enum):
    """Search scope options"""
    ALL = "all"
    TITLE = "title"
    CONTENT = "content"
    METADATA = "metadata"
    TAGS = "tags"


# Base Models
class KnowledgeBase(BaseModel):
    """Base knowledge article model"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    summary: Optional[str] = Field(None, description="Article summary")
    category: KnowledgeCategory = Field(..., description="Knowledge category")
    tags: List[str] = Field(default=[], description="Article tags")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    # Authoring information
    author: str = Field(..., description="Article author")
    contributors: List[str] = Field(default=[], description="Contributors")
    
    # Status and lifecycle
    status: KnowledgeStatus = Field(default=KnowledgeStatus.DRAFT)
    version: str = Field(default="1.0", description="Article version")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    # Quality metrics
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    view_count: int = Field(default=0)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    
    class Config:
        orm_mode = True
    framework: str = Field(..., description="ML framework used (e.g., tensorflow, pytorch)")
    algorithm: str = Field(..., description="Algorithm used")
    
    # Performance metrics
    metrics: Dict[str, float] = Field(default_factory=dict, description="Model performance metrics")
    accuracy: Optional[float] = Field(None, description="Model accuracy (if applicable)")
    precision: Optional[float] = Field(None, description="Model precision")
    recall: Optional[float] = Field(None, description="Model recall")
    f1_score: Optional[float] = Field(None, description="F1 score")
    
    # Training data
    training_dataset: str = Field(..., description="Training dataset identifier")
    training_size: int = Field(..., description="Number of training samples")
    validation_size: Optional[int] = Field(None, description="Number of validation samples")
    test_size: Optional[int] = Field(None, description="Number of test samples")
    
    # Infrastructure requirements
    cpu_requirements: float = Field(default=1.0, description="CPU cores required")
    memory_requirements: float = Field(default=2.0, description="Memory in GB required")
    gpu_requirements: Optional[int] = Field(None, description="GPU units required")
    
    # Model artifacts
    model_path: str = Field(..., description="Path to model artifacts")
    config_path: Optional[str] = Field(None, description="Path to model configuration")
    preprocessing_path: Optional[str] = Field(None, description="Path to preprocessing pipeline")
    
    # Lineage and governance
    created_by: str = Field(..., description="Creator of the model")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    parent_model_id: Optional[str] = Field(None, description="Parent model for versioning")
    experiment_id: Optional[str] = Field(None, description="Associated experiment ID")
    
    # Deployment information
    deployed_endpoints: List[str] = Field(default_factory=list, description="Deployed endpoint URLs")
    deployment_config: Dict[str, Any] = Field(default_factory=dict, description="Deployment configuration")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "saraswati_healing_predictor_v1",
                "name": "Infrastructure Healing Predictor",
                "version": "1.0.0",
                "model_type": "classification",
                "status": "deployed",
                "description": "Predicts infrastructure failures for proactive healing",
                "tags": ["infrastructure", "prediction", "healing"],
                "framework": "scikit-learn",
                "algorithm": "random_forest",
                "metrics": {"accuracy": 0.95, "precision": 0.93, "recall": 0.97},
                "training_dataset": "infra_logs_2024",
                "training_size": 100000,
                "cpu_requirements": 2.0,
                "memory_requirements": 4.0,
                "model_path": "/models/healing_predictor/v1/",
                "created_by": "saraswati_ai_engine"
            }
        }


class KnowledgeNode(BaseModel):
    """Knowledge Graph Node representing a concept or entity"""
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Human-readable label")
    node_type: KnowledgeType = Field(..., description="Type of knowledge")
    
    # Content and metadata
    title: str = Field(..., description="Knowledge title")
    content: str = Field(..., description="Knowledge content")
    summary: Optional[str] = Field(None, description="Brief summary")
    keywords: List[str] = Field(default_factory=list, description="Associated keywords")
    
    # Relationships and context
    parent_nodes: List[str] = Field(default_factory=list, description="Parent node IDs")
    child_nodes: List[str] = Field(default_factory=list, description="Child node IDs")
    related_nodes: List[str] = Field(default_factory=list, description="Related node IDs")
    
    # Source and validation
    source: str = Field(..., description="Source of knowledge")
    confidence_score: float = Field(default=1.0, description="Confidence in knowledge accuracy")
    validated: bool = Field(default=False, description="Whether knowledge has been validated")
    validated_by: Optional[str] = Field(None, description="Validator identifier")
    
    # Usage analytics
    access_count: int = Field(default=0, description="Number of times accessed")
    usefulness_score: float = Field(default=0.0, description="Community usefulness rating")
    
    # Temporal information
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Knowledge expiration date")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "kubernetes_troubleshooting_pod_crashloop",
                "label": "Pod CrashLoopBackOff Resolution",
                "node_type": "troubleshooting",
                "title": "Resolving Kubernetes Pod CrashLoopBackOff",
                "content": "Step-by-step guide to diagnose and fix CrashLoopBackOff...",
                "summary": "Common causes and solutions for pod restart loops",
                "keywords": ["kubernetes", "pods", "crashloop", "troubleshooting"],
                "source": "kubernetes_operations_team",
                "confidence_score": 0.95,
                "validated": True
            }
        }


class KnowledgeRelationship(BaseModel):
    """Relationship between knowledge nodes"""
    id: str = Field(..., description="Unique relationship identifier")
    source_node_id: str = Field(..., description="Source node ID")
    target_node_id: str = Field(..., description="Target node ID")
    relationship_type: str = Field(..., description="Type of relationship")
    weight: float = Field(default=1.0, description="Relationship strength")
    bidirectional: bool = Field(default=False, description="Whether relationship is bidirectional")
    
    # Metadata
    description: Optional[str] = Field(None, description="Relationship description")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="Creator of the relationship")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "rel_pod_troubleshooting_to_kubernetes_basics",
                "source_node_id": "kubernetes_troubleshooting_pod_crashloop",
                "target_node_id": "kubernetes_basics_pods",
                "relationship_type": "requires_knowledge_of",
                "weight": 0.8,
                "bidirectional": False,
                "description": "Pod troubleshooting requires basic pod knowledge"
            }
        }


class ModelRegistry(BaseModel):
    """Model registry for managing ML model lifecycle"""
    id: str = Field(..., description="Registry identifier")
    name: str = Field(..., description="Registry name")
    description: str = Field(..., description="Registry description")
    
    # Models in registry
    models: List[str] = Field(default_factory=list, description="Model IDs in registry")
    featured_models: List[str] = Field(default_factory=list, description="Featured model IDs")
    
    # Access control
    public: bool = Field(default=False, description="Whether registry is public")
    authorized_users: List[str] = Field(default_factory=list, description="Authorized user IDs")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="Registry creator")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "infrastructure_models",
                "name": "Infrastructure AI Models",
                "description": "Collection of ML models for infrastructure management",
                "models": ["saraswati_healing_predictor_v1", "cost_optimizer_v2"],
                "featured_models": ["saraswati_healing_predictor_v1"],
                "public": True,
                "created_by": "saraswati_engine"
            }
        }


class WisdomQuery(BaseModel):
    """Query for knowledge retrieval"""
    query: str = Field(..., description="Natural language query")
    knowledge_types: Optional[List[KnowledgeType]] = Field(None, description="Filter by knowledge types")
    limit: int = Field(default=10, description="Maximum results to return")
    min_confidence: float = Field(default=0.0, description="Minimum confidence score")
    include_related: bool = Field(default=True, description="Include related knowledge")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "How to fix high CPU usage in Kubernetes pods",
                "knowledge_types": ["troubleshooting", "performance"],
                "limit": 5,
                "min_confidence": 0.7,
                "include_related": True
            }
        }


class WisdomResponse(BaseModel):
    """Response from knowledge query"""
    query: str = Field(..., description="Original query")
    results: List[KnowledgeNode] = Field(..., description="Matching knowledge nodes")
    related_models: List[MLModel] = Field(default_factory=list, description="Related ML models")
    total_results: int = Field(..., description="Total number of results")
    confidence_score: float = Field(..., description="Overall confidence in results")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "How to fix high CPU usage in Kubernetes pods",
                "results": [],
                "related_models": [],
                "total_results": 3,
                "confidence_score": 0.85
            }
        }

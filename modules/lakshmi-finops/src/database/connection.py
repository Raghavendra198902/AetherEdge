"""
💰 Lakshmi FinOps Database Connection
====================================

Database connection and schema management for the divine financial operations engine.
Lakshmi's prosperity flows through structured financial data patterns.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, Index, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..config import get_database_url

logger = logging.getLogger(__name__)

Base = declarative_base()


class CostEntryDB(Base):
    """Cost entry database model"""
    __tablename__ = "cost_entries"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Resource identification
    resource_id = Column(String(255), nullable=False, index=True)
    resource_name = Column(String(500), nullable=False)
    resource_type = Column(String(50), nullable=False, index=True)
    
    # Provider information
    cloud_provider = Column(String(50), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    availability_zone = Column(String(100))
    
    # Cost details
    cost_amount = Column(DECIMAL(precision=15, scale=4), nullable=False)
    currency = Column(String(3), default="USD")
    billing_period_start = Column(DateTime(timezone=True), nullable=False)
    billing_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Organization
    account_id = Column(String(255), nullable=False, index=True)
    project_id = Column(String(255), index=True)
    department = Column(String(255), index=True)
    team = Column(String(255), index=True)
    environment = Column(String(50), index=True)
    
    # Categorization
    category = Column(String(50), nullable=False, index=True)
    tags = Column(JSON, default=dict)
    
    # Usage metrics
    usage_quantity = Column(DECIMAL(precision=15, scale=4))
    usage_unit = Column(String(50))
    rate = Column(DECIMAL(precision=15, scale=6))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_cost_provider_type', 'cloud_provider', 'resource_type'),
        Index('idx_cost_billing_period', 'billing_period_start', 'billing_period_end'),
        Index('idx_cost_account_category', 'account_id', 'category'),
        Index('idx_cost_amount_desc', 'cost_amount'),
    )


class BudgetDB(Base):
    """Budget database model"""
    __tablename__ = "budgets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Budget scope
    account_ids = Column(JSON, nullable=False)
    project_ids = Column(JSON, default=list)
    departments = Column(JSON, default=list)
    categories = Column(JSON, default=list)
    
    # Budget amounts
    total_amount = Column(DECIMAL(precision=15, scale=2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Time period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Thresholds
    warning_threshold = Column(Float, default=80.0)
    critical_threshold = Column(Float, default=95.0)
    
    # Status tracking
    current_spend = Column(DECIMAL(precision=15, scale=2), default=0.00)
    forecasted_spend = Column(DECIMAL(precision=15, scale=2))
    status = Column(String(20), default="on_track")
    
    # Metadata
    created_by = Column(String(255), nullable=False)
    approved_by = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_budget_period', 'period_start', 'period_end'),
        Index('idx_budget_status', 'status'),
        Index('idx_budget_created_by', 'created_by'),
    )


class OptimizationRecommendationDB(Base):
    """Optimization recommendation database model"""
    __tablename__ = "optimization_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Target resource
    resource_id = Column(String(255), nullable=False, index=True)
    resource_name = Column(String(500), nullable=False)
    resource_type = Column(String(50), nullable=False, index=True)
    cloud_provider = Column(String(50), nullable=False, index=True)
    
    # Optimization details
    optimization_type = Column(String(100), nullable=False)
    current_cost = Column(DECIMAL(precision=15, scale=2), nullable=False)
    optimized_cost = Column(DECIMAL(precision=15, scale=2), nullable=False)
    savings_amount = Column(DECIMAL(precision=15, scale=2), nullable=False)
    savings_percentage = Column(Float, nullable=False)
    
    # Implementation
    implementation_effort = Column(String(50), nullable=False)
    implementation_steps = Column(JSON, default=list)
    prerequisites = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    
    # Priority and confidence
    priority = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    # Status tracking
    status = Column(String(20), default="identified", index=True)
    assigned_to = Column(String(255))
    due_date = Column(DateTime(timezone=True))
    
    # Metadata
    category = Column(String(50), nullable=False, index=True)
    tags = Column(JSON, default=list)
    
    # Timestamps
    identified_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    implemented_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_recommendation_status_priority', 'status', 'priority'),
        Index('idx_recommendation_savings', 'savings_amount'),
        Index('idx_recommendation_confidence', 'confidence_score'),
    )


class CostAlertDB(Base):
    """Cost alert database model"""
    __tablename__ = "cost_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    
    # Alert details
    severity = Column(String(20), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    
    # Trigger conditions
    trigger_resource = Column(String(255))
    trigger_account = Column(String(255))
    trigger_amount = Column(DECIMAL(precision=15, scale=2))
    threshold_amount = Column(DECIMAL(precision=15, scale=2))
    
    # Resolution
    is_resolved = Column(Boolean, default=False, index=True)
    resolved_by = Column(String(255))
    resolution_notes = Column(Text)
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_alert_severity_resolved', 'severity', 'is_resolved'),
        Index('idx_alert_triggered_at', 'triggered_at'),
    )


class CostForecastDB(Base):
    """Cost forecast database model"""
    __tablename__ = "cost_forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope = Column(String(255), nullable=False, index=True)
    
    # Forecast details
    forecast_period_start = Column(DateTime(timezone=True), nullable=False)
    forecast_period_end = Column(DateTime(timezone=True), nullable=False)
    forecasted_amount = Column(DECIMAL(precision=15, scale=2), nullable=False)
    confidence_interval_lower = Column(DECIMAL(precision=15, scale=2), nullable=False)
    confidence_interval_upper = Column(DECIMAL(precision=15, scale=2), nullable=False)
    confidence_level = Column(Float, default=0.95)
    
    # Model information
    model_type = Column(String(50), nullable=False)
    model_accuracy = Column(Float)
    
    # Historical data
    historical_period_days = Column(Integer, nullable=False)
    trend_direction = Column(String(20), nullable=False)
    seasonality_detected = Column(Boolean, default=False)
    
    # Metadata
    currency = Column(String(3), default="USD")
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_forecast_period', 'forecast_period_start', 'forecast_period_end'),
        Index('idx_forecast_scope', 'scope'),
    )


class DatabaseConnection:
    """Database connection manager for Lakshmi"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to database"""
        try:
            database_url = get_database_url()
            logger.info("🔌 Connecting to Lakshmi FinOps database...")
            
            # Create async engine
            self.engine = create_async_engine(
                database_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self._connected = True
            logger.info("✅ Connected to Lakshmi FinOps database")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from database"""
        if self.engine:
            logger.info("🔌 Disconnecting from Lakshmi FinOps database...")
            await self.engine.dispose()
            self._connected = False
            logger.info("✅ Disconnected from database")
    
    async def initialize_schema(self) -> None:
        """Initialize database schema"""
        if not self._connected:
            raise RuntimeError("Database not connected")
        
        try:
            logger.info("🏗️ Initializing Lakshmi FinOps schema...")
            
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("✅ FinOps schema initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize schema: {str(e)}")
            raise
    
    async def get_session(self) -> AsyncSession:
        """Get database session"""
        if not self._connected:
            raise RuntimeError("Database not connected")
        
        return self.session_factory()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            if not self._connected:
                return {
                    "status": "disconnected",
                    "error": "Database not connected"
                }
            
            async with self.get_session() as session:
                # Simple query to test connection
                result = await session.execute("SELECT 1")
                result.fetchone()
                
                # Get table counts
                cost_count = await session.execute(
                    "SELECT COUNT(*) FROM cost_entries"
                )
                total_costs = cost_count.scalar()
                
                budget_count = await session.execute(
                    "SELECT COUNT(*) FROM budgets"
                )
                total_budgets = budget_count.scalar()
                
                return {
                    "status": "healthy",
                    "total_cost_entries": total_costs,
                    "total_budgets": total_budgets,
                    "connection_pool_size": self.engine.pool.size(),
                    "checked_out_connections": self.engine.pool.checkedout()
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connected


# Global database connection instance
db_connection = DatabaseConnection()


async def get_db_session() -> AsyncSession:
    """Dependency to get database session"""
    return await db_connection.get_session()


# Utility functions
async def get_cost_summary(
    start_date: str, 
    end_date: str, 
    account_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get cost summary for a period"""
    async with db_connection.get_session() as session:
        # Build query
        query = """
        SELECT 
            SUM(cost_amount) as total_cost,
            COUNT(*) as total_entries,
            AVG(cost_amount) as avg_cost
        FROM cost_entries 
        WHERE billing_period_start >= %s 
        AND billing_period_end <= %s
        """
        
        params = [start_date, end_date]
        
        if account_ids:
            query += " AND account_id = ANY(%s)"
            params.append(account_ids)
        
        result = await session.execute(query, params)
        row = result.fetchone()
        
        return {
            "total_cost": float(row[0]) if row[0] else 0.0,
            "total_entries": row[1] if row[1] else 0,
            "average_cost": float(row[2]) if row[2] else 0.0,
            "period_start": start_date,
            "period_end": end_date
        }

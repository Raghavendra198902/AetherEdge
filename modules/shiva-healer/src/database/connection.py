"""
🔥 Shiva Database Connection
===========================

Async PostgreSQL database connection management for Shiva healer.
"""

import asyncio
import logging
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool
import os

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Divine database connection manager for Shiva
    """
    
    def __init__(self):
        self.pool: Optional[Pool] = None
        self.connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """Build database connection string from environment variables"""
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        database = os.getenv("POSTGRES_DB", "shiva_db")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
        
        # Handle Docker secrets
        if password.startswith("/run/secrets/"):
            try:
                with open(password, 'r') as f:
                    password = f.read().strip()
            except Exception as e:
                logger.error(f"Failed to read password from secrets: {e}")
                password = ""
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    async def connect(self) -> bool:
        """Establish database connection pool"""
        try:
            logger.info("Connecting to Shiva database...")
            
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=5,
                max_size=20,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
                command_timeout=30
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            
            logger.info("Database connection pool established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            logger.info("Closing database connection pool...")
            await self.pool.close()
            self.pool = None
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def health_check(self) -> dict:
        """Perform database health check"""
        try:
            if not self.pool:
                return {"status": "unhealthy", "error": "No connection pool"}
            
            async with self.pool.acquire() as conn:
                start_time = asyncio.get_event_loop().time()
                await conn.fetchval("SELECT 1")
                response_time = asyncio.get_event_loop().time() - start_time
                
                pool_stats = {
                    "size": self.pool.get_size(),
                    "max_size": self.pool.get_max_size(),
                    "min_size": self.pool.get_min_size()
                }
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time * 1000, 2),
                    "pool_stats": pool_stats
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def initialize_schema(self):
        """Initialize database schema for Shiva"""
        try:
            logger.info("Initializing Shiva database schema...")
            
            schema_sql = """
            -- Healing actions table
            CREATE TABLE IF NOT EXISTS healing_actions (
                id VARCHAR(36) PRIMARY KEY,
                resource_id VARCHAR(255) NOT NULL,
                resource_type VARCHAR(100) NOT NULL,
                issue_type VARCHAR(100) NOT NULL,
                issue_description TEXT,
                healing_strategy VARCHAR(50) DEFAULT 'conservative',
                status VARCHAR(20) DEFAULT 'pending',
                priority VARCHAR(20) DEFAULT 'medium',
                auto_approved BOOLEAN DEFAULT FALSE,
                rollback_enabled BOOLEAN DEFAULT TRUE,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                execution_duration FLOAT,
                actions_taken JSONB,
                success_rate FLOAT,
                metrics_before JSONB,
                metrics_after JSONB,
                rollback_data JSONB,
                triggered_by VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Anomaly reports table
            CREATE TABLE IF NOT EXISTS anomaly_reports (
                id VARCHAR(36) PRIMARY KEY,
                resource_id VARCHAR(255) NOT NULL,
                resource_type VARCHAR(100) NOT NULL,
                anomaly_type VARCHAR(50) NOT NULL,
                severity VARCHAR(20) DEFAULT 'medium',
                confidence_score FLOAT NOT NULL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                time_window_start TIMESTAMP NOT NULL,
                time_window_end TIMESTAMP NOT NULL,
                baseline_values JSONB,
                anomaly_values JSONB,
                threshold_breached JSONB,
                correlation_data JSONB,
                root_cause_analysis TEXT,
                impact_assessment JSONB,
                recommended_actions JSONB,
                status VARCHAR(20) DEFAULT 'open',
                assigned_to VARCHAR(100),
                resolved_at TIMESTAMP,
                resolution_notes TEXT,
                healing_action_id VARCHAR(36),
                auto_healing_triggered BOOLEAN DEFAULT FALSE
            );
            
            -- Performance optimizations table
            CREATE TABLE IF NOT EXISTS performance_optimizations (
                id VARCHAR(36) PRIMARY KEY,
                resource_id VARCHAR(255) NOT NULL,
                optimization_type VARCHAR(100) NOT NULL,
                baseline_metrics JSONB NOT NULL,
                target_metrics JSONB NOT NULL,
                optimization_actions JSONB NOT NULL,
                status VARCHAR(20) DEFAULT 'planned',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                actual_metrics JSONB,
                improvement_percentage FLOAT,
                cost_impact FLOAT,
                performance_score FLOAT,
                triggered_by VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Auto-scaling events table
            CREATE TABLE IF NOT EXISTS autoscaling_events (
                id VARCHAR(36) PRIMARY KEY,
                resource_id VARCHAR(255) NOT NULL,
                resource_type VARCHAR(100) NOT NULL,
                scaling_action VARCHAR(50) NOT NULL,
                trigger_metric VARCHAR(100) NOT NULL,
                trigger_value FLOAT NOT NULL,
                threshold_value FLOAT NOT NULL,
                capacity_before JSONB,
                capacity_after JSONB,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                success BOOLEAN,
                error_message TEXT,
                cost_impact FLOAT,
                performance_impact JSONB
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_healing_actions_resource ON healing_actions(resource_id);
            CREATE INDEX IF NOT EXISTS idx_healing_actions_status ON healing_actions(status);
            CREATE INDEX IF NOT EXISTS idx_anomaly_reports_resource ON anomaly_reports(resource_id);
            CREATE INDEX IF NOT EXISTS idx_anomaly_reports_severity ON anomaly_reports(severity);
            CREATE INDEX IF NOT EXISTS idx_performance_opt_resource ON performance_optimizations(resource_id);
            """
            
            async with self.pool.acquire() as conn:
                await conn.execute(schema_sql)
            
            logger.info("Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise


# Global database connection instance
db_connection = DatabaseConnection()

"""
🛡️ Vishnu Database Connection
=============================

Async PostgreSQL database connection management for Vishnu orchestrator.
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
    Divine database connection manager for Vishnu
    """
    
    def __init__(self):
        self.pool: Optional[Pool] = None
        self.connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """Build database connection string from environment variables"""
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        database = os.getenv("POSTGRES_DB", "vishnu_db")
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
        """
        Establish database connection pool
        """
        try:
            logger.info("Connecting to Vishnu database...")
            
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
        """
        Close database connection pool
        """
        if self.pool:
            logger.info("Closing database connection pool...")
            await self.pool.close()
            self.pool = None
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Get database connection from pool
        """
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def health_check(self) -> dict:
        """
        Perform database health check
        """
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
        """
        Initialize database schema for Vishnu
        """
        try:
            logger.info("Initializing Vishnu database schema...")
            
            schema_sql = """
            -- Policies table
            CREATE TABLE IF NOT EXISTS policies (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                policy_type VARCHAR(50) NOT NULL,
                rules JSONB NOT NULL,
                scope JSONB NOT NULL,
                enforcement_mode VARCHAR(20) DEFAULT 'monitor',
                compliance_framework VARCHAR(100),
                severity VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'active',
                created_by VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_evaluated TIMESTAMP
            );
            
            -- Compliance checks table
            CREATE TABLE IF NOT EXISTS compliance_checks (
                id VARCHAR(36) PRIMARY KEY,
                check_name VARCHAR(255) NOT NULL,
                frameworks JSONB NOT NULL,
                resources JSONB NOT NULL,
                overall_score FLOAT,
                total_violations INTEGER DEFAULT 0,
                critical_violations INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'running',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                checked_by VARCHAR(100) NOT NULL,
                report_path VARCHAR(500)
            );
            
            -- Compliance results table
            CREATE TABLE IF NOT EXISTS compliance_results (
                id VARCHAR(36) PRIMARY KEY,
                check_id VARCHAR(36) NOT NULL,
                resource_id VARCHAR(255) NOT NULL,
                framework VARCHAR(100) NOT NULL,
                rule_id VARCHAR(100),
                rule_name VARCHAR(255),
                status VARCHAR(20),
                score FLOAT,
                violation_details JSONB,
                remediation_advice TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Workflow executions table
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                workflow_definition JSONB NOT NULL,
                target_resources JSONB NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                progress_percentage FLOAT DEFAULT 0.0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_by VARCHAR(100) NOT NULL,
                approval_required BOOLEAN DEFAULT FALSE,
                approved_by VARCHAR(100),
                approved_at TIMESTAMP,
                execution_results JSONB,
                error_messages JSONB
            );
            
            -- Policy violations table
            CREATE TABLE IF NOT EXISTS policy_violations (
                id VARCHAR(36) PRIMARY KEY,
                policy_id VARCHAR(36) NOT NULL,
                resource_id VARCHAR(255) NOT NULL,
                violation_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'open',
                violation_details JSONB,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged_at TIMESTAMP,
                remediated_at TIMESTAMP,
                acknowledged_by VARCHAR(100),
                remediation_action TEXT
            );
            
            -- Remediation actions table
            CREATE TABLE IF NOT EXISTS remediation_actions (
                id VARCHAR(36) PRIMARY KEY,
                violation_id VARCHAR(36) NOT NULL,
                action_type VARCHAR(100) NOT NULL,
                action_details JSONB,
                status VARCHAR(20) DEFAULT 'pending',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                triggered_by VARCHAR(100) NOT NULL,
                result JSONB,
                error_message TEXT
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_policies_type ON policies(policy_type);
            CREATE INDEX IF NOT EXISTS idx_policies_status ON policies(status);
            CREATE INDEX IF NOT EXISTS idx_violations_policy ON policy_violations(policy_id);
            CREATE INDEX IF NOT EXISTS idx_violations_status ON policy_violations(status);
            CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflow_executions(status);
            """
            
            async with self.pool.acquire() as conn:
                await conn.execute(schema_sql)
            
            logger.info("Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise


# Global database connection instance
db_connection = DatabaseConnection()

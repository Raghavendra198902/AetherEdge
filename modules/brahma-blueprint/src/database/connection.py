"""
🗄️ Database Connection and Session Management
==============================================

Database configuration and session management for the Brahma Blueprint module.
Implements connection pooling, health checks, and transaction management.
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom database exception"""
    pass


# Database configuration from environment
_default_db_url = (
    "postgresql+asyncpg://aetheredge:"
    "${POSTGRES_PASSWORD}@localhost:5432/aetheredge_brahma"
)
DATABASE_URL = os.getenv("DATABASE_URL", _default_db_url)

# Pool configuration
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,  # Validate connections before use
    # Use NullPool for development/testing
    poolclass=NullPool if os.getenv("ENVIRONMENT") == "development" else None
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)

# Base class for models
Base = declarative_base()


class DatabaseManager:
    """Database manager for handling connections and sessions"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
        
    async def create_tables(self):
        """Create all database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Error creating database tables: %s", str(e))
            raise
    
    async def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error("Error dropping database tables: %s", str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            async with self.session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error("Database health check failed: %s", str(e))
            return False
    
    async def get_connection_info(self) -> dict:
        """Get database connection information"""
        try:
            async with self.session_factory() as session:
                # Get database version
                version_result = await session.execute(
                    text("SELECT version()")
                )
                version = version_result.scalar()
                
                # Get current database
                db_result = await session.execute(
                    text("SELECT current_database()")
                )
                database = db_result.scalar()
                
                # Get connection count
                conn_query = (
                    "SELECT count(*) FROM pg_stat_activity "
                    "WHERE state = 'active'"
                )
                conn_result = await session.execute(text(conn_query))
                active_connections = conn_result.scalar()
                
                return {
                    "database": database,
                    "version": version,
                    "active_connections": active_connections,
                    "pool_size": POOL_SIZE,
                    "max_overflow": MAX_OVERFLOW,
                    "status": "healthy"
                }
        except Exception as e:
            logger.error("Error getting connection info: %s", str(e))
            return {"status": "unhealthy", "error": str(e)}
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session for FastAPI"""
    async with db_manager.get_session() as session:
        yield session


async def init_database():
    """Initialize database on startup"""
    try:
        logger.info("Initializing database...")
        await db_manager.create_tables()
        
        # Verify connection
        if await db_manager.health_check():
            logger.info("Database initialization completed successfully")
        else:
            raise DatabaseError(
                "Database health check failed after initialization"
            )
            
    except Exception as e:
        logger.error("Database initialization failed: %s", str(e))
        raise


async def close_database():
    """Close database connections on shutdown"""
    try:
        logger.info("Closing database connections...")
        await db_manager.close()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error("Error closing database connections: %s", str(e))

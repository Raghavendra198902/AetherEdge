"""
Database configuration and connection management

Handles database connections, session management, and initialization
for PostgreSQL with SQLAlchemy and TimescaleDB support.
"""

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import asyncpg
import asyncio
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from .config import settings

logger = logging.getLogger(__name__)

# Database engine and session configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Metadata for schema reflection
metadata = MetaData()


async def init_db():
    """Initialize database connection and create tables if needed"""
    try:
        logger.info("Initializing database connection...")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("Database connection successful")
        
        # Create tables (in production, use Alembic migrations)
        if settings.ENVIRONMENT == "development":
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created")
            
        logger.info("Database initialization complete")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


async def close_db():
    """Close database connections"""
    try:
        logger.info("Closing database connections...")
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")


def get_db() -> Session:
    """
    Dependency for getting database session
    
    Usage in FastAPI endpoints:
    async def endpoint(db: Session = Depends(get_db)):
        # Use db session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[Session, None]:
    """Async context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# TimescaleDB specific functions
def enable_timescaledb_extension():
    """Enable TimescaleDB extension for time-series data"""
    try:
        with engine.connect() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            logger.info("TimescaleDB extension enabled")
    except Exception as e:
        logger.warning(f"Could not enable TimescaleDB: {str(e)}")


def create_hypertable(table_name: str, time_column: str = "timestamp"):
    """Create TimescaleDB hypertable for time-series data"""
    try:
        with engine.connect() as conn:
            query = f"SELECT create_hypertable('{table_name}', '{time_column}', if_not_exists => TRUE);"
            conn.execute(query)
            logger.info(f"Hypertable created for {table_name}")
    except Exception as e:
        logger.warning(f"Could not create hypertable for {table_name}: {str(e)}")


# Database health check
async def check_db_health() -> dict:
    """Check database health and return status"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT version();")
            version = result.fetchone()[0]
            
            # Check TimescaleDB
            try:
                ts_result = conn.execute("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';")
                ts_version = ts_result.fetchone()
                timescaledb_version = ts_version[0] if ts_version else None
            except:
                timescaledb_version = None
            
            return {
                "status": "healthy",
                "postgres_version": version,
                "timescaledb_version": timescaledb_version,
                "pool_size": engine.pool.size(),
                "checked_out": engine.pool.checkedout(),
                "checked_in": engine.pool.checkedin()
            }
            
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Event listeners for connection management
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for development/testing"""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log SQL queries in debug mode"""
    if settings.DEBUG:
        logger.debug(f"SQL: {statement}")
        if parameters:
            logger.debug(f"Parameters: {parameters}")

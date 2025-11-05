"""
🧠 Saraswati Knowledge Database Connection
=========================================

Database connection and schema management for the divine knowledge engine.
Saraswati's wisdom flows through structured data patterns.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..config import get_database_url

logger = logging.getLogger(__name__)

Base = declarative_base()


class KnowledgeArticle(Base):
    """Knowledge article database model"""
    __tablename__ = "knowledge_articles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core content
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    
    # Organization
    category = Column(String(50), nullable=False, index=True)
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    
    # Authoring
    author = Column(String(255), nullable=False, index=True)
    contributors = Column(JSON, default=list)
    
    # Status and versioning
    status = Column(String(20), default="draft", index=True)
    version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Quality and analytics
    quality_score = Column(Float)
    view_count = Column(Integer, default=0)
    rating = Column(Float)
    
    # Search optimization
    content_vector = Column(Text)  # For vector embeddings
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_knowledge_category_status', 'category', 'status'),
        Index('idx_knowledge_created_at', 'created_at'),
        Index('idx_knowledge_author_status', 'author', 'status'),
        Index('idx_knowledge_quality_score', 'quality_score'),
    )


class KnowledgeComment(Base):
    """Knowledge article comments"""
    __tablename__ = "knowledge_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Comment content
    comment = Column(Text, nullable=False)
    author = Column(String(255), nullable=False)
    
    # Metadata
    is_suggestion = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_comments_article_id', 'article_id'),
        Index('idx_comments_author', 'author'),
    )


class KnowledgeRating(Base):
    """Knowledge article ratings"""
    __tablename__ = "knowledge_ratings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Rating details
    user_id = Column(String(255), nullable=False)
    rating = Column(Float, nullable=False)  # 1.0 to 5.0
    review = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_ratings_article_id', 'article_id'),
        Index('idx_ratings_user_id', 'user_id'),
    )


class KnowledgeAnalytics(Base):
    """Knowledge analytics and metrics"""
    __tablename__ = "knowledge_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Analytics data
    event_type = Column(String(50), nullable=False)  # view, search, download, etc.
    user_id = Column(String(255))
    session_id = Column(String(255))
    
    # Context
    search_query = Column(String(500))
    referrer = Column(String(500))
    user_agent = Column(String(500))
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_analytics_article_id', 'article_id'),
        Index('idx_analytics_event_type', 'event_type'),
        Index('idx_analytics_created_at', 'created_at'),
    )


class DatabaseConnection:
    """Database connection manager for Saraswati"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to database"""
        try:
            database_url = get_database_url()
            logger.info("🔌 Connecting to Saraswati knowledge database...")
            
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
            logger.info("✅ Connected to Saraswati knowledge database")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from database"""
        if self.engine:
            logger.info("🔌 Disconnecting from Saraswati knowledge database...")
            await self.engine.dispose()
            self._connected = False
            logger.info("✅ Disconnected from database")
    
    async def initialize_schema(self) -> None:
        """Initialize database schema"""
        if not self._connected:
            raise RuntimeError("Database not connected")
        
        try:
            logger.info("🏗️ Initializing Saraswati knowledge schema...")
            
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("✅ Knowledge schema initialized successfully")
            
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
                article_count = await session.execute(
                    "SELECT COUNT(*) FROM knowledge_articles"
                )
                total_articles = article_count.scalar()
                
                return {
                    "status": "healthy",
                    "total_articles": total_articles,
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
async def execute_query(query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Execute raw SQL query"""
    async with db_connection.get_session() as session:
        result = await session.execute(query, params or {})
        return [dict(row) for row in result.fetchall()]


async def get_article_stats() -> Dict[str, Any]:
    """Get knowledge article statistics"""
    async with db_connection.get_session() as session:
        # Total articles
        total_query = "SELECT COUNT(*) as total FROM knowledge_articles"
        total_result = await session.execute(total_query)
        total = total_result.scalar()
        
        # Published articles
        published_query = "SELECT COUNT(*) as published FROM knowledge_articles WHERE status = 'published'"
        published_result = await session.execute(published_query)
        published = published_result.scalar()
        
        # Average quality score
        quality_query = "SELECT AVG(quality_score) as avg_quality FROM knowledge_articles WHERE quality_score IS NOT NULL"
        quality_result = await session.execute(quality_query)
        avg_quality = quality_result.scalar() or 0.0
        
        # Total views
        views_query = "SELECT SUM(view_count) as total_views FROM knowledge_articles"
        views_result = await session.execute(views_query)
        total_views = views_result.scalar() or 0
        
        return {
            "total_articles": total,
            "published_articles": published,
            "draft_articles": total - published,
            "average_quality_score": round(avg_quality, 2),
            "total_views": total_views
        }

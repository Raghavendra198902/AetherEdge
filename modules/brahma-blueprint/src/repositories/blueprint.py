"""
📊 Blueprint Repository Layer
=============================

Data access layer for Blueprint entities with advanced querying,
caching, and transaction management capabilities.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import IntegrityError

from ..models.blueprint import (
    Blueprint,
    BlueprintStatus,
    BlueprintTemplate,
    BlueprintDeployment,
    BlueprintAuditLog
)
from ..database.connection import get_db_session

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


class BlueprintRepository:
    """Repository for Blueprint entity operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, blueprint_data: Dict[str, Any]) -> Blueprint:
        """Create a new blueprint"""
        try:
            blueprint = Blueprint(**blueprint_data)
            self.session.add(blueprint)
            await self.session.flush()  # Get the ID without committing
            
            # Log creation event
            await self._log_audit_event(
                blueprint.id,
                "created",
                "Blueprint created",
                blueprint_data.get("created_by", "system"),
                {"initial_data": blueprint_data}
            )
            
            logger.info("Blueprint created: %s", blueprint.id)
            return blueprint
            
        except IntegrityError as e:
            logger.error("Integrity error creating blueprint: %s", str(e))
            raise ValueError(f"Blueprint creation failed: {str(e)}")
        except Exception as e:
            logger.error("Error creating blueprint: %s", str(e))
            raise
    
    async def get_by_id(self, blueprint_id: str) -> Optional[Blueprint]:
        """Get blueprint by ID"""
        try:
            result = await self.session.execute(
                select(Blueprint)
                .where(
                    and_(
                        Blueprint.id == blueprint_id,
                        Blueprint.is_deleted.is_(False)
                    )
                )
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Error getting blueprint %s: %s", blueprint_id, str(e)
            )
            raise
    
    async def get_by_name(
        self,
        name: str,
        created_by: Optional[str] = None
    ) -> Optional[Blueprint]:
        """Get blueprint by name"""
        try:
            query = select(Blueprint).where(
                and_(
                    Blueprint.name == name,
                    Blueprint.is_deleted.is_(False)
                )
            )
            
            if created_by:
                query = query.where(Blueprint.created_by == created_by)
            
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Error getting blueprint by name %s: %s", name, str(e)
            )
            raise
    
    async def list_blueprints(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[BlueprintStatus] = None,
        created_by: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        environment: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> List[Blueprint]:
        """List blueprints with filtering"""
        try:
            query = select(Blueprint).where(Blueprint.is_deleted.is_(False))
            
            # Apply filters
            if status:
                query = query.where(Blueprint.status == status)
            
            if created_by:
                query = query.where(Blueprint.created_by == created_by)
            
            if cloud_provider:
                query = query.where(Blueprint.cloud_provider == cloud_provider)
            
            if environment:
                query = query.where(Blueprint.environment == environment)
            
            if search_term:
                search_filter = or_(
                    Blueprint.name.ilike(f"%{search_term}%"),
                    Blueprint.description.ilike(f"%{search_term}%"),
                    Blueprint.intent.ilike(f"%{search_term}%")
                )
                query = query.where(search_filter)
            
            # Apply pagination and ordering
            query = (query
                     .order_by(Blueprint.created_at.desc())
                     .offset(skip)
                     .limit(limit))
            
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Error listing blueprints: %s", str(e))
            raise
    
    async def update(
        self,
        blueprint_id: str,
        update_data: Dict[str, Any],
        updated_by: str
    ) -> Optional[Blueprint]:
        """Update blueprint"""
        try:
            # Get current blueprint
            blueprint = await self.get_by_id(blueprint_id)
            if not blueprint:
                return None
            
            # Track what changed
            changes = {}
            for key, value in update_data.items():
                if hasattr(blueprint, key):
                    old_value = getattr(blueprint, key)
                    if old_value != value:
                        changes[key] = {"old": old_value, "new": value}
                        setattr(blueprint, key, value)
            
            # Update metadata
            blueprint.updated_at = utc_now()
            blueprint.updated_by = updated_by
            
            await self.session.flush()
            
            # Log update event
            if changes:
                await self._log_audit_event(
                    blueprint_id,
                    "updated",
                    f"Blueprint updated by {updated_by}",
                    updated_by,
                    {"changes": changes}
                )
            
            logger.info("Blueprint updated: %s", blueprint_id)
            return blueprint
            
        except Exception as e:
            logger.error("Error updating blueprint %s: %s", blueprint_id, str(e))
            raise
    
    async def delete(self, blueprint_id: str, deleted_by: str) -> bool:
        """Soft delete blueprint"""
        try:
            blueprint = await self.get_by_id(blueprint_id)
            if not blueprint:
                return False
            
            # Soft delete
            blueprint.is_deleted = True
            blueprint.deleted_at = utc_now()
            blueprint.deleted_by = deleted_by
            
            await self.session.flush()
            
            # Log deletion event
            await self._log_audit_event(
                blueprint_id,
                "deleted",
                f"Blueprint deleted by {deleted_by}",
                deleted_by,
                {"deletion_reason": "user_request"}
            )
            
            logger.info("Blueprint deleted: %s", blueprint_id)
            return True
            
        except Exception as e:
            logger.error("Error deleting blueprint %s: %s", blueprint_id, str(e))
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get blueprint statistics"""
        try:
            # Total count
            total_result = await self.session.execute(
                select(func.count()).select_from(Blueprint)
                .where(Blueprint.is_deleted.is_(False))
            )
            total_count = total_result.scalar()
            
            # Status distribution
            status_result = await self.session.execute(
                select(Blueprint.status, func.count())
                .where(Blueprint.is_deleted.is_(False))
                .group_by(Blueprint.status)
            )
            status_distribution = dict(status_result.all())
            
            # Recent activity (last 7 days)
            from datetime import timedelta
            week_ago = utc_now() - timedelta(days=7)
            recent_result = await self.session.execute(
                select(func.count()).select_from(Blueprint)
                .where(
                    and_(
                        Blueprint.is_deleted.is_(False),
                        Blueprint.created_at >= week_ago
                    )
                )
            )
            recent_count = recent_result.scalar()
            
            return {
                "total_blueprints": total_count,
                "status_distribution": status_distribution,
                "recent_blueprints": recent_count,
                "last_updated": utc_now().isoformat()
            }
            
        except Exception as e:
            logger.error("Error getting blueprint statistics: %s", str(e))
            raise
    
    async def _log_audit_event(
        self,
        blueprint_id: str,
        event_type: str,
        description: str,
        user_id: str,
        event_data: Optional[Dict[str, Any]] = None
    ):
        """Log audit event"""
        try:
            audit_log = BlueprintAuditLog(
                blueprint_id=blueprint_id,
                event_type=event_type,
                event_description=description,
                event_data=event_data or {},
                user_id=user_id,
                timestamp=utc_now()
            )
            
            self.session.add(audit_log)
            await self.session.flush()
            
        except Exception as e:
            logger.error("Error logging audit event: %s", str(e))
            # Don't raise here as it's auxiliary functionality


class BlueprintTemplateRepository:
    """Repository for Blueprint Template operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def list_public_templates(
        self,
        category: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        complexity_level: Optional[str] = None
    ) -> List[BlueprintTemplate]:
        """List public blueprint templates"""
        try:
            query = select(BlueprintTemplate).where(
                BlueprintTemplate.is_public.is_(True)
            )
            
            if category:
                query = query.where(BlueprintTemplate.category == category)
            
            if cloud_provider:
                query = query.where(
                    BlueprintTemplate.cloud_providers.contains(
                        [cloud_provider]
                    )
                )
            
            if complexity_level:
                query = query.where(
                    BlueprintTemplate.complexity_level == complexity_level
                )
            
            query = query.order_by(BlueprintTemplate.average_rating.desc())
            
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Error listing templates: %s", str(e))
            raise


class BlueprintDeploymentRepository:
    """Repository for Blueprint Deployment operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_deployment(
        self,
        deployment_data: Dict[str, Any]
    ) -> BlueprintDeployment:
        """Create a new deployment record"""
        try:
            deployment = BlueprintDeployment(**deployment_data)
            self.session.add(deployment)
            await self.session.flush()
            
            logger.info("Deployment created: %s", deployment.id)
            return deployment
            
        except Exception as e:
            logger.error("Error creating deployment: %s", str(e))
            raise
    
    async def get_deployments_for_blueprint(
        self,
        blueprint_id: str
    ) -> List[BlueprintDeployment]:
        """Get all deployments for a blueprint"""
        try:
            result = await self.session.execute(
                select(BlueprintDeployment)
                .where(BlueprintDeployment.blueprint_id == blueprint_id)
                .order_by(BlueprintDeployment.started_at.desc())
            )
            return result.scalars().all()
            
        except Exception as e:
            logger.error(
                "Error getting deployments for blueprint %s: %s",
                blueprint_id, str(e)
            )
            raise


# Repository factory functions
async def get_blueprint_repository() -> BlueprintRepository:
    """Get blueprint repository with database session"""
    async with get_db_session() as session:
        return BlueprintRepository(session)


async def get_template_repository() -> BlueprintTemplateRepository:
    """Get template repository with database session"""
    async with get_db_session() as session:
        return BlueprintTemplateRepository(session)


async def get_deployment_repository() -> BlueprintDeploymentRepository:
    """Get deployment repository with database session"""
    async with get_db_session() as session:
        return BlueprintDeploymentRepository(session)

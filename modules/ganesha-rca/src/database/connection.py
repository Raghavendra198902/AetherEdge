"""
Ganesha RCA Engine - Database Connection
Sacred problem resolution data persistence
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from ..config import config

logger = logging.getLogger(__name__)


class RCADatabase:
    """RCA database operations manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to the RCA database"""
        try:
            connection_string = (
                f"mongodb://{config.MONGODB_USER}:{config.MONGODB_PASSWORD}@"
                f"{config.MONGODB_HOST}:{config.MONGODB_PORT}/"
                f"{config.MONGODB_DATABASE}"
            )
            
            self.client = AsyncIOMotorClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=5,
                maxIdleTimeMS=30000
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.database = self.client[config.MONGODB_DATABASE]
            self.connected = True
            
            # Create indexes for RCA collections
            await self._create_indexes()
            
            logger.info("Ganesha RCA Database connected successfully")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to RCA database: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to database: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the database"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("Ganesha RCA Database disconnected")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Incidents indexes
            await self.database.incidents.create_index([
                ("severity", 1), ("status", 1)
            ])
            await self.database.incidents.create_index([
                ("created_at", -1), ("severity", 1)
            ])
            await self.database.incidents.create_index([
                ("affected_services", 1), ("status", 1)
            ])
            
            # RCA analyses indexes
            await self.database.rca_analyses.create_index([
                ("incident_id", 1), ("status", 1)
            ])
            await self.database.rca_analyses.create_index([
                ("created_at", -1), ("status", 1)
            ])
            
            # Knowledge base indexes
            await self.database.knowledge_base.create_index([
                ("problem_type", 1), ("symptoms", 1)
            ])
            await self.database.knowledge_base.create_index([
                ("tags", 1), ("confidence_score", -1)
            ])
            
            # Remediation actions indexes
            await self.database.remediation_actions.create_index([
                ("incident_id", 1), ("status", 1)
            ])
            await self.database.remediation_actions.create_index([
                ("action_type", 1), ("status", 1)
            ])
            
            logger.info("RCA database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")
    
    async def store_incident(self, incident_data: Dict[str, Any]) -> str:
        """Store an incident"""
        try:
            incident_data["_id"] = incident_data.get("id")
            incident_data["created_at"] = datetime.now()
            incident_data["updated_at"] = datetime.now()
            
            result = await self.database.incidents.insert_one(incident_data)
            logger.info(f"Incident stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing incident: {e}")
            raise
    
    async def get_incidents(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve incidents with filtering"""
        try:
            query = filters or {}
            cursor = self.database.incidents.find(query)
            cursor = cursor.sort("created_at", -1).skip(skip).limit(limit)
            
            incidents = []
            async for incident in cursor:
                incidents.append(incident)
            
            return incidents
            
        except Exception as e:
            logger.error(f"Error retrieving incidents: {e}")
            raise
    
    async def update_incident_status(
        self, 
        incident_id: str, 
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update incident status"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now()
            }
            
            if metadata:
                update_data.update(metadata)
            
            result = await self.database.incidents.update_one(
                {"_id": incident_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating incident status: {e}")
            raise
    
    async def store_rca_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Store an RCA analysis"""
        try:
            analysis_data["_id"] = analysis_data.get("id")
            analysis_data["created_at"] = datetime.now()
            analysis_data["updated_at"] = datetime.now()
            
            result = await self.database.rca_analyses.insert_one(analysis_data)
            logger.info(f"RCA analysis stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing RCA analysis: {e}")
            raise
    
    async def get_rca_analyses(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve RCA analyses with filtering"""
        try:
            query = filters or {}
            cursor = self.database.rca_analyses.find(query)
            cursor = cursor.sort("created_at", -1).skip(skip).limit(limit)
            
            analyses = []
            async for analysis in cursor:
                analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error retrieving RCA analyses: {e}")
            raise
    
    async def store_knowledge_entry(self, knowledge_data: Dict[str, Any]) -> str:
        """Store a knowledge base entry"""
        try:
            knowledge_data["_id"] = knowledge_data.get("id")
            knowledge_data["created_at"] = datetime.now()
            knowledge_data["updated_at"] = datetime.now()
            
            result = await self.database.knowledge_base.insert_one(knowledge_data)
            logger.info(f"Knowledge entry stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing knowledge entry: {e}")
            raise
    
    async def search_knowledge_base(
        self, 
        symptoms: List[str],
        problem_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search knowledge base for similar problems"""
        try:
            query = {"symptoms": {"$in": symptoms}}
            
            if problem_type:
                query["problem_type"] = problem_type
            
            cursor = self.database.knowledge_base.find(query)
            cursor = cursor.sort("confidence_score", -1).limit(10)
            
            entries = []
            async for entry in cursor:
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            raise
    
    async def get_rca_metrics(self, timeframe_hours: int = 24) -> Dict[str, Any]:
        """Get RCA metrics for dashboard"""
        try:
            since = datetime.now() - timedelta(hours=timeframe_hours)
            
            # Incidents by severity
            incidents_pipeline = [
                {"$match": {"created_at": {"$gte": since}}},
                {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
            ]
            incidents_by_severity = {}
            async for result in self.database.incidents.aggregate(
                incidents_pipeline
            ):
                incidents_by_severity[result["_id"]] = result["count"]
            
            # Incidents by status
            status_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            incidents_by_status = {}
            async for result in self.database.incidents.aggregate(status_pipeline):
                incidents_by_status[result["_id"]] = result["count"]
            
            # Resolution time analysis
            resolved_pipeline = [
                {
                    "$match": {
                        "status": "resolved",
                        "resolved_at": {"$exists": True},
                        "created_at": {"$gte": since}
                    }
                },
                {
                    "$project": {
                        "resolution_time": {
                            "$subtract": ["$resolved_at", "$created_at"]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "avg_resolution_time": {"$avg": "$resolution_time"},
                        "total_resolved": {"$sum": 1}
                    }
                }
            ]
            
            resolution_stats = {"avg_resolution_time": 0, "total_resolved": 0}
            async for result in self.database.incidents.aggregate(
                resolved_pipeline
            ):
                if result["_id"] is None:
                    resolution_stats = {
                        "avg_resolution_time": result["avg_resolution_time"] / 
                                            (1000 * 60),  # Convert to minutes
                        "total_resolved": result["total_resolved"]
                    }
            
            # Total counts
            total_incidents = await self.database.incidents.count_documents({})
            total_analyses = await self.database.rca_analyses.count_documents({})
            
            return {
                "incidents_by_severity": incidents_by_severity,
                "incidents_by_status": incidents_by_status,
                "resolution_stats": resolution_stats,
                "total_incidents": total_incidents,
                "total_analyses": total_analyses,
                "timeframe_hours": timeframe_hours,
                "generated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating RCA metrics: {e}")
            raise


# Global database instance
rca_db = RCADatabase()

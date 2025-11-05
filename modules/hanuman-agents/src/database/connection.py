"""
Hanuman Agents Engine - Database Connection
Sacred agent and task management data persistence
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from ..config import config

logger = logging.getLogger(__name__)


class AgentsDatabase:
    """Agents database operations manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to the agents database"""
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
            
            # Create indexes for agents collections
            await self._create_indexes()
            
            logger.info("Hanuman Agents Database connected successfully")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to agents database: {e}")
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
            logger.info("Hanuman Agents Database disconnected")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Agents indexes
            await self.database.agents.create_index([
                ("status", 1), ("agent_type", 1)
            ])
            await self.database.agents.create_index([
                ("last_heartbeat", -1), ("status", 1)
            ])
            await self.database.agents.create_index([
                ("capabilities", 1), ("status", 1)
            ])
            
            # Tasks indexes
            await self.database.tasks.create_index([
                ("status", 1), ("priority", 1)
            ])
            await self.database.tasks.create_index([
                ("agent_id", 1), ("status", 1)
            ])
            await self.database.tasks.create_index([
                ("created_at", -1), ("priority", 1)
            ])
            await self.database.tasks.create_index([
                ("task_type", 1), ("status", 1)
            ])
            
            # Workflows indexes
            await self.database.workflows.create_index([
                ("status", 1), ("priority", 1)
            ])
            await self.database.workflows.create_index([
                ("created_at", -1), ("status", 1)
            ])
            
            # Agent groups indexes
            await self.database.agent_groups.create_index([
                ("group_type", 1), ("enabled", 1)
            ])
            
            logger.info("Agents database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")
    
    async def store_agent(self, agent_data: Dict[str, Any]) -> str:
        """Store an agent"""
        try:
            agent_data["_id"] = agent_data.get("id")
            agent_data["created_at"] = datetime.now()
            agent_data["last_heartbeat"] = datetime.now()
            
            result = await self.database.agents.insert_one(agent_data)
            logger.info(f"Agent stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing agent: {e}")
            raise
    
    async def get_agents(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve agents with filtering"""
        try:
            query = filters or {}
            cursor = self.database.agents.find(query)
            cursor = cursor.sort("last_heartbeat", -1).skip(skip).limit(limit)
            
            agents = []
            async for agent in cursor:
                agents.append(agent)
            
            return agents
            
        except Exception as e:
            logger.error(f"Error retrieving agents: {e}")
            raise
    
    async def update_agent_status(
        self, 
        agent_id: str, 
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update agent status and heartbeat"""
        try:
            update_data = {
                "status": status,
                "last_heartbeat": datetime.now(),
                "updated_at": datetime.now()
            }
            
            if metadata:
                update_data.update(metadata)
            
            result = await self.database.agents.update_one(
                {"_id": agent_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating agent status: {e}")
            raise
    
    async def store_task(self, task_data: Dict[str, Any]) -> str:
        """Store a task"""
        try:
            task_data["_id"] = task_data.get("id")
            task_data["created_at"] = datetime.now()
            task_data["updated_at"] = datetime.now()
            
            result = await self.database.tasks.insert_one(task_data)
            logger.info(f"Task stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing task: {e}")
            raise
    
    async def get_tasks(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve tasks with filtering"""
        try:
            query = filters or {}
            cursor = self.database.tasks.find(query)
            cursor = cursor.sort("created_at", -1).skip(skip).limit(limit)
            
            tasks = []
            async for task in cursor:
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error retrieving tasks: {e}")
            raise
    
    async def update_task_status(
        self, 
        task_id: str, 
        status: str,
        result_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update task status and result"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now()
            }
            
            if result_data:
                update_data["result"] = result_data
            
            if status in ["completed", "failed"]:
                update_data["finished_at"] = datetime.now()
            
            result = await self.database.tasks.update_one(
                {"_id": task_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            raise
    
    async def get_available_agents(
        self, 
        capabilities: Optional[List[str]] = None,
        agent_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get available agents for task assignment"""
        try:
            query = {"status": {"$in": ["active", "idle"]}}
            
            if capabilities:
                query["capabilities"] = {"$in": capabilities}
            
            if agent_type:
                query["agent_type"] = agent_type
            
            cursor = self.database.agents.find(query)
            cursor = cursor.sort("last_heartbeat", -1)
            
            agents = []
            async for agent in cursor:
                agents.append(agent)
            
            return agents
            
        except Exception as e:
            logger.error(f"Error getting available agents: {e}")
            raise
    
    async def get_agent_metrics(self, timeframe_hours: int = 24) -> Dict[str, Any]:
        """Get agent metrics for dashboard"""
        try:
            since = datetime.now() - timedelta(hours=timeframe_hours)
            
            # Agent status distribution
            status_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            agents_by_status = {}
            async for result in self.database.agents.aggregate(status_pipeline):
                agents_by_status[result["_id"]] = result["count"]
            
            # Task status distribution
            task_pipeline = [
                {"$match": {"created_at": {"$gte": since}}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            tasks_by_status = {}
            async for result in self.database.tasks.aggregate(task_pipeline):
                tasks_by_status[result["_id"]] = result["count"]
            
            # Agent type distribution
            type_pipeline = [
                {"$group": {"_id": "$agent_type", "count": {"$sum": 1}}}
            ]
            agents_by_type = {}
            async for result in self.database.agents.aggregate(type_pipeline):
                agents_by_type[result["_id"]] = result["count"]
            
            # Total counts
            total_agents = await self.database.agents.count_documents({})
            active_agents = await self.database.agents.count_documents(
                {"status": {"$in": ["active", "idle"]}}
            )
            
            return {
                "agents_by_status": agents_by_status,
                "tasks_by_status": tasks_by_status,
                "agents_by_type": agents_by_type,
                "total_agents": total_agents,
                "active_agents": active_agents,
                "agent_utilization": (active_agents / total_agents * 100) if total_agents > 0 else 0,
                "timeframe_hours": timeframe_hours,
                "generated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating agent metrics: {e}")
            raise


# Global database instance
agents_db = AgentsDatabase()

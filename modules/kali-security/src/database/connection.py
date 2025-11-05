"""
Kali Security Engine - Database Connection
Sacred security data persistence and management
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from ..config import config

logger = logging.getLogger(__name__)


class SecurityDatabase:
    """Security database operations manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to the security database"""
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
            
            # Create indexes for security collections
            await self._create_indexes()
            
            logger.info("Kali Security Database connected successfully")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to security database: {e}")
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
            logger.info("Kali Security Database disconnected")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Security events indexes
            await self.database.security_events.create_index([
                ("timestamp", -1), ("threat_level", 1)
            ])
            await self.database.security_events.create_index([
                ("event_type", 1), ("source_ip", 1)
            ])
            await self.database.security_events.create_index([
                ("status", 1), ("threat_level", 1)
            ])
            
            # Vulnerabilities indexes
            await self.database.vulnerabilities.create_index([
                ("severity", 1), ("status", 1)
            ])
            await self.database.vulnerabilities.create_index([
                ("resource_id", 1), ("vulnerability_type", 1)
            ])
            await self.database.vulnerabilities.create_index([
                ("discovered_at", -1), ("severity", 1)
            ])
            
            # Security policies indexes
            await self.database.security_policies.create_index([
                ("policy_type", 1), ("enabled", 1)
            ])
            await self.database.security_policies.create_index([
                ("framework", 1), ("severity", 1)
            ])
            
            # Compliance reports indexes
            await self.database.compliance_reports.create_index([
                ("framework", 1), ("generated_at", -1)
            ])
            await self.database.compliance_reports.create_index([
                ("compliance_score", 1), ("status", 1)
            ])
            
            # Threat intelligence indexes
            await self.database.threat_intelligence.create_index([
                ("threat_type", 1), ("confidence", 1)
            ])
            await self.database.threat_intelligence.create_index([
                ("ioc_value", 1), ("ioc_type", 1)
            ])
            
            logger.info("Security database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")
    
    async def store_security_event(self, event_data: Dict[str, Any]) -> str:
        """Store a security event"""
        try:
            event_data["_id"] = event_data.get("id")
            event_data["created_at"] = datetime.now()
            
            result = await self.database.security_events.insert_one(event_data)
            logger.info(f"Security event stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing security event: {e}")
            raise
    
    async def get_security_events(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve security events with filtering"""
        try:
            query = filters or {}
            cursor = self.database.security_events.find(query)
            cursor = cursor.sort("timestamp", -1).skip(skip).limit(limit)
            
            events = []
            async for event in cursor:
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving security events: {e}")
            raise
    
    async def store_vulnerability(self, vulnerability_data: Dict[str, Any]) -> str:
        """Store a vulnerability"""
        try:
            vulnerability_data["_id"] = vulnerability_data.get("id")
            vulnerability_data["created_at"] = datetime.now()
            
            result = await self.database.vulnerabilities.insert_one(vulnerability_data)
            logger.info(f"Vulnerability stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing vulnerability: {e}")
            raise
    
    async def get_vulnerabilities(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve vulnerabilities with filtering"""
        try:
            query = filters or {}
            cursor = self.database.vulnerabilities.find(query)
            cursor = cursor.sort("severity", -1).skip(skip).limit(limit)
            
            vulnerabilities = []
            async for vuln in cursor:
                vulnerabilities.append(vuln)
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"Error retrieving vulnerabilities: {e}")
            raise
    
    async def store_security_policy(self, policy_data: Dict[str, Any]) -> str:
        """Store a security policy"""
        try:
            policy_data["_id"] = policy_data.get("id")
            policy_data["created_at"] = datetime.now()
            
            result = await self.database.security_policies.insert_one(policy_data)
            logger.info(f"Security policy stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing security policy: {e}")
            raise
    
    async def get_security_policies(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve security policies with filtering"""
        try:
            query = filters or {}
            cursor = self.database.security_policies.find(query)
            cursor = cursor.sort("created_at", -1).skip(skip).limit(limit)
            
            policies = []
            async for policy in cursor:
                policies.append(policy)
            
            return policies
            
        except Exception as e:
            logger.error(f"Error retrieving security policies: {e}")
            raise
    
    async def store_compliance_report(self, report_data: Dict[str, Any]) -> str:
        """Store a compliance report"""
        try:
            report_data["_id"] = report_data.get("id")
            report_data["created_at"] = datetime.now()
            
            result = await self.database.compliance_reports.insert_one(report_data)
            logger.info(f"Compliance report stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing compliance report: {e}")
            raise
    
    async def get_security_metrics(self, timeframe_hours: int = 24) -> Dict[str, Any]:
        """Get security metrics for dashboard"""
        try:
            since = datetime.now() - timedelta(hours=timeframe_hours)
            
            # Security events by severity
            events_pipeline = [
                {"$match": {"timestamp": {"$gte": since}}},
                {"$group": {"_id": "$threat_level", "count": {"$sum": 1}}}
            ]
            events_by_severity = {}
            async for result in self.database.security_events.aggregate(events_pipeline):
                events_by_severity[result["_id"]] = result["count"]
            
            # Vulnerability counts by status
            vuln_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            vulns_by_status = {}
            async for result in self.database.vulnerabilities.aggregate(vuln_pipeline):
                vulns_by_status[result["_id"]] = result["count"]
            
            # Policy compliance rate
            total_policies = await self.database.security_policies.count_documents({})
            enabled_policies = await self.database.security_policies.count_documents({"enabled": True})
            
            return {
                "events_by_severity": events_by_severity,
                "vulnerabilities_by_status": vulns_by_status,
                "total_policies": total_policies,
                "enabled_policies": enabled_policies,
                "policy_compliance_rate": (enabled_policies / total_policies * 100) if total_policies > 0 else 0,
                "timeframe_hours": timeframe_hours,
                "generated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating security metrics: {e}")
            raise


# Global database instance
security_db = SecurityDatabase()

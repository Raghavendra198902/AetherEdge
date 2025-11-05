"""
🔥 Shiva Healing Engine
======================

Automated healing and remediation engine.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import uuid

from ..models.healing import HealingAction, HealingStatus, HealingStrategy

logger = logging.getLogger(__name__)


@dataclass
class HealingResult:
    """Healing execution result"""
    success: bool
    actions_taken: List[str]
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    execution_time: float
    rollback_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class HealingEngine:
    """
    Divine healing engine for automated remediation
    """

    def __init__(self):
        self.healing_strategies = {}
        self.active_healings = {}
        self.rollback_cache = {}
        self._initialize_strategies()

    async def trigger_healing(self, resource_id: str, issue_type: str,
                            strategy: str = "conservative",
                            auto_approve: bool = False,
                            rollback_enabled: bool = True,
                            triggered_by: str = "system") -> str:
        """
        Trigger healing action for a resource
        """
        try:
            healing_id = str(uuid.uuid4())
            
            logger.info(f"Triggering healing {healing_id} for {resource_id}")
            
            # Create healing action record
            healing_action = HealingAction(
                id=healing_id,
                resource_id=resource_id,
                resource_type=await self._detect_resource_type(resource_id),
                issue_type=issue_type,
                healing_strategy=strategy,
                status=HealingStatus.PENDING,
                auto_approved=auto_approve,
                rollback_enabled=rollback_enabled,
                triggered_by=triggered_by
            )
            
            await healing_action.save()
            
            # Execute healing if auto-approved
            if auto_approve:
                await self._execute_healing_async(healing_id)
            else:
                logger.info(f"Healing {healing_id} pending manual approval")
            
            return healing_id
            
        except Exception as e:
            logger.error(f"Error triggering healing: {str(e)}")
            raise

    async def execute_healing(self, healing_id: str) -> HealingResult:
        """
        Execute healing action
        """
        try:
            logger.info(f"Executing healing {healing_id}")
            
            # Get healing action
            healing_action = await HealingAction.get(healing_id)
            if not healing_action:
                raise ValueError(f"Healing action {healing_id} not found")
            
            # Update status
            healing_action.status = HealingStatus.RUNNING
            healing_action.started_at = datetime.now(timezone.utc)
            await healing_action.save()
            
            # Capture metrics before healing
            metrics_before = await self._capture_metrics(healing_action.resource_id)
            
            # Execute healing strategy
            result = await self._execute_strategy(healing_action)
            
            # Capture metrics after healing
            metrics_after = await self._capture_metrics(healing_action.resource_id)
            
            # Update healing action with results
            healing_action.completed_at = datetime.now(timezone.utc)
            healing_action.execution_duration = (
                healing_action.completed_at - healing_action.started_at
            ).total_seconds()
            healing_action.actions_taken = result.actions_taken
            healing_action.metrics_before = metrics_before
            healing_action.metrics_after = metrics_after
            healing_action.rollback_data = result.rollback_data
            
            if result.success:
                healing_action.status = HealingStatus.COMPLETED
                healing_action.success_rate = self._calculate_success_rate(
                    metrics_before, metrics_after, healing_action.issue_type
                )
            else:
                healing_action.status = HealingStatus.FAILED
                
            await healing_action.save()
            
            # Store in active healings for monitoring
            self.active_healings[healing_id] = healing_action
            
            logger.info(f"Healing {healing_id} completed with status: {healing_action.status}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing healing {healing_id}: {str(e)}")
            # Update status to failed
            try:
                healing_action = await HealingAction.get(healing_id)
                if healing_action:
                    healing_action.status = HealingStatus.FAILED
                    healing_action.completed_at = datetime.now(timezone.utc)
                    await healing_action.save()
            except:
                pass
            
            return HealingResult(
                success=False,
                actions_taken=[],
                metrics_before={},
                metrics_after={},
                execution_time=0.0,
                error_message=str(e)
            )

    async def rollback_healing(self, healing_id: str) -> bool:
        """
        Rollback a healing action
        """
        try:
            logger.info(f"Rolling back healing {healing_id}")
            
            healing_action = await HealingAction.get(healing_id)
            if not healing_action:
                raise ValueError(f"Healing action {healing_id} not found")
            
            if not healing_action.rollback_enabled:
                raise ValueError("Rollback not enabled for this healing action")
            
            if not healing_action.rollback_data:
                raise ValueError("No rollback data available")
            
            # Execute rollback steps
            rollback_success = await self._execute_rollback(
                healing_action.resource_id,
                healing_action.rollback_data
            )
            
            if rollback_success:
                healing_action.status = HealingStatus.ROLLED_BACK
                await healing_action.save()
                logger.info(f"Healing {healing_id} rolled back successfully")
            
            return rollback_success
            
        except Exception as e:
            logger.error(f"Error rolling back healing {healing_id}: {str(e)}")
            return False

    async def get_healing_status(self, healing_id: str) -> Optional[Dict[str, Any]]:
        """
        Get healing action status and details
        """
        try:
            healing_action = await HealingAction.get(healing_id)
            if not healing_action:
                return None
            
            return {
                "healing_id": healing_action.id,
                "resource_id": healing_action.resource_id,
                "issue_type": healing_action.issue_type,
                "status": healing_action.status,
                "strategy": healing_action.healing_strategy,
                "progress": self._calculate_progress(healing_action),
                "started_at": healing_action.started_at,
                "completed_at": healing_action.completed_at,
                "execution_duration": healing_action.execution_duration,
                "success_rate": healing_action.success_rate,
                "actions_taken": healing_action.actions_taken,
                "rollback_enabled": healing_action.rollback_enabled
            }
            
        except Exception as e:
            logger.error(f"Error getting healing status: {str(e)}")
            return None

    async def _execute_healing_async(self, healing_id: str):
        """
        Execute healing in background
        """
        asyncio.create_task(self.execute_healing(healing_id))

    async def _execute_strategy(self, healing_action: HealingAction) -> HealingResult:
        """
        Execute healing strategy based on issue type and strategy
        """
        strategy_key = f"{healing_action.issue_type}_{healing_action.healing_strategy}"
        
        if strategy_key not in self.healing_strategies:
            # Fallback to generic strategy
            strategy_key = f"generic_{healing_action.healing_strategy}"
        
        if strategy_key not in self.healing_strategies:
            raise ValueError(f"No strategy found for {strategy_key}")
        
        strategy = self.healing_strategies[strategy_key]
        
        start_time = datetime.now(timezone.utc)
        actions_taken = []
        rollback_data = {}
        
        try:
            # Execute healing steps
            for step in strategy["steps"]:
                action_result = await self._execute_healing_step(
                    healing_action.resource_id,
                    step,
                    healing_action.healing_strategy
                )
                actions_taken.append(action_result["action"])
                
                if "rollback_info" in action_result:
                    rollback_data[step["name"]] = action_result["rollback_info"]
                
                # Wait between steps if specified
                if "wait_seconds" in step:
                    await asyncio.sleep(step["wait_seconds"])
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return HealingResult(
                success=True,
                actions_taken=actions_taken,
                metrics_before={},  # Will be filled by caller
                metrics_after={},   # Will be filled by caller
                execution_time=execution_time,
                rollback_data=rollback_data
            )
            
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            return HealingResult(
                success=False,
                actions_taken=actions_taken,
                metrics_before={},
                metrics_after={},
                execution_time=execution_time,
                rollback_data=rollback_data,
                error_message=str(e)
            )

    async def _execute_healing_step(self, resource_id: str, step: Dict[str, Any],
                                  strategy: str) -> Dict[str, Any]:
        """
        Execute individual healing step
        """
        step_type = step["type"]
        parameters = step.get("parameters", {})
        
        logger.info(f"Executing healing step: {step_type} for {resource_id}")
        
        if step_type == "restart_service":
            return await self._restart_service(resource_id, parameters)
        elif step_type == "scale_resources":
            return await self._scale_resources(resource_id, parameters)
        elif step_type == "clear_cache":
            return await self._clear_cache(resource_id, parameters)
        elif step_type == "update_configuration":
            return await self._update_configuration(resource_id, parameters)
        elif step_type == "restart_application":
            return await self._restart_application(resource_id, parameters)
        elif step_type == "run_health_check":
            return await self._run_health_check(resource_id, parameters)
        else:
            raise ValueError(f"Unknown healing step type: {step_type}")

    async def _restart_service(self, resource_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Restart service healing action"""
        await asyncio.sleep(1)  # Simulate restart
        return {
            "action": f"Restarted service for {resource_id}",
            "rollback_info": {"action": "restart", "timestamp": datetime.now(timezone.utc).isoformat()}
        }

    async def _scale_resources(self, resource_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Scale resources healing action"""
        scale_factor = parameters.get("scale_factor", 1.5)
        await asyncio.sleep(2)  # Simulate scaling
        return {
            "action": f"Scaled {resource_id} by factor {scale_factor}",
            "rollback_info": {"original_capacity": "current", "action": "scale"}
        }

    async def _clear_cache(self, resource_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Clear cache healing action"""
        cache_type = parameters.get("cache_type", "all")
        await asyncio.sleep(0.5)
        return {
            "action": f"Cleared {cache_type} cache for {resource_id}",
            "rollback_info": {"cache_backup": "saved"}
        }

    async def _update_configuration(self, resource_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration healing action"""
        config_changes = parameters.get("changes", {})
        await asyncio.sleep(1)
        return {
            "action": f"Updated configuration for {resource_id}: {config_changes}",
            "rollback_info": {"previous_config": "backed_up"}
        }

    async def _restart_application(self, resource_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Restart application healing action"""
        await asyncio.sleep(3)  # Simulate app restart
        return {
            "action": f"Restarted application on {resource_id}",
            "rollback_info": {"action": "restart_app"}
        }

    async def _run_health_check(self, resource_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run health check healing action"""
        await asyncio.sleep(0.5)
        return {
            "action": f"Ran health check for {resource_id}",
            "rollback_info": None
        }

    async def _execute_rollback(self, resource_id: str, rollback_data: Dict[str, Any]) -> bool:
        """Execute rollback steps"""
        try:
            for step_name, rollback_info in rollback_data.items():
                logger.info(f"Rolling back step {step_name} for {resource_id}")
                await asyncio.sleep(1)  # Simulate rollback
            return True
        except Exception as e:
            logger.error(f"Error in rollback: {str(e)}")
            return False

    async def _capture_metrics(self, resource_id: str) -> Dict[str, float]:
        """Capture resource metrics"""
        # Mock implementation
        await asyncio.sleep(0.2)
        import random
        return {
            "cpu_usage": random.uniform(20, 80),
            "memory_usage": random.uniform(30, 90),
            "response_time": random.uniform(100, 500),
            "error_rate": random.uniform(0, 5)
        }

    async def _detect_resource_type(self, resource_id: str) -> str:
        """Detect resource type from ID"""
        if resource_id.startswith("i-"):
            return "ec2_instance"
        elif resource_id.startswith("pod-"):
            return "kubernetes_pod"
        elif resource_id.startswith("app-"):
            return "application"
        else:
            return "unknown"

    def _calculate_success_rate(self, metrics_before: Dict[str, float],
                              metrics_after: Dict[str, float], issue_type: str) -> float:
        """Calculate healing success rate"""
        # Simple success calculation - would be more sophisticated in production
        if issue_type == "high_cpu":
            cpu_before = metrics_before.get("cpu_usage", 100)
            cpu_after = metrics_after.get("cpu_usage", 100)
            improvement = max(0, cpu_before - cpu_after) / cpu_before
            return min(improvement * 100, 100.0)
        
        # Default success rate
        return 85.0

    def _calculate_progress(self, healing_action: HealingAction) -> float:
        """Calculate healing progress percentage"""
        if healing_action.status == HealingStatus.COMPLETED:
            return 100.0
        elif healing_action.status == HealingStatus.FAILED:
            return 0.0
        elif healing_action.status == HealingStatus.RUNNING:
            return 50.0  # Estimated progress
        else:
            return 0.0

    def _initialize_strategies(self):
        """Initialize healing strategies"""
        self.healing_strategies = {
            "high_cpu_conservative": {
                "steps": [
                    {"type": "run_health_check", "name": "initial_check"},
                    {"type": "clear_cache", "name": "clear_cache", "parameters": {"cache_type": "memory"}},
                    {"type": "run_health_check", "name": "post_cache_check", "wait_seconds": 30}
                ]
            },
            "high_cpu_aggressive": {
                "steps": [
                    {"type": "restart_service", "name": "restart"},
                    {"type": "scale_resources", "name": "scale", "parameters": {"scale_factor": 2.0}},
                    {"type": "run_health_check", "name": "final_check", "wait_seconds": 60}
                ]
            },
            "high_memory_conservative": {
                "steps": [
                    {"type": "clear_cache", "name": "clear_cache"},
                    {"type": "run_health_check", "name": "check", "wait_seconds": 30}
                ]
            },
            "application_error_conservative": {
                "steps": [
                    {"type": "run_health_check", "name": "check"},
                    {"type": "restart_application", "name": "restart_app"},
                    {"type": "run_health_check", "name": "final_check", "wait_seconds": 60}
                ]
            }
        }

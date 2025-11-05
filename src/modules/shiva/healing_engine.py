"""
AetherEdge - Shiva Module: AI Healing Engine
The Transformer - Performs adaptive correction, auto-scaling, and optimization

This module embodies the cosmic principle of Shiva (Transformer) in digital form,
performing intelligent healing, anomaly detection, and system transformation.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import statistics
import random

# Setup logging
logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies detected"""
    PERFORMANCE = "performance"
    CAPACITY = "capacity"
    SECURITY = "security"
    AVAILABILITY = "availability"
    COST = "cost"
    CONFIGURATION = "configuration"


class HealingAction(Enum):
    """Types of healing actions"""
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    FAILOVER = "failover"
    RESET_CONFIG = "reset_config"
    PATCH_SYSTEM = "patch_system"
    CLEAN_LOGS = "clean_logs"
    OPTIMIZE_RESOURCES = "optimize_resources"


class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HealingStatus(Enum):
    """Healing action status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class MetricData:
    """Time-series metric data point"""
    timestamp: datetime
    value: float
    metric_name: str
    resource_id: str
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Anomaly:
    """Detected anomaly"""
    anomaly_id: str
    anomaly_type: AnomalyType
    resource_id: str
    metric_name: str
    detected_at: datetime
    confidence_score: float
    description: str
    baseline_value: float
    actual_value: float
    deviation_percentage: float
    severity: IncidentSeverity
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealingPlan:
    """Automated healing plan"""
    plan_id: str
    anomaly_id: str
    recommended_actions: List[HealingAction]
    estimated_success_rate: float
    estimated_duration_minutes: int
    risk_level: str  # low, medium, high
    prerequisites: List[str] = field(default_factory=list)
    rollback_plan: List[str] = field(default_factory=list)


@dataclass
class HealingExecution:
    """Healing action execution record"""
    execution_id: str
    plan_id: str
    action: HealingAction
    status: HealingStatus
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    rollback_executed: bool = False
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)


class AnomalyDetectionEngine:
    """AI-powered anomaly detection"""
    
    def __init__(self):
        self.metric_history: Dict[str, List[MetricData]] = {}
        self.baselines: Dict[str, Dict[str, float]] = {}
        self.detection_rules = self._load_detection_rules()
        logger.info("Anomaly Detection Engine initialized")
    
    def _load_detection_rules(self) -> Dict[str, Any]:
        """Load anomaly detection rules and thresholds"""
        return {
            "cpu_utilization": {
                "threshold_high": 90.0,
                "threshold_critical": 95.0,
                "window_minutes": 5,
                "sensitivity": 2.0  # Standard deviations
            },
            "memory_utilization": {
                "threshold_high": 85.0,
                "threshold_critical": 95.0,
                "window_minutes": 5,
                "sensitivity": 2.0
            },
            "disk_utilization": {
                "threshold_high": 80.0,
                "threshold_critical": 90.0,
                "window_minutes": 10,
                "sensitivity": 1.5
            },
            "response_time": {
                "threshold_high": 2000.0,  # ms
                "threshold_critical": 5000.0,
                "window_minutes": 3,
                "sensitivity": 2.5
            },
            "error_rate": {
                "threshold_high": 5.0,  # percentage
                "threshold_critical": 10.0,
                "window_minutes": 5,
                "sensitivity": 2.0
            }
        }
    
    def ingest_metric(self, metric: MetricData):
        """Ingest new metric data point"""
        key = f"{metric.resource_id}:{metric.metric_name}"
        
        if key not in self.metric_history:
            self.metric_history[key] = []
        
        self.metric_history[key].append(metric)
        
        # Keep only last 24 hours of data
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metric_history[key] = [
            m for m in self.metric_history[key] 
            if m.timestamp > cutoff_time
        ]
        
        # Update baseline if enough data
        self._update_baseline(key)
    
    def _update_baseline(self, metric_key: str):
        """Update baseline statistics for metric"""
        metrics = self.metric_history.get(metric_key, [])
        
        if len(metrics) < 10:  # Need minimum data points
            return
        
        # Calculate baseline over last 7 days or available data
        baseline_window = datetime.now() - timedelta(days=7)
        baseline_metrics = [
            m for m in metrics 
            if m.timestamp > baseline_window
        ]
        
        if not baseline_metrics:
            return
        
        values = [m.value for m in baseline_metrics]
        
        self.baselines[metric_key] = {
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99),
            "last_updated": datetime.now()
        }
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * percentile / 100
        f = int(k)
        c = int(k) + 1
        
        if f == c:
            return sorted_values[f]
        
        return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)
    
    def detect_anomalies(self, metric: MetricData) -> List[Anomaly]:
        """Detect anomalies in real-time"""
        anomalies = []
        key = f"{metric.resource_id}:{metric.metric_name}"
        
        # Rule-based detection
        rule_anomaly = self._detect_rule_based_anomaly(metric)
        if rule_anomaly:
            anomalies.append(rule_anomaly)
        
        # Statistical detection
        stat_anomaly = self._detect_statistical_anomaly(metric, key)
        if stat_anomaly:
            anomalies.append(stat_anomaly)
        
        return anomalies
    
    def _detect_rule_based_anomaly(self, metric: MetricData) -> Optional[Anomaly]:
        """Detect anomalies using predefined rules"""
        rules = self.detection_rules.get(metric.metric_name, {})
        if not rules:
            return None
        
        threshold_high = rules.get("threshold_high", float("inf"))
        threshold_critical = rules.get("threshold_critical", float("inf"))
        
        if metric.value >= threshold_critical:
            return Anomaly(
                anomaly_id=f"anom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                anomaly_type=self._get_anomaly_type(metric.metric_name),
                resource_id=metric.resource_id,
                metric_name=metric.metric_name,
                detected_at=metric.timestamp,
                confidence_score=0.95,
                description=f"{metric.metric_name} exceeded critical threshold",
                baseline_value=threshold_critical,
                actual_value=metric.value,
                deviation_percentage=((metric.value - threshold_critical) / threshold_critical) * 100,
                severity=IncidentSeverity.CRITICAL
            )
        elif metric.value >= threshold_high:
            return Anomaly(
                anomaly_id=f"anom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                anomaly_type=self._get_anomaly_type(metric.metric_name),
                resource_id=metric.resource_id,
                metric_name=metric.metric_name,
                detected_at=metric.timestamp,
                confidence_score=0.85,
                description=f"{metric.metric_name} exceeded high threshold",
                baseline_value=threshold_high,
                actual_value=metric.value,
                deviation_percentage=((metric.value - threshold_high) / threshold_high) * 100,
                severity=IncidentSeverity.HIGH
            )
        
        return None
    
    def _detect_statistical_anomaly(
        self, metric: MetricData, key: str
    ) -> Optional[Anomaly]:
        """Detect anomalies using statistical analysis"""
        baseline = self.baselines.get(key)
        if not baseline:
            return None
        
        rules = self.detection_rules.get(metric.metric_name, {})
        sensitivity = rules.get("sensitivity", 2.0)
        
        mean = baseline["mean"]
        std = baseline["std"]
        
        if std == 0:  # No variation in baseline
            return None
        
        # Calculate z-score
        z_score = abs((metric.value - mean) / std)
        
        if z_score > sensitivity:
            severity = IncidentSeverity.HIGH if z_score > 3 else IncidentSeverity.MEDIUM
            
            return Anomaly(
                anomaly_id=f"anom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                anomaly_type=self._get_anomaly_type(metric.metric_name),
                resource_id=metric.resource_id,
                metric_name=metric.metric_name,
                detected_at=metric.timestamp,
                confidence_score=min(0.99, z_score / 4),  # Confidence based on z-score
                description=f"Statistical anomaly detected in {metric.metric_name}",
                baseline_value=mean,
                actual_value=metric.value,
                deviation_percentage=((metric.value - mean) / mean) * 100,
                severity=severity,
                metadata={"z_score": z_score, "baseline_std": std}
            )
        
        return None
    
    def _get_anomaly_type(self, metric_name: str) -> AnomalyType:
        """Determine anomaly type based on metric name"""
        if metric_name in ["cpu_utilization", "memory_utilization", "response_time"]:
            return AnomalyType.PERFORMANCE
        elif metric_name in ["disk_utilization", "network_utilization"]:
            return AnomalyType.CAPACITY
        elif metric_name in ["error_rate", "failed_requests"]:
            return AnomalyType.AVAILABILITY
        else:
            return AnomalyType.PERFORMANCE


class HealingPlanGenerator:
    """Generates automated healing plans"""
    
    def __init__(self):
        self.healing_patterns = self._load_healing_patterns()
        logger.info("Healing Plan Generator initialized")
    
    def _load_healing_patterns(self) -> Dict[str, Any]:
        """Load healing patterns and success rates"""
        return {
            "high_cpu": {
                "actions": [HealingAction.SCALE_UP, HealingAction.RESTART_SERVICE],
                "success_rates": [0.85, 0.70],
                "estimated_duration": [15, 5],
                "risk_levels": ["medium", "low"]
            },
            "high_memory": {
                "actions": [HealingAction.RESTART_SERVICE, HealingAction.CLEAN_LOGS],
                "success_rates": [0.80, 0.60],
                "estimated_duration": [5, 10],
                "risk_levels": ["low", "low"]
            },
            "high_disk": {
                "actions": [HealingAction.CLEAN_LOGS, HealingAction.SCALE_UP],
                "success_rates": [0.75, 0.90],
                "estimated_duration": [10, 20],
                "risk_levels": ["low", "medium"]
            },
            "high_response_time": {
                "actions": [HealingAction.SCALE_UP, HealingAction.OPTIMIZE_RESOURCES],
                "success_rates": [0.85, 0.70],
                "estimated_duration": [15, 30],
                "risk_levels": ["medium", "low"]
            },
            "high_error_rate": {
                "actions": [HealingAction.RESTART_SERVICE, HealingAction.FAILOVER],
                "success_rates": [0.75, 0.95],
                "estimated_duration": [5, 30],
                "risk_levels": ["low", "high"]
            }
        }
    
    def generate_healing_plan(self, anomaly: Anomaly) -> HealingPlan:
        """Generate healing plan for detected anomaly"""
        pattern_key = self._get_pattern_key(anomaly)
        pattern = self.healing_patterns.get(pattern_key, {})
        
        actions = pattern.get("actions", [HealingAction.RESTART_SERVICE])
        success_rates = pattern.get("success_rates", [0.50])
        durations = pattern.get("estimated_duration", [10])
        risk_levels = pattern.get("risk_levels", ["medium"])
        
        # Select best action based on success rate and risk
        best_action_idx = 0
        if len(success_rates) > 1:
            best_action_idx = success_rates.index(max(success_rates))
        
        plan = HealingPlan(
            plan_id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            anomaly_id=anomaly.anomaly_id,
            recommended_actions=actions,
            estimated_success_rate=success_rates[best_action_idx],
            estimated_duration_minutes=durations[best_action_idx],
            risk_level=risk_levels[best_action_idx],
            prerequisites=self._get_prerequisites(actions[best_action_idx]),
            rollback_plan=self._get_rollback_plan(actions[best_action_idx])
        )
        
        logger.info(f"Generated healing plan: {plan.plan_id}")
        return plan
    
    def _get_pattern_key(self, anomaly: Anomaly) -> str:
        """Get pattern key for anomaly"""
        metric_name = anomaly.metric_name.lower()
        
        if "cpu" in metric_name:
            return "high_cpu"
        elif "memory" in metric_name:
            return "high_memory"
        elif "disk" in metric_name:
            return "high_disk"
        elif "response" in metric_name or "latency" in metric_name:
            return "high_response_time"
        elif "error" in metric_name:
            return "high_error_rate"
        else:
            return "high_cpu"  # Default
    
    def _get_prerequisites(self, action: HealingAction) -> List[str]:
        """Get prerequisites for healing action"""
        prerequisites = {
            HealingAction.SCALE_UP: ["Check resource limits", "Verify scaling group"],
            HealingAction.RESTART_SERVICE: ["Backup current state", "Check dependencies"],
            HealingAction.FAILOVER: ["Verify secondary systems", "Check data sync"],
            HealingAction.CLEAN_LOGS: ["Identify safe cleanup targets"],
            HealingAction.OPTIMIZE_RESOURCES: ["Analyze resource usage patterns"]
        }
        
        return prerequisites.get(action, [])
    
    def _get_rollback_plan(self, action: HealingAction) -> List[str]:
        """Get rollback plan for healing action"""
        rollback_plans = {
            HealingAction.SCALE_UP: ["Scale down to original size"],
            HealingAction.RESTART_SERVICE: ["Restore from backup if needed"],
            HealingAction.FAILOVER: ["Failback to primary system"],
            HealingAction.CLEAN_LOGS: ["Restore from backup if needed"],
            HealingAction.OPTIMIZE_RESOURCES: ["Revert configuration changes"]
        }
        
        return rollback_plans.get(action, [])


class HealingExecutor:
    """Executes healing actions"""
    
    def __init__(self):
        self.executions: Dict[str, HealingExecution] = {}
        logger.info("Healing Executor initialized")
    
    def execute_healing_plan(self, plan: HealingPlan) -> List[HealingExecution]:
        """Execute healing plan"""
        executions = []
        
        for action in plan.recommended_actions:
            execution = HealingExecution(
                execution_id=f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                plan_id=plan.plan_id,
                action=action,
                status=HealingStatus.PENDING
            )
            
            self.executions[execution.execution_id] = execution
            
            # Execute action
            try:
                execution.status = HealingStatus.IN_PROGRESS
                success = self._execute_action(action, execution)
                
                execution.status = HealingStatus.SUCCESS if success else HealingStatus.FAILED
                execution.success = success
                execution.completed_at = datetime.now()
                
                if success:
                    logger.info(f"Healing action completed: {action.value}")
                else:
                    logger.error(f"Healing action failed: {action.value}")
                
            except Exception as e:
                execution.status = HealingStatus.FAILED
                execution.error_message = str(e)
                execution.completed_at = datetime.now()
                logger.error(f"Healing action error: {str(e)}")
            
            executions.append(execution)
            
            # Stop on first failure unless configured otherwise
            if not execution.success:
                break
        
        return executions
    
    def _execute_action(self, action: HealingAction, execution: HealingExecution) -> bool:
        """Execute specific healing action"""
        try:
            # Simulate action execution with random success/failure
            # In real implementation, these would call actual system APIs
            
            if action == HealingAction.RESTART_SERVICE:
                return self._restart_service(execution)
            elif action == HealingAction.SCALE_UP:
                return self._scale_up(execution)
            elif action == HealingAction.SCALE_DOWN:
                return self._scale_down(execution)
            elif action == HealingAction.FAILOVER:
                return self._failover(execution)
            elif action == HealingAction.CLEAN_LOGS:
                return self._clean_logs(execution)
            elif action == HealingAction.OPTIMIZE_RESOURCES:
                return self._optimize_resources(execution)
            else:
                logger.warning(f"Unknown healing action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing {action.value}: {str(e)}")
            return False
    
    def _restart_service(self, execution: HealingExecution) -> bool:
        """Restart service healing action"""
        logger.info("Executing service restart")
        # Simulate restart with 80% success rate
        success = random.random() < 0.8
        
        if success:
            execution.metrics_after = {"status": "running", "uptime": 0}
        
        return success
    
    def _scale_up(self, execution: HealingExecution) -> bool:
        """Scale up healing action"""
        logger.info("Executing scale up")
        # Simulate scale up with 85% success rate
        success = random.random() < 0.85
        
        if success:
            execution.metrics_after = {"instance_count": 4, "capacity": "increased"}
        
        return success
    
    def _scale_down(self, execution: HealingExecution) -> bool:
        """Scale down healing action"""
        logger.info("Executing scale down")
        # Simulate scale down with 90% success rate
        success = random.random() < 0.90
        
        if success:
            execution.metrics_after = {"instance_count": 2, "capacity": "decreased"}
        
        return success
    
    def _failover(self, execution: HealingExecution) -> bool:
        """Failover healing action"""
        logger.info("Executing failover")
        # Simulate failover with 95% success rate
        success = random.random() < 0.95
        
        if success:
            execution.metrics_after = {"active_instance": "secondary", "status": "failed_over"}
        
        return success
    
    def _clean_logs(self, execution: HealingExecution) -> bool:
        """Clean logs healing action"""
        logger.info("Executing log cleanup")
        # Simulate log cleanup with 75% success rate
        success = random.random() < 0.75
        
        if success:
            execution.metrics_after = {"disk_space_freed": "2GB", "log_size": "reduced"}
        
        return success
    
    def _optimize_resources(self, execution: HealingExecution) -> bool:
        """Optimize resources healing action"""
        logger.info("Executing resource optimization")
        # Simulate optimization with 70% success rate
        success = random.random() < 0.70
        
        if success:
            execution.metrics_after = {"cpu_optimized": True, "memory_optimized": True}
        
        return success
    
    def get_execution_status(self, execution_id: str) -> Optional[HealingExecution]:
        """Get healing execution status"""
        return self.executions.get(execution_id)


class LearningSystem:
    """Machine learning system for healing optimization"""
    
    def __init__(self):
        self.healing_history: List[Dict[str, Any]] = []
        self.success_patterns: Dict[str, float] = {}
        logger.info("Learning System initialized")
    
    def record_healing_outcome(
        self, anomaly: Anomaly, plan: HealingPlan, 
        executions: List[HealingExecution]
    ):
        """Record healing outcome for learning"""
        overall_success = all(exec.success for exec in executions)
        
        record = {
            "timestamp": datetime.now(),
            "anomaly_type": anomaly.anomaly_type.value,
            "metric_name": anomaly.metric_name,
            "severity": anomaly.severity.value,
            "healing_actions": [action.value for action in plan.recommended_actions],
            "success": overall_success,
            "duration_minutes": sum([
                (exec.completed_at - exec.started_at).total_seconds() / 60
                for exec in executions if exec.completed_at
            ])
        }
        
        self.healing_history.append(record)
        self._update_success_patterns()
        
        logger.info(f"Recorded healing outcome: success={overall_success}")
    
    def _update_success_patterns(self):
        """Update success patterns based on history"""
        patterns = {}
        
        for record in self.healing_history:
            key = f"{record['anomaly_type']}:{record['metric_name']}"
            
            if key not in patterns:
                patterns[key] = {"successes": 0, "total": 0}
            
            patterns[key]["total"] += 1
            if record["success"]:
                patterns[key]["successes"] += 1
        
        # Calculate success rates
        for key, data in patterns.items():
            self.success_patterns[key] = data["successes"] / data["total"]
    
    def get_predicted_success_rate(
        self, anomaly_type: AnomalyType, metric_name: str
    ) -> float:
        """Get predicted success rate for healing"""
        key = f"{anomaly_type.value}:{metric_name}"
        return self.success_patterns.get(key, 0.75)  # Default 75%
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from learning system"""
        if not self.healing_history:
            return {"message": "No healing history available"}
        
        total_healings = len(self.healing_history)
        successful_healings = sum(1 for record in self.healing_history if record["success"])
        
        return {
            "total_healing_attempts": total_healings,
            "successful_healings": successful_healings,
            "overall_success_rate": successful_healings / total_healings,
            "top_success_patterns": dict(
                sorted(self.success_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            "average_healing_duration": statistics.mean([
                record["duration_minutes"] for record in self.healing_history
                if record.get("duration_minutes", 0) > 0
            ]) if self.healing_history else 0
        }


class HealingEngine:
    """Main AI Healing Engine (Shiva)"""
    
    def __init__(self):
        self.anomaly_detector = AnomalyDetectionEngine()
        self.plan_generator = HealingPlanGenerator()
        self.executor = HealingExecutor()
        self.learning_system = LearningSystem()
        self.active_anomalies: List[Anomaly] = []
        self.healing_enabled = True
        
        logger.info("Shiva AI Healing Engine initialized")
    
    def process_metric(self, metric: MetricData) -> Dict[str, Any]:
        """Process incoming metric and trigger healing if needed"""
        result = {
            "metric_processed": True,
            "anomalies_detected": [],
            "healing_triggered": False,
            "healing_executions": []
        }
        
        try:
            # Ingest metric
            self.anomaly_detector.ingest_metric(metric)
            
            # Detect anomalies
            anomalies = self.anomaly_detector.detect_anomalies(metric)
            result["anomalies_detected"] = [a.anomaly_id for a in anomalies]
            
            # Process each anomaly
            for anomaly in anomalies:
                self.active_anomalies.append(anomaly)
                
                if self.healing_enabled and self._should_trigger_healing(anomaly):
                    healing_result = self._trigger_healing(anomaly)
                    result["healing_triggered"] = True
                    result["healing_executions"].extend(healing_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing metric: {str(e)}")
            result["error"] = str(e)
            return result
    
    def _should_trigger_healing(self, anomaly: Anomaly) -> bool:
        """Determine if healing should be triggered for anomaly"""
        # Trigger healing for high and critical severity anomalies
        if anomaly.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            return True
        
        # Check if confidence is high enough
        if anomaly.confidence_score > 0.8:
            return True
        
        return False
    
    def _trigger_healing(self, anomaly: Anomaly) -> List[str]:
        """Trigger automated healing for anomaly"""
        try:
            # Generate healing plan
            plan = self.plan_generator.generate_healing_plan(anomaly)
            
            # Execute healing plan
            executions = self.executor.execute_healing_plan(plan)
            
            # Record outcome for learning
            self.learning_system.record_healing_outcome(anomaly, plan, executions)
            
            logger.info(f"Healing triggered for anomaly: {anomaly.anomaly_id}")
            return [exec.execution_id for exec in executions]
            
        except Exception as e:
            logger.error(f"Error triggering healing: {str(e)}")
            return []
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        recent_time = datetime.now() - timedelta(hours=1)
        recent_anomalies = [
            a for a in self.active_anomalies 
            if a.detected_at > recent_time
        ]
        
        # Count by severity
        severity_counts = {
            "critical": len([a for a in recent_anomalies if a.severity == IncidentSeverity.CRITICAL]),
            "high": len([a for a in recent_anomalies if a.severity == IncidentSeverity.HIGH]),
            "medium": len([a for a in recent_anomalies if a.severity == IncidentSeverity.MEDIUM]),
            "low": len([a for a in recent_anomalies if a.severity == IncidentSeverity.LOW])
        }
        
        # Calculate health score
        health_score = 100
        health_score -= severity_counts["critical"] * 20
        health_score -= severity_counts["high"] * 10
        health_score -= severity_counts["medium"] * 5
        health_score -= severity_counts["low"] * 2
        health_score = max(0, health_score)
        
        return {
            "health_score": health_score,
            "status": self._get_health_status(health_score),
            "recent_anomalies": len(recent_anomalies),
            "anomalies_by_severity": severity_counts,
            "healing_enabled": self.healing_enabled,
            "learning_insights": self.learning_system.get_learning_insights(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_health_status(self, score: float) -> str:
        """Get health status based on score"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 50:
            return "fair"
        elif score >= 25:
            return "poor"
        else:
            return "critical"
    
    def enable_healing(self):
        """Enable automated healing"""
        self.healing_enabled = True
        logger.info("Automated healing enabled")
    
    def disable_healing(self):
        """Disable automated healing"""
        self.healing_enabled = False
        logger.info("Automated healing disabled")
    
    def get_active_anomalies(self) -> List[Dict[str, Any]]:
        """Get list of active anomalies"""
        return [
            {
                "anomaly_id": a.anomaly_id,
                "type": a.anomaly_type.value,
                "resource_id": a.resource_id,
                "metric_name": a.metric_name,
                "severity": a.severity.value,
                "detected_at": a.detected_at.isoformat(),
                "confidence_score": a.confidence_score,
                "description": a.description
            }
            for a in self.active_anomalies
        ]
    
    def simulate_metric_stream(self) -> List[MetricData]:
        """Simulate metric stream for testing"""
        resources = ["web-server-1", "db-server-1", "api-gateway-1"]
        metrics = ["cpu_utilization", "memory_utilization", "response_time"]
        
        simulated_metrics = []
        
        for resource in resources:
            for metric_name in metrics:
                # Generate normal and anomalous values
                if random.random() < 0.1:  # 10% chance of anomaly
                    if metric_name == "cpu_utilization":
                        value = random.uniform(85, 98)  # High CPU
                    elif metric_name == "memory_utilization":
                        value = random.uniform(80, 95)  # High memory
                    else:  # response_time
                        value = random.uniform(2000, 8000)  # High latency
                else:
                    if metric_name == "cpu_utilization":
                        value = random.uniform(20, 60)  # Normal CPU
                    elif metric_name == "memory_utilization":
                        value = random.uniform(30, 70)  # Normal memory
                    else:  # response_time
                        value = random.uniform(100, 500)  # Normal latency
                
                metric = MetricData(
                    timestamp=datetime.now(),
                    value=value,
                    metric_name=metric_name,
                    resource_id=resource,
                    tags={"environment": "production", "team": "platform"}
                )
                
                simulated_metrics.append(metric)
        
        return simulated_metrics


# Export main class
__all__ = ["HealingEngine", "MetricData", "Anomaly", "HealingPlan"]

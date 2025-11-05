"""
AetherEdge - Lakshmi Module: FinOps Intelligence Engine
The Prosperity Keeper - Balances cost, performance, and utilization

This module embodies the cosmic principle of Lakshmi (Prosperity) in digital form,
optimizing infrastructure costs while maintaining performance and compliance.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import statistics

# Setup logging
logger = logging.getLogger(__name__)


class CostCategory(Enum):
    """Cost categories for analysis"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    MONITORING = "monitoring"
    SECURITY = "security"
    BACKUP = "backup"
    OTHER = "other"


class OptimizationType(Enum):
    """Types of cost optimizations"""
    RIGHT_SIZING = "right_sizing"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_INSTANCES = "spot_instances"
    STORAGE_TIERING = "storage_tiering"
    LIFECYCLE_MANAGEMENT = "lifecycle_management"
    SCHEDULED_SCALING = "scheduled_scaling"
    UNUSED_RESOURCES = "unused_resources"
    DUPLICATE_RESOURCES = "duplicate_resources"


class RecommendationPriority(Enum):
    """Priority levels for recommendations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CostRecord:
    """Individual cost record"""
    record_id: str
    resource_id: str
    resource_type: str
    service_name: str
    cost_category: CostCategory
    amount: float
    currency: str
    billing_period: str
    region: str
    environment: str
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UtilizationMetric:
    """Resource utilization metrics"""
    resource_id: str
    cpu_utilization: float
    memory_utilization: float
    storage_utilization: float
    network_utilization: float
    measurement_period: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CostOptimizationRecommendation:
    """Cost optimization recommendation"""
    recommendation_id: str
    resource_id: str
    optimization_type: OptimizationType
    current_cost: float
    projected_cost: float
    potential_savings: float
    confidence_score: float
    priority: RecommendationPriority
    description: str
    implementation_effort: str  # low, medium, high
    risk_level: str  # low, medium, high
    implementation_steps: List[str]
    prerequisites: List[str] = field(default_factory=list)
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BudgetAlert:
    """Budget monitoring alert"""
    alert_id: str
    budget_name: str
    current_spend: float
    budget_limit: float
    threshold_percentage: float
    alert_type: str  # warning, critical, exceeded
    period: str
    triggered_at: datetime = field(default_factory=datetime.now)


class CostAnalyzer:
    """Analyzes infrastructure costs and trends"""
    
    def __init__(self):
        self.cost_history: List[CostRecord] = []
        self.budget_limits: Dict[str, float] = {}
        self.cost_baselines: Dict[str, float] = {}
        logger.info("Cost Analyzer initialized")
    
    def ingest_cost_data(self, cost_record: CostRecord):
        """Ingest cost data for analysis"""
        self.cost_history.append(cost_record)
        
        # Keep only last 12 months of data
        cutoff_date = datetime.now() - timedelta(days=365)
        self.cost_history = [
            record for record in self.cost_history 
            if record.timestamp > cutoff_date
        ]
        
        logger.debug(f"Cost record ingested: {cost_record.record_id}")
    
    def analyze_cost_trends(self, period_days: int = 30) -> Dict[str, Any]:
        """Analyze cost trends over specified period"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Filter records for the period
        period_records = [
            record for record in self.cost_history
            if start_date <= record.timestamp <= end_date
        ]
        
        if not period_records:
            return {"error": "No cost data available for the specified period"}
        
        # Aggregate costs by category
        category_costs = {}
        for record in period_records:
            category = record.cost_category.value
            category_costs[category] = category_costs.get(category, 0) + record.amount
        
        # Calculate total cost
        total_cost = sum(category_costs.values())
        
        # Compare with previous period
        prev_start = start_date - timedelta(days=period_days)
        prev_end = start_date
        
        prev_records = [
            record for record in self.cost_history
            if prev_start <= record.timestamp <= prev_end
        ]
        
        prev_total = sum(record.amount for record in prev_records)
        cost_change = ((total_cost - prev_total) / prev_total * 100) if prev_total > 0 else 0
        
        return {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_cost": total_cost,
            "previous_period_cost": prev_total,
            "cost_change_percentage": cost_change,
            "cost_by_category": category_costs,
            "average_daily_cost": total_cost / period_days,
            "trend": "increasing" if cost_change > 5 else "decreasing" if cost_change < -5 else "stable"
        }
    
    def analyze_cost_by_resource(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Analyze costs by individual resources"""
        # Aggregate costs by resource
        resource_costs = {}
        for record in self.cost_history:
            resource_id = record.resource_id
            if resource_id not in resource_costs:
                resource_costs[resource_id] = {
                    "resource_id": resource_id,
                    "resource_type": record.resource_type,
                    "total_cost": 0,
                    "environment": record.environment,
                    "region": record.region
                }
            resource_costs[resource_id]["total_cost"] += record.amount
        
        # Sort by cost and return top N
        sorted_resources = sorted(
            resource_costs.values(), 
            key=lambda x: x["total_cost"], 
            reverse=True
        )
        
        return sorted_resources[:top_n]
    
    def analyze_cost_anomalies(self, sensitivity: float = 2.0) -> List[Dict[str, Any]]:
        """Detect cost anomalies using statistical analysis"""
        if len(self.cost_history) < 30:  # Need enough data
            return []
        
        # Group by day and calculate daily costs
        daily_costs = {}
        for record in self.cost_history:
            date_key = record.timestamp.date().isoformat()
            daily_costs[date_key] = daily_costs.get(date_key, 0) + record.amount
        
        costs = list(daily_costs.values())
        if len(costs) < 10:
            return []
        
        mean_cost = statistics.mean(costs)
        std_cost = statistics.stdev(costs) if len(costs) > 1 else 0
        
        anomalies = []
        for date, cost in daily_costs.items():
            if std_cost > 0:
                z_score = abs((cost - mean_cost) / std_cost)
                if z_score > sensitivity:
                    anomalies.append({
                        "date": date,
                        "cost": cost,
                        "expected_cost": mean_cost,
                        "deviation_percentage": ((cost - mean_cost) / mean_cost) * 100,
                        "z_score": z_score,
                        "severity": "high" if z_score > 3 else "medium"
                    })
        
        return sorted(anomalies, key=lambda x: x["z_score"], reverse=True)
    
    def set_budget_limit(self, category: str, limit: float):
        """Set budget limit for category"""
        self.budget_limits[category] = limit
        logger.info(f"Budget limit set for {category}: ${limit}")
    
    def check_budget_alerts(self) -> List[BudgetAlert]:
        """Check for budget threshold breaches"""
        alerts = []
        current_month = datetime.now().strftime("%Y-%m")
        
        for category, limit in self.budget_limits.items():
            # Calculate current month spend for category
            month_records = [
                record for record in self.cost_history
                if (record.timestamp.strftime("%Y-%m") == current_month and 
                    (category == "total" or record.cost_category.value == category))
            ]
            
            current_spend = sum(record.amount for record in month_records)
            percentage = (current_spend / limit) * 100 if limit > 0 else 0
            
            # Generate alerts based on thresholds
            if percentage >= 100:
                alert_type = "exceeded"
            elif percentage >= 90:
                alert_type = "critical"
            elif percentage >= 75:
                alert_type = "warning"
            else:
                continue
            
            alert = BudgetAlert(
                alert_id=f"budget_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                budget_name=category,
                current_spend=current_spend,
                budget_limit=limit,
                threshold_percentage=percentage,
                alert_type=alert_type,
                period=current_month
            )
            
            alerts.append(alert)
        
        return alerts


class UtilizationAnalyzer:
    """Analyzes resource utilization for optimization"""
    
    def __init__(self):
        self.utilization_history: List[UtilizationMetric] = []
        logger.info("Utilization Analyzer initialized")
    
    def ingest_utilization_data(self, metric: UtilizationMetric):
        """Ingest utilization metrics"""
        self.utilization_history.append(metric)
        
        # Keep only last 30 days of data
        cutoff_date = datetime.now() - timedelta(days=30)
        self.utilization_history = [
            metric for metric in self.utilization_history
            if metric.timestamp > cutoff_date
        ]
        
        logger.debug(f"Utilization metric ingested: {metric.resource_id}")
    
    def analyze_underutilized_resources(
        self, cpu_threshold: float = 20.0, memory_threshold: float = 30.0
    ) -> List[Dict[str, Any]]:
        """Identify underutilized resources"""
        # Group metrics by resource
        resource_metrics = {}
        for metric in self.utilization_history:
            resource_id = metric.resource_id
            if resource_id not in resource_metrics:
                resource_metrics[resource_id] = []
            resource_metrics[resource_id].append(metric)
        
        underutilized = []
        for resource_id, metrics in resource_metrics.items():
            if len(metrics) < 5:  # Need enough data points
                continue
            
            avg_cpu = statistics.mean([m.cpu_utilization for m in metrics])
            avg_memory = statistics.mean([m.memory_utilization for m in metrics])
            max_cpu = max([m.cpu_utilization for m in metrics])
            max_memory = max([m.memory_utilization for m in metrics])
            
            if avg_cpu < cpu_threshold and avg_memory < memory_threshold:
                underutilized.append({
                    "resource_id": resource_id,
                    "average_cpu_utilization": avg_cpu,
                    "average_memory_utilization": avg_memory,
                    "max_cpu_utilization": max_cpu,
                    "max_memory_utilization": max_memory,
                    "sample_count": len(metrics),
                    "optimization_potential": "high" if avg_cpu < 10 and avg_memory < 20 else "medium"
                })
        
        return sorted(underutilized, key=lambda x: x["average_cpu_utilization"])
    
    def analyze_overutilized_resources(
        self, cpu_threshold: float = 80.0, memory_threshold: float = 85.0
    ) -> List[Dict[str, Any]]:
        """Identify overutilized resources"""
        resource_metrics = {}
        for metric in self.utilization_history:
            resource_id = metric.resource_id
            if resource_id not in resource_metrics:
                resource_metrics[resource_id] = []
            resource_metrics[resource_id].append(metric)
        
        overutilized = []
        for resource_id, metrics in resource_metrics.items():
            if len(metrics) < 5:
                continue
            
            avg_cpu = statistics.mean([m.cpu_utilization for m in metrics])
            avg_memory = statistics.mean([m.memory_utilization for m in metrics])
            max_cpu = max([m.cpu_utilization for m in metrics])
            max_memory = max([m.memory_utilization for m in metrics])
            
            if avg_cpu > cpu_threshold or avg_memory > memory_threshold:
                overutilized.append({
                    "resource_id": resource_id,
                    "average_cpu_utilization": avg_cpu,
                    "average_memory_utilization": avg_memory,
                    "max_cpu_utilization": max_cpu,
                    "max_memory_utilization": max_memory,
                    "sample_count": len(metrics),
                    "scaling_urgency": "high" if max_cpu > 95 or max_memory > 95 else "medium"
                })
        
        return sorted(overutilized, key=lambda x: max(x["average_cpu_utilization"], x["average_memory_utilization"]), reverse=True)
    
    def get_utilization_summary(self) -> Dict[str, Any]:
        """Get overall utilization summary"""
        if not self.utilization_history:
            return {"error": "No utilization data available"}
        
        # Calculate overall averages
        avg_cpu = statistics.mean([m.cpu_utilization for m in self.utilization_history])
        avg_memory = statistics.mean([m.memory_utilization for m in self.utilization_history])
        avg_storage = statistics.mean([m.storage_utilization for m in self.utilization_history])
        avg_network = statistics.mean([m.network_utilization for m in self.utilization_history])
        
        # Count resources by utilization bands
        total_resources = len(set(m.resource_id for m in self.utilization_history))
        
        return {
            "total_resources_monitored": total_resources,
            "average_cpu_utilization": avg_cpu,
            "average_memory_utilization": avg_memory,
            "average_storage_utilization": avg_storage,
            "average_network_utilization": avg_network,
            "utilization_efficiency": "good" if 30 <= avg_cpu <= 70 else "poor",
            "optimization_opportunities": self._count_optimization_opportunities()
        }
    
    def _count_optimization_opportunities(self) -> Dict[str, int]:
        """Count optimization opportunities"""
        underutilized = self.analyze_underutilized_resources()
        overutilized = self.analyze_overutilized_resources()
        
        return {
            "underutilized_resources": len(underutilized),
            "overutilized_resources": len(overutilized),
            "right_sizing_candidates": len(underutilized) + len(overutilized)
        }


class OptimizationEngine:
    """Generates cost optimization recommendations"""
    
    def __init__(self):
        self.cost_analyzer = CostAnalyzer()
        self.utilization_analyzer = UtilizationAnalyzer()
        self.optimization_patterns = self._load_optimization_patterns()
        logger.info("Optimization Engine initialized")
    
    def _load_optimization_patterns(self) -> Dict[str, Any]:
        """Load optimization patterns and savings estimates"""
        return {
            "right_sizing_down": {
                "typical_savings": 0.25,  # 25% cost reduction
                "confidence": 0.85,
                "implementation_effort": "low",
                "risk_level": "low"
            },
            "right_sizing_up": {
                "typical_savings": -0.15,  # 15% cost increase but better performance
                "confidence": 0.90,
                "implementation_effort": "low",
                "risk_level": "medium"
            },
            "reserved_instances": {
                "typical_savings": 0.40,  # 40% cost reduction
                "confidence": 0.95,
                "implementation_effort": "medium",
                "risk_level": "low"
            },
            "spot_instances": {
                "typical_savings": 0.60,  # 60% cost reduction
                "confidence": 0.75,
                "implementation_effort": "high",
                "risk_level": "medium"
            },
            "storage_tiering": {
                "typical_savings": 0.30,  # 30% cost reduction
                "confidence": 0.80,
                "implementation_effort": "medium",
                "risk_level": "low"
            },
            "unused_resources": {
                "typical_savings": 1.0,  # 100% cost reduction
                "confidence": 0.95,
                "implementation_effort": "low",
                "risk_level": "low"
            }
        }
    
    def generate_recommendations(
        self, cost_records: List[CostRecord], 
        utilization_metrics: List[UtilizationMetric]
    ) -> List[CostOptimizationRecommendation]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        # Ingest data
        for record in cost_records:
            self.cost_analyzer.ingest_cost_data(record)
        
        for metric in utilization_metrics:
            self.utilization_analyzer.ingest_utilization_data(metric)
        
        # Generate right-sizing recommendations
        recommendations.extend(self._generate_rightsizing_recommendations())
        
        # Generate reserved instance recommendations
        recommendations.extend(self._generate_reserved_instance_recommendations())
        
        # Generate unused resource recommendations
        recommendations.extend(self._generate_unused_resource_recommendations())
        
        # Generate storage optimization recommendations
        recommendations.extend(self._generate_storage_optimization_recommendations())
        
        # Sort by potential savings
        recommendations.sort(key=lambda x: x.potential_savings, reverse=True)
        
        return recommendations
    
    def _generate_rightsizing_recommendations(self) -> List[CostOptimizationRecommendation]:
        """Generate right-sizing recommendations"""
        recommendations = []
        
        # Underutilized resources - recommend downsizing
        underutilized = self.utilization_analyzer.analyze_underutilized_resources()
        for resource in underutilized:
            pattern = self.optimization_patterns["right_sizing_down"]
            
            # Estimate current cost (simplified)
            current_cost = 200.0  # Mock value
            projected_cost = current_cost * (1 - pattern["typical_savings"])
            
            recommendation = CostOptimizationRecommendation(
                recommendation_id=f"rs_down_{resource['resource_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                resource_id=resource["resource_id"],
                optimization_type=OptimizationType.RIGHT_SIZING,
                current_cost=current_cost,
                projected_cost=projected_cost,
                potential_savings=current_cost - projected_cost,
                confidence_score=pattern["confidence"],
                priority=RecommendationPriority.HIGH if resource["optimization_potential"] == "high" else RecommendationPriority.MEDIUM,
                description=f"Downsize resource due to low utilization (CPU: {resource['average_cpu_utilization']:.1f}%, Memory: {resource['average_memory_utilization']:.1f}%)",
                implementation_effort=pattern["implementation_effort"],
                risk_level=pattern["risk_level"],
                implementation_steps=[
                    "1. Schedule maintenance window",
                    "2. Create resource snapshot/backup",
                    "3. Resize resource to smaller instance type",
                    "4. Monitor performance for 24-48 hours",
                    "5. Validate application functionality"
                ],
                prerequisites=["Backup/snapshot capability", "Maintenance window approval"],
                impact_analysis={
                    "performance_impact": "minimal",
                    "availability_impact": "brief downtime during resize",
                    "estimated_downtime_minutes": 15
                }
            )
            
            recommendations.append(recommendation)
        
        # Overutilized resources - recommend upsizing
        overutilized = self.utilization_analyzer.analyze_overutilized_resources()
        for resource in overutilized:
            pattern = self.optimization_patterns["right_sizing_up"]
            
            current_cost = 200.0  # Mock value
            projected_cost = current_cost * (1 - pattern["typical_savings"])  # Increase cost
            
            recommendation = CostOptimizationRecommendation(
                recommendation_id=f"rs_up_{resource['resource_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                resource_id=resource["resource_id"],
                optimization_type=OptimizationType.RIGHT_SIZING,
                current_cost=current_cost,
                projected_cost=projected_cost,
                potential_savings=current_cost - projected_cost,  # Negative (cost increase)
                confidence_score=pattern["confidence"],
                priority=RecommendationPriority.CRITICAL if resource["scaling_urgency"] == "high" else RecommendationPriority.HIGH,
                description=f"Upsize resource due to high utilization (CPU: {resource['average_cpu_utilization']:.1f}%, Memory: {resource['average_memory_utilization']:.1f}%)",
                implementation_effort=pattern["implementation_effort"],
                risk_level=pattern["risk_level"],
                implementation_steps=[
                    "1. Schedule maintenance window",
                    "2. Create resource snapshot/backup",
                    "3. Resize resource to larger instance type",
                    "4. Monitor performance improvements",
                    "5. Validate enhanced application performance"
                ],
                prerequisites=["Backup/snapshot capability", "Budget approval for cost increase"],
                impact_analysis={
                    "performance_impact": "significant improvement",
                    "availability_impact": "brief downtime during resize",
                    "estimated_downtime_minutes": 15
                }
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_reserved_instance_recommendations(self) -> List[CostOptimizationRecommendation]:
        """Generate reserved instance recommendations"""
        recommendations = []
        
        # Analyze steady-state resources for reserved instance opportunities
        # This is a simplified implementation
        pattern = self.optimization_patterns["reserved_instances"]
        
        # Mock steady-state resources
        steady_resources = ["web-server-1", "db-server-1", "cache-server-1"]
        
        for resource_id in steady_resources:
            current_cost = 300.0  # Mock monthly on-demand cost
            projected_cost = current_cost * (1 - pattern["typical_savings"])
            
            recommendation = CostOptimizationRecommendation(
                recommendation_id=f"ri_{resource_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                resource_id=resource_id,
                optimization_type=OptimizationType.RESERVED_INSTANCES,
                current_cost=current_cost,
                projected_cost=projected_cost,
                potential_savings=current_cost - projected_cost,
                confidence_score=pattern["confidence"],
                priority=RecommendationPriority.HIGH,
                description=f"Convert to reserved instance for steady-state workload",
                implementation_effort=pattern["implementation_effort"],
                risk_level=pattern["risk_level"],
                implementation_steps=[
                    "1. Analyze 12-month usage patterns",
                    "2. Purchase reserved instance commitment",
                    "3. Apply reservation to existing resource",
                    "4. Monitor cost savings",
                    "5. Set calendar reminder for renewal evaluation"
                ],
                prerequisites=["Budget approval", "12-month commitment approval"],
                impact_analysis={
                    "performance_impact": "none",
                    "availability_impact": "none",
                    "payment_structure": "upfront or monthly commitment"
                }
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_unused_resource_recommendations(self) -> List[CostOptimizationRecommendation]:
        """Generate unused resource recommendations"""
        recommendations = []
        
        # Identify resources with zero utilization
        # This is a simplified implementation
        pattern = self.optimization_patterns["unused_resources"]
        
        # Mock unused resources
        unused_resources = ["test-server-old", "backup-storage-temp"]
        
        for resource_id in unused_resources:
            current_cost = 150.0  # Mock monthly cost
            projected_cost = 0.0  # Cost after removal
            
            recommendation = CostOptimizationRecommendation(
                recommendation_id=f"unused_{resource_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                resource_id=resource_id,
                optimization_type=OptimizationType.UNUSED_RESOURCES,
                current_cost=current_cost,
                projected_cost=projected_cost,
                potential_savings=current_cost,
                confidence_score=pattern["confidence"],
                priority=RecommendationPriority.HIGH,
                description=f"Remove unused resource to eliminate cost",
                implementation_effort=pattern["implementation_effort"],
                risk_level=pattern["risk_level"],
                implementation_steps=[
                    "1. Verify resource is truly unused",
                    "2. Check for any dependencies",
                    "3. Create final backup if needed",
                    "4. Terminate/delete resource",
                    "5. Verify cost savings in next bill"
                ],
                prerequisites=["Stakeholder confirmation", "Dependency check"],
                impact_analysis={
                    "performance_impact": "none",
                    "availability_impact": "none if truly unused",
                    "recovery_difficulty": "high if backup not taken"
                }
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_storage_optimization_recommendations(self) -> List[CostOptimizationRecommendation]:
        """Generate storage optimization recommendations"""
        recommendations = []
        
        pattern = self.optimization_patterns["storage_tiering"]
        
        # Mock storage resources needing tiering
        storage_resources = ["backup-storage-1", "archive-storage-1"]
        
        for resource_id in storage_resources:
            current_cost = 100.0  # Mock monthly storage cost
            projected_cost = current_cost * (1 - pattern["typical_savings"])
            
            recommendation = CostOptimizationRecommendation(
                recommendation_id=f"storage_{resource_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                resource_id=resource_id,
                optimization_type=OptimizationType.STORAGE_TIERING,
                current_cost=current_cost,
                projected_cost=projected_cost,
                potential_savings=current_cost - projected_cost,
                confidence_score=pattern["confidence"],
                priority=RecommendationPriority.MEDIUM,
                description=f"Implement storage tiering for cost optimization",
                implementation_effort=pattern["implementation_effort"],
                risk_level=pattern["risk_level"],
                implementation_steps=[
                    "1. Analyze data access patterns",
                    "2. Define tiering policies",
                    "3. Configure automated lifecycle management",
                    "4. Monitor cost and performance impact",
                    "5. Adjust policies based on results"
                ],
                prerequisites=["Storage analytics", "Lifecycle management capability"],
                impact_analysis={
                    "performance_impact": "minimal for infrequently accessed data",
                    "availability_impact": "none",
                    "retrieval_time": "may increase for archived data"
                }
            )
            
            recommendations.append(recommendation)
        
        return recommendations


class FinOpsEngine:
    """Main FinOps Intelligence Engine (Lakshmi)"""
    
    def __init__(self):
        self.cost_analyzer = CostAnalyzer()
        self.utilization_analyzer = UtilizationAnalyzer()
        self.optimization_engine = OptimizationEngine()
        self.savings_tracking: List[Dict[str, Any]] = []
        
        logger.info("Lakshmi FinOps Intelligence Engine initialized")
    
    def analyze_financial_health(self) -> Dict[str, Any]:
        """Comprehensive financial health analysis"""
        try:
            # Cost trends
            cost_trends = self.cost_analyzer.analyze_cost_trends()
            
            # Budget alerts
            budget_alerts = self.cost_analyzer.check_budget_alerts()
            
            # Cost anomalies
            cost_anomalies = self.cost_analyzer.analyze_cost_anomalies()
            
            # Utilization summary
            utilization_summary = self.utilization_analyzer.get_utilization_summary()
            
            # Calculate financial health score
            health_score = self._calculate_financial_health_score(
                cost_trends, budget_alerts, cost_anomalies, utilization_summary
            )
            
            return {
                "financial_health_score": health_score,
                "status": self._get_health_status(health_score),
                "cost_trends": cost_trends,
                "budget_alerts": len(budget_alerts),
                "cost_anomalies": len(cost_anomalies),
                "utilization_efficiency": utilization_summary.get("utilization_efficiency", "unknown"),
                "optimization_opportunities": utilization_summary.get("optimization_opportunities", {}),
                "recommendations_available": True,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing financial health: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_financial_health_score(
        self, cost_trends: Dict[str, Any], budget_alerts: List[BudgetAlert],
        cost_anomalies: List[Dict[str, Any]], utilization_summary: Dict[str, Any]
    ) -> float:
        """Calculate overall financial health score (0-100)"""
        score = 100
        
        # Deduct for cost increase trend
        cost_change = cost_trends.get("cost_change_percentage", 0)
        if cost_change > 20:
            score -= 30
        elif cost_change > 10:
            score -= 15
        elif cost_change > 5:
            score -= 5
        
        # Deduct for budget alerts
        for alert in budget_alerts:
            if alert.alert_type == "exceeded":
                score -= 25
            elif alert.alert_type == "critical":
                score -= 15
            elif alert.alert_type == "warning":
                score -= 5
        
        # Deduct for cost anomalies
        for anomaly in cost_anomalies:
            if anomaly["severity"] == "high":
                score -= 10
            else:
                score -= 5
        
        # Deduct for poor utilization efficiency
        utilization_efficiency = utilization_summary.get("utilization_efficiency", "good")
        if utilization_efficiency == "poor":
            score -= 20
        
        return max(0, score)
    
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
    
    def generate_cost_forecast(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Generate cost forecast"""
        try:
            # Analyze recent cost trends
            recent_trends = self.cost_analyzer.analyze_cost_trends(period_days=30)
            
            current_daily_cost = recent_trends.get("average_daily_cost", 0)
            cost_change_rate = recent_trends.get("cost_change_percentage", 0) / 100
            
            # Simple linear forecast (can be enhanced with ML models)
            forecasted_daily_cost = current_daily_cost * (1 + cost_change_rate)
            total_forecasted_cost = forecasted_daily_cost * days_ahead
            
            return {
                "forecast_period_days": days_ahead,
                "current_daily_average": current_daily_cost,
                "forecasted_daily_average": forecasted_daily_cost,
                "total_forecasted_cost": total_forecasted_cost,
                "projected_change_percentage": cost_change_rate * 100,
                "confidence_level": "medium",  # Can be enhanced with statistical confidence
                "forecast_generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating cost forecast: {str(e)}")
            return {"error": str(e)}
    
    def track_optimization_savings(
        self, recommendation_id: str, actual_savings: float, 
        implementation_date: datetime
    ):
        """Track actual savings from implemented optimizations"""
        savings_record = {
            "recommendation_id": recommendation_id,
            "actual_savings": actual_savings,
            "implementation_date": implementation_date,
            "tracked_at": datetime.now()
        }
        
        self.savings_tracking.append(savings_record)
        logger.info(f"Optimization savings tracked: ${actual_savings}")
    
    def get_savings_summary(self) -> Dict[str, Any]:
        """Get summary of optimization savings"""
        if not self.savings_tracking:
            return {"message": "No optimization savings tracked yet"}
        
        total_savings = sum(record["actual_savings"] for record in self.savings_tracking)
        total_optimizations = len(self.savings_tracking)
        average_savings = total_savings / total_optimizations if total_optimizations > 0 else 0
        
        # Calculate monthly savings rate
        current_month = datetime.now().strftime("%Y-%m")
        monthly_savings = sum(
            record["actual_savings"] for record in self.savings_tracking
            if record["implementation_date"].strftime("%Y-%m") == current_month
        )
        
        return {
            "total_savings_ytd": total_savings,
            "total_optimizations_implemented": total_optimizations,
            "average_savings_per_optimization": average_savings,
            "monthly_savings": monthly_savings,
            "savings_trend": "positive" if monthly_savings > 0 else "neutral",
            "last_updated": datetime.now().isoformat()
        }
    
    def get_finops_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for FinOps dashboard"""
        return {
            "financial_health": self.analyze_financial_health(),
            "cost_forecast": self.generate_cost_forecast(),
            "savings_summary": self.get_savings_summary(),
            "top_cost_resources": self.cost_analyzer.analyze_cost_by_resource(top_n=5),
            "budget_status": self.cost_analyzer.check_budget_alerts(),
            "optimization_opportunities": len(
                self.optimization_engine.generate_recommendations([], [])
            ),
            "dashboard_updated_at": datetime.now().isoformat()
        }


# Export main class
__all__ = ["FinOpsEngine", "CostRecord", "UtilizationMetric", "CostOptimizationRecommendation"]

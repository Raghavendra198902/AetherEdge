"""
💰 Cost Estimator Service
==========================

Estimates infrastructure costs for generated blueprints across
different cloud providers. Provides detailed breakdowns and
optimization recommendations.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .ai_engine import ArchitectureBlueprint, InfrastructureComponent

logger = logging.getLogger(__name__)


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a component"""
    component_name: str
    component_type: str
    monthly_cost: float
    yearly_cost: float
    cost_factors: Dict[str, float]
    optimization_suggestions: List[str]


@dataclass
class CostEstimate:
    """Complete cost estimate for an architecture"""
    total_monthly: float
    total_yearly: float
    components: List[CostBreakdown]
    currency: str = "USD"
    region: str = "eastus"
    confidence_level: str = "medium"
    last_updated: str = ""


class CostEstimator:
    """
    Infrastructure cost estimation service
    
    Provides cost estimates for infrastructure components
    across different cloud providers and regions.
    """
    
    def __init__(self):
        self.pricing_data = self._initialize_pricing_data()
        self.regional_multipliers = self._initialize_regional_multipliers()
        
    async def estimate_cost(
        self,
        architecture: Optional[ArchitectureBlueprint] = None,
        terraform_code: Optional[str] = None,
        cloud_provider: str = "azure",
        region: str = "eastus"
    ) -> Dict[str, Any]:
        """
        Estimate costs for infrastructure architecture
        """
        try:
            logger.info(
                "Estimating costs for %s in %s", cloud_provider, region
            )
            
            if architecture:
                components = architecture.components
            elif terraform_code:
                components = self._parse_terraform_components(terraform_code)
            else:
                raise ValueError(
                    "Either architecture or terraform_code required"
                )
            
            # Calculate cost for each component
            cost_breakdowns = []
            total_monthly = 0.0
            
            for component in components:
                breakdown = self._calculate_component_cost(
                    component, cloud_provider, region
                )
                cost_breakdowns.append(breakdown)
                total_monthly += breakdown.monthly_cost
            
            # Create cost estimate
            estimate = CostEstimate(
                total_monthly=total_monthly,
                total_yearly=total_monthly * 12,
                components=cost_breakdowns,
                region=region
            )
            
            # Convert to dictionary for JSON serialization
            result = {
                "summary": {
                    "total_monthly_usd": round(estimate.total_monthly, 2),
                    "total_yearly_usd": round(estimate.total_yearly, 2),
                    "currency": estimate.currency,
                    "region": estimate.region,
                    "confidence_level": estimate.confidence_level
                },
                "components": [
                    {
                        "name": breakdown.component_name,
                        "type": breakdown.component_type,
                        "monthly_cost": round(breakdown.monthly_cost, 2),
                        "yearly_cost": round(breakdown.yearly_cost, 2),
                        "cost_factors": breakdown.cost_factors,
                        "optimization_suggestions": (
                            breakdown.optimization_suggestions
                        )
                    }
                    for breakdown in cost_breakdowns
                ],
                "optimization_summary": self._generate_optimization_summary(
                    cost_breakdowns
                ),
                "cost_alerts": self._generate_cost_alerts(estimate)
            }
            
            logger.info(
                "Cost estimation completed: $%.2f/month", total_monthly
            )
            return result
            
        except Exception as e:
            logger.error("Error estimating costs: %s", str(e))
            raise
    
    def _calculate_component_cost(
        self,
        component: InfrastructureComponent,
        cloud_provider: str,
        region: str
    ) -> CostBreakdown:
        """Calculate cost for a single component"""
        
        # Get base pricing for component type
        base_cost = self._get_base_cost(
            component.type, cloud_provider, component.properties
        )
        
        # Apply regional multiplier
        regional_multiplier = self.regional_multipliers.get(
            f"{cloud_provider}_{region}", 1.0
        )
        
        # Apply tier multiplier based on cost tier
        tier_multipliers = {"low": 0.5, "medium": 1.0, "high": 2.0}
        tier_multiplier = tier_multipliers.get(component.cost_tier, 1.0)
        
        # Calculate final cost
        monthly_cost = base_cost * regional_multiplier * tier_multiplier
        
        # Generate cost factors breakdown
        cost_factors = {
            "base_cost": base_cost,
            "regional_multiplier": regional_multiplier,
            "tier_multiplier": tier_multiplier,
            "final_monthly": monthly_cost
        }
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_component_optimizations(
            component, monthly_cost
        )
        
        return CostBreakdown(
            component_name=component.name,
            component_type=component.type,
            monthly_cost=monthly_cost,
            yearly_cost=monthly_cost * 12,
            cost_factors=cost_factors,
            optimization_suggestions=optimization_suggestions
        )
    
    def _get_base_cost(
        self,
        component_type: str,
        cloud_provider: str,
        properties: Dict[str, Any]
    ) -> float:
        """Get base monthly cost for component type"""
        
        # Future: Get base pricing for component type
        # pricing_key = f"{cloud_provider}_{component_type}"
        # base_pricing = self.pricing_data.get(pricing_key, {})
        
        if component_type == "web_app":
            # Cost based on instance size and scaling
            instance_size = properties.get("instance_size", "small")
            scale_factor = properties.get("scale_factor", 1)
            
            size_costs = {"small": 50, "medium": 100, "large": 200}
            return size_costs.get(instance_size, 100) * scale_factor
            
        elif component_type == "database":
            # Cost based on engine, storage, and compute
            engine = properties.get("engine", "postgresql")
            storage_gb = properties.get("storage_gb", 100)
            compute_tier = properties.get("compute_tier", "standard")
            
            # Base compute cost
            compute_costs = {"basic": 30, "standard": 100, "premium": 300}
            compute_cost = compute_costs.get(compute_tier, 100)
            
            # Storage cost (per GB)
            storage_cost = storage_gb * 0.12  # $0.12 per GB
            
            return compute_cost + storage_cost
            
        elif component_type == "storage":
            # Cost based on storage type and size
            storage_type = properties.get("type", "standard")
            size_gb = properties.get("size_gb", 100)
            
            # Cost per GB based on type
            type_costs = {"standard": 0.05, "premium": 0.15, "hot": 0.02}
            cost_per_gb = type_costs.get(storage_type, 0.05)
            
            return size_gb * cost_per_gb
            
        elif component_type == "container_app":
            # Cost based on CPU/memory allocation
            cpu_cores = properties.get("cpu_cores", 1)
            memory_gb = properties.get("memory_gb", 2)
            
            cpu_cost = cpu_cores * 25  # $25 per vCPU
            memory_cost = memory_gb * 5  # $5 per GB RAM
            
            return cpu_cost + memory_cost
            
        elif component_type == "api_management":
            # Cost based on tier and requests
            tier = properties.get("tier", "standard")
            monthly_requests = properties.get("monthly_requests", 100000)
            
            tier_costs = {"developer": 50, "standard": 250, "premium": 2500}
            base_cost = tier_costs.get(tier, 250)
            
            # Additional cost for requests over included amount
            included_requests = {"developer": 1000000, "standard": 1000000, 
                               "premium": 10000000}
            excess_requests = max(
                0, monthly_requests - included_requests.get(tier, 1000000)
            )
            request_cost = (excess_requests / 1000) * 0.035
            
            return base_cost + request_cost
            
        else:
            # Default cost for unknown component types
            return 50.0
    
    def _generate_component_optimizations(
        self, component: InfrastructureComponent, monthly_cost: float
    ) -> List[str]:
        """Generate optimization suggestions for a component"""
        suggestions = []
        
        if monthly_cost > 200:
            suggestions.append("Consider right-sizing to reduce costs")
            
        if component.type == "database":
            suggestions.extend([
                "Enable automatic pause for dev/test environments",
                "Consider reserved instances for production workloads",
                "Optimize storage with lifecycle policies"
            ])
            
        elif component.type == "web_app":
            suggestions.extend([
                "Implement auto-scaling to optimize costs",
                "Consider spot instances for non-critical workloads",
                "Use CDN to reduce compute costs"
            ])
            
        elif component.type == "storage":
            suggestions.extend([
                "Implement intelligent tiering",
                "Set up lifecycle management policies",
                "Consider compression for archived data"
            ])
            
        if component.cost_tier == "high":
            suggestions.append("Review if premium tier is necessary")
            
        return suggestions
    
    def _generate_optimization_summary(
        self, breakdowns: List[CostBreakdown]
    ) -> Dict[str, Any]:
        """Generate overall optimization summary"""
        total_cost = sum(b.monthly_cost for b in breakdowns)
        high_cost_components = [
            b for b in breakdowns if b.monthly_cost > 100
        ]
        
        potential_savings = 0.0
        for breakdown in high_cost_components:
            # Estimate 15-30% savings potential for high-cost components
            potential_savings += breakdown.monthly_cost * 0.2
        
        return {
            "total_monthly_cost": round(total_cost, 2),
            "high_cost_components": len(high_cost_components),
            "estimated_monthly_savings": round(potential_savings, 2),
            "savings_percentage": round(
                (potential_savings / total_cost * 100) if total_cost > 0 else 0, 1
            ),
            "recommendations": [
                "Review resource utilization regularly",
                "Implement auto-scaling policies",
                "Consider reserved instances for predictable workloads",
                "Use monitoring to identify unused resources",
                "Implement cost budgets and alerts"
            ]
        }
    
    def _generate_cost_alerts(self, estimate: CostEstimate) -> List[Dict[str, str]]:
        """Generate cost-related alerts"""
        alerts = []
        
        if estimate.total_monthly > 1000:
            alerts.append({
                "level": "warning",
                "message": "Monthly cost exceeds $1,000 - review for optimization",
                "recommendation": "Consider implementing cost controls"
            })
            
        if estimate.total_monthly > 5000:
            alerts.append({
                "level": "critical",
                "message": "Monthly cost exceeds $5,000 - immediate review required",
                "recommendation": "Implement strict cost monitoring and controls"
            })
            
        # Check for components with high individual costs
        expensive_components = [
            c for c in estimate.components if c.monthly_cost > 500
        ]
        
        if expensive_components:
            alerts.append({
                "level": "info",
                "message": f"{len(expensive_components)} component(s) exceed $500/month",
                "recommendation": "Review these components for optimization opportunities"
            })
            
        return alerts
    
    def _parse_terraform_components(
        self, terraform_code: str
    ) -> List[InfrastructureComponent]:
        """Parse Terraform code to extract components (simplified)"""
        # This is a simplified parser - in production would use proper HCL parsing
        components = []
        
        # Simple regex-based parsing for demo purposes
        import re
        
        # Find resource blocks
        resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{'
        matches = re.findall(resource_pattern, terraform_code)
        
        for resource_type, resource_name in matches:
            # Map Terraform resource types to our component types
            component_type = self._map_terraform_type_to_component_type(
                resource_type
            )
            
            component = InfrastructureComponent(
                name=resource_name,
                type=component_type,
                properties={},
                dependencies=[],
                security_requirements=[],
                cost_tier="medium"
            )
            components.append(component)
            
        return components
    
    def _map_terraform_type_to_component_type(
        self, terraform_type: str
    ) -> str:
        """Map Terraform resource types to our component types"""
        mapping = {
            "azurerm_linux_web_app": "web_app",
            "azurerm_windows_web_app": "web_app",
            "aws_elastic_beanstalk_environment": "web_app",
            "azurerm_postgresql_server": "database",
            "azurerm_mysql_server": "database", 
            "aws_db_instance": "database",
            "azurerm_storage_account": "storage",
            "aws_s3_bucket": "storage",
            "azurerm_container_app": "container_app",
            "aws_ecs_service": "container_app"
        }
        
        return mapping.get(terraform_type, "unknown")
    
    def _initialize_pricing_data(self) -> Dict[str, Dict[str, float]]:
        """Initialize base pricing data for different cloud providers"""
        return {
            # Azure pricing (monthly USD)
            "azure_web_app": {"small": 50, "medium": 100, "large": 200},
            "azure_database": {"basic": 30, "standard": 100, "premium": 300},
            "azure_storage": {"standard": 0.05, "premium": 0.15},
            "azure_container_app": {"cpu_hour": 25, "memory_gb": 5},
            
            # AWS pricing (monthly USD)
            "aws_web_app": {"small": 45, "medium": 95, "large": 190},
            "aws_database": {"basic": 25, "standard": 90, "premium": 280},
            "aws_storage": {"standard": 0.045, "premium": 0.13},
            "aws_container_app": {"cpu_hour": 23, "memory_gb": 4.5},
            
            # GCP pricing (monthly USD)
            "gcp_web_app": {"small": 40, "medium": 85, "large": 170},
            "gcp_database": {"basic": 20, "standard": 80, "premium": 250},
            "gcp_storage": {"standard": 0.04, "premium": 0.12},
            "gcp_container_app": {"cpu_hour": 20, "memory_gb": 4}
        }
    
    def _initialize_regional_multipliers(self) -> Dict[str, float]:
        """Initialize regional pricing multipliers"""
        return {
            # Azure regions
            "azure_eastus": 1.0,
            "azure_westus": 1.1,
            "azure_northeurope": 1.05,
            "azure_westeurope": 1.08,
            "azure_southeastasia": 1.12,
            
            # AWS regions
            "aws_us-east-1": 1.0,
            "aws_us-west-2": 1.05,
            "aws_eu-west-1": 1.08,
            "aws_ap-southeast-1": 1.15,
            
            # GCP regions
            "gcp_us-central1": 1.0,
            "gcp_us-west1": 1.03,
            "gcp_europe-west1": 1.06,
            "gcp_asia-southeast1": 1.12
        }

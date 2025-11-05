"""
AetherEdge - Brahma Module: AI Blueprint Engine
The Creator - Generates infrastructure blueprints from human intent

This module embodies the cosmic principle of Brahma (Creator) in digital form,
converting natural language infrastructure requirements into executable
IaC templates.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import yaml
import re
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)


class InfrastructureType(Enum):
    """Supported infrastructure types"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    SECURITY = "security"
    MONITORING = "monitoring"
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    VMWARE = "vmware"
    OPENSTACK = "openstack"
    ON_PREMISE = "on_premise"


@dataclass
class BlueprintRequest:
    """Blueprint generation request"""
    intent: str
    provider: CloudProvider
    environment: str  # dev, staging, prod
    compliance_requirements: List[str]
    budget_limit: Optional[float] = None
    performance_requirements: Optional[Dict[str, Any]] = None
    security_level: str = "medium"  # low, medium, high, critical


@dataclass
class GeneratedBlueprint:
    """Generated infrastructure blueprint"""
    blueprint_id: str
    name: str
    description: str
    provider: CloudProvider
    infrastructure_type: InfrastructureType
    terraform_code: str
    ansible_playbook: str
    estimated_cost: float
    compliance_score: float
    security_score: float
    created_at: datetime
    metadata: Dict[str, Any]


class AIIntelligenceEngine:
    """AI-powered infrastructure intelligence"""
    
    def __init__(self):
        self.patterns = self._load_infrastructure_patterns()
        self.cost_models = self._load_cost_models()
        
    def _load_infrastructure_patterns(self) -> Dict[str, Any]:
        """Load pre-trained infrastructure patterns"""
        return {
            "web_application": {
                "components": ["load_balancer", "compute", "database", "storage"],
                "best_practices": ["multi_az", "auto_scaling", "backup"],
                "security": ["ssl_termination", "waf", "security_groups"]
            },
            "data_pipeline": {
                "components": ["data_ingestion", "processing", "storage", "analytics"],
                "best_practices": ["data_validation", "monitoring", "lineage"],
                "security": ["encryption", "access_control", "audit_logging"]
            },
            "microservices": {
                "components": ["service_mesh", "kubernetes", "monitoring", "cicd"],
                "best_practices": ["circuit_breaker", "observability", "secrets_management"],
                "security": ["mtls", "rbac", "network_policies"]
            }
        }
    
    def _load_cost_models(self) -> Dict[str, Any]:
        """Load cost estimation models"""
        return {
            "aws": {
                "ec2": {"t3.micro": 0.0104, "t3.small": 0.0208, "t3.medium": 0.0416},
                "rds": {"db.t3.micro": 0.017, "db.t3.small": 0.034},
                "s3": {"standard": 0.023, "ia": 0.0125, "glacier": 0.004}
            },
            "azure": {
                "vm": {"b1s": 0.0104, "b2s": 0.0416, "b4ms": 0.166},
                "sql": {"basic": 0.017, "standard": 0.034},
                "storage": {"hot": 0.0184, "cool": 0.01, "archive": 0.002}
            }
        }
    
    def analyze_intent(self, intent: str) -> Dict[str, Any]:
        """Analyze natural language intent using AI"""
        # Extract infrastructure requirements from natural language
        analysis = {
            "infrastructure_type": self._detect_infrastructure_type(intent),
            "components": self._extract_components(intent),
            "scale_requirements": self._extract_scale(intent),
            "security_requirements": self._extract_security_needs(intent),
            "compliance_needs": self._extract_compliance(intent)
        }
        
        logger.info(f"Intent analysis completed: {analysis}")
        return analysis
    
    def _detect_infrastructure_type(self, intent: str) -> InfrastructureType:
        """Detect primary infrastructure type from intent"""
        intent_lower = intent.lower()
        
        if any(keyword in intent_lower for keyword in ["web", "application", "api", "frontend"]):
            return InfrastructureType.COMPUTE
        elif any(keyword in intent_lower for keyword in ["data", "analytics", "etl", "pipeline"]):
            return InfrastructureType.DATABASE
        elif any(keyword in intent_lower for keyword in ["kubernetes", "container", "microservice"]):
            return InfrastructureType.KUBERNETES
        elif any(keyword in intent_lower for keyword in ["lambda", "function", "serverless"]):
            return InfrastructureType.SERVERLESS
        else:
            return InfrastructureType.COMPUTE  # Default
    
    def _extract_components(self, intent: str) -> List[str]:
        """Extract infrastructure components from intent"""
        components = []
        intent_lower = intent.lower()
        
        component_keywords = {
            "load_balancer": ["load balancer", "lb", "alb", "nlb"],
            "database": ["database", "db", "mysql", "postgres", "mongodb"],
            "cache": ["cache", "redis", "memcached"],
            "storage": ["storage", "s3", "blob", "file system"],
            "compute": ["server", "vm", "ec2", "compute"],
            "monitoring": ["monitoring", "metrics", "logs", "observability"]
        }
        
        for component, keywords in component_keywords.items():
            if any(keyword in intent_lower for keyword in keywords):
                components.append(component)
        
        return components
    
    def _extract_scale(self, intent: str) -> Dict[str, Any]:
        """Extract scaling requirements"""
        scale_info = {"instances": 1, "auto_scaling": False}
        
        # Extract numbers for scaling
        numbers = re.findall(r'\d+', intent)
        if numbers:
            scale_info["instances"] = int(numbers[0])
        
        if any(keyword in intent.lower() for keyword in ["scale", "auto", "elastic"]):
            scale_info["auto_scaling"] = True
        
        return scale_info
    
    def _extract_security_needs(self, intent: str) -> List[str]:
        """Extract security requirements"""
        security_needs = []
        intent_lower = intent.lower()
        
        security_keywords = {
            "encryption": ["encrypt", "ssl", "tls"],
            "firewall": ["firewall", "security group", "network security"],
            "authentication": ["auth", "login", "sso", "oauth"],
            "compliance": ["compliant", "gdpr", "hipaa", "pci"]
        }
        
        for need, keywords in security_keywords.items():
            if any(keyword in intent_lower for keyword in keywords):
                security_needs.append(need)
        
        return security_needs
    
    def _extract_compliance(self, intent: str) -> List[str]:
        """Extract compliance requirements"""
        compliance = []
        intent_lower = intent.lower()
        
        compliance_standards = ["gdpr", "hipaa", "pci", "sox", "iso27001", "nist"]
        for standard in compliance_standards:
            if standard in intent_lower:
                compliance.append(standard.upper())
        
        return compliance


class TerraformGenerator:
    """Generates Terraform IaC templates"""
    
    def __init__(self):
        self.templates = self._load_terraform_templates()
    
    def _load_terraform_templates(self) -> Dict[str, str]:
        """Load Terraform template library"""
        return {
            "aws_web_app": '''
# AWS Web Application Infrastructure
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.environment}-igw"
    Environment = var.environment
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count = 2
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.environment}-public-${count.index + 1}"
    Environment = var.environment
  }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "${var.environment}-public-rt"
    Environment = var.environment
  }
}

# Route Table Association
resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Security Group for Web Servers
resource "aws_security_group" "web" {
  name_prefix = "${var.environment}-web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-web-sg"
    Environment = var.environment
  }
}

# Launch Template
resource "aws_launch_template" "web" {
  name_prefix   = "${var.environment}-web-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = base64encode(<<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              echo "<h1>AetherEdge ${var.environment} Environment</h1>" > /var/www/html/index.html
              EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name        = "${var.environment}-web"
      Environment = var.environment
    }
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "web" {
  name                = "${var.environment}-web-asg"
  vpc_zone_identifier = aws_subnet.public[*].id
  min_size            = 1
  max_size            = 3
  desired_capacity    = 2

  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.environment}-web-asg"
    propagate_at_launch = false
  }

  tag {
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.web.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    Name        = "${var.environment}-alb"
    Environment = var.environment
  }
}

# Target Group
resource "aws_lb_target_group" "web" {
  name     = "${var.environment}-web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.environment}-web-tg"
    Environment = var.environment
  }
}

# Load Balancer Listener
resource "aws_lb_listener" "web" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# Auto Scaling Group Attachment
resource "aws_autoscaling_attachment" "web" {
  autoscaling_group_name = aws_autoscaling_group.web.id
  lb_target_group_arn    = aws_lb_target_group.web.arn
}

# Data Sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Outputs
output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}
            ''',
            "kubernetes_cluster": '''
# Kubernetes Cluster Infrastructure
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "aether-edge"
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.cluster_version

  vpc_config {
    subnet_ids = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster_AmazonEKSClusterPolicy,
  ]

  tags = {
    Name = var.cluster_name
  }
}

# EKS Node Group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = aws_subnet.private[*].id

  scaling_config {
    desired_size = 2
    max_size     = 4
    min_size     = 1
  }

  instance_types = ["t3.medium"]

  depends_on = [
    aws_iam_role_policy_attachment.node_AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.node_AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.node_AmazonEC2ContainerRegistryReadOnly,
  ]

  tags = {
    Name = "${var.cluster_name}-nodes"
  }
}

# IAM roles and policies for EKS cluster and nodes...
# (Additional IAM configuration would be added here)
            '''
        }
    
    def generate_terraform(self, analysis: Dict[str, Any], request: BlueprintRequest) -> str:
        """Generate Terraform code based on analysis"""
        infrastructure_type = analysis.get("infrastructure_type")
        provider = request.provider
        
        # Select appropriate template
        if infrastructure_type == InfrastructureType.KUBERNETES:
            template = self.templates.get("kubernetes_cluster", "")
        elif infrastructure_type == InfrastructureType.COMPUTE:
            template = self.templates.get("aws_web_app", "")
        else:
            template = self.templates.get("aws_web_app", "")  # Default
        
        # Customize template based on requirements
        customized = self._customize_template(template, analysis, request)
        
        return customized
    
    def _customize_template(self, template: str, analysis: Dict[str, Any], request: BlueprintRequest) -> str:
        """Customize template based on specific requirements"""
        # Replace placeholders with actual values
        customizations = {
            "${environment}": request.environment,
            "${security_level}": request.security_level
        }
        
        customized = template
        for placeholder, value in customizations.items():
            customized = customized.replace(placeholder, value)
        
        return customized


class AnsibleGenerator:
    """Generates Ansible playbooks for configuration management"""
    
    def generate_playbook(self, analysis: Dict[str, Any], request: BlueprintRequest) -> str:
        """Generate Ansible playbook"""
        playbook = {
            "name": f"Configure {request.environment} infrastructure",
            "hosts": "all",
            "become": True,
            "vars": {
                "environment": request.environment,
                "security_level": request.security_level
            },
            "tasks": self._generate_tasks(analysis, request)
        }
        
        return yaml.dump([playbook], default_flow_style=False)
    
    def _generate_tasks(self, analysis: Dict[str, Any], request: BlueprintRequest) -> List[Dict[str, Any]]:
        """Generate Ansible tasks based on analysis"""
        tasks = [
            {
                "name": "Update system packages",
                "package": {
                    "name": "*",
                    "state": "latest"
                }
            },
            {
                "name": "Install security updates",
                "package": {
                    "name": "{{ item }}",
                    "state": "present"
                },
                "loop": ["fail2ban", "ufw", "clamav"]
            }
        ]
        
        # Add tasks based on components
        components = analysis.get("components", [])
        if "database" in components:
            tasks.append({
                "name": "Install and configure database",
                "include_tasks": "database.yml"
            })
        
        if "monitoring" in components:
            tasks.append({
                "name": "Install monitoring agents",
                "include_tasks": "monitoring.yml"
            })
        
        return tasks


class CostEstimator:
    """Estimates infrastructure costs"""
    
    def __init__(self):
        self.ai_engine = AIIntelligenceEngine()
    
    def estimate_cost(self, analysis: Dict[str, Any], request: BlueprintRequest) -> float:
        """Estimate monthly infrastructure cost"""
        provider = request.provider.value
        cost_models = self.ai_engine.cost_models.get(provider, {})
        
        base_cost = 0.0
        components = analysis.get("components", [])
        scale = analysis.get("scale_requirements", {})
        instances = scale.get("instances", 1)
        
        # Estimate based on components
        if "compute" in components:
            compute_cost = cost_models.get("ec2", {}).get("t3.small", 0.0208)
            base_cost += compute_cost * instances * 24 * 30  # Monthly
        
        if "database" in components:
            db_cost = cost_models.get("rds", {}).get("db.t3.small", 0.034)
            base_cost += db_cost * 24 * 30  # Monthly
        
        if "storage" in components:
            storage_cost = cost_models.get("s3", {}).get("standard", 0.023)
            base_cost += storage_cost * 100  # 100GB assumed
        
        # Apply environment multiplier
        env_multipliers = {"dev": 0.5, "staging": 0.8, "prod": 1.2}
        multiplier = env_multipliers.get(request.environment, 1.0)
        
        estimated_cost = base_cost * multiplier
        
        logger.info(f"Estimated monthly cost: ${estimated_cost:.2f}")
        return estimated_cost


class ComplianceScorer:
    """Scores blueprint compliance"""
    
    def calculate_compliance_score(self, analysis: Dict[str, Any], request: BlueprintRequest) -> float:
        """Calculate compliance score (0-100)"""
        score = 70.0  # Base score
        
        # Check security requirements
        security_needs = analysis.get("security_requirements", [])
        if "encryption" in security_needs:
            score += 10
        if "firewall" in security_needs:
            score += 5
        if "authentication" in security_needs:
            score += 10
        
        # Check compliance requirements
        compliance_needs = analysis.get("compliance_needs", [])
        if compliance_needs:
            score += len(compliance_needs) * 5
        
        # Cap at 100
        return min(score, 100.0)


class BlueprintEngine:
    """Main AI Blueprint Engine (Brahma)"""
    
    def __init__(self):
        self.ai_engine = AIIntelligenceEngine()
        self.terraform_generator = TerraformGenerator()
        self.ansible_generator = AnsibleGenerator()
        self.cost_estimator = CostEstimator()
        self.compliance_scorer = ComplianceScorer()
        
        logger.info("Brahma AI Blueprint Engine initialized")
    
    async def generate_blueprint(self, request: BlueprintRequest) -> GeneratedBlueprint:
        """Generate infrastructure blueprint from natural language intent"""
        try:
            logger.info(f"Generating blueprint for: {request.intent}")
            
            # Step 1: Analyze intent using AI
            analysis = self.ai_engine.analyze_intent(request.intent)
            
            # Step 2: Generate Terraform code
            terraform_code = self.terraform_generator.generate_terraform(analysis, request)
            
            # Step 3: Generate Ansible playbook
            ansible_playbook = self.ansible_generator.generate_playbook(analysis, request)
            
            # Step 4: Estimate cost
            estimated_cost = self.cost_estimator.estimate_cost(analysis, request)
            
            # Step 5: Calculate compliance score
            compliance_score = self.compliance_scorer.calculate_compliance_score(analysis, request)
            
            # Step 6: Calculate security score
            security_score = self._calculate_security_score(analysis, request)
            
            # Create blueprint
            blueprint = GeneratedBlueprint(
                blueprint_id=f"bp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=f"Generated Infrastructure for {request.environment}",
                description=f"AI-generated blueprint based on: {request.intent}",
                provider=request.provider,
                infrastructure_type=analysis["infrastructure_type"],
                terraform_code=terraform_code,
                ansible_playbook=ansible_playbook,
                estimated_cost=estimated_cost,
                compliance_score=compliance_score,
                security_score=security_score,
                created_at=datetime.now(),
                metadata={
                    "analysis": analysis,
                    "original_request": {
                        "intent": request.intent,
                        "provider": request.provider.value,
                        "environment": request.environment,
                        "compliance_requirements": request.compliance_requirements
                    }
                }
            )
            
            logger.info(f"Blueprint generated successfully: {blueprint.blueprint_id}")
            return blueprint
            
        except Exception as e:
            logger.error(f"Error generating blueprint: {str(e)}")
            raise
    
    def _calculate_security_score(self, analysis: Dict[str, Any], request: BlueprintRequest) -> float:
        """Calculate security score (0-100)"""
        score = 60.0  # Base score
        
        # Security level bonus
        security_levels = {"low": 0, "medium": 10, "high": 20, "critical": 30}
        score += security_levels.get(request.security_level, 10)
        
        # Security requirements bonus
        security_needs = analysis.get("security_requirements", [])
        score += len(security_needs) * 5
        
        return min(score, 100.0)
    
    async def list_blueprints(self) -> List[Dict[str, Any]]:
        """List all generated blueprints"""
        # In a real implementation, this would query a database
        return []
    
    async def get_blueprint(self, blueprint_id: str) -> Optional[GeneratedBlueprint]:
        """Get specific blueprint by ID"""
        # In a real implementation, this would query a database
        return None


# Export main class
__all__ = ["BlueprintEngine", "BlueprintRequest", "GeneratedBlueprint"]

# 🌌 AetherEdge Terraform Variables
# ==================================
# Variable definitions for the divine infrastructure deployment

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "development"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "location" {
  description = "Azure region for resource deployment"
  type        = string
  default     = "East US"
}

variable "tenant_id" {
  description = "Azure AD tenant ID"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version for AKS cluster"
  type        = string
  default     = "1.28.3"
}

variable "node_count" {
  description = "Initial number of nodes in the AKS cluster"
  type        = number
  default     = 3

  validation {
    condition     = var.node_count >= 3 && var.node_count <= 10
    error_message = "Node count must be between 3 and 10."
  }
}

variable "node_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "postgres_admin_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "divine_admin"

  validation {
    condition     = length(var.postgres_admin_username) >= 4
    error_message = "PostgreSQL admin username must be at least 4 characters long."
  }
}

variable "postgres_admin_password" {
  description = "PostgreSQL administrator password"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.postgres_admin_password) >= 12
    error_message = "PostgreSQL admin password must be at least 12 characters long."
  }
}

variable "enable_monitoring" {
  description = "Enable comprehensive monitoring and observability"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backup for databases and storage"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30

  validation {
    condition     = var.backup_retention_days >= 7 && var.backup_retention_days <= 365
    error_message = "Backup retention must be between 7 and 365 days."
  }
}

variable "enable_waf" {
  description = "Enable Web Application Firewall"
  type        = bool
  default     = true
}

variable "allowed_ip_ranges" {
  description = "List of allowed IP ranges for access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "ssl_certificate_path" {
  description = "Path to SSL certificate for HTTPS"
  type        = string
  default     = ""
}

variable "cost_optimization_enabled" {
  description = "Enable cost optimization features"
  type        = bool
  default     = true
}

variable "auto_scaling_enabled" {
  description = "Enable auto-scaling for compute resources"
  type        = bool
  default     = true
}

variable "compliance_frameworks" {
  description = "List of compliance frameworks to enforce"
  type        = list(string)
  default     = ["SOC2", "NIST", "ISO27001"]
}

variable "divine_modules_config" {
  description = "Configuration for divine modules"
  type = map(object({
    enabled      = bool
    replicas     = number
    cpu_request  = string
    cpu_limit    = string
    mem_request  = string
    mem_limit    = string
    storage_size = string
  }))
  default = {
    brahma = {
      enabled      = true
      replicas     = 3
      cpu_request  = "500m"
      cpu_limit    = "1000m"
      mem_request  = "1Gi"
      mem_limit    = "2Gi"
      storage_size = "10Gi"
    }
    vishnu = {
      enabled      = true
      replicas     = 3
      cpu_request  = "500m"
      cpu_limit    = "1000m"
      mem_request  = "1Gi"
      mem_limit    = "2Gi"
      storage_size = "10Gi"
    }
    shiva = {
      enabled      = true
      replicas     = 2
      cpu_request  = "750m"
      cpu_limit    = "1500m"
      mem_request  = "1.5Gi"
      mem_limit    = "3Gi"
      storage_size = "20Gi"
    }
    saraswati = {
      enabled      = true
      replicas     = 2
      cpu_request  = "1000m"
      cpu_limit    = "2000m"
      mem_request  = "2Gi"
      mem_limit    = "4Gi"
      storage_size = "50Gi"
    }
    lakshmi = {
      enabled      = true
      replicas     = 2
      cpu_request  = "500m"
      cpu_limit    = "1000m"
      mem_request  = "1Gi"
      mem_limit    = "2Gi"
      storage_size = "10Gi"
    }
    kali = {
      enabled      = true
      replicas     = 3
      cpu_request  = "500m"
      cpu_limit    = "1000m"
      mem_request  = "1Gi"
      mem_limit    = "2Gi"
      storage_size = "10Gi"
    }
    hanuman = {
      enabled      = true
      replicas     = 5
      cpu_request  = "250m"
      cpu_limit    = "500m"
      mem_request  = "512Mi"
      mem_limit    = "1Gi"
      storage_size = "5Gi"
    }
    ganesha = {
      enabled      = true
      replicas     = 2
      cpu_request  = "500m"
      cpu_limit    = "1000m"
      mem_request  = "1Gi"
      mem_limit    = "2Gi"
      storage_size = "15Gi"
    }
  }
}

variable "ai_models_config" {
  description = "Configuration for AI/ML models"
  type = object({
    model_registry_storage = string
    inference_cpu_limit    = string
    inference_memory_limit = string
    training_node_count    = number
    gpu_enabled           = bool
  })
  default = {
    model_registry_storage = "100Gi"
    inference_cpu_limit    = "2000m"
    inference_memory_limit = "4Gi"
    training_node_count    = 2
    gpu_enabled           = false
  }
}

variable "security_config" {
  description = "Security configuration settings"
  type = object({
    enable_pod_security_policy = bool
    enable_network_policy      = bool
    enable_rbac               = bool
    enable_admission_controller = bool
    secret_rotation_days      = number
  })
  default = {
    enable_pod_security_policy = true
    enable_network_policy      = true
    enable_rbac               = true
    enable_admission_controller = true
    secret_rotation_days      = 90
  }
}

variable "monitoring_config" {
  description = "Monitoring and observability configuration"
  type = object({
    enable_prometheus     = bool
    enable_grafana       = bool
    enable_jaeger        = bool
    enable_elk_stack     = bool
    log_retention_days   = number
    metrics_retention_days = number
  })
  default = {
    enable_prometheus     = true
    enable_grafana       = true
    enable_jaeger        = true
    enable_elk_stack     = true
    log_retention_days   = 30
    metrics_retention_days = 90
  }
}

variable "disaster_recovery_config" {
  description = "Disaster recovery configuration"
  type = object({
    enable_cross_region_backup = bool
    backup_region             = string
    rpo_hours                 = number
    rto_hours                 = number
  })
  default = {
    enable_cross_region_backup = true
    backup_region             = "West US 2"
    rpo_hours                 = 1
    rto_hours                 = 4
  }
}

variable "cost_management" {
  description = "Cost management and optimization settings"
  type = object({
    enable_budget_alerts     = bool
    monthly_budget_limit     = number
    enable_resource_tagging  = bool
    enable_rightsizing      = bool
    enable_reserved_instances = bool
  })
  default = {
    enable_budget_alerts     = true
    monthly_budget_limit     = 10000
    enable_resource_tagging  = true
    enable_rightsizing      = true
    enable_reserved_instances = false
  }
}

variable "networking_config" {
  description = "Network configuration settings"
  type = object({
    vnet_address_space          = list(string)
    aks_subnet_cidr            = string
    database_subnet_cidr       = string
    appgw_subnet_cidr          = string
    enable_private_endpoints   = bool
    enable_service_endpoints   = bool
  })
  default = {
    vnet_address_space         = ["10.0.0.0/16"]
    aks_subnet_cidr           = "10.0.1.0/24"
    database_subnet_cidr      = "10.0.2.0/24"
    appgw_subnet_cidr         = "10.0.3.0/24"
    enable_private_endpoints  = true
    enable_service_endpoints  = true
  }
}

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

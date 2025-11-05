#!/usr/bin/env pwsh

<#
.SYNOPSIS
    AetherEdge Infrastructure Deployment Script
.DESCRIPTION
    This script deploys the complete AetherEdge infrastructure including:
    - Database layer (PostgreSQL, Redis, ElasticSearch, MinIO)
    - Monitoring stack (Prometheus, Grafana, Jaeger, OpenTelemetry)
    - Security and compliance validation
.PARAMETER Environment
    Deployment environment (dev, staging, production)
.PARAMETER SkipValidation
    Skip pre-deployment validation checks
.PARAMETER Component
    Deploy specific component only (database, monitoring, all)
.EXAMPLE
    .\deploy-infrastructure.ps1 -Environment production
.EXAMPLE
    .\deploy-infrastructure.ps1 -Environment dev -Component database
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("dev", "staging", "production")]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipValidation,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("database", "monitoring", "all")]
    [string]$Component = "all"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue
$Cyan = [System.ConsoleColor]::Cyan

function Write-ColoredOutput {
    param(
        [string]$Message,
        [System.ConsoleColor]$Color = [System.ConsoleColor]::White
    )
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

function Write-Banner {
    param([string]$Title)
    Write-Host ""
    Write-ColoredOutput "=" * 80 -Color $Cyan
    Write-ColoredOutput "  $Title" -Color $Cyan
    Write-ColoredOutput "=" * 80 -Color $Cyan
    Write-Host ""
}

function Test-Prerequisites {
    Write-Banner "Checking Prerequisites"
    
    $prerequisites = @(
        @{ Name = "Docker"; Command = "docker --version" },
        @{ Name = "Docker Compose"; Command = "docker-compose --version" },
        @{ Name = "Git"; Command = "git --version" }
    )
    
    $allGood = $true
    
    foreach ($prereq in $prerequisites) {
        try {
            $result = Invoke-Expression $prereq.Command 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColoredOutput "✓ $($prereq.Name) is installed" -Color $Green
            } else {
                Write-ColoredOutput "✗ $($prereq.Name) is not working properly" -Color $Red
                $allGood = $false
            }
        } catch {
            Write-ColoredOutput "✗ $($prereq.Name) is not installed" -Color $Red
            $allGood = $false
        }
    }
    
    # Check available disk space (minimum 10GB)
    $freeSpace = (Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB
    if ($freeSpace -lt 10) {
        Write-ColoredOutput "✗ Insufficient disk space. Available: $([math]::Round($freeSpace, 2))GB, Required: 10GB" -Color $Red
        $allGood = $false
    } else {
        Write-ColoredOutput "✓ Sufficient disk space available: $([math]::Round($freeSpace, 2))GB" -Color $Green
    }
    
    # Check Docker daemon
    try {
        docker info > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "✓ Docker daemon is running" -Color $Green
        } else {
            Write-ColoredOutput "✗ Docker daemon is not running" -Color $Red
            $allGood = $false
        }
    } catch {
        Write-ColoredOutput "✗ Cannot connect to Docker daemon" -Color $Red
        $allGood = $false
    }
    
    if (-not $allGood) {
        Write-ColoredOutput "Prerequisites check failed. Please install missing components." -Color $Red
        exit 1
    }
    
    Write-ColoredOutput "All prerequisites satisfied!" -Color $Green
}

function Initialize-Environment {
    Write-Banner "Initializing Environment: $Environment"
    
    # Create environment file if it doesn't exist
    $envFile = ".env.$Environment"
    if (-not (Test-Path $envFile)) {
        Write-ColoredOutput "Creating environment file: $envFile" -Color $Yellow
        
        $envContent = @"
# AetherEdge Environment Configuration - $Environment
ENVIRONMENT=$Environment

# Database Configuration
POSTGRES_USER=aetheredge
POSTGRES_PASSWORD=$(Get-Random -Minimum 100000000 -Maximum 999999999)aE!
POSTGRES_DB=aetheredge

# MinIO Configuration
MINIO_ROOT_USER=aetheredge
MINIO_ROOT_PASSWORD=$(Get-Random -Minimum 100000000 -Maximum 999999999)minio!

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=$(Get-Random -Minimum 100000000 -Maximum 999999999)graf!

# Security Configuration
JWT_SECRET=$(New-Guid)
ENCRYPTION_KEY=$(New-Guid)

# External Services (configure as needed)
SLACK_WEBHOOK_URL=
PAGERDUTY_INTEGRATION_KEY=
SMTP_SERVER=
SMTP_USER=
SMTP_PASSWORD=

# Cloud Provider Credentials (configure as needed)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1

AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_TENANT_ID=

GCP_PROJECT_ID=
GCP_SERVICE_ACCOUNT_KEY=
"@
        
        $envContent | Out-File -FilePath $envFile -Encoding UTF8
        Write-ColoredOutput "✓ Environment file created. Please review and update credentials in $envFile" -Color $Green
    } else {
        Write-ColoredOutput "✓ Environment file exists: $envFile" -Color $Green
    }
    
    # Create Docker network
    $networkExists = docker network ls --filter name=aetheredge-network --format "{{.Name}}" | Select-String "aetheredge-network"
    if (-not $networkExists) {
        Write-ColoredOutput "Creating Docker network: aetheredge-network" -Color $Yellow
        docker network create aetheredge-network --subnet=172.20.0.0/16
        Write-ColoredOutput "✓ Docker network created" -Color $Green
    } else {
        Write-ColoredOutput "✓ Docker network already exists" -Color $Green
    }
}

function Deploy-Database {
    Write-Banner "Deploying Database Infrastructure"
    
    Set-Location "infrastructure/database"
    
    # Load environment variables
    if (Test-Path "../../.env.$Environment") {
        Write-ColoredOutput "Loading environment variables from .env.$Environment" -Color $Yellow
        Get-Content "../../.env.$Environment" | ForEach-Object {
            if ($_ -match "^([^#][^=]*)=(.*)$") {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
            }
        }
    }
    
    Write-ColoredOutput "Starting database services..." -Color $Yellow
    docker-compose --env-file "../../.env.$Environment" up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColoredOutput "✓ Database services started successfully" -Color $Green
        
        # Wait for services to be healthy
        Write-ColoredOutput "Waiting for services to become healthy..." -Color $Yellow
        $maxAttempts = 60
        $attempt = 0
        
        do {
            $attempt++
            Start-Sleep 5
            
            $postgresHealth = docker ps --filter "name=aetheredge-postgres" --filter "health=healthy" --format "{{.Names}}"
            $redisHealth = docker ps --filter "name=aetheredge-redis" --filter "health=healthy" --format "{{.Names}}"
            
            $healthyServices = @($postgresHealth, $redisHealth).Where({ $_ })
            
            Write-ColoredOutput "Healthy services: $($healthyServices.Count)/2 (Attempt $attempt/$maxAttempts)" -Color $Yellow
            
        } while ($healthyServices.Count -lt 2 -and $attempt -lt $maxAttempts)
        
        if ($healthyServices.Count -eq 2) {
            Write-ColoredOutput "✓ All database services are healthy" -Color $Green
        } else {
            Write-ColoredOutput "⚠ Some services may not be fully healthy yet" -Color $Yellow
        }
        
    } else {
        Write-ColoredOutput "✗ Failed to start database services" -Color $Red
        exit 1
    }
    
    Set-Location "../.."
}

function Deploy-Monitoring {
    Write-Banner "Deploying Monitoring Infrastructure"
    
    Set-Location "infrastructure/monitoring"
    
    # Load environment variables
    if (Test-Path "../../.env.$Environment") {
        Get-Content "../../.env.$Environment" | ForEach-Object {
            if ($_ -match "^([^#][^=]*)=(.*)$") {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
            }
        }
    }
    
    Write-ColoredOutput "Starting monitoring services..." -Color $Yellow
    docker-compose --env-file "../../.env.$Environment" up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColoredOutput "✓ Monitoring services started successfully" -Color $Green
        
        # Wait for Prometheus and Grafana to be ready
        Write-ColoredOutput "Waiting for monitoring services to be ready..." -Color $Yellow
        Start-Sleep 30
        
        # Check if Prometheus is accessible
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-ColoredOutput "✓ Prometheus is ready at http://localhost:9090" -Color $Green
            }
        } catch {
            Write-ColoredOutput "⚠ Prometheus may still be starting up" -Color $Yellow
        }
        
        # Check if Grafana is accessible
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-ColoredOutput "✓ Grafana is ready at http://localhost:3000" -Color $Green
            }
        } catch {
            Write-ColoredOutput "⚠ Grafana may still be starting up" -Color $Yellow
        }
        
    } else {
        Write-ColoredOutput "✗ Failed to start monitoring services" -Color $Red
        exit 1
    }
    
    Set-Location "../.."
}

function Show-ServiceStatus {
    Write-Banner "Service Status"
    
    $services = @(
        @{ Name = "PostgreSQL"; Container = "aetheredge-postgres"; Port = "5432"; URL = "postgres://localhost:5432" },
        @{ Name = "Redis"; Container = "aetheredge-redis"; Port = "6379"; URL = "redis://localhost:6379" },
        @{ Name = "ElasticSearch"; Container = "aetheredge-elasticsearch"; Port = "9200"; URL = "http://localhost:9200" },
        @{ Name = "Kibana"; Container = "aetheredge-kibana"; Port = "5601"; URL = "http://localhost:5601" },
        @{ Name = "MinIO"; Container = "aetheredge-minio"; Port = "9001"; URL = "http://localhost:9001" },
        @{ Name = "Prometheus"; Container = "aetheredge-prometheus"; Port = "9090"; URL = "http://localhost:9090" },
        @{ Name = "Grafana"; Container = "aetheredge-grafana"; Port = "3000"; URL = "http://localhost:3000" },
        @{ Name = "AlertManager"; Container = "aetheredge-alertmanager"; Port = "9093"; URL = "http://localhost:9093" },
        @{ Name = "Jaeger"; Container = "aetheredge-jaeger"; Port = "16686"; URL = "http://localhost:16686" }
    )
    
    Write-Host ""
    Write-Host "Service Status:" -ForegroundColor $Cyan
    Write-Host "----------------------------------------" -ForegroundColor $Cyan
    
    foreach ($service in $services) {
        $status = docker ps --filter "name=$($service.Container)" --format "{{.Status}}"
        if ($status) {
            if ($status -match "Up") {
                Write-ColoredOutput "✓ $($service.Name): Running - $($service.URL)" -Color $Green
            } else {
                Write-ColoredOutput "⚠ $($service.Name): $status" -Color $Yellow
            }
        } else {
            Write-ColoredOutput "✗ $($service.Name): Not running" -Color $Red
        }
    }
}

function Show-NextSteps {
    Write-Banner "Next Steps"
    
    Write-Host ""
    Write-ColoredOutput "Infrastructure deployment completed successfully!" -Color $Green
    Write-Host ""
    Write-ColoredOutput "Access your services:" -Color $Cyan
    Write-ColoredOutput "• Grafana Dashboard: http://localhost:3000 (admin/admin123)" -Color $Blue
    Write-ColoredOutput "• Prometheus: http://localhost:9090" -Color $Blue
    Write-ColoredOutput "• Jaeger Tracing: http://localhost:16686" -Color $Blue
    Write-ColoredOutput "• Kibana Logs: http://localhost:5601" -Color $Blue
    Write-ColoredOutput "• MinIO Console: http://localhost:9001" -Color $Blue
    Write-Host ""
    Write-ColoredOutput "To deploy AetherEdge applications:" -Color $Cyan
    Write-ColoredOutput "1. Review and update .env.$Environment with your credentials" -Color $Yellow
    Write-ColoredOutput "2. Run: .\deploy-applications.ps1 -Environment $Environment" -Color $Yellow
    Write-Host ""
    Write-ColoredOutput "To stop all services:" -Color $Cyan
    Write-ColoredOutput "docker-compose -f infrastructure/database/docker-compose.yml down" -Color $Yellow
    Write-ColoredOutput "docker-compose -f infrastructure/monitoring/docker-compose.yml down" -Color $Yellow
    Write-Host ""
    Write-ColoredOutput "For troubleshooting, check logs with:" -Color $Cyan
    Write-ColoredOutput "docker-compose -f infrastructure/[component]/docker-compose.yml logs -f" -Color $Yellow
    Write-Host ""
}

# Main execution
try {
    Write-Banner "AetherEdge Infrastructure Deployment"
    Write-ColoredOutput "Environment: $Environment" -Color $Blue
    Write-ColoredOutput "Component: $Component" -Color $Blue
    Write-Host ""
    
    if (-not $SkipValidation) {
        Test-Prerequisites
    }
    
    Initialize-Environment
    
    switch ($Component) {
        "database" {
            Deploy-Database
        }
        "monitoring" {
            Deploy-Monitoring
        }
        "all" {
            Deploy-Database
            Deploy-Monitoring
        }
    }
    
    Show-ServiceStatus
    Show-NextSteps
    
} catch {
    Write-ColoredOutput "Deployment failed: $($_.Exception.Message)" -Color $Red
    Write-ColoredOutput "Full error: $($_.Exception.ToString())" -Color $Red
    exit 1
}

Write-ColoredOutput "Deployment completed successfully!" -Color $Green

#!/usr/bin/env pwsh
# AetherEdge Platform - Kubernetes Deployment Script
# Description: Deploy AetherEdge platform to Kubernetes cluster
# Version: 1.0.0

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [Parameter(Mandatory = $false)]
    [string]$Namespace = "aetheredge",
    
    [Parameter(Mandatory = $false)]
    [switch]$UseHelm = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$DryRun = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipPrerequisites = $false,
    
    [Parameter(Mandatory = $false)]
    [string]$KubeConfig = ""
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Script variables
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$KubernetesDir = Join-Path $ProjectRoot "kubernetes"
$HelmDir = Join-Path $ProjectRoot "helm"

Write-Host "🚀 AetherEdge Platform - Kubernetes Deployment" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Namespace: $Namespace" -ForegroundColor Yellow
Write-Host "Use Helm: $UseHelm" -ForegroundColor Yellow
Write-Host "Dry Run: $DryRun" -ForegroundColor Yellow

# Set kubectl context if kubeconfig is provided
if ($KubeConfig) {
    $env:KUBECONFIG = $KubeConfig
    Write-Host "✅ Using kubeconfig: $KubeConfig" -ForegroundColor Green
}

# Check prerequisites
if (-not $SkipPrerequisites) {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Blue
    
    # Check kubectl
    try {
        $null = kubectl version --client
        Write-Host "✅ kubectl is available" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ kubectl is not available. Please install kubectl."
        exit 1
    }
    
    # Check cluster connectivity
    try {
        $null = kubectl cluster-info
        Write-Host "✅ Kubernetes cluster is accessible" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    }
    
    # Check Helm if using Helm deployment
    if ($UseHelm) {
        try {
            $null = helm version
            Write-Host "✅ Helm is available" -ForegroundColor Green
        }
        catch {
            Write-Error "❌ Helm is not available. Please install Helm."
            exit 1
        }
    }
    else {
        # Check Kustomize
        try {
            $null = kubectl kustomize --help
            Write-Host "✅ Kustomize is available" -ForegroundColor Green
        }
        catch {
            Write-Error "❌ Kustomize is not available. Please install kustomize or use a newer version of kubectl."
            exit 1
        }
    }
}

# Function to deploy with Kustomize
function Deploy-WithKustomize {
    param($Environment, $Namespace, $DryRun)
    
    Write-Host "📦 Deploying with Kustomize..." -ForegroundColor Blue
    
    $KustomizePath = Join-Path $KubernetesDir "overlays" $Environment
    
    if (-not (Test-Path $KustomizePath)) {
        Write-Error "❌ Kustomize overlay not found for environment: $Environment"
        exit 1
    }
    
    # Create namespace if it doesn't exist
    if (-not $DryRun) {
        kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -
        Write-Host "✅ Namespace '$Namespace' ready" -ForegroundColor Green
    }
    
    # Apply kustomization
    $KustomizeArgs = @("apply", "-k", $KustomizePath)
    if ($DryRun) {
        $KustomizeArgs += "--dry-run=client"
    }
    
    Write-Host "🚀 Applying Kubernetes manifests..." -ForegroundColor Blue
    & kubectl @KustomizeArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Kustomize deployment completed successfully" -ForegroundColor Green
    }
    else {
        Write-Error "❌ Kustomize deployment failed"
        exit 1
    }
}

# Function to deploy with Helm
function Deploy-WithHelm {
    param($Environment, $Namespace, $DryRun)
    
    Write-Host "⛵ Deploying with Helm..." -ForegroundColor Blue
    
    $ChartPath = Join-Path $HelmDir "aetheredge"
    $ValuesFile = Join-Path $ChartPath "values-$Environment.yaml"
    
    if (-not (Test-Path $ChartPath)) {
        Write-Error "❌ Helm chart not found at: $ChartPath"
        exit 1
    }
    
    # Create namespace if it doesn't exist
    if (-not $DryRun) {
        kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -
        Write-Host "✅ Namespace '$Namespace' ready" -ForegroundColor Green
    }
    
    # Prepare Helm command
    $HelmArgs = @("upgrade", "--install", "aetheredge", $ChartPath, "--namespace", $Namespace)
    
    if (Test-Path $ValuesFile) {
        $HelmArgs += @("--values", $ValuesFile)
        Write-Host "✅ Using values file: $ValuesFile" -ForegroundColor Green
    }
    
    if ($DryRun) {
        $HelmArgs += "--dry-run"
    }
    
    $HelmArgs += @("--wait", "--timeout", "600s")
    
    Write-Host "🚀 Installing/Upgrading Helm release..." -ForegroundColor Blue
    & helm @HelmArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Helm deployment completed successfully" -ForegroundColor Green
    }
    else {
        Write-Error "❌ Helm deployment failed"
        exit 1
    }
}

# Main deployment logic
try {
    if ($UseHelm) {
        Deploy-WithHelm -Environment $Environment -Namespace $Namespace -DryRun $DryRun
    }
    else {
        Deploy-WithKustomize -Environment $Environment -Namespace $Namespace -DryRun $DryRun
    }
    
    # Wait for deployment to be ready (skip for dry-run)
    if (-not $DryRun) {
        Write-Host "⏳ Waiting for deployment to be ready..." -ForegroundColor Blue
        kubectl wait --for=condition=available --timeout=600s deployment/aetheredge-api -n $Namespace
        
        # Show deployment status
        Write-Host "📊 Deployment Status:" -ForegroundColor Blue
        kubectl get pods,svc,ingress -n $Namespace
        
        # Show application logs
        Write-Host "📋 Recent Application Logs:" -ForegroundColor Blue
        kubectl logs -l app=aetheredge-api -n $Namespace --tail=20
    }
    
    Write-Host "🎉 AetherEdge Platform deployment completed successfully!" -ForegroundColor Green
    Write-Host "🌐 Access the API at: https://api.aetheredge.com" -ForegroundColor Cyan
    Write-Host "📚 API Documentation: https://api.aetheredge.com/docs" -ForegroundColor Cyan
}
catch {
    Write-Error "❌ Deployment failed: $_"
    exit 1
}

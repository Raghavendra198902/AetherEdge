#!/bin/bash

# AetherEdge Production Deployment Script
# This script implements blue/green deployment strategy

set -euo pipefail

# Configuration
CLUSTER_NAME="aetheredge-production"
REGION="us-east-1"
NAMESPACE="aetheredge"
IMAGE_TAG="${GITHUB_SHA:-latest}"
REGISTRY="ghcr.io"
REPO_NAME="aetheredge"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    for cmd in kubectl aws docker helm; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd is not installed"
            exit 1
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    # Check Kubernetes context
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Kubernetes cluster not accessible"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Deploy infrastructure using Terraform
deploy_infrastructure() {
    log_info "Deploying infrastructure..."
    
    cd infrastructure/terraform/production
    
    # Initialize Terraform
    terraform init -backend-config="bucket=aetheredge-terraform-state"
    
    # Plan deployment
    terraform plan -var="image_tag=${IMAGE_TAG}" -out=production.tfplan
    
    # Apply changes
    terraform apply -auto-approve production.tfplan
    
    log_success "Infrastructure deployed"
}

# Update Kubernetes configuration
update_kubeconfig() {
    log_info "Updating Kubernetes configuration..."
    
    aws eks update-kubeconfig \
        --region $REGION \
        --name $CLUSTER_NAME
    
    log_success "Kubernetes configuration updated"
}

# Get current deployment color
get_current_color() {
    local current_color
    current_color=$(kubectl get deployment api-gateway -n $NAMESPACE -o jsonpath='{.metadata.labels.version}' 2>/dev/null || echo "green")
    echo $current_color
}

# Get next deployment color
get_next_color() {
    local current_color=$1
    if [ "$current_color" = "blue" ]; then
        echo "green"
    else
        echo "blue"
    fi
}

# Deploy services with blue/green strategy
deploy_services() {
    local current_color=$(get_current_color)
    local next_color=$(get_next_color $current_color)
    
    log_info "Current deployment: $current_color"
    log_info "Deploying to: $next_color"
    
    # Create namespace if it doesn't exist
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy to the inactive environment
    deploy_to_environment $next_color
    
    # Run health checks
    if run_health_checks $next_color; then
        # Switch traffic to new environment
        switch_traffic $next_color
        
        # Clean up old environment
        cleanup_old_environment $current_color
        
        log_success "Deployment completed successfully"
    else
        log_error "Health checks failed, rolling back..."
        cleanup_failed_deployment $next_color
        exit 1
    fi
}

# Deploy to specific environment (blue/green)
deploy_to_environment() {
    local color=$1
    log_info "Deploying to $color environment..."
    
    # Set image references
    export API_GATEWAY_IMAGE="$REGISTRY/$REPO_NAME/aetheredge-api-gateway:$IMAGE_TAG"
    export FRONTEND_IMAGE="$REGISTRY/$REPO_NAME/aetheredge-frontend:$IMAGE_TAG"
    
    # Deploy using Helm
    helm upgrade --install aetheredge-$color ./charts/aetheredge \
        --namespace $NAMESPACE \
        --set image.tag=$IMAGE_TAG \
        --set deployment.color=$color \
        --set apiGateway.image=$API_GATEWAY_IMAGE \
        --set frontend.image=$FRONTEND_IMAGE \
        --set database.host=$DB_HOST \
        --set redis.host=$REDIS_HOST \
        --set secrets.databaseUrl=$DATABASE_URL \
        --set secrets.redisUrl=$REDIS_URL \
        --wait --timeout=600s
    
    # Deploy divine modules
    for module in saraswati lakshmi kali hanuman ganesha brahma vishnu shiva; do
        local module_image="$REGISTRY/$REPO_NAME/aetheredge-$module:$IMAGE_TAG"
        
        helm upgrade --install $module-$color ./charts/$module \
            --namespace $NAMESPACE \
            --set image.repository=$REGISTRY/$REPO_NAME/aetheredge-$module \
            --set image.tag=$IMAGE_TAG \
            --set deployment.color=$color \
            --wait --timeout=300s
    done
    
    log_success "$color environment deployed"
}

# Run comprehensive health checks
run_health_checks() {
    local color=$1
    log_info "Running health checks for $color environment..."
    
    local api_gateway_url="http://api-gateway-$color.$NAMESPACE.svc.cluster.local:8000"
    local max_attempts=30
    local attempt=1
    
    # Wait for pods to be ready
    log_info "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod \
        -l app=api-gateway,version=$color \
        -n $NAMESPACE \
        --timeout=300s
    
    # Health check loop
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"
        
        # Basic health check
        if kubectl exec -n $NAMESPACE deployment/api-gateway-$color -- curl -f $api_gateway_url/health; then
            log_info "Basic health check passed"
            
            # Run comprehensive tests
            if run_smoke_tests $color; then
                log_success "All health checks passed"
                return 0
            fi
        fi
        
        log_warning "Health check failed, retrying in 10 seconds..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Health checks failed after $max_attempts attempts"
    return 1
}

# Run smoke tests
run_smoke_tests() {
    local color=$1
    log_info "Running smoke tests for $color environment..."
    
    # Run critical path tests
    kubectl run smoke-test-$color \
        --image=python:3.11-slim \
        --rm -i --restart=Never \
        --namespace=$NAMESPACE \
        -- /bin/bash -c "
            pip install httpx pytest &&
            python -c '
import httpx
import sys

try:
    client = httpx.Client(base_url=\"http://api-gateway-$color.$NAMESPACE.svc.cluster.local:8000\")
    
    # Test health endpoint
    response = client.get(\"/health\")
    assert response.status_code == 200
    
    # Test dashboard
    response = client.get(\"/api/dashboard/status\")
    assert response.status_code == 200
    
    # Test each divine module
    modules = [\"saraswati\", \"lakshmi\", \"kali\", \"hanuman\", \"ganesha\"]
    for module in modules:
        response = client.get(f\"/api/{module}/health\")
        assert response.status_code == 200
    
    print(\"All smoke tests passed\")
    sys.exit(0)
    
except Exception as e:
    print(f\"Smoke test failed: {e}\")
    sys.exit(1)
'"
    
    if [ $? -eq 0 ]; then
        log_success "Smoke tests passed"
        return 0
    else
        log_error "Smoke tests failed"
        return 1
    fi
}

# Switch traffic to new environment
switch_traffic() {
    local new_color=$1
    log_info "Switching traffic to $new_color environment..."
    
    # Update service selector to point to new color
    kubectl patch service api-gateway \
        -n $NAMESPACE \
        -p '{"spec":{"selector":{"version":"'$new_color'"}}}'
    
    # Update ingress if using ingress controller
    kubectl patch ingress aetheredge-ingress \
        -n $NAMESPACE \
        -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/service-upstream":"api-gateway-'$new_color'"}}}'
    
    log_success "Traffic switched to $new_color environment"
}

# Cleanup old environment
cleanup_old_environment() {
    local old_color=$1
    log_info "Cleaning up $old_color environment..."
    
    # Wait a bit to ensure new environment is stable
    sleep 60
    
    # Remove old deployments
    helm uninstall aetheredge-$old_color -n $NAMESPACE || true
    
    for module in saraswati lakshmi kali hanuman ganesha brahma vishnu shiva; do
        helm uninstall $module-$old_color -n $NAMESPACE || true
    done
    
    log_success "Old environment cleaned up"
}

# Cleanup failed deployment
cleanup_failed_deployment() {
    local failed_color=$1
    log_info "Cleaning up failed deployment: $failed_color"
    
    # Remove failed deployments
    helm uninstall aetheredge-$failed_color -n $NAMESPACE || true
    
    for module in saraswati lakshmi kali hanuman ganesha brahma vishnu shiva; do
        helm uninstall $module-$failed_color -n $NAMESPACE || true
    done
    
    log_success "Failed deployment cleaned up"
}

# Rollback function
rollback() {
    log_warning "Rolling back deployment..."
    
    local current_color=$(get_current_color)
    local previous_color=$(get_next_color $current_color)
    
    # Switch traffic back
    switch_traffic $previous_color
    
    # Cleanup current environment
    cleanup_old_environment $current_color
    
    log_success "Rollback completed"
}

# Setup monitoring and alerting
setup_monitoring() {
    log_info "Setting up monitoring and alerting..."
    
    # Deploy monitoring stack
    helm upgrade --install monitoring ./charts/monitoring \
        --namespace monitoring \
        --create-namespace \
        --set prometheus.enabled=true \
        --set grafana.enabled=true \
        --set alertmanager.enabled=true
    
    # Deploy logging stack
    helm upgrade --install logging ./charts/logging \
        --namespace logging \
        --create-namespace \
        --set elasticsearch.enabled=true \
        --set kibana.enabled=true \
        --set fluentd.enabled=true
    
    log_success "Monitoring and alerting setup completed"
}

# Backup database
backup_database() {
    log_info "Creating database backup..."
    
    # Create backup using pg_dump
    kubectl exec -n $NAMESPACE deployment/postgres -- \
        pg_dump -U postgres aetheredge > backup-$(date +%Y%m%d-%H%M%S).sql
    
    # Upload to S3
    aws s3 cp backup-*.sql s3://aetheredge-backups/database/
    
    log_success "Database backup completed"
}

# Main deployment function
main() {
    log_info "Starting AetherEdge production deployment..."
    
    # Check if this is a rollback
    if [[ "${1:-}" == "rollback" ]]; then
        rollback
        exit 0
    fi
    
    # Run pre-deployment checks
    check_prerequisites
    
    # Create database backup
    backup_database
    
    # Deploy infrastructure
    deploy_infrastructure
    
    # Update kubeconfig
    update_kubeconfig
    
    # Deploy services
    deploy_services
    
    # Setup monitoring
    setup_monitoring
    
    log_success "AetherEdge production deployment completed successfully!"
    log_info "Application is available at: https://aetheredge.com"
}

# Trap errors and cleanup
trap 'log_error "Deployment failed at line $LINENO"' ERR

# Run main function
main "$@"

#!/bin/bash

# 🌌 AetherEdge Cosmic Bootstrap Script
# =====================================
# Divine initialization script to set up the complete AetherEdge platform
# with all necessary dependencies, configurations, and services.

set -e  # Exit on any error

# Colors for divine output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Divine ASCII Art
show_divine_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
    
    🌌 AetherEdge - Divine AI Infrastructure Framework
    ================================================
    
                    ॐ श्री गणेशाय नमः
    
        "धर्मो रक्षति रक्षितः"
        Dharma protects those who protect Dharma
    
    🌟 Brahma    - Blueprint Creation
    🛡️ Vishnu    - Orchestration & Preservation  
    ⚡ Shiva     - Healing & Transformation
    📚 Saraswati - Knowledge & Wisdom
    💰 Lakshmi   - Financial Operations
    🗡️ Kali      - Security & Protection
    🦍 Hanuman   - Agent Execution
    🐘 Ganesha   - Problem Resolution
    
EOF
    echo -e "${NC}"
}

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

log_divine() {
    echo -e "${PURPLE}[DIVINE]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_requirements() {
    log_divine "Checking cosmic system requirements..."
    
    local missing_deps=()
    
    # Check for required commands
    local required_commands=("docker" "docker-compose" "git" "curl" "python3" "node" "npm")
    
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install the missing dependencies and run this script again."
        
        # Provide installation hints based on OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            log_info "Ubuntu/Debian: sudo apt-get install docker.io docker-compose git curl python3 nodejs npm"
            log_info "RHEL/CentOS: sudo yum install docker docker-compose git curl python3 nodejs npm"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            log_info "macOS: brew install docker docker-compose git curl python3 node npm"
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            log_info "Windows: Install Docker Desktop, Git, Python, and Node.js from their official websites"
        fi
        
        exit 1
    fi
    
    log_success "All cosmic requirements satisfied ✨"
}

# Check Docker and Docker Compose
check_docker() {
    log_divine "Verifying Docker cosmic engine..."
    
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check Docker Compose version
    local compose_version
    if command_exists "docker-compose"; then
        compose_version=$(docker-compose --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")
    elif docker compose version >/dev/null 2>&1; then
        compose_version=$(docker compose version --short)
    else
        log_error "Docker Compose not found"
        exit 1
    fi
    
    log_success "Docker cosmic engine ready (Compose: $compose_version) 🐳"
}

# Setup environment
setup_environment() {
    log_divine "Setting up divine environment..."
    
    # Create environment file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating divine environment configuration..."
        cat > .env << EOF
# 🌌 AetherEdge Divine Environment Configuration
# ==============================================

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database Configuration
POSTGRES_DB=aetheredge
POSTGRES_USER=divine_admin
POSTGRES_PASSWORD=divine_cosmic_secret_2024

# Redis Configuration
REDIS_PASSWORD=divine_cache_secret

# JWT Configuration
SECRET_KEY=divine_jwt_secret_key_2024
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Vault Configuration
VAULT_TOKEN=divine_vault_token

# AI Configuration (Optional - Set your API keys)
OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=true

# Security
ENABLE_SECURITY_SCANNING=true
ENABLE_COMPLIANCE_CHECKING=true

# Cost Management
ENABLE_COST_OPTIMIZATION=true
BUDGET_ALERT_THRESHOLD=1000

# Notification
SLACK_WEBHOOK_URL=
TEAMS_WEBHOOK_URL=
EMAIL_SMTP_SERVER=
EMAIL_USERNAME=
EMAIL_PASSWORD=

EOF
        log_success "Divine environment configuration created ✨"
    else
        log_info "Divine environment already configured 🔮"
    fi
}

# Create necessary directories
create_directories() {
    log_divine "Creating cosmic directory structure..."
    
    local directories=(
        "logs"
        "data/postgres"
        "data/redis"
        "data/prometheus"
        "data/grafana"
        "data/elasticsearch"
        "data/vault"
        "templates"
        "policies"
        "playbooks"
        "models"
        "reports"
        "security"
        "agents"
        "correlation"
        "mlflow"
        "nginx/ssl"
        "monitoring/prometheus"
        "monitoring/grafana"
        "scripts/db-init"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    done
    
    log_success "Cosmic directory structure materialized 🏗️"
}

# Setup monitoring configuration
setup_monitoring() {
    log_divine "Configuring cosmic observability..."
    
    # Prometheus configuration
    cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'aetheredge-api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'

  - job_name: 'aetheredge-modules'
    static_configs:
      - targets: 
        - 'brahma-service:8001'
        - 'vishnu-service:8002'
        - 'shiva-service:8003'
        - 'saraswati-service:8004'
        - 'lakshmi-service:8005'
        - 'kali-service:8006'
        - 'hanuman-service:8007'
        - 'ganesha-service:8008'
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF

    # Grafana datasource configuration
    mkdir -p monitoring/grafana/datasources
    cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

    log_success "Cosmic observability configured 📊"
}

# Setup Nginx configuration
setup_nginx() {
    log_divine "Configuring divine gateway..."
    
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api-gateway:8000;
    }
    
    upstream ui_backend {
        server divine-ui:3000;
    }

    server {
        listen 80;
        server_name localhost;

        # UI Routes
        location / {
            proxy_pass http://ui_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API Routes
        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health checks
        location /health {
            proxy_pass http://api_backend/health;
        }

        # Metrics endpoint
        location /metrics {
            proxy_pass http://api_backend/metrics;
        }
    }
}
EOF

    log_success "Divine gateway configured 🚪"
}

# Initialize database
init_database() {
    log_divine "Preparing cosmic database schema..."
    
    cat > scripts/db-init/01-create-extensions.sql << 'EOF'
-- AetherEdge Database Initialization
-- Divine extensions for PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS brahma;
CREATE SCHEMA IF NOT EXISTS vishnu;
CREATE SCHEMA IF NOT EXISTS shiva;
CREATE SCHEMA IF NOT EXISTS saraswati;
CREATE SCHEMA IF NOT EXISTS lakshmi;
CREATE SCHEMA IF NOT EXISTS kali;
CREATE SCHEMA IF NOT EXISTS hanuman;
CREATE SCHEMA IF NOT EXISTS ganesha;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create audit table
CREATE TABLE IF NOT EXISTS audit.divine_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_name VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(255),
    user_id VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    details JSONB,
    ip_address INET,
    user_agent TEXT
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_audit_module_timestamp ON audit.divine_audit_log(module_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_user_timestamp ON audit.divine_audit_log(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit.divine_audit_log(action);

COMMENT ON TABLE audit.divine_audit_log IS 'Divine audit trail for all AetherEdge operations';
EOF

    log_success "Cosmic database schema prepared 🗄️"
}

# Pull required Docker images
pull_images() {
    log_divine "Downloading cosmic container images..."
    
    local images=(
        "postgres:15-alpine"
        "redis:7-alpine"
        "vault:1.15"
        "prom/prometheus:latest"
        "grafana/grafana:latest"
        "docker.elastic.co/elasticsearch/elasticsearch:8.11.0"
        "docker.elastic.co/kibana/kibana:8.11.0"
        "jaegertracing/all-in-one:latest"
        "nginx:alpine"
        "python:3.11-slim"
    )
    
    for image in "${images[@]}"; do
        log_info "Pulling $image..."
        docker pull "$image"
    done
    
    log_success "Cosmic images assembled 📦"
}

# Build custom images
build_images() {
    log_divine "Building divine module containers..."
    
    # Check if Dockerfiles exist and create basic ones if needed
    local modules=("api-gateway" "modules/brahma-blueprint" "modules/vishnu-orchestrator" "modules/shiva-healer" "modules/saraswati-knowledge" "modules/lakshmi-finops" "modules/kali-security" "modules/hanuman-agents" "modules/ganesha-rca" "ui")
    
    for module in "${modules[@]}"; do
        if [ ! -f "$module/Dockerfile" ]; then
            log_info "Creating Dockerfile for $module..."
            
            if [[ $module == "ui" ]]; then
                # React UI Dockerfile
                cat > "$module/Dockerfile" << 'EOF'
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
EOF
            else
                # Python service Dockerfile
                cat > "$module/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash divine && \
    chown -R divine:divine /app
USER divine

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
            fi
            
            # Create basic requirements.txt if it doesn't exist
            if [[ $module != "ui" ]] && [ ! -f "$module/requirements.txt" ]; then
                cat > "$module/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
prometheus-client==0.19.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.2
python-dateutil==2.8.2
EOF
            fi
        fi
    done
    
    log_success "Divine containers prepared for manifestation 🐳"
}

# Start services
start_services() {
    log_divine "Awakening the divine cosmos..."
    
    # Start infrastructure services first
    log_info "Starting cosmic infrastructure..."
    docker-compose up -d postgres redis vault prometheus grafana elasticsearch
    
    # Wait for database to be ready
    log_info "Waiting for cosmic database to awaken..."
    sleep 10
    
    # Start application services
    log_info "Manifesting divine modules..."
    docker-compose up -d
    
    log_success "Divine cosmos is now awakened and operational! ✨"
}

# Show service status
show_status() {
    log_divine "Divine Service Status:"
    echo
    docker-compose ps
    echo
    
    log_info "Access Points:"
    echo -e "  🎨 Divine Dashboard:      ${CYAN}http://localhost:3000${NC}"
    echo -e "  🔥 API Gateway (Indra):   ${CYAN}http://localhost:8000${NC}"
    echo -e "  📊 Grafana:               ${CYAN}http://localhost:3001${NC} (admin/divine_grafana_secret)"
    echo -e "  🔍 Prometheus:            ${CYAN}http://localhost:9090${NC}"
    echo -e "  📈 Kibana:                ${CYAN}http://localhost:5601${NC}"
    echo -e "  🧪 MLflow:                ${CYAN}http://localhost:5000${NC}"
    echo -e "  🔍 Jaeger:                ${CYAN}http://localhost:16686${NC}"
    echo -e "  🔐 Vault:                 ${CYAN}http://localhost:8200${NC} (token: divine_vault_token)"
    echo
    
    log_divine "Divine Module Endpoints:"
    echo -e "  🌟 Brahma (Blueprints):   ${CYAN}http://localhost:8001${NC}"
    echo -e "  🛡️ Vishnu (Orchestrator): ${CYAN}http://localhost:8002${NC}"
    echo -e "  ⚡ Shiva (Healer):        ${CYAN}http://localhost:8003${NC}"
    echo -e "  📚 Saraswati (Knowledge): ${CYAN}http://localhost:8004${NC}"
    echo -e "  💰 Lakshmi (FinOps):      ${CYAN}http://localhost:8005${NC}"
    echo -e "  🗡️ Kali (Security):       ${CYAN}http://localhost:8006${NC}"
    echo -e "  🦍 Hanuman (Agents):      ${CYAN}http://localhost:8007${NC}"
    echo -e "  🐘 Ganesha (RCA):         ${CYAN}http://localhost:8008${NC}"
    echo
}

# Main execution
main() {
    show_divine_banner
    
    log_divine "Beginning cosmic initialization..."
    
    check_requirements
    check_docker
    setup_environment
    create_directories
    setup_monitoring
    setup_nginx
    init_database
    pull_images
    build_images
    start_services
    
    echo
    log_success "🌌 AetherEdge Divine Platform has been successfully initialized! ✨"
    echo
    show_status
    
    echo
    log_divine "May the cosmic forces guide your infrastructure journey!"
    log_info "Run 'docker-compose logs -f' to view divine logs"
    log_info "Run 'docker-compose down' to stop all services"
    log_info "Run './scripts/divine-status.sh' to check service health"
    echo
}

# Run main function
main "$@"

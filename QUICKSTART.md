# 🚀 AetherEdge Quick Start Guide

Welcome to AetherEdge - the Divine AI Infrastructure Framework! This guide will help you get the entire platform up and running.

## 🌟 Prerequisites

Before starting your divine journey, ensure you have:

- **Docker & Docker Compose** (v20.10+)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for frontend development)
- **Git** (for cloning repositories)
- **PowerShell** (on Windows) or **Bash** (on Linux/Mac)

## 🎯 Quick Start

### 1. Clone the Divine Repository

```bash
git clone https://github.com/your-org/aetheredge.git
cd aetheredge
```

### 2. Start the Divine Platform

Using VS Code tasks (recommended):
1. Open VS Code in the project directory
2. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
3. Type "Tasks: Run Task"
4. Select "Build and Run AetherEdge Platform"

Or using command line:
```bash
docker-compose up --build -d
```

### 3. Verify Divine Services

Run the health check task:
1. In VS Code: `Ctrl+Shift+P` → "Tasks: Run Task" → "Check Divine Services Health"

Or manually check each service:
```bash
# API Gateway (Indra)
curl http://localhost:8000/health

# Brahma (Blueprint Engine)
curl http://localhost:8001/health

# Vishnu (Orchestrator)
curl http://localhost:8002/health

# Shiva (Healer)
curl http://localhost:8003/health

# Saraswati (Knowledge)
curl http://localhost:8004/health

# Lakshmi (FinOps)
curl http://localhost:8005/health

# Kali (Security)
curl http://localhost:8006/health

# Hanuman (Agents)
curl http://localhost:8007/health

# Ganesha (RCA)
curl http://localhost:8008/health
```

## 🎨 Service Architecture

### Divine Trinity (Core Services)
- **🎨 Brahma** (Port 8001): Infrastructure blueprint generation
- **🛡️ Vishnu** (Port 8002): Policy orchestration and preservation
- **🔥 Shiva** (Port 8003): AI healing and auto-remediation

### Intelligence Layer (Devi Shakti)
- **📚 Saraswati** (Port 8004): Knowledge management and ML models
- **💰 Lakshmi** (Port 8005): FinOps and cost optimization
- **🗡️ Kali** (Port 8006): Security and threat protection

### Execution Layer
- **🦍 Hanuman** (Port 8007): Distributed agent execution
- **🐘 Ganesha** (Port 8008): Root cause analysis

### Gateway & UI
- **🔥 Indra** (Port 8000): Central API Gateway
- **✨ Divine Dashboard** (Port 3000): React frontend

## 📊 Available Endpoints

### Core API Gateway (http://localhost:8000)
```
GET  /                          # Welcome message
GET  /health                    # Overall system health
GET  /api/v1/divine-status      # Detailed system status
GET  /divine-docs               # Interactive API documentation
```

### Service-Specific APIs
Each divine service exposes:
```
GET  /{service}/                # Service welcome
GET  /{service}/health          # Service health check
GET  /{service}/divine-info     # Deity information
GET  /{service}/docs            # Service API docs
```

## 🔧 Development

### Running Individual Services

To run a specific service in development mode:

```bash
# Example: Running Brahma locally
cd modules/brahma-blueprint
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8001
```

### Environment Configuration

Each service supports environment configuration via `.env` files:

```bash
# Example .env for Brahma
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://postgres:password@localhost:5432/aetheredge
```

### Database Setup

The platform uses PostgreSQL. Initialize with:

```bash
# Using Docker
docker run -d \
  --name aetheredge-postgres \
  -e POSTGRES_DB=aetheredge \
  -e POSTGRES_USER=divine_admin \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  postgres:15-alpine
```

## 🎯 VS Code Tasks

Available tasks in VS Code (`Ctrl+Shift+P` → "Tasks: Run Task"):

- **Build and Run AetherEdge Platform**: Start all services with Docker Compose
- **Check Divine Services Health**: Verify all services are running
- **Stop AetherEdge Platform**: Shutdown all services
- **View Platform Logs**: Follow logs from all services
- **Open Divine Dashboard**: Open the React frontend

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000-8008 and 3000 are available
2. **Docker memory**: Allocate at least 8GB RAM to Docker
3. **Service startup**: Some services may take 30-60 seconds to initialize

### Debug Commands

```bash
# Check service logs
docker-compose logs service-name

# Restart specific service
docker-compose restart service-name

# Rebuild and restart
docker-compose up --build -d service-name

# Check container status
docker-compose ps
```

### Health Check Status Codes

- **healthy**: Service is operational
- **unhealthy**: Service has issues
- **starting**: Service is initializing

## 🌍 Production Deployment

For production deployment:

1. **Kubernetes**: Use the provided Helm charts in `/helm/aetheredge`
2. **Environment Variables**: Configure production settings
3. **Secrets Management**: Use HashiCorp Vault integration
4. **Monitoring**: Enable Prometheus + Grafana stack
5. **Security**: Configure mTLS and RBAC

### Kubernetes Quick Deploy

```bash
# Install with Helm
helm install aetheredge ./helm/aetheredge \
  --namespace aetheredge \
  --create-namespace \
  --values production-values.yaml
```

## 📚 API Usage Examples

### Create Infrastructure Blueprint

```bash
curl -X POST "http://localhost:8000/api/v1/brahma/blueprints" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "web-app-infrastructure",
    "description": "Three-tier web application",
    "infrastructure_type": "kubernetes",
    "requirements": {
      "replicas": 3,
      "environment": "production",
      "resources": {
        "cpu": "2",
        "memory": "4Gi"
      }
    }
  }'
```

### Create Policy

```bash
curl -X POST "http://localhost:8000/api/v1/vishnu/policies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "security-baseline",
    "description": "Baseline security requirements",
    "policy_type": "security",
    "rules": {
      "require_https": true,
      "min_replicas": 2,
      "resource_limits": true
    }
  }'
```

### Report Incident

```bash
curl -X POST "http://localhost:8000/api/v1/shiva/incidents" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "High CPU usage detected",
    "description": "CPU usage exceeded 90% threshold",
    "severity": "high",
    "affected_resources": ["web-app-pod-1", "web-app-pod-2"],
    "symptoms": ["high_cpu", "slow_response"]
  }'
```

## 🔒 Authentication

The platform uses JWT-based authentication. To get started:

1. **Development**: Use the built-in test tokens
2. **Production**: Configure OAuth2/OIDC integration
3. **API Keys**: Available for service-to-service communication

## 📈 Monitoring & Observability

Access the monitoring stack:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Jaeger**: http://localhost:16686
- **Elasticsearch**: http://localhost:9200

## 🤝 Support & Community

- **Documentation**: `/docs` in each service
- **Issues**: GitHub Issues
- **Community**: Discord/Slack channels
- **Contributing**: See CONTRIBUTING.md

## 🙏 Divine Philosophy

*"धर्मो रक्षति रक्षितः"* - Dharma protects those who protect Dharma

AetherEdge embodies the eternal principles of Sanatana Dharma, ensuring technology serves humanity with wisdom, compassion, and cosmic harmony.

---

**May your infrastructure be blessed with divine stability and cosmic performance!** 🕉️

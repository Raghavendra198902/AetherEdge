# AetherEdge API Documentation

## Overview

The AetherEdge Platform API provides a comprehensive RESTful interface for managing enterprise AI-driven infrastructure. The API is built with FastAPI and follows OpenAPI specifications for interactive documentation.

## Architecture

### API Gateway
- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Authentication**: JWT bearer token authentication
- **Rate Limiting**: Token bucket algorithm with Redis backend
- **Security**: Comprehensive middleware for threat protection
- **Monitoring**: Prometheus metrics and OpenTelemetry tracing

### Module Structure

The API is organized into core modules representing the AetherEdge platform components:

#### 🧠 Brahma - AI Blueprint Engine
- **Endpoint**: `/api/v1/brahma`
- **Purpose**: Infrastructure blueprint generation and deployment automation
- **Features**:
  - Blueprint creation and management
  - Multi-cloud template generation
  - Cost estimation
  - Deployment orchestration

#### ⚖️ Vishnu - Policy & Orchestration Engine  
- **Endpoint**: `/api/v1/vishnu`
- **Purpose**: Policy management and compliance orchestration
- **Features**:
  - Policy creation and enforcement
  - Compliance monitoring
  - Workflow orchestration
  - Governance controls

#### 🔧 Shiva - AI Healing Engine
- **Endpoint**: `/api/v1/shiva`
- **Purpose**: Self-healing infrastructure and anomaly detection
- **Features**:
  - Anomaly detection
  - Automated healing actions
  - Health monitoring
  - Incident response

#### 💰 Lakshmi - FinOps Intelligence Engine
- **Endpoint**: `/api/v1/lakshmi`
- **Purpose**: Cost optimization and financial operations
- **Features**:
  - Cost analysis and reporting
  - Budget management
  - Optimization recommendations
  - Spending forecasts

#### 🛡️ Kali - Security Enforcement Layer
- **Endpoint**: `/api/v1/kali`
- **Purpose**: Security monitoring and threat protection
- **Features**:
  - Threat detection
  - Vulnerability scanning
  - Security policy enforcement
  - Incident response

## Authentication

### JWT Token Authentication

All API endpoints (except health checks) require JWT authentication:

```bash
POST /api/v1/auth/token
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123",
  "expires_in": 3600
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "expires_at": "2024-01-01T12:00:00Z"
}
```

### Using the Token

Include the JWT token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

## Core Endpoints

### Health & Monitoring

```bash
# Simple health check
GET /health

# Detailed health status
GET /api/v1/health/detailed

# Readiness probe (Kubernetes)
GET /api/v1/health/ready

# Liveness probe (Kubernetes)
GET /api/v1/health/live

# Prometheus metrics
GET /metrics
```

### Authentication Management

```bash
# Create access token
POST /api/v1/auth/token

# Validate token
POST /api/v1/auth/validate

# Get current user info
GET /api/v1/auth/me

# Revoke token
DELETE /api/v1/auth/revoke
```

## Module-Specific APIs

### Brahma (Blueprint Engine)

```bash
# Create blueprint
POST /api/v1/brahma/blueprints
{
  "name": "Web Application Stack",
  "description": "Production web app infrastructure",
  "requirements": {
    "compute": {"type": "ec2", "size": "t3.medium"},
    "database": {"type": "rds", "engine": "postgresql"}
  },
  "cloud_provider": "aws",
  "environment": "production"
}

# List blueprints
GET /api/v1/brahma/blueprints?page=1&page_size=20

# Get blueprint details
GET /api/v1/brahma/blueprints/{blueprint_id}

# Deploy blueprint
POST /api/v1/brahma/blueprints/{blueprint_id}/deploy
{
  "parameters": {"region": "us-east-1"},
  "dry_run": false
}

# Cost estimation
GET /api/v1/brahma/cost-estimate?cloud_provider=aws&resources={"t3.medium":2}
```

### Vishnu (Policy & Orchestration)

```bash
# Create policy
POST /api/v1/vishnu/policies
{
  "name": "Security Baseline",
  "policy_type": "security",
  "rules": {
    "require_encryption": true,
    "min_password_length": 12
  }
}

# List policies
GET /api/v1/vishnu/policies

# Check compliance
GET /api/v1/vishnu/compliance/{resource_id}

# Execute workflow
POST /api/v1/vishnu/orchestrate
{
  "workflow_type": "deployment",
  "steps": [...]
}
```

### Shiva (AI Healing)

```bash
# List anomalies
GET /api/v1/shiva/anomalies

# Trigger healing
POST /api/v1/shiva/heal/{resource_id}

# Health check
POST /api/v1/shiva/health-check
{
  "resource_ids": ["server-001", "server-002"],
  "check_type": "full"
}

# Healing history
GET /api/v1/shiva/healing-history
```

### Lakshmi (FinOps)

```bash
# Cost analysis
GET /api/v1/lakshmi/cost-analysis?resource_id=all&period=monthly

# Budget alerts
GET /api/v1/lakshmi/budget-alerts

# Optimize costs
POST /api/v1/lakshmi/optimize
{
  "resource_ids": ["i-1234567890abcdef0"],
  "optimization_type": "cost"
}

# Spending trends
GET /api/v1/lakshmi/spending-trends?period=30d&granularity=daily
```

### Kali (Security)

```bash
# List threats
GET /api/v1/kali/threats?severity=high&status=active

# Vulnerability scan
POST /api/v1/kali/scan/{resource_id}

# Create security policy
POST /api/v1/kali/policies
{
  "name": "Web Server Security",
  "policy_type": "firewall",
  "rules": ["block_port_22", "allow_port_443"]
}

# Block IP address
POST /api/v1/kali/block-ip
{
  "ip_address": "192.168.1.100",
  "reason": "Suspicious activity detected"
}

# Security dashboard
GET /api/v1/kali/security-dashboard
```

## Error Handling

The API uses standard HTTP status codes and returns structured error responses:

```json
{
  "detail": "Resource not found",
  "error_code": "RESOURCE_NOT_FOUND",
  "error_message": "The requested resource could not be found",
  "trace_id": "req_12345",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Status Codes

- `200` - OK: Request successful
- `201` - Created: Resource created successfully
- `400` - Bad Request: Invalid request data
- `401` - Unauthorized: Authentication required
- `403` - Forbidden: Insufficient permissions
- `404` - Not Found: Resource not found
- `422` - Unprocessable Entity: Validation error
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server error

## Rate Limiting

The API implements rate limiting with the following defaults:

- **Requests per minute**: 100
- **Window size**: 60 seconds
- **Headers returned**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining in window
  - `X-RateLimit-Reset`: Window reset time

## Security Features

### Request Security
- HTTPS enforcement (production)
- Security headers (HSTS, CSP, etc.)
- Input validation and sanitization
- SQL injection prevention
- XSS protection

### Authentication & Authorization
- JWT-based authentication
- Token expiration and refresh
- Role-based access control
- API key validation

### Monitoring & Logging
- Request/response logging
- Security event tracking
- Audit trail maintenance
- Anomaly detection

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/aetheredge"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"

# Run the API server
python -m src.api.main
```

### API Documentation

When running locally, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Configuration

The API uses environment-based configuration. Key settings:

```bash
# Application
APP_NAME="AetherEdge Platform API"
VERSION="1.0.0"
ENVIRONMENT="development"  # development, staging, production
DEBUG=false

# Server
HOST="0.0.0.0"
PORT=8000

# Security
SECRET_KEY="change-this-in-production"
API_TOKEN="dev-token-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL="postgresql://aetheredge:password@localhost:5432/aetheredge"
REDIS_URL="redis://localhost:6379/0"

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Module Toggles
BRAHMA_ENABLED=true
VISHNU_ENABLED=true
SHIVA_ENABLED=true
LAKSHMI_ENABLED=true
KALI_ENABLED=true
```

## Deployment

### Docker Deployment

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/aetheredge
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aetheredge-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aetheredge-api
  template:
    metadata:
      labels:
        app: aetheredge-api
    spec:
      containers:
      - name: api
        image: aetheredge/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: aetheredge-secrets
              key: database-url
```

## Support

- **Documentation**: Available at `/docs` endpoint
- **Health Monitoring**: Use `/health` endpoints
- **Logs**: Structured JSON logging with correlation IDs
- **Metrics**: Prometheus metrics at `/metrics` endpoint

For technical support, refer to the platform documentation or contact the AetherEdge support team.

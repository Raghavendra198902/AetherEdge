# AetherEdge Project Structure

## 🌌 Divine Architecture Overview

This document outlines the complete project structure for the AetherEdge platform, organized according to Hindu mythology-inspired modules representing different aspects of cosmic order.

## 📁 Root Directory Structure

```text
aetheredge/
├── 📚 docs/                           # Sacred Documentation
│   ├── architecture/                  # System architecture docs
│   ├── api/                          # API documentation
│   ├── deployment/                   # Deployment guides
│   └── security/                     # Security documentation
├── 🎨 ui/                            # Divine Dashboard (React TypeScript)
│   ├── src/
│   │   ├── components/               # Reusable UI components
│   │   ├── pages/                   # Application pages
│   │   ├── services/                # API service layers
│   │   └── utils/                   # Utility functions
│   ├── public/                      # Static assets
│   └── tests/                       # Frontend tests
├── 🔥 api-gateway/                   # Indra - Central Gateway
│   ├── src/                         # FastAPI gateway source
│   ├── middleware/                  # Authentication & routing
│   ├── schemas/                     # API schemas
│   └── tests/                       # Gateway tests
├── 🌟 modules/                       # Core Divine Modules
│   ├── brahma-blueprint/             # Creation Engine
│   │   ├── src/                     # Blueprint generation logic
│   │   ├── templates/               # IaC templates
│   │   ├── ai-models/              # AI model artifacts
│   │   └── tests/                   # Module tests
│   ├── vishnu-orchestrator/          # Preservation Engine
│   │   ├── src/                     # Orchestration logic
│   │   ├── policies/               # Policy definitions
│   │   ├── workflows/              # Workflow definitions
│   │   └── tests/                   # Module tests
│   ├── shiva-healer/                 # Transformation Engine
│   │   ├── src/                     # Healing algorithms
│   │   ├── playbooks/              # Ansible playbooks
│   │   ├── ml-models/              # ML model artifacts
│   │   └── tests/                   # Module tests
│   ├── saraswati-knowledge/          # Wisdom Engine
│   │   ├── src/                     # Knowledge management
│   │   ├── models/                 # ML models repository
│   │   ├── graphs/                 # Knowledge graphs
│   │   └── tests/                   # Module tests
│   ├── lakshmi-finops/              # Prosperity Engine
│   │   ├── src/                     # Cost optimization logic
│   │   ├── reports/                # Financial reports
│   │   ├── forecasts/              # Cost forecasting models
│   │   └── tests/                   # Module tests
│   ├── kali-security/               # Protection Engine
│   │   ├── src/                     # Security enforcement
│   │   ├── policies/               # Security policies
│   │   ├── scanners/               # Vulnerability scanners
│   │   └── tests/                   # Module tests
│   ├── hanuman-agents/              # Execution Engine
│   │   ├── src/                     # Agent framework
│   │   ├── agents/                 # Platform-specific agents
│   │   ├── tasks/                  # Task definitions
│   │   └── tests/                   # Module tests
│   └── ganesha-rca/                 # Problem Resolution Engine
│       ├── src/                     # RCA algorithms
│       ├── correlations/           # Event correlation rules
│       ├── remediation/            # Auto-remediation scripts
│       └── tests/                   # Module tests
├── 🛠️ infrastructure/               # Terraform & Ansible
│   ├── terraform/                   # Infrastructure as Code
│   │   ├── modules/                # Reusable Terraform modules
│   │   ├── environments/           # Environment-specific configs
│   │   └── policies/               # Terraform policies
│   ├── ansible/                     # Configuration management
│   │   ├── playbooks/              # Ansible playbooks
│   │   ├── roles/                  # Ansible roles
│   │   └── inventories/            # Environment inventories
│   └── kubernetes/                  # K8s manifests
│       ├── base/                   # Base configurations
│       ├── overlays/               # Environment overlays
│       └── operators/              # Custom operators
├── 📊 monitoring/                   # Observability Stack
│   ├── prometheus/                  # Metrics configuration
│   ├── grafana/                    # Dashboard definitions
│   ├── jaeger/                     # Tracing configuration
│   └── alerts/                     # Alert rules
├── 🔐 security/                     # Zero-Trust Framework
│   ├── policies/                   # Security policies
│   ├── certificates/              # Certificate management
│   ├── vault/                     # Secrets management
│   └── compliance/                # Compliance definitions
├── 🧪 tests/                        # Divine Test Suites
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── e2e/                       # End-to-end tests
│   ├── performance/               # Performance tests
│   └── security/                  # Security tests
├── 📦 helm/                         # Kubernetes Charts
│   ├── aetheredge/                # Main Helm chart
│   ├── charts/                    # Sub-charts
│   └── values/                    # Environment values
├── 🔄 pipelines/                    # CI/CD Workflows
│   ├── github/                    # GitHub Actions
│   ├── azure/                     # Azure DevOps
│   ├── jenkins/                   # Jenkins pipelines
│   └── security/                  # Security scanning
├── 📋 scripts/                      # Automation Scripts
│   ├── setup/                     # Setup scripts
│   ├── deployment/                # Deployment scripts
│   ├── backup/                    # Backup scripts
│   └── maintenance/               # Maintenance scripts
├── 🔧 configs/                      # Configuration Files
│   ├── development/               # Dev environment configs
│   ├── staging/                   # Staging environment configs
│   ├── production/                # Production environment configs
│   └── local/                     # Local development configs
└── 📄 legal/                        # Legal Documents
    ├── LICENSE                    # Software license
    ├── TERMS.md                   # Terms of service
    └── PRIVACY.md                 # Privacy policy
```

## 🏗️ Module Architecture

### Core Divine Modules

Each module follows a standard structure:

```text
module-name/
├── src/
│   ├── __init__.py               # Module initialization
│   ├── main.py                   # Entry point
│   ├── api/                      # API endpoints
│   ├── services/                 # Business logic
│   ├── models/                   # Data models
│   ├── utils/                    # Utility functions
│   └── config/                   # Configuration
├── tests/
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test fixtures
├── docs/                         # Module documentation
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container definition
├── docker-compose.yml           # Local development
└── README.md                     # Module documentation
```

## 🔍 Configuration Management

### Environment Configuration

- **Development**: Local development environment
- **Staging**: Integration testing environment
- **Production**: Live production environment
- **DR**: Disaster recovery environment

### Configuration Hierarchy

1. Default configurations in code
2. Environment-specific config files
3. Environment variables
4. External configuration services (Vault, ConfigMaps)

## 🛡️ Security Structure

### Zero-Trust Components

- **Identity Management**: Authentication and authorization
- **Network Security**: Micro-segmentation and encryption
- **Data Protection**: Encryption at rest and in transit
- **Policy Enforcement**: Automated policy compliance
- **Audit & Compliance**: Comprehensive audit trails

## 📊 Monitoring Structure

### Observability Stack

- **Metrics**: Prometheus for time-series data
- **Logs**: ELK stack for centralized logging
- **Traces**: Jaeger for distributed tracing
- **Alerts**: AlertManager for intelligent notifications
- **Dashboards**: Grafana for visualization

## 🚀 Deployment Structure

### Kubernetes Deployment

- **Helm Charts**: Templated Kubernetes manifests
- **Operators**: Custom Kubernetes operators
- **Service Mesh**: Istio for service communication
- **Ingress**: Traffic routing and load balancing
- **Storage**: Persistent volume management

This structure ensures scalability, maintainability, and alignment with enterprise architecture principles while embodying the divine wisdom of Sanatana Dharma.

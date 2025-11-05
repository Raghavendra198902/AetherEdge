"""
🔥 Indra - Divine API Gateway
==========================

The central gateway that manages all communication between divine modules.
Indra, the king of gods, controls the flow of divine energy (data) between realms.

Features:
- Authentication & Authorization
- Rate limiting & Traffic shaping
- Service discovery & Load balancing
- API versioning & Documentation
- Metrics & Observability
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
import logging
from typing import Optional
import os
from datetime import datetime

try:
    from .middleware.auth import verify_token
    from .middleware.rate_limit import RateLimitMiddleware
    from .middleware.logging import LoggingMiddleware
    from .security import SecurityHeadersMiddleware, security_audit_config, log_security_audit
    from .routers import (
        brahma,      # Blueprint generation
        vishnu,      # Orchestration
        shiva,       # Healing & remediation
        saraswati,   # Knowledge management
        lakshmi,     # FinOps
        kali,        # Security
        hanuman,     # Agent management
        ganesha,     # RCA
        health       # Health checks
    )
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from middleware.auth import verify_token
    from middleware.rate_limit import RateLimitMiddleware
    from middleware.logging import LoggingMiddleware
    from security import SecurityHeadersMiddleware, security_audit_config, log_security_audit
    from routers import (
        brahma,      # Blueprint generation
        vishnu,      # Orchestration
        shiva,       # Healing & remediation
        saraswati,   # Knowledge management
        lakshmi,     # FinOps
        kali,        # Security
        hanuman,     # Agent management
        ganesha,     # RCA
        health       # Health checks
    )
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with divine metadata
app = FastAPI(
    title="🔥 Indra - Divine API Gateway",
    description="""
    The central gateway for AetherEdge platform, managing communication between divine modules.
    
    **Divine Architecture:**
    - 🌟 **Brahma**: Infrastructure blueprint generation
    - 🛡️ **Vishnu**: Policy orchestration and preservation
    - ⚡ **Shiva**: Healing and transformation
    - 📚 **Saraswati**: Knowledge and wisdom
    - 💰 **Lakshmi**: Financial operations
    - 🗡️ **Kali**: Security and protection
    - 🦍 **Hanuman**: Agent execution
    - 🐘 **Ganesha**: Problem resolution
    """,
    version="1.0.0",
    contact={
        "name": "AetherEdge Team",
        "email": "divine-ops@aetheredge.com",
        "url": "https://aetheredge.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/divine-docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/divine-redoc" if settings.ENVIRONMENT != "production" else None
)

# Security setup
security = HTTPBearer()

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Prometheus metrics
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/health", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="indra_requests_inprogress",
    inprogress_labels=True,
)

if settings.ENABLE_METRICS:
    instrumentator.instrument(app).expose(app)

# Include divine module routers
app.include_router(
    brahma.router,
    prefix="/api/v1/brahma",
    tags=["🌟 Brahma - Creation"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    vishnu.router,
    prefix="/api/v1/vishnu",
    tags=["🛡️ Vishnu - Preservation"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    shiva.router,
    prefix="/api/v1/shiva",
    tags=["⚡ Shiva - Transformation"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    saraswati.router,
    prefix="/api/v1/saraswati",
    tags=["📚 Saraswati - Wisdom"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    lakshmi.router,
    prefix="/api/v1/lakshmi",
    tags=["💰 Lakshmi - Prosperity"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    kali.router,
    prefix="/api/v1/kali",
    tags=["🗡️ Kali - Protection"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    hanuman.router,
    prefix="/api/v1/hanuman",
    tags=["🦍 Hanuman - Execution"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    ganesha.router,
    prefix="/api/v1/ganesha",
    tags=["🐘 Ganesha - Problem Resolution"],
    dependencies=[Depends(verify_token)]
)

# Health check endpoint (no authentication required)
app.include_router(
    health.router,
    prefix="/health",
    tags=["🔋 Health"]
)

@app.get("/", summary="Divine Gateway Welcome")
async def root():
    """
    Welcome to the Divine API Gateway
    """
    return {
        "message": "🕉️ Welcome to Indra - Divine API Gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "divine_modules": {
            "brahma": "Blueprint Creation",
            "vishnu": "Orchestration & Preservation", 
            "shiva": "Healing & Transformation",
            "saraswati": "Knowledge & Wisdom",
            "lakshmi": "Financial Operations",
            "kali": "Security & Protection",
            "hanuman": "Agent Execution",
            "ganesha": "Problem Resolution"
        },
        "philosophy": "धर्मो रक्षति रक्षितः - Dharma protects those who protect Dharma"
    }

@app.get("/api/v1/divine-status", summary="Divine System Status")
async def divine_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get overall system status across all divine modules
    """
    try:
        # Verify authentication
        await verify_token(credentials)
        
        # TODO: Implement actual health checks for each module
        divine_health = {
            "brahma": {"status": "healthy", "uptime": "99.9%"},
            "vishnu": {"status": "healthy", "uptime": "99.95%"},
            "shiva": {"status": "healing", "uptime": "99.8%"},
            "saraswati": {"status": "learning", "uptime": "99.9%"},
            "lakshmi": {"status": "optimizing", "uptime": "99.7%"},
            "kali": {"status": "protecting", "uptime": "100%"},
            "hanuman": {"status": "executing", "uptime": "99.9%"},
            "ganesha": {"status": "resolving", "uptime": "99.8%"}
        }
        
        return {
            "cosmic_harmony": "balanced",
            "timestamp": datetime.utcnow().isoformat(),
            "divine_modules": divine_health,
            "overall_health": "excellent"
        }
    except Exception as e:
        logger.error(f"Error getting divine status: {str(e)}")
        raise HTTPException(status_code=500, detail="Unable to retrieve divine status")

@app.on_event("startup")
async def startup_event():
    """
    Divine gateway startup - Initialize connections to all modules
    """
    logger.info("🔥 Indra Divine Gateway starting up...")
    logger.info("🕉️ Establishing connections to divine realms...")
    
    # TODO: Initialize connections to all divine modules
    # TODO: Verify database connections
    # TODO: Load configuration from Vault
    
    logger.info("✨ Divine Gateway ready to serve cosmic requests")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Divine gateway shutdown - Graceful closure of all connections
    """
    logger.info("🔥 Indra Divine Gateway shutting down...")
    logger.info("🙏 Closing connections to divine realms gracefully...")
    
    # TODO: Close database connections
    # TODO: Flush any pending metrics
    
    logger.info("✨ Divine Gateway shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )

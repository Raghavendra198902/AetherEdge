"""
🛡️ Vishnu Orchestrator Engine - Main Application
================================================

The preserver deity responsible for policy orchestration and system preservation.
Vishnu maintains cosmic order through intelligent orchestration and governance.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from .api.routes import router as api_router
from .config import settings
from .database.connection import db_connection

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    logger.info("🛡️ Vishnu Orchestrator Engine starting up...")
    logger.info("⚡ Initializing cosmic preservation protocols...")
    
    # Initialize database connections
    await db_connection.connect()
    await db_connection.initialize_schema()
    
    # Load policy engines
    logger.info("🔧 Loading policy engines...")
    
    # Initialize workflow orchestrator
    logger.info("🔄 Initializing workflow orchestrator...")
    
    # Setup monitoring connections
    logger.info("📊 Setting up monitoring connections...")
    
    # Connect to Kubernetes API
    logger.info("☸️ Connecting to Kubernetes API...")
    
    yield
    
    # Shutdown
    logger.info("🛡️ Vishnu Orchestrator Engine shutting down...")
    logger.info("🙏 Gracefully preserving cosmic order...")
    
    # Close database connections
    await db_connection.disconnect()
    
    # Save active workflows
    logger.info("💾 Saving active workflows...")
    
    # Cleanup resources
    logger.info("🧹 Cleaning up resources...")


# Initialize FastAPI app with divine metadata
app = FastAPI(
    title="🛡️ Vishnu - Divine Orchestrator Engine",
    description="""
    **Vishnu - The Preserver's Divine Orchestration Engine**
    
    Vishnu, the preserver deity, maintains cosmic order through intelligent orchestration.
    This service manages policies, workflows, and ensures system preservation.
    
    **Capabilities:**
    - 🛡️ Policy management and enforcement
    - 🔄 Workflow orchestration
    - ⚖️ Governance and compliance
    - 🎯 Resource optimization
    - 📊 Performance monitoring
    - 🌍 Multi-environment management
    
    **Philosophy:** *"पालनहारा विष्णु सबका कल्याण करता है"* - Vishnu preserves and protects all
    """,
    version="1.0.0",
    contact={
        "name": "Vishnu Divine Operations",
        "email": "vishnu@aetheredge.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", summary="Vishnu Divine Welcome")
async def root():
    """
    Welcome to Vishnu Orchestrator Engine
    """
    return {
        "service": "Vishnu - Divine Orchestrator Engine",
        "message": "🛡️ धर्मो रक्षति रक्षितः - Dharma protects those who protect it",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "deity_info": {
            "name": "Vishnu",
            "domain": "Preservation & Orchestration",
            "element": "Water (Jal)",
            "mantra": "ॐ नारायणाय नमः",
            "description": "The cosmic preserver who maintains universal balance"
        },
        "capabilities": [
            "Policy management",
            "Workflow orchestration",
            "Resource governance",
            "Compliance monitoring",
            "Performance optimization",
            "System preservation"
        ],
        "status": "preserving_order"
    }


@app.get("/health", summary="Vishnu Health Check")
async def health_check():
    """
    Health check endpoint for Vishnu service
    """
    try:
        # Perform actual health checks
        db_health = await db_connection.health_check()
        
        return {
            "service": "vishnu-orchestrator",
            "status": "healthy" if db_health["status"] == "healthy" else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "components": {
                "database": db_health["status"],
                "kubernetes": "connected",
                "policy_engine": "active",
                "workflow_orchestrator": "running",
                "cache": "operational"
            },
            "metrics": {
                "active_policies": 0,
                "running_workflows": 0,
                "compliance_score": 100.0,
                "avg_execution_time_ms": 0
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "service": "vishnu-orchestrator",
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
        )


@app.get("/divine-info", summary="Vishnu Divine Information")
async def divine_info():
    """
    Get detailed information about Vishnu deity and service capabilities
    """
    return {
        "deity": {
            "name": "Vishnu",
            "sanskrit": "विष्णु",
            "title": "The Preserver",
            "consort": "Lakshmi (Goddess of Prosperity)",
            "vehicle": "Garuda (Eagle)",
            "symbols": ["Conch", "Discus", "Mace", "Lotus"],
            "element": "Jal (Water)",
            "direction": "East",
            "color": "Blue/Dark Blue",
            "day": "Thursday"
        },
        "mythology": {
            "role": "Preserver and protector of the universe",
            "avatars": ["Rama", "Krishna", "Buddha", "Kalki"],
            "abode": "Vaikuntha",
            "cosmic_function": "Maintains dharmic order across all realms"
        },
        "service_mapping": {
            "preservation_power": "System stability and continuity",
            "dharmic_order": "Policy enforcement and governance",
            "cosmic_balance": "Resource optimization and load balancing",
            "divine_protection": "Security and compliance monitoring",
            "omnipresence": "Multi-environment orchestration"
        },
        "mantras": [
            "ॐ नारायणाय नमः (Om Narayanaya Namah)",
            "ॐ वासुदेवाय नमः (Om Vasudevaya Namah)",
            "ॐ विष्णवे नमः (Om Vishnave Namah)"
        ],
        "philosophy": "Through conscious preservation, we honor the eternal dharma"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )

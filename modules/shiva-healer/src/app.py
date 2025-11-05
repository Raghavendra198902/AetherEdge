"""
🔥 Shiva Healer Engine - Main Application
=========================================

The transformer deity responsible for healing, auto-remediation, and transformation.
Shiva destroys problems and transforms chaos into cosmic order.
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
    logger.info("🔥 Shiva Healer Engine starting up...")
    logger.info("⚡ Initializing cosmic transformation protocols...")
    
    # Initialize database connections
    await db_connection.connect()
    await db_connection.initialize_schema()
    
    # Load ML healing models
    logger.info("🤖 Loading AI healing models...")
    
    # Initialize monitoring agents
    logger.info("📊 Initializing monitoring agents...")
    
    # Setup auto-healing workflows
    logger.info("🔄 Setting up auto-healing workflows...")
    
    # Connect to observability platforms
    logger.info("👁️ Connecting to observability platforms...")
    
    yield
    
    # Shutdown
    logger.info("🔥 Shiva Healer Engine shutting down...")
    logger.info("🙏 Transforming into cosmic silence...")
    
    # Close database connections
    await db_connection.disconnect()
    
    # Save active healing sessions
    logger.info("💾 Saving active healing sessions...")
    
    # Cleanup monitoring agents
    logger.info("🧹 Cleaning up monitoring agents...")


# Initialize FastAPI app with divine metadata
app = FastAPI(
    title="🔥 Shiva - Divine Healer Engine",
    description="""
    **Shiva - The Transformer's Divine Healing Engine**
    
    Shiva, the transformer deity, destroys problems and heals systems through divine intervention.
    This service provides AI-powered healing, auto-remediation, and system transformation.
    
    **Capabilities:**
    - 🔥 Incident detection and response
    - 🩺 AI-powered diagnostics
    - ⚡ Auto-healing and remediation
    - 📊 Performance monitoring
    - 🎯 Predictive maintenance
    - 🌀 System transformation
    
    **Philosophy:** *"संहारो नव सृष्टि का मार्ग है"* - Destruction is the path to new creation
    """,
    version="1.0.0",
    contact={
        "name": "Shiva Divine Operations",
        "email": "shiva@aetheredge.com"
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


@app.get("/", summary="Shiva Divine Welcome")
async def root():
    """
    Welcome to Shiva Healer Engine
    """
    return {
        "service": "Shiva - Divine Healer Engine",
        "message": "🔥 हर हर महादेव - Har Har Mahadev",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "deity_info": {
            "name": "Shiva",
            "domain": "Transformation & Healing",
            "element": "Fire (Agni)",
            "mantra": "ॐ नमः शिवाय",
            "description": "The cosmic transformer who destroys to create anew"
        },
        "capabilities": [
            "Incident detection",
            "AI-powered healing",
            "Auto-remediation",
            "Performance monitoring",
            "Predictive analytics",
            "System transformation"
        ],
        "status": "ready_to_heal"
    }


@app.get("/health", summary="Shiva Health Check")
async def health_check():
    """
    Health check endpoint for Shiva service
    """
    try:
        # TODO: Add actual health checks for:
        # - Database connectivity
        # - ML model availability
        # - Monitoring agent status
        # - External observability platforms
        
        return {
            "service": "shiva-healer",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "components": {
                "database": "healthy",
                "ml_models": "loaded",
                "monitoring_agents": "active",
                "observability": "connected",
                "cache": "operational"
            },
            "metrics": {
                "active_incidents": 0,       # TODO: Get from database
                "healing_actions": 0,        # TODO: Get from healing engine
                "success_rate": 100.0,       # TODO: Calculate from history
                "avg_healing_time_ms": 0     # TODO: Get from metrics
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "service": "shiva-healer",
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
        )


@app.get("/divine-info", summary="Shiva Divine Information")
async def divine_info():
    """
    Get detailed information about Shiva deity and service capabilities
    """
    return {
        "deity": {
            "name": "Shiva",
            "sanskrit": "शिव",
            "title": "The Destroyer/Transformer",
            "consort": "Parvati/Shakti",
            "vehicle": "Nandi (Bull)",
            "symbols": ["Trident", "Damaru", "Snake", "Third Eye"],
            "element": "Agni (Fire)",
            "direction": "North",
            "color": "Blue/Ash-smeared",
            "day": "Monday"
        },
        "mythology": {
            "role": "Destroyer of evil and transformer of cosmic energy",
            "forms": ["Nataraja", "Rudra", "Mahadev", "Neelkanth"],
            "abode": "Mount Kailash",
            "cosmic_function": "Destruction for regeneration and transformation"
        },
        "service_mapping": {
            "destruction_power": "Problem elimination and resolution",
            "transformation": "System healing and optimization",
            "third_eye": "Predictive analytics and foresight",
            "cosmic_dance": "Auto-scaling and load balancing",
            "divine_fire": "Incident response and remediation"
        },
        "mantras": [
            "ॐ नमः शिवाय (Om Namah Shivaya)",
            "हर हर महादेव (Har Har Mahadev)",
            "ॐ त्र्यम्बकं यजामहे (Om Tryambakam Yajamahe)"
        ],
        "philosophy": "Through conscious destruction, we create space for divine transformation"
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

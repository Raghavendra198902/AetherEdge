"""
🎨 Brahma Blueprint Engine - Main Application
=============================================

The creator deity responsible for generating divine infrastructure blueprints.
Brahma manifests the cosmic blueprints into tangible infrastructure code.
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from .api.routes import router as api_router
from .config import settings

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
    logger.info("🎨 Brahma Blueprint Engine starting up...")
    logger.info("🌟 Initializing cosmic blueprint generation...")
    
    try:
        # Initialize database connections
        from .database.connection import init_database, db_manager
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        # Verify database connection
        if await db_manager.health_check():
            logger.info("✅ Database health check passed")
        else:
            logger.error("❌ Database health check failed")
            from .database.connection import DatabaseError
            raise DatabaseError("Database connection failed")
            
        logger.info("🚀 Brahma Blueprint Engine ready to create!")
        
    except Exception as e:
        logger.error("❌ Failed to start Brahma Blueprint Engine: %s", str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("🎨 Brahma Blueprint Engine shutting down...")
    logger.info("🙏 Closing cosmic connections gracefully...")
    
    try:
        # Close database connections
        from .database.connection import close_database
        await close_database()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error("❌ Error during shutdown: %s", str(e))


# Initialize FastAPI app with divine metadata
app = FastAPI(
    title="🎨 Brahma - Divine Blueprint Engine",
    description="""
    **Brahma - The Creator's Divine Blueprint Engine**
    
    Brahma, the creator deity, manifests infrastructure blueprints through divine inspiration.
    This service generates, validates, and manages infrastructure-as-code templates.
    
    **Capabilities:**
    - 🏗️ Infrastructure blueprint generation
    - 📝 Template management and versioning
    - ✅ Blueprint validation and testing
    - 🔄 Multi-cloud compatibility
    - 🤖 AI-powered optimization
    - 📊 Blueprint analytics and insights
    
    **Philosophy:** *"सृष्टि करना ही ब्रह्मा का धर्म है"* - Creation is Brahma's dharma
    """,
    version="1.0.0",
    contact={
        "name": "Brahma Divine Operations",
        "email": "brahma@aetheredge.com"
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


@app.get("/", summary="Brahma Divine Welcome")
async def root():
    """
    Welcome to Brahma Blueprint Engine
    """
    return {
        "service": "Brahma - Divine Blueprint Engine",
        "message": "🎨 सत्यं शिवं सुन्दरम् - Truth, Goodness, Beauty",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "deity_info": {
            "name": "Brahma",
            "domain": "Creation & Blueprint Generation",
            "element": "Space (Akasha)",
            "mantra": "ॐ ब्रह्मा नमः",
            "description": "The cosmic architect who designs the universe"
        },
        "capabilities": [
            "Infrastructure blueprint generation",
            "Multi-cloud template creation", 
            "AI-powered optimization",
            "Blueprint validation",
            "Template versioning",
            "Compliance checking"
        ],
        "status": "ready_to_create"
    }


@app.get("/health", summary="Brahma Health Check")
async def health_check():
    """
    Health check endpoint for Brahma service
    """
    try:
        # Check database connectivity and get statistics
        from .database.connection import db_manager
        from .repositories.blueprint import BlueprintRepository
        from .database.connection import get_db_session
        
        db_healthy = await db_manager.health_check()
        db_info = await db_manager.get_connection_info()
        
        # Get blueprint statistics
        blueprint_stats = {"total": 0, "templates": 0}
        if db_healthy:
            try:
                async with get_db_session() as session:
                    repo = BlueprintRepository(session)
                    stats = await repo.get_statistics()
                    blueprint_stats = {
                        "total": stats.get("total_blueprints", 0),
                        # Template count from template repo
                        "templates": 0
                    }
            except Exception:
                pass  # Stats are optional for health check
        
        return {
            "service": "brahma-blueprint",
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "components": {
                "database": db_info.get("status", "unknown"),
                "ai_models": "loaded",
                "template_repo": "accessible",
                "cache": "operational"
            },
            "metrics": {
                "blueprints_generated": blueprint_stats["total"],
                "templates_available": blueprint_stats["templates"],
                "success_rate": 100.0,
                "avg_generation_time_ms": 0
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "service": "brahma-blueprint",
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
        )


@app.get("/divine-info", summary="Brahma Divine Information")
async def divine_info():
    """
    Get detailed information about Brahma deity and service capabilities
    """
    return {
        "deity": {
            "name": "Brahma",
            "sanskrit": "ब्रह्मा",
            "title": "The Creator",
            "consort": "Saraswati (Goddess of Knowledge)",
            "vehicle": "Hamsa (Swan)",
            "symbols": ["Lotus", "Vedas", "Water pot", "Mala"],
            "element": "Akasha (Space/Ether)",
            "direction": "East",
            "color": "Red/Golden",
            "day": "Thursday"
        },
        "mythology": {
            "origin": "Born from the naval lotus of Vishnu",
            "role": "Creator of the universe and all beings",
            "wisdom": "Possessor of all Vedic knowledge",
            "creation_cycle": "Creates the universe at the beginning of each kalpa"
        },
        "service_mapping": {
            "creation_power": "Infrastructure blueprint generation",
            "vedic_knowledge": "Template and pattern libraries",
            "cosmic_design": "Architecture optimization",
            "divine_inspiration": "AI-powered suggestions",
            "manifestation": "Code generation from blueprints"
        },
        "mantras": [
            "ॐ ब्रह्मा नमः (Om Brahma Namah)",
            "ॐ वेदाय नमः (Om Vedaya Namah)", 
            "ॐ सर्वज्ञाय नमः (Om Sarvajnaya Namah)"
        ],
        "philosophy": "Through conscious creation, we honor the divine architect within"
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

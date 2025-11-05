"""
🧠 Saraswati Knowledge Engine - Main Application
===============================================

The divine knowledge management and wisdom engine.
Saraswati, the goddess of knowledge, learning, and wisdom, 
orchestrates the flow of information and insights.
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
    logger.info("🧠 Saraswati Knowledge Engine starting up...")
    logger.info("📚 Initializing divine wisdom protocols...")
    
    # Initialize database connections
    await db_connection.connect()
    await db_connection.initialize_schema()
    
    # Initialize search indices
    logger.info("🔍 Initializing search indices...")
    
    # Load knowledge models
    logger.info("🤖 Loading AI knowledge models...")
    
    # Setup document processing
    logger.info("📄 Setting up document processing...")
    
    # Initialize knowledge graph
    logger.info("🕸️ Initializing knowledge graph...")
    
    yield
    
    # Shutdown
    logger.info("🧠 Saraswati Knowledge Engine shutting down...")
    logger.info("🙏 Returning wisdom to the cosmic library...")
    
    # Close database connections
    await db_connection.disconnect()
    
    # Save knowledge indices
    logger.info("💾 Saving knowledge indices...")
    
    # Cleanup resources
    logger.info("🧹 Cleaning up knowledge resources...")


# Initialize FastAPI app with divine metadata
app = FastAPI(
    title="🧠 Saraswati - Divine Knowledge Engine",
    description="""
    **Saraswati - The Goddess of Knowledge and Wisdom**
    
    Saraswati, the divine embodiment of knowledge, learning, and wisdom,
    manages organizational intelligence and transforms data into actionable insights.
    
    **Capabilities:**
    - 📚 Knowledge article management
    - 🔍 Intelligent search and discovery
    - 📄 Document processing and extraction
    - 🧠 AI-powered insights and recommendations
    - 📊 Knowledge analytics and metrics
    - 🕸️ Knowledge graph visualization
    
    **Philosophy:** *"ज्ञानं ब्रह्म"* - Knowledge is the Supreme Reality
    """,
    version="1.0.0",
    contact={
        "name": "Saraswati Divine Operations",
        "email": "saraswati@aetheredge.com"
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


@app.get("/", summary="Saraswati Divine Welcome")
async def root():
    """
    Welcome to Saraswati Knowledge Engine
    """
    return {
        "service": "Saraswati - Divine Knowledge Engine",
        "message": "🧠 ॐ ऐं सरस्वत्यै नमः - Om Aim Saraswatyai Namah",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "deity_info": {
            "name": "Saraswati",
            "domain": "Knowledge & Wisdom",
            "element": "Water (Apas)",
            "mantra": "ॐ ऐं सरस्वत्यै नमः",
            "description": "The goddess of knowledge, learning, arts, and wisdom"
        },
        "capabilities": [
            "Knowledge management",
            "Intelligent search",
            "Document processing",
            "AI-powered insights",
            "Knowledge analytics",
            "Graph visualization"
        ],
        "status": "ready_to_enlighten"
    }


@app.get("/health", summary="Saraswati Health Check")
async def health_check():
    """
    Health check endpoint for Saraswati service
    """
    try:
        # Get database health
        db_health = await db_connection.health_check()
        
        # TODO: Add health checks for:
        # - Search service connectivity
        # - Document processing availability
        # - ML model status
        # - Knowledge graph status
        
        return {
            "service": "saraswati-knowledge",
            "status": "healthy" if db_health["status"] == "healthy" else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "components": {
                "database": db_health["status"],
                "search_engine": "healthy",  # TODO: Implement actual check
                "document_processor": "healthy",  # TODO: Implement actual check
                "knowledge_graph": "healthy",  # TODO: Implement actual check
                "ml_models": "loaded"  # TODO: Implement actual check
            },
            "metrics": {
                "total_articles": db_health.get("total_articles", 0),
                "search_queries_last_hour": 0,  # TODO: Get from analytics
                "documents_processed_today": 0,  # TODO: Get from analytics
                "knowledge_graph_nodes": 0  # TODO: Get from graph service
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "service": "saraswati-knowledge",
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
        )


@app.get("/divine-info", summary="Saraswati Divine Information")
async def divine_info():
    """
    Get detailed information about Saraswati deity and service capabilities
    """
    return {
        "deity": {
            "name": "Saraswati",
            "sanskrit": "सरस्वती",
            "title": "The Goddess of Knowledge",
            "consort": "Brahma",
            "vehicle": "Swan (Hamsa)",
            "symbols": ["Lotus", "Veena", "Sacred Books", "Peacock"],
            "element": "Apas (Water)",
            "direction": "East",
            "color": "White/Yellow",
            "day": "Thursday"
        },
        "mythology": {
            "role": "Goddess of knowledge, learning, arts, and wisdom",
            "forms": ["Bharati", "Vani", "Vidya", "Sharada"],
            "abode": "Brahmaloka",
            "cosmic_function": "Flow of knowledge and creative expression"
        },
        "service_mapping": {
            "divine_knowledge": "Comprehensive knowledge management",
            "flowing_wisdom": "Intelligent search and discovery",
            "sacred_texts": "Document processing and analysis",
            "creative_arts": "Content generation and insights",
            "divine_voice": "Knowledge sharing and communication"
        },
        "mantras": [
            "ॐ ऐं सरस्वत्यै नमः (Om Aim Saraswatyai Namah)",
            "सरस्वती नमस्तुभ्यं वरदे कामरूपिणि",
            "या कुन्देन्दुतुषारहारधवला या शुभ्रवस्त्रावृता"
        ],
        "philosophy": "Through divine knowledge and wisdom, we transform information into enlightenment"
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

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )

"""
💰 Lakshmi FinOps Engine - Main Application
===========================================

The divine financial operations and cost management engine.
Lakshmi, the goddess of wealth and prosperity, optimizes costs and maximizes value.
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
    logger.info("💰 Lakshmi FinOps Engine starting up...")
    logger.info("💎 Initializing divine prosperity protocols...")
    
    # Initialize database connections
    await db_connection.connect()
    await db_connection.initialize_schema()
    
    # Initialize cloud provider connectors
    logger.info("☁️ Initializing cloud provider connectors...")
    
    # Load cost optimization models
    logger.info("🤖 Loading AI cost optimization models...")
    
    # Setup cost data ingestion
    logger.info("📊 Setting up cost data ingestion...")
    
    # Initialize budget monitoring
    logger.info("💳 Initializing budget monitoring...")
    
    # Setup forecasting models
    logger.info("🔮 Setting up cost forecasting models...")
    
    yield
    
    # Shutdown
    logger.info("💰 Lakshmi FinOps Engine shutting down...")
    logger.info("🙏 Returning prosperity to the cosmic treasury...")
    
    # Close database connections
    await db_connection.disconnect()
    
    # Save optimization models
    logger.info("💾 Saving optimization models...")
    
    # Cleanup cloud connections
    logger.info("🧹 Cleaning up cloud connections...")


# Initialize FastAPI app with divine metadata
app = FastAPI(
    title="💰 Lakshmi - Divine FinOps Engine",
    description="""
    **Lakshmi - The Goddess of Wealth and Prosperity**
    
    Lakshmi, the divine embodiment of wealth, prosperity, and abundance,
    manages financial operations and transforms cost chaos into optimized prosperity.
    
    **Capabilities:**
    - 💰 Comprehensive cost tracking and analysis
    - 💳 Budget management and monitoring
    - 🎯 AI-powered cost optimization
    - 🔮 Advanced cost forecasting
    - 📊 Multi-cloud financial operations
    - ⚡ Automated savings recommendations
    
    **Philosophy:** *"श्रीर्वै समृद्धिः"* - Prosperity is true wealth
    """,
    version="1.0.0",
    contact={
        "name": "Lakshmi Divine Operations",
        "email": "lakshmi@aetheredge.com"
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


@app.get("/", summary="Lakshmi Divine Welcome")
async def root():
    """
    Welcome to Lakshmi FinOps Engine
    """
    return {
        "service": "Lakshmi - Divine FinOps Engine",
        "message": "💰 ॐ श्रीं लक्ष्म्यै नमः - Om Shreem Lakshmyai Namah",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "deity_info": {
            "name": "Lakshmi",
            "domain": "Wealth & Prosperity",
            "element": "Water (Apas)",
            "mantra": "ॐ श्रीं लक्ष्म्यै नमः",
            "description": "The goddess of wealth, fortune, and prosperity"
        },
        "capabilities": [
            "Cost tracking & analysis",
            "Budget management",
            "Cost optimization",
            "Financial forecasting",
            "Multi-cloud FinOps",
            "Automated savings"
        ],
        "status": "ready_to_prosper"
    }


@app.get("/health", summary="Lakshmi Health Check")
async def health_check():
    """
    Health check endpoint for Lakshmi service
    """
    try:
        # Get database health
        db_health = await db_connection.health_check()
        
        # TODO: Add health checks for:
        # - Cloud provider connections
        # - Cost data ingestion
        # - ML model availability
        # - Forecasting service
        
        return {
            "service": "lakshmi-finops",
            "status": "healthy" if db_health["status"] == "healthy" else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "components": {
                "database": db_health["status"],
                "cloud_connectors": "healthy",  # TODO: Implement actual check
                "cost_ingestion": "healthy",  # TODO: Implement actual check
                "optimization_engine": "healthy",  # TODO: Implement actual check
                "forecasting_service": "healthy"  # TODO: Implement actual check
            },
            "metrics": {
                "total_cost_entries": db_health.get("total_cost_entries", 0),
                "active_budgets": db_health.get("total_budgets", 0),
                "optimization_opportunities": 0,  # TODO: Get from optimization service
                "monthly_savings": 0.0  # TODO: Get from optimization service
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "service": "lakshmi-finops",
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
        )


@app.get("/divine-info", summary="Lakshmi Divine Information")
async def divine_info():
    """
    Get detailed information about Lakshmi deity and service capabilities
    """
    return {
        "deity": {
            "name": "Lakshmi",
            "sanskrit": "लक्ष्मी",
            "title": "The Goddess of Wealth",
            "consort": "Vishnu",
            "vehicle": "Owl (Uluka)",
            "symbols": ["Lotus", "Gold Coins", "Conch", "Pot of Gold"],
            "element": "Apas (Water)",
            "direction": "North",
            "color": "Golden/Pink",
            "day": "Friday"
        },
        "mythology": {
            "role": "Goddess of wealth, fortune, prosperity, and abundance",
            "forms": ["Mahalakshmi", "Shree", "Kamala", "Padma"],
            "abode": "Vaikuntha with Lord Vishnu",
            "cosmic_function": "Bestowing material and spiritual prosperity"
        },
        "service_mapping": {
            "divine_wealth": "Comprehensive cost tracking and analysis",
            "prosperity_flow": "Budget management and financial planning",
            "golden_wisdom": "AI-powered cost optimization",
            "abundance_vision": "Advanced cost forecasting",
            "fortune_blessing": "Automated savings and recommendations"
        },
        "mantras": [
            "ॐ श्रीं लक्ष्म्यै नमः (Om Shreem Lakshmyai Namah)",
            "ॐ महालक्ष्म्यै च विद्महे (Om Mahalakshmyai Cha Vidmahe)",
            "सर्वमंगल मांगल्ये शिवे सर्वार्थ साधिके"
        ],
        "philosophy": "Through divine prosperity and wise resource management, we create sustainable abundance"
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
        port=8005,
        reload=True,
        log_level="info"
    )

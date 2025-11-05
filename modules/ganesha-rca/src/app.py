"""
Ganesha RCA Module - Main Application
Divine Problem Resolution and Root Cause Analysis Engine
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from .api.routes import router
from .database.connection import rca_db


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🐘 Ganesha RCA Engine starting up...")
    
    # Connect to database
    if await rca_db.connect():
        logger.info("✅ Ganesha RCA Database connected")
    else:
        logger.error("❌ Failed to connect to RCA database")
    
    yield
    
    # Shutdown
    logger.info("🐘 Ganesha RCA Engine shutting down...")
    rca_db.disconnect()
    logger.info("✅ Ganesha RCA Database disconnected")


# Create FastAPI app
app = FastAPI(
    title="🐘 Ganesha - Divine RCA Engine",
    description="Sacred problem resolution and root cause analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint for Ganesha RCA Engine"""
    return {
        "message": "🕉️ Welcome to Ganesha - Divine RCA Engine",
        "deity": "Ganesha",
        "domain": "Problem Resolution & Root Cause Analysis",
        "blessing": "ॐ गं गणपतये नमः। May divine wisdom remove all obstacles.",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8005,
        reload=True
    )

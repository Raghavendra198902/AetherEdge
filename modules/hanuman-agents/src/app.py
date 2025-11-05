"""
Hanuman Agents Module - Main Application
Divine Execution and Agent Management Engine
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from .api.routes import router
from .database.connection import agents_db


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Hanuman Agents Engine starting up...")
    
    # Connect to database
    if await agents_db.connect():
        logger.info("✅ Hanuman Agents Database connected")
    else:
        logger.error("❌ Failed to connect to agents database")
    
    yield
    
    # Shutdown
    logger.info("🚀 Hanuman Agents Engine shutting down...")
    agents_db.disconnect()
    logger.info("✅ Hanuman Agents Database disconnected")


# Create FastAPI app
app = FastAPI(
    title="🦍 Hanuman - Divine Agent Engine",
    description="Sacred execution and distributed agent management",
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
    """Root endpoint for Hanuman Agent Engine"""
    return {
        "message": "🕉️ Welcome to Hanuman - Divine Agent Engine",
        "deity": "Hanuman",
        "domain": "Execution & Agent Network",
        "blessing": "ॐ हं हनुमते नमः। May divine strength empower execution.",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8004,
        reload=True
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8007,
        reload=True,
        log_level="info"
    )

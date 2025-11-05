"""
Kali Security Module - Main Application
Divine Protection and Security Engine
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from .api.routes import router
from .database.connection import security_db


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🗡️ Kali Security Engine starting up...")
    
    # Connect to database
    if await security_db.connect():
        logger.info("✅ Kali Security Database connected")
    else:
        logger.error("❌ Failed to connect to security database")
    
    yield
    
    # Shutdown
    logger.info("🗡️ Kali Security Engine shutting down...")
    security_db.disconnect()
    logger.info("✅ Kali Security Database disconnected")


# Create FastAPI app
app = FastAPI(
    title="🗡️ Kali - Divine Security Engine",
    description="Sacred protection and security threat management",
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
    """Root endpoint for Kali Security Engine"""
    return {
        "message": "🕉️ Welcome to Kali - Divine Security Engine",
        "deity": "Kali",
        "domain": "Protection & Security",
        "blessing": "ॐ क्रीं कालिकायै नमः। May divine protection shield all.",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info"
    )

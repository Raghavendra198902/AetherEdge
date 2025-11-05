"""
AetherEdge API Gateway

Main FastAPI application that serves as the central API gateway
for all AetherEdge modules and services.
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any
import uvicorn

from .middleware.security import SecurityMiddleware
from .middleware.rate_limiting import RateLimitMiddleware
from .middleware.logging import LoggingMiddleware
from .routers import (
    brahma_router,
    vishnu_router,
    shiva_router,
    lakshmi_router,
    kali_router,
    health_router,
    auth_router
)
from .core.config import settings
from .core.database import init_db, close_db
from .core.monitoring import metrics, setup_metrics


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info("Starting AetherEdge API Gateway...")
    await init_db()
    setup_metrics()
    logger.info("AetherEdge API Gateway started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AetherEdge API Gateway...")
    await close_db()
    logger.info("AetherEdge API Gateway shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="AetherEdge Platform API",
    description="""
    AetherEdge is an enterprise AI-driven infrastructure management platform
    that provides intelligent automation, cost optimization, security enforcement,
    and operational excellence across multi-cloud environments.
    
    ## Features
    
    * **🧠 Brahma**: AI Blueprint Engine for infrastructure automation
    * **⚖️ Vishnu**: Policy & Orchestration Engine for compliance management  
    * **🔧 Shiva**: AI Healing Engine for self-healing infrastructure
    * **💰 Lakshmi**: FinOps Intelligence Engine for cost optimization
    * **🛡️ Kali**: Security Enforcement Layer for threat protection
    
    ## Authentication
    
    This API uses Bearer token authentication. Include your API token in the
    Authorization header: `Authorization: Bearer <your-token>`
    """,
    version="1.0.0",
    terms_of_service="https://aetheredge.com/terms",
    contact={
        "name": "AetherEdge Support",
        "url": "https://aetheredge.com/support",
        "email": "support@aetheredge.com",
    },
    license_info={
        "name": "Enterprise License",
        "url": "https://aetheredge.com/license",
    },
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

# Add security middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Validate API token and return user information"""
    try:
        # In production, validate token against auth service
        # For now, using simple token validation
        token = credentials.credentials
        
        if not token or token != settings.API_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Return user context (would come from token validation)
        return {
            "user_id": "api_user",
            "permissions": ["read", "write", "admin"],
            "organization": "default"
        }
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": f"err_{int(time.time())}",
            "message": "An unexpected error occurred. Please contact support."
        }
    )


# Health check endpoint (no auth required)
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Metrics endpoint for Prometheus
@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to AetherEdge Platform API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "status": "operational"
    }


# Include routers
app.include_router(
    health_router.router,
    prefix="/api/v1/health",
    tags=["Health"],
)

app.include_router(
    auth_router.router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

app.include_router(
    brahma_router.router,
    prefix="/api/v1/brahma",
    tags=["Brahma - AI Blueprint Engine"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    vishnu_router.router,
    prefix="/api/v1/vishnu",
    tags=["Vishnu - Policy & Orchestration"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    shiva_router.router,
    prefix="/api/v1/shiva",
    tags=["Shiva - AI Healing Engine"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    lakshmi_router.router,
    prefix="/api/v1/lakshmi",
    tags=["Lakshmi - FinOps Intelligence"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    kali_router.router,
    prefix="/api/v1/kali",
    tags=["Kali - Security Enforcement"],
    dependencies=[Depends(get_current_user)]
)


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )

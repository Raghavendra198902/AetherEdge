"""
Router for Ganesha RCA Module
"""

from fastapi import APIRouter

# Import the actual routes from the module
try:
    from ...modules.ganesha_rca.src.api.routes import (
        router as ganesha_router
    )
except ImportError:
    # Fallback if module structure is different
    ganesha_router = APIRouter()
    
    @ganesha_router.get("/")
    async def ganesha_placeholder():
        return {"message": "Ganesha RCA Module - Coming Soon"}

router = ganesha_router
